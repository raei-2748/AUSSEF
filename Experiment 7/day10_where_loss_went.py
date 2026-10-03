"""Experiment 7, Day 10: where did the loss go? (PRESPEC_DAY10.md, LOCK_DAY10.txt)
A grants (council), B rents (council quarterly), C business sectors (SA2), D population (SA2).
Run: python3 day10_where_loss_went.py"""
import json
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from scipy.stats import norm, spearmanr

import build_y2 as B
import day2_consequence as C
import day4_blurry as D4
import day7_B_businesses as BB

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
TARGET = 'homes_per_1000_v2_inferred'


# ------------------------------------------------------------ council rows with homes-destroyed dose
def council_rows():
    m, ly = B.load()
    r = C.rows_table(m, C.council_traits())
    m = m.merge(r[['agrn', 'region_id', TARGET]], on=['agrn', 'region_id'], how='left')
    m['dose10'] = m[TARGET] / 10.0              # per 10 homes destroyed per 1,000 dwellings
    return m, ly


def check_A(m):
    y = m.FP_grants_per_capita_change_plus1_excess.to_numpy(float)
    x = m.dose10.to_numpy(float)
    s = D4.slope_boot(y, x, m.region_id.to_numpy())
    bs = m[(m.agrn == '871')].copy()
    bs['homes'] = bs[TARGET] * 0  # placeholder replaced below
    tot = bs.FP_reported_black_summer_grants_total_aud.sum(min_count=1)
    homes = (m[m.agrn == '871'].DL_homes_destroyed_in_council).sum(min_count=1)
    s.update(unit='A$ per resident per 10 homes destroyed per 1,000', expected='up',
             bs_reported_grants_total_aud=float(tot) if pd.notna(tot) else None,
             bs_homes_destroyed_in_rows=float(homes) if pd.notna(homes) else None,
             bs_grants_per_home_aud=float(tot / homes) if pd.notna(tot) and homes else None)
    s['detected'] = bool(s.get('ci_low', -1) > 0)
    return s


def check_B(m, ly):
    groups = B.olg_groups(ly)
    aff, master, _ = B.affected_fys(m)
    bad = aff | master
    r = pd.read_parquet(B.DATASET / 'data/rent/rent_lga_quarter.parquet')
    r['region_id'] = r.region_id.astype(str)
    r = r[r.region_id.isin(set(groups.region_id)) & (r.median_rent > 0)]
    d = pd.DataFrame({'region_id': r.region_id, 'period': pd.PeriodIndex(r.quarter.astype(str), freq='Q'),
                      'y': np.log(r.median_rent.astype(float))}).reset_index(drop=True)
    d['fy'] = [p.year if p.quarter >= 3 else p.year - 1 for p in d.period]
    d['season'] = [p.quarter for p in d.period]
    d['clean'] = ~B.unclean(d, bad)
    c = d[d.clean].reset_index(drop=True)
    fe = B.FE(c, groups, 'group', True)
    loo = {(a, p): v for a, p, v in zip(c.region_id, c.period, fe.loo)}
    obs = {(a, p): (y, se) for a, p, y, se in zip(d.region_id, d.period, d.y, d.season)}

    def resid(a, p):
        if (a, p) in loo:
            return loo[(a, p)]
        if (a, p) in obs:
            y, se = obs[(a, p)]
            pr = fe.predict(a, p, se)
            return y - pr if np.isfinite(pr) else np.nan
        return np.nan

    def window(a, q0, ks):
        v = [resid(a, q0 + k) for k in ks]
        v = [x for x in v if np.isfinite(x)]
        return np.mean(v) if v else np.nan
    ch = np.array([window(a, q, [1, 2, 3, 4]) - window(a, q, [-4, -3, -2, -1]) for a, q in zip(m.region_id, m.q0)]) * 100
    pt = np.array([window(a, q, [-1]) - window(a, q, [-4, -3, -2]) for a, q in zip(m.region_id, m.q0)]) * 100
    s = D4.slope_boot(ch, m.dose10.to_numpy(float), m.region_id.to_numpy())
    p = D4.slope_boot(pt, m.dose10.to_numpy(float), m.region_id.to_numpy())
    s.update(unit='% change in median rent per 10 homes destroyed per 1,000', expected='up',
             pretrend_slope=p.get('slope_per_10pp'), pretrend_lo=p.get('ci_low'), pretrend_hi=p.get('ci_high'),
             rent_quarters=f'{d.period.min()}..{d.period.max()}')
    s['detected'] = bool(s.get('ci_low', -1) > 0 and p.get('ci_low', 1) <= 0 <= p.get('ci_high', -1))
    return s


