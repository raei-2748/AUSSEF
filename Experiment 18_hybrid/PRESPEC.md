# Experiment 18 pre-specification: hybrid Indirect Loss (IL) pillar

Written 2 Oct 2026 (night), **before any modelled IL value, calibration or model fit is computed**. Hash-locked in
`LOCK.txt`. Later changes are numbered deviations in FINDINGS.md. Sources: `bibliography/parts/exp18_hybrid_2026-10-03.csv`
(E18-IO*, E18L*, E18-D*, E18P-*). Assumed values are marked **[assumed]**.

**Why.** In Y v4 the IL pillar barely tracks the fire (RF rho +0.09, Experiment 14). Measured local data (Experiments 7,
13) mostly say "not detected" with useful CIs. Plan: build a standard input-output (IO) estimate of IL, hold it to the
measured CIs, and use it only to fill the IL pillar. **The primary scientific result stays Y_measured = Y_v4.**

## A. Modelled IL per council x fire row (218 rows of Experiment 14 ANALYSIS_TABLE)
Direct shocks (first 24 months from the month of first fire start):
1. **Tourism:** annual visitor spend S (TRA LGA profile, 2014-17 average; E18-D1) x d/12 x e. d = months disrupted
   (default 6 **[assumed]**). e = exposed share, by the reach rule r: inside outline = residents_in / residents_council;
   **1 km (default)** = residents_1km / residents_council; council = 1 (Experiment 16 table, E18P-08). Spend is spread
   over IO industries Accommodation, Food and beverage services, Retail trade and Road transport in proportion to their
   national household final consumption (ABS Table 2, E18-IO1) **[assumed split]**. No TRA value ('np', '-', or no file)
   = tourism shock missing, and then modelled IL is missing for that row.
2. **Farm output: omitted.** No farm output or value per hectare is on disk (INVENTORY.md). Farmland burned (farm_km2_in)
   exists but cannot be priced. Stated as a gap.
3. **Business interruption:** council jobs (Census 2016 G51 for fires before Jul 2021, 2021 G54 after; E18-D3/D4) x
   workplace_mb_in / workplace_mb_council (Experiment 16) x d/12, spread by the council's industry mix; jobs -> output
   with national output per job by industry (Tables 5 and 20).
4. **Rebuild offset:** homes destroyed (homes_v2) x A$344,300 (Experiment 17 mid rebuild cost per home, sources E17R-038,
   E17R-040) x b, as extra demand for Construction spread evenly over months 7-36. b = offset share, default 0.66
   (= 1 - households' 34% uninsured share, Experiment 17) **[assumed]**.

**IO model.** ABS 2023-24 national tables (E18-IO1..IO5; ABS warns national multipliers overstate for small regions,
E18L08). Regionalise the direct-requirements matrix (Table 6) with Flegg's FLQ: a_ij(region) = a_ij x min(1, CILQ_ij x
lambda), lambda = [log2(1 + council jobs / NSW jobs)]^delta, delta default 0.3 **[assumed; FLQ source E18L10 is a
snippet only]**. LQs from Census industry divisions; each of the 114 IO industries takes its division's LQ (ANZSIC
lookup). **Type I** = (I - A_r)^-1. **Type II** closes the model with households: labour income row = compensation of
employees / output (Table 2), household spending column = Table 2 household consumption shares, both regionalised the
same way. Outputs per row: modelled output loss (A$, net of offset), job loss, labour income loss, and each as a share
of council baseline (baseline output = council jobs by industry x national output per job). Dollars are nominal and
mixed-year; only the shares are used for checks and ranks.

## B. Calibration to measured limits (the new part)
Each check compares a **model dose-response slope** with a **measured 95% CI on the same dose scale**. The model slope
= OLS slope through the origin of the row's modelled change on its dose, over the rows of the named sample.

