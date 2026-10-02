"""Experiment 6: pre-fire council risk score, validated against the real fires' Y (DL/IL/FP/SL).

Score (all inputs known before the first fire in the data, snapshot 2014 -> fall back to 2015/2016):
  H hazard        BFPL share (Cat 1; Cat 1+2), NVIS forest share       [BFPL is the new data]
                Cat 3 (grassland, 480,000 km2 of western NSW) is excluded: 'any BFPL' is ~100% of most rural councils
  E exposure      log population, log people inside BFPL Cat 1-2 (pop x share, uniform-density proxy)
  V vulnerability low SEIFA IRSD, low median income, high unemployment
  F fiscal        low cash cover, low own-source %, high debt-service ratio,
                  low operating ratio, high infrastructure backlog, low unrestricted current ratio
Each item is turned into a 0-1 percentile rank across the NSW councils (oriented so 1 = worse),
each block is the mean of its items, the score is a fixed prior combination. No Y is used to build it.

Validation on master (218 council x fire rows, 96 fires): Spearman(score, Y and each pillar) with a
council-cluster bootstrap, for several "large fire" definitions, plus council-level checks.

Run: python3 build_and_validate_score.py   (needs results/COUNCIL_HAZARD.csv)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
WORKBOOK = Path('/Users/ray/Research/AUSSEF - Local/data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx')
EXPOSURE = sys.argv[1] if len(sys.argv) > 1 else 'v1'      # 'v2' = share of dwellings/residents inside BFPL Cat 1-2
assert EXPOSURE in ('v1', 'v2')
SUF = '' if EXPOSURE == 'v1' else '_v2'                     # v1 result files are never overwritten
SEED = 20260929
N_BOOT = 2000
SNAP_YEARS = (2014, 2015, 2016)
YCOLS = ['Y', 'DL', 'IL', 'FP', 'SL']

# item -> (source column, orientation +1 = higher is worse, -1 = lower is worse)
ITEMS_E_V2 = {'dwellings_in_bfpl12_share': +1, 'residents_in_bfpl12_share': +1}
ITEMS = {
    'H': {'bfpl_share_cat1': +1, 'bfpl_share_cat12': +1, 'nvis_forest_share': +1},
    'E': {'log_pop': +1, 'log_pop_in_bfpl': +1},
    'V': {'seifa_irsd': -1, 'median_income_aud_fy': -1, 'unemp_rate': +1},
    'F': {'fiscal_cash_cover_months_fy': -1, 'fiscal_own_source_pct_fy': -1,
          'fiscal_debt_service_ratio_pct_fy': +1, 'fiscal_operating_ratio_pct_fy': -1,
          'fiscal_infra_backlog_ratio_pct_fy': +1, 'fiscal_unrestricted_current_ratio_fy': -1},
}


def pct(s, sign):
    r = s.rank(pct=True)
    return r if sign > 0 else 1 - r + 1 / s.notna().sum()


def snapshot(ly):
    cols = sorted({c for b in ITEMS.values() for c in b if c in ly.columns} | {'population', 'area_km2'})
    ly = ly[ly.year.isin(SNAP_YEARS)].sort_values(['region_id', 'year'])
    snap = ly.groupby('region_id')[cols].first()          # first non-null per council, earliest year first
    return snap.reset_index()


def build_score(ly, hazard):
    snap = snapshot(ly).merge(hazard, on='region_id', how='inner')
    snap['log_pop'] = np.log(snap.population)
    snap['log_pop_in_bfpl'] = np.log1p(snap.population * snap.bfpl_share_cat12)
    items_all = ITEMS
    if EXPOSURE == 'v2':
        exp = pd.read_csv(OUT / 'COUNCIL_EXPOSURE_BFPL.csv')[['region_id', 'dwellings_in_bfpl12_share',
                                                               'residents_in_bfpl12_share']]
        snap = snap.merge(exp, on='region_id', how='left')
        snap['E_v1'] = pd.DataFrame({c: pct(snap[c], s) for c, s in ITEMS['E'].items()}).mean(axis=1)
        items_all = {**ITEMS, 'E': ITEMS_E_V2}
    blocks = {}
    for b, items in items_all.items():
        cols = pd.DataFrame({c: pct(snap[c], s) for c, s in items.items()})
        blocks[b] = cols.mean(axis=1, skipna=True)
        snap[f'{b}_missing_items'] = cols.isna().sum(axis=1)
    B = pd.DataFrame(blocks)
    for b in B:                                            # block with no data at all -> NSW median
        B[b] = B[b].fillna(B[b].median())
    snap = pd.concat([snap, B], axis=1)
    snap['risk_add'] = B[['H', 'E', 'V', 'F']].mean(axis=1)
    snap['risk_mult'] = (B.H * B.E * (0.5 * B.V + 0.5 * B.F)).rank(pct=True)
    # ablations: what does each block / BFPL add?
    hz_nobfpl = pd.DataFrame({'nvis_forest_share': pct(snap.nvis_forest_share, +1)}).mean(axis=1)
    snap['risk_add_no_bfpl'] = pd.concat([hz_nobfpl.rename('H'), B[['E', 'V', 'F']]], axis=1).mean(axis=1)
    snap['risk_hazard_only'] = B.H
    # EXPLORATORY (structure chosen after looking at block-level validation): likelihood x consequence
    snap['risk_HV_mean'] = B[['H', 'V']].mean(axis=1)
    snap['risk_HV_prod'] = (B.H * B.V).rank(pct=True)
    snap['risk_vuln_fiscal_only'] = B[['V', 'F']].mean(axis=1)
    return snap


def load_master():
    m = pd.read_excel(WORKBOOK, sheet_name='master', header=2, keep_default_na=False, na_values=[''])
    m['year'] = pd.to_datetime(m.first_fire_start).dt.year
    m['share'] = m.X_fire_share_of_council_burned
    m['burn_ha'] = m.X_fire_burn_area_in_council_ha
    m['region_id'] = m.region_id.astype(int)
    return m


def boot_spearman(x, y, groups, rng, n=N_BOOT):
    d = pd.DataFrame({'x': x, 'y': y, 'g': groups}).dropna()
    if len(d) < 6 or d.x.nunique() < 3 or d.y.nunique() < 3:
        return len(d), np.nan, np.nan, np.nan
    est = spearmanr(d.x, d.y)[0]
    gs = {g: sub[['x', 'y']].to_numpy() for g, sub in d.groupby('g')}
    keys = list(gs)
    if len(keys) < 4:
        return len(d), est, np.nan, np.nan
    bs = []
    for _ in range(n):
        pick = rng.choice(len(keys), len(keys))
        a = np.vstack([gs[keys[i]] for i in pick])
        if np.unique(a[:, 0]).size > 2 and np.unique(a[:, 1]).size > 2:
            bs.append(spearmanr(a[:, 0], a[:, 1])[0])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return len(d), est, lo, hi


def auc(score, positive):
    r = rankdata(score)
    n1 = positive.sum()
    n0 = len(positive) - n1
    return (r[positive].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def definitions(m):
    return {
        'all rows (no size filter)': np.ones(len(m), bool),
        'share burned >= 2%': (m.share >= 0.02).to_numpy(),
        'share burned >= 5%': (m.share >= 0.05).to_numpy(),
        'share burned >= 10%': (m.share >= 0.10).to_numpy(),
        'share burned >= 20% (old)': (m.share >= 0.20).to_numpy(),
        'burned >= 1,000 ha in council': (m.burn_ha >= 1000).to_numpy(),
        'burned >= 5,000 ha in council': (m.burn_ha >= 5000).to_numpy(),
        'Y class Severe/Extreme': (m.Y_class >= 3).to_numpy(),
    }


def main():
    rng = np.random.default_rng(SEED)
    ly = pd.read_excel(WORKBOOK, sheet_name='lga_year', header=1, keep_default_na=False, na_values=[''])
    hazard = pd.read_csv(OUT / 'COUNCIL_HAZARD.csv')
    snap = build_score(ly, hazard)
    keep = ['region_id', 'region_name', 'area_km2_geom', 'population', 'bfpl_share_any', 'bfpl_share_cat1',
            'bfpl_share_cat12', 'nvis_forest_share', 'H', 'E', 'V', 'F', 'risk_add', 'risk_mult', 'risk_add_no_bfpl',
            'risk_hazard_only', 'risk_vuln_fiscal_only', 'risk_HV_mean', 'risk_HV_prod', 'H_missing_items', 'E_missing_items',
            'V_missing_items', 'F_missing_items']
    snap = snap.merge(hazard[['region_id', 'region_name', 'area_km2_geom']], on='region_id', how='left',
                      suffixes=('_x', ''))
    snap.to_csv(OUT / f'COUNCIL_ITEMS{SUF}.csv', index=False)      # every item + block, used by the RF script
    snap[keep].sort_values('risk_add', ascending=False).to_csv(OUT / f'COUNCIL_RISK_SCORE{SUF}.csv', index=False)
    print(len(snap), 'councils scored')

    m = load_master().merge(snap[['region_id', 'H', 'E', 'V', 'F', 'risk_add', 'risk_mult', 'risk_add_no_bfpl',
                                  'risk_hazard_only', 'risk_vuln_fiscal_only', 'risk_HV_mean', 'risk_HV_prod']], on='region_id', how='left')
    print('rows with score', m.risk_add.notna().sum(), 'of', len(m))
    m['rows_pop'] = 1
    scores = ['risk_add', 'risk_mult', 'risk_add_no_bfpl', 'risk_hazard_only', 'risk_vuln_fiscal_only',
              'risk_HV_mean', 'risk_HV_prod', 'H', 'E', 'V', 'F']

    # ---- 1. row-level validation, by large-fire definition
    rows = []
    for dname, mask in definitions(m).items():
        sub = m[mask]
        for sc in scores:
            for y in YCOLS:
                n, est, lo, hi = boot_spearman(sub[sc], sub[y], sub.region_id, rng)
                rows.append(dict(definition=dname, rows=int(mask.sum()), fires=int(sub.agrn.nunique()),
                                 councils=int(sub.region_id.nunique()), score=sc, target=y,
                                 n_used=n, spearman=est, ci_low=lo, ci_high=hi))
    val = pd.DataFrame(rows)
    val.to_csv(OUT / f'VALIDATION_ROW_LEVEL{SUF}.csv', index=False)

    # ---- 2. Black Summer excluded (declaration 871) and Black Summer only
    bs = (m.agrn.astype(str) == '871')
    rows = []
    for label, mask in {'Black Summer only': bs, 'excluding Black Summer': ~bs}.items():
        sub = m[mask]
        for sc in ['risk_add', 'risk_add_no_bfpl', 'risk_mult', 'risk_HV_mean']:
            for y in YCOLS:
                n, est, lo, hi = boot_spearman(sub[sc], sub[y], sub.region_id, rng)
                rows.append(dict(subset=label, rows=int(mask.sum()), score=sc, target=y, n_used=n,
                                 spearman=est, ci_low=lo, ci_high=hi))
    pd.DataFrame(rows).to_csv(OUT / f'VALIDATION_BLACK_SUMMER_SPLIT{SUF}.csv', index=False)

    # ---- 3. council-level: did high-risk councils suffer more?
    allc = snap[['region_id', 'region_name', 'risk_add', 'risk_add_no_bfpl', 'risk_mult', 'H', 'E', 'V', 'F', 'risk_HV_mean', 'risk_HV_prod', 'bfpl_share_cat1', 'bfpl_share_cat12', 'nvis_forest_share', 'bfpl_share_any']].copy()
    g = m.groupby('region_id')
    cs = pd.DataFrame({'max_Y': g.Y.max(), 'mean_Y': g.Y.mean(), 'n_fires': g.size(),
                       'max_share': g.share.max(), 'max_burn_ha': g.burn_ha.max()}).reset_index()
    allc = allc.merge(cs, on='region_id', how='left')
    rows = []
    for dname, thr in {'share >= 2%': .02, 'share >= 5%': .05, 'share >= 10%': .10, 'share >= 20%': .20}.items():
        pos = (allc.max_share.fillna(0) >= thr).to_numpy()
        for sc in ['risk_add', 'risk_add_no_bfpl', 'risk_mult', 'H', 'E', 'V', 'F', 'risk_HV_mean', 'risk_HV_prod', 'bfpl_share_cat1', 'bfpl_share_cat12', 'nvis_forest_share', 'bfpl_share_any']:
            rows.append(dict(event=f'council had a fire with {dname}', positives=int(pos.sum()), councils=len(allc),
                             score=sc, AUC=auc(allc[sc].to_numpy(), pos)))
    pd.DataFrame(rows).to_csv(OUT / f'VALIDATION_COUNCIL_AUC{SUF}.csv', index=False)
    aff = allc[allc.n_fires.notna()]
    rows = []
    for sc in ['risk_add', 'risk_add_no_bfpl', 'risk_mult', 'H', 'E', 'V', 'F', 'risk_HV_mean']:
        for y in ['max_Y', 'mean_Y']:
            n, est, lo, hi = boot_spearman(aff[sc], aff[y], aff.region_id, rng)
            rows.append(dict(score=sc, target=y, councils=n, spearman=est, ci_low=lo, ci_high=hi))
    pd.DataFrame(rows).to_csv(OUT / f'VALIDATION_COUNCIL_SEVERITY{SUF}.csv', index=False)

    corr = snap[['bfpl_share_any', 'bfpl_share_cat1', 'bfpl_share_cat12', 'nvis_forest_share', 'population']].corr(method='spearman')
    corr.round(3).to_csv(OUT / f'HAZARD_INPUT_CORRELATIONS{SUF}.csv')
    m['risk_quintile_dummy'] = 0
    # ---- 4. risk quintile vs impact
    m['risk_quintile'] = pd.qcut(m.risk_add, 5, labels=[1, 2, 3, 4, 5])
    q = m.groupby('risk_quintile', observed=True).agg(rows=('Y', 'size'), councils=('region_id', 'nunique'),
                                                        mean_Y=('Y', 'mean'), mean_DL=('DL', 'mean'),
                                                        mean_IL=('IL', 'mean'), mean_FP=('FP', 'mean'),
                                                        mean_SL=('SL', 'mean'), share_severe=('Y_class', lambda s: (s >= 3).mean()))
    q.to_csv(OUT / f'QUINTILES{SUF}.csv')

    # ---- 5. definitions: how many cases each gives
    dd = []
    for dname, mask in definitions(m).items():
        sub = m[mask]
        dd.append(dict(definition=dname, rows=int(mask.sum()), fires=int(sub.agrn.nunique()),
                       councils=int(sub.region_id.nunique()), years=', '.join(map(str, sorted(sub.year.unique()))),
                       black_summer_rows=int((sub.agrn.astype(str) == '871').sum()),
                       mean_Y=float(sub.Y.mean())))
    pd.DataFrame(dd).to_csv(OUT / f'LARGE_FIRE_DEFINITIONS{SUF}.csv', index=False)

    m[['agrn', 'region_id', 'region_name', 'year', 'share', 'burn_ha', 'Y', 'DL', 'IL', 'FP', 'SL', 'Y_class'] +
      scores].to_csv(OUT / f'ROWS_WITH_SCORE{SUF}.csv', index=False)
    json.dump(dict(seed=SEED, n_boot=N_BOOT, councils_scored=int(len(snap)), master_rows=int(len(m)),
                   rows_with_score=int(m.risk_add.notna().sum())), open(OUT / f'SUMMARY{SUF}.json', 'w'), indent=2)
    print(val[(val.score == 'risk_add')].pivot_table(index='definition', columns='target', values='spearman').round(2))


if __name__ == '__main__':
    main()
