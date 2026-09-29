"""Shuffled-Y and planted-effect sanity check for the all-rows continuous analysis (same spirit as Experiment 6 power_check.py).

=====================================================================================================================
PRE-SPECIFICATION v2  (fixed and hash-locked in results/PRESPEC_LOCK.txt; this script runs BEFORE the real fits)
v2 replaces v1 (results/sanity_v1/, PRESPEC_LOCK_v1.txt): same scenarios, primary model and inference now as in
allrows_continuous.py v2 (event dummies, delete-one-council jackknife). See AMENDMENT LOG there.
=====================================================================================================================
Purpose: show the method (M1 in allrows_continuous.py: rank-normal OLS, block x size interactions, event-stratum dummies,
  jackknife council-cluster CIs with t(G-1)) is calibrated and can find an effect if one exists, using the real X (the
  same 218 rows, blocks, size and event strata) and a FAKE Y. It never fits the real Y to X. Target Y only; both samples
  (all rows, and without Black Summer). Fake Y is standardised (mean 0, SD 1) in every simulation. Coefficients are those
  of M1 (b_H..b_F, g_H..g_F) plus the omnibus test that the four g_B are all 0 ("omnibus_g", F with 4, G-1 df).
  Two model variants are simulated: M1_primary (with event dummies) and M1_noevent (without; shown for comparison only).
  Leave-out fits use the closed-form CR3 (identical to actual refits for full-rank designs; checked in a unit test).

NULL SCENARIOS (no block effect of any kind; 2,000 simulations each)
  null_stratum  real T* shuffled between rows inside a stratum (Black Summer rows among themselves; every other row among
                rows of the same start year). Keeps Y's spread and its Black Summer / year level shifts, destroys any
                link between blocks and Y within stratum. (The early Experiment 6 version that shuffled within fire only
                leaked real signal; do not use that.)
  null_full     real T* shuffled over all 218 rows (no structure at all).
  null_council  T* = sqrt(icc)*u_council + sqrt(1-icc)*e, u and e iid N(0,1); icc = one-way ANOVA intra-council
                correlation of the real T* (uses Y only, no X). A stress test of the council-cluster SE with
                council-persistent noise.
  Readout: two-sided false-alarm rate (95% CI excludes 0; omnibus p < 0.05) per coefficient, nominal 5%.
  Pass: every coefficient within 2-8% in each null scenario and both samples (Monte-Carlo SE about 0.5%). A coefficient
  above 10% is FLAGGED and its finding cannot be labelled SUPPORTED. The stratum shuffle keeps between-event Y
  differences, so a high false-alarm rate there, as seen without event dummies in v1, means the model attributes event
  differences to blocks.

PLANTED EFFECTS (1,000 simulations per cell; fake Y = shuffled-within-stratum T*, then an effect is added)
  int      pure interaction on block B in {H,E,V,F}: Y* = sqrt(1-rho^2)*z(shuffled) + rho*z(z_B * s),
           rho in {0.05, 0.10, 0.15, 0.20, 0.30}. The implied true g_B = rho / sd(z_B * s) is reported (SD of target per SD
           of block per SD of size); all other coefficients are truly 0.
  thr      threshold effect on V and on F: rows with share >= 5% get Y* = sqrt(1-r^2)*z(shuffled) + r*z_L(block)
           (z_L = standardised within those rows), all other rows keep the shuffled Y; r in {0.2, 0.4, 0.6}. r = 0.6 is
           about the size of the Experiment 6 +0.58. Tests whether a continuous-interaction model can see a
           threshold-shaped effect (event dummies absorb part of it because 30 of the 38 large-fire rows are Black Summer).
  main     constant effect on V and on F for all rows, no interaction: Y* = sqrt(1-r^2)*z(shuffled) + r*z(block),
           r in {0.2, 0.3, 0.4}. Readout: power for b_B, and the false-alarm rate of g_B when the true effect does not
           depend on size (should stay near 5%).
  Readouts per coefficient, sample and variant: mean estimate, two-sided rejection rate, power with the planted
  (positive) sign ("CI excludes 0 above"), and for the g_B the power after Holm across the four g_B (the actual
  decision rule B). Bias check: mean estimated g_B / implied g_B in int scenarios (aim 0.8-1.2 in the all-rows sample).
  Reported for reading a null: the smallest implied g_B detected at 80% power (linear interpolation over rho), with and
  without Holm, per block, sample and variant (SANITY_MDE.csv), and the omnibus power in the int scenarios.
  Limits stated in advance: the fake Y has no council-persistent signal except in null_council; the planted effects are
  single-block; power for the without-Black-Summer sample refers to the same planted DGP, whose effect is diluted there;
  GLM, mixed, two-way and bootstrap checks in allrows_continuous.py are not simulated here.
Seed: SEED = 20260930.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import BLOCKS, RES, design, holm, load, ols_cr3_multi, prep_cr3, verify_lock

SEED = 20260930
N_NULL = 2000
N_SIM = 1000
RHOS = [0.05, 0.10, 0.15, 0.20, 0.30]
THR_R = [0.2, 0.4, 0.6]
MAIN_R = [0.2, 0.3, 0.4]
TERMS = [f'b_{b}' for b in BLOCKS] + [f'g_{b}' for b in BLOCKS]


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
        self.T = d.t_Y.to_numpy()
        self.council = d.council.to_numpy()
        self.bs = d.bs.to_numpy()
        self.strata = d.stratum.to_numpy()
        self.samples = {'all': np.ones(len(d), bool), 'excl_BS': ~self.bs}
        self.names = list(design(d, 'log_share', events=False).columns)
        self.X_plain = design(d, 'log_share', events=False).to_numpy()      # for planting (no event columns)
        self.ib = [self.names.index(b) for b in BLOCKS]
        self.ig = [self.names.index(f'{b}:size') for b in BLOCKS]
        self.variants = {}
        for vname, ev in [('M1_primary', True), ('M1_noevent', False)]:
            for s, m in self.samples.items():
                X = design(d[m], 'log_share', events=ev).to_numpy()
                self.variants[(vname, s)] = (X, prep_cr3(X, self.council[m]), m)

    def fit(self, Y):
        """Y: (N x m). Returns {(variant, sample): dict of arrays}."""
        out = {}
        idx = self.ib + self.ig
        for (v, s), (X, prep, m) in self.variants.items():
            B, se, G, D = ols_cr3_multi(X, Y[m], prep, want_D=True)
            dof = G - 1
            p = 2 * stats.t.sf(np.abs(B[idx] / se[idx]), dof)
            # omnibus on the four g_B
            Dg = D[:, self.ig, :]                                               # (G, 4, m)
            Vg = (G - 1) / G * np.einsum('gim,gjm->mij', Dg, Dg)                # (m, 4, 4)
            bg = B[self.ig].T                                                   # (m, 4)
            W = np.einsum('mi,mij,mj->m', bg, np.linalg.pinv(Vg), bg)
            p_om = stats.f.sf(W / 4, 4, dof)
            out[(v, s)] = dict(B=B[idx], p=p, p_om=p_om)
        return out


def holm_multi(P):
    adj = np.empty_like(P)
    for j in range(P.shape[1]):
        adj[:, j] = holm(P[:, j])
    return adj


def summarise(fits, scenario, planted, strength, implied_g, nsim):
    rows = []
    for (v, s), r in fits.items():
        B, p = r['B'], r['p']
        padj = holm_multi(p[4:])
        for i, term in enumerate(TERMS):
            sig = p[i] < 0.05
            row = dict(scenario=scenario, planted=planted, strength=strength, implied_g=implied_g, model=v, sample=s,
                       term=term, mean_est=float(B[i].mean()), rej_two_sided_pct=100 * float(sig.mean()),
                       power_pos_pct=100 * float((sig & (B[i] > 0)).mean()), sims=nsim)
            if i >= 4:
                row['power_pos_holm_pct'] = 100 * float(((padj[i - 4] < 0.05) & (B[i] > 0)).mean())
            rows.append(row)
        om = 100 * float((r['p_om'] < 0.05).mean())
        rows.append(dict(scenario=scenario, planted=planted, strength=strength, implied_g=implied_g, model=v, sample=s,
                         term='omnibus_g', mean_est=np.nan, rej_two_sided_pct=om, power_pos_pct=om, sims=nsim))
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
    for blk in BLOCKS:
        prod = S.X_plain[:, S.names.index(f'{blk}:size')]
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

    # ---- minimum detectable g at 80% power (linear interpolation over the rho grid; power at g = 0 is the null rate)
    mde = []
    for v in ['M1_primary', 'M1_noevent']:
        for blk in BLOCKS:
            for s in ['all', 'excl_BS']:
                sub = out[(out.scenario == 'int') & (out.planted == blk) & (out.model == v) & (out['sample'] == s) &
                          (out.term == f'g_{blk}')].sort_values('implied_g')
                nul = out[(out.scenario == 'null_stratum') & (out.model == v) & (out['sample'] == s) &
                          (out.term == f'g_{blk}')].iloc[0]
                g = np.r_[0.0, sub.implied_g.to_numpy()]
                for col, lab in [('power_pos_pct', 'unadjusted'), ('power_pos_holm_pct', 'Holm')]:
                    pw = np.r_[nul[col], sub[col].to_numpy()]
                    hit = np.flatnonzero(pw >= 80)
                    if len(hit) == 0:
                        val = np.nan
                    else:
                        k = hit[0]
                        val = g[k] if k == 0 else g[k - 1] + (80 - pw[k - 1]) * (g[k] - g[k - 1]) / (pw[k] - pw[k - 1])
                    mde.append(dict(model=v, block=blk, sample=s, rule=lab, mde_g_80pct_power=val,
                                    power_at_largest_rho_pct=float(sub[col].iloc[-1]),
                                    largest_implied_g=float(sub.implied_g.iloc[-1])))
    mde = pd.DataFrame(mde)
    mde.to_csv(RES / 'SANITY_MDE.csv', index=False)
    print(mde.to_string())
    nul = out[out.scenario.str.startswith('null') & (out.model == 'M1_primary')]
    print('\nNULL false-alarm rates, M1_primary (two-sided %, nominal 5):')
    print(nul.pivot_table(index=['scenario', 'sample'], columns='term', values='rej_two_sided_pct').round(1).to_string())
    nul = out[out.scenario.str.startswith('null') & (out.model == 'M1_noevent')]
    print('\nNULL false-alarm rates, M1_noevent (for comparison):')
    print(nul.pivot_table(index=['scenario', 'sample'], columns='term', values='rej_two_sided_pct').round(1).to_string())


if __name__ == '__main__':
    main()
