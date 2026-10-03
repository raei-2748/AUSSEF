"""Experiment 11: impact clock (PRESPEC.md, LOCK.txt). Channels x horizons, Spearman with fire dose.
Run: python3 run_clock.py      -> results/CLOCK.csv, results/CLOCK_ROWS.csv, results/REBUILD_CURVE.csv
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'Experiment 9'))
import build_v3_indicators as V  # noqa: E402  (council names, master, traffic, statements helpers)

RNG = np.random.default_rng(20261002)
OUT = HERE / 'results'
HM = {'H0': range(0, 4), 'H1': range(4, 13), 'H2': range(13, 25), 'H3': range(25, 49)}   # months after m0
HY = {'H0': 0, 'H1': 1, 'H2': 2, 'H3': 3}                                                # FY offsets
PRIMARY = {'C1_traffic': ('H0', -1), 'C2_rent': ('H2', 1), 'C3_dv': ('H2', 1), 'C4_grants_pc': ('H1', 1),
           'C5_fire_grant_share': ('H1', 1)}


def rows():
    m = V.master()
    T = pd.read_csv(ROOT / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
    m = m.merge(T[['agrn', 'region_id', 'log_homes_in_fire_per_1000', 'log_share']], on=['agrn', 'region_id'], how='left',
                validate='1:1')
    return m


def with_excess(m, own_fn, comp_ids_fn):
    """own_fn(region_id, row) -> value or nan; excess = own - median over comparison ids."""
    out, cache = [], {}
    for r in m.itertuples():
        own = own_fn(r.region_id, r)
        if pd.isna(own):
            out.append(np.nan); continue
        key = (r.F, r.m0)
        if key not in cache:
            c = [own_fn(cid, r) for cid in comp_ids_fn(r)]
            c = [x for x in c if pd.notna(x)]
            cache[key] = np.median(c) if c else np.nan
        out.append(own - cache[key])
    return pd.Series(out, index=m.index)


def unburned_fn(m):
    allc = set(V.councils().region_id)
    by_F = m.groupby('F').region_id.apply(set).to_dict()
    return lambda r: sorted(allc - by_F[r.F])


# ------------------------------------------------------------------ C1 traffic
def c1(m):
    d = V.traffic_monthly()
    c = V.councils()
    d['region_id'] = d.lga.map(V.norm).map(c.set_index('key').region_id)
    d = d.dropna(subset=['region_id', 'vol'])
    d['month'] = pd.to_datetime(d.day).dt.to_period('M')
    g = d.groupby(['station_key', 'month']).agg(vol=('vol', 'mean'), n=('vol', 'size')).reset_index()
    g['ok'] = g.n >= 0.5 * g.month.map(lambda p: p.days_in_month)
    g = g[g.ok]
    S = g.pivot(index='month', columns='station_key', values='vol')
    reg = d.drop_duplicates('station_key').set_index('station_key').region_id
    stations = {k: list(v.index) for k, v in reg.groupby(reg)}
    out = {}
    for h, mm in HM.items():
        cache = {}

        def own(cid, r, mm=mm, cache=cache):
            key = (cid, r.m0)
            if key in cache:
                return cache[key]
            W = [r.m0 + k for k in mm]
            B = [p - 12 for p in W] + [p - 24 for p in W]
            vals = []
            for s in stations.get(cid, []):
                if s not in S:
                    continue
                w, b = S[s].reindex(W), S[s].reindex(B)
                if w.notna().sum() >= 0.5 * len(W) and b.notna().sum() >= 0.5 * len(B) and w.mean() > 0 and b.mean() > 0:
                    vals.append(np.log(w.mean() / b.mean()))
            cache[key] = np.median(vals) if vals else np.nan
            return cache[key]
        out[h] = with_excess(m, own, unburned_fn(m))
    return out


# ------------------------------------------------------------------ C2 rents (quarterly)
def c2(m):
    r = pd.read_parquet(ROOT / 'fire_event_dataset/data/rent/rent_lga_quarter.parquet')
    r['q'] = pd.PeriodIndex(r.quarter.astype(str), freq='Q')
    r['region_id'] = r.region_id.astype(str)
    R = np.log(r.pivot_table(index='q', columns='region_id', values='median_rent', aggfunc='mean'))
    QH = {'H0': range(0, 2), 'H1': range(2, 5), 'H2': range(5, 9), 'H3': range(9, 17)}
    out = {}
    for h, qq in QH.items():
        def own(cid, row, qq=qq):
            if cid not in R:
                return np.nan
            q0 = row.m0.asfreq('Q')
            post = R[cid].reindex([q0 + k for k in qq]); pre = R[cid].reindex([q0 - k for k in range(1, 5)])
            return post.mean() - pre.mean() if post.notna().any() and pre.notna().sum() >= 2 else np.nan
        out[h] = with_excess(m, own, unburned_fn(m))
    return out


# ------------------------------------------------------------------ C3 domestic violence (monthly)
def dv_table():
    import openpyxl
    wb = openpyxl.load_workbook(V.RAW / 'bocsar/RCI_offencebymonth.xlsm', read_only=True)
    it = wb['Data'].iter_rows(values_only=True)
    hdr = next(it)
    months = [pd.Period(x, 'M') for x in hdr[3:]]
    data = {r[0]: r[3:] for r in it if r[2] == 'Domestic violence related assault'}
    df = pd.DataFrame(data, index=months).apply(pd.to_numeric, errors='coerce')
    c = V.councils().set_index('key').region_id
    df.columns = [c.get(V.norm(x)) for x in df.columns]
    df = df.loc[:, pd.Series(df.columns).notna().to_numpy()]
    return df.T.groupby(level=0).sum().T


def c3(m):
    D = dv_table()
    last = D.index.max()
    out = {}
    for h, mm in HM.items():
        def own(cid, r, mm=mm):
            if cid not in D:
                return np.nan
            post = D[cid].reindex([r.m0 + k for k in mm if r.m0 + k <= last])
            pre = D[cid].reindex([r.m0 - k for k in range(1, 25)])
            if post.notna().sum() < max(2, 0.5 * len(mm)) or pre.notna().sum() < 12 or post.mean() <= 0 or pre.mean() <= 0:
                return np.nan
            return np.log(post.mean() / pre.mean())
        out[h] = with_excess(m, own, unburned_fn(m))
    return out


# ------------------------------------------------------------------ C4 grants per resident (OLG, FY)
def c4(m):
    o = pd.read_parquet(ROOT / 'fire_event_dataset/data/olg/olg_long.parquet')
    w = o.pivot_table(index=['council_name_norm', 'fy_start'], columns='metric', values='value', aggfunc='first').reset_index()
    w['gpc'] = w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population
    c = V.councils()
    w['region_id'] = w.council_name_norm.map(V.norm).map(c.set_index('key').region_id)
    w = w.dropna(subset=['region_id'])
    G = np.log(w[w.gpc > 0].pivot_table(index='fy_start', columns='region_id', values='gpc', aggfunc='mean'))
    out = {}
    for h, k in HY.items():
        def own(cid, r, k=k):
            if cid not in G:
                return np.nan
            post = G[cid].get(r.F + k, np.nan); pre = G[cid].reindex([r.F - 2, r.F - 1])
            return post - pre.mean() if pd.notna(post) and pre.notna().any() else np.nan
        out[h] = with_excess(m, own, unburned_fn(m))
    return out, int(G.shape[1])


# ------------------------------------------------------------------ C5 / C6 statements (FY)
def c56(m):
    fs = V.statement_shares(V.E10 / 'A_fire_councils/statements_tidy.csv', ['disaster_grant_operating', 'disaster_grant_capital'])
    cs = V.statement_shares(V.E10 / 'A_comparison_councils/statements_tidy.csv',
                            ['disaster_grant_operating', 'disaster_grant_capital', 'bushfire_emergency_services_grant'])
    has = set(fs[fs.fire.notna()].index.get_level_values(0))
    fs.loc[~fs.index.get_level_values(0).isin(has), 'fire_share'] = np.nan
    comp = list(cs.index.get_level_values(0).unique())
    res = {}
    for col, name in (('fire_share', 'C5_fire_grant_share'), ('cap_share', 'C6_capex_share')):
        res[name] = {}
        for h, k in HY.items():
            def val(s, cid, y):
                try:
                    return s.loc[(cid, y), col]
                except KeyError:
                    return np.nan

            def change(s, cid, F, k=k):
                post = val(s, cid, F + k); pre = [val(s, cid, F - 2), val(s, cid, F - 1)]
                pre = [x for x in pre if pd.notna(x)]
                return post - np.mean(pre) if pd.notna(post) and pre else np.nan
            ex = []
            for r in m.itertuples():
                own = change(fs, r.region_id, r.F)
                cc = [change(cs, c, r.F) for c in comp]; cc = [x for x in cc if pd.notna(x)]
                ex.append(own - np.median(cc) if pd.notna(own) and cc else np.nan)
            res[name][h] = pd.Series(ex, index=m.index)
    return res


# ------------------------------------------------------------------ C7 rebuild curve (descriptive)
def c7(m):
    fr = []
    for f in sorted((V.RAW / 'abs_building_approvals').glob('BA_LGA20*.csv')):
        d = pd.read_csv(f, dtype=str)
        if 'REGION_TYPE' in d:
            fr.append(d[d.REGION_TYPE.str.startswith('LGA') & d.REGION.str.startswith('1')][['REGION', 'TIME_PERIOD', 'OBS_VALUE']])
    d = pd.concat(fr)
    d['month'] = pd.PeriodIndex(d.TIME_PERIOD, freq='M'); d['v'] = pd.to_numeric(d.OBS_VALUE, errors='coerce')
    ba = d.pivot_table(index='month', columns='REGION', values='v', aggfunc='last')
    dl = pd.read_csv(ROOT / 'Experiment 6/followups/dl_fill/DL_FILLED.csv', dtype={'agrn': str, 'region_id': str})
    hm = m[['agrn', 'region_id']].merge(dl, on=['agrn', 'region_id'], how='left')
    homes = (hm.homes_per_1000_v2_inferred * hm.dwellings / 1000).to_numpy()
    out = []
    for i, r in enumerate(m.itertuples()):
        if not homes[i] >= 5 or r.region_id not in ba or r.m0 < pd.Period('2019-07', 'M'):
            continue
        col = ba[r.region_id]; base = col.reindex([r.m0 - k for k in range(1, 13)]).mean()
        for H in (6, 12, 24, 36, 48):
            post = col.reindex([r.m0 + k for k in range(1, H + 1)])
            if post.notna().sum() == H:
                out.append(dict(agrn=r.agrn, region_id=r.region_id, region_name=r.region_name, F=r.F, homes=homes[i],
                                months=H, extra_per_home=(post.sum() - H * base) / homes[i]))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ stats
def stats(x, y, groups, season, n_boot=2000, n_perm=2000):
    ok = x.notna() & y.notna()
    x, y, groups, season = x[ok].to_numpy(), y[ok].to_numpy(), groups[ok].to_numpy(), season[ok].to_numpy()
    n = len(x)
    if n < 10 or np.std(x) == 0:
        return dict(n=n, rho=np.nan, lo=np.nan, hi=np.nan, p_perm=np.nan, n_dosed=int((x > 0).sum()))
    rho = spearmanr(x, y)[0]
    ug = np.unique(groups); idx = {g: np.where(groups == g)[0] for g in ug}
    bs = []
    for _ in range(n_boot):
        s = np.concatenate([idx[g] for g in RNG.choice(ug, len(ug))])
        if np.std(x[s]) > 0 and np.std(y[s]) > 0:
            bs.append(spearmanr(x[s], y[s])[0])
    perm = []
    seas = {s: np.where(season == s)[0] for s in np.unique(season)}
    for _ in range(n_perm):
        xp = x.copy()
        for s, ii in seas.items():
            xp[ii] = RNG.permutation(x[ii])
        perm.append(spearmanr(xp, y)[0])
    perm = np.array(perm)
    p = (1 + (np.abs(perm) >= abs(rho)).sum()) / (1 + n_perm)
    return dict(n=n, rho=rho, lo=np.nanpercentile(bs, 2.5), hi=np.nanpercentile(bs, 97.5), p_perm=p, n_dosed=int((x > 0).sum()))


def main():
    m = rows()
    ch = {}
    ch['C1_traffic'] = c1(m)
    ch['C2_rent'] = c2(m)
    ch['C3_dv'] = c3(m)
    ch['C4_grants_pc'], n_olg = c4(m)
    ch.update(c56(m))
    R = m[['agrn', 'region_id', 'region_name', 'F', 'log_homes_in_fire_per_1000', 'log_share']].copy()
    res = []
    for c, hs in ch.items():
        for h, s in hs.items():
            R[f'{c}_{h}'] = s
            for label, sub in (('all', m.index), ('no_black_summer', m.index[m.F != 2019])):
                st = stats(m.log_homes_in_fire_per_1000.loc[sub], s.loc[sub], m.region_id.loc[sub], m.F.loc[sub])
                res.append(dict(channel=c, horizon=h, sample=label, dose='homes_in_fire', **st))
            if c in ('C1_traffic', 'C3_dv'):
                st = stats(m.log_share, s, m.region_id, m.F)
                res.append(dict(channel=c, horizon=h, sample='all', dose='log_share', **st))
    C = pd.DataFrame(res)
    C['expected_sign'] = C.channel.map({k: v[1] for k, v in PRIMARY.items()})
    C['primary'] = [(c in PRIMARY and PRIMARY[c][0] == h and s == 'all' and d == 'homes_in_fire')
                    for c, h, s, d in zip(C.channel, C.horizon, C['sample'], C.dose)]
    P = C[C.primary].sort_values('p_perm')
    k = len(P); holm = []
    run = 0
    for i, p in enumerate(P.p_perm):
        run = max(run, min(1, (k - i) * p)); holm.append(run)
    C.loc[P.index, 'p_holm'] = holm
    C['detected'] = C.primary & (C.p_holm < 0.05) & (np.sign(C.rho) == C.expected_sign)
    C.to_csv(OUT / 'CLOCK.csv', index=False)
    R.to_csv(OUT / 'CLOCK_ROWS.csv', index=False)
    rb = c7(m); rb.to_csv(OUT / 'REBUILD_CURVE.csv', index=False)
    print(C[C['sample'].eq('all') & C.dose.eq('homes_in_fire')][['channel', 'horizon', 'n', 'n_dosed', 'rho', 'lo', 'hi', 'p_perm', 'primary', 'p_holm', 'detected']].round(3).to_string(index=False))
    print('\nno Black Summer:'); print(C[C['sample'].eq('no_black_summer')][['channel', 'horizon', 'n', 'rho', 'lo', 'hi', 'p_perm']].round(3).to_string(index=False))
    print('\nrebuild curve (median extra approvals per home destroyed):'); print(rb.groupby('months').extra_per_home.describe()[['count', '50%', 'mean']].round(2))
    json.dump({'olg_councils': n_olg}, open(OUT / 'RUN_INFO.json', 'w'))


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    main()
