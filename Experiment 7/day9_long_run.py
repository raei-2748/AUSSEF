"""Experiment 7, Day 9: up to 5 years after the fire, dose = share of SA2 homes inside the fire outline
(PRESPEC_DAY9.md, LOCK_DAY9.txt). Run: python3 day9_long_run.py"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import day5_sa2_income as D5

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'


def fy_of_period(p):
    p = pd.Period(p, 'Q')
    return p.year if p.quarter >= 3 else p.year - 1


def panels():
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    u = pd.read_parquet(HERE / 'panels/sa2_unemployment.parquet')
    u = u[u.in_sa2_info].assign(fy=lambda t: t.period.map(fy_of_period))
    u = u.groupby(['SA2', 'fy']).value.mean().rename('y').reset_index()
    w = pd.read_parquet(HERE / 'panels/sa2_welfare.parquet')
    w = w[w.code_unchanged & w.in_sa2_info & w.value.notna() & (w['pop'] >= 100)].assign(
        fy=lambda t: t.period.map(fy_of_period))
    w = w.groupby(['SA2', 'fy']).value.mean().rename('y').reset_index()
    b = pd.read_parquet(HERE / 'panels/sa2_businesses.parquet')
    b = b[b.in_sa2_info & (b.value > 0)].assign(fy=lambda t: t.june - 1, y=lambda t: np.log(t.value))[['SA2', 'fy', 'y']]
    inc, _ = D5.panel()
    inc = inc.merge(info[['SA2', 'pop']], on='SA2')
    inc = inc[(inc['pop'] >= 100) & (inc['sum'] > 0)]
    ts = inc.assign(y=np.log(inc['sum']))[['SA2', 'fy', 'y']]
    tm = inc.assign(y=np.log(inc['median']))[['SA2', 'fy', 'y']]
    return {'unemployment_rate': (u, 'up', 5, 'percentage points'), 'welfare_per_1000': (w, 'up', 5, 'per 1,000'),
            'log_businesses': (b, 'down', 5, 'log x100 = %'), 'log_total_income': (ts, 'down', 2, 'log x100 = %'),
            'log_median_income': (tm, 'down', 2, 'log x100 = %')}, info


def main():
    dose = pd.read_parquet(HERE / 'panels/sa2_fy_dose_homes_in.parquet').set_index(['SA2', 'fy']).dose
    pans, info = panels()
    rows, paths = [], []
    for name, (p, worse, K, unit) in pans.items():
        p = p[p.fy.between(2015, 2024)].merge(info[['SA2', 'SA3', 'GCCSA']], on='SA2', how='inner').dropna(subset=['y'])
        lags = [f'B{k}' for k in range(K + 1)]
        for k in range(K + 1):
            p[f'B{k}'] = [dose.get((s, t - k), 0.0) for s, t in zip(p.SA2, p.fy)]
        p['F1'] = [dose.get((s, t + 1), 0.0) for s, t in zip(p.SA2, p.fy)]
        p['F2'] = [dose.get((s, t + 2), 0.0) for s, t in zip(p.SA2, p.fy)]
        p['gt'] = p.GCCSA.astype(str) + '_' + p.fy.astype(str)
        scale = 100 if name.startswith('log') else 1
        X = p[lags + ['F1', 'F2']].astype(float)
        Y = p['y'].astype(float)
        # Frisch-Waugh: sweep out SA2 and GCCSA x year effects by alternating projections, then OLS + SA3 clusters
        def sweep(v):
            v = v.copy()
            for _ in range(200):
                old = v.copy()
                v = v - v.groupby(p.SA2.values).transform('mean')
                v = v - v.groupby(p['gt'].values).transform('mean')
                if np.max(np.abs((v - old).to_numpy())) < 1e-10:
                    break
            return v
        Xr = X.apply(sweep)
        yr = sweep(Y)
        XtX_inv = np.linalg.inv(Xr.T.to_numpy() @ Xr.to_numpy())
        beta = XtX_inv @ Xr.T.to_numpy() @ yr.to_numpy()
        resid = yr.to_numpy() - Xr.to_numpy() @ beta
        meat = np.zeros((X.shape[1], X.shape[1]))
        for _, idx in p.groupby(p.SA3.astype(str)).indices.items():
            sg = Xr.to_numpy()[idx].T @ resid[idx]
            meat += np.outer(sg, sg)
        G, N, Kp = p.SA3.nunique(), len(p), X.shape[1] + p.SA2.nunique() + p['gt'].nunique()
        V = XtX_inv @ meat @ XtX_inv * G / (G - 1) * (N - 1) / (N - Kp)
        params = pd.Series(beta, index=X.columns)
        cov = pd.DataFrame(V, index=X.columns, columns=X.columns)

        class M:
            pass
        m = M()
        m.params = params
        m.cov_params = lambda: cov

        def comb(names):
            from scipy.stats import norm
            wv = pd.Series(0.0, index=params.index)
            wv[names] = 0.1 / len(names)
            e, se = float(wv @ params), float(np.sqrt(wv @ cov @ wv))
            z = e / se if se > 0 else 0.0
            return e * scale, (e - 1.96 * se) * scale, (e + 1.96 * se) * scale, float(2 * norm.sf(abs(z)))
        long_names = ['B2'] if K == 2 else [f'B{k}' for k in range(2, K + 1)]
        le, ll, lh, lp = comb(long_names)
        se_, sl, sh, _ = comb(['B0', 'B1'])
        pe, pl, ph, _ = comb(['F1', 'F2'])
        rows.append(dict(outcome=name, unit=unit, worse=worse, rows=int(len(p)), sa2s=int(p.SA2.nunique()),
                         years=f'{p.fy.min()}-{p.fy.max()}', long_run=le, long_lo=ll, long_hi=lh, long_p=lp,
                         short_run=se_, short_lo=sl, short_hi=sh, placebo=pe, placebo_lo=pl, placebo_hi=ph,
                         treated_sa2s=int((p.B0 > 0.01).groupby(p.SA2).any().sum())))
        for k in range(K + 1):
            e, lo, hi, _ = comb([f'B{k}'])
            paths.append(dict(outcome=name, years_after=k, est=e * 1, lo=lo, hi=hi))
    t = pd.DataFrame(rows)
    order = np.argsort(t.long_p.to_numpy())
    adj, run = np.empty(len(t)), 0
    for i, j in enumerate(order):
        run = max(run, (len(t) - i) * t.long_p.iloc[j])
        adj[j] = min(1, run)
    t['long_p_holm'] = adj
    worse_dir = np.where(t.worse == 'up', t.long_lo > 0, t.long_hi < 0)
    t['detected'] = worse_dir & (t.long_p_holm < 0.05) & (t.placebo_lo <= 0) & (t.placebo_hi >= 0)
    t.to_csv(OUT / 'DAY9_LONG_RUN.csv', index=False)
    pd.DataFrame(paths).to_csv(OUT / 'DAY9_PATHS.csv', index=False)
    pd.set_option('display.width', 250)
    print(t.round(3).to_string())
    print(pd.DataFrame(paths).pivot_table(index='outcome', columns='years_after', values='est').round(3))


if __name__ == '__main__':
    main()
