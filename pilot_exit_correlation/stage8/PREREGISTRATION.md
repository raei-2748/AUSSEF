# Pre-registration: stage 8, did towns cut off in Black Summer change differently, 2016 to 2021? (exploratory)

**Date registered:** 2026-09-22. Written before any 2016–2021 change was computed. Only file lists and
column names were inspected.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Status: exploratory
This is a first look at socioeconomic change, not proof of impact. Reasons:
- About 20 towns were cut off.
- Most were cut off by one fire complex, so they are not independent.
- The 2021 Census was taken in August 2021, during COVID-19 lockdowns and 18 months after the fires.

No causal or lives-saved claims will be made.

## Question
Between the 2016 and 2021 Censuses, did towns fully cut off by a Black Summer fire change differently
from towns that were **burned but not cut off**? The comparison is designed to separate "being
trapped" from "being burned".

## Groups (towns with ≥ 2 exits, stage-1/2 exit paths, S0 closure, 20 km ring)
Black Summer fires are part-A fire families with a start date from 2019-07-01 to 2020-06-30.

- **Cut off:** a Black Summer fire isolated the town.
- **Burned, not cut off (primary comparison):** a Black Summer fire closed ≥ 1 exit, but none isolated the town.
- **Not touched (secondary comparison):** no Black Summer fire closed any exit.

## Linking 2021 towns to 2016 towns
- Each 2021 UCL polygon is linked to the 2016 UCL polygon it overlaps most (both in EPSG:3577).
- Link quality is IoU = intersection area ÷ union area.
- A town is analysed only if **IoU ≥ 0.7**, so that change is not a boundary redraw. Towns failing this are counted and listed.
- Sensitivity: IoU ≥ 0.5 and IoU ≥ 0.85.

## Outcomes (change from 2016 to 2021)
1. **Primary:** population growth (%) = (persons 2021 − persons 2016) ÷ persons 2016 × 100 (G01 `Tot_P_P`).
2. Change in median weekly household income, nominal % (G02 `Median_tot_hhd_inc_weekly`).
3. Change in the employment-to-population ratio, in percentage points: `P_Tot_Emp_Tot` ÷ (`P_Tot_LF_Tot` + `P_Not_in_LF_Tot`) (2016 G43B, 2021 G46B).
4. Change in the unemployment rate, in percentage points: `P_Tot_Unemp_Tot` ÷ `P_Tot_LF_Tot`.

A value is missing (never zero) when a denominator is 0 or a median is not published.

## Decision (primary outcome, primary comparison)
- Estimate: median(cut off) − median(burned, not cut off).
- 95% CI: bootstrap over towns, 2,000 resamples, seed 20260921, resampling within each group.
- Also reported: two-sided Mann–Whitney p.
- **WORSE** if the whole CI is < 0.
- **BETTER** if the whole CI is > 0.
- **NO CLEAR DIFFERENCE** otherwise.
- **NOT EVALUABLE** if fewer than 10 cut-off towns pass the IoU filter.

## Secondary (descriptive, no verdict)
- Outcomes 2–4 (Holm-adjusted p-values).
- All outcomes against the not-touched group.
- IoU thresholds of 0.5 and 0.85 for the primary outcome.

## Inputs (downloaded with the user's approval on 2026-09-22)
- ABS 2016 Census GCP UCL NSW data pack: `2016_GCP_UCL_for_NSW_short-header.zip`, SHA-256 `2455e718330840eeb83a1b0cca53174366b31d5a2a451e9efa0691298db76b16`.
- ABS ASGS 2016 UCL boundaries: `1270055004_ucl_2016_aust_shape.zip`, SHA-256 `692668cee6e0d0a5db7b46970118b5c775ee283893d9d2f50c99535e0335ffd1`.
- The 2021 data pack and boundaries (frozen in `../RUN_LOG.md`), the stage-1 exit paths, and the stage-1 inputs (all hash-verified).

## Caveats
- COVID-19 affected the 2021 Census, especially jobs and where people were on Census night. COVID should affect both groups, but not necessarily equally.
- One fire complex dominates the cut-off group. Towns are not independent, so the CIs are optimistic.
- There is no pre-fire trend check (2011 data were not obtained).
- Nominal income is not adjusted for inflation. Both groups face the same inflation, so the comparison between groups is unaffected.
