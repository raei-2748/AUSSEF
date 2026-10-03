"""Experiment 13 exposure (outcome-free). For every NSW Census 2021 mesh block (MB) and every fire financial year
(FY labelled by its starting year, July-June), the share of the MB's area inside the union of that FY's fire outlines
(no buffer) and inside the outline buffered by 1 km. Aggregated to postcodes (POA 2021), suburbs (SAL 2021) and
SA2s (ASGS 2021):
  H = share of the unit's dwellings inside a fire outline        (primary dose, "homes inside the fire")
  R = share of the unit's residents inside or within 1 km         (secondary dose, Experiment 7 method)
  S = share of the unit's dwellings on land burned at high or extreme severity (FESM classes 4-5); FY2019 only
Dwellings/residents are spread evenly over each MB's area (as in Experiment 7 prep_sa2_dose.py).

Fire outlines: Geoscience Australia national historical bushfire boundaries (non-prescribed, NSW) for fires that
started before 1 Jan 2015; the project master fire file (fire_event_dataset/data/cache/fires.parquet) from 1 Jan 2015.
Run: uv run --no-project --with geopandas --with pyogrio --with pyarrow --with openpyxl --with rasterio python build_exposure.py
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DS = ROOT / 'fire_event_dataset'
sys.path.insert(0, str(DS))
from src.affected_pop import load_counts, load_mb  # noqa: E402

OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)
P1 = Path('/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw')
GDB = f"/vsizip/{P1 / 'ga_original.zip'}/Bushfire_Boundaries_Historical.gdb"
FESM_1920 = Path('/Users/ray/Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/'
                 'Fire Dataset Build Inputs (only needed to rebuild the fire dataset)/'
                 'Fire severity map FESM 2019-20 (Black Summer - unzipped)/fesm_201920')
CUT = pd.Timestamp('2015-01-01')
FY_MIN, FY_MAX = 2006, 2024


def fy_of(t):
    return np.where(t.dt.month >= 7, t.dt.year, t.dt.year - 1)


def read_alloc(name, cols):
    cache = OUT / f'alloc_{name}.parquet'
    if cache.exists():
        return pd.read_parquet(cache)
    p = {'MB': DS / 'data/raw/grp_insurance/asgs/MB_2021_AUST.xlsx', 'POA': HERE / 'raw/POA_2021_AUST.xlsx',
         'SAL': HERE / 'raw/SAL_2021_AUST.xlsx'}[name]
    d = pd.read_excel(p, dtype=str, usecols=cols)
    d = d[d.MB_CODE_2021.str.startswith('1')]          # NSW mesh blocks start with state digit 1
    d.to_parquet(cache, index=False)
    return d


def fires():
    a = pd.read_csv(P1 / 'fire_attributes.csv', low_memory=False)
    a = a[a.state.str.startswith('NSW', na=False) & (a.fire_type != 'Prescribed Burn')].copy()
    a['dt'] = pd.to_datetime(a.ignition_date, errors='coerce', utc=True).dt.tz_localize(None)
    a = a[(a.dt < CUT) & (a.dt >= pd.Timestamp(f'{FY_MIN}-07-01'))]
    a = a.sort_values('source_objectid')
    fids = a.source_objectid.astype(int).values
    g = pyogrio.read_dataframe(GDB, fids=fids, columns=['state', 'area_ha'])
    assert len(g) == len(fids) and np.allclose(g.area_ha.values, a.area_ha.values), 'FID/attribute mismatch'
    g['fy'] = fy_of(a.dt.reset_index(drop=True)).astype(int)
    g['src'] = 'GA'
    g = g.to_crs(3577)[['fy', 'src', 'geometry']]
    f = gpd.read_parquet(DS / 'data/cache/fires.parquet')
    f = f[f.geometry.notna() & ~f.geometry.is_empty].to_crs(3577)
    f['start'] = pd.to_datetime(f.start_date)
    f = f[f.start >= CUT].copy()
    f['fy'] = fy_of(f.start).astype(int)
    f['src'] = 'master'
    allf = pd.concat([g, f[['fy', 'src', 'geometry']]], ignore_index=True)
    allf = allf[allf.fy <= FY_MAX]
    allf = allf[allf.geometry.notna() & ~allf.geometry.is_empty]
    allf['geometry'] = shapely.make_valid(allf.geometry.values)
    return gpd.GeoDataFrame(allf, crs=3577)


def mb_shares(mb, fz):
    tree = shapely.STRtree(mb.geometry.values)
    area = mb.geometry.area.values
    rows = []
    for fy, sub in fz.groupby('fy'):
        zone0 = shapely.make_valid(shapely.union_all(sub.geometry.values))
        for buf, col in ((0, 'in'), (1000, 'k1')):
            zone = zone0.buffer(buf) if buf else zone0
            shapely.prepare(zone)
            idx = tree.query(zone, predicate='intersects')
            g = mb.geometry.values[idx]
            inside = shapely.contains_properly(zone, g)
            share = np.ones(len(idx))
            e = ~inside
            if e.any():
                share[e] = shapely.area(shapely.intersection(g[e], zone)) / area[idx][e]
            rows.append(pd.DataFrame({'MB_CODE': mb.MB_CODE.values[idx], 'fy': int(fy), 'kind': col,
                                      'share': np.clip(share, 0, 1)}))
        print(fy, len(sub), 'outlines; MBs touched (1 km):', len(rows[-1]), flush=True)
    s = pd.concat(rows).pivot_table(index=['MB_CODE', 'fy'], columns='kind', values='share', fill_value=0).reset_index()
    s.columns.name = None
    return s.rename(columns={'in': 'share_in', 'k1': 'share_1km'})


def severity(mb, s):
    """FY2019 only: share of each MB's area mapped high or extreme (FESM 2019-20 classes 4-5)."""
    import rasterio
    from rasterio.mask import mask as rmask
    sel = s[(s.fy == 2019) & (s.share_in > 0)].MB_CODE.unique()
    g = mb[mb.MB_CODE.isin(sel)]
    out = []
    with rasterio.open(FESM_1920) as src:
        print('FESM 2019-20:', src.crs, src.res, src.nodata, flush=True)
        nod = src.nodata if src.nodata is not None else 255
        gg = g.to_crs(src.crs)
        for code, geom in zip(gg.MB_CODE.values, gg.geometry.values):
            try:
                arr, _ = rmask(src, [geom], crop=True, filled=True, nodata=nod)
            except ValueError:
                out.append((code, np.nan, 0))
                continue
            a = arr[0]
            valid = (a != nod) & (a > 0)          # 0 = outside mapped extent
            n = int(valid.sum())
            hx = int(((a == 4) | (a == 5)).sum())
            out.append((code, hx / n if n else np.nan, n))
    return pd.DataFrame(out, columns=['MB_CODE', 'share_hx', 'n_px'])


