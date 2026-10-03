# Experiment 7, Day 3: the new Y and X, and one new test (fire weather). Rules fixed first

Written 2026-10-01 before any Day 3 number. Locked in `LOCK_DAY3.txt`.

## New Y (per council × fire row)
- Main Y: homes destroyed per 1,000 dwellings (DL_FILLED v2: reported plus zeros inferred from RFS totals).
- Severity class (absolute, not percentile):
  4 Extreme: >= 100 homes destroyed
  3 Severe: >= 10 homes destroyed or >= 2 deaths
  2 Moderate: >= 1 home destroyed or 1 death
  1 Light: 0 homes and 0 deaths
  Unknown: no homes figure and no death recorded.
  Deaths = SL_deaths_sourced, else info_reported_deaths (as in v1).
- Income, businesses, council finances and welfare are not part of the per-fire Y (Day 1: no dose-response).

## New X
- Fire: log share of council burned; peak fire danger X_fire_max_ffdi (pre-declared single weather variable).
- Pre-fire council: E2 (share of dwellings in BFPL Cat 1-2), V (disadvantage block), H (hazard block).
  Council finances dropped (Day 2: no contribution). All standardised.

## One new test: does fire weather explain the Black Summer gap?
Models (Poisson, offset log dwellings), same leave-one-fire-season-out design as Day 2:
- M2: log share + E2 + V   (baseline)
- M4: M2 + FFDI
Reported: out-of-season Spearman and Poisson deviance of M2 vs M4 (paired council bootstrap for the Spearman
difference); predicted vs observed homes for the Black Summer fold; in-sample FFDI rate ratio with council-cluster
bootstrap (1,000 refits). "Weather helps" if the deviance falls and the Spearman difference interval is above 0;
"partly" if only one of the two; otherwise "no".