| Check | Model output | Measured CI it must sit inside |
|---|---|---|
| M1 unemployment (council, primary) | job loss / council labour force (all lost jobs assumed held by residents, so an upper bound), per 10% of residents in or within 1 km | Exp 7 Day 6: -0.01 pts [-0.35, +0.59], all seasons |
| M1b unemployment (SA2, secondary) | same, per 10 pp of homes inside outline (H), Black Summer rows | Exp 13 SA2 B: -0.09 [-0.29, +0.12]; placebo fails, so secondary |
| M2 income (primary) | Type II labour income loss / baseline labour income, years 1-2, per 10 pp H, Black Summer | Exp 13 ATO postcode B: -1.2% [-3.1, +0.8] |
| M2b income (secondary) | same | Exp 13 SA2 PIA B: -1.6% [-2.6, -0.7] |
| M3 accommodation & food | % change in Accommodation + Food services output, years 1-2, per 10 pp H, Black Summer; businesses assumed to move 1:1 with output **[assumed, an upper bound]** | Exp 13 CABEE B: +3.6% [-1.2, +8.6] |
| Duration (bounds only) | d | Exp 15 night lights: inside / within 1 km dip about 1.5-2.5 years; 1-5 km ring not detected (-3.6% [-9.9, +1.7]) |
| Descriptive only | jobs lost per home destroyed | Exp 12 income-support recipients per home destroyed, upper 4.48 (not a calibration: job loss need not lead to income support) |

**"Model overstates"** = the model slope lies beyond the harmful end of the measured CI (M1: above +0.59; M1b: above
+0.12; M2: below -3.1%; M3: below -1.2%). "Understates" = beyond the other end (e.g. M2b: less negative than -0.7%).
Otherwise "inside".

**Unconstrained** = defaults (d = 6, r = 1 km, b = 0.66, delta = 0.3, Type II). **Constrained**: grid search over
d in {1, 2, 3, 6, 9, 12, 18, 24, 30} months, r in {inside, 1 km, council}, b in {0, 0.25, 0.5, 0.66, 0.75, 1},
delta in {0.1, 0.2, 0.3, 0.4, 0.5}, Type I or II. Pick the setting with the most primary checks (M1, M2, M3) inside;
ties -> fewest secondary checks outside; then the smallest total distance from defaults (each parameter scaled to its
range); then Type II. Plausible bounds: **d 1-30 months** (night lights), b 0-1, delta 0.1-0.5. The same global
parameters apply to all rows. Both unconstrained and constrained results are reported, check by check.
**Out-of-sample check:** calibrate on the pre-COVID (P) CIs of Exp 13 only and report whether the Black Summer checks
pass (P CIs are wide, so this is weak and stated as such).

## C. Hybrid Y
IL_model = constrained modelled output loss share (net of offset), sign +1, as a percentile rank across rows where it
exists (1 = worst), as in v4. **Y_hybrid** = v4 Y with the IL pillar replaced by IL_model; DL, FP, SL unchanged; equal
weights, re-normalised when a pillar is missing. **Y_measured = Y_v4, unchanged.**

## D. Models
Exactly as Experiment 14: same X sets (PRE; PRE+FIRE), RF (500 trees, max_features 1/3, min_samples_leaf 5, seed
20261002), training mean, ridge, fire-size line; leave-one-fire-season-out (council-grouped 5-fold as check); 2,000
council-cluster bootstrap; permutation importance; the same "beats baseline" and "real ranking signal" rules.
**Primary scientific result = Y_measured and its pillars** (re-run with the same code to confirm it matches
Experiment 14). Y_hybrid and IL_model are **secondary, labelled "partly assumed"** in every table and figure.

## E. Leakage and circularity guards
- Model inputs that are also X or Y parts: share burned (X log_share), residents/homes inside and within 1 km (X log
  homes inside / within 1 km per 1,000), homes destroyed (DL1, through the rebuild offset), council industry mix
  (checked against the V items in COUNCIL_ITEMS_v2 before the build; any overlap is listed).
- Y_hybrid and IL_model models are run (a) with full X and (b) with the overlapping X columns removed. "Skill from the
  modelled part" = rho(a) - rho(b), and rho(Y_hybrid) - rho(Y_measured), each with bootstrap CI.
- Also reported: Spearman of IL_model with DL, and IL_model without the rebuild offset.
- SHAP / importance is interpreted scientifically **only for measured targets**; for Y_hybrid it is shown as "what the
  assumed model encodes".
- Shuffled-Y check (200 permutations) for Y_hybrid PRE+FIRE and IL_model PRE+FIRE.
- Calibration uses Black Summer small-area slopes, which include held-out fold fires; the P-only calibration is the
  guard against that.

## F. Pilot gate (Black Summer rows, season 2019, 57 rows)
Build the model for these rows first. **Proceed to all 218 rows only if** the constrained setting puts at least 2 of
M1, M2, M3 inside their CIs, with every parameter inside its plausible bound, and IL_model is not trivial (not all
zero or constant; fewer than half the rows tied). Otherwise **stop** and report the unconstrained and best constrained
results, and which check failed. Y_measured models are reported either way.
