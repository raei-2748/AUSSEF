"""X5 hotspot density: DEA Hotspots (satellite fire detections) inside each fire outline during the fire, per km².

One WFS query per fire: the outline's bounding box, from the day before the start to the day after the end
(capped at 120 days). Reuses the pilot's DEA downloader (cached per fire under data/hotspot_cache/).
DEA combines several products (MODIS, VIIRS, AVHRR, Himawari), so one fire pixel can appear in several products;
X5 counts all detections, and a VIIRS-only density is given separately for a consistent sensor.
Density = detections inside the outline + 500 m buffer, divided by the area of that buffered outline (km²).
"""
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from src.common import DATA, REPO, record_source

_spec = importlib.util.spec_from_file_location("pilot_hotspots", REPO / "pilot_exit_correlation/stage3/s3/hotspots.py")
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

CACHE = DATA / "hotspot_cache"
MIN_HA, MAX_DAYS, BUFFER_M = 0, 120, 500


def _one(r):
    s = pd.Timestamp(r.start).normalize() - pd.Timedelta(days=1)
    e = pd.Timestamp(r.end).normalize() if pd.notna(r.end) else pd.Timestamp(r.start).normalize()
    e = min(max(e, s), s + pd.Timedelta(days=MAX_DAYS)) + pd.Timedelta(days=2)
    g = gpd.GeoSeries([r.geometry], crs=3577).buffer(BUFFER_M).to_crs(4326)
    bbox = tuple(g.total_bounds)
    H.fetch_event(r.event_id, bbox, s.strftime("%Y-%m-%dT00:00:00Z"), e.strftime("%Y-%m-%dT00:00:00Z"), CACHE)
    pts = pd.read_parquet(CACHE / f"{r.event_id}.parquet")
    area_km2 = g.to_crs(3577).iloc[0].area / 1e6  # searched area: outline + buffer (keeps tiny fires comparable)
    if len(pts):
        p = gpd.GeoDataFrame(pts, geometry=gpd.points_from_xy(pts.longitude, pts.latitude), crs=4326).to_crs(3577)
        inside = p[p.within(g.to_crs(3577).iloc[0])]
    else:
        inside = pts
    viirs = inside[inside.sensor.astype(str).str.upper().str.contains("VIIRS")] if len(inside) else inside
    return dict(event_id=r.event_id, X5_hotspot_density=len(inside) / area_km2, hotspot_count=len(inside),
                hotspot_viirs_count=len(viirs), hotspot_viirs_density=len(viirs) / area_km2,
                hotspot_first_utc=str(inside.datetime.min()) if len(inside) else "",
                hotspot_last_utc=str(inside.datetime.max()) if len(inside) else "")


def run(ev, out_path, workers=4):
    CACHE.mkdir(parents=True, exist_ok=True)
    big = ev[ev.burn_area_ha >= MIN_HA]
    rows = []
    with ThreadPoolExecutor(workers) as ex:
        for n, row in enumerate(ex.map(_one, big.itertuples())):
            rows.append(row)
            if n % 200 == 0:
                print(f"  hotspots {n}/{len(big)}", flush=True)
    out = pd.DataFrame(rows)
    small = ev.loc[ev.burn_area_ha < MIN_HA, ["event_id"]].assign(hotspot_note=f"fire < {MIN_HA} ha: not queried")
    out = pd.concat([out, small], ignore_index=True)
    out.to_parquet(out_path)
    doc = {
        "hotspot_count": ["Satellite hotspots inside the outline (+500 m) during the fire", "count", "DEA Hotspots", "all products"],
        "hotspot_viirs_count": ["VIIRS hotspots inside the outline during the fire", "count", "DEA Hotspots", ""],
        "hotspot_viirs_density": ["VIIRS hotspots per km² of burned area", "per km²", "DEA Hotspots", ""],
        "hotspot_first_utc": ["First hotspot time inside the outline", "UTC", "DEA Hotspots", ""],
        "hotspot_last_utc": ["Last hotspot time inside the outline", "UTC", "DEA Hotspots", ""],
        "hotspot_note": ["Why hotspot columns are blank", "str", "", ""],
    }
    Path(str(out_path).replace(".parquet", ".doc.json")).write_text(json.dumps(doc, indent=1))
    record_source("DEA Hotspots WFS (Geoscience Australia)", H.WFS, None, "CC BY 4.0",
                  f"per fire >= {MIN_HA} ha: bbox of outline + {BUFFER_M} m, day before start to day after end")
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    (DATA / "enrich").mkdir(exist_ok=True)
    run(ev, DATA / "enrich/hotspots.parquet")
