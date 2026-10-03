"""Experiment 7, Day 7, dataset B: SA2 business counts (ABS CABEE 8165.0, June stocks, all industries)
vs share of residents within 1 km of fires (PRESPEC_DAY7.md, LOCK_DAY7.txt).

Model (fixed by PRESPEC_DAY7, annual):
  log count[s, June y] = a[s] + b[GCCSA, y] + beta0 D[s, FY y-1] + beta1 D[s, FY y-2]
                         + lambda1 D[s, FY y] + lambda2 D[s, FY y+1]
  FY is labelled by its starting year (prep_sa2_dose.py), so FY y-1 = Jul (y-1)..Jun y, the 12 months before the
  June y count. SEs clustered by SA3. Primary = beta0 + beta1, placebo = lambda1 + lambda2, per 10 pp of residents,
  reported in % (log points x 100). Worse direction for B: down. Detected = primary CI < 0 AND placebo CI includes 0.

Panel construction (panels/sa2_businesses.parquet):
  Each June comes from the latest release that contains it (each SA2 cube holds only its last 3 Junes):
    2023-2025  Jul2021-Jun2025 release, 8165DC08 (ASGS 2021)
    2021-2022  Jul2019-Jun2023 release, 8165DC08_revised (ASGS 2021)
    2019-2020  Jul2017-Jun2021 release, 816508 (ASGS 2021)
    2017-2018  Jul2015-Jun2019 release, 816508.xls (ASGS 2016)
    2015-2016  Jun2013-Jun2017 release, 816508.xls (ASGS 2016)
  value = sum of the 'Total' column over all industry divisions (A..S and X 'Currently Unknown').
  ASGS 2016 years are kept only for SA2s whose code AND name are identical in ASGS 2021, and are ratio-linked
  (as in day5_sa2_income.py): June 2017-18 are scaled by count(2019, ASGS 2021 release)/count(2019, Jun2019 release);
  June 2015-16 by count(2017, Jun2019 release)/count(2017, Jun2017 release), then by the 2019 factor.
  'value_raw' keeps the unlinked latest-release value.
Run: python3 day7_B_businesses.py  (builds the panel if missing)"""
import json
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

from xls_reader import read_xls, to_rows

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
RAW = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/raw/sa2/businesses')
PANEL = HERE / 'panels/sa2_businesses.parquet'
SCALE = 0.1   # per 10 percentage points of residents affected (dose is a 0-1 share)

# (file, sheet, june, release label, asgs)
SOURCES = [
    ('jul2021-jun2025_8165DC08.xlsx', 'Table 1', 2025, 'Jul2021-Jun2025', 2021),
    ('jul2021-jun2025_8165DC08.xlsx', 'Table 2', 2024, 'Jul2021-Jun2025', 2021),
    ('jul2021-jun2025_8165DC08.xlsx', 'Table 3 ', 2023, 'Jul2021-Jun2025', 2021),
    ('jul2019-jun2023_8165DC08_revised.xlsx', 'Table 1', 2023, 'Jul2019-Jun2023', 2021),
    ('jul2019-jun2023_8165DC08_revised.xlsx', 'Table 2', 2022, 'Jul2019-Jun2023', 2021),
    ('jul2019-jun2023_8165DC08_revised.xlsx', 'Table 3', 2021, 'Jul2019-Jun2023', 2021),
    ('jul2017-jun2021_816508.xlsx', '2021 a', 2021, 'Jul2017-Jun2021', 2021),
    ('jul2017-jun2021_816508.xlsx', '2020 a', 2020, 'Jul2017-Jun2021', 2021),
    ('jul2017-jun2021_816508.xlsx', '2019', 2019, 'Jul2017-Jun2021', 2021),
    ('jul2015-jun2019_816508.xls', 'June 2019', 2019, 'Jul2015-Jun2019', 2016),
    ('jul2015-jun2019_816508.xls', 'June 2018', 2018, 'Jul2015-Jun2019', 2016),
    ('jul2015-jun2019_816508.xls', 'June 2017', 2017, 'Jul2015-Jun2019', 2016),
    ('jun2013-jun2017_816508.xls', 'June 2017', 2017, 'Jun2013-Jun2017', 2016),
    ('jun2013-jun2017_816508.xls', 'June 2016', 2016, 'Jun2013-Jun2017', 2016),
    ('jun2013-jun2017_816508.xls', 'June 2015', 2015, 'Jun2013-Jun2017', 2016),
]
# latest release for each June
USE = {2025: 'Jul2021-Jun2025', 2024: 'Jul2021-Jun2025', 2023: 'Jul2021-Jun2025', 2022: 'Jul2019-Jun2023',
       2021: 'Jul2019-Jun2023', 2020: 'Jul2017-Jun2021', 2019: 'Jul2017-Jun2021', 2018: 'Jul2015-Jun2019',
       2017: 'Jul2015-Jun2019', 2016: 'Jun2013-Jun2017', 2015: 'Jun2013-Jun2017'}


