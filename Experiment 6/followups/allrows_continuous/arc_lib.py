"""Shared helpers for the all-rows continuous analysis (data prep, OLS with cluster-robust SE, other estimators).

No analysis choices live here that are not already fixed in the pre-specification headers of allrows_continuous.py
and sanity_check.py; this file only implements them. (v2 of the pre-specification: see AMENDMENT LOG in
allrows_continuous.py; the v1 code is kept in amendment_v1_record/.)
"""
import ast
import hashlib
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'inputs' / 'ROWS_WITH_SCORE_v2.csv'
RES = ROOT / 'results'
LOCK = RES / 'PRESPEC_LOCK.txt'

BLOCKS = ['H', 'E', 'V', 'F']
PILLARS = ['DL', 'IL', 'FP', 'SL']
TARGETS = ['Y'] + PILLARS
BS_AGRN = '871'                     # Black Summer declaration
SHARE_FLOOR = 1e-4                  # log10(share) is floored at 0.01% of the council
HA_FLOOR = 1.0                      # log10(burn_ha) is floored at 1 ha
STEP = 0.05                         # bridge spec only: 1[share >= 5%]
CONT_SIZES = ['log_share', 'share', 'rank_share', 'log_burn_ha']
SHARES_FOR_SLOPES = [0.001, 0.01, 0.05, 0.20]
EVENT_REF = '2023'                  # reference event stratum (the largest)
EVENT_LEVELS = ['BS', '2015', '2016', '2017', '2018', '2019', '2024', '2025']


# ---------------------------------------------------------------- pre-specification lock
def header_hash(path):
    doc = ast.get_docstring(ast.parse(Path(path).read_text()), clean=False)
    return hashlib.sha256(doc.encode()).hexdigest()


def verify_lock(script):
    """The docstring (pre-specification) of `script` must equal the one recorded in PRESPEC_LOCK.txt."""
    assert LOCK.exists(), 'run lock_prespec.py first'
    rec = dict(line.split(': ', 1) for line in LOCK.read_text().splitlines() if ': ' in line)
    name = Path(script).name
    assert rec.get(f'{name} header sha256') == header_hash(script), \
        f'{name}: pre-specification header changed since it was locked'


# ---------------------------------------------------------------- data
def zs(a):
    a = np.asarray(a, float)
    return (a - np.nanmean(a)) / np.nanstd(a, ddof=1)


def rank_normal(y):
    """Blom normal scores of the ranks (ties averaged) of the non-missing values, standardised to SD 1."""
    y = pd.Series(np.asarray(y, float))
    ok = y.notna()
    r = y[ok].rank(method='average')
    out = pd.Series(np.nan, index=y.index)
    out[ok] = stats.norm.ppf((r - 0.375) / (ok.sum() + 0.25))
    out[ok] = zs(out[ok])
    return out.to_numpy()


def load():
    d = pd.read_csv(INPUT)
    d['agrn'] = d.agrn.astype(str)
    d['bs'] = d.agrn.eq(BS_AGRN)
    d['council'] = d.region_id
    d['fire'] = d.agrn
    d['stratum'] = np.where(d.bs, 'BS', d.year.astype(str))
    assert set(d.stratum) <= set(EVENT_LEVELS + [EVENT_REF]), set(d.stratum)
    d['s_log_share'] = zs(np.log10(np.maximum(d.share, SHARE_FLOOR)))
    d['s_share'] = zs(d.share)
    d['s_rank_share'] = zs(d.share.rank(pct=True))
    d['s_log_burn_ha'] = zs(np.log10(np.maximum(d.burn_ha, HA_FLOOR)))
    d['s_step5'] = (d.share >= STEP).astype(float)
    for b in BLOCKS + ['risk_add']:
        d['z_' + b] = zs(d[b])
    for t in TARGETS:
        d['t_' + t] = rank_normal(d[t])
    return d


def size_stats(d):
    x = np.log10(np.maximum(d.share, SHARE_FLOOR))
    return float(x.mean()), float(x.std(ddof=1))


def s_at_share(d, share):
    mu, sd = size_stats(d)
    return (np.log10(max(share, SHARE_FLOOR)) - mu) / sd


def event_dummies(d):
    """One 0/1 column per event stratum (Black Summer, or the start year of the other fires) except the reference 2023.
    All-zero columns (stratum absent from this sample) are dropped."""
    D = pd.DataFrame({f'ev_{v}': (d.stratum == v).astype(float) for v in EVENT_LEVELS}, index=d.index)
    return D.loc[:, D.sum() > 0]


def design(d, size, blocks=BLOCKS, events=True):
    """Columns: const, size, one z-scored column per block, block:size interactions, then (events=True) the event dummies."""
    cols = {'const': np.ones(len(d)), 'size': d['s_' + size].to_numpy()}
    for b in blocks:
        cols[b] = d['z_' + b].to_numpy()
    for b in blocks:
        cols[f'{b}:size'] = d['z_' + b].to_numpy() * d['s_' + size].to_numpy()
    X = pd.DataFrame(cols, index=d.index)
    if events:
        X = pd.concat([X, event_dummies(d)], axis=1)
    return X


# ---------------------------------------------------------------- estimators
def _codes(g):
    return pd.factorize(np.asarray(g))[0]


