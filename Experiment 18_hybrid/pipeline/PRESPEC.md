# Experiment 14 pre-specification: composite impact score, version 4 ("Y v4")

Written 2 Oct 2026 (late evening), **before any v4 value is computed or looked at** and before any model is fitted.
Hash-locked in `LOCK_PRESPEC.txt` before the indicator build. Config and built inputs are hashed again in
`LOCK.txt` before `run_models.py`. Later changes are reported as numbered deviations in FINDINGS.md.

**v4 was chosen AFTER seeing the v3 results** (Experiment 9 FINDINGS_V3.md), the impact clock (Experiment 11),
the spillover study and the audit (Experiment 12). It is therefore not an independent test of the framework. Every
table and figure from this experiment is labelled "v4 (post-v3)". Each change below is justified on measurement
grounds (what the indicator measures, when, and against what), not on which version scored better.

## What stays the same as Experiment 9
Bowen's framework Y = DL + IL + FP + SL, equal weights. The same 218 council x fire rows. Each indicator becomes a
percentile rank across the rows where it exists (1 = worst, after its sign); pillar = mean of its indicator ranks
present; Y = weighted mean of the pillars present (weights re-normalised). Missing stays missing (never 0).
The same X sets (PRE = H, E2, V, F, X23; PRE+FIRE adds log share burned, peak FFDI, high/extreme severity share,
log homes inside the fire per 1,000, log homes within 1 km per 1,000), taken unchanged from
`Experiment 9/results/ANALYSIS_TABLE.csv`. The same models (RF 500 trees, max_features 1/3, min_samples_leaf 5,
seed 20261002; training mean; ridge; fire-size line; Poisson for DL), the same leave-one-fire-season-out validation
(council-grouped 5-fold as a check), the same council-cluster bootstrap (2,000), permutation importance, shuffled-Y
checks (200 for the main Y with each X set, 100 per pillar), and the same decision rules:
- RF **beats a baseline** if the 95% CI of (RF MAE minus baseline MAE) is entirely below 0.
- RF has a **real ranking signal** if the Spearman 95% CI lower bound is above 0 and shuffled-Y p < 0.05.
- Otherwise: "no detectable predictive skill above the stated CI", not "no effect".
- **Primary result:** Y v4, PRE+FIRE, RF vs training mean, leave-one-season-out. Everything else is secondary.

## Common rules for v4 indicators
- m0 = month of `first_fire_start`; F = fire financial year (start year, e.g. 2019 = Jul 2019 to Jun 2020), as in
  the master. FY offsets use the OLG / statement convention `fy_start` (FY+1 of F = 2019 is 2020-21).
- **Comparison group = FAR unburned councils** (replaces "all councils with no master row in F"). For fire year F, a
  council is FAR if (a) it has no master row in F, (b) it does not share a border with any council that has a master
  row in F (Experiment 12 `results/ADJACENCY.csv`: 2021 polygons touching within 50 m), and (c) less than 0.5% of its
  area burned in FY F (`fire_event_dataset/out/fires.csv`, `share_of_region_burned` summed by council and FY; audit
  check c2). Why: Experiment 12 found neighbours of burned councils absorb rent effects, and the audit found burned
  councils without a master row inside the old pool, so both pull the old comparison toward the burned rows.
- **Excess** = the row's own change minus the median of the same change, same window, over FAR councils with a value.
  If fewer than 5 FAR councils have a value, the row is missing.
- **Sensitivity (pre-declared):** the same indicators with FAR councils restricted to the row's OLG group
  (Metro / Regional / Rural, from `time-series-data-2018-2019.xlsx` as in audit script 05); minimum 5, else missing.
  Coastal vs inland matching is not done (no ready, sourced coastal flag on disk).

## v4 indicators (main Y v4)

### DL (unchanged)
- **DL1 homes destroyed per 1,000 dwellings** (v2, `homes_per_1000_v2_inferred`), sign +1.

### IL (v3 minus traffic)
- **IL1 traffic: removed.** The audit (Experiment 12/audit/AUDIT.md, f1, f2) found half-counted one-direction days
  that become more common after bigger fires; corrected, it does not track the fire.
- **Experiment 13 fine-geography results are NOT used:** its `audit/` folder is empty (checked 2 Oct 2026, 22:19),
  so it is neither finished nor audited.
- **IL2 income in the affected small areas** and **IL3 businesses in the affected small areas**: as v3 (Experiment 9
  PRESPEC Addendum v3), except that control SA2s must also lie in a FAR council for F (SA2 -> council by 2021
  residents, as v3). Same GCCSA rule, zero-dose rule and weights as v3. Signs -1.

### FP (measured at its peak timing from the impact clock)
Why: Experiment 11 showed council money keeps arriving for 3 years (grants per resident link +0.08 in the fire year,
+0.21, +0.29, +0.43 at FY+3; fire-related grant share peaks at FY+2, +0.53). A one-year window measures only part of
the cost. Window for all three flow measures: **post = mean over the available years FY+1, FY+2, FY+3 (at least
one needed); pre = mean of FY F-2 and F-1 (at least one needed)**. The number of post years used is recorded per row.
- **FP1 grants per resident rise:** OLG `grants_contributions_revenue_pct / 100 x total_revenue_continuing_ops_aud /
  population`; own change = mean log(post) - mean log(pre) (Experiment 11 C4 definition, extended to FY+1..FY+3);
  excess vs FAR councils (all NSW councils in OLG). Sign +1. Replaces the master column (one year, all unburned).
