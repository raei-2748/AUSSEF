"""Experiment 16, Part 2 (PRESPEC.md, LOCK.txt): do workplaces near/inside the fire link to local jobs and earnings
better than homes near/inside the fire? SA2 x financial-year panel, Experiment 7 Day 9 set-up.
Run: ./run.sh employment_test.py"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/ray/Research/AUSSEF - Local')
P7 = ROOT / 'Experiment 7/panels'
RES = HERE / 'results'
PIA = Path('/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw')
BLOCKS = {'earners': 2, 'median_age': 7, 'sum': 12, 'median': 17, 'mean': 22}


# ------------------------------------------------------------------ outcome panels (copied from Experiment 7 Day 5/9)
def read_pia(path):
    d = pd.read_excel(path, 'Table 1.4', header=None)
    years = [str(v) for v in d.iloc[6, 2:7]]
    body = d.iloc[7:]
    body = body[body[0].astype(str).str.fullmatch(r'1\d{8}')]
    out = []
    for k, y in enumerate(years):
        rec = pd.DataFrame({'SA2': body[0].astype(str).values, 'name': body[1].astype(str).values, 'fy': int(y[:4])})
        for name, c in BLOCKS.items():
            rec[name] = pd.to_numeric(body[c + k].astype(str).str.replace(',', ''), errors='coerce').values
        out.append(rec)
    return pd.concat(out, ignore_index=True)


def pia_panel():
    new = read_pia(PIA / 'pia_2024.xlsx')                       # 2017-18..2021-22, ASGS 2021
    old = read_pia(PIA / 'project_inputs/pia_old_total.xlsx')   # 2015-16..2019-20, ASGS 2016
    same = set(new[['SA2', 'name']].drop_duplicates().itertuples(index=False, name=None)) & \
        set(old[['SA2', 'name']].drop_duplicates().itertuples(index=False, name=None))
    keep = {s for s, _ in same}
    link = new[new.fy == 2017].set_index('SA2')[['earners', 'sum']].div(
        old[old.fy == 2017].set_index('SA2')[['earners', 'sum']])
    early = old[old.fy.isin([2015, 2016]) & old.SA2.isin(keep)].copy()
    for c in ('earners', 'sum'):
        early[c] = early[c] * early.SA2.map(link[c])
    return pd.concat([early, new], ignore_index=True)


def fy_of_period(p):
    p = pd.Period(p, 'Q')
    return p.year if p.quarter >= 3 else p.year - 1


def panels():
    info = pd.read_parquet(P7 / 'sa2_info.parquet')
    u = pd.read_parquet(P7 / 'sa2_unemployment.parquet')
    u = u[u.in_sa2_info].assign(fy=lambda t: t.period.map(fy_of_period))
    u = u.groupby(['SA2', 'fy']).value.mean().rename('y').reset_index()
    b = pd.read_parquet(P7 / 'sa2_businesses.parquet')
    b = b[b.in_sa2_info & (b.value > 0)].assign(fy=lambda t: t.june - 1, y=lambda t: np.log(t.value))[['SA2', 'fy', 'y']]
    inc = pia_panel().merge(info[['SA2', 'pop']], on='SA2')
    inc = inc[(inc['pop'] >= 100) & (inc['sum'] > 0) & (inc.earners > 0)]
    e = inc.assign(y=np.log(inc.earners))[['SA2', 'fy', 'y']]
    i = inc.assign(y=np.log(inc['sum']))[['SA2', 'fy', 'y']]
    # name: (panel, worse direction, K lags, first FY, last FY, unit)
    return {'U_unemployment_rate': (u, 'up', 4, 2015, 2024, 'percentage points'),
            'E_log_income_earners': (e, 'down', 2, 2015, 2021, '%'),
            'I_log_total_income': (i, 'down', 2, 2015, 2021, '%'),
            'B_log_businesses': (b, 'down', 4, 2015, 2024, '%')}, info


# ------------------------------------------------------------------ estimation
def fit(p, xcols):
    """OLS after sweeping out SA2 and GCCSA x FY effects; SA3-clustered covariance (Day 9 code)."""
    def sweep(v):
        v = v.copy()
        for _ in range(500):
            old = v.copy()
            v = v - v.groupby(p.SA2.values).transform('mean')
            v = v - v.groupby(p['gt'].values).transform('mean')
            if np.max(np.abs((v - old).to_numpy())) < 1e-10:
                break
        return v
    X = p[xcols].astype(float).apply(sweep)
    y = sweep(p['y'].astype(float))
    Xa, ya = X.to_numpy(), y.to_numpy()
    XtX_inv = np.linalg.pinv(Xa.T @ Xa)
    beta = XtX_inv @ Xa.T @ ya
    resid = ya - Xa @ beta
    meat = np.zeros((len(xcols), len(xcols)))
    for _, idx in p.groupby(p.SA3.astype(str)).indices.items():
        sg = Xa[idx].T @ resid[idx]
        meat += np.outer(sg, sg)
    G, N, Kp = p.SA3.nunique(), len(p), len(xcols) + p.SA2.nunique() + p['gt'].nunique()
    V = XtX_inv @ meat @ XtX_inv * G / (G - 1) * (N - 1) / (N - Kp)
    r2_within = 1 - (resid @ resid) / (ya @ ya)
    return pd.Series(beta, index=xcols), pd.DataFrame(V, index=xcols, columns=xcols), float(r2_within)


def comb(b, V, weights, scale):
    w = pd.Series(0.0, index=b.index)
    for k, v in weights.items():
        w[k] = v
    e, se = float(w @ b), float(np.sqrt(max(w @ V @ w, 0)))
    z = e / se if se > 0 else 0.0
    return e * scale, (e - 1.96 * se) * scale, (e + 1.96 * se) * scale, float(2 * norm.sf(abs(z)))


def design(p, dose, X, K):
    cols = []
    for k in range(K + 1):
        p[f'{X}_L{k}'] = [dose.get((s, t - k), 0.0) for s, t in zip(p.SA2, p.fy)]
        cols.append(f'{X}_L{k}')
    for k in (1, 2):
        p[f'{X}_F{k}'] = [dose.get((s, t + k), 0.0) for s, t in zip(p.SA2, p.fy)]
        cols.append(f'{X}_F{k}')
    return cols


def effects(b, V, X, scale):
    """effect = mean beta_0..2 per 10 pp; placebo = mean of the two leads per 10 pp."""
    eff = comb(b, V, {f'{X}_L{k}': 0.1 / 3 for k in range(3)}, scale)
    pla = comb(b, V, {f'{X}_F1': 0.05, f'{X}_F2': 0.05}, scale)
    return eff, pla


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj, run = np.empty(len(p)), 0.0
    for i, j in enumerate(order):
        run = max(run, (len(p) - i) * p[j])
        adj[j] = min(1.0, run)
    return adj


def main():
    expo = pd.read_parquet(HERE / 'data/sa2_fy_exposure.parquet')
    pans, info = panels()
    single, joint, extra = [], [], {}
    for name, (p0, worse, K, f0, f1, unit) in pans.items():
        sgn = 1 if worse == 'up' else -1
        scale = 1 if unit == 'percentage points' else 100
        p0 = p0[p0.fy.between(f0, f1)].merge(info[['SA2', 'SA3', 'GCCSA']], on='SA2', how='inner').dropna(subset=['y'])
        p0['gt'] = p0.GCCSA.astype(str) + '_' + p0.fy.astype(str)
        for zone, sfx in (('1 km (primary)', '_1km'), ('inside (secondary)', '')):
            doses = {X: expo.set_index(['SA2', 'fy'])[X + sfx] for X in ['H', 'W', 'W_osm', 'F', 'P', 'A']}
            # ---- single-exposure models
            for X in ['H', 'W', 'W_osm', 'F', 'P']:
                p = p0.copy()
                cols = design(p, doses[X], X, K)
                b, V, r2 = fit(p, cols)
                (e, lo, hi, pv), (pe, pl, ph, _) = effects(b, V, X, scale)
                single.append(dict(outcome=name, zone=zone, exposure=X + sfx, worse=worse, unit=unit, rows=len(p),
                                   sa2s=p.SA2.nunique(), years=f'{p.fy.min()}-{p.fy.max()}',
                                   effect=e, lo=lo, hi=hi, p=pv, placebo=pe, placebo_lo=pl, placebo_hi=ph,
                                   r2_within=r2,
                                   exposed_sa2_years_ge10pct=int((p[f'{X}_L0'] >= 0.1).sum())))
            # ---- joint models: homes + workplaces
            for Wx in ['W', 'W_osm']:
                p = p0.copy()
                cols = design(p, doses['H'], 'H', K) + design(p, doses[Wx], Wx, K)
                b, V, r2 = fit(p, cols)
                (eh, lh, hh, _), (ph_, plh, phh, _) = effects(b, V, 'H', scale)
                (ew, lw, hw, _), (pw, plw, phw, _) = effects(b, V, Wx, scale)
                wts = {f'{Wx}_L{k}': sgn * 0.1 / 3 for k in range(3)}
                wts.update({f'H_L{k}': -sgn * 0.1 / 3 for k in range(3)})
                D, Dlo, Dhi, Dp = comb(b, V, wts, scale)
                joint.append(dict(outcome=name, zone=zone, workplace=Wx + sfx, worse=worse, unit=unit, rows=len(p),
                                  home_effect=eh, home_lo=lh, home_hi=hh, home_placebo_lo=plh, home_placebo_hi=phh,
                                  work_effect=ew, work_lo=lw, work_hi=hw, work_placebo_lo=plw,
                                  work_placebo_hi=phw, D_work_minus_home_worse=D, D_lo=Dlo, D_hi=Dhi, D_p=Dp,
                                  r2_within=r2))
    s, j = pd.DataFrame(single), pd.DataFrame(joint)
    prim = j.zone.str.startswith('1 km')
    j['D_p_holm'] = np.nan
    j.loc[prim, 'D_p_holm'] = holm(j.loc[prim, 'D_p'])

    def worse_ci(lo, hi, worse):
        return lo > 0 if worse == 'up' else hi < 0

    def verdict(r):
        if not r.zone.startswith('1 km'):
            return 'reported (secondary, no verdict)'
        wp = r.work_placebo_lo <= 0 <= r.work_placebo_hi
        hp = r.home_placebo_lo <= 0 <= r.home_placebo_hi
        if r.D_p_holm < 0.05 and r.D_work_minus_home_worse > 0 and worse_ci(r.work_lo, r.work_hi, r.worse) and wp:
            return 'Workplace exposure links better'
        if r.D_p_holm < 0.05 and r.D_work_minus_home_worse < 0 and worse_ci(r.home_lo, r.home_hi, r.worse) and hp:
            return 'Home exposure links better'
        return 'Cannot tell apart'
    j['verdict'] = j.apply(verdict, axis=1)
    s.to_csv(RES / 'EMPLOYMENT_SINGLE.csv', index=False)
    j.to_csv(RES / 'EMPLOYMENT_JOINT.csv', index=False)
    pd.set_option('display.width', 250)
    print(s.round(3).to_string())
    print(j.round(3).to_string())


if __name__ == '__main__':
    main()
