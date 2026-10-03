# Experiment 19 FINDINGS (3 Oct 2026)
Rules: PRESPEC.md (LOCK.txt, locked before running). Numbers: results/METRICS.csv, BRIDGE.csv, posthoc_noDL.txt.
RF, PRE+FIRE X, leave-one-fire-season-out, council-cluster bootstrap 95% CI.

## Deviation
D1. Reproduction tolerance not met: Y_v4 rho 0.432044 vs Exp 18 0.431853; FP -0.094868 vs -0.094703 (diff < 2e-4,
not < 1e-6). Cause: run on Linux/Python 3.12 via uv instead of the Mac environment (RF floating-point and library
differences). No reading changes at this size.

## Q1. Is the FP null an aggregation artefact? Pre-set reading: NOT SUPPORTED.
| Target | rows | seasons | RF rho [95% CI] | rho with homes in fire (all rows, descriptive) |
|---|---|---|---|---|
| FP pillar (Exp 18) | 199 | 8 | -0.09 [-0.32, +0.13] | +0.24 |
| **FP1 grants per resident, FY+1..3 (primary)** | 199 | 8 | **+0.16 [-0.08, +0.36]** | +0.25 |
| FP1 grants, FY+3 only (secondary) | 134 | 6 | +0.36 [+0.06, +0.58] | +0.35 |
| FP4 cash drawdown (secondary) | 199 | 8 | -0.19 [-0.39, +0.04] | +0.04 |
| FP grants (FP1+FP2) (secondary) | 199 | 8 | +0.17 [-0.07, +0.37] | +0.28 |
- Removing cash drawdown moves the FP rho from -0.09 to +0.16, but the primary interval still includes 0.
- Cash drawdown (FP4) has no link with fire size (+0.04): it is the weak indicator.
- Year-3 grants are predicted (+0.36, CI above 0) on fewer rows and seasons; secondary, no verdict.
- Reading: grants rise with fire size within the data (+0.25 to +0.35), but predicting them in a fire season the
  model has not seen is not shown at the pre-set 3-year-mean window.

## Q2. Is composite Y carried by DL? Pre-set reading: NO, there is signal beyond DL.
- Y without DL: RF rho **+0.33 [+0.12, +0.49]**, 218 rows, 9 seasons (full Y: +0.43 [+0.27, +0.55]).
- POST-HOC (descriptive, not pre-registered): the indicators most linked to fire size outside DL are fire-related
  grant share (+0.52, 51 rows), deaths per 100k (+0.49, 140 rows), rents year 2 (+0.26) and grants per resident
  (+0.25). Each pillar alone is not predicted (Exp 18), so the non-DL signal is spread thinly across pillars.
- Caveat: the number of pillars present rises with fire size (+0.26), so which rows have data is itself linked to
  fire size. Not tested further.