- **FP2 fire-related grant share:** Experiment 10 audited statements, same item and label rule as v3, including the
  rule that sets the share to missing for a fire council with no fire/disaster line in any year (audit f4, now
  stated). Own change = mean share(post) - mean share(pre). Excess vs the median of the Experiment 10 comparison
  councils that are FAR in F (minimum 5; if fewer, missing). Sign +1.
- **FP3 capital spending share:** `capex_ippe / total expenses`, same windows and comparison as FP2. Sign +1.
- **FP4 cash drawdown:** OLG `cash_expense_cover_ratio_months`; own change = mean(F, F+1) - mean(F-2, F-1); excess vs
  FAR councils. Sign -1. Recomputed (v3 used master columns compared with all unburned councils). Cash drawdown is an
  immediate effect, so its window is not lengthened.

### SL
- **SL1 rents:** NSW new-bond median rent by council and quarter (`rent_lga_quarter.parquet`); own change = mean log
  rent in quarters 5-8 after the fire quarter - mean log rent in the 4 quarters before (Experiment 11 C2 H2 /
  Experiment 12 definition: the 1-2 year scale of mechanism #5); excess vs FAR councils. Sign +1. Replaces the master
  column (one quarter, all unburned).
- **SL2 domestic violence:** as v3 (BOCSAR, months 6-24 vs 24 months before, at least 12 post months), excess vs FAR
  councils. Sign +1.
- **SL3 rebuild gap (trend-adjusted):** as v3 (rows with >= 5 homes destroyed, approvals from July 2018), but the
  expected approvals without the fire = 24 x own pre-fire monthly mean x (1 + g), where g = median over FAR councils
  of (their mean monthly approvals in m0+1..m0+24 / their mean in m0-12..m0-1) - 1. Gap = 1 - clip(extra / homes
  destroyed, 0, 1). Sign +1. Why: Experiment 11 found the unadjusted per-home curve tracks normal council growth (v3
  deviation 3).
- **SL4 deaths per 100,000 residents (new):** master `SL_deaths_sourced` / `X_council_council_population_pre` x
  100,000. 142 rows recorded (17 above 0); blank stays missing. Sign +1. Includes responders, as recorded in the
  master. Sensitivity: residents only (`SL_deaths_sourced - SL_deaths_responders`).
- **Injuries: descriptive only** (`SL_injuries_sourced`: 10 rows recorded, 48 injuries; blank = not reported, not 0).
- **Disaster payments to households: NOT included** (decided before any v4 value, on coverage). The NEMA
  Location-Based Disaster Assistance Payments file (DATA_CHECK.md) has no record for AGRN 871 (Black Summer, 50 panel
  rows) and no AGDRP for any 2022-2024 panel event; only AGRN 880 (7 panel rows) has household payments. An indicator
  with at most 7 of 218 rows would be ranked on almost nothing. The AGRN 880 payments per 1,000 residents are reported
  in a descriptive table only.
- **Insurance:** no public council-level data (DATA_CHECK.md). X23 stays as the underinsurance proxy.

## Other Y versions reported (all secondary)
1. **Y v4 magnitude** (keeps size): the same indicators; each raw value x sign is standardised across the rows where
   it exists (z = (x - mean) / SD), then clipped to [-3, +3] so one extreme row cannot dominate; pillar = mean z;
   Y = equal-weight mean of pillars present. Not on a 0-1 scale (MAE not comparable with the rank Ys).
2. **Per-horizon Ys** (same rank/pillar/composite rules; a pillar with no indicator at that horizon is missing):
   - **H0 immediate** (fire FY, first months): DL1; SL4 deaths; FP1, FP2, FP3 at FY+0 (post = FY F only); FP4 with
     post = FY F only.
   - **H12 one to two years:** IL2, IL3; FP1, FP2, FP3 with post = mean of FY+1, FY+2; FP4 with post = FY+1 only;
     SL1 rents quarters 5-8; SL2 DV months 6-24; SL3 rebuild gap.
   - **H3 three years and later:** FP1, FP2, FP3 with post = FY+3 only; SL1 rents quarters 9-16.
3. **Y v4, OLG-group-matched comparison** (sensitivity above).
4. **Y v4, deaths of residents only** (SL4 sensitivity).
5. For side by side, taken read-only from Experiment 9 `results/METRICS.csv` and `SHUFFLE_CHECK.csv` (same code, same
   seed): **v1** (`Y_comp_cfgv1` and its pillars; workbook `Y_v1`) and **v3** (`Y_comp` and its pillars).

## Models run in Experiment 14
Targets: Y_v4 and its four pillars (main); Y_v4_mag, Y_v4_H0, Y_v4_H12, Y_v4_H3, Y_v4_olg, Y_v4_resident_deaths
(secondary). Both X sets, both CV schemes, all baselines, permutation importance as in Experiment 9. Shuffled-Y:
Y_v4 PRE+FIRE and PRE (200 each), each v4 pillar PRE+FIRE (100 each).

## Descriptive (not pre-registered as tests)
Spearman of each v4 indicator (rank) with log homes inside the fire per 1,000 and with log share burned, as in the v3
findings. Coverage (rows with a value) for every indicator, pillar and Y.

## Audit before reporting
A fresh reviewer agent, not shown my numbers first, re-derives from the raw files with its own code: FP1 and SL1 for
all rows, the FAR comparison sets per fire year, SL4, Y_v4 for at least 10 rows, and the primary metric; and checks
council-name matching in every source used. Its report goes in `audit/AUDIT.md`; findings that change numbers are
fixed and listed as deviations.