def read_table(fname, sheet):
    path = RAW / fname
    if fname.endswith('.xlsx'):
        rows = list(openpyxl.load_workbook(path, read_only=True)[sheet].iter_rows(values_only=True))
    else:
        rows = to_rows(read_xls(path, sheets={sheet})[sheet])
    hdr = next(i for i, r in enumerate(rows) if r and r[0] == 'Industry' and r[2] == 'SA2')
    assert rows[hdr][9] == 'Total', rows[hdr]
    title = next(str(r[0]) for r in rows[:hdr] if r and r[0] and 'Statistical Area Level 2' in str(r[0]))
    d = pd.DataFrame([r[:10] for r in rows[hdr + 2:] if r and r[0] is not None and r[2] is not None],
                     columns=['ind', 'ind_label', 'SA2', 'name', 'ne', 'e1', 'e5', 'e20', 'e200', 'total'])
    d['SA2'] = pd.to_numeric(d.SA2).astype('int64').astype(str)
    d['total'] = pd.to_numeric(d.total, errors='coerce')
    g = d.groupby(['SA2', 'name'], as_index=False).agg(total=('total', lambda x: x.sum(min_count=1)),
                                                       n_ind=('ind', 'nunique'))
    return g, title


def build_panel():
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    tabs = []
    for fname, sheet, june, rel, asgs in SOURCES:
        g, title = read_table(fname, sheet)
        assert f'June {june}' in title, (fname, sheet, title)
        g['june'], g['release'], g['asgs'], g['file'] = june, rel, asgs, fname
        tabs.append(g)
    t = pd.concat(tabs, ignore_index=True)
    new_names = t[t.asgs == 2021][['SA2', 'name']].drop_duplicates()
    old_names = t[t.asgs == 2016][['SA2', 'name']].drop_duplicates()
    same = new_names.merge(old_names, on=['SA2', 'name'])          # code and name unchanged 2016 -> 2021
    keep16 = set(same.SA2)
    tot = t.set_index(['SA2', 'release', 'june']).total
    f19 = (tot.xs(('Jul2017-Jun2021', 2019), level=['release', 'june']) /
           tot.xs(('Jul2015-Jun2019', 2019), level=['release', 'june']))
    f17 = (tot.xs(('Jul2015-Jun2019', 2017), level=['release', 'june']) /
           tot.xs(('Jun2013-Jun2017', 2017), level=['release', 'june']))
    p = t[[USE[j] == r for j, r in zip(t.june, t.release)]].copy()
    p = p[(p.asgs == 2021) | p.SA2.isin(keep16)].copy()
    p['link_factor'] = 1.0
    o = p.asgs == 2016
    p.loc[o, 'link_factor'] = p.loc[o, 'SA2'].map(f19).values
    o15 = p.june.isin([2015, 2016])
    p.loc[o15, 'link_factor'] = p.loc[o15, 'link_factor'] * p.loc[o15, 'SA2'].map(f17).values
    p['link_factor'] = p.link_factor.where(np.isfinite(p.link_factor))   # zero/missing base count: not linkable
    p['value_raw'] = p.total
    p['value'] = p.total * p.link_factor
    p['period'] = 'June ' + p.june.astype(str)
    p['in_sa2_info'] = p.SA2.isin(set(info.SA2))
    p['measure'] = 'CABEE business count, all industries (sum of Total over divisions A-S and X)'
    p = p[['SA2', 'name', 'period', 'june', 'value', 'value_raw', 'link_factor', 'release', 'asgs', 'file',
           'n_ind', 'measure', 'in_sa2_info']].sort_values(['SA2', 'june']).reset_index(drop=True)
    p.to_parquet(PANEL, index=False)
    return p


