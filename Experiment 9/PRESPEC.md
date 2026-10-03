# Experiment 9 pre-specification: Bowen's modelling pipeline on the composite Y

Written 2 Oct 2026, before any model is fitted. Hash-locked in LOCK.txt together with config.toml.
Any later change is reported as a numbered deviation in FINDINGS.md.

## Question
Using Bowen's framework (composite Y = DL + IL + FP + SL, X variable groups, council x fire panel, random forest +
variable importance), how well can the composite Y and each pillar be predicted for a fire season the model has
not seen, and which X variables matter? Expectation stated in advance (from Experiments 6 and 7): fire X variables
should predict DL; IL, FP and SL, as currently measured, mostly do not respond to fire size, so they may not be
predictable. Results are reported pillar by pillar so this is visible.

## Rows
The 218 council x fire rows of the master workbook (69 councils, fire seasons = financial years 2014-2024).

## Y versions (all on a 0-1 scale, 1 = worst)
- **Y_comp (main):** pillars rebuilt from config.toml. Each indicator = percentile rank across the 218 rows after
  applying its sign; pillar = mean of its indicator ranks; Y = weighted mean of the pillars present for that row
  (weights re-normalised), equal weights. DL = homes destroyed per 1,000 dwellings from DL_FILLED.csv, variant v2
  (sourced + reported + inferred-zero seasons; 135 rows). IL, FP, SL = the workbook's current indicators.
  The code must reproduce the workbook IL, FP, SL and v1 DL ranks exactly (check, max abs diff < 1e-9).
- **Y_v1:** workbook column `Y` (same rule, original DL with 90 rows).
- **Pillar targets:** DL, IL, FP, SL separately (rows where the pillar exists).
- **Weighting sensitivity for Y_comp:** class note (35/25/30/10), deck (30/25/25/20), entropy weights (standard
  entropy method on the four pillar values, rows with all four pillars), and leave-one-pillar-out (equal weights
  on the other three). Also: Y_comp on complete rows only (all four pillars present).

## X sets
- **PRE (known before the fire):** council hazard H, exposure E2 (share of dwellings in bush fire prone land cat 1-2),
  vulnerability V, fiscal F, from COUNCIL_ITEMS_v2.csv.
- **PRE+FIRE:** PRE plus log share of council burned, peak FFDI, share of burned area at high/extreme severity,
  log(1 + dwellings inside the fire per 1,000 council dwellings), log(1 + dwellings within 1 km per 1,000).
Missing X values: median of the training fold (only severity has gaps).

## Models (fixed settings, no tuning on the test data)
- **RF:** random forest regressor, 500 trees, max_features = 1/3, min_samples_leaf = 5, fixed seed.
- **Baselines:** (a) training-fold mean; (b) ridge on standardised X (alpha by inner leave-one-out CV over a fixed
  grid); (c) fire-size line: OLS of Y on log share burned only; (d) DL pillar only: Experiment 7's Poisson model
  (homes destroyed ~ log share + E2, offset log dwellings); its predicted rate is mapped to the 0-1 scale with the
  training rows' empirical distribution so MAE is comparable.

## Validation and metrics
- **Main:** leave-one-fire-season-out (financial year). Out-of-fold predictions are pooled across folds.
- **Check:** council-grouped 5-fold CV (no council in both train and test), fixed seed.
- **Metrics on pooled out-of-fold predictions:** Spearman rho, MAE. 95% CIs by council cluster bootstrap
  (2,000 resamples). Paired MAE difference RF minus baseline with the same bootstrap.
- **Shuffled-Y check:** permute Y across rows, rerun RF with leave-one-season-out; 200 shuffles for Y_comp (both X
  sets), 100 for each pillar (PRE+FIRE). p = (1 + shuffles with rho >= real rho) / (1 + shuffles).

