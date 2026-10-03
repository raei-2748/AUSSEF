# Experiment 7, Day 5: income where the affected people live (SA2)

Date: 1 Oct 2026. Rules locked first: `PRESPEC_DAY5.md` (LOCK_DAY5.txt). Scripts: `prep_sa2_dose.py`,
`day5_sa2_income.py`. No downloads (ABS income files and Census mesh blocks already in the project).

## Why
Council data dilute fires: in the typical council-fire, about 0.5% of residents were in or near the fire. At SA2
level (623 NSW small areas), the typical Black Summer SA2 that was touched had 5% of residents within 1 km of fire,
and 49 SA2s had 25% to 100%.

## Result: not detected, but now with tight limits
Panel: 623 SA2s × 2015-16 to 2021-22 (4,018 rows). SA2 and year (Sydney / rest of NSW) fixed effects, standard
errors clustered by SA3. Per 10 percentage points of residents in or within 1 km of the fire:

| Outcome | Fire year + next year | 95% CI | Future-fire placebo |
|---|---|---|---|
| Total income | +0.1% | -0.9% to +1.1% | passes |
| Earners | +0.3% | -0.4% to +1.0% | passes |
| Mean income | -0.2% | -0.7% to +0.4% | passes |
| Median income | -0.2% | -0.7% to +0.2% | passes |

- Scaled to an SA2 where everyone lived in or near the fire: median income about -2% (CI -7% to +2%).
- Direction matches the literature (small falls), but it cannot be told apart from zero. Falls larger than about
  7% for whole small areas are ruled out.
- 49 heavily affected SA2s (>= 25% of residents): no clear drop after the fire (fire year +0.8%, year after -0.5%,
  relative to their own pre-fire level and other SA2s; noisy).

## What it means
Even without dilution, taxable income in burned areas did not measurably fall. Likely reasons: most residents
kept their jobs, insurance and recovery money flowed in, and income tax data cover the whole year. The literature's
falls (e.g. -8% for employed people after Black Saturday) come from following individual people over 5 years,
which public area data cannot do.
