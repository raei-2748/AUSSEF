# Experiment 7, Day 1: a better impact measure (Y v2) — rules fixed before any result

Written 2026-09-30, before computing any Y v2 value or comparing anything with fire size.
Locked by SHA-256 in `LOCK_DAY1.txt`. Any change after the lock is listed in FINDINGS as a deviation.

## Why
Y v1 measures each indicator as "change in this council minus the median change in NSW councils with no fire
of 100 ha or more". That comparison has three weaknesses: (1) one year before vs one year after, so ordinary
year-to-year noise in a single council goes straight into Y; (2) the comparison councils are mostly
metropolitan, so shocks that hit rural councils differently (drought 2018-19, COVID 2020) leak into Y;
(3) Y_class is percentile-based, so half the rows are labelled Moderate or worse even if all were pure noise.

## What changes (only the counterfactual; the indicators, windows, signs and aggregation stay as in v1)
Imputation estimator (Borusyak, Jaravel & Spiess 2024; Gardner 2021), one model per indicator series:

    y[i,t] = a[i] + b[g(i),t] (+ c[i,season] for quarterly series) + e[i,t]

fitted by OLS on CLEAN council-periods only. The fire effect for a master row is
tau = observed y − predicted y at the row's window. g = the council's OLG 2018-19 classification collapsed to
three groups: Metro (Metropolitan, Metropolitan Fringe), Regional (Regional Town/City), Rural (Rural, Large Rural).
z = sign × tau / sigma, where sigma = SD of leave-one-out residuals of clean periods (same window shape).

Clean = not in FY F..F+2 of any council-FY with burned share >= 0.5% (fires.csv pieces summed; NSW Oct 2013
fires from extra_fire_rows.csv added), and not in FY F..F+2 of any of the 218 master rows (so every master
row's tau is out of sample).

| Pillar | Indicator (sign: higher = worse) | Series | Window |
|---|---|---|---|
| DL | homes destroyed per 1,000 dwellings | master column, unchanged | - |
| IL | total personal income (−) | log total_income_aud_fy | FY F |
| IL | business count (−) | log biz_total_june | June F+1 |
| FP | cash cover (−) | cash_cover_months | mean of FY F, F+1 |
| FP | services share of spending (−) | service_share_pct | FY F+1 |
| FP | renewals ratio (+) | renewals_ratio_pct | FY F+1 |
| SL | income-support recipients per 1,000 (+) | DSS quarterly, harmonised as src/vulnerable | quarter q0+1 |
| IL (candidate) | night-time lights, fire pixels removed (−) | log ntl_mean_rad_excl_fire, quarterly | quarter q0+1 |

F = financial year of first_fire_start (label = FY start year); q0 = its calendar quarter.

## Variants and the selection rule (X-free)
- V1: the workbook's Y (baseline).
- V2a: imputation, one NSW-wide period effect b[t]; 7 v1 indicators.
- V2b: imputation, group-specific period effect b[g,t]; 7 v1 indicators.
- V2a+NTL, V2b+NTL: as above plus night lights in IL.
Aggregation for all: v1's (percentile rank across rows -> pillar mean -> Y = mean of >= 2 pillars).

Criterion: Spearman(S, burned share) with council-cluster bootstrap (2,000; seed 20260930), where
S = mean of the IL, FP, SL pillar ranks (rows with >= 2 of them). DL is identical in every variant, so it is left
out of the criterion. The chosen variant is the one with the highest criterion among those that pass the
placebo check; V1 stays if no V2 variant beats it.

Placebo check (V2 variants): shift every master row back 3 financial years (pseudo fire F−3, q0−12), compute
leave-one-out z at the pseudo window where it is clean, aggregate the same way (no DL). Pass = 95% interval of
Spearman(placebo S, burned share) includes 0.

No pre-fire predictor (H, E, V, F, SEIFA, income, finance) is used anywhere in Day 1.

## Severity classes v2 (descriptive, for the chosen variant)
S_z = mean of available IL, FP, SL pillar z (pillar z = mean of its indicator z). Null = S_z at clean pseudo
windows (every clean council-FY used as a pseudo fire, q0 = first quarter of the FY).
- 4 Extreme: S_z above the null 99.5th percentile, or >= 100 homes destroyed
- 3 Severe: above the 97.5th, or >= 10 homes destroyed, or >= 2 deaths
- 2 Moderate: above the 90th
- 1 Light: indistinguishable from normal year-to-year variation
(the v1 direct-loss floors are kept; one death raises one level, at most 3).

## Reported regardless of outcome
Per-indicator dose-response (mean z by burned-share bin <1%, 1-5%, 5-20%, >=20%, bootstrap CIs) and placebo;
v1 vs v2 per indicator; event-study profile (tau at relative years −3..+3) for councils >= 20% burned;
Black Summer vs other fires.