# ------------------------------------------------------------ SA2 machinery (Day 9 model)
def fit_lags(p, K, scale, primary):
    dose = pd.read_parquet(HERE / 'panels/sa2_fy_dose_homes_in.parquet').set_index(['SA2', 'fy']).dose
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    p = p[p.fy.between(2015, 2024)].merge(info[['SA2', 'SA3', 'GCCSA']], on='SA2', how='inner').dropna(subset=['y'])
    p = p.reset_index(drop=True)
    cols = [f'B{k}' for k in range(K + 1)] + ['F1', 'F2']
    for k in range(K + 1):
        p[f'B{k}'] = [dose.get((s, t - k), 0.0) for s, t in zip(p.SA2, p.fy)]
    p['F1'] = [dose.get((s, t + 1), 0.0) for s, t in zip(p.SA2, p.fy)]
    p['F2'] = [dose.get((s, t + 2), 0.0) for s, t in zip(p.SA2, p.fy)]
    p['gt'] = p.GCCSA.astype(str) + '_' + p.fy.astype(str)

    def sweep(v):
        v = v.astype(float).copy()
        for _ in range(500):
            old = v.copy()
            v = v - v.groupby(p['SA2'].values).transform('mean')
            v = v - v.groupby(p['gt'].values).transform('mean')
            if np.max(np.abs((v - old).to_numpy())) < 1e-10:
                break
        return v
    Xr = p[cols].apply(sweep).to_numpy()
    yr = sweep(p['y']).to_numpy()
    XtX = np.linalg.inv(Xr.T @ Xr)
    beta = XtX @ Xr.T @ yr
    res = yr - Xr @ beta
    meat = np.zeros((len(cols), len(cols)))
    for _, idx in p.groupby(p['SA3'].astype(str)).indices.items():
        g = Xr[idx].T @ res[idx]
        meat += np.outer(g, g)
    G, N, Kp = p['SA3'].nunique(), len(p), len(cols) + p['SA2'].nunique() + p['gt'].nunique()
    V = XtX @ meat @ XtX * G / (G - 1) * (N - 1) / (N - Kp)
    params, cov = pd.Series(beta, index=cols), pd.DataFrame(V, index=cols, columns=cols)

    def comb(names):
        w = pd.Series(0.0, index=cols)
        w[names] = 0.1 / len(names)
        e, se = float(w @ params), float(np.sqrt(w @ cov @ w))
        return e * scale, (e - 1.96 * se) * scale, (e + 1.96 * se) * scale, float(2 * norm.sf(abs(e / se)))
    e, lo, hi, pv = comb(primary)
    pe, pl, ph, _ = comb(['F1', 'F2'])
    path = {f'year_{k}': comb([f'B{k}'])[0] for k in range(K + 1)}
    return dict(rows=int(len(p)), sa2s=int(p['SA2'].nunique()), est=e, lo=lo, hi=hi, p=pv, placebo=pe,
                placebo_lo=pl, placebo_hi=ph, **path)


