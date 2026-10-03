# Experiment 19: is the FP null an aggregation artefact? Is composite Y just DL? (PRESPEC, 3 Oct 2026)

Fixed before any result is seen. Hash in LOCK.txt. Changes after locking are listed as deviations.

## Questions
Q1. The FP pillar is not predicted (Exp 18: RF season-out rho -0.09), yet council grants per resident rise with fire
size for 3 years (Exp 11: rho +0.42 at FY+3). Is the FP signal lost by averaging grants with weaker FP indicators?
Q2. Is the composite Y (rho +0.43) carried by the DL pillar alone?

## Data and code (unchanged)
- Table: Experiment 18_hybrid/pipeline/results/ANALYSIS_TABLE_exp14_copy.csv (218 rows).
- Code: Experiment 18_hybrid/pipeline (data.py pillars/composite; run_models.py cv_run, metrics), imported, not edited.
- X = PRE+FIRE; leave-one-fire-season-out CV; models mean, ridge, size_line, rf; council-cluster bootstrap (2000).
- Seed 20261002 (config). Rows with a missing target are dropped for that target (missing stays missing).

## Targets
0. Reproduction check: Y_v4 and FP must reproduce Exp 18 MODEL_METRICS rf/season rho to 1e-6.
1. FP1_main: grants per resident, excess change, mean of FY+1..FY+3 (percentile rank, sign as config).
2. FP1_h3: same, FY+3 only.
3. FP4_main: cash drawdown (rank, sign as config).
4. FP_grants: mean of the ranks of FP1 and FP2 (fire-related grant share) where present.
5. Y_noDL: composite of IL, FP, SL with DL removed (same weights, re-normalised).

## Pre-set readings (rf, season CV, 95% CI)
- Q1 "aggregation artefact" if FP1_main (primary) has CI lower bound > 0. If it does not, the reading is "FP is not
  predictable from X even when restricted to grants". FP1_h3, FP4_main, FP_grants are secondary, reported without
  a verdict of their own.
- Q2 "composite is carried by DL" if Y_noDL CI includes 0. If CI lower bound > 0, the composite has signal beyond DL.
- Descriptive bridge (no verdict): Spearman of each target with log_homes_in_fire_per_1000 on all rows present.
- 5 targets, no multiplicity correction; the primary tests are FP1_main (Q1) and Y_noDL (Q2).
