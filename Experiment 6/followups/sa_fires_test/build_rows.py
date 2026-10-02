"""Step 2a (SA fires): event polygons, council roster (burned share >= 1%) and no-fire comparison groups. Frozen rules: PRESPEC.md sections 3 and 4.2.

Reads only files already on disk (GA outlines, ABS LGA 2015 / 2018 / 2021 layers). Reuses the scoping overlay code unchanged
(inputs/overlay_candidates.py: load_ga, load_lga) so the polygon selection and shares are identical to the scoping table.

Outputs (results/): event_polygons.csv, roster.csv, comparison_groups.csv, boundary_2021_check.csv
Run: /Users/ray/Research/AUSSEF - Local/.venv/bin/python build_rows.py
"""
import re
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely

warnings.filterwarnings('ignore')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'inputs'))
import overlay_candidates as oc          # noqa: E402  (frozen scoping code, hash-locked in PRESPEC.lock)

RES = HERE / 'results'
RES.mkdir(exist_ok=True)
CRS = oc.CRS

EVENTS = {   # key: (state, first ignition, last ignition, min polygon ha, name regex, LGA vintage, fire FY start year)
    'SA_2015_sampson_flat': ('SA', '2015-01-01', '2015-01-10', 5000, None, '2015', 2014),
    'SA_2015_pinery': ('SA', '2015-11-24', '2015-11-28', 10000, None, '2015', 2015),
    'SA_2019_cudlee_creek': ('SA', '2019-12-15', '2019-12-25', 1000, r'Cudlee', '2018', 2019),
    'SA_2019_20_kangaroo_island': ('SA', '2019-12-15', '2020-01-31', 1000, r'^(Ravine|KI Complex)', '2018', 2019),
    'SA_2019_20_keilira': ('SA', '2019-12-25', '2020-01-05', 1000, r'Keilira', '2018', 2019),
}
COMPARE_HA = 100


def select(ga, st, d0, d1, minha, pat=None):
    sel = ga[(ga.st == st) & (ga.dt >= pd.Timestamp(d0)) & (ga.dt <= pd.Timestamp(d1) + pd.Timedelta(days=1)) & (ga.area_ha >= minha)]
    if pat:
        sel = sel[sel.fire_name.fillna('').str.contains(pat, flags=re.I, regex=True)]
    return sel


def union_of(sel):
    fids = sel.source_objectid.astype(int).sort_values().values
    g = pyogrio.read_dataframe(oc.GDB, fids=fids, columns=['state', 'area_ha'])
    chk = sel.set_index('source_objectid').loc[fids]
    assert len(g) == len(fids) and np.allclose(g.area_ha.values, chk.area_ha.values), 'FID/attribute mismatch'
    g = g.to_crs(CRS)
    return shapely.union_all(shapely.make_valid(g.geometry.values)), fids


def burned(geom, lga):
    ev = gpd.GeoDataFrame({'e': [0]}, geometry=[geom], crs=CRS)
    hit = gpd.overlay(lga, ev, how='intersection', keep_geom_type=True)
    hit['burned_km2'] = hit.geometry.area / 1e6
    hit['share'] = hit.burned_km2 / hit.lga_area_km2
    return hit.drop(columns='geometry')


