# Experiment 7, Day 4: dealing with blurry socioeconomic data. Rules fixed first

Written 2026-10-01 before any Day 4 number. Locked in `LOCK_DAY4.txt`. Ray asked for options 1-3
(affected people as dose, pooling, quarterly data), then option 4 (per-fire estimates with ranges) if a signal exists.

## Dose (option 1)
Primary: share of the council's residents living inside or within 1 km of the event's fire outlines
(`pop_within_1km` from fire_event_dataset/data/enrich/affected_pop_event_council.parquet, Census 2016/2021 mesh blocks)
÷ council population at 30 June before the fire (lga_year). Secondary: residents inside the outlines only.

## Outcome per row and indicator
Counterfactual = Day 1 V2b (council effects + Metro/Regional/Rural year effects, fitted on clean council-periods;
leave-one-out residuals where the period is clean). Change = mean residual after the fire minus mean residual in the
council's own pre-fire periods, oriented so + = worse, divided by the SD of the same change at clean pseudo-fires.
- Annual: total income, businesses, cash cover, services share, renewals ratio: after = relative years 0-1,
  before = relative years -3..-1 (as Day 1 D2).
- Quarterly (option 3): income-support recipients per 1,000: after = quarters q0+1, q0+2; before = q0-4..q0-1.
  Night lights stay out (Day 1: fire light). Payroll jobs not used (series starts 2020Q1, after Black Summer began).

## Pooled tests (option 2)
For each of the 6 indicators: OLS slope of change on dose (per 10 percentage points of residents affected),
council-cluster bootstrap 95% CI (2,000; seed 20261001), plus Spearman. Holm correction across the 6 at 0.05
(bootstrap p = 2 × smaller tail share). Pre-trend check for each: same slope with the pre-period drift
(residual at rel -1 minus mean of rel -3, -2; quarterly: q0-1 minus mean of q0-4..q0-2) as outcome.
An indicator counts as "detected" only if its Holm-adjusted slope is significant, positive, and its pre-trend slope CI
includes 0. Composite: mean of the available standardised changes (>= 3 indicators), same tests.
Reported also: area share burned as dose (to compare with Day 1), and Black Summer excluded.

## Option 4 (only for detected indicators, or the composite if detected)
Empirical Bayes per fire: prior mean = pooled dose line at the row's dose; noise variance = 1 (changes are in
noise-SD units); signal variance tau^2 = method of moments (variance of residuals around the line minus 1, floor 0).
Estimate = prior + tau^2/(tau^2 + 1) × (observed − prior), 90% interval from the posterior variance.
If nothing is detected, option 4 is not run and the report says the per-fire socioeconomic signal is below detection.
