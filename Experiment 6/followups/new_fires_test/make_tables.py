"""Markdown tables for FINDINGS.md from the frozen outputs (no new statistics)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
FT = RES / 'frozen_test'
Y = pd.read_csv(RES / 'Y_indicators_new_rows.csv', dtype={'region_id': str})
R = pd.read_csv(FT / 'TEST_RESULTS.csv')
P = pd.read_csv(FT / 'POWER_CHECK.csv')
V = json.load(open(FT / 'VERDICT.json'))


def f(x, d=2):
    return '' if pd.isna(x) else f'{x:.{d}f}'


out = []
out.append('### Row table (score, pillars, coverage)\n')
out.append('| Event | Council | Burned % | Homes destroyed (status) | Blocks | risk_add_avail | V | DL | IL | FP | pillars | Y_new |')
out.append('|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|')
for r in Y.itertuples():
    blocks = ''.join(b for b, v in zip('HEVF', [r.H, r.E, r.V, r.F]) if pd.notna(v)) or '-'
    hd = '' if pd.isna(r.homes_destroyed) else f'{r.homes_destroyed:.0f} ({r.flag_DL})'
    if pd.isna(r.homes_destroyed):
        hd = 'blank'
    out.append(f'| {"NSW 2013" if r.event.startswith("NSW") else "Vic 2009"} | {r.region_name} | {100*r.share_burned:.1f} | {hd} | {blocks} | {f(r.risk_add_avail)} | {f(r.V)} | {f(r.DL)} | {f(r.IL)} | {f(r.FP)} | {r.pillars_n} | {f(r.Y_new)} |')
out.append('\n### Tests\n')
out.append('| Test | Scope | Score | Target | n | Spearman | 95% CI |')
out.append('|---|---|---|---|---:|---:|---|')
for r in R.itertuples():
    ci = '' if pd.isna(r.ci_low) else f'[{r.ci_low:+.2f}, {r.ci_high:+.2f}]'
    out.append(f'| {r.test} | {r.scope} | {r.score} | {r.target} | {r.n} | {f(r.spearman)} | {ci or "not estimable"} |')
out.append('\n### Planted-effect power\n')
out.append('| Rows | n | planted rho | power (CI lower > 0) | chance CI upper < 0.30 |')
out.append('|---|---:|---:|---:|---:|')
for r in P.itertuples():
    out.append(f'| {r.rows_set} | {r.n} | {r.planted_rho} | {100*r.power_lo_gt0:.0f}% | {100*r.chance_hi_lt_030:.0f}% |')
(FT / 'TABLES.md').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
print(V['verdict'])
