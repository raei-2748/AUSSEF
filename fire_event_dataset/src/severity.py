"""X6 severity: NSW Fire Extent and Severity Mapping (FESM) classes inside each fire outline (fires >= 10 ha).

FESM classes: 1 unburnt, 2 low, 3 moderate, 4 high, 5 extreme (full canopy consumption); 0 = outside mapped extent.
One raster per fire season (July–June) from SEED, read directly from the zip; the 2021-22 grid (66 GB unzipped) is
first streamed to a 30 m GeoTIFF by src/fesm_convert.py.
X6 = share of burnt pixels (classes 2–5) that are high or extreme. The fire's start season is used; if under 20% of
the outline is mapped there, the next season is tried (fires that ran over 30 June).
Run with: uv run --no-sync --with rasterio python -m src.severity
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds

from src.common import DATA, REPO, record_source

Z = "/vsizip/" + str(DATA / "fesm")
RASTERS = {
    2014: f"{Z}/fesm_201415.zip/cvmsre_NSWWildfire_20142015_ag1l0.img",
    2015: f"{Z}/fesm_201516.zip/cvmsre_NSWWildfire_20152016_ag1l0.img",
    2016: f"{Z}/fesm_201617.zip/Fire_FESM_2016_17_GRID_Data/fesm201617",
    2017: f"{Z}/fesm_201718.zip/FESM_201718/fesm201718",
    2018: f"{Z}/fesm_201819.zip/FESM_201819/fesm201819",
    2019: str(REPO / "data/Manual/FireSeverityFESM/fesm_201920"),
    2020: f"{Z}/fesm_202021b.zip/fesm_20_21",
    2021: str(DATA / "fesm/fesm_202122_30m.tif"),  # 66 GB grid streamed to 30 m by src/fesm_convert.py
    2022: f"{Z}/fesm_202223.zip/fesm2223",
    2023: f"{Z}/fesm_202324.zip/fesm2324",
    2024: f"{Z}/fesm_202425.zip/fesmWFs2425_grid/fesmwfs2425",
    2025: f"{Z}/fesm_202526.zip/FESM_GRID20260331/fesm20260331",
}
MIN_HA, MAX_PX, MIN_MAPPED = 10, 4000, 0.2
NAMES = {1: "unburnt", 2: "low", 3: "moderate", 4: "high", 5: "extreme"}


def season(ts):
    ts = pd.Timestamp(ts)
    return ts.year if ts.month >= 7 else ts.year - 1


def classes(src, geom):
    l, b, r, t = geom.bounds
    win = from_bounds(l, b, r, t, src.transform).round_offsets().round_lengths()
    h, w = int(win.height) + 1, int(win.width) + 1
    k = max(1, int(np.ceil(max(h, w) / MAX_PX)))  # decimate very large fires (nearest neighbour)
    arr = src.read(1, window=win, out_shape=(max(1, h // k), max(1, w // k)), boundless=True, fill_value=0,
                   resampling=Resampling.nearest)
    tr = src.window_transform(win) * rasterio.Affine.scale(w / arr.shape[1] if k > 1 else 1, h / arr.shape[0] if k > 1 else 1)
    inside = geometry_mask([geom], out_shape=arr.shape, transform=tr, invert=True, all_touched=False)
    v = arr[inside]
    n = int(inside.sum())
    counts = {c: int((v == c).sum()) for c in NAMES}
    return n, counts, k


def run(ev, out_path):
    big = ev[ev.burn_area_ha >= MIN_HA].copy()
    big["season"] = big.start.map(season)
    srcs = {y: rasterio.open(p) for y, p in RASTERS.items()}
    geoms = {y: None for y in srcs}
    rows = []
    for n_, r in enumerate(big.itertuples()):
        row = dict(event_id=r.event_id)
        for y in (r.season, r.season + 1):
            if y not in srcs:
                continue
            g = gpd.GeoSeries([r.geometry], crs=3577).to_crs(srcs[y].crs).iloc[0]
            n, c, k = classes(srcs[y], g)
            mapped = sum(c.values())
            if n and mapped / n >= MIN_MAPPED:
                burnt = c[2] + c[3] + c[4] + c[5]
                row.update(X6_severity=(c[4] + c[5]) / burnt if burnt else np.nan,
                           severity_mapped_share=mapped / n, severity_season=f"{y}-{str(y + 1)[2:]}",
                           severity_decimation=k,
                           **{f"severity_share_{NAMES[i]}": c[i] / mapped for i in NAMES})
                break
        else:
            row["severity_note"] = "outline not mapped by FESM (under 20% coverage) in start or next season"
        rows.append(row)
        if n_ % 300 == 0:
            print(f"  severity {n_}/{len(big)}", flush=True)
    out = pd.DataFrame(rows)
    out = pd.concat([out, ev.loc[ev.burn_area_ha < MIN_HA, ["event_id"]].assign(
        severity_note=f"fire < {MIN_HA} ha: not computed")], ignore_index=True)
    out.to_parquet(out_path)
    doc = {"severity_mapped_share": ["Share of the outline covered by FESM mapping", "fraction", "NSW FESM", ""],
           "severity_season": ["FESM season used", "str", "NSW FESM", "July–June"],
           "severity_decimation": ["Pixel stride used (1 = full resolution)", "int", "", "very large fires sampled"],
           "severity_note": ["Why severity is blank", "str", "", ""]}
    doc.update({f"severity_share_{v}": [f"Share of mapped pixels in the {v} class", "fraction", "NSW FESM", ""]
                for v in NAMES.values()})
    Path(str(out_path).replace(".parquet", ".doc.json")).write_text(json.dumps(doc, indent=1))
    record_source("NSW Fire Extent and Severity Mapping (FESM), seasons 2014-15 to 2025-26",
                  "https://datasets.seed.nsw.gov.au/dataset/fire-extent-and-severity-mapping-fesm", DATA / "fesm/urls.txt",
                  "CC BY 4.0 (NSW DCCEEW)", "one raster per season from SEED; 2019-20 from data/Manual; 2020-21 fireseverityfesm.zip")
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    out = run(ev, DATA / "enrich/severity.parquet")
    print(out.describe().T.to_string())
    print(out.severity_note.value_counts())
