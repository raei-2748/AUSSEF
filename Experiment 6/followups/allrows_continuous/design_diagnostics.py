"""Design-only diagnostics for the all-rows continuous analysis. X side and missingness pattern ONLY.

This script never computes any relation between Y (or a pillar) and anything else: the Y columns are dropped
right after counting non-missing cells. It exists so the pre-specification in allrows_continuous.py can be written
knowing the sample sizes, cluster counts and collinearity of the design, without having looked at results.

Run: python3 design_diagnostics.py   (writes results/DESIGN_DIAGNOSTICS.txt)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
d = pd.read_csv(ROOT / 'inputs' / 'ROWS_WITH_SCORE_v2.csv')
d['agrn'] = d.agrn.astype(str)
TARGETS = ['Y', 'DL', 'IL', 'FP', 'SL']
BS = d.agrn == '871'
lines = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    lines.append(s)


P('rows', len(d), '| fires', d.agrn.nunique(), '| councils', d.region_id.nunique())
P('non-missing per target (all rows / excluding Black Summer / Black Summer only):')
for t in TARGETS:
    ok = d[t].notna()
    P(f'  {t:>2}: {int(ok.sum()):3d} / {int((ok & ~BS).sum()):3d} / {int((ok & BS).sum()):3d}')
d = d.drop(columns=TARGETS + ['Y_class'])          # from here on no outcome is available

P('\nclusters: councils all rows', d.region_id.nunique(), '| excl BS', d[~BS].region_id.nunique(),
  '| fires excl BS', d[~BS].agrn.nunique())
cnt = d.groupby('region_id').size()
P('rows per council: 1 row', int((cnt == 1).sum()), '| 2+ rows', int((cnt >= 2).sum()), '| max', int(cnt.max()))
cnt2 = d[~BS].groupby('region_id').size()
P('excl BS, rows per council: 1 row', int((cnt2 == 1).sum()), '| 2+ rows', int((cnt2 >= 2).sum()))
fc = d.groupby('agrn').size()
P('rows per fire: 1 row', int((fc == 1).sum()), '| 2+ rows', int((fc >= 2).sum()), '| max (Black Summer)', int(fc.max()))

P('\nfire-size measures (all rows):')
P('  share: min', f'{d.share.min():.2e}', 'median', f'{d.share.median():.4f}', 'max', f'{d.share.max():.3f}',
  '| share == 0 rows:', int((d.share <= 0).sum()))
P('  burn_ha: min', f'{d.burn_ha.min():.3f}', 'median', f'{d.burn_ha.median():.0f}', 'max', f'{d.burn_ha.max():.0f}')
P('  share >= 5%:', int((d.share >= .05).sum()), 'rows (Black Summer', int(((d.share >= .05) & BS).sum()), ')')
d['s_log'] = np.log10(d.share)
d['s_rank'] = d.share.rank(pct=True)
d['s_logha'] = np.log10(d.burn_ha)
P('  log10(share): mean', f'{d.s_log.mean():.3f}', 'sd', f'{d.s_log.std():.3f}',
  '| in Black Summer mean', f'{d[BS].s_log.mean():.3f}', '| elsewhere', f'{d[~BS].s_log.mean():.3f}')
P('  log10(share) at 5%:', f'{np.log10(.05):.3f}', ' -> z =', f'{(np.log10(.05) - d.s_log.mean()) / d.s_log.std():.2f}')

X = ['H', 'E', 'V', 'F']
P('\nSpearman among predictors (rows, all):')
P(d[X + ['s_log', 's_rank', 's_logha']].corr(method='spearman').round(2).to_string())
P('\nSpearman among predictors, excluding Black Summer:')
P(d[~BS][X + ['s_log', 's_rank', 's_logha']].corr(method='spearman').round(2).to_string())


def vif(M):
    M = (M - M.mean()) / M.std()
    out = {}
    for c in M:
        others = np.column_stack([np.ones(len(M)), M.drop(columns=c).to_numpy()])
        b = np.linalg.lstsq(others, M[c].to_numpy(), rcond=None)[0]
        r2 = 1 - ((M[c].to_numpy() - others @ b) ** 2).sum() / ((M[c] - M[c].mean()) ** 2).sum()
        out[c] = 1 / (1 - r2)
    return pd.Series(out)


z = lambda a: (a - a.mean()) / a.std()
for lab, sub in [('all rows', d), ('excluding Black Summer', d[~BS])]:
    Z = pd.DataFrame({c: z(d[c]) for c in X + ['s_log']}).loc[sub.index]
    for b in X:
        Z[f'{b}:s'] = Z[b] * Z['s_log']
    P(f'\nVIF of the primary design ({lab}; blocks and log10 share standardised on all rows):')
    P(vif(Z).round(1).to_string())

P('\nBlock means, Black Summer rows vs others (X side only):')
P(d.groupby(BS)[X].mean().round(3).to_string())
(ROOT / 'results').mkdir(exist_ok=True)
(ROOT / 'results' / 'DESIGN_DIAGNOSTICS.txt').write_text('\n'.join(lines) + '\n')