def main():
    ga = oc.load_ga()
    lgas = {v: oc.load_lga(v) for v in ('2015', '2016', '2018', '2020', '2021')}
    poly_rows, roster = [], []
    for key, (st, d0, d1, minha, pat, vint, fy) in EVENTS.items():
        sel = select(ga, st, d0, d1, minha, pat)
        assert len(sel) > 0, key
        geom, fids = union_of(sel)
        for r in sel.sort_values('ignition_date').itertuples():
            poly_rows.append(dict(event=key, source_objectid=int(r.source_objectid), fire_name=r.fire_name, ignition_date=r.ignition_date,
                                  area_ha=r.area_ha, fire_type=r.fire_type))
        L = lgas[vint]
        L = L[L.lga_code.str[0] == oc.STATE_DIGIT[st]]
        hit = burned(geom, L)
        hit = hit[(hit.share >= 0.01) & ~hit.lga_name.str.startswith('Unincorporated')].copy()
        hit['event'], hit['state'], hit['lga_vintage'] = key, st, vint
        hit['first_fire_start'] = pd.to_datetime(sel.dt).min().date().isoformat()
        hit['n_polygons'] = len(sel)
        hit['union_km2'] = geom.area / 1e6
        roster.append(hit)
    pd.DataFrame(poly_rows).to_csv(RES / 'event_polygons.csv', index=False)
    R = pd.concat(roster).sort_values(['event', 'share'], ascending=[True, False]).reset_index(drop=True)
    # code in the ASGS 2018 edition (series on 2018+ codes: SALM, ERP, DSS 2018 file); only Mallala (43920) was renamed and recoded
    l18 = lgas['2018'].set_index('lga_code')
    l15 = lgas['2015'].set_index('lga_code')
    R['code_lga2018'] = R.lga_code.map(lambda c: '40150' if c == '43920' else c)
    R['code_lga2015'] = R.lga_code.map(lambda c: '43920' if c == '40150' else c)
    R.to_csv(RES / 'roster.csv', index=False)
    print(R[['event', 'lga_code', 'lga_name', 'lga_area_km2', 'burned_km2', 'share', 'code_lga2018']].round(4).to_string())

    # boundary checks (reported, not used to select): SA council codes and areas across editions 2015 / 2016 / 2018 / 2020 / 2021
    chk = []
    sa = {v: lgas[v][lgas[v].lga_code.str[0] == '4'].set_index('lga_code') for v in lgas}
    for v0, v1 in (('2015', '2016'), ('2016', '2018'), ('2018', '2020'), ('2020', '2021')):
        a, b = sa[v0], sa[v1]
        for c in sorted(set(a.index) | set(b.index)):
            in_a, in_b = c in a.index, c in b.index
            ra = b.lga_area_km2.get(c) / a.lga_area_km2.get(c) - 1 if in_a and in_b else np.nan
            chk.append(dict(from_edition=v0, to_edition=v1, code=c, name=(a.lga_name.get(c) if in_a else b.lga_name.get(c)), in_from=in_a, in_to=in_b, area_change=ra))
    C0 = pd.DataFrame(chk)
    C0.to_csv(RES / 'boundary_edition_check.csv', index=False)
    bad = C0[(~C0.in_from) | (~C0.in_to) | (C0.area_change.abs() > 0.01)]
    print('SA codes missing in an edition or with area change > 1% between editions:')
    print(bad.to_string())

    # comparison groups: SA councils with >= 100 ha burning inside during the window (all GA non-prescribed polygons, all sizes)
    rows = []
    wins = {}
    for key, (st, d0, d1, minha, pat, vint, fy) in EVENTS.items():
        wins[key] = [(f'FY{fy}-{str(fy + 1)[2:]}', f'{fy}-07-01', f'{fy + 1}-06-30'),
                     (f'FY{fy}-{str(fy + 1)[2:]}..FY{fy + 1}-{str(fy + 2)[2:]}', f'{fy}-07-01', f'{fy + 2}-06-30')]
        q0 = pd.Timestamp(d0).to_period('Q')                      # SL window: 5 quarters from q0-3 to q0+1 (src/vulnerable.py)
        wins[key].append(('SL_5Q', str((q0 - 3).start_time.date()), str((q0 + 1).end_time.date())))
    for key, (st, *_rest) in EVENTS.items():
        for label, d0, d1 in wins[key]:
            sel = ga[(ga.st == st) & (ga.dt >= pd.Timestamp(d0)) & (ga.dt <= pd.Timestamp(d1) + pd.Timedelta(days=1))]
            geom, fids = union_of(sel)
            for v in ('2015', '2018'):
                L = lgas[v]
                L = L[L.lga_code.str[0] == oc.STATE_DIGIT[st]]
                hit = burned(geom, L)
                hit['burned_ha'] = hit.burned_km2 * 100
                full = L[['lga_code', 'lga_name']].merge(hit[['lga_code', 'burned_ha']], on='lga_code', how='left')
                full['burned_ha'] = full.burned_ha.fillna(0)
                full['has_fire_100ha'] = full.burned_ha >= COMPARE_HA
                full['event'], full['window'], full['lga_vintage'], full['n_polygons'] = key, label, v, len(sel)
                full['window_start'], full['window_end'] = d0, d1
                rows.append(full)
    C = pd.concat(rows)
    C.to_csv(RES / 'comparison_groups.csv', index=False)
    print(C.groupby(['event', 'window', 'lga_vintage']).agg(councils=('lga_code', 'size'), with_fire=('has_fire_100ha', 'sum'),
                                                          n_polygons=('n_polygons', 'first')).to_string())


if __name__ == '__main__':
    main()
