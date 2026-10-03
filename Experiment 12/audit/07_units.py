"""Audit check (d): units and signs.
 - statements: total_expenses vs OLG total_expenses_continuing_ops_aud for the same council-year (ratio ~1 if AUD and
   x1000 applied once; ~0.001 or ~1000 if not); fire-line values and fire share ranges; capex sign.
 - OLG grants per resident: distribution (A$ per resident).
 - traffic: sign convention of C1 (log(window/baseline): fall -> negative; expected sign -1)."""
import re
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path('/Users/ray/Research/AUSSEF - Local'); OUT = Path(__file__).resolve().parent
cl = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})[['region_id', 'region_name_x']]
GEN = {'city', 'council', 'shire', 'regional', 'municipal', 'of', 'the', 'area'}
key = lambda s: ' '.join(x for x in re.findall(r'[a-z]+', re.sub(r'\(.*?\)', ' ', str(s).lower()).replace('-', ' ')) if x not in GEN)
k2id = {key(n): r for r, n in zip(cl.region_id, cl.region_name_x)}
o = pd.read_parquet(ROOT / 'fire_event_dataset/data/olg/olg_long.parquet')
o = o[o.metric.isin(['total_expenses_continuing_ops_aud', 'grants_contributions_revenue_pct', 'total_revenue_continuing_ops_aud', 'population'])]
w = o.pivot_table(index=['council_name_norm', 'fy_start'], columns='metric', values='value', aggfunc='first').reset_index()
w['region_id'] = w.council_name_norm.map(key).map(k2id); w = w.dropna(subset=['region_id'])
w['gpc'] = w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population
print('OLG grants per resident (A$), quantiles 1/50/99%:', w.gpc.quantile([.01, .5, .99]).round(0).to_dict())
print('largest:', w.nlargest(5, 'gpc')[['council_name_norm', 'fy_start', 'gpc', 'population']].to_string(index=False))
lines = []
for side in ('A_fire_councils', 'A_comparison_councils'):
    t = pd.read_csv(ROOT / f'Experiment 10/{side}/statements_tidy.csv', dtype={'region_id': str})
    t['fy_start'] = t.fy.str[:4].astype(int)
    te = t[t['item'] == 'total_expenses'][['region_id', 'fy_start', 'value_aud']]
    j = te.merge(w[['region_id', 'fy_start', 'total_expenses_continuing_ops_aud']], on=['region_id', 'fy_start'])
    j['ratio'] = j.value_aud / j.total_expenses_continuing_ops_aud
    bad = j[(j.ratio < 0.8) | (j.ratio > 1.25)]
    print(f'\n{side}: statement total_expenses / OLG total expenses, n={len(j)}, median ratio {j.ratio.median():.3f}, '
          f'outside 0.8-1.25: {len(bad)}'); print(bad.round(3).to_string(index=False))
    print('capex_ippe negative values:', int((t[t['item'] == 'capex_ippe'].value_aud < 0).sum()),
          '| disaster/fire lines negative:', int((t[t['item'].str.contains('disaster|bushfire')].value_aud < 0).sum()))
    s = t[t['item'].str.contains('disaster_grant|bushfire_emergency')]
    print('fire/disaster line values (A$) quantiles:', s.value_aud.quantile([.05, .5, .95]).round(0).to_dict())
    lines.append(bad.assign(side=side))
pd.concat(lines).to_csv(OUT / 'units_statement_vs_olg_outliers.csv', index=False)
