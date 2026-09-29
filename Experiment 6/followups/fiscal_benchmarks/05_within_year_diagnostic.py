"""Step 5 (POST-HOC diagnostic, not pre-specified): both Y and the new measure drift with the fire year, so a pooled
correlation can pick up a common time trend. Re-run the primary test after ranking stress_bench and Y WITHIN each
fire financial year (percentile rank inside the year), all rows and excluding Black Summer. Same bootstrap routine.
Writes WITHIN_YEAR_DIAGNOSTIC.txt.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROWS = Path('/Users/ray/Research/AUSSEF/Experiment 6/results/ROWS_WITH_SCORE_v2.csv')
rng = np.random.default_rng(20260929)
m = pd.read_csv(HERE / 'BENCHMARK_MEASURE_ROWS.csv', dtype={'agrn': str})
r = pd.read_csv(ROWS, dtype={'agrn': str}).rename(columns={'F': 'F_old'})
d = r.merge(m[['agrn', 'region_id', 'stress_bench', 'F_tm', 'fire_fy_start']], on=['agrn', 'region_id']).dropna(subset=['stress_bench'])
lines = [f"drift with fire year: Spearman(stress_bench, fire FY)={spearmanr(d.stress_bench, d.fire_fy_start)[0]:+.2f}, "
         f"Spearman(Y, fire FY)={spearmanr(d.Y, d.fire_fy_start)[0]:+.2f}, Spearman(F_old, fire FY)={spearmanr(d.F_old, d.fire_fy_start)[0]:+.2f}"]
for tgt in ['Y', 'DL', 'IL', 'FP', 'SL']:
    for col in ['stress_bench', 'F_tm']:
        d[f'{col}_w'] = d.groupby('fire_fy_start')[col].rank(pct=True)
    d[f'{tgt}_w'] = d.groupby('fire_fy_start')[tgt].rank(pct=True)
for label, sub in [('all rows', d), ('all rows excl. Black Summer', d[d.agrn != '871']),
                   ('>= 5% burned', d[d.share >= 0.05])]:
    for tgt in ['Y', 'DL', 'IL', 'FP', 'SL']:
        s = sub.dropna(subset=[tgt, f'{tgt}_w'])
        if len(s) < 8:
            continue
        cells = []
        for col in ['stress_bench', 'F_tm']:
            est = spearmanr(s[f'{col}_w'], s[f'{tgt}_w'])[0]
            grp = {k: g[[f'{col}_w', f'{tgt}_w']].to_numpy() for k, g in s.groupby('region_id')}
            keys = list(grp)
            bs = []
            for _ in range(2000):
                a = np.vstack([grp[keys[i]] for i in rng.choice(len(keys), len(keys))])
                if len(np.unique(a[:, 0])) > 2 and len(np.unique(a[:, 1])) > 2:
                    bs.append(spearmanr(a[:, 0], a[:, 1])[0])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            cells.append(f'{col} {est:+.2f} [{lo:+.2f}, {hi:+.2f}]')
        lines.append(f'{label:28s} {tgt:3s} n={len(s):3d}  ' + ' | '.join(cells))
txt = '\n'.join(lines)
print(txt)
(HERE / 'WITHIN_YEAR_DIAGNOSTIC.txt').write_text(txt + '\n')
