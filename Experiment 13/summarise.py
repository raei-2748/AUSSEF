"""Experiment 13: collect results, Holm over the primary family, verdicts and COVID-survival rule (PRESPEC 2.3, 5).
Binary-dose rows: the effect is for the indicator (H >= 10%), so the 'full' columns are the effect; per-10pp
columns are blanked for those rows. Run: uv run --no-project --with pandas --with scipy python summarise.py"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

import e13lib as L

RES = Path(__file__).resolve().parent / 'results'
rows = []
for ch in ('income', 'pia', 'unemployment', 'businesses', 'dv', 'dv_postcode', 'property'):
    f = RES / f'{ch}.json'
    if f.exists():
        for r in json.loads(f.read_text()):
            r = dict(r)
            path = r.pop('path', {})
            r['path'] = '; '.join(f"{k}: {v['per10']:+.2f} [{v['lo']:+.2f}, {v['hi']:+.2f}]" for k, v in path.items())
            r.pop('placebo_terms', None)
            rows.append(r)
d = pd.DataFrame(rows)
b = d.binary == True  # noqa: E712
for c in ('main_per10', 'main_lo', 'main_hi', 'placebo_per10', 'placebo_lo', 'placebo_hi'):
    if c in d:
        d.loc[b, c] = np.nan
d['unit_of_effect'] = np.where(d.outcome.isin(['rate']), 'pct points', np.where(d.outcome == 'ne_share', 'share (x100 = pct points)', '% change'))
d['placebo_pass'] = (d.placebo_lo <= 0) & (d.placebo_hi >= 0)
d.loc[b, 'placebo_pass'] = (d.loc[b, 'placebo_full_lo'] <= 0) & (d.loc[b, 'placebo_full_hi'] >= 0)
pr = d[d.primary == True].copy()  # noqa: E712
pr['holm_p'] = L.holm(pr.main_p.values)
d = d.merge(pr[['channel', 'outcome', 'sample', 'spec', 'holm_p']], on=['channel', 'outcome', 'sample', 'spec'], how='left')


def verdict(r):
    lo, hi = r.main_lo, r.main_hi
    if pd.isna(lo):
        return 'not estimable'
    excl = lo > 0 or hi < 0
    if not excl:
        return 'not detected at this scale'
    sign = 'up' if lo > 0 else 'down'
    if r.get('primary') and r.holm_p < 0.05 and r.placebo_pass:
        return f'detected ({sign})'
    return f'suggestive ({sign})' + ('' if r.placebo_pass else '; placebo fails')


d['verdict'] = d.apply(verdict, axis=1)
# COVID-survival rule for B primary rows: placebo passes and P estimate same sign
ps = d[(d['sample'] == 'P') & (d.spec == 'primary')].set_index(['channel', 'outcome']).main_per10
def covid(r):
    if r['sample'] != 'B' or r.spec != 'primary':
        return ''
    pv = ps.get((r.channel, r.outcome), np.nan)
    if pd.isna(pv):
        return 'no pre-COVID estimate'
    ok = r.placebo_pass and np.sign(pv) == np.sign(r.main_per10)
    return 'passes COVID checks' if ok else ('fails: placebo' if not r.placebo_pass else 'fails: pre-COVID sign differs')
d['covid_check'] = d.apply(covid, axis=1)
cols = ['channel', 'outcome', 'sample', 'spec', 'primary', 'dose', 'fe', 'model', 'years', 'n_units', 'n_obs',
        'n_exposed_units', 'unit_of_effect', 'main_per10', 'main_lo', 'main_hi', 'main_p', 'holm_p', 'main_full',
        'main_full_lo', 'main_full_hi', 'placebo_per10', 'placebo_lo', 'placebo_hi', 'placebo_full', 'placebo_pass',
        'verdict', 'covid_check', 'path', 'placebo_n_obs', 'placebo_error']
d[[c for c in cols if c in d]].to_csv(RES / 'ALL_RESULTS.csv', index=False)
show = d[d.spec == 'primary'][['channel', 'outcome', 'sample', 'main_per10', 'main_lo', 'main_hi', 'holm_p',
                                'placebo_per10', 'placebo_lo', 'placebo_hi', 'n_exposed_units', 'verdict', 'covid_check']]
pd.set_option('display.width', 250)
print(show.round(3).to_string())
