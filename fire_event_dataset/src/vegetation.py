"""X12 vegetation (dominant NVIS Major Vegetation Group) and X13 canopy cover (Hansen tree cover 2000) inside each fire.

- NVIS 6.0 Present MVG, 100 m, EPSG:3577, fetched for the NSW fire extent from the MDBA ImageServer (src/nvis_fetch.py).
  NVIS 7.0 is published only as an ArcGIS FileGDB raster, which the GDAL in the rasterio wheel cannot read.
- Hansen Global Forest Change v1.11 treecover2000 (% canopy closure for vegetation taller than 5 m, year 2000), 30 m.
Run with: uv run --no-sync --with rasterio python -m src.vegetation
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from shapely.geometry import box
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds

from src.common import DATA, record_source

NVIS = DATA / "nvis/nvis6_mvg_nsw.tif"
HANSEN = sorted((DATA / "hansen").glob("tc_*.tif"))
HANSEN_URL = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_treecover2000_{t}.tif"
MIN_HA, MAX_PX = 0, 4000
MVG = {1: "Rainforests and Vine Thickets", 2: "Eucalypt Tall Open Forests", 3: "Eucalypt Open Forests",
       4: "Eucalypt Low Open Forests", 5: "Eucalypt Woodlands", 6: "Acacia Forests and Woodlands",
       7: "Callitris Forests and Woodlands", 8: "Casuarina Forests and Woodlands", 9: "Melaleuca Forests and Woodlands",
       10: "Other Forests and Woodlands", 11: "Eucalypt Open Woodlands", 12: "Tropical Eucalypt Woodlands/Grasslands",
       13: "Acacia Open Woodlands", 14: "Mallee Woodlands and Shrublands",
       15: "Low Closed Forests and Tall Closed Shrublands", 16: "Acacia Shrublands", 17: "Other Shrublands",
       18: "Heathlands", 19: "Tussock Grasslands", 20: "Hummock Grasslands",
       21: "Other Grasslands, Herblands, Sedgelands and Rushlands",
       22: "Chenopod Shrublands, Samphire Shrublands and Forblands", 23: "Mangroves",
       24: "Inland Aquatic - freshwater, salt lakes, lagoons", 25: "Cleared, non-native vegetation, buildings",
       26: "Unclassified native vegetation", 27: "Naturally bare - sand, rock, claypan, mudflat",
       28: "Sea and estuaries", 29: "Regrowth, modified native vegetation", 30: "Unclassified Forest",
       31: "Other Open Woodlands", 32: "Mallee Open Woodlands and Sparse Mallee Shrublands", 99: "Unknown/no data"}
FOREST = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30}


def pixels(src, geom):
    """Values of src inside geom (geom in src CRS); large areas read with a nearest-neighbour stride."""
    l, b, r, t = geom.bounds
    win = from_bounds(l, b, r, t, src.transform).round_offsets().round_lengths()
    h, w = int(win.height) + 1, int(win.width) + 1
    k = max(1, int(np.ceil(max(h, w) / MAX_PX)))
    arr = src.read(1, window=win, out_shape=(max(1, h // k), max(1, w // k)), boundless=True,
                   fill_value=src.nodata if src.nodata is not None else 255, resampling=Resampling.nearest)
    tr = src.window_transform(win) * rasterio.Affine.scale(w / arr.shape[1], h / arr.shape[0])
    inside = geometry_mask([geom], out_shape=arr.shape, transform=tr, invert=True, all_touched=True)
    return arr[inside]


def run(ev, out_path):
    big = ev[ev.burn_area_ha >= MIN_HA]
    nv = rasterio.open(NVIS)
    hs = [rasterio.open(p) for p in HANSEN]
    g4326 = big.geometry.to_crs(4326)
    rows = []
    for n_, (eid, g, g4) in enumerate(zip(big.event_id, big.geometry, g4326)):
        row = dict(event_id=eid)
        v = pixels(nv, g)
        v = v[(v >= 1) & (v <= 32)]
        if len(v):
            u, c = np.unique(v, return_counts=True)
            top = int(u[c.argmax()])
            row.update(X12_vegetation=MVG[top], vegetation_mvg_code=top, vegetation_dominant_share=c.max() / len(v),
                       vegetation_forest_share=float(np.isin(v, list(FOREST)).mean()),
                       vegetation_cleared_share=float((v == 25).mean()))
        tc = []
        for h in hs:
            tile = box(*h.bounds)
            if g4.intersects(tile):
                part = pixels(h, g4.intersection(tile))
                tc.append(part[part <= 100])
        tc = np.concatenate(tc) if tc else np.array([])
        if len(tc):
            row.update(X13_canopy_cover=float(tc.mean()), canopy_cover_share_over_30pct=float((tc > 30).mean()))
        rows.append(row)
        if n_ % 300 == 0:
            print(f"  vegetation {n_}/{len(big)}", flush=True)
    out = pd.DataFrame(rows)
    out = pd.concat([out, ev.loc[ev.burn_area_ha < MIN_HA, ["event_id"]].assign(
        vegetation_note=f"fire < {MIN_HA} ha: not computed")], ignore_index=True)
    out.to_parquet(out_path)
    doc = {"vegetation_mvg_code": ["NVIS Major Vegetation Group number of X12", "int", "NVIS 6.0", ""],
           "vegetation_dominant_share": ["Share of the fire in the dominant group", "fraction", "NVIS 6.0", ""],
           "vegetation_forest_share": ["Share of the fire in forest or woodland groups (MVG 1–10, 30)", "fraction", "NVIS 6.0", ""],
           "vegetation_cleared_share": ["Share of the fire that is cleared / non-native (MVG 25)", "fraction", "NVIS 6.0", ""],
           "canopy_cover_share_over_30pct": ["Share of the fire with tree cover over 30%", "fraction", "Hansen 2000", ""],
           "vegetation_note": ["Why vegetation is blank", "str", "", ""]}
    Path(str(out_path).replace(".parquet", ".doc.json")).write_text(json.dumps(doc, indent=1))
    record_source("NVIS 6.0 Present Major Vegetation Groups (MDBA ImageServer export, 100 m, EPSG:3577)",
                  "https://gis.mdba.gov.au/arcgis/rest/services/Vegetation/NVIS_Version_6_0_Australia_Present_Major_Vegetation_Groups/ImageServer",
                  NVIS, "CC BY 4.0 (DCCEEW)", "tiles 2000 px, mosaicked by src/nvis_fetch.py")
    for p in HANSEN:
        t = p.stem.replace("tc_", "")
        record_source(f"Hansen GFC v1.11 treecover2000 {t}", HANSEN_URL.format(t=t), p, "CC BY 4.0", "")
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    out = run(ev, DATA / "enrich/vegetation.parquet")
    print(out.describe().T.to_string())
    print(out.X12_vegetation.value_counts().head(12))
