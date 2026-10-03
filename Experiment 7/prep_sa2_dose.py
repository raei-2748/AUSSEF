"""Experiment 7, Day 5 prep: share of each NSW SA2's residents (Census 2021 mesh blocks, area-weighted) inside or
within 1 km of the union of fires starting in each financial year. Outcome-free.
Run: PYTHONDONTWRITEBYTECODE=1 ../.venv/bin/python prep_sa2_dose.py"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

HERE = Path(__file__).resolve().parent
DS = HERE.parent / 'fire_event_dataset'
sys.path.insert(0, str(DS))
from src.affected_pop import SOURCES, load_counts, load_mb  # noqa: E402

counts = load_counts(2021)
mb, info = load_mb(2021, counts)
asgs = pd.read_excel(DS / 'data/raw/grp_insurance/asgs/MB_2021_AUST.xlsx', dtype={'MB_CODE_2021': str, 'SA2_CODE_2021': str,
                                                                                  'SA3_CODE_2021': str})
asgs = asgs[asgs.STATE_CODE_2021.astype(str) == '1']
mb = mb.merge(asgs[['MB_CODE_2021', 'SA2_CODE_2021', 'SA3_CODE_2021', 'GCCSA_CODE_2021']].rename(
    columns={'MB_CODE_2021': 'MB_CODE'}), on='MB_CODE', how='left')
print(info, 'MBs without SA2:', mb.SA2_CODE_2021.isna().sum())
mb['area'] = mb.area
tree = shapely.STRtree(mb.geometry.values)

f = gpd.read_parquet(DS / 'data/cache/fires.parquet')
f = f[f.geometry.notna() & ~f.geometry.is_empty].to_crs(mb.crs)
f['start'] = pd.to_datetime(f.start_date)
f['fy'] = np.where(f.start.dt.month >= 7, f.start.dt.year, f.start.dt.year - 1)
KEY = sys.argv[1] if len(sys.argv) > 1 else 'fy'
HOMES_IN = len(sys.argv) > 2 and sys.argv[2] == 'homes_in'   # dwellings inside the outline, no buffer
COUNT = 'dwelling' if HOMES_IN else 'person'
if KEY == 'quarter':
    f['quarter'] = f.start.dt.to_period('Q').astype(str)
rows = []
for fy, sub in f.groupby(KEY):
    zone = shapely.make_valid(shapely.union_all(sub.geometry.values)).buffer(0 if HOMES_IN else 1000)
    shapely.prepare(zone)
    idx = tree.query(zone, predicate='intersects')
    g = mb.geometry.values[idx]
    inside = shapely.contains_properly(zone, g)
    share = np.ones(len(idx))
    e = ~inside
    if e.any():
        clipped = [shapely.clip_by_rect(zone, *b) for b in shapely.bounds(g[e])]
        share[e] = shapely.area(shapely.intersection(g[e], np.array(clipped, dtype=object))) / mb.area.values[idx][e]
    d = pd.DataFrame({'SA2': mb.SA2_CODE_2021.values[idx], 'persons': mb[COUNT].values[idx] * np.clip(share, 0, 1)})
    d = d.groupby('SA2', as_index=False).persons.sum()
    d[KEY] = fy if KEY == 'quarter' else int(fy)
    rows.append(d)
    print(fy, len(sub), 'fires;', len(d), 'SA2s touched')
dose = pd.concat(rows)
tot = mb.groupby('SA2_CODE_2021').agg(pop=(COUNT, 'sum'), SA3=('SA3_CODE_2021', 'first'),
                                     GCCSA=('GCCSA_CODE_2021', 'first')).reset_index().rename(columns={'SA2_CODE_2021': 'SA2'})
dose = dose.merge(tot[['SA2', 'pop']], on='SA2')
dose['dose'] = (dose.persons / dose['pop']).clip(upper=1)
(HERE / 'panels').mkdir(exist_ok=True)
dose.to_parquet(HERE / f'panels/sa2_{KEY}_dose{"_homes_in" if HOMES_IN else ""}.parquet', index=False)
if not HOMES_IN:
    tot.to_parquet(HERE / 'panels/sa2_info.parquet', index=False)
print(dose.groupby(KEY).dose.describe().round(3).tail(12))
