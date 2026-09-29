"""Exposure v2: share of each council's dwellings and residents that sit inside BFPL Category 1-2 land.

Uses real housing locations instead of an even-density guess:
  ABS 2016 Census Mesh Block counts (dwellings, residents) x ABS ASGS 2016 Mesh Block polygons, split at
  ABS LGA 2021 council lines (both steps reuse fire_event_dataset/src/affected_pop.py unchanged), then each piece is
  weighted by the share of its area inside BFPL Cat 1 or 2 (allocation rule: people are spread evenly over each Mesh
  Block, the same assumption as the dataset's other people-in-fire columns).

Vintage: 2016 Census, i.e. up to about one year after the first fires in the data (2015); the dataset uses the
same convention. BFPL is the current mapping. Overlapping BFPL polygons are capped at 100% of a piece.

Output: results/COUNCIL_EXPOSURE_BFPL.csv (per council: dwellings, residents, share in BFPL Cat 1-2, counts).

Run from the repository root:
  uv run --no-sync --with geopandas --with shapely --with pyarrow --with pyogrio python "Experiment 6/build_exposure_bfpl.py"
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'fire_event_dataset'))
from src import affected_pop as ap            # noqa: E402
from src.regions import load_lgas             # noqa: E402

OUT = ROOT / 'results'
BFPL = ROOT.parent / 'fire_event_dataset/data/bfpl'
CRS = 3577


def load_bfpl_cat12():
    parts = []
    for f in sorted(BFPL.glob('page_*.json')):
        g = gpd.read_file(f)
        parts.append(g.loc[g.Category.isin([1, 2]), ['OBJECTID', 'Category', 'geometry']])
    b = pd.concat(parts, ignore_index=True)
    b = gpd.GeoDataFrame(b, geometry='geometry', crs=4326).to_crs(CRS)
    b['geometry'] = shapely.make_valid(b.geometry.values)
    return b


def main():
    counts = ap.load_counts(2016)
    mb, info1 = ap.load_mb(2016, counts)
    lga = load_lgas()
    pieces, info2 = ap.split_mb_by_lga(mb, lga)
    print(info1, info2, len(pieces), flush=True)

    bfpl = load_bfpl_cat12()
    print('BFPL Cat 1-2 polygons', len(bfpl), flush=True)
    bg = bfpl.geometry.values
    tree = shapely.STRtree(bg)
    pg = pieces.geometry.values
    pi, bi = tree.query(pg, predicate='intersects')
    # area of each (piece, BFPL polygon) intersection, summed per piece, capped at the piece area
    inter = shapely.area(shapely.intersection(pg[pi], bg[bi]))
    in_area = np.bincount(pi, weights=inter, minlength=len(pieces))
    pieces['bfpl12_frac'] = np.minimum(1.0, in_area / pieces.area.values)
    pieces['dw_in'] = pieces.dwelling * pieces.bfpl12_frac
    pieces['pp_in'] = pieces.person * pieces.bfpl12_frac
    g = pieces.groupby('region_id').agg(dwellings_mb=('dwelling', 'sum'), residents_mb=('person', 'sum'),
                                        dwellings_in_bfpl12=('dw_in', 'sum'), residents_in_bfpl12=('pp_in', 'sum'))
    g['dwellings_in_bfpl12_share'] = g.dwellings_in_bfpl12 / g.dwellings_mb
    g['residents_in_bfpl12_share'] = g.residents_in_bfpl12 / g.residents_mb
    names = lga[['LGA_CODE21', 'LGA_NAME21']].astype({'LGA_CODE21': str}) if 'LGA_NAME21' in lga else None
    g = g.reset_index()
    g['region_id'] = g.region_id.astype(int)
    if names is not None:
        g = g.merge(names.rename(columns={'LGA_CODE21': 'region_id', 'LGA_NAME21': 'region_name'}).assign(
            region_id=lambda d: d.region_id.astype(int)), on='region_id', how='left')
    g.to_csv(OUT / 'COUNCIL_EXPOSURE_BFPL.csv', index=False)
    print(g.describe().T[['count', 'min', 'mean', 'max']])


if __name__ == '__main__':
    main()