def absorb(M, groups, tol=1e-12, maxit=5000):
    """Residualise columns of M on several sets of categorical fixed effects (alternating projections)."""
    M = M.copy()
    codes = [pd.factorize(g)[0] for g in groups]
    for _ in range(maxit):
        old = M.copy()
        for c in codes:
            n = np.bincount(c)
            for j in range(M.shape[1]):
                M[:, j] -= (np.bincount(c, weights=M[:, j]) / n)[c]
        if np.max(np.abs(M - old)) < tol:
            break
    return M


def fit(p, D):
    """OLS with SA2 and GCCSA x year fixed effects absorbed by alternating projections (Frisch-Waugh-Lovell;
    identical point estimates to dummies; statsmodels' dummy OLS returned NaN on this design matrix);
    SEs clustered by SA3 with the CR1 correction used in day7_U_unemployment.py."""
    p = p.copy()
    names = ['b0', 'b1', 'l1', 'l2']
    for lab, k in (('b0', 1), ('b1', 2), ('l1', 0), ('l2', -1)):
        p[lab] = [D.get((s, y - k), 0.0) for s, y in zip(p.SA2, p.june)]
    g2 = p.GCCSA + '_' + p.june.astype(str)
    M = absorb(p[['y'] + names].to_numpy(float), [p.SA2.to_numpy(), g2.to_numpy()])
    y, X = M[:, 0], M[:, 1:]
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    cl = pd.factorize(p.SA3)[0]
    G = cl.max() + 1
    S = np.zeros((G, X.shape[1]))
    np.add.at(S, cl, X * e[:, None])
    N = len(y)
    K = X.shape[1] + g2.nunique()     # SA2 FE nested in SA3 clusters (not counted, as fixest / the U script)
    V = XtX_inv @ (S.T @ S) @ XtX_inv * G / (G - 1) * (N - 1) / (N - K)

    def comb(cols):
        w = np.array([SCALE if n in cols else 0.0 for n in names])
        est, se = float(w @ b) * 100, float(np.sqrt(w @ V @ w)) * 100
        return dict(est=est, se=se, ci_low=est - 1.96 * se, ci_high=est + 1.96 * se)
    return dict(n_obs=int(N), n_sa2=int(p.SA2.nunique()), n_clusters=int(G),
                n_treated_sa2=int(p.loc[p[names].abs().sum(axis=1) > 0, 'SA2'].nunique()),
                primary=comb(['b0', 'b1']), placebo=comb(['l1', 'l2']),
                coefs_pct_per10pp={n: float(b[i] * SCALE * 100) for i, n in enumerate(names)},
                ses_pct_per10pp={n: float(np.sqrt(V[i, i]) * SCALE * 100) for i, n in enumerate(names)})


def verdict(r):
    pr, pl = r['primary'], r['placebo']
    placebo_ok = pl['ci_low'] <= 0 <= pl['ci_high']
    if pr['ci_high'] < 0 and placebo_ok:
        return 'Detected'
    if pr['ci_high'] < 0:
        return 'Not claimed: placebo fails'
    return 'Not detected'


