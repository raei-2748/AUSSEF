"""Weather enrichment: X2 FFDI, X3 SPEI-3, X7 max temperature, X8 min humidity, X9 max wind.

- Fire-day weather: Open-Meteo historical archive (ERA5), one request per fire, days start-1 .. end (max 60 days).
- Long daily rain/temperature: NASA POWER (MERRA-2, 0.5°) per 0.5° cell, 1991–2025, for KBDI -> drought factor and SPEI-3.
All responses are cached under data/weather_cache/ so reruns make no new requests.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from src.common import DATA, record_source
from src.fire_weather import drought_factor, ffdi, hargreaves_pet, kbdi_series, spei3_monthly

CACHE = DATA / "weather_cache"
MIN_HA, MAX_DAYS, DRIZZLE_MM = 0, 60, 1.0
OM = "https://archive-api.open-meteo.com/v1/archive"
POWER = "https://power.larc.nasa.gov/api/temporal/daily/point"


def _get(url, tries=6, wait=5):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(60 * (k + 1))
                continue
            if k == tries - 1:
                raise
        except Exception:
            if k == tries - 1:
                raise
        time.sleep(wait * (k + 1))
    raise RuntimeError(f"no response after {tries} tries (rate limited): {url[:120]}")


def power_cell(lat, lon):
    la, lo = round(lat * 2) / 2, round(lon * 2) / 2
    f = CACHE / f"power_{la:.1f}_{lo:.1f}.json"
    if not f.exists():
        q = POWER + "?" + urllib.parse.urlencode(dict(parameters="PRECTOTCORR,T2M_MAX,T2M_MIN", community="AG",
                                                      latitude=la, longitude=lo, start="19910101", end="20251231",
                                                      format="JSON"))
        f.write_text(json.dumps(_get(q)))
        time.sleep(0.5)
    p = json.loads(f.read_text())["properties"]["parameter"]
    d = pd.DataFrame({k: pd.Series(v) for k, v in p.items()})
    d.index = pd.to_datetime(d.index, format="%Y%m%d")
    return d.replace(-999.0, np.nan).rename(columns={"PRECTOTCORR": "rain", "T2M_MAX": "tmax", "T2M_MIN": "tmin"}), (la, lo)


def cell_indices(d, lat):
    """KBDI, drought factor and monthly SPEI-3 for one POWER cell."""
    d = d.copy()
    mar = d.rain["1991":"2020"].groupby(d["1991":"2020"].index.year).sum().mean()
    # gridded rain has drizzle on most days; days under 1 mm count as dry for KBDI and the drought factor
    r = d.rain.where(d.rain >= DRIZZLE_MM, 0.0).values
    d["kbdi"] = kbdi_series(r, d.tmax.values, mar)
    d["df"] = drought_factor(d.kbdi.values, r)
    d["pet"] = hargreaves_pet(d.tmax.values, d.tmin.values, lat, d.index)
    spei = spei3_monthly(d)
    return d, spei


def open_meteo(event_id, lat, lon, start, end):
    f = CACHE / f"om_{event_id}.json"
    if not f.exists():
        q = OM + "?" + urllib.parse.urlencode(dict(
            latitude=round(lat, 4), longitude=round(lon, 4), start_date=start.date().isoformat(),
            end_date=end.date().isoformat(), timezone="Australia/Sydney",
            daily="temperature_2m_max,relative_humidity_2m_min,wind_speed_10m_max,precipitation_sum"))
        f.write_text(json.dumps(_get(q)))
        time.sleep(0.3)
    j = json.loads(f.read_text())["daily"]
    return pd.DataFrame(j).assign(time=lambda x: pd.to_datetime(x.time)).set_index("time")


def run(ev, out_path):
    CACHE.mkdir(parents=True, exist_ok=True)
    cells, rows = {}, []
    ev = ev.sort_values("start")
    for n, r in enumerate(ev.itertuples()):
        d, key = power_cell(r.centroid_lat, r.centroid_lon)
        if key not in cells:
            cells[key] = cell_indices(d, key[0])
        cd, spei = cells[key]
        s = pd.Timestamp(r.start).normalize()
        e = pd.Timestamp(r.end).normalize() if pd.notna(r.end) else s
        e = min(max(e, s), s + pd.Timedelta(days=MAX_DAYS))
        row = dict(event_id=r.event_id, power_cell=f"{key[0]:.1f},{key[1]:.1f}",
                   X3_SPEI=float(spei.get(s.replace(day=1), np.nan)),
                   kbdi_at_start=float(cd.kbdi.get(s, np.nan)), drought_factor_at_start=float(cd.df.get(s, np.nan)))
        if r.burn_area_ha >= MIN_HA:
            w = open_meteo(r.event_id, r.centroid_lat, r.centroid_lon, s - pd.Timedelta(days=1), e)
            dfw = cd.df.reindex(w.index)
            f = pd.Series(ffdi(w.temperature_2m_max, w.relative_humidity_2m_min, w.wind_speed_10m_max, dfw), index=w.index)
            f[dfw.isna() | w.temperature_2m_max.isna()] = np.nan
            row.update(X2_FFDI=float(np.nanmax(f)) if np.isfinite(f).any() else np.nan,
                       X7_temp_max=float(w.temperature_2m_max.max()), X8_humidity_min=float(w.relative_humidity_2m_min.min()),
                       X9_wind_max=float(w.wind_speed_10m_max.max()), rain_during_fire_mm=float(w.precipitation_sum.sum()),
                       weather_days=int(len(w)), ffdi_peak_date=str(f.idxmax().date()) if np.isfinite(f).any() else "")
        else:
            row.update(weather_note=f"fire < {MIN_HA} ha: fire-day weather not requested")
        rows.append(row)
        if n % 200 == 0:
            print(f"  weather {n}/{len(ev)}; POWER cells {len(cells)}", flush=True)
            pd.DataFrame(rows).to_parquet(out_path)
    out = pd.DataFrame(rows)
    out.to_parquet(out_path)
    doc = {
        "kbdi_at_start": ["Keetch–Byram drought index on the start day (mm, 0–203)", "mm", "computed from NASA POWER rain/temperature", ""],
        "drought_factor_at_start": ["Griffiths drought factor on the start day (0–10)", "0–10", "computed from NASA POWER", ""],
        "rain_during_fire_mm": ["Total rain during the fire window", "mm", "Open-Meteo ERA5", "fires >= 10 ha"],
        "weather_days": ["Days of fire-day weather used", "days", "Open-Meteo ERA5", "start-1 to end, capped at 60 days"],
        "ffdi_peak_date": ["Date of the highest FFDI during the fire", "date", "computed", ""],
        "power_cell": ["NASA POWER 0.5° cell used for drought indices", "lat,lon", "NASA POWER", ""],
        "weather_note": ["Why fire-day weather is blank", "str", "", ""],
    }
    Path(str(out_path).replace(".parquet", ".doc.json")).write_text(json.dumps(doc, indent=1))
    record_source("Open-Meteo historical weather API (ERA5 reanalysis)", OM, None, "CC BY 4.0 (Open-Meteo, ECMWF ERA5)",
                  f"daily Tmax, RH min, wind max, rain per fire >= {MIN_HA} ha")
    record_source("NASA POWER daily point API (MERRA-2)", POWER, None, "NASA open data",
                  "daily PRECTOTCORR, T2M_MAX, T2M_MIN 1991–2025 per 0.5° cell")
    return out


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(DATA.parent))
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    (DATA / "enrich").mkdir(exist_ok=True)
    run(ev, DATA / "enrich/weather.parquet")
