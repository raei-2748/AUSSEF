"""Shuffled-Y and planted-effect sanity check for the all-rows continuous analysis (same spirit as Experiment 6 power_check.py).

=====================================================================================================================
PRE-SPECIFICATION  (fixed and hash-locked in results/PRESPEC_LOCK.txt; this script runs BEFORE the real fits)
=====================================================================================================================
Purpose: show the method (M1 in allrows_continuous.py: rank-normal OLS, block x size interactions, council-cluster CR1
  CIs with t(G-1)) is calibrated and can find an effect if one exists, using the real X (the same 218 rows, blocks and
  size) and a FAKE Y. It never fits the real Y to X. Target Y only; both samples (all rows, and without Black Summer).
  Fake Y is standardised (mean 0, SD 1) in every simulation. Coefficients are those of M1 (b_H..b_F, g_H..g_F).

NULL SCENARIOS (no block effect of any kind; 2,000 simulations each)
  null_stratum  real T* shuffled between rows inside a stratum (Black Summer rows among themselves; every other row among
                rows of the same start year). Keeps Y's spread and its Black Summer / year level shifts, destroys any
                link between blocks and Y within stratum. (The early Experiment 6 version that shuffled within fire only
                leaked real signal; do not use that.)
  null_full     real T* shuffled over all 218 rows (no structure at all).
  null_council  T* = sqrt(icc)*u_council + sqrt(1-icc)*e, u and e iid N(0,1); icc = one-way ANOVA intra-council
                correlation of the real T* (uses Y only, no X). A stress test of the council-cluster SE with
                council-persistent noise.
  Readout: two-sided false-alarm rate (95% CI excludes 0) per coefficient, nominal 5%.
  Pass: every coefficient within 2-8% in each null scenario. A coefficient above 10% is FLAGGED and its finding cannot be
  labelled SUPPORTED. The stratum shuffle keeps between-stratum Y differences, so a high false-alarm rate on a block main
  effect b_B in the all-rows sample there is a real warning about Black Summer confounding, reported as such.

PLANTED EFFECTS (1,000 simulations per cell; fake Y = shuffled-within-stratum T*, then an effect is added)
  int      pure interaction on block B in {H,E,V,F}: Y* = sqrt(1-rho^2)*z(shuffled) + rho*z(z_B * s),
           rho in {0.05, 0.10, 0.15, 0.20, 0.30}. The implied true g_B = rho / sd(z_B * s) is reported (SD of target per SD
           of block per SD of size), all other coefficients are truly 0.
  thr      threshold effect on V and on F: rows with share >= 5% get Y* = sqrt(1-r^2)*z(shuffled) + r*z_L(block)
           (z_L = standardised within those rows), all other rows keep the shuffled Y; r in {0.2, 0.4, 0.6}. r = 0.6 is
           about the size of the Experiment 6 +0.58. Tests whether a continuous-interaction model can see a
           threshold-shaped effect.
  main     constant effect on V and on F for all rows, no interaction: Y* = sqrt(1-r^2)*z(shuffled) + r*z(block),
           r in {0.2, 0.3, 0.4}. Readout: power for b_B, and the false-alarm rate of g_B when the true effect does not
           depend on size (should stay near 5%).
  Readouts per coefficient and sample: mean estimate, two-sided rejection rate, power with the planted (positive) sign
  ("CI excludes 0 above"), and for the g_B the power after Holm across the four g_B (the actual decision rule B).
  Bias check: mean estimated g_B / implied g_B in int scenarios (aim 0.8-1.2 in the all-rows sample).
  Reported for reading a null: the smallest implied g_B detected at 80% power (linear interpolation over rho), with and
  without Holm, per block and sample.
  Limits stated in advance: the fake Y has no council-persistent signal except in null_council; the planted effects are
  single-block; power for the without-Black-Summer sample refers to the same planted DGP, whose effect is diluted there.
Seed: SEED = 20260930.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import BLOCKS, RES, design, holm, load, ols_cr1_multi, verify_lock

SEED = 20260930
N_NULL = 2000
N_SIM = 1000
RHOS = [0.05, 0.10, 0.15, 0.20, 0.30]
THR_R = [0.2, 0.4, 0.6]
MAIN_R = [0.2, 0.3, 0.4]


def zcols(A):
    return (A - A.mean(axis=0)) / A.std(axis=0, ddof=1)


def shuffle_strata(T, strata, nsim, rng):
    out = np.empty((len(T), nsim))
    groups = [np.flatnonzero(strata == k) for k in np.unique(strata)]
    for j in range(nsim):
        for g in groups:
            out[g, j] = T[rng.permutation(g)]
    return out


def icc_anova(T, cl):
    codes = pd.factorize(cl)[0]
    G = codes.max() + 1
    n_i = np.bincount(codes)
    N = len(T)
    means = np.bincount(codes, weights=T) / n_i
    grand = T.mean()
    msb = (n_i * (means - grand) ** 2).sum() / (G - 1)
    msw = ((T - means[codes]) ** 2).sum() / (N - G)
    n0 = (N - (n_i ** 2).sum() / N) / (G - 1)
    return max(0.0, (msb - msw) / (msb + (n0 - 1) * msw))


class Setup:
    def __init__(self):
        d = load()
        self.d = d
        X = design(d, 'log_share')
        self.names = list(X.columns)
        self.X = X.to_numpy()
        self.T = d.t_Y.to_numpy()
        self.council = d.council.to_numpy()
        self.bs = d.bs.to_numpy()
        self.strata = np.where(self.bs, 'BS', d.year.astype(str).to_numpy())
        self.ib = [self.names.index(b) for b in BLOCKS]
        self.ig = [self.names.index(f'{b}:size') for b in BLOCKS]
        self.samples = {'all': np.ones(len(d), bool), 'excl_BS': ~self.bs}

    def fit(self, Y):
        """Y: (N x m). Returns {sample: (B, p, lo, hi)} for the 8 coefficients (b_H..b_F, g_H..g_F)."""
        out = {}
        for s, m in self.samples.items():
            B, se, G = ols_cr1_multi(self.X[m], Y[m], self.council[m])
            dof = G - 1
            tc = stats.t.ppf(0.975, dof)
            idx = self.ib + self.ig
            B, se = B[idx], se[idx]
            p = 2 * stats.t.sf(np.abs(B / se), dof)
            out[s] = (B, p, B - tc * se, B + tc * se)
        return out


TERMS = [f'b_{b}' for b in BLOCKS] + [f'g_{b}' for b in BLOCKS]


def holm_multi(P):
    """P: (4 x m) p-values -> Holm-adjusted, column by column."""
    adj = np.empty_like(P)
    for j in range(P.shape[1]):
        adj[:, j] = holm(P[:, j])
    return adj


def summarise(fits, scenario, planted, strength, implied_g, nsim):
    rows = []
    for s, (B, p, lo, hi) in fits.items():
        padj = holm_multi(p[4:])
        for i, term in enumerate(TERMS):
            sig = p[i] < 0.05
            r = dict(scenario=scenario, planted=planted, strength=strength, implied_g=implied_g, sample=s, term=term,
                     mean_est=float(B[i].mean()), rej_two_sided_pct=100 * float(sig.mean()),
                     power_pos_pct=100 * float((sig & (B[i] > 0)).mean()), sims=nsim)
            if i >= 4:
                r['power_pos_holm_pct'] = 100 * float(((padj[i - 4] < 0.05) & (B[i] > 0)).mean())
            rows.append(r)
    return rows


def main():
    verify_lock(__file__)
    S = Setup()
    rng = np.random.default_rng(SEED)
    T, N = S.T, len(S.T)
    rows = []
    t0 = time.time()

    # ---- nulls
    Y = zcols(shuffle_strata(T, S.strata, N_NULL, rng))
    rows += summarise(S.fit(Y), 'null_stratum', '', 0.0, np.nan, N_NULL)
    Y = zcols(np.column_stack([T[rng.permutation(N)] for _ in range(N_NULL)]))
    rows += summarise(S.fit(Y), 'null_full', '', 0.0, np.nan, N_NULL)
    icc = icc_anova(T, S.council)
    codes = pd.factorize(S.council)[0]
    u = rng.standard_normal((codes.max() + 1, N_NULL))[codes]
    Y = zcols(np.sqrt(icc) * u + np.sqrt(1 - icc) * rng.standard_normal((N, N_NULL)))
    rows += summarise(S.fit(Y), 'null_council', f'icc={icc:.3f}', 0.0, np.nan, N_NULL)
    print(f'nulls done {time.time() - t0:.0f}s; ICC of real T* by council = {icc:.3f}', flush=True)

    # ---- planted effects: shuffled-within-stratum base
    base = zcols(shuffle_strata(T, S.strata, N_SIM, rng))
    s_col = S.X[:, S.names.index('size')]
    for blk in BLOCKS:
        prod = S.X[:, S.names.index(f'{blk}:size')]
        sd = prod.std(ddof=1)
        zp = (prod - prod.mean()) / sd
        for rho in RHOS:
            Y = np.sqrt(1 - rho ** 2) * base + rho * zp[:, None]
            rows += summarise(S.fit(Y), 'int', blk, rho, rho / sd, N_SIM)
    print(f'int done {time.time() - t0:.0f}s', flush=True)

    big = (S.d.share >= 0.05).to_numpy()
    for blk in ['V', 'F']:
        zb = S.d['z_' + blk].to_numpy()
        zl = zb.copy()
        zl[big] = (zb[big] - zb[big].mean()) / zb[big].std(ddof=1)
        for r in THR_R:
            Y = base.copy()
            Y[big] = np.sqrt(1 - r ** 2) * base[big] + r * zl[big][:, None]
            rows += summarise(S.fit(Y), 'thr', blk, r, np.nan, N_SIM)
        for r in MAIN_R:
            Y = np.sqrt(1 - r ** 2) * base + r * ((zb - zb.mean()) / zb.std(ddof=1))[:, None]
            rows += summarise(S.fit(Y), 'main', blk, r, np.nan, N_SIM)
    print(f'thr/main done {time.time() - t0:.0f}s', flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(RES / 'SANITY_CHECK.csv', index=False)

    # ---- minimum detectable g at 80% power (linear interpolation over the rho grid)
    mde = []
    for blk in BLOCKS:
        for s in ['all', 'excl_BS']:
            sub = out[(out.scenario == 'int') & (out.planted == blk) & (out['sample'] == s) & (out.term == f'g_{blk}')]
            sub = sub.sort_values('implied_g')
            g = np.r_[0.0, sub.implied_g.to_numpy()]
            for col, lab in [('power_pos_pct', 'unadjusted'), ('power_pos_holm_pct', 'Holm')]:
                pw = np.r_[float(out[(out.scenario == 'null_stratum') & (out['sample'] == s) &
                                    (out.term == f'g_{blk}')][col].iloc[0]) if col in out else 0.0,
                           sub[col].to_numpy()]
                pw = np.nan_to_num(pw)
                hit = np.flatnonzero(pw >= 80)
                if len(hit) == 0:
                    v = np.nan
                else:
                    k = hit[0]
                    v = g[k] if k == 0 else g[k - 1] + (80 - pw[k - 1]) * (g[k] - g[k - 1]) / (pw[k] - pw[k - 1])
                mde.append(dict(block=blk, sample=s, rule=lab, mde_g_80pct_power=v))
    pd.DataFrame(mde).to_csv(RES / 'SANITY_MDE.csv', index=False)
    print(pd.DataFrame(mde).to_string())
    nul = out[out.scenario.str.startswith('null')]
    print('\nNULL false-alarm rates (two-sided %, nominal 5):')
    print(nul.pivot_table(index=['scenario', 'sample'], columns='term', values='rej_two_sided_pct').round(1).to_string())


if __name__ == '__main__':
    main()