def main():
    w = pd.read_parquet(PANEL) if PANEL.exists() else build_panel()
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    ok = w[np.isfinite(w.value) & (w.value > 0)]
    match = dict(sa2_info_n=int(len(info)),
                 sa2_info_codes_in_cabee_asgs2021=int(info.SA2.isin(set(w[w.asgs == 2021].SA2)).sum()),
                 sa2_info_codes_with_positive_count=int(info.SA2.isin(set(ok.SA2)).sum()),
                 sa2_info_codes_linked_back_to_asgs2016=int(info.SA2.isin(set(w[w.asgs == 2016].SA2)).sum()))
    match['match_rate'] = match['sa2_info_codes_in_cabee_asgs2021'] / match['sa2_info_n']
    dose = pd.read_parquet(HERE / 'panels/sa2_fy_dose.parquet')
    D = {(s, int(y)): v for s, y, v in zip(dose.SA2, dose.fy, dose.dose)}
    match['dose_sa2s_with_counts'] = int(dose.SA2.drop_duplicates().isin(set(ok.SA2)).sum())
    match['dose_sa2s_total'] = int(dose.SA2.nunique())

    p = ok.merge(info[['SA2', 'SA3', 'GCCSA']], on='SA2', how='inner')
    p['SA3'], p['GCCSA'] = p.SA3.astype(str), p.GCCSA.astype(str)
    p['y'] = np.log(p.value)
    p = p.reset_index(drop=True)
    res = dict(dataset='B: ABS CABEE 8165.0 business counts by SA2 (June stocks, all industries), ASGS 2021 '
                       '(June 2015-2018 from ASGS 2016 releases, unchanged codes only, ratio-linked)',
               source_files=sorted({s[0] for s in SOURCES}), source_dir=str(RAW),
               units='% change in business count (log points x 100) per 10 pp of residents within 1 km',
               worse_direction='down', period_range=f'June {p.june.min()}..June {p.june.max()}',
               panel_rows=int(len(p)), sa2s=int(p.SA2.nunique()), code_match=match,
               dose_fy_range=[int(dose.fy.min()), int(dose.fy.max())])
    main_r = fit(p, D)
    res['main'] = main_r
    res['verdict'] = verdict(main_r)
    res['bound_in_worse_direction'] = main_r['primary']['ci_low']   # largest fall consistent with the data

    # Also reported (PRESPEC): heavily affected SA2s (dose >= 25%) and Black Summer only (FY 2019 = Jul 2019-Jun 2020)
    mx = dose.groupby('SA2').dose.max()
    heavy = set(mx[mx >= 0.25].index)
    zero = set(p.SA2) - set(mx[mx > 0].index)
    ph = p[p.SA2.isin(heavy | zero)].reset_index(drop=True)
    res['heavy'] = dict(definition='sample = SA2s with any FY dose >= 25% plus SA2s with zero dose in every FY; '
                                   'same model', **fit(ph, D))
    bs = {k: v for k, v in D.items() if k[1] == 2019}
    res['black_summer'] = dict(definition='dose kept only for FY 2019 (Jul 2019-Jun 2020, covers fire quarters '
                                          '2019Q3-2020Q1; other FYs set to 0); full sample; same model', **fit(p, bs))
    # Sensitivities (not part of the verdict)
    pin = p[p.june.between(2016, 2023)].reset_index(drop=True)
    res['sens_window_all_terms_observed'] = dict(
        definition='June 2016-2023 only, where every dose term (FY y-2..y+1) lies inside the dose panel', **fit(pin, D))
    pr = p.copy()
    pr['y'] = np.log(pr.value_raw)
    res['sens_unlinked'] = dict(definition='latest-release counts without ratio-linking the ASGS 2016 years',
                                **fit(pr[np.isfinite(pr.y)].reset_index(drop=True), D))
    pa = p[p.asgs == 2021].reset_index(drop=True)
    res['sens_asgs2021_only'] = dict(definition='June 2019-2025 only (ASGS 2021 releases, no chaining)', **fit(pa, D))
    for k in ('heavy', 'black_summer', 'sens_window_all_terms_observed', 'sens_unlinked', 'sens_asgs2021_only'):
        res[k]['verdict'] = verdict(res[k])
    res['notes'] = [
        'Dose panel covers FY 2014 (fires from Jan 2015 only) to FY 2024; dose terms outside it are set to 0 '
        '(June 2015 lag FY 2013; June 2024-2025 leads FY 2025-2026), as in the U script.',
        'Each CABEE SA2 cube holds only its last 3 Junes, so five releases are chained; June values come from the '
        'latest release containing them.',
        'CABEE cells are perturbed by the ABS for confidentiality; the SA2 total is the sum of perturbed division totals.',
        'From the Jul2017-Jun2021 release on, size ranges are annualised; the Total column (all sizes) is used throughout.',
        'Primary = beta0 + beta1, placebo = lambda1 + lambda2 (sums, per PRESPEC), scaled to 10 pp of residents; '
        'normal CIs (1.96) with cluster CR1 correction (as day7_U_unemployment.py).']
    OUT.mkdir(exist_ok=True)
    json.dump(res, open(OUT / 'DAY7_B.json', 'w'), indent=2, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == '__main__':
    main()