def industry_panel():
    """SA2 x June counts by industry division, chained like day7_B (link factor of the all-industry total)."""
    tabs = []
    for fname, sheet, june, rel, asgs in BB.SOURCES:
        if BB.USE[june] != rel:
            continue
        path = BB.RAW / fname
        if fname.endswith('.xlsx'):
            rows = list(openpyxl.load_workbook(path, read_only=True)[sheet].iter_rows(values_only=True))
        else:
            rows = BB.to_rows(BB.read_xls(path, sheets={sheet})[sheet])
        hdr = next(i for i, r in enumerate(rows) if r and r[0] == 'Industry' and r[2] == 'SA2')
        d = pd.DataFrame([r[:10] for r in rows[hdr + 2:] if r and r[0] is not None and r[2] is not None],
                         columns=['ind', 'ind_label', 'SA2', 'name', 'ne', 'e1', 'e5', 'e20', 'e200', 'total'])
        d['SA2'] = pd.to_numeric(d.SA2).astype('int64').astype(str)
        d['total'] = pd.to_numeric(d.total, errors='coerce')
        d['ind'] = d.ind.astype(str).str.strip().str[0]
        d['june'] = june
        tabs.append(d[['SA2', 'ind', 'june', 'total']])
    t = pd.concat(tabs, ignore_index=True)
    lf = pd.read_parquet(HERE / 'panels/sa2_businesses.parquet')[['SA2', 'june', 'link_factor']]
    t = t.merge(lf, on=['SA2', 'june'], how='inner')
    t['value'] = t.total * t.link_factor
    return t


def check_C():
    t = industry_panel()
    out = {}
    for code, lab, exp in (('A', 'agriculture', 'down'), ('G', 'retail', 'down'), ('H', 'accommodation_food', 'down'),
                           ('E', 'construction', 'up')):
        p = t[(t.ind == code) & (t.value > 0)].assign(fy=lambda x: x.june - 1, y=lambda x: np.log(x.value))[['SA2', 'fy', 'y']]
        r = fit_lags(p, 5, 100, ['B0', 'B1', 'B2'])
        r.update(expected=exp, unit='% change in business count per 10 pp of homes inside the fire (mean of years 0-2)')
        out[lab] = r
    ps = np.array([v['p'] for v in out.values()])
    order, run, adj = np.argsort(ps), 0, np.empty(len(ps))
    for i, j in enumerate(order):
        run = max(run, (len(ps) - i) * ps[j])
        adj[j] = min(1, run)
    for (k, v), a in zip(out.items(), adj):
        good = v['hi'] < 0 if v['expected'] == 'down' else v['lo'] > 0
        v['p_holm'] = float(a)
        v['detected'] = bool(good and a < 0.05 and v['placebo_lo'] <= 0 <= v['placebo_hi'])
    return out


def check_D():
    d = pd.read_excel(B.DATASET / 'data/raw/sa2/population/32180DS0003_2001-25.xlsx', 'Table 1', header=None)
    years = [int(v) for v in d.iloc[4, 10:] if pd.notna(v)]
    body = d.iloc[6:]
    body = body[pd.to_numeric(body[0], errors='coerce') == 1]
    long = body[[8] + list(range(10, 10 + len(years)))].copy()
    long.columns = ['SA2'] + years
    long['SA2'] = long.SA2.astype('int64').astype(str)
    long = long.melt(id_vars='SA2', var_name='june', value_name='erp')
    long['erp'] = pd.to_numeric(long.erp, errors='coerce')
    long = long[long.erp >= 100]
    p = long.assign(fy=lambda x: x.june.astype(int) - 1, y=lambda x: np.log(x.erp))[['SA2', 'fy', 'y']]
    r = fit_lags(p, 5, 100, ['B1', 'B2', 'B3', 'B4', 'B5'])
    r.update(expected='down', unit='% change in population per 10 pp of homes inside the fire (mean of years 1-5)')
    r['detected'] = bool(r['hi'] < 0 and r['placebo_lo'] <= 0 <= r['placebo_hi'])
    return r


def main():
    m, ly = council_rows()
    res = {'A_grants': check_A(m), 'B_rents': check_B(m, ly), 'C_sectors': check_C(), 'D_population': check_D()}
    json.dump(res, open(OUT / 'DAY10_WHERE_LOSS_WENT.json', 'w'), indent=2, default=float)
    print(json.dumps(res, indent=1, default=lambda v: round(float(v), 3)))


if __name__ == '__main__':
    main()
