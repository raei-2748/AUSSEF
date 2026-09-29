"""Step 2a: event polygons, council roster (burned share >= 1%) and no-fire comparison groups. Frozen rules: PRESPEC.md sections 3 and 4.2.

Reads only files already on disk (GA outlines, ABS LGA 2015 / 2018 / 2021 layers). Reuses the scoping overlay code unchanged
(inputs/overlay_candidates.py: load_ga, load_lga) so the polygon selection and shares are identical to the scoping table.

Outputs (results/): event_polygons.csv, roster.csv, comparison_groups.csv, boundary_2021_check.csv
Run: /Users/ray/Research/AUSSEF/.venv/bin/python build_rows.py
"""
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

EVENTS = {   # key: (state, first ignition, last ignition, min polygon ha, LGA vintage, fire FY start year)
    'NSW_2013_oct': ('NSW', '2013-10-10', '2013-10-31', 1000, '2015', 2013),
    'VIC_2009_black_saturday': ('VIC', '2009-02-04', '2009-02-09', 1000, '2015', 2008),
}
COMPARE_HA = 100


def select(ga, st, d0, d1, minha):
    return ga[(ga.st == st) & (ga.dt >= pd.Timestamp(d0)) & (ga.dt <= pd.Timestamp(d1) + pd.Timedelta(days=1)) & (ga.area_ha >= minha)]


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
    lgas = {v: oc.load_lga(v) for v in ('2015', '2018', '2021')}
    poly_rows, roster = [], []
    for key, (st, d0, d1, minha, vint, fy) in EVENTS.items():
        sel = select(ga, st, d0, d1, minha)
        geom, fids = union_of(sel)
        for r in sel.sort_values('ignition_date').itertuples():
            poly_rows.append(dict(event=key, source_objectid=int(r.source_objectid), fire_name=r.fire_name, ignition_date=r.ignition_date,
                                  area_ha=r.area_ha, fire_type=r.fire_type))
        L = lgas[vint]
        L = L[L.lga_code.str[0] == oc.STATE_DIGIT[st]]
        hit = burned(geom, L)
        hit = hit[hit.share >= 0.01].copy()
        hit['event'], hit['state'], hit['lga_vintage'] = key, st, vint
        hit['first_fire_start'] = pd.to_datetime(sel.dt).min().date().isoformat()
        hit['n_polygons'] = len(sel)
        hit['union_km2'] = geom.area / 1e6
        roster.append(hit)
    pd.DataFrame(poly_rows).to_csv(RES / 'event_polygons.csv', index=False)
    R = pd.concat(roster).sort_values(['event', 'share'], ascending=[True, False]).reset_index(drop=True)

    # NSW councils in force in 2013: does the same ABS code + area (within 1%) exist in LGA 2021?
    l21 = lgas['2021'].set_index('lga_code')
    l15 = lgas['2015'].set_index('lga_code')

    def same_in_2021(code):
        if code not in l21.index:
            return False
        return abs(l21.loc[code, 'lga_area_km2'] / l15.loc[code, 'lga_area_km2'] - 1) <= 0.01
    R['unchanged_in_lga2021'] = R.lga_code.map(same_in_2021)
    R['in_original_129'] = R.lga_code.map(lambda c: c in set(pd.read_csv(HERE / 'inputs/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str}).region_id))
    R.loc[R.state == 'VIC', ['unchanged_in_lga2021', 'in_original_129']] = [None, False]
    R['scoreable_in_nsw_129'] = (R.state == 'NSW') & R.unchanged_in_lga2021 & R.in_original_129
    R.to_csv(RES / 'roster.csv', index=False)
    print(R[['event', 'lga_code', 'lga_name', 'lga_area_km2', 'burned_km2', 'share', 'unchanged_in_lga2021', 'scoreable_in_nsw_129']].round(4).to_string())

    # comparison groups: councils with >= 100 ha burning inside during the window (all GA non-prescribed polygons, all sizes)
    rows = []
    wins = {  # event -> list of (window label, vintage layers, first day, last day)
        'NSW_2013_oct': [('FY2013-14', '2013-07-01', '2014-06-30'), ('FY2013-14..FY2014-15', '2013-07-01', '2015-06-30')],
        'VIC_2009_black_saturday': [('FY2008-09', '2008-07-01', '2009-06-30'), ('FY2008-09..FY2009-10', '2008-07-01', '2010-06-30')],
    }
    for key, (st, *_rest) in EVENTS.items():
        for label, d0, d1 in wins[key]:
            sel = ga[(ga.st == st) & (ga.dt >= pd.Timestamp(d0)) & (ga.dt <= pd.Timestamp(d1) + pd.Timedelta(days=1))]
            geom, fids = union_of(sel)
            vints = ['2015', '2018'] if st == 'NSW' else ['2015']
            for v in vints:
                L = lgas[v]
                L = L[L.lga_code.str[0] == oc.STATE_DIGIT[st]]
                hit = burned(geom, L)
                hit['burned_ha'] = hit.burned_km2 * 100
                full = L[['lga_code', 'lga_name']].merge(hit[['lga_code', 'burned_ha']], on='lga_code', how='left')
                full['burned_ha'] = full.burned_ha.fillna(0)
                full['has_fire_100ha'] = full.burned_ha >= COMPARE_HA
                full['event'], full['window'], full['lga_vintage'], full['n_polygons'] = key, label, v, len(sel)
                rows.append(full)
    C = pd.concat(rows)
    C.to_csv(RES / 'comparison_groups.csv', index=False)
    print(C.groupby(['event', 'window', 'lga_vintage']).agg(councils=('lga_code', 'size'), with_fire=('has_fire_100ha', 'sum'),
                                                          n_polygons=('n_polygons', 'first')).to_string())


if __name__ == '__main__':
    main()
