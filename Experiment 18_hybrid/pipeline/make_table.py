"""Experiment 14: v1 / v3 / v4 side by side (RF, PRE+FIRE, leave-one-season-out), pillar by pillar.
v1 and v3 rows are read from Experiment 9 results (same code, same seed); v4 from this experiment.
Run: python3 make_table.py -> results/V1_V3_V4_TABLE.csv
"""
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
E9 = HERE.parent / 'Experiment 9/results'
m9, s9 = pd.read_csv(E9 / 'METRICS.csv'), pd.read_csv(E9 / 'SHUFFLE_CHECK.csv')
m14, s14 = pd.read_csv(HERE / 'results/METRICS.csv'), pd.read_csv(HERE / 'results/SHUFFLE_CHECK.csv')
SPEC = {'v1': (m9, s9, {'Y': 'Y_comp_cfgv1', 'DL': 'DL', 'IL': 'IL_cfgv1', 'FP': 'FP_cfgv1', 'SL': 'SL_cfgv1'}),
        'v3': (m9, s9, {'Y': 'Y_comp', 'DL': 'DL', 'IL': 'IL', 'FP': 'FP', 'SL': 'SL'}),
        'v4 (post-v3)': (m14, s14, {'Y': 'Y_v4', 'DL': 'DL', 'IL': 'IL', 'FP': 'FP', 'SL': 'SL'})}
rows = []
for xs in ('PRE+FIRE', 'PRE'):
    for ver, (M, S, tg) in SPEC.items():
        for item, t in tg.items():
            q = M[(M.target == t) & (M.xset == xs) & (M.cv == 'season')]
            rf, mean = q[q.model == 'rf'].iloc[0], q[q.model == 'mean'].iloc[0]
            sh = S[(S.target == t) & (S.xset == xs)]
            rows.append(dict(xset=xs, version=ver, item=item, target=t, n=int(rf.n), rho=rf.rho, rho_lo=rf.rho_lo,
                             rho_hi=rf.rho_hi, shuffle_p=sh.p.iloc[0] if len(sh) else None,
                             rf_minus_mean_mae=mean.rf_minus_this_mae, lo=mean.rf_minus_this_lo, hi=mean.rf_minus_this_hi,
                             beats_mean=bool(mean.rf_beats_this)))
R = pd.DataFrame(rows)
R.to_csv(HERE / 'results/V1_V3_V4_TABLE.csv', index=False)
print(R.round(3).to_string(index=False))
sec = m14[(m14.cv == 'season') & (m14.model == 'rf')][['target', 'xset', 'n', 'rho', 'rho_lo', 'rho_hi', 'mae']]
mb = m14[(m14.cv == 'season') & (m14.model == 'mean')][['target', 'xset', 'rf_minus_this_lo', 'rf_minus_this_hi', 'rf_beats_this']]
print(sec.merge(mb, on=['target', 'xset']).round(3).to_string(index=False))
