"""Build the NSW fire-event workbook (one row per fire × LGA), 2015–2025. No models are fitted.

    uv run --no-sync --with openpyxl python fire_event_dataset/build_all.py

Enrichment modules (weather, hotspots, terrain, severity, vegetation, economy) each save a result file in
data/enrich/; this script merges whichever exist, so the workbook can be rebuilt as they complete.
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from src import export, socio  # noqa: E402
from src.common import AUSSEF_DB, DATA, OUT, sha256  # noqa: E402
from src.fires import GA_ZIP, GA_ZIP_SHA256, load_fire_events  # noqa: E402
from src.regions import load_lgas, road_exposure, split_by_lga  # noqa: E402

ENRICH = DATA / "enrich"
CACHE = DATA / "cache"

EXTRAS_DOC = {
    "fire_type_flag": ("GA fire type: bushfire, or type unknown (never prescribed)", "category", "GA", ""),
    "ignition_cause": ("Recorded ignition cause", "category", "GA", "often blank for historical records"),
    "agency": ("Mapping agency", "str", "GA", ""),
    "capture_method": ("How the outline was captured", "str", "GA", ""),
    "ga_source": ("GA layer holding the record", "str", "GA", "GA_V2 historical, GA_RECENT_3 2020–25"),
    "ga_fire_ids": ("Agency fire ID(s)", "str", "GA", ""),
    "date_end_note": ("Why date_end is blank although GA has a value", "str", "GA", "end before start in the source record"),
    "centroid_lat": ("Fire centroid latitude (point inside the fire)", "deg", "GA outline", ""),
    "centroid_lon": ("Fire centroid longitude", "deg", "GA outline", ""),
    "region_burn_area_ha": ("Burned area inside this LGA (ha)", "ha", "GA outline × ABS LGA", ""),
    "region_share_of_fire": ("Share of the fire inside this LGA", "fraction", "", ""),
    "share_of_region_burned": ("Share of the LGA burned by this fire", "fraction", "", ""),
    "road_km_within_100m": ("Road km within 100 m of the fire in this LGA", "km", "2019 OSM network", ""),
    "official_declaration_agrn": ("Matching NSW bushfire disaster declaration (AGRN)", "str",
                                  "AUSSEF disaster declarations", "declaration for this LGA starting within 30 days before to the end of the fire"),
    "official_declaration_name": ("Declared event name", "str", "AUSSEF disaster declarations", ""),
    "historical_bushfire_declarations_10y": ("Declared bushfire disasters for the LGA, previous 10 years", "int", "", ""),
    "population_prev_year": ("LGA population, year before the fire", "persons", "ABS ERP (Regional population 2024-25)", "2025 LGA boundaries"),
    "IL_total_income_change_pct_proxy": ("Total personal income change, event FY vs previous (%)", "%",
                                         "ABS Personal Income in Australia", "proxy for GRP change"),
    "X16_regional_GDP_proxy_total_income_aud": ("Total personal income, FY before (AUD)", "AUD", "ABS PIA", "proxy for regional GDP"),
    "FP_debt_ratio_change_raw": ("Change in debt service ratio, event FY vs previous (pp)", "pp", "AUSSEF fiscal panel", ""),
    "FP_operating_ratio_change_proxy": ("Change in operating ratio, event FY vs previous (pp)", "pp", "AUSSEF fiscal panel", ""),
    "FP_cash_cover_change_proxy": ("Change in cash cover, event FY vs previous (months)", "months", "AUSSEF fiscal panel", ""),
}


def lga_year_table(lga):
    rows = []
    pop, inc, sf, fis = socio.population(), socio.income(), socio.seifa(), socio.fiscal()
    for code, name, area in zip(lga.LGA_CODE21.astype(str), lga.LGA_NAME21, lga.AREASQKM21):
        key = socio.norm(name)
        for y in range(2014, 2026):
            r = dict(region_id=code, region_name=name, year=y, area_km2=area,
                     population=pop.get((code, y), np.nan),
                     seifa_irsd=sf.get((code, 2016 if y <= 2020 else 2021), np.nan))
            if (code, y) in inc.index:
                v = inc.loc[(code, y)]
                r.update(median_income_aud_fy=v.median_income_aud, total_income_aud_fy=v.total_income_aud,
                         income_earners_fy=v.income_earners)
            if (key, y) in fis.index:
                f = fis.loc[(key, y)]
                r.update({f"fiscal_{c}_fy": f[c] for c in fis.columns})
            rows.append(r)
    t = pd.DataFrame(rows)
    t["population_density"] = t.population / t.area_km2
    for p in sorted((DATA / "enrich_lga").glob("*.parquet")):
        d = pd.read_parquet(p)
        d["region_id"] = d.region_id.astype(str)
        t = t.merge(d, on=["region_id", "year"], how="left")
    return t


def main():
    OUT.mkdir(exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    assert sha256(GA_ZIP) == GA_ZIP_SHA256, "GA historical zip hash mismatch"
    db_before = sha256(AUSSEF_DB)

    ev_path, pieces_path = CACHE / "fires.parquet", CACHE / "fire_lga_pieces.parquet"
    if ev_path.exists() and pieces_path.exists():
        ev, pieces = gpd.read_parquet(ev_path), gpd.read_parquet(pieces_path)
        counts = json.loads((CACHE / "fire_counts.json").read_text())
    else:
        ev, counts = load_fire_events()
        lga = load_lgas()
        pieces = road_exposure(split_by_lga(ev, lga))
        ev.to_parquet(ev_path)
        pieces.to_parquet(pieces_path)
        (CACHE / "fire_counts.json").write_text(json.dumps(counts, indent=2))
    print("fires", counts, flush=True)

    r = socio.attach(pd.DataFrame(pieces.drop(columns="geometry")), ev)
    e = ev.drop(columns="geometry").set_index("event_id")
    r["event_name"] = r.event_id.map(e.event_name)
    r["region_id"], r["region_name"] = r.LGA_CODE21.astype(str), r.LGA_NAME21
    r["year"] = r.event_id.map(e.year)
    r["date_start"] = r.event_id.map(e.start).dt.date
    r["date_end"] = r.event_id.map(e.end).dt.date
    # GA records with an end date before the start (1969-12-31 empty-date placeholders or typos) -> blank, flagged
    bad = pd.to_datetime(r.date_end) < pd.to_datetime(r.date_start)
    r["date_end_note"] = np.where(bad, "source end date " + r.date_end.astype(str) + " is before the start: blanked", "")
    r.loc[bad, "date_end"] = pd.NaT
    r["X1_burn_area"] = r.event_id.map(e.burn_area_ha)
    r["X4_fire_duration"] = r.event_id.map(e.duration_days)
    r["X14_road_exposure"] = r.road_km_inside
    for c in ("fire_type_flag", "ignition_cause", "agency", "capture_method", "ga_fire_ids", "centroid_lat", "centroid_lon"):
        r[c] = r.event_id.map(e[c])
    r["ga_source"] = r.event_id.map(e.source)

    # merge any finished enrichments (keyed by event_id, or event_id + region_id)
    merged = []
    for p in sorted(ENRICH.glob("*.parquet")) if ENRICH.exists() else []:
        d = pd.read_parquet(p)
        keys = ["event_id", "region_id"] if "region_id" in d.columns else ["event_id"]
        r = r.drop(columns=[c for c in d.columns if c not in keys and c in r.columns]).merge(d, on=keys, how="left")
        merged.append(p.stem)
        doc = HERE / "data/enrich" / f"{p.stem}.doc.json"
        if doc.exists():
            EXTRAS_DOC.update({k: tuple(v) for k, v in json.loads(doc.read_text()).items()})

    drop = ["LGA_CODE21", "LGA_NAME21", "AREASQKM21", "key", "fy", "road_km_inside"]
    r = r.drop(columns=[c for c in drop if c in r.columns]).sort_values(["date_start", "event_id", "region_id"])
    lga_year = lga_year_table(load_lgas())
    xlsx, dic = export.write(r, lga_year, EXTRAS_DOC)
    assert sha256(AUSSEF_DB) == db_before, "aussef.duckdb changed"
    meta = dict(rows=len(r), fires=int(r.event_id.nunique()), enrichments=merged, counts=counts)
    (OUT / "build_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print(json.dumps(meta, indent=2, default=str))
    print(dic[dic.in_template == "yes"][["column", "coverage_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
