"""Experiment 16, descriptive (outcome-free): what was inside / within 1 km of ALL NSW fires starting in each
financial year, by building function, counted once (union of outlines, no council split, so fires linked to two
declarations are not double counted). 2016 Census MBs for FY up to 2020, 2021 after (affected_pop.py rule).
Run: ./run.sh season_totals.py"""
import sys
sys.dont_write_bytecode = True
import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402
import build_exposure as X  # noqa: E402

osm, ln = X.load_osm()
ftree, ltree = shapely.STRtree(osm.geometry.values), shapely.STRtree(ln.geometry.values)
mbs = {y: X.load_mb_all(y) for y in (2016, 2021)}
trees = {y: shapely.STRtree(m.geometry.values) for y, m in mbs.items()}
f = gpd.read_parquet(X.DS / 'data/cache/fires.parquet')
f = f[f.geometry.notna() & ~f.geometry.is_empty]
st = pd.to_datetime(f.start_date)
f['fy'] = np.where(st.dt.month >= 7, st.dt.year, st.dt.year - 1)
rows = []
for fy, sub in f.groupby('fy'):
    y = 2016 if fy + 1 <= 2020 else 2021      # FY starting Jul fy ends Jun fy+1
    U = shapely.make_valid(shapely.union_all(sub.geometry.values))
    for z, suf in ((U, 'in'), (shapely.buffer(U, 1000, quad_segs=8), '1km')):
        r = {'fy': f'{fy}-{str(fy + 1)[2:]}', 'zone': 'inside' if suf == 'in' else 'within 1 km', 'fires': len(sub),
             'census': y, 'zone_km2': float(shapely.area(z) / 1e6)}
        idx, sh = X.area_shares(z, mbs[y].geometry.values, trees[y], mbs[y].area.values)
        r.update({k[:-len(suf) - 1]: v for k, v in X.mb_summary(mbs[y], idx, sh, suf).items()})
        r.update({k[:-len(suf) - 1]: v for k, v in X.osm_summary(osm, ftree, ln, ltree, z, suf).items()})
        rows.append(r)
    print(fy, flush=True)
t = pd.DataFrame(rows)
t.to_csv(X.RES / 'SEASON_TOTALS_BY_FUNCTION.csv', index=False)
pd.set_option('display.width', 250)
print(t.round(1).T.to_string())
