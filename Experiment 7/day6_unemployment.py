"""Experiment 7, Day 6: council unemployment (SALM, quarterly) vs residents affected (PRESPEC_DAY6.md, LOCK_DAY6.txt).
Run: python3 day6_unemployment.py"""
import json
import numpy as np
import pandas as pd

import build_y2 as B
import day4_blurry as D4

Q = {'Mar': 1, 'Jun': 2, 'Sep': 3, 'Dec': 4}


def salm():
    """Same parsing as fire_event_dataset/src/economy.salm (copied to avoid its geopandas import)."""
    d = pd.read_csv(B.DATASET / 'data/salm/salm_lga.csv', skiprows=2, dtype=str).dropna(subset=['LGA Code (2025 ASGS)'])
    d = d.rename(columns={'Data Item': 'item', 'LGA Code (2025 ASGS)': 'region_id'}).drop(columns=d.columns[1])
    long = d.melt(id_vars=['item', 'region_id'], var_name='q', value_name='v')
    long['v'] = pd.to_numeric(long.v.str.replace(',', ''), errors='coerce')
    mon, yy = long.q.str[:3], long.q.str[-2:]
    long['period'] = pd.PeriodIndex(year=2000 + yy.astype(int), quarter=mon.map(Q), freq='Q')
    w = long.pivot_table(index=['region_id', 'period'], columns='item', values='v', aggfunc='first')
    return w.rename(columns={'Smoothed unemployment rate (%)': 'unemployment_rate'})

OUT = B.OUT


def main():
    m, ly = B.load()
    groups = B.olg_groups(ly)
    aff, master, _ = B.affected_fys(m)
    bad = aff | master
    s = salm().reset_index()
    s['region_id'] = s.region_id.astype(str)
    s = s[s.region_id.isin(set(groups.region_id))].dropna(subset=['unemployment_rate'])
    d = pd.DataFrame({'region_id': s.region_id, 'period': s.period, 'y': s.unemployment_rate})
    d['fy'] = [p.year if p.quarter >= 3 else p.year - 1 for p in d.period]
    d['season'] = [p.quarter for p in d.period]
    d = d.reset_index(drop=True)
    d['clean'] = ~B.unclean(d, bad)
    c = d[d.clean].reset_index(drop=True)
    fe = B.FE(c, groups, 'group', True)
    loo = {(r, p): v for r, p, v in zip(c.region_id, c.period, fe.loo)}
    obs = {(r, p): (y, se) for r, p, y, se in zip(d.region_id, d.period, d.y, d.season)}

    def resid(r, p):
        if (r, p) in loo:
            return loo[(r, p)]
        if (r, p) in obs:
            y, se = obs[(r, p)]
            pr = fe.predict(r, p, se)
            return y - pr if np.isfinite(pr) else np.nan
        return np.nan
    after, before, late, early = [1, 2, 3, 4], [-4, -3, -2, -1], [-1], [-4, -3, -2]

    def change(r, b, fn, strict=False):
        vals = [[fn(r, b + k) for k in ks] for ks in (after, before, late, early)]
        if strict and not all(np.isfinite(sum(vals, []))):
            return np.nan, np.nan
        a, p, l, e = [[x for x in v if np.isfinite(x)] for v in vals]
        return (np.mean(a) - np.mean(p) if a and p else np.nan), (np.mean(l) - np.mean(e) if l and e else np.nan)
    lfn = lambda r, p: loo.get((r, p), np.nan)  # noqa: E731
    nul = [change(r, p, lfn, True) for (r, p) in loo]
    nch = np.array([x[0] for x in nul if np.isfinite(x[0])])
    npt = np.array([x[1] for x in nul if np.isfinite(x[0])])
    ch = np.array([change(r, q0, resid)[0] for r, q0 in zip(m.region_id, m.q0)])
    pt = np.array([change(r, q0, resid)[1] for r, q0 in zip(m.region_id, m.q0)])
    ap = pd.read_parquet(B.DATASET / 'data/enrich/affected_pop_event_council.parquet')
    ap['agrn'], ap['region_id'] = ap.agrn.astype(str), ap.region_id.astype(str)
    m = m.merge(ap[['agrn', 'region_id', 'pop_within_1km']], on=['agrn', 'region_id'], how='left')
    pop = ly.set_index(['region_id', 'year']).population
    m['dose'] = m.pop_within_1km / [pop.get((r, F), np.nan) for r, F in zip(m.region_id, m.F)]
    g = m.region_id.to_numpy()
    res = dict(null_n=int(len(nch)), sd_change_pp=float(nch.std(ddof=1)))
    z, zp = ch / nch.std(ddof=1), pt / npt.std(ddof=1)
    for lab, y, x, sel in (('main', z, m.dose * 10, None), ('pretrend', zp, m.dose * 10, None),
                           ('area_share', z, m.share * 10, None), ('pp_main', ch, m.dose * 10, None),
                           ('excl_black_summer', z, m.dose * 10, (m.agrn != '871').to_numpy())):
        xs, ys, gs = x.to_numpy(), y, g
        if sel is not None:
            xs, ys, gs = xs[sel], ys[sel], gs[sel]
        res[lab] = D4.slope_boot(ys, xs, gs)
    big = (m.dose >= 0.05).to_numpy()
    res['mean_change_pp_dose_ge5pct'] = [float(np.nanmean(ch[big])), int(np.isfinite(ch[big]).sum())]
    res['mean_change_pp_dose_lt1pct'] = [float(np.nanmean(ch[m.dose.to_numpy() < .01])), int(np.isfinite(ch[m.dose.to_numpy() < .01]).sum())]
    mn, pr = res['main'], res['pretrend']
    res['verdict'] = 'Detected' if mn['ci_low'] > 0 and pr['ci_low'] <= 0 <= pr['ci_high'] else 'Not detected'
    json.dump(res, open(OUT / 'DAY6_UNEMPLOYMENT.json', 'w'), indent=2)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
