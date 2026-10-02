"""Step 2b-1: H and E raw items for the SA roster councils (PRESPEC section 2). X side only; no outcome is read.

H: share of council area in BPA High (h1) and High+Medium (h2), area shares in EPSG:3577, overlapping polygons unioned.
   A council is 'mapped' if it has >= 1 ha of any BPA class inside (implementation tolerance for boundary slivers, recorded per council).
E: share of dwellings (e1) and residents (e2) inside BPA High+Medium, recipe of build_exposure_bfpl.py with ABS 2021 mesh-block counts and
   2021 mesh-block polygons (SA): dwellings/persons spread evenly over each mesh block, mesh blocks split at the council lines of the row's LGA
   edition, weighted by the area share inside BPA High+Medium.
Output: results/geo_items_sa.csv
Run: /Users/ray/Research/AUSSEF - Local/.venv/bin/python build_geo_items.py
"""
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

warnings.filterwarnings('ignore')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'inputs'))
import overlay_candidates as oc          # noqa: E402

CRS = 3577
RES = HERE / 'results'
FED = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset')
roster = pd.read_csv(RES / 'roster.csv', dtype={'lga_code': str, 'code_lga2018': str, 'code_lga2015': str})

bpa = gpd.read_file(f'zip://{FED}/data/raw/extra_fires/p2_sa_bpa/BushfireProtectionAreas_shp.zip!BushfireProtectionAreas_GDA94.shp').to_crs(CRS)
bpa['geometry'] = shapely.make_valid(bpa.geometry.values)
u_high = shapely.union_all(bpa[bpa.bf_code == 'High'].geometry.values)
u_hm = shapely.union_all(bpa[bpa.bf_code.isin(['High', 'Medium'])].geometry.values)
u_any = shapely.union_all(bpa.geometry.values)

# mesh blocks (SA) with 2021 counts
mb = gpd.read_file(f'zip://{FED}/data/raw/pop/MB_2021_AUST_SHP_GDA94.zip!MB_2021_AUST_GDA94.shp', where="STE_CODE21 = '4'")[['MB_CODE21', 'geometry']]
mb = mb.to_crs(CRS)
mb['geometry'] = shapely.make_valid(mb.geometry.values)
cnt = pd.read_csv(FED / 'data/extra_fires/mb2021_sa_counts.csv', dtype={'MB_CODE_2021': str})
mb = mb.merge(cnt[['MB_CODE_2021', 'Dwelling', 'Person']].rename(columns={'MB_CODE_2021': 'MB_CODE21'}), on='MB_CODE21', how='left')
mb = mb[(mb.Dwelling.fillna(0) > 0) | (mb.Person.fillna(0) > 0)].reset_index(drop=True)
mb['mb_area'] = mb.geometry.area
print('SA mesh blocks with counts', len(mb), 'dwellings', mb.Dwelling.sum(), 'persons', mb.Person.sum())

rows = []
for vint in sorted(roster.lga_vintage.astype(str).unique()):
    L = oc.load_lga(vint)
    L = L[L.lga_code.str[0] == '4']
    codes = roster[roster.lga_vintage.astype(str) == vint].lga_code.unique()
    Lr = L[L.lga_code.isin(codes)]
    # split mesh blocks at these council lines
    pieces = gpd.overlay(mb[['MB_CODE21', 'Dwelling', 'Person', 'mb_area', 'geometry']], Lr[['lga_code', 'geometry']], how='intersection', keep_geom_type=True)
    pieces['frac'] = pieces.geometry.area / pieces.mb_area
    pieces['dw'] = pieces.Dwelling * pieces.frac
    pieces['pp'] = pieces.Person * pieces.frac
    pg = pieces.geometry.values
    inter = shapely.area(shapely.intersection(pg, u_hm))
    pieces['in_frac'] = np.minimum(1.0, inter / pieces.geometry.area.values)
    pieces['dw_in'] = pieces.dw * pieces.in_frac
    pieces['pp_in'] = pieces.pp * pieces.in_frac
    g = pieces.groupby('lga_code').agg(dwellings_mb=('dw', 'sum'), residents_mb=('pp', 'sum'), dw_in=('dw_in', 'sum'), pp_in=('pp_in', 'sum'))
    for r in Lr.itertuples():
        area = r.geometry.area
        a_high = shapely.area(shapely.intersection(r.geometry, u_high))
        a_hm = shapely.area(shapely.intersection(r.geometry, u_hm))
        a_any = shapely.area(shapely.intersection(r.geometry, u_any))
        gg = g.loc[r.lga_code] if r.lga_code in g.index else None
        rows.append(dict(lga_vintage=vint, lga_code=r.lga_code, lga_name=r.lga_name, council_area_km2=area / 1e6,
                         bpa_any_ha=a_any / 1e4, mapped=bool(a_any / 1e4 >= 1.0),
                         h1_bpa_high_share=a_high / area, h2_bpa_high_medium_share=a_hm / area,
                         dwellings_mb2021=gg.dwellings_mb if gg is not None else np.nan, residents_mb2021=gg.residents_mb if gg is not None else np.nan,
                         e1_dwellings_in_bpa_hm_share=(gg.dw_in / gg.dwellings_mb) if gg is not None and gg.dwellings_mb > 0 else np.nan,
                         e2_residents_in_bpa_hm_share=(gg.pp_in / gg.residents_mb) if gg is not None and gg.residents_mb > 0 else np.nan))
G = pd.DataFrame(rows)
G.to_csv(RES / 'geo_items_sa.csv', index=False)
print(G.round(4).to_string())
