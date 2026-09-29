"""Council-wide fire-hazard features for every NSW LGA (ABS LGA 2021 boundaries).

  bfpl_share_any    share of the council area inside any NSW Bush Fire Prone Land polygon
                    (Category 1, 2, 3 and the vegetation buffer)
  bfpl_share_cat1   share of the council area in Category 1 (highest risk vegetation)
  bfpl_share_cat12  share in Category 1 or 2
  nvis_forest_share share of the council in NVIS 6.0 forest / woodland groups (MVG 1-10, 30)

BFPL: NSW RFS / DPHI 'NSW Bush Fire Prone Land' via the ePlanning service (see fetch_bfpl.py).
Geometry generalised to ~30 m. The layer is the current (post-2019) mapping, not a 2014 snapshot.

Run: uv run --no-sync --with geopandas --with shapely --with pyarrow --with rasterio python build_council_hazard.py
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import shapely
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'fire_event_dataset/data'
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
ALBERS = 3577
FOREST = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30}


def load_lgas():
    d = pd.read_parquet(DATA / 'cache/lga2021_nsw_geom.parquet')
    d['geometry'] = shapely.from_wkb(d.geometry)
    return gpd.GeoDataFrame(d, geometry='geometry', crs=4283).to_crs(ALBERS)


def load_bfpl():
    parts = []
    for f in sorted((DATA / 'bfpl').glob('page_*.json')):
        g = gpd.read_file(f)
        parts.append(g[['OBJECTID', 'Category', 'geometry']])
    b = pd.concat(parts, ignore_index=True)
    b = gpd.GeoDataFrame(b, geometry='geometry', crs=4326).to_crs(ALBERS)
    b['geometry'] = shapely.make_valid(b.geometry.values)
    assert b.OBJECTID.is_unique, 'duplicate BFPL objects across pages'
    return b


def share(tree, geoms, cats, lga_geom, mask):
    idx = tree.query(lga_geom, predicate='intersects')
    idx = [i for i in idx if mask[i]]
    if not idx:
        return 0.0
    u = shapely.union_all(shapely.intersection(geoms[idx], lga_geom))
    return float(u.area / lga_geom.area)


def nvis_forest(lga):
    src = rasterio.open(DATA / 'nvis/nvis6_mvg_nsw.tif')
    out = {}
    for rid, g in zip(lga.region_id, lga.geometry):
        l, b, r, t = g.bounds
        win = from_bounds(l, b, r, t, src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=win, boundless=True, fill_value=src.nodata)
        tr = src.window_transform(win)
        inside = geometry_mask([g], out_shape=arr.shape, transform=tr, invert=True, all_touched=False)
        v = arr[inside]
        v = v[v != src.nodata]
        out[rid] = float(np.isin(v, list(FOREST)).mean()) if len(v) else np.nan
    return out


def main():
    lga = load_lgas()
    bfpl = load_bfpl()
    print('BFPL polygons', len(bfpl), 'LGAs', len(lga), flush=True)
    geoms = bfpl.geometry.values
    cat = bfpl.Category.values
    tree = shapely.STRtree(geoms)
    masks = {'any': np.ones(len(bfpl), bool), 'cat1': cat == 1, 'cat12': np.isin(cat, [1, 2])}
    rows = []
    for k, (rid, name, g) in enumerate(zip(lga.region_id, lga.region_name, lga.geometry)):
        row = dict(region_id=int(rid), region_name=name, area_km2_geom=g.area / 1e6)
        for key, m in masks.items():
            row[f'bfpl_share_{key}'] = share(tree, geoms, cat, g, m)
        rows.append(row)
        print(k, name, round(row['bfpl_share_any'], 3), flush=True)
    df = pd.DataFrame(rows)
    df['nvis_forest_share'] = df.region_id.map(nvis_forest(lga.assign(region_id=lga.region_id.astype(int))))
    df.to_csv(OUT / 'COUNCIL_HAZARD.csv', index=False)
    meta = dict(bfpl_polygons=int(len(bfpl)), categories={int(k): int(v) for k, v in bfpl.Category.value_counts().items()},
                lgas=int(len(df)), note='BFPL generalised to ~30 m; current mapping vintage')
    (OUT / 'COUNCIL_HAZARD_META.json').write_text(json.dumps(meta, indent=2))
    print(df.describe().T)


if __name__ == '__main__':
    main()
