"""Experiment 16, Part 1 (PRESPEC.md, LOCK.txt): does each exposure type predict what was actually destroyed?
Spearman rank correlation of exposure with destroyed counts per council x event; council-cluster bootstrap.
Run: ./run.sh damage_check.py"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/ray/Research/AUSSEF - Local')
RES = HERE / 'results'
SEED, B = 20261002, 2000


def load():
    e = pd.read_csv(RES / 'EXPOSURE_COUNCIL_FIRE.csv', dtype={'agrn': str, 'region_id': str})
    a = pd.read_csv(ROOT / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str},
                    usecols=['agrn', 'region_id', 'dwellings', 'homes_per_1000_v2_inferred'])
    m = pd.read_excel(ROOT / 'data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx', sheet_name='master', header=2,
                      usecols=['agrn', 'region_id', 'DL_facilities_destroyed_sourced',
                               'DL_outbuildings_destroyed_sourced', 'info_DL_facilities_destroyed_sourced_scope',
                               'info_DL_outbuildings_destroyed_sourced_scope'], dtype={'agrn': str, 'region_id': str})
    d = e.merge(a, on=['agrn', 'region_id'], validate='1:1').merge(m, on=['agrn', 'region_id'], validate='1:1')
    d['homes_destroyed'] = d.homes_per_1000_v2_inferred * d.dwellings / 1000
    d['facilities_destroyed'] = d.DL_facilities_destroyed_sourced
    d['outbuildings_destroyed'] = d.DL_outbuildings_destroyed_sourced
    for z in ('in', '1km'):
        d[f'nonres_mb_{z}'] = d[f'workplace_mb_{z}'] + d[f'public_mb_{z}']
        d[f'nonres_osm_{z}'] = d[f'osm_workplace_{z}'] + d[f'osm_public_{z}']
        d[f'farm_osm_{z}'] = d[f'osm_farm_{z}'] + d[f'osm_other_building_{z}']
    return d


# damage -> (matched primary, same-zone homes, [other exposures reported])
PLAN = {
    'homes_destroyed': ('homes_in', None, ['homes_1km', 'osm_home_in', 'osm_home_1km']),
    'facilities_destroyed': ('nonres_mb_1km', 'homes_1km',
                             ['nonres_mb_in', 'nonres_osm_in', 'nonres_osm_1km', 'workplace_mb_1km', 'public_mb_1km',
                              'homes_in']),
    'outbuildings_destroyed': ('farm_homes_in', 'homes_in',
                               ['farm_homes_1km', 'farm_km2_in', 'farm_osm_in', 'farm_osm_1km', 'homes_1km']),
}


def rho(x, y):
    if np.std(x) == 0 or np.std(y) == 0:
        return np.nan
    return spearmanr(x, y)[0]


def boot(d, y, cols, rng):
    """bootstrap rho for each column, resampling councils (all their rows together)."""
    groups = d.groupby('region_id').indices
    keys = list(groups)
    out = np.full((B, len(cols)), np.nan)
    for b in range(B):
        idx = np.concatenate([groups[k] for k in rng.choice(keys, len(keys), replace=True)])
        s = d.iloc[idx]
        out[b] = [rho(s[c].to_numpy(), s[y].to_numpy()) for c in cols]
    return out


def ci(v):
    v = v[~np.isnan(v)]
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def run(d, label, rng):
    rows, verdicts = [], {}
    for y, (prim, homes, others) in PLAN.items():
        s = d[d[y].notna()].reset_index(drop=True)
        cols = [prim, 'burned_km2'] + ([homes] if homes else []) + others
        cols = list(dict.fromkeys(cols))
        bs = boot(s, y, cols, rng)
        est = {c: rho(s[c].to_numpy(), s[y].to_numpy()) for c in cols}
        for j, c in enumerate(cols):
            lo, hi = ci(bs[:, j])
            rows.append(dict(sample=label, damage=y, exposure=c, role=('matched (primary)' if c == prim else
                                                                     'area burned' if c == 'burned_km2' else
                                                                     'homes, same zone' if c == homes else 'other'),
                             rows=len(s), rows_with_loss=int((s[y] > 0).sum()), total_destroyed=float(s[y].sum()),
                             rho=est[c], lo=lo, hi=hi))
        dA = bs[:, 0] - bs[:, 1]
        res = dict(rows=len(s), rho=est[prim], rho_ci=ci(bs[:, 0]), minus_area=est[prim] - est['burned_km2'],
                   minus_area_ci=ci(dA))
        works = res['rho_ci'][0] > 0 and res['minus_area_ci'][0] > 0
        if homes:
            dH = bs[:, 0] - bs[:, cols.index(homes)]
            res.update(minus_homes=est[prim] - est[homes], minus_homes_ci=ci(dH))
            spec = works and res['minus_homes_ci'][0] > 0
        else:
            spec = None
        res['verdict'] = ('Type-specific' if spec else 'Matched exposure works' +
                          (' (homes in the same zone does as well)' if homes else '')) if works else \
            'Not better than area burned'
        verdicts[y] = res
    return rows, verdicts


def main():
    d = load()
    rng = np.random.default_rng(SEED)
    rows, ver = run(d, 'all seasons', rng)
    rows2, ver2 = run(d[d.season == 2019].reset_index(drop=True), 'Black Summer 2019-20 only', rng)
    t = pd.DataFrame(rows + rows2)
    t.to_csv(RES / 'DAMAGE_CHECK.csv', index=False)
    json.dump({'all seasons (primary)': ver, 'Black Summer only (reported)': ver2}, open(RES / 'DAMAGE_CHECK.json', 'w'),
              indent=2)
    d.to_csv(RES / 'DAMAGE_CHECK_ROWS.csv', index=False)
    pd.set_option('display.width', 220)
    print(t.round(3).to_string())
    print(json.dumps(ver, indent=1))
    print(json.dumps(ver2, indent=1))
    for y in PLAN:
        s = d[d[y].notna()]
        print(y, 'rows', len(s), 'seasons', s.season.value_counts().to_dict(), 'scope',
              s.get(f'info_DL_{y.replace("_destroyed", "")}_destroyed_sourced_scope', pd.Series(dtype=str))
              .value_counts().to_dict())


if __name__ == '__main__':
    main()
