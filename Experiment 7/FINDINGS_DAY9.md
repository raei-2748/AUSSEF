# Experiment 7, Day 9: longer timeline (up to 5 years) with a sharper dose

Date: 1 Oct 2026. Rules locked first: `PRESPEC_DAY9.md` (LOCK_DAY9.txt). Script: `day9_long_run.py`; results
`results/DAY9_LONG_RUN.csv`, `DAY9_PATHS.csv`. No new downloads.

Dose: share of an SA2's homes inside the fire outline. In practice this is a Black Summer study: other seasons put
almost no homes inside fire outlines (max 2-17% of an SA2 vs up to 100% in 2019-20). 57-72 SA2s treated.
Fixed effects swept out by alternating projections (the dummy-variable version gave unstable standard errors with
this many lags; same point estimates), SEs clustered by SA3.

## Results per 10 percentage points of an SA2's homes inside the fire
| Outcome | Years 2-5 after (income: year 2) | 95% CI | Placebo | Verdict |
|---|---|---|---|---|
| Total income | **-1.6%** | -2.7% to -0.4% | passes | **Detected** (Holm p = 0.026) |
| Median income | -0.4% | -1.1% to +0.4% | passes | not detected |
| Unemployment rate | -0.3 pts | -0.7 to +0.1 | passes | not detected |
| Income-support per 1,000 | -2.5 (fewer, not more) | -4.2 to -0.8 | passes | not "worse" |
| Businesses | +2.5% | -0.2% to +5.2% | passes | not detected |

Time path of total income: -0.3% (fire year), -0.9% (year 1), -1.6% (year 2): it builds up.

## Post-hoc check (not pre-registered): why did total income fall?
Number of income earners -1.2% [-2.6%, +0.2%] at year 2; mean income per earner -0.3% [-1.7%, +1.0%].
So the fall is mostly fewer earners, not lower pay. Together with fewer welfare recipients per resident (the
denominator is fixed Census 2021 population), the most consistent reading is that people left heavily burned
areas, rather than that the people who stayed got poorer. This matches US evidence of out-migration after the most
destructive fires (McConnell et al. 2021). It is a reading, not proven: we cannot follow individuals.

## Caveats
- Essentially one season (Black Summer), with COVID (2020-21) and the 2022 floods in the post-fire years.
- Income data end in 2021-22, so income is only followed 2 years.
- Dwelling counts are Census 2021 (after Black Summer), so the dose understates the worst-hit SA2s.
