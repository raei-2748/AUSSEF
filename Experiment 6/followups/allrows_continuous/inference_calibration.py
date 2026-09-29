"""Calibration of candidate inference procedures on FAKE Y only (added after the first sanity run, before any real fit).

Why this exists: the locked v1 sanity check (results/sanity_v1/) found that CR1 cluster-robust t intervals reject a true
null 6-12% of the time (nominal 5%) even when Y is shuffled over all rows, and that the within-stratum shuffle leaves
between-event structure in Y that leaks into some coefficients. Before touching the real Y, candidate fixes are compared
here on the same fake-Y scenarios. Real Y is used only through its marginal distribution (shuffles) and its intra-council
correlation (null_council); no real Y-X relation is computed.

Candidates
  cr1     CR1 variance, t(G-1)                         (the v1 method)
  cr3     delete-one-council jackknife (CR3) variance around the full-sample estimate, t(G-1)
Model variants
  M1      as pre-specified
  M1+ev   M1 plus event-stratum fixed effects: a Black Summer indicator and one dummy per start year of the other fires
          (in the sample without Black Summer only the year dummies)
Scenarios: null_full, null_council, null_stratum (as in sanity_check.py), 2,000 simulations each.
Output: results/sanity_v1/INFERENCE_CALIBRATION.csv (two-sided false-alarm % per coefficient) and a printed table.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import BLOCKS, RES, _codes, design, load
from sanity_check import N_NULL, SEED, Setup, icc_anova, shuffle_strata, zcols


def prep_cr3(X, g):
    A = np.linalg.pinv(X.T @ X)
    c = _codes(g)
    out = []
    for k in range(c.max() + 1):
        idx = np.flatnonzero(c == k)
        Xg = X[idx]
        M = np.linalg.pinv(np.eye(len(idx)) - Xg @ A @ Xg.T)
        out.append((idx, A @ Xg.T @ M))
    return A, out


def fit_methods(X, Y, g, prep):
    """Return {method: (B, p)} for all coefficients; Y is N x m."""
    n, k = X.shape
    A, groups = prep
    B = A @ X.T @ Y
    E = Y - X @ B
    G = len(groups)
    dof = G - 1
    # CR1
    c = _codes(g)
    M = np.zeros((G, n))
    M[c, np.arange(n)] = 1.0
    m = Y.shape[1]
    XE = (X[:, :, None] * E[:, None, :]).reshape(n, k * m)
    S = (M @ XE).reshape(G, k, m)
    Z = np.einsum('jl,glm->jgm', A, S)
    se1 = np.sqrt(G / (G - 1) * (n - 1) / (n - k) * (Z ** 2).sum(axis=1))
    # CR3
    D = np.zeros((G, k, m))
    for i, (idx, W) in enumerate(groups):
        D[i] = W @ E[idx]
    se3 = np.sqrt((G - 1) / G * (D ** 2).sum(axis=0))
    res = {}
    for name, se in [('cr1', se1), ('cr3', se3)]:
        res[name] = (B, 2 * stats.t.sf(np.abs(B / se), dof))
    return res


def event_dummies(d, mask):
    sub = d[mask]
    lab = np.where(sub.bs, 'BS', sub.year.astype(str))
    lv = [v for v in np.unique(lab)]
    drop = lv[0]                                            # reference stratum
    cols = {f'ev_{v}': (lab == v).astype(float) for v in lv if v != drop}
    return pd.DataFrame(cols, index=sub.index)


def main():
    S = Setup()
    d = S.d
    rng = np.random.default_rng(SEED + 1)
    T, N = S.T, len(S.T)
    idx8 = S.ib + S.ig
    terms = [f'b_{b}' for b in BLOCKS] + [f'g_{b}' for b in BLOCKS]
    designs = {}
    for s, m in S.samples.items():
        X = S.X[m]
        ev = event_dummies(d, m).to_numpy()
        # drop constant / collinear dummy columns
        keepc = [j for j in range(ev.shape[1]) if ev[:, j].sum() > 0]
        Xe = np.column_stack([X, ev[:, keepc]])
        designs[(s, 'M1')] = (X, prep_cr3(X, S.council[m]), m)
        designs[(s, 'M1+ev')] = (Xe, prep_cr3(Xe, S.council[m]), m)
        print(s, 'event dummies', len(keepc), 'rows per stratum',
              pd.Series(np.where(d[m].bs, 'BS', d[m].year.astype(str))).value_counts().to_dict())
    icc = icc_anova(T, S.council)
    codes = _codes(S.council)
    scen = {
        'null_full': zcols(np.column_stack([T[rng.permutation(N)] for _ in range(N_NULL)])),
        'null_council': zcols(np.sqrt(icc) * rng.standard_normal((codes.max() + 1, N_NULL))[codes] +
                              np.sqrt(1 - icc) * rng.standard_normal((N, N_NULL))),
        'null_stratum': zcols(shuffle_strata(T, S.strata, N_NULL, rng)),
    }
    rows = []
    for sname, Y in scen.items():
        for (s, mv), (X, prep, m) in designs.items():
            res = fit_methods(X, Y[m], S.council[m], prep)
            for meth, (B, p) in res.items():
                for i, term in zip(idx8, terms):
                    rows.append(dict(scenario=sname, sample=s, model=mv, method=meth, term=term,
                                     false_alarm_pct=100 * float((p[i] < 0.05).mean())))
    out = pd.DataFrame(rows)
    out.to_csv(RES / 'sanity_v1' / 'INFERENCE_CALIBRATION.csv', index=False)
    for mv in ['M1', 'M1+ev']:
        for meth in ['cr1', 'cr3']:
            sub = out[(out.model == mv) & (out.method == meth)]
            print(f'\n=== {mv}, {meth}: two-sided false-alarm % (nominal 5) ===')
            print(sub.pivot_table(index=['scenario', 'sample'], columns='term', values='false_alarm_pct').round(1).to_string())


if __name__ == '__main__':
    main()