def _lstsq(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def ols_cr1(X, y, g):
    """OLS with Liang-Zeger cluster-robust variance, CR1 small-sample factor G/(G-1) * (N-1)/(N-K)."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n, k = X.shape
    A = np.linalg.pinv(X.T @ X)
    b = A @ X.T @ y
    e = y - X @ b
    c = _codes(g)
    G = c.max() + 1
    S = np.zeros((G, k))
    np.add.at(S, c, X * e[:, None])
    V = G / (G - 1) * (n - 1) / (n - k) * A @ (S.T @ S) @ A
    return b, V, G


def jackknife(fit, X, y, g):
    """Delete-one-cluster jackknife around the full-sample estimate (CR3-type):
    V = (G-1)/G * sum_g (b_(-g) - b)(b_(-g) - b)'.  `fit(X, y, g)` returns the coefficient vector (g = cluster ids of the rows kept).
    Returns b, V, G and the number of leave-out refits that failed (those contribute a zero difference)."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    c = _codes(g)
    G = c.max() + 1
    b = np.asarray(fit(X, y, np.asarray(g)), float)
    diffs, failed = [], 0
    for k in range(G):
        keep = c != k
        try:
            diffs.append(np.asarray(fit(X[keep], y[keep], np.asarray(g)[keep]), float) - b)
        except Exception:
            diffs.append(np.zeros_like(b))
            failed += 1
    D = np.array(diffs)
    return b, (G - 1) / G * D.T @ D, G, failed


def ols_jack(X, y, g):
    return jackknife(lambda A, yy, gg: _lstsq(A, yy), X, y, g)


def prep_cr3(X, g):
    """X-only pieces of the closed-form CR3 (equals the leave-one-cluster-out OLS refits when they are full rank)."""
    X = np.asarray(X, float)
    A = np.linalg.pinv(X.T @ X)
    c = _codes(g)
    out = []
    for k in range(c.max() + 1):
        idx = np.flatnonzero(c == k)
        Xg = X[idx]
        out.append((idx, A @ Xg.T @ np.linalg.pinv(np.eye(len(idx)) - Xg @ A @ Xg.T)))
    return A, out


def ols_cr3_multi(X, Y, prep, want_D=False):
    """Fast CR3 for many outcome vectors (columns of Y), X fixed. Returns B (k x m), se (k x m), G [, D (G x k x m)]."""
    X = np.asarray(X, float)
    A, groups = prep
    B = A @ X.T @ Y
    E = Y - X @ B
    G = len(groups)
    D = np.zeros((G, X.shape[1], Y.shape[1]))
    for i, (idx, W) in enumerate(groups):
        D[i] = W @ E[idx]
    se = np.sqrt((G - 1) / G * (D ** 2).sum(axis=0))
    return (B, se, G, D) if want_D else (B, se, G)


def ols_twoway(X, y, g1, g2):
    """Cameron-Gelbach-Miller two-way cluster variance: V(g1) + V(g2) - V(g1 x g2), CR1 factors, PSD-fixed."""
    b, V1, G1 = ols_cr1(X, y, g1)
    _, V2, G2 = ols_cr1(X, y, g2)
    both = np.char.add(np.char.add(np.asarray(g1).astype(str), '|'), np.asarray(g2).astype(str))
    _, V12, _ = ols_cr1(X, y, both)
    V = V1 + V2 - V12
    w, U = np.linalg.eigh((V + V.T) / 2)
    V = (U * np.clip(w, 0, None)) @ U.T
    return b, V, min(G1, G2)


def council_fe_demean(X, y, g):
    """Within-council transform (singleton councils dropped). Returns Xd, yd, council codes, n kept."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    c = _codes(g)
    keep = np.bincount(c)[c] >= 2
    X, y, c = X[keep], y[keep], _codes(c[keep])
    cnt = np.bincount(c)

    def dm(a):
        a = np.atleast_2d(a.T).T
        means = np.array([np.bincount(c, weights=a[:, j]) / cnt for j in range(a.shape[1])]).T
        return a - means[c]
    return dm(X), dm(y).ravel(), c, int(keep.sum())


def glm_fit(X, y):
    import statsmodels.api as sm
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        m = sm.GLM(np.asarray(y, float), np.asarray(X, float), family=sm.families.Binomial()).fit()
    return np.asarray(m.params)


def mixed_fit(X, y, g):
    import statsmodels.api as sm
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        m = sm.MixedLM(np.asarray(y, float), np.asarray(X, float), groups=_codes(g)).fit(reml=True, method=['lbfgs'])
    return np.asarray(m.fe_params), bool(m.converged), float(np.asarray(m.cov_re).ravel()[0])


def mixed_crossed(X, y, council, fire):
    """Linear mixed model with crossed random intercepts for council and fire (variance components in one group).
    Model-based (Wald) covariance."""
    import statsmodels.api as sm
    n, k = X.shape
    cc, ff = _codes(council), _codes(fire)
    Zc = np.eye(cc.max() + 1)[cc]
    Zf = np.eye(ff.max() + 1)[ff]
    from statsmodels.regression.mixed_linear_model import VCSpec
    vc = VCSpec(names=['council', 'fire'],
                colnames=[[list(map(str, range(Zc.shape[1])))], [list(map(str, range(Zf.shape[1])))]],
                mats=[[Zc], [Zf]])
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        m = sm.MixedLM(np.asarray(y, float), np.asarray(X, float), groups=np.zeros(n, int), exog_vc=vc).fit(
            reml=True, method=['lbfgs'])
    return (np.asarray(m.fe_params), np.asarray(m.cov_params())[:k, :k], bool(m.converged),
            [float(v) for v in m.vcomp])


def ci(b, V, dof, alpha=0.05):
    b = np.asarray(b, float)
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    t = stats.t.ppf(1 - alpha / 2, dof)
    p = 2 * stats.t.sf(np.abs(b / np.where(se > 0, se, np.nan)), dof)
    return se, b - t * se, b + t * se, p


def holm(p):
    """Holm step-down adjusted p-values."""
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * p[i])
        adj[i] = min(1.0, run)
    return adj
