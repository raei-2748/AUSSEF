"""Experiment 12: spillover to neighbours (Part A), far-only comparison (Part B), per-home bounds (Part C).
Rules: PRESPEC.md (LOCK.txt). Run: python3 run_spillover.py (after adjacency.py)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'Experiment 11'))
import run_clock as RC  # noqa: E402  (master rows, BOCSAR table, council names)

RNG = np.random.default_rng(20261002)
OUT = HERE / 'results'

m = RC.rows()
T = pd.read_csv(ROOT / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
m = m.merge(T[['agrn', 'region_id', 'homes_v2', 'dwellings']], on=['agrn', 'region_id'], how='left', validate='1:1')
adj = pd.read_csv(OUT / 'ADJACENCY.csv', dtype=str)
NB = adj.groupby('region_id').neighbour_id.apply(set).to_dict()
ALL = set(RC.V.councils().region_id)

# ---------------------------------------------------------------- monthly / quarterly series
r = pd.read_parquet(ROOT / 'fire_event_dataset/data/rent/rent_lga_quarter.parquet')
r['q'] = pd.PeriodIndex(r.quarter.astype(str), freq='Q'); r['region_id'] = r.region_id.astype(str)
RENT = np.log(r.pivot_table(index='q', columns='region_id', values='median_rent', aggfunc='mean'))
DV = RC.dv_table()
s = pd.read_parquet(ROOT / 'Experiment 7/panels/dss_quarter.parquet')
s['q'] = pd.PeriodIndex(s.quarter.astype(str), freq='Q'); s['region_id'] = s.region_id.astype(str)
SUP = s.pivot_table(index='q', columns='region_id', values='income_support_total', aggfunc='sum')


def rent_change(cid, m0):
    if cid not in RENT:
        return np.nan
    q0 = m0.asfreq('Q')
    post, pre = RENT[cid].reindex([q0 + k for k in range(5, 9)]), RENT[cid].reindex([q0 - k for k in range(1, 5)])
    return post.mean() - pre.mean() if post.notna().any() and pre.notna().sum() >= 2 else np.nan


def dv_change(cid, m0, level=False):
    if cid not in DV:
        return np.nan
    post = DV[cid].reindex([m0 + k for k in range(13, 25) if m0 + k <= DV.index.max()])
    pre = DV[cid].reindex([m0 - k for k in range(1, 25)])
    if post.notna().sum() < 6 or pre.notna().sum() < 12 or post.mean() <= 0 or pre.mean() <= 0:
        return np.nan
    return (post.mean() - pre.mean()) * 12 if level else np.log(post.mean() / pre.mean())


def sup_change(cid, m0, level=False):
    if cid not in SUP:
        return np.nan
    q0 = m0.asfreq('Q')
    qs = sorted({(m0 + k).asfreq('Q') for k in range(4, 13)})
    post, pre = SUP[cid].reindex(qs), SUP[cid].reindex([q0 - k for k in range(1, 5)])
    if post.notna().sum() < 2 or pre.notna().sum() < 3 or post.mean() <= 0 or pre.mean() <= 0:
        return np.nan
    return post.mean() - pre.mean() if level else np.log(post.mean() / pre.mean())


OUTC = {'rent': rent_change, 'dv': dv_change, 'income_support': sup_change}

# ---------------------------------------------------------------- Part A: neighbours vs far
units = []
for F, g in m.groupby('F'):
    heavy = g[g.homes_v2 >= 5]
    if heavy.empty:
        continue
    burned = set(g.region_id)
    near_any = set().union(*[NB.get(c, set()) for c in burned])
    far = sorted(ALL - burned - near_any)
    for c in sorted(ALL - burned):
        hn = heavy[heavy.region_id.isin(NB.get(c, set()))]
        if hn.empty:
            continue
        top = hn.sort_values('homes_v2').iloc[-1]
        units.append(dict(F=F, region_id=c, exposure=np.log1p(hn.homes_v2.sum()), homes_next_door=hn.homes_v2.sum(),
                          m0=top.m0, far=far))
U = pd.DataFrame(units)
for k, fn in OUTC.items():
    vals = []
    for u in U.itertuples():
        own = fn(u.region_id, u.m0)
        comp = [fn(c, u.m0) for c in u.far]; comp = [x for x in comp if pd.notna(x)]
        vals.append(own - np.median(comp) if pd.notna(own) and comp else np.nan)
    U[k] = vals


def cluster_mean(x, groups, n=2000):
    ok = x.notna(); x, groups = x[ok].to_numpy(), groups[ok].to_numpy()
    ug = np.unique(groups); idx = {gg: np.where(groups == gg)[0] for gg in ug}
    bs = [x[np.concatenate([idx[gg] for gg in RNG.choice(ug, len(ug))])].mean() for _ in range(n)]
    flips = [(x * RNG.choice([-1, 1], len(x))).mean() for _ in range(n)]
    p = (1 + (np.abs(flips) >= abs(x.mean())).sum()) / (1 + n)
    return len(x), len(ug), x.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), p


res = []
for k in OUTC:
    n, nc, mean, lo, hi, p = cluster_mean(U[k], U.region_id)
    d = U[[k, 'exposure']].dropna()
    rho = spearmanr(d[k], d.exposure)[0] if len(d) > 5 else np.nan
    res.append(dict(part='A', outcome=k, n_units=n, n_councils=nc, mean_excess=mean, lo=lo, hi=hi, p_signflip=p,
                    rho_with_exposure=rho))
A = pd.DataFrame(res).sort_values('p_signflip')
run, holm = 0, []
for i, p in enumerate(A.p_signflip):
    run = max(run, min(1, (len(A) - i) * p)); holm.append(run)
A['p_holm'] = holm
A['detected'] = (A.p_holm < 0.05) & (A.mean_excess > 0)

# ---------------------------------------------------------------- Part B: far-only comparison for burned rows
burned_by_F = m.groupby('F').region_id.apply(set).to_dict()
B = []
for k, fn, ref in (('rent', rent_change, 'C2_rent_H2'), ('dv', dv_change, 'C3_dv_H2')):
    vals = []
    for row in m.itertuples():
        burned = burned_by_F[row.F]
        near_any = set().union(*[NB.get(c, set()) for c in burned])
        far = sorted(ALL - burned - near_any)
        own = fn(row.region_id, row.m0)
        comp = [fn(c, row.m0) for c in far]; comp = [x for x in comp if pd.notna(x)]
        vals.append(own - np.median(comp) if pd.notna(own) and comp else np.nan)
    v = pd.Series(vals, index=m.index)
    d = pd.DataFrame({'v': v, 'dose': m.log_homes_in_fire_per_1000}).dropna()
    clock = pd.read_csv(ROOT / 'Experiment 11/results/CLOCK.csv')
    c = clock[(clock.channel == ('C2_rent' if k == 'rent' else 'C3_dv')) & (clock.horizon == 'H2') &
              (clock['sample'] == 'all') & (clock.dose == 'homes_in_fire')].iloc[0]
    B.append(dict(part='B', outcome=k, n=len(d), rho_far_only=spearmanr(d.v, d.dose)[0], rho_exp11=c.rho))
B = pd.DataFrame(B)

# ---------------------------------------------------------------- Part C: per destroyed home bounds
def unburned_level(fn, row, level):
    burned = burned_by_F[row.F]
    comp = [fn(c, row.m0, level) if level is not None else fn(c, row.m0) for c in sorted(ALL - burned)]
    comp = [x for x in comp if pd.notna(x)]
    return np.median(comp) if comp else np.nan


C = []
specs = [('rent_pct_per_100_homes', lambda c, m0: rent_change(c, m0), 100.0, 100),
         ('dv_incidents_per_year_per_home', lambda c, m0: dv_change(c, m0, level=True), 1.0, 1),
         ('income_support_recipients_per_home', lambda c, m0: sup_change(c, m0, level=True), 1.0, 1)]
for name, fn, scale, per in specs:
    y, x, gid = [], [], []
    cache = {}
    for row in m[m.homes_v2.notna()].itertuples():
        own = fn(row.region_id, row.m0)
        key = (row.F, row.m0)
        if key not in cache:
            comp = [fn(c, row.m0) for c in sorted(ALL - burned_by_F[row.F])]
            comp = [v for v in comp if pd.notna(v)]
            cache[key] = np.median(comp) if comp else np.nan
        if pd.notna(own) and pd.notna(cache[key]):
            y.append((own - cache[key]) * scale); x.append(row.homes_v2); gid.append(row.region_id)
    y, x, gid = np.array(y), np.array(x), np.array(gid)
    slope = np.polyfit(x, y, 1)[0] * per
    ug = np.unique(gid); idx = {g: np.where(gid == g)[0] for g in ug}
    bs = []
    for _ in range(2000):
        ii = np.concatenate([idx[g] for g in RNG.choice(ug, len(ug))])
        if np.std(x[ii]) > 0:
            bs.append(np.polyfit(x[ii], y[ii], 1)[0] * per)
    C.append(dict(part='C', measure=name, n=len(y), rows_with_homes=int((x > 0).sum()), slope=slope,
                  lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5)))
C = pd.DataFrame(C)

U.drop(columns=['far']).to_csv(OUT / 'NEIGHBOUR_UNITS.csv', index=False)
pd.concat([A, B]).to_csv(OUT / 'SPILLOVER.csv', index=False)
C.to_csv(OUT / 'BOUNDS.csv', index=False)
pd.set_option('display.width', 200)
print('Part A (neighbour units:', len(U), ')'); print(A.round(4).to_string(index=False))
print('\nPart B'); print(B.round(3).to_string(index=False))
print('\nPart C'); print(C.round(3).to_string(index=False))
