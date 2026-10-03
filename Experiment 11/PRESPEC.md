# Experiment 11 pre-specification: the impact clock (channels at different time horizons)

Written 2 Oct 2026, before any horizon-specific value is computed. Hash-locked in LOCK.txt. Later changes are
numbered deviations in FINDINGS.md.

## Question
Bushfire harm reaches people through channels that take different times to act (Experiment 8 mechanism table:
"days-weeks", "months", "1-2 years", "3+ years"). Measuring every channel in the same window can miss a channel that
peaks earlier or later. For each channel: at which horizon after the fire does it move with fire size, if at all?

## Rows and dose
The 218 council x fire rows (Experiment 9). Dose D = log(1 + dwellings inside the fire outline per 1,000 council
dwellings) (`log_homes_in_fire_per_1000`, available for all rows; it is the variable that predicts homes destroyed).
m0 = month of `first_fire_start`; F = fire financial year (start year).

## Horizons
Monthly/quarterly channels: H0 = months 0-3 after m0, H1 = 4-12, H2 = 13-24, H3 = 25-48.
Annual (financial-year) channels: H0 = FY F, H1 = FY F+1, H2 = FY F+2, H3 = FY F+3.
**Expected peak horizon (fixed now by rule from the mechanism table's time scale):** "days-weeks" or "months" -> H0;
"1-2 years" -> H2 for monthly channels (13-24 months) and H1 for annual channels (FY F+1); "3+ years" -> H3.

## Channels (outcome at each horizon; "excess" = minus the median of the same quantity in NSW councils with no row in
## fire year F, same calendar window)
| # | Channel (mechanism, pillar) | Data (all already on disk) | Outcome at horizon h | Expected sign | Primary horizon |
|---|---|---|---|---|---|
| C1 | Tourism shutdown (#2, IL, months) | TfNSW permanent traffic stations, daily | council median over stations of log(mean daily volume in h / same calendar months 12 and 24 months earlier) | down | H0 |
| C2 | Rents (#5, SL, 1-2 yrs) | DCJ new-bond median rent by council, quarterly, 2017Q3-2026Q2 | mean log rent of the quarters in h minus mean log rent of the 4 quarters before the fire quarter | up | H2 |
| C3 | Domestic violence (#7, SL, 1-2 yrs) | BOCSAR DV-related assault, monthly by council | log(mean monthly count in h / mean monthly count in months -24..-1) | up | H2 |
| C4 | Grants per resident (#4, FP, 1-2 yrs) | OLG grants % x total revenue / population, FY 2013-2024 | log(grants per resident in FY h) minus mean log over FY F-2, F-1 | up | H1 |
| C5 | Fire-related grant share (#4, FP, 1-2 yrs) | Experiment 10 audited statements (v3 FP2 line rule) | share in FY h minus mean share over available FY F-2, F-1; excess vs the 25 comparison councils | up | H1 |

Descriptive only (no primary test): C6 capital-spending share (#15/#16, 3+ yrs; statements, coverage too thin at H2-H3)
and C7 rebuild (#6, 3+ yrs): cumulative new houses approved above the 12-month pre-fire rate per home destroyed, at
6, 12, 24, 36 and 48 months, rows with >= 5 homes destroyed and m0 >= July 2019. Income, earners, businesses,
unemployment and population paths are not re-run (Experiment 7 Days 5-10 already report them by year).

## Statistics
- For each channel x horizon: Spearman rho between D and the excess outcome over rows with data; 95% CI by council
  cluster bootstrap (2,000 resamples); permutation p by shuffling D across rows within the same fire season (2,000).
- **Primary tests:** the five (channel, primary horizon) pairs above. "Detected" if Holm-adjusted p < 0.05 across
  these five AND rho has the expected sign. Otherwise "not detected; rho CI [..]".
- All other horizons are descriptive (the clock curves), shown with CIs, no claims.
- **Sensitivity (pre-set):** (a) without Black Summer rows (F = 2019), because its months 4-24 coincide with COVID
  (from March 2020) and its years 2-3 with the 2022 floods; (b) traffic and DV with D replaced by log share burned.

## Outputs
results/CLOCK.csv (channel, horizon, n, rho, CI, p, Holm p for primary), results/CLOCK_ROWS.csv (row values),
figures/fig1_impact_clock.png (rho by horizon per channel, expected peak marked), FINDINGS.md in plain English.