def aggregate(mbinfo, s, unit_col):
    m = mbinfo[mbinfo[unit_col].notna()][['MB_CODE', unit_col, 'person', 'dwelling', 'SA3_CODE_2021', 'SA4_CODE_2021',
                                           'GCCSA_CODE_2021']]
    tot = m.groupby(unit_col).agg(persons=('person', 'sum'), dwellings=('dwelling', 'sum')).reset_index()
    w = m.assign(w=m.dwelling + 1e-6 * m.person)
    for c in ('SA3_CODE_2021', 'SA4_CODE_2021', 'GCCSA_CODE_2021'):
        r = w.groupby([unit_col, c]).w.sum().reset_index().sort_values('w').drop_duplicates(unit_col, keep='last')
        tot[c.split('_')[0]] = tot[unit_col].map(r.set_index(unit_col)[c])
    x = s.merge(m[['MB_CODE', unit_col, 'person', 'dwelling']], on='MB_CODE')
    x['dw_in'] = x.dwelling * x.share_in
    x['p_1km'] = x.person * x.share_1km
    x['dw_hx'] = x.dwelling * x.share_in * x.share_hx.fillna(0)
    d = x.groupby([unit_col, 'fy']).agg(dw_in=('dw_in', 'sum'), p_1km=('p_1km', 'sum'), dw_hx=('dw_hx', 'sum')).reset_index()
    d = d.merge(tot[[unit_col, 'persons', 'dwellings']], on=unit_col)
    d['H'] = (d.dw_in / d.dwellings.where(d.dwellings > 0)).clip(upper=1).fillna(0)
    d['R'] = (d.p_1km / d.persons.where(d.persons > 0)).clip(upper=1).fillna(0)
    d['S'] = (d.dw_hx / d.dwellings.where(d.dwellings > 0)).clip(upper=1).fillna(0)
    return d.rename(columns={unit_col: 'unit'}), tot.rename(columns={unit_col: 'unit'})


