"""Small statistics helpers (no SciPy in the project environment)."""
import math

import numpy as np
import pandas as pd


def mann_whitney_p(x, y):
    """Two-sided Mann-Whitney U p-value, normal approximation with tie correction and continuity correction."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return np.nan
    r = pd.Series(np.r_[x, y]).rank().values
    u1 = r[:n1].sum() - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    _, counts = np.unique(np.r_[x, y], return_counts=True)
    n = n1 + n2
    tie = (counts ** 3 - counts).sum() / (n * (n - 1)) if n > 1 else 0
    sigma = math.sqrt(n1 * n2 / 12 * ((n + 1) - tie))
    if sigma == 0:
        return 1.0
    z = (abs(u1 - mu) - 0.5) / sigma
    return float(math.erfc(max(z, 0) / math.sqrt(2)))


def median_diff_ci(x, y, rng, B=2000):
    """median(x) - median(y) with a percentile bootstrap resampling within each group."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    est = float(np.median(x) - np.median(y))
    bx = np.median(x[rng.integers(0, len(x), (B, len(x)))], axis=1)
    by = np.median(y[rng.integers(0, len(y), (B, len(y)))], axis=1)
    lo, hi = np.quantile(bx - by, [0.025, 0.975], method="inverted_cdf")
    return est, float(lo), float(hi)


def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for k, i in enumerate(order):
        running = max(running, min(1.0, (len(p) - k) * p[i]))
        adj[i] = running
    return adj


def spearman_perm(x, y, rng, B=10000):
    x, y = pd.Series(x, dtype=float).rank().values, pd.Series(y, dtype=float).rank().values
    rho = float(np.corrcoef(x, y)[0, 1])
    perm = np.array([np.corrcoef(x, rng.permutation(y))[0, 1] for _ in range(B)])
    return rho, float((np.sum(np.abs(perm) >= abs(rho)) + 1) / (B + 1))
