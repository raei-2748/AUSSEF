# Experiment 7, Day 5: income where the affected people live (SA2), no dilution. Rules fixed first

Written 2026-10-01 before any SA2 income number was looked at. Locked in `LOCK_DAY5.txt`. No downloads: uses the
ABS Personal Income in Australia Table 1.4 (SA2) files already in the project and the local Census 2021 mesh blocks.

## Units and data
- Unit: NSW SA2 (ASGS 2021) × financial year, 2015-16 to 2021-22.
- Income: Table 1.4 of the 2024 release (2017-18 to 2021-22, ASGS 2021). 2015-16 and 2016-17 come from the 2022
  release (ASGS 2016) only for SA2s whose code and name are unchanged, chain-linked by the ratio of the two releases
  in 2017-18. Other SA2s start in 2017-18.
- Outcomes: primary = log total income (sum $). Secondary: log earners, log mean income (sum / earners),
  log median income.
- Dose D[s,t]: share of the SA2's usual residents (Census 2021 mesh blocks, area-weighted) living inside or within
  1 km of the union of all mapped fires that started in financial year t (out/fires.csv geometries,
  data/cache/fires.parquet). Caveat: 2021 counts are after Black Summer, so the dose is if anything understated.

## Model (two-way fixed effects with distributed lags and leads)
log y[s,t] = a[s] + b[GCCSA(s), t] + β0 D[s,t] + β1 D[s,t-1] + β2 D[s,t-2] + λ1 D[s,t+1] + λ2 D[s,t+2] + e
GCCSA = Greater Sydney vs Rest of NSW. Standard errors clustered by SA3. D missing (outside 2015-16..2021-22)
is set to 0 for lags/leads of the panel edges; fires before FY2015 are not in the fire layer (caveat).

## Tests
- Primary: cumulative effect β0 + β1 on log total income (per 10 percentage points of residents affected),
  95% CI. "Income effect detected" if the CI is below 0.
- Placebo / pre-trend: λ1 + λ2 (future fires) must have a CI that includes 0; if not, the detection is not claimed.
- Secondary (reported regardless): same for earners, mean income, median income; β2 (two years after);
  heavily affected SA2s only (D >= 25% in some year) event-time means; Black Summer (FY2019-20) only.
- Comparison: the council-level bound from Day 4 (income fall < 1.6% per 10 pp affected).
