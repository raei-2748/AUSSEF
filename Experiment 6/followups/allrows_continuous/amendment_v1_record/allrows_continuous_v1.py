"""All-rows continuous analysis (Experiment 6 follow-up): does the pre-fire score's link to impact grow with fire size?

=====================================================================================================================
PRE-SPECIFICATION  (fixed and hash-locked in results/PRESPEC_LOCK.txt BEFORE any model was fitted to the real Y)
=====================================================================================================================

QUESTION
  Experiment 6 built a pre-fire council score from four blocks: H hazard, E exposure (v2, share of housing in bush-prone
  land), V vulnerability, F fiscal. On fires burning >= 5% of a council (38 of 218 rows, 30 of them Black Summer) V
  correlated +0.58 with impact Y, on all rows +0.25. Cut-off subsets throw rows away and depend on the threshold. Here ALL
  218 rows are used, burned share enters as a continuous term, and each block is interacted with it:
  does the effect of H / E / V / F on impact grow with fire size?

STATUS OF THE EVIDENCE (declared up front)
  Not blind. These are the same 218 rows on which Experiment 6 already saw V rise with fire size, so "V's effect grows
  with size" is a hypothesis that came from these data. This analysis re-tests it without a threshold and with all rows;
  it is NOT an independent confirmation. No new fires, no new data, no new sources. Before this header was locked only
  X-side facts were looked at (results/DESIGN_DIAGNOSTICS.txt: counts, clusters, collinearity, missingness) and the
  marginal spread of size. No relation between any Y-type column and anything else was computed.

DATA
  inputs/ROWS_WITH_SCORE_v2.csv (copy of Experiment 6 results; sha256 in results/INPUT_SHA256.txt): 218 council x fire
  rows, 96 fires, 69 councils; Black Summer (AGRN 871) = 50 rows, 168 rows without it (54 councils).
  Targets: Y (composite; PRIMARY, 218 rows) and the pillars DL (90 rows), IL (218), FP (199), SL (213).
  Non-missing rows are used for each target; nothing is imputed.

VARIABLES
  target   T* = Blom rank-normal score of the target over ITS non-missing rows in the full sample, standardised to SD 1.
           The same T* values are used in the excluding-Black-Summer run (transform is not redone on the subset).
  blocks   z_H, z_E, z_V, z_F = each block score standardised over the 218 rows (SD 1); 1 = worse.
  size     PRIMARY  s = log10(max(share, 1e-4)), standardised over the 218 rows. share = fraction of the council burned.
           (12 rows burned < 0.01% of a council, min 3e-7; the floor stops that left tail from dominating. Fixed from the X
            side only.) 1 SD of s is about a 10-fold change in share; a 5% share sits at about +0.9 SD.
           CHECKS   share (raw, standardised) | rank of share (percentile, standardised) | log10(max(burn_ha, 1)),
            standardised | step: 1[share >= 5%] (bridge to Experiment 6 only; not in the support rule).
  All standardisations use the 218 rows, also in subset runs, so coefficients are comparable across runs.
  Units: a coefficient is SD of the target per SD of the predictor.

MODELS (all with council as the cluster, the unit that repeats: 69 councils, 43 with 2+ rows)
  M1 PRIMARY  OLS  T* = a + bs*s + sum_B b_B*z_B + sum_B g_B*(z_B*s) + e,   B in {H,E,V,F} jointly.
              b_B = effect of +1 SD of block B at an average-size fire; g_B = change in that effect per +1 SD of size.
              Inference: CR1 cluster-robust variance, 95% CI from t with G-1 df (G = councils in the sample).
              Also reported: cluster-robust omnibus Wald test that all four g_B = 0 (F with 4, G-1 df), and simple slopes
              b_B + g_B*s0 at share = 0.1%, 1%, 5%, 20% (delta method, same variance).
  Checks (rows listed as C1..C8; every one is also run on the sample without Black Summer):
    C1  M1 with each alternative size scale (raw share, rank of share, log burn_ha, step >= 5%).
    C2  one block at a time: T* = a + bs*s + b*z_B + g*(z_B*s), four separate models (marginal, not mutually adjusted).
    C3  fractional-logit GLM (binomial, logit link) on the RAW target in [0,1], same M1 design, council-cluster SE.
    C4  linear mixed model, random intercept per council (REML), M1 design; C4b (Y only) adds a crossed random intercept
        for fire, reported with its convergence flag.
    C5  two-way cluster-robust SE (council and fire; Cameron-Gelbach-Miller). Black Summer is one 50-row fire cluster.
    C6  council fixed effects: only within-council variation, so time-invariant council traits are removed; the block main
        effects drop out and g_B is identified from councils with 2+ fires.
    C7  council-pairs bootstrap (2,000 resamples of councils, percentile 95% CI) for M1.
    C8  the pre-specified composite score risk_add in place of the four blocks (score, score:size).
  C1, C3, C4 are run for all five targets; C2, C4b, C5, C6, C7, C8 for Y only.

MULTIPLICITY
  Family 1 (the question, target Y): the four g_B of M1 on all rows; Holm-adjusted p across those 4.
  Family 2 (secondary, pillars): the 16 g_B of M1 (4 pillars x 4 blocks) on all rows; Holm across the 16.
  b_B, simple slopes and every check are descriptive and carry no adjustment.

WHAT COUNTS AS SUPPORT for "the effect of block B grows with fire size" (positive g_B; block scores are oriented so 1 = worse)
  A  M1, all rows: g_B > 0 and its 95% cluster-robust CI excludes 0.
  B  Holm-adjusted p < 0.05 within the family.
  C  Size scale: g_B > 0 in all three alternative continuous scales and CI excludes 0 in at least two of them.
  D  Model class: g_B > 0 with CI excluding 0 in BOTH the fractional-logit GLM (C3) and the mixed model (C4).
  E  Black Summer: M1 without Black Summer has g_B > 0 with CI excluding 0.
  Verdict per block:  SUPPORTED = A-E.  BLACK-SUMMER-DEPENDENT = A-D hold, E fails.  SUGGESTIVE = A holds, B-D not all.
  NOT SUPPORTED = A fails.  A negative g_B with CI excluding 0 is reported as CONTRADICTED (the effect shrinks with size).
  A verdict cannot be SUPPORTED if sanity_check.py flags the coefficient (null false-alarm rate > 10% in any null
  scenario, either sample); it is then labelled "inference not validated".
  E is demanding: without Black Summer only 8 rows exceed 5% share, so a failure on E is weak evidence of dependence unless
  the planted-effect check (SANITY_CHECK.csv) shows that design had the power to see an effect of the observed size.
  Pillars use the same rule with their own Holm family; C uses the same scales, D the GLM and mixed model for that pillar.

NOTHING FOUND
  If no block reaches SUGGESTIVE or better, and the omnibus test on Y is not significant, the finding is reported as
  "no evidence that any block's effect grows with fire size in these data", with the 95% CIs and the smallest
  interaction the planted-effect check could detect at 80% power (so the null can be read for what it excludes).

NO TUNING
  Nothing above may change after results on the real Y are seen (no new transforms, blocks, subsets, size scales,
  estimators or thresholds). A code bug found later is fixed and logged under "Deviations" in FINDINGS.md; a bug fix must
  not alter any choice above. Outputs: results/ALLROWS_MODELS.csv (every coefficient of every model), OMNIBUS.csv,
  SIMPLE_SLOPES.csv, VERDICTS.csv. Seeds: SEED_BOOT = 20260929.
Run: python3 lock_prespec.py; python3 sanity_check.py; python3 allrows_continuous.py
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import (BLOCKS, CONT_SIZES, PILLARS, RES, ROOT, SHARES_FOR_SLOPES, TARGETS, ci, design, glm_fraclogit,
                     holm, load, mixed_crossed, mixed_ri, ols_cr1, ols_council_fe, ols_twoway, s_at_share,
                     verify_lock)

SEED_BOOT = 20260929
N_BOOT = 2000
INF = 1e9                                   # dof for Wald normal intervals
ALT_SIZES = ['share', 'rank_share', 'log_burn_ha']
DRY = None                                  # set by --dry: directory; Y is replaced by within-stratum shuffled Y


def term_label(nm):
    if nm in ('const', 'size'):
        return nm
    return ('g_' + nm.split(':')[0]) if ':' in nm else ('b_' + nm)


def tidy(target, sample, model, size, names, b, V, dof, n, G, **extra):
    se, lo, hi, p = ci(b, V, dof)
    return [dict(target=target, sample=sample, model=model, size=size, term=term_label(nm), est=b[j], se=se[j],
                 lo=lo[j], hi=hi[j], p=p[j], n=n, clusters=G, **extra) for j, nm in enumerate(names)]


def omnibus(b, V, names, G, blocks=BLOCKS):
    idx = [names.index(f'{x}:size') for x in blocks]
    W = float(b[idx] @ np.linalg.pinv(V[np.ix_(idx, idx)]) @ b[idx])
    F = W / len(idx)
    return F, float(stats.f.sf(F, len(idx), G - 1))


def slopes(target, sample, names, b, V, G, d_all):
    rows = []
    for blk in BLOCKS:
        ib, ig = names.index(blk), names.index(f'{blk}:size')
        for sh in SHARES_FOR_SLOPES:
            s0 = s_at_share(d_all, sh)
            est = b[ib] + s0 * b[ig]
            var = V[ib, ib] + s0 ** 2 * V[ig, ig] + 2 * s0 * V[ib, ig]
            se = np.sqrt(max(var, 0))
            t = stats.t.ppf(0.975, G - 1)
            rows.append(dict(target=target, sample=sample, block=blk, share=sh, s0=s0, est=est, se=se,
                             lo=est - t * se, hi=est + t * se))
    return rows


def boot_pairs(X, y, g, rng):
    codes = pd.factorize(np.asarray(g))[0]
    members = [np.flatnonzero(codes == k) for k in range(codes.max() + 1)]
    out = []
    for _ in range(N_BOOT):
        pick = rng.integers(0, len(members), len(members))
        idx = np.concatenate([members[i] for i in pick])
        out.append(np.linalg.lstsq(X[idx], y[idx], rcond=None)[0])
    out = np.array(out)
    return np.percentile(out, 2.5, axis=0), np.percentile(out, 97.5, axis=0)


def fit_sample(d, tgt, sample, rng, d_all):
    dd = d[d['t_' + tgt].notna()]
    if sample == 'excl_BS':
        dd = dd[~dd.bs]
    y, yraw, g, fire = dd['t_' + tgt].to_numpy(), dd[tgt].to_numpy(), dd.council.to_numpy(), dd.fire.to_numpy()
    n = len(dd)
    rows, om, sl, notes = [], [], [], []
    X = design(dd, 'log_share')
    names = list(X.columns)
    Xa = X.to_numpy()

    b, V, G = ols_cr1(Xa, y, g)                                              # M1
    rows += tidy(tgt, sample, 'M1_primary', 'log_share', names, b, V, G - 1, n, G)
    F, p = omnibus(b, V, names, G)
    om.append(dict(target=tgt, sample=sample, model='M1_primary', n=n, clusters=G, F=F, df1=4, df2=G - 1, p=p))
    sl += slopes(tgt, sample, names, b, V, G, d_all)

    for sz in ALT_SIZES + ['step5']:                                        # C1
        Xs = design(dd, sz)
        bb, VV, GG = ols_cr1(Xs.to_numpy(), y, g)
        rows += tidy(tgt, sample, 'C1_size_' + sz, sz, list(Xs.columns), bb, VV, GG - 1, n, GG)
        FF, pp = omnibus(bb, VV, list(Xs.columns), GG)
        om.append(dict(target=tgt, sample=sample, model='C1_size_' + sz, n=n, clusters=GG, F=FF, df1=4, df2=GG - 1, p=pp))

    bb, VV, GG, conv = glm_fraclogit(Xa, yraw, g)                            # C3
    rows += tidy(tgt, sample, 'C3_fraclogit', 'log_share', names, bb, VV, GG - 1, n, GG, converged=conv)
    bb, VV, conv, tau2 = mixed_ri(Xa, y, g)                                  # C4
    rows += tidy(tgt, sample, 'C4_mixed_ri', 'log_share', names, bb, VV, INF, n, G, converged=conv, council_var=tau2)

    if tgt == 'Y':
        for blk in BLOCKS:                                                   # C2
            X1 = design(dd, 'log_share', [blk])
            bb, VV, GG = ols_cr1(X1.to_numpy(), y, g)
            rows += tidy(tgt, sample, f'C2_one_block_{blk}', 'log_share', list(X1.columns), bb, VV, GG - 1, n, GG)
        try:                                                                 # C4b
            bb, VV, conv, vcomp = mixed_crossed(Xa, y, g, fire)
            rows += tidy(tgt, sample, 'C4b_mixed_crossed', 'log_share', names, bb, VV, INF, n, G, converged=conv,
                         council_var=vcomp[0], fire_var=vcomp[1])
        except Exception as e:                                               # reported, not hidden
            notes.append(f'C4b crossed mixed model failed on {sample}: {type(e).__name__}: {e}')
        bb, VV, GG2 = ols_twoway(Xa, y, g, fire)                             # C5
        rows += tidy(tgt, sample, 'C5_twoway_cluster', 'log_share', names, bb, VV, GG2 - 1, n, GG2)
        cols_fe = ['size'] + [f'{x}:size' for x in BLOCKS]                   # C6
        bb, VV, GG3, n_fe = ols_council_fe(X[cols_fe].to_numpy(), y, g)
        rows += tidy(tgt, sample, 'C6_council_FE', 'log_share', cols_fe, bb, VV, GG3 - 1, n_fe, GG3)
        lo, hi = boot_pairs(Xa, y, g, rng)                                   # C7
        b_all = np.linalg.lstsq(Xa, y, rcond=None)[0]
        rows += [dict(target=tgt, sample=sample, model='C7_pairs_bootstrap', size='log_share', term=term_label(nm),
                      est=b_all[j], se=np.nan, lo=lo[j], hi=hi[j], p=np.nan, n=n, clusters=G)
                 for j, nm in enumerate(names)]
        Xs = design(dd, 'log_share', ['risk_add'])                            # C8
        bb, VV, GG = ols_cr1(Xs.to_numpy(), y, g)
        rows += tidy(tgt, sample, 'C8_composite_score', 'log_share', list(Xs.columns), bb, VV, GG - 1, n, GG)
    return rows, om, sl, notes


def verdicts(res, om):
    m1 = res[(res.model == 'M1_primary') & (res['sample'] == 'all') & res.term.str.startswith('g_')].copy()
    m1['p_holm'] = np.nan
    yfam = m1.target == 'Y'
    m1.loc[yfam, 'p_holm'] = holm(m1.loc[yfam, 'p'].to_numpy())
    pil = m1.target != 'Y'
    m1.loc[pil, 'p_holm'] = holm(m1.loc[pil, 'p'].to_numpy())
    flags = {}
    sc = RES / 'SANITY_CHECK.csv'
    if sc.exists():
        s = pd.read_csv(sc)
        nul = s[s.scenario.str.startswith('null')]
        flags = nul.groupby('term').rej_two_sided_pct.max().to_dict()

    def get(model, tgt, sample, term):
        r = res[(res.model == model) & (res.target == tgt) & (res['sample'] == sample) & (res.term == term)]
        return r.iloc[0]

    def pos(r):
        return bool(r.est > 0 and r.lo > 0)
    out = []
    for _, r in m1.iterrows():
        tgt, term = r.target, r.term
        blk = term[2:]
        A = pos(r)
        B = bool(r.p_holm < 0.05)
        alts = [get('C1_size_' + z, tgt, 'all', term) for z in ALT_SIZES]
        Cc = all(a.est > 0 for a in alts) and sum(pos(a) for a in alts) >= 2
        Dd = pos(get('C3_fraclogit', tgt, 'all', term)) and pos(get('C4_mixed_ri', tgt, 'all', term))
        Ee = pos(get('M1_primary', tgt, 'excl_BS', term))
        contra = bool(r.est < 0 and r.hi < 0)
        flagged = bool(flags.get(term, 0) > 10)
        if contra:
            v = 'CONTRADICTED'
        elif not A:
            v = 'NOT SUPPORTED'
        elif A and B and Cc and Dd and Ee:
            v = 'SUPPORTED'
        elif A and Cc and Dd and not Ee:
            v = 'BLACK-SUMMER-DEPENDENT' if B else 'SUGGESTIVE'
        else:
            v = 'SUGGESTIVE'
        if flagged and v == 'SUPPORTED':
            v = 'inference not validated'
        exb = get('M1_primary', tgt, 'excl_BS', term)
        out.append(dict(target=tgt, block=blk, g_est=r.est, g_lo=r.lo, g_hi=r.hi, p=r.p, p_holm=r.p_holm,
                        A_ci_positive=A, B_holm=B, C_scale=Cc, D_model_class=Dd, E_excl_BS=Ee,
                        g_exclBS=exb.est, g_exclBS_lo=exb.lo, g_exclBS_hi=exb.hi,
                        null_false_alarm_max_pct=flags.get(term, np.nan), verdict=v))
    return pd.DataFrame(out)


def main():
    global DRY
    outdir = RES
    if '--dry' in sys.argv:
        DRY = Path(sys.argv[sys.argv.index('--dry') + 1])
        DRY.mkdir(parents=True, exist_ok=True)
        outdir = DRY
    else:
        verify_lock(__file__)
    d = load()
    if DRY:                                    # code test only: Y shuffled within stratum, real results untouched
        r0 = np.random.default_rng(1)
        strat = np.where(d.bs, 'BS', d.year.astype(str))
        for t in TARGETS:
            ok = d[t].notna().to_numpy()
            v = d[t].to_numpy().copy()
            for k in np.unique(strat):
                idx = np.flatnonzero((strat == k) & ok)
                v[idx] = v[r0.permutation(idx)]
            d[t] = v
        from arc_lib import rank_normal
        for t in TARGETS:
            d['t_' + t] = rank_normal(d[t])
    rng = np.random.default_rng(SEED_BOOT)
    rows, om, sl, notes = [], [], [], []
    t0 = time.time()
    for tgt in TARGETS:
        for sample in ['all', 'excl_BS']:
            r, o, s, nt = fit_sample(d, tgt, sample, rng, d)
            rows += r
            om += o
            sl += s
            notes += nt
            print(tgt, sample, f'{time.time() - t0:.0f}s', flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(outdir / 'ALLROWS_MODELS.csv', index=False)
    pd.DataFrame(om).to_csv(outdir / 'OMNIBUS.csv', index=False)
    pd.DataFrame(sl).to_csv(outdir / 'SIMPLE_SLOPES.csv', index=False)
    ver = verdicts(res, om)
    ver.to_csv(outdir / 'VERDICTS.csv', index=False)
    (outdir / 'RUN_NOTES.txt').write_text('\n'.join(notes) + '\n')
    for nt in notes:
        print('NOTE', nt)
    print(f'done, {len(res)} coefficient rows')


if __name__ == '__main__':
    main()