def main():
    counts = load_counts(2021)
    mb, info = load_mb(2021, counts)
    print(info, flush=True)
    asgs = read_alloc('MB', ['MB_CODE_2021', 'SA2_CODE_2021', 'SA2_NAME_2021', 'SA3_CODE_2021', 'SA4_CODE_2021',
                             'GCCSA_CODE_2021'])
    poa = read_alloc('POA', ['MB_CODE_2021', 'POA_CODE_2021'])
    sal = read_alloc('SAL', ['MB_CODE_2021', 'SAL_CODE_2021', 'SAL_NAME_2021'])
    mbinfo = (counts[['MB_CODE', 'person', 'dwelling']].rename(columns={'MB_CODE': 'MB_CODE_2021'})
              .merge(asgs, on='MB_CODE_2021', how='left').merge(poa, on='MB_CODE_2021', how='left')
              .merge(sal, on='MB_CODE_2021', how='left').rename(columns={'MB_CODE_2021': 'MB_CODE'}))
    print('MBs:', len(mbinfo), 'missing SA2/POA/SAL:', mbinfo.SA2_CODE_2021.isna().sum(), mbinfo.POA_CODE_2021.isna().sum(),
          mbinfo.SAL_CODE_2021.isna().sum(), flush=True)
    mbinfo.to_parquet(OUT / 'mb_info.parquet', index=False)
    cache = OUT / 'mb_fy_shares.parquet'
    if cache.exists():
        s = pd.read_parquet(cache)
    else:
        fz = fires()
        print(fz.groupby(['fy', 'src']).size().to_string(), flush=True)
        s = mb_shares(mb, fz)
        s.to_parquet(cache, index=False)
    sv_cache = OUT / 'mb_severity_fy2019.parquet'
    if sv_cache.exists():
        sv = pd.read_parquet(sv_cache)
    else:
        sv = severity(mb, s)
        sv.to_parquet(sv_cache, index=False)
    s = s.merge(sv[['MB_CODE', 'share_hx']].assign(fy=2019), on=['MB_CODE', 'fy'], how='left')
    for col, name in (('POA_CODE_2021', 'poa'), ('SAL_CODE_2021', 'sal'), ('SA2_CODE_2021', 'sa2')):
        d, tot = aggregate(mbinfo, s, col)
        d.to_parquet(OUT / f'dose_{name}.parquet', index=False)
        tot.to_parquet(OUT / f'units_{name}.parquet', index=False)
        summ = d.groupby('fy').apply(lambda x: pd.Series({'H>=1%': (x.H >= .01).sum(), 'H>=10%': (x.H >= .1).sum(),
                                                         'R>=10%': (x.R >= .1).sum(), 'S>=1%': (x.S >= .01).sum(),
                                                         'dw_in': x.dw_in.sum()}))
        summ.round(0).to_csv(OUT / f'exposure_summary_{name}.csv')
        print(name, 'units:', len(tot), '\n', summ.round(0).to_string(), flush=True)
    sal[['SAL_CODE_2021', 'SAL_NAME_2021']].drop_duplicates().to_parquet(OUT / 'sal_names.parquet', index=False)


if __name__ == '__main__':
    main()
