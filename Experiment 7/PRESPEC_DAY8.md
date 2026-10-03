# Experiment 7, Day 8: rapid damage estimate right after a fire. Rules fixed first

Written 2026-10-01 before any Day 8 number. Locked in `LOCK_DAY8.txt`.
Question: using only information available days after a fire (the burned outline, the homes inside or near it,
satellite burn severity, fire weather), how well can we estimate homes destroyed per 1,000 dwellings, compared with
area burned alone?

## Data
Same 218 rows; target DL_FILLED v2 (135 rows). Post-fire predictors:
- A = log share of the council's homes within 1 km of the fire outline
  (dwellings_within_1km from affected_pop_event_council / council dwellings), floored at 1e-6.
- I = log share of the council's homes inside the outline (dwellings_in_fire), floored at 1e-6.
- S = high/extreme burn severity share of the burned area (NSW FESM; X_fire_severity_high_extreme_share), standardised.
- W = peak FFDI (X_fire_max_ffdi), standardised.
Rows need all predictors (S is missing for some rows), so all models use the same rows.

## Models (Poisson, offset log council dwellings, as Day 2)
- R0: log share burned (area only; Day 2 M0)
- R1: A + I
- R2: R1 + S          <- pre-specified rapid-estimate model
- R3: R2 + W
## Tests (leave-one-fire-season-out, as Day 2)
Primary: R2 vs R0, out-of-season Spearman difference (paired council bootstrap, 2,000, seed 20261001) AND
out-of-season Poisson deviance. "Rapid estimate works" if the Spearman CI is above 0 and deviance falls;
"partly" if only one; otherwise "no". Reported: all models, Black Summer fold predicted vs observed homes, in-sample
rate ratios, and the share of rows where the R2 out-of-season prediction is within a factor of 2 of the observed
homes count (rows with >= 1 home lost).
