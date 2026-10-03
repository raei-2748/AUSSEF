"""Experiment 7, Day 7, dataset U: SA2 unemployment rate (DEWR SALM, UNSMOOTHED, ASGS 2021, quarterly)
vs share of residents within 1 km of fires (PRESPEC_DAY7.md, LOCK_DAY7.txt).

Model (fixed by PRESPEC_DAY7, quarterly):
  y[s,q] = a[s,season] + b[GCCSA,q] + sum_{k=0..4} beta_k D[s,q-k] + sum_{k=1..4} lambda_k D[s,q+k]
  (a[s,season] absorbs a[s]); SEs clustered by SA3; sample 2016Q1..2025Q2.
  Primary = mean(beta_0..beta_4) per 10 pp of residents affected; placebo = mean(lambda_1..lambda_4).
  Worse direction for U: up. Detected = primary CI > 0 AND placebo CI includes 0.
Fixed effects are absorbed by alternating projections (Frisch-Waugh-Lovell); identical point estimates to dummies.
Run: python3 day7_U_unemployment.py  (builds panels/sa2_unemployment.parquet if missing)"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
RAW = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/raw/sa2/U_salm_unsmoothed/'
           'salm_unsmoothed_sa2_asgs2021_mar2026.csv')
PANEL = HERE / 'panels/sa2_unemployment.parquet'
QMAP = {'Mar': 1, 'Jun': 2, 'Sep': 3, 'Dec': 4}
START, END = pd.Period('2016Q1', 'Q'), pd.Period('2025Q2', 'Q')
LAGS, LEADS = range(0, 5), range(1, 5)
SCALE = 0.1   # per 10 percentage points of residents affected (dose is a 0-1 share)


def build_panel():
    d = pd.read_csv(RAW, skiprows=2, dtype=str, encoding='utf-8-sig')
    d = d.rename(columns={'Data Item': 'item', 'Statistical Area Level 2 (SA2) (2021 ASGS)': 'name',
                          'SA2 Code (2021 ASGS)': 'SA2'}).dropna(subset=['SA2'])
    long = d.melt(id_vars=['item', 'name', 'SA2'], var_name='q', value_name='v')
    long['v'] = pd.to_numeric(long.v.str.replace(',', '').str.strip(), errors='coerce')   # '-' -> NaN
    long['period'] = [str(pd.Period(year=2000 + int(q[-2:]), quarter=QMAP[q[:3]], freq='Q')) for q in long.q]
    w = long.pivot_table(index=['SA2', 'name', 'period'], columns='item', values='v', aggfunc='first').reset_index()
    w = w.rename(columns={'Unsmoothed unemployment rate (%)': 'value',
                          'Unsmoothed unemployment (persons)': 'unemployed',
                          'Unsmoothed labour force (persons)': 'labour_force'})
    w.columns.name = None
    w['SA2'] = w.SA2.astype(str).str.strip()
    w['measure'] = 'unsmoothed unemployment rate (%)'
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    w['in_sa2_info'] = w.SA2.isin(set(info.SA2))
    w = w[['SA2', 'name', 'period', 'value', 'unemployed', 'labour_force', 'measure', 'in_sa2_info']]
    w.to_parquet(PANEL, index=False)
    return w


def absorb(M, groups, tol=1e-10, maxit=2000):
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
    """p: panel rows (SA2, period Period, y, season, GCCSA, SA3); D: dict (SA2, Period) -> dose."""
    p = p.copy()
    names = [f'b{k}' for k in LAGS] + [f'l{k}' for k in LEADS]
    for k in LAGS:
        p[f'b{k}'] = [D.get((s, q - k), 0.0) for s, q in zip(p.SA2, p.period)]
    for k in LEADS:
        p[f'l{k}'] = [D.get((s, q + k), 0.0) for s, q in zip(p.SA2, p.period)]
    g1 = p.SA2 + '_' + p.season.astype(str)
    g2 = p.GCCSA + '_' + p.period.astype(str)
    M = absorb(p[['y'] + names].to_numpy(float), [g1.to_numpy(), g2.to_numpy()])
    y, X = M[:, 0], M[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    cl = pd.factorize(p.SA3)[0]
    G = cl.max() + 1
    S = np.zeros((G, X.shape[1]))
    np.add.at(S, cl, X * e[:, None])
    N = len(y)
    K = X.shape[1] + g2.nunique()     # SA2 x season FE are nested in SA3 clusters (not counted, as fixest)
    V = XtX_inv @ (S.T @ S) @ XtX_inv * G / (G - 1) * (N - 1) / (N - K)
    tcrit = 1.96

    def comb(cols):
        w = np.zeros(len(names))
        for c in cols:
            w[names.index(c)] = SCALE / len(cols)
        est, se = float(w @ b), float(np.sqrt(w @ V @ w))
        return dict(est=est, se=se, ci_low=est - tcrit * se, ci_high=est + tcrit * se)
    out = dict(n_obs=int(N), n_sa2=int(p.SA2.nunique()), n_clusters=int(G),
               n_treated_sa2=int(p.loc[p[names].abs().sum(axis=1) > 0, 'SA2'].nunique()),
               primary=comb([f'b{k}' for k in LAGS]), placebo=comb([f'l{k}' for k in LEADS]),
               coefs_per10pp={n: float(b[i] * SCALE) for i, n in enumerate(names)},
               ses_per10pp={n: float(np.sqrt(V[i, i]) * SCALE) for i, n in enumerate(names)})
    return out


def verdict(r):
    pr, pl = r['primary'], r['placebo']
    placebo_ok = pl['ci_low'] <= 0 <= pl['ci_high']
    if pr['ci_low'] > 0 and placebo_ok:
        return 'Detected'
    if pr['ci_low'] > 0:
        return 'Not claimed: placebo fails'
    return 'Not detected'


def main():
    w = pd.read_parquet(PANEL) if PANEL.exists() else build_panel()
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    ok = w.dropna(subset=['value'])
    match = dict(sa2_info_n=int(len(info)),
                 sa2_info_codes_in_salm_file=int(info.SA2.isin(set(w.SA2)).sum()),
                 sa2_info_codes_with_any_rate=int(info.SA2.isin(set(ok.SA2)).sum()),
                 sa2_info_codes_with_rate_in_window=int(info.SA2.isin(set(
                     ok[ok.period.map(lambda s: START <= pd.Period(s, 'Q') <= END)].SA2)).sum()))
    match['match_rate_any_rate'] = match['sa2_info_codes_with_any_rate'] / match['sa2_info_n']
    dq = pd.read_parquet(HERE / 'panels/sa2_quarter_dose.parquet')
    dq['q'] = dq.quarter.map(lambda s: pd.Period(s, 'Q'))
    match['dose_sa2s_in_salm_with_rate'] = int(dq.SA2.drop_duplicates().isin(set(ok.SA2)).sum())
    match['dose_sa2s_total'] = int(dq.SA2.nunique())
    D = {(s, q): v for s, q, v in zip(dq.SA2, dq.q, dq.dose)}

    p = ok.merge(info[['SA2', 'SA3', 'GCCSA']], on='SA2', how='inner')
    p['period'] = p.period.map(lambda s: pd.Period(s, 'Q'))
    p = p[(p.period >= START) & (p.period <= END)].copy()
    p['y'] = p.value.astype(float)
    p['season'] = p.period.map(lambda q: q.quarter)
    p['SA3'], p['GCCSA'] = p.SA3.astype(str), p.GCCSA.astype(str)
    p = p.reset_index(drop=True)

    res = dict(dataset='U: DEWR SALM unsmoothed SA2 unemployment rate (%), ASGS 2021',
               source_file=str(RAW), units='percentage points of unemployment rate per 10 pp of residents within 1 km',
               worse_direction='up', period_range=f'{p.period.min()}..{p.period.max()}',
               panel_rows=int(len(p)), sa2s=int(p.SA2.nunique()), code_match=match)
    main_r = fit(p, D)
    res['main'] = main_r
    res['verdict'] = verdict(main_r)
    res['bound_in_worse_direction'] = main_r['primary']['ci_high']   # largest increase consistent with data

    # Also reported (PRESPEC): heavily affected SA2s (dose >= 25%) and Black Summer only (fire quarters 2019Q3-2020Q1)
    mx = dq.groupby('SA2').dose.max()
    heavy = set(mx[mx >= 0.25].index)
    zero = set(p.SA2) - set(mx[mx > 0].index)
    ph = p[p.SA2.isin(heavy | zero)].reset_index(drop=True)
    res['heavy'] = dict(definition='sample = SA2s with any fire-quarter dose >= 25% plus SA2s with zero dose in '
                                   'every quarter; same model', **fit(ph, D))
    bs = {k: v for k, v in D.items() if pd.Period('2019Q3', 'Q') <= k[1] <= pd.Period('2020Q1', 'Q')}
    res['black_summer'] = dict(definition='dose kept only for fire quarters 2019Q3-2020Q1 (other quarters set to 0); '
                                          'full sample; same model', **fit(p, bs))
    for k in ('heavy', 'black_summer'):
        res[k]['verdict'] = verdict(res[k])
    res['notes'] = ['DEWR flags March quarter 2025 unsmoothed estimates in some SA4s (mutual-obligation suspensions) '
                    'as to be viewed with caution; kept in sample as pre-specified.',
                    'Leads for 2024Q3..2025Q2 reach beyond the dose panel end (2025Q2); later fires counted as 0.',
                    'Primary and placebo are averages of the 5 lag / 4 lead coefficients, scaled to 10 pp of '
                    'residents; CIs are normal (1.96) with CR1 small-sample correction.']
    OUT.mkdir(exist_ok=True)
    json.dump(res, open(OUT / 'DAY7_U.json', 'w'), indent=2, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == '__main__':
    main()
