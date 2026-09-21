"""P_obs, P_ind, rho (log scale), bootstrap intervals and N_eff. Missing is NaN, never 0."""
import numpy as np

LOG5 = np.log(5.0)


def jeffreys(k, n):
    return (k + 0.5) / (n + 1.0)


def log_rho(iso, closed):
    """iso: (n,) bool; closed: (n, m) bool. Returns (log P_obs, log P_ind, log rho); rho NaN if k == 0."""
    n = iso.shape[0]
    k = iso.sum()
    lp_obs = np.log(jeffreys(k, n))
    lp_ind = np.log(jeffreys(closed.sum(axis=0), n)).sum()
    lr = lp_obs - lp_ind if k > 0 else np.nan
    return lp_obs, lp_ind, lr


def bootstrap_log_rho(iso, closed, rng, B=1000):
    """Percentile 95% interval for log rho. Undefined resamples (k == 0) rank below all defined values."""
    n = iso.shape[0]
    idx = rng.integers(0, n, size=(B, n))
    k = iso[idx].sum(axis=1)
    c = closed[idx].sum(axis=1)  # (B, m)
    lr = np.log(jeffreys(k, n)) - np.log(jeffreys(c, n)).sum(axis=1)
    lr = np.where(k > 0, lr, -np.inf)
    # No interpolation, so an undefined (-inf) neighbour never produces NaN arithmetic.
    lo, hi = np.quantile(lr, [0.025, 0.975], method="inverted_cdf")
    undefined_share = float((k == 0).mean())
    lo = np.nan if not np.isfinite(lo) else lo
    hi = np.nan if not np.isfinite(hi) else hi
    return lo, hi, undefined_share


def n_eff(closed):
    """Effective number of exits from the phi-correlation eigen-spectrum.

    Constant columns (never closed / always closed) are excluded because phi is undefined.
    """
    if closed.shape[1] == 0:
        return np.nan, 0, 0
    col = closed.sum(axis=0)
    n = closed.shape[0]
    never = int((col == 0).sum())
    always = int((col == n).sum())
    X = closed[:, (col > 0) & (col < n)].astype(float)
    m = X.shape[1]
    if m == 0:
        return np.nan, never, always
    if m == 1:
        return 1.0, never, always
    C = np.corrcoef(X, rowvar=False)
    lam = np.linalg.eigvalsh(C)
    return float(lam.sum() ** 2 / (lam ** 2).sum()), never, always
