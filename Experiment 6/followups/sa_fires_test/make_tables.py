"""Markdown tables for FINDINGS.md from the frozen outputs (no new statistics)."""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
FT = RES / 'frozen_test'
Y = pd.read_csv(RES / 'Y_indicators_new_rows.csv', dtype={'region_id': str})
R = pd.read_csv(FT / 'TEST_RESULTS.csv')
P = pd.read_csv(FT / 'POWER_CHECK.csv')
N = pd.read_csv(FT / 'ROWS_NEEDED.csv')
V = json.load(open(FT / 'VERDICT.json'))
SHORT = {'SA_2015_sampson_flat': 'Sampson Flat 2015', 'SA_2015_pinery': 'Pinery 2015', 'SA_2019_cudlee_creek': 'Cudlee Creek 2019',
         'SA_2019_20_kangaroo_island': 'Kangaroo Island 2019-20', 'SA_2019_20_keilira': 'Keilira 2019-20'}


def f(x, d=2):
    return '' if pd.isna(x) else f'{x:.{d}f}'


out = ['### SA row table (score, pillars, coverage)\n',
       '| Event | Council | Burned % | Homes destroyed (status) | Blocks | risk_add_avail | V | DL | IL | FP | SL | pillars | Y_new |',
       '|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in Y.sort_values(['event', 'share_burned'], ascending=[True, False]).itertuples():
    blocks = ''.join(b for b, v in zip('HEVF', [r.H, r.E, r.V, r.F]) if pd.notna(v)) or '-'
    hd = 'blank' if pd.isna(r.homes_destroyed) else f'{r.homes_destroyed:.0f} ({r.flag_DL})'
    out.append(f'| {SHORT[r.event]} | {r.region_name} | {100 * r.share_burned:.1f} | {hd} | {blocks} | {f(r.risk_add_avail)} | {f(r.V)} | {f(r.DL)} | {f(r.IL)} | {f(r.FP)} | {f(r.SL)} | {r.pillars_n} | {f(r.Y_new)} |')
out += ['\n### Tests\n', '| Test | Scope | Score | Target | n | Spearman | 95% CI |', '|---|---|---|---|---:|---:|---|']
for r in R.itertuples():
    ci = '' if pd.isna(r.ci_low) else f'[{r.ci_low:+.2f}, {r.ci_high:+.2f}]'
    out.append(f'| {r.test} | {r.scope} | {r.score} | {r.target} | {r.n} | {f(r.spearman)} | {ci or "not estimable"} |')
out += ['\n### Planted-effect power\n', '| Rows | n | planted rho | power (CI lower > 0) | chance CI upper < 0.30 |', '|---|---:|---:|---:|---:|']
for r in P.itertuples():
    out.append(f'| {r.rows_set} | {r.n} | {r.planted_rho} | {100 * r.power_lo_gt0:.0f}% | {100 * r.chance_hi_lt_030:.0f}% |')
out += ['\n### Rows still needed (80% power, Fisher approximation)\n', '| true rho | rows needed | pooled rows now | further rows |', '|---:|---:|---:|---:|']
for r in N.itertuples():
    out.append(f'| {r.true_rho} | {r.rows_needed_for_80pct_power} | {r.pooled_rows_now} | {r.further_rows_needed} |')
(FT / 'TABLES.md').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
print(V['verdict'])
