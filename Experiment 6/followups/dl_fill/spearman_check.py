"""Spearman(score, DL) with a council-cluster bootstrap, same algorithm as Experiment 6 (build_and_validate_score.py).

Difference from Experiment 6: every (score, subset) gets its own fixed-seed generator, and the SAME resampled council
draws are used for 'before' and 'after', so the change in rho has its own paired interval. Point estimates are exact
reproductions of Experiment 6; the CI end points can differ from REPORT.md in the second decimal because the original
shared one random stream across hundreds of calls.
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

SEED = 20260929
N_BOOT = 2000


def _rho(x, y):
    if np.unique(x).size < 3 or np.unique(y).size < 3:
        return np.nan
    return spearmanr(x, y)[0]


def paired_boot(df, score, cols, n_boot=N_BOOT, seed=SEED):
    """df has columns: score, region_id, and each of `cols` (DL variants; NaN = not available).
    Returns dict col -> (n, rho, lo, hi) and dict for the change vs cols[0] (the 'before' column)."""
    sub = df[['region_id', score] + cols].copy()
    groups = {g: s for g, s in sub.groupby('region_id')}
    keys = list(groups)
    rng = np.random.default_rng(seed)
    est = {}
    for c in cols:
        d = sub[[score, c]].dropna()
        est[c] = (len(d), _rho(d[score].to_numpy(), d[c].to_numpy()) if len(d) >= 6 else np.nan)
    draws = {c: [] for c in cols}
    diff = {c: [] for c in cols[1:]}
    for _ in range(n_boot):
        pick = rng.choice(len(keys), len(keys))
        b = pd.concat([groups[keys[i]] for i in pick], ignore_index=True)
        r = {}
        for c in cols:
            d = b[[score, c]].dropna()
            r[c] = _rho(d[score].to_numpy(), d[c].to_numpy()) if len(d) >= 6 else np.nan
            draws[c].append(r[c])
        for c in cols[1:]:
            diff[c].append(r[c] - r[cols[0]])
    out, chg = {}, {}
    for c in cols:
        a = np.array(draws[c], float)
        a = a[~np.isnan(a)]
        lo, hi = np.percentile(a, [2.5, 97.5]) if len(a) > 50 else (np.nan, np.nan)
        out[c] = (est[c][0], est[c][1], lo, hi)
    for c in cols[1:]:
        a = np.array(diff[c], float)
        a = a[~np.isnan(a)]
        lo, hi = np.percentile(a, [2.5, 97.5]) if len(a) > 50 else (np.nan, np.nan)
        chg[c] = (out[c][1] - out[cols[0]][1], lo, hi)
    return out, chg
