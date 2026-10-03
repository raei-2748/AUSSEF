"""Audit checks (c) and (f): who is in the 'unburned' comparison set, and does C4 H1 survive stricter comparisons?
 - per fire year F: comparison councils (no master row in F); of those, how many had >= 0.5% of area burned in FY F
   (fires.csv, Experiment 7 rule) or a master row in F-2..F+1 (fire inside the outcome/baseline window).
 - C4 H1 recomputed with: (i) comparison minus councils burned >= 0.5% in F, (ii) minus councils with a master row
   in any FY F-2..F+1, (iii) comparison restricted to the same OLG group (Metro / Regional / Rural).
 - C4 H1 within-season Spearman (rows ranked within F) as a check that it is not a between-season artefact."""
import re
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
ROOT = Path('/Users/ray/Research/AUSSEF - Local'); OUT = Path(__file__).resolve().parent
m = pd.read_csv(OUT / 'rederived_c4_c5_rows.csv', dtype={'agrn': str, 'region_id': str})
D = m.log_homes_in_fire_per_1000
cl = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})[['region_id', 'region_name_x']]
ALL = set(cl.region_id); name = cl.set_index('region_id').region_name_x
master = m.groupby('F').region_id.apply(set).to_dict()
f = pd.read_csv(ROOT / 'fire_event_dataset/out/fires.csv', low_memory=False, dtype={'region_id': str})
t = pd.to_datetime(f.date_start); f['fy'] = np.where(t.dt.month >= 7, t.dt.year, t.dt.year - 1)
g = f.groupby(['region_id', 'fy']).share_of_region_burned.sum()
aff = {F: set(g[(g.index.get_level_values(1) == F) & (g >= 0.005)].index.get_level_values(0)) for F in range(2012, 2026)}
rows = []
for F in sorted(master):
    comp = ALL - master[F]
    near = set().union(*[master.get(y, set()) for y in range(F - 2, F + 2)]) - master[F]
    rows.append(dict(F=F, master_rows=int((m.F == F).sum()), comparison=len(comp), comp_burned_ge_0_5pct_in_F=len(comp & aff.get(F, set())),
                     comp_with_master_row_in_F_minus2_to_F_plus1=len(comp & near),
                     examples_burned=', '.join(sorted(name[list(comp & aff.get(F, set()))])[:8])))
E = pd.DataFrame(rows); print(E.to_string(index=False)); E.to_csv(OUT / 'comparison_sets.csv', index=False)

# C4 values (same definition as 02)
o = pd.read_parquet(ROOT / 'fire_event_dataset/data/olg/olg_long.parquet')
w = o.pivot_table(index=['council_name_norm', 'fy_start'], columns='metric', values='value', aggfunc='first').reset_index()
w['gpc'] = w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population
GEN = {'city', 'council', 'shire', 'regional', 'municipal', 'of', 'the', 'area'}
key = lambda s: ' '.join(x for x in re.findall(r'[a-z]+', re.sub(r'\(.*?\)', ' ', str(s).lower()).replace('-', ' ')) if x not in GEN)
k2id = {key(n): r for r, n in zip(cl.region_id, cl.region_name_x)}
w['rid'] = w.council_name_norm.map(key).map(k2id); w = w.dropna(subset=['rid'])
L = np.log(w[w.gpc > 0].set_index(['rid', 'fy_start']).gpc)
def ch(cid, F, k=1):
    post = L.get((cid, F + k), np.nan); pre = [x for x in (L.get((cid, F - 2), np.nan), L.get((cid, F - 1), np.nan)) if pd.notna(x)]
    return post - np.mean(pre) if pd.notna(post) and pre else np.nan
# OLG groups
x = pd.read_excel(ROOT / 'fire_event_dataset/data/olg/time-series-data-2018-2019.xlsx', sheet_name='2018_19_Councils', header=None).iloc[3:, :3]
x.columns = ['council', 'grp', 'cls']
GROUPS = {'Metropolitan': 'Metro', 'Metropolitan Fringe': 'Metro', 'Regional Town/City': 'Regional', 'Rural': 'Rural', 'Large Rural': 'Rural'}
x['rid'] = x.council.map(key).map(k2id); x['G'] = x.cls.map(GROUPS)
grp = x.dropna(subset=['rid', 'G']).set_index('rid').G.to_dict()
print('councils with OLG group:', len(grp))
def excess(comp_fn, k=1):
    out = []
    for r in m.itertuples():
        own = ch(r.region_id, r.F, k)
        comp = [v for v in (ch(c, r.F, k) for c in comp_fn(r)) if pd.notna(v)]
        out.append(own - np.median(comp) if pd.notna(own) and comp else np.nan)
    return pd.Series(out, index=m.index)
def sp(y, lab):
    ok = y.notna(); rho = spearmanr(D[ok], y[ok])[0]
    # within-season rank correlation: rank x and y within F, then Spearman of the within-F percentile ranks
    rx = D[ok].groupby(m.F[ok]).rank(pct=True); ry = y[ok].groupby(m.F[ok]).rank(pct=True)
    print(f'{lab}: n={ok.sum()} rho={rho:+.3f}  within-season-rank rho={spearmanr(rx, ry)[0]:+.3f}')
    return dict(variant=lab, n=int(ok.sum()), rho=rho, within_season=spearmanr(rx, ry)[0])
res = [sp(excess(lambda r: ALL - master[r.F]), 'C4 H1 as Exp11 (comparison = no master row in F)'),
       sp(excess(lambda r: ALL - master[r.F] - aff.get(r.F, set())), 'C4 H1 comparison also excludes councils burned >=0.5% in F'),
       sp(excess(lambda r: ALL - set().union(*[master.get(y, set()) for y in range(r.F - 2, r.F + 2)])), 'C4 H1 comparison excludes master rows F-2..F+1'),
       sp(excess(lambda r: {c for c in ALL - master[r.F] if grp.get(c) == grp.get(r.region_id)}), 'C4 H1 comparison = same OLG group only')]
# own change only, no comparison
own = pd.Series([ch(r.region_id, r.F) for r in m.itertuples()], index=m.index)
res.append(sp(own, 'C4 H1 own change only (no comparison)'))
# by fire season
for F, sub in m.groupby('F'):
    y = excess(lambda r: ALL - master[r.F])[sub.index]; ok = y.notna()
    if ok.sum() >= 8: print(f'  F={F}: n={ok.sum()} rho={spearmanr(D[sub.index][ok], y[ok])[0]:+.3f}')
pd.DataFrame(res).to_csv(OUT / 'c4_sensitivity.csv', index=False)
