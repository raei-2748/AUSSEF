"""POST HOC, DESCRIPTIVE, NOT PART OF THE LOCKED TEST (run after the locked analysis; excluded from every verdict).

Purpose: explain how the Experiment 6 result (V vs Y: Spearman +0.25 on all rows, +0.58 on fires burning >= 5% of a
council) fits with the locked continuous-size analysis, which finds no growth of V's effect with fire size. Spearman
correlation of V and Y (same definition as Experiment 6, council-cluster bootstrap 95% interval, 2,000 draws) in
groups defined by event and size. Every group here was chosen after seeing the locked results, so treat the numbers as
context for reading them, not as tests.
Also gives, per group, the plain OLS slope of Y* (rank-normal Y) on z_V (SD of Y* per SD of V, no other terms), the
SD of Y* and the residual SD, to separate "V matters more" (bigger slope) from "Y is less noisy" (smaller residual SD).
Writes results/POSTHOC_V_BY_EVENT.csv and results/POSTHOC_V_SLOPES.csv.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import RES, load

d = load()
rng = np.random.default_rng(20260929)


def boot(sub, x='V', y='Y', n=2000):
    a = sub[[x, y, 'council']].dropna()
    est = spearmanr(a[x], a[y])[0]
    gs = {k: g[[x, y]].to_numpy() for k, g in a.groupby('council')}
    keys = list(gs)
    if len(keys) < 4:
        return len(a), len(keys), est, np.nan, np.nan
    bs = []
    for _ in range(n):
        pick = rng.integers(0, len(keys), len(keys))
        m = np.vstack([gs[keys[i]] for i in pick])
        if np.unique(m[:, 0]).size > 2 and np.unique(m[:, 1]).size > 2:
            bs.append(spearmanr(m[:, 0], m[:, 1])[0])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return len(a), len(keys), est, lo, hi


groups = {
    'all rows': d.index == d.index,
    'Black Summer (50)': d.bs,
    'all other fires (168)': ~d.bs,
    'share >= 5% (Exp 6 subset)': d.share >= .05,
    'share >= 5%, Black Summer': (d.share >= .05) & d.bs,
    'share >= 5%, other fires': (d.share >= .05) & ~d.bs,
    'share < 5%': d.share < .05,
    'share < 5%, Black Summer': (d.share < .05) & d.bs,
    'share < 5%, other fires': (d.share < .05) & ~d.bs,
    'share 1-5%': (d.share >= .01) & (d.share < .05),
    'share < 1%': d.share < .01,
}
rows = []
for name, m in groups.items():
    m = np.asarray(m)
    for tgt in ['Y', 'DL', 'IL', 'FP', 'SL']:
        n, g, est, lo, hi = boot(d[m], 'V', tgt)
        rows.append(dict(group=name, target=tgt, rows=n, councils=g, spearman_V=est, lo=lo, hi=hi))
out = pd.DataFrame(rows)
out.to_csv(RES / 'POSTHOC_V_BY_EVENT.csv', index=False)
y = out[out.target == 'Y']
print(y.round(2).to_string(index=False))


# ---- slope vs noise by group (target Y only)
rows = []
for name, m in groups.items():
    a = d[np.asarray(m)]
    x, y = a.z_V.to_numpy(), a.t_Y.to_numpy()
    X = np.column_stack([np.ones(len(a)), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    res = y - X @ b
    rows.append(dict(group=name, rows=len(a), slope_Y_on_V=b[1], sd_Y=y.std(ddof=1), resid_sd=res.std(ddof=2),
                     sd_V=x.std(ddof=1), r_pearson=np.corrcoef(x, y)[0, 1]))
sl = pd.DataFrame(rows)
sl.to_csv(RES / 'POSTHOC_V_SLOPES.csv', index=False)
print()
print(sl.round(2).to_string(index=False))


# ---- is a V x size interaction visible in simpler settings? (jackknife CIs as in the locked analysis; Y only)
from arc_lib import BLOCKS, ci, design, ols_jack

rows = []
for label, blocks, events, sub in [
        ('V only, no event dummies', ['V'], False, d),
        ('V only, event dummies', ['V'], True, d),
        ('four blocks, no event dummies', BLOCKS, False, d),
        ('four blocks, event dummies (= locked primary)', BLOCKS, True, d),
        ('V only, no event dummies, excluding Black Summer', ['V'], False, d[~d.bs])]:
    X = design(sub, 'log_share', blocks, events)
    b, V, G, _ = ols_jack(X.to_numpy(), sub.t_Y.to_numpy(), sub.council.to_numpy())
    _, lo, hi, p = ci(b, V, G - 1)
    j = list(X.columns).index('V:size')
    rows.append(dict(model=label, g_V=b[j], lo=lo[j], hi=hi[j], p=p[j], rows=len(sub), councils=G))
dec = pd.DataFrame(rows)
dec.to_csv(RES / 'POSTHOC_V_DECOMP.csv', index=False)
print()
print(dec.round(3).to_string(index=False))
