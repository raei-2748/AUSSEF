"""Audit check (e): hand spot-checks of time alignment and arithmetic for 5 rows.
Shows m0, F, the FY values used for C4 and C5, the calendar months used for C1 H0 and C3 H2, and compares the row's
excess with Experiment 11 CLOCK_ROWS."""
import re
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/Users/ray/Research/AUSSEF - Local'); OUT = Path(__file__).resolve().parent
m = pd.read_csv(OUT / 'rederived_c4_c5_rows.csv', dtype={'agrn': str, 'region_id': str})
R = pd.read_csv(ROOT / 'Experiment 11/results/CLOCK_ROWS.csv', dtype={'agrn': str, 'region_id': str})
cl = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})[['region_id', 'region_name_x']]
ALL = set(cl.region_id); master = m.groupby('F').region_id.apply(set).to_dict()
GEN = {'city', 'council', 'shire', 'regional', 'municipal', 'of', 'the', 'area'}
key = lambda s: ' '.join(x for x in re.findall(r'[a-z]+', re.sub(r'\(.*?\)', ' ', str(s).lower()).replace('-', ' ')) if x not in GEN)
k2id = {key(n): r for r, n in zip(cl.region_id, cl.region_name_x)}
o = pd.read_parquet(ROOT / 'fire_event_dataset/data/olg/olg_long.parquet')
w = o.pivot_table(index=['council_name_norm', 'fy_start'], columns='metric', values='value', aggfunc='first').reset_index()
w['gpc'] = w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population
w['rid'] = w.council_name_norm.map(key).map(k2id); G = w.dropna(subset=['rid']).set_index(['rid', 'fy_start']).gpc
def ch(c, F, k=1):
    post = G.get((c, F + k), np.nan); pre = [np.log(x) for x in (G.get((c, F - 2), np.nan), G.get((c, F - 1), np.nan)) if pd.notna(x) and x > 0]
    return np.log(post) - np.mean(pre) if pd.notna(post) and post > 0 and pre else np.nan
t = pd.read_csv(ROOT / 'Experiment 10/A_fire_councils/statements_tidy.csv', dtype={'region_id': str})
picks = [('871', '10550'), ('871', '12750'), ('1071', '14350'), ('1052', '11200'), ('RAA-raa_2016_p13_r07', '17400')]
lines = []
for agrn, rid in picks:
    r = m[(m.agrn == agrn) & (m.region_id == rid)].iloc[0]; rr = R[(R.agrn == agrn) & (R.region_id == rid)].iloc[0]
    s = pd.Timestamp(r.first_fire_start); m0 = s.to_period('M'); F = r.F
    comp = [v for v in (ch(c, F) for c in ALL - master[F]) if pd.notna(v)]
    own = ch(rid, F)
    L = [f'### {r.region_name} (region {rid}), AGRN {agrn}',
         f'- first_fire_start {s.date()} -> m0 = {m0}; F = {F} (FY {F}-{str(F + 1)[2:]}); expected F = {s.year if s.month >= 7 else s.year - 1}',
         f'- C1 H0 window months {m0}..{m0 + 3}; baseline {m0 - 12}..{m0 - 9} and {m0 - 24}..{m0 - 21}. C3 H2 window {m0 + 13}..{m0 + 24}, baseline {m0 - 24}..{m0 - 1}',
         f'- C4: grants per resident FY{F - 2}={G.get((rid, F - 2), np.nan):.0f}, FY{F - 1}={G.get((rid, F - 1), np.nan):.0f}, FY{F + 1}={G.get((rid, F + 1), np.nan):.0f} A$; '
         f'own log change {own:+.3f}; comparison median ({len(comp)} councils) {np.median(comp):+.3f}; excess {own - np.median(comp):+.3f}; Exp11 C4_H1 {rr.C4_grants_pc_H1:+.3f}']
    tt = t[t.region_id == rid]
    if len(tt):
        te = tt[tt['item'] == 'total_expenses'].set_index(tt[tt['item'] == 'total_expenses'].fy.str[:4].astype(int)).value_aud
        L.append(f'- statements total expenses by FY: {te.to_dict()}; Exp11 C5_H1 = {rr.C5_fire_grant_share_H1}')
    lines += L + ['']
txt = '\n'.join(lines); print(txt); open(OUT / 'spot_checks.md', 'w').write(txt)
