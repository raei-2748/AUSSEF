"""Experiment 14 descriptive tables (NOT pre-registered tests; PRESPEC 'Descriptive' section).
1. Spearman of each v4 indicator rank (and v3 counterpart) with log homes in fire per 1,000 and log share burned.
2. Payments (NEMA, AGRN 880 only) per 1,000 residents for panel rows: descriptive only, not in Y.
3. Injuries recorded (descriptive only).
4. How much Y v4 agrees with Y v3 / v1 (Spearman across rows).
Run: python3 descriptive.py -> results/DESC_*.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'Experiment 9'))
import build_v3_indicators as V  # noqa: E402  (council name normaliser, read-only)

T = pd.read_csv(HERE / 'results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
E9 = pd.read_csv(HERE.parent / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
T = T.merge(E9[['agrn', 'region_id'] + [c for c in E9 if c.startswith('ind_')]].rename(
    columns=lambda c: c.replace('ind_', 'v3_') if c.startswith('ind_') else c), on=['agrn', 'region_id'], validate='1:1')


def sp(a, b):
    ok = a.notna() & b.notna()
    return (spearmanr(a[ok], b[ok])[0], int(ok.sum())) if ok.sum() >= 10 else (np.nan, int(ok.sum()))


rows = []
for c in [c for c in T if c.startswith('ind_') or c.startswith('v3_')] + ['DL', 'IL', 'FP', 'SL', 'Y_v4', 'Y_v4_mag',
                                                                         'Y_v4_H0', 'Y_v4_H12', 'Y_v4_H3', 'Y_v3', 'Y_v1cfg']:
    r1, n1 = sp(T[c], T.log_homes_in_fire_per_1000)
    r2, n2 = sp(T[c], T.log_share)
    rows.append(dict(item=c, version='v3' if c.startswith('v3_') or c == 'Y_v3' else ('v1' if c == 'Y_v1cfg' else 'v4'),
                     n=n1, rho_homes_in_fire=r1, rho_log_share=r2))
pd.DataFrame(rows).to_csv(HERE / 'results/DESC_TRACK_FIRE.csv', index=False)
print(pd.DataFrame(rows).round(2).to_string(index=False))

agree = [dict(a=a, b=b, rho=sp(T[a], T[b])[0], n=sp(T[a], T[b])[1]) for a, b in
         [('Y_v4', 'Y_v3'), ('Y_v4', 'Y_v1cfg'), ('Y_v3', 'Y_v1cfg'), ('Y_v4', 'Y_v4_mag'), ('FP', 'FP_v3'),
          ('SL', 'SL_v3'), ('IL', 'IL_v3'), ('Y_v4', 'Y_v4_olg'), ('Y_v4', 'Y_v4_resident_deaths')]]
pd.DataFrame(agree).to_csv(HERE / 'results/DESC_AGREEMENT.csv', index=False)
print(pd.DataFrame(agree).round(3).to_string(index=False))

# payments (descriptive only)
p = pd.read_csv(HERE / 'raw/disaster_history_payments_2026_april_17.csv')
p = p[(p['State Name'] == 'New South Wales') & (p['Location Type'] == 'LGA')]
key = V.councils().set_index('key').region_id
p['region_id'] = p['Location Name'].map(V.norm).map(key)
unmatched = sorted(p.loc[p.region_id.isna(), 'Location Name'].unique())
num = lambda s: pd.to_numeric(s.astype(str).str.replace(r'[$,]', '', regex=True).replace({'<20': np.nan, '<20,000.00': np.nan}), errors='coerce')  # noqa: E731
p['eligible'] = num(p['Eligible Claims (No.)'])
p['granted'] = num(p['Dollars Granted ($)'])
p['suppressed'] = p['Eligible Claims (No.)'].astype(str).str.startswith('<')
pp = p[p['Payment Type Name'].isin(['Disaster Recovery Payment', 'Disaster Recovery Allowance'])]
pp = pp.assign(agrn=pp['Disaster AGRN'].astype(str))
w = pp.pivot_table(index=['agrn', 'region_id'], columns='Payment Type Name', values=['eligible', 'granted'], aggfunc='sum')
w.columns = [f'{a}_{b.split()[-1].lower()}' for a, b in w.columns]
sup = pp.groupby(['agrn', 'region_id', 'Payment Type Name']).suppressed.any().unstack().add_prefix('suppressed_')
sup.columns = [c.split()[-1].lower() and f"suppressed_{c.split()[-1].lower()}" for c in sup.columns]
w = w.join(sup).reset_index()
D = T[['agrn', 'region_id', 'region_name', 'season', 'population_pre']].merge(w, on=['agrn', 'region_id'], how='inner')
D['AGDRP_eligible_per_1000'] = D.eligible_payment / D.population_pre * 1000
D.to_csv(HERE / 'results/DESC_PAYMENTS_AGRN880.csv', index=False)
print('payments: panel rows with any AGDRP/DRA record:', len(D), '| NSW LGA names unmatched:', unmatched)
print(D.round(2).to_string(index=False))

inj = T.loc[T.injuries_descriptive.notna(), ['agrn', 'region_id', 'region_name', 'season', 'injuries_descriptive']]
inj.to_csv(HERE / 'results/DESC_INJURIES.csv', index=False)
print('injuries recorded rows', len(inj), 'total', inj.injuries_descriptive.sum())