## Decision rules
- RF **beats a baseline** if the 95% CI of (RF MAE minus baseline MAE) is entirely below 0.
- RF has a **real ranking signal** if the Spearman 95% CI lower bound is above 0 and shuffled-Y p < 0.05.
- Otherwise: "no detectable predictive skill above the stated CI", not "no effect".
- Primary result: Y_comp, PRE+FIRE, RF vs training mean, leave-one-season-out. Everything else is secondary.

## Variable importance
- **Permutation importance on held-out folds:** for each leave-one-season-out fold, shuffle one X column in the test
  rows only and predict with that fold's model; pooled MAE increase vs unshuffled; 30 repeats; report mean and
  2.5-97.5% range across repeats. For every target x X set.
- **SHAP:** TreeSHAP mean |SHAP| for an RF fitted on all rows (descriptive only), Y_comp and each pillar, PRE+FIRE.
  shap runs in a throwaway uv environment pinned to the same scikit-learn version.

## Outputs
results/*.csv|json, figures (importance ranking, predicted vs actual, pillar-by-pillar skill), FINDINGS.md in plain
English, README.md with run order.

---

## Addendum v3 (2 Oct 2026, evening): fire-matched pillar indicators ("Y v3")

Written before any v3 indicator value is computed or looked at, and before any v3 model is fitted. Locked in
LOCK_v3.txt (this file's hash) before the indicator build; the config and built inputs are hashed again in LOCK.txt
before `run_models.py`. Framework unchanged: Bowen's composite Y = DL + IL + FP + SL, equal weights, same rows
(218), same rank/pillar/composite rules, same models, validation and decision rules as above. What changes: which
indicators fill each pillar, and one X variable (Bowen's X23) is filled.

**Why.** Experiments 6-9 showed IL, FP and SL, measured as whole-council annual changes, do not move with the fire.
Experiment 8 (55 mechanisms, 141 non-ACM sources) ranks how bushfires cause harm. Rule for v3: each pillar uses the
highest-ranked mechanisms that can be matched to the fire in place (the affected area or the council's own accounts)
and time (fire start month / fire financial year and after, against the same place's own pre-fire level).

**Common rules.** m0 = month of `first_fire_start` for the row; F = fire financial year (start year) as in the master.
"Excess" = the row's change minus the median change over the same window in NSW councils with no row in that fire
financial year (unburned comparison), unless stated otherwise. Missing stays missing (never 0); a pillar is the mean
of the ranks present; Y re-normalises over pillars present (unchanged rule). Indicator signs: +1 = higher is worse.

### DL (unchanged)
- DL1 homes destroyed per 1,000 dwellings, v2 (`homes_per_1000_v2_inferred`), sign +1. Mechanisms #26.

### IL (replaces whole-council income and business count)
- **IL1 tourism traffic** (mechanism #2 peak-season tourism shutdown). TfNSW permanent counting stations
  (`raw.manual_traffic_hourly_permanent_*` and station reference in `data/aussef.duckdb`), all-vehicle daily totals
  summed over directions per station-day. Window W = calendar months m0 to m0+3; baseline = the same calendar months
  12 and 24 months earlier. Station change = log(mean daily volume in W / mean daily volume in baseline), requiring
  >= 50% of days present in W and in the baseline. Council change = median over the council's stations (station `lga`
  field matched to council name). Excess vs unburned councils with stations, same window. Sign -1 (fall = worse).
  Rows in councils without a qualifying station: missing.
- **IL2 income in the affected small areas** (mechanism #22 local earnings). Experiment 7 SA2 panels: SA2s assigned
  to the council in which most of their 2021 residents live; affected SA2s = those with residents within 1 km of fire
  in FY F (`sa2_fy_dose.parquet`, dose > 0). SA2 change = log(total income FY F+2) - log(total income FY F-1).
  Row value = mean over affected SA2s weighted by affected persons, minus the mean change of SA2s with zero dose in
  FY F-1..F+2 in the same GCCSA. Sign -1. Income ends FY2021-22, so defined for F <= 2019 only.
- **IL3 businesses in the affected small areas** (mechanism #10 business closure). Same SA2s and weights; CABEE count
  change log(June F+2) - log(June F), excess as IL2. Sign -1.

### FP (replaces services crowd-out and renewals ratio; keeps cash drawdown)
- **FP1 grants per resident rise** (mechanisms #4, #8): master `FP_grants_per_capita_change_plus1_excess` (OLG, all
  councils). Sign +1.
- **FP2 fire-related grant jump** (mechanisms #4, #16): Experiment 10 audited statements (fire councils, own-year
  statement values, `statements_tidy.csv`). Fire-related grant lines = items `disaster_grant_*` whose label matches
  bushfire / bush fire / rural fire / fire protection / fire service / emergency services / disaster recovery /
  natural disaster / bushfire relief or recovery, and does NOT match storm / flood. Share = sum / total expenses.
  Value = mean share over FY F and F+1 minus mean share over the available years of F-2 and F-1 (at least one of
  each period required). Excess vs the median of the same change in the 25 comparison councils (same item rule,
  `bushfire_emergency_services_grant` + `disaster_grant_*`). Sign +1. Rows without statements: missing.
  (Rule change vs Experiment 10 SUMMARY: "Bushfire and emergency services" is kept, because Black Summer recovery
  money was booked there; see BLACK_SUMMER_FIRST_LOOK.md. Measured as a jump over the council's own baseline.)
- **FP3 capital spending jump** (mechanisms #15, #16): capex_ippe / total expenses, same windows, baseline and excess
  as FP2. Sign +1.
- **FP4 cash drawdown** (kept from v1): master `FP_cash_cover_change_event_excess`, `FP_cash_cover_change_plus1_excess`
  (mean), sign -1.

### SL (replaces income-support rise)
- **SL1 rents** (mechanism #5): master `SL_rent_change_excess_pct` (new-bond median rent, quarter after the fire vs
  a year earlier, excess). Sign +1.
- **SL2 domestic violence** (mechanism #7): BOCSAR `RCI_offencebymonth.xlsm`, "Domestic violence related assault",
  monthly by LGA. Value = log(mean monthly count in m0+6..m0+24 / mean monthly count in m0-24..m0-1), needing >= 12
  post months available; excess vs unburned councils, same months. Sign +1.
- **SL3 rebuild gap** (mechanism #6, consequence of #1 underinsurance): ABS new houses approved per month by council
  (`BA_LGA2018`-`BA_LGA2026`, total sector, new work, houses). Extra approvals = sum over m0+1..m0+24 minus 24 x the
  mean monthly approvals in the 12 months before m0 (>= 6 months needed). Rebuild gap = 1 - clip(extra / homes
  destroyed, 0, 1), homes destroyed = DL v2 count. Defined only for rows with >= 5 homes destroyed and data from July
  2018; other rows missing (not applicable). Sign +1.

### X23 underinsurance proxy (mechanism #1, a moderator; Bowen's template slot X23 "insurance coverage")
- Share of occupied private dwellings owned outright (no lender-enforced building insurance), Census 2016 GCP
  (G33) for F <= 2020 and Census 2021 (G37) for F >= 2021, by council. Added to the PRE X set (so PRE+FIRE too).
  It is a proxy, not measured insurance; low income is already in V.

### Known gaps (stated, not measured)
Mental health (#3, published only for large areas yearly), farm capital (#21), public payments to households (#8,
optional later), tourism beyond road traffic.

### Outputs and comparison
`data.py` builds Y v3 from config v3; Y_v1 (workbook) and Y_comp_v1 (config v1 values carried as a column) are kept
for side-by-side reporting. Primary result unchanged in form: Y_comp (now v3), PRE+FIRE, RF vs training mean,
leave-one-season-out. **Map:** RF on the PRE set fitted on all 218 rows, predicted for every NSW council (pre-fire
risk of composite Y v3); plus observed mean Y v3 for councils with rows. Descriptive; its out-of-season skill is the
PRE row of the metrics table.
