# Pre-registration: stage 10, were the roads really closed, how long was the escape window, and what did isolation cost?

**Date registered:** 2026-09-23. Written before any traffic outcome, validation result, corridor
deficit or fiscal index was computed. Only coverage counts and table formats were inspected.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Why
Stages 1–9 infer that a road is closed when a final fire outline touches it. That inference has never
been checked against what happened on the road. People also often evacuate before roads close, so
this project will not claim anyone was "trapped". Stage 10:
- (A) checks the closure rule against traffic counters;
- (B) restates the escape window;
- (C) measures short-run disruption to movement;
- (D) decides, by a rule fixed now, whether a council finance model is worth building.

## Data
- **Traffic:** `aussef.duckdb` raw layer (approved by the user, 2026-09-23):
  - Counts: `raw.manual_traffic_hourly_permanent_0` … `_4`, TfNSW permanent counters, 2006 to 30 April 2020, one row per station × date × direction × vehicle class.
  - Locations: `raw.manual_traffic_station_reference`.
  - Classes: `classification_seq` 0 = all vehicles, 2 = light, 3 = heavy (freight).
  - Raw-layer fingerprint: the row count and the SHA-256 of the sorted (station_key, date, direction, class, daily_total) rows, recorded in RUN_LOG.
- **Fires:** part A families (2019–23) and part B historical events (stage-2 definitions), with event windows from `stage3/run_stage3.py:event_tables`.
- **Roads:** the frozen 2019 network, excluding `service`.

## Day validity (applies to every part)
- A station-day is **valid** only if every direction the station reports in its baseline period is present, and each has ≥ 20 non-blank hourly values.
- A day that fails is **missing**, never zero: a broken or burned counter is not a road closure.
- The daily volume is the sum of `daily_total` over directions, for the relevant class.

## Part A: closure-rule validation (descriptive, with interpretation bands)
- **Station → edge:** the nearest road edge within 30 m.
- **Pairs:** station × fire event, 2006-01-01 to 2020-04-30, where the fire (event geometry) lies within 500 m of the station's edge.
- **Fire window:** event start − 1 day to event end + 7 days (end = start + 30 days if unknown).
- **Eligibility:** ≥ 3 valid days in the window.
- **Baseline:** the median valid all-vehicle daily volume over the same calendar window (day of year ± 7 days) in the 3 preceding years. At least 7 valid baseline days are required, otherwise the pair is ineligible.
- **Observed closed:** at least one valid window day at ≤ 20% of baseline. Sensitivity: ≤ 50%.
- **Predicted closed:** S0, the fire outline intersects the edge. Sensitivity: ≥ 50% of the edge length inside the outline, and S100 (within 100 m).
- **Reported:**
  - The % observed closed among predicted-closed pairs, and among near-but-untouched pairs, each with a Wilson 95% interval.
  - The difference between the two.
  - The full pair table.
- **Interpretation (S0, 20% threshold):**
  - **RULE SUPPORTED** if ≥ 60% of predicted-closed pairs are observed closed **and** the Wilson lower bound for predicted-closed exceeds the point rate for untouched pairs.
  - **RULE UNRELIABLE** if < 40%.
  - Otherwise **INCONCLUSIVE**.
  - **NOT EVALUABLE** if fewer than 5 eligible predicted-closed pairs.

## Part B: escape window (restated, no new inference)
From `stage4/out/timing_pairs_near_town.parquet` (K = 5 km): the hours between fire first reaching the
first and last exit near town, for the 31 satellite-era cut-offs. Reported: median, quartiles, the
share within 6, 12 and 24 h, and undated cases.

## Part C: short-run disruption to movement (descriptive)
- **Stations:** valid stations whose edge lies within 5 km of a Black Summer family (start 2019-07-01 to 2020-06-30).
- **Weeks:** Monday-start weeks from 2019-11-04 to the week ending 2020-02-23 (pre-COVID).
- **Baseline:** the mean of the same week-of-season in 2016-17, 2017-18 and 2018-19.
- A week is valid with ≥ 6 valid days; a baseline needs ≥ 2 valid years.
- **Reported per station, for all vehicles and heavy vehicles:**
  - weeks below 80% of baseline
  - the deepest weekly ratio
  - the net deficit Σ(baseline − observed) in vehicle trips
- **Totals across stations.** Labelled as disrupted movement, not dollar losses.

## Part D: council fiscal-shock feasibility (descriptive, with a go/no-go gate)
- **Council groups**, from stage-8 town groups mapped to councils by largest overlap:
  - **cut off:** contains ≥ 1 town cut off by a Black Summer fire
  - **burned only:** contains ≥ 1 burned-not-cut-off town and none cut off
  - **untouched:** the rest
- **Measures, each indexed to the council's own 2018-19 value = 100:**
  - road spending (`olg_road_expenditure_panel.csv`, roads/bridges/footpaths)
  - total grants (`capital_grants_aud` + `operating_grants_aud`, `master.fiscal_panel_extended`)
- **Gap in year y:** median index(cut off) − median index(burned only).
- **GO** for a council finance model if, for either measure, max(gap in 2019-20, gap in 2020-21) exceeds max |gap| over 2016-17 and 2017-18. Otherwise **NO-GO**.

## Caveats
- Few validation pairs, so the intervals will be wide. Part A can detect a badly wrong rule, not measure accuracy precisely.
- Counters sit at fixed points: a closure elsewhere on a road may or may not reduce flow at the counter.
- Traffic falls for reasons other than closure: evacuation orders, tourist leave zones, holiday patterns, smoke. Observed closure means "traffic nearly stopped", not "officially closed".
- COVID-19 affects everything after February 2020, so Part C stops there.
- Descriptive throughout: no causal claims, and no claims about people being trapped.
