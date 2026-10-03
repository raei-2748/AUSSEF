# Experiment 13 findings: measuring fire effects where people were actually exposed

2 Oct 2026. Rules locked first (`PRESPEC.md`, `LOCK.txt`, 22:34). Scripts: `exposure/build_exposure.py`,
`income_ato/build_ato.py`, `run_channels.py`, `e13lib.py`, `summarise.py`. All numbers: `results/ALL_RESULTS.csv`.
Independent audit: `audit/AUDIT.md` (see the end). Sources: `bibliography/parts/exp13_fine_grained_2026-10-02.csv`.
Property values were not done (decision 3 Oct 2026, section 5).

## How the tests work (in one paragraph)
For every small area (postcode, suburb or SA2) and every fire year we measured **H = the share of its homes that sit
inside a fire outline** (Census 2021 mesh blocks). Each area is compared only with **unexposed areas in the same SA4
region in the same year**, which cancels region-wide shocks (COVID, JobKeeper, the regional rent and tourism swings,
the 2022 floods). Two samples: **P = pre-COVID fires** (2009-10 to 2018-19, incl. Coonabarabran Jan 2013,
Winmalee / Yellow Rock / Catherine Hill Bay Oct 2013, Tathra 2018, Tingha 2019), followed only to June 2019; and
**B = Black Summer** (2019-20). The main number is the average effect in the two years after the fire year, **per 10
percentage points of homes inside the fire**; "x10" gives a fully burned area. Placebo: the same model with every fire
moved 24 months earlier (should show nothing). Holm correction across the 10 primary tests.

**Power warning (stated in the prespec before results):** before COVID, few postcodes or SA2s had many homes inside
fires (46 postcode-years with H >= 1% over ten years, versus 65 postcodes in Black Summer alone). Pre-COVID
postcode/SA2 estimates are therefore wide; suburbs are the fine unit where pre-COVID fires are informative.

## Results by channel (primary tests in bold)

| Channel (unit) | Sample | Effect per 10 pp of homes inside the fire, years 1-2 [95% CI] | Placebo (24 months earlier) | Verdict | COVID checks |
|---|---|---|---|---|---|
| **Total taxable income (postcode, ATO)** | P | +0.8% [-2.7, +4.4] | passes | not detected at this scale | - |
| **Total taxable income (postcode, ATO)** | B | -1.2% [-3.1, +0.8] | passes | not detected at this scale | pre-COVID sign differs |
| **Wage earners (postcode, ATO)** | P | +1.0% [-0.8, +2.8] | passes | not detected | - |
| **Wage earners (postcode, ATO)** | B | -0.7% [-2.3, +0.9] | passes | not detected | pre-COVID sign differs |
| Total income (SA2, ABS PIA), secondary | B | **-1.6% [-2.6, -0.7]** | not estimable* | suggestive (down) | no pre-COVID data |
| **Unemployment rate (SA2, SALM)** | P | +0.11 pts [-0.83, +1.05] | passes | not detected | - |
| **Unemployment rate (SA2, SALM)** | B | -0.09 pts [-0.29, +0.12] | **fails** (-0.20 [-0.36, -0.03]) | not detected | fails placebo |
| **Accommodation & food businesses (SA2, CABEE)** | P | +8.6% [-6.4, +26.0] | passes | not detected | - |
| **Accommodation & food businesses (SA2, CABEE)** | B | +3.6% [-1.2, +8.6] | passes | not detected | same sign pre-COVID |
| **Domestic-violence assault (suburb, BOCSAR)** | P | -2.3% [-11.2, +7.5] | passes | not detected | - |
| **Domestic-violence assault (suburb, BOCSAR)** | B | -0.5% [-3.2, +2.4] | passes | not detected | same sign pre-COVID |

All ten primary tests have Holm p = 1.0. **Nothing is detected at the pre-registered standard.**

### 1. Income and earners (ATO postcode 2010-11 to 2022-23; ABS PIA SA2 to 2022-23)
- Black Summer, postcode: total taxable income -1.2% per 10 pp in years 1-2, and the time path keeps falling:
  fire year +0.9%, year 1 -0.2%, **year 2 -2.1% [-3.9, -0.3], year 3 -2.7% [-5.0, -0.3]** (time path, not the primary
  test). Wage earners drift the same way (-0.4%, -1.0%, -1.3% by year 3; CIs include 0). Income per person -0.8%
  [-2.5, +0.8]. So the fall, if real, is again more "fewer earners / less income in total" than lower pay, as in
  Experiment 7 Day 9.
- ABS PIA by SA2 (secondary, now extended to 2022-23): total income -1.6% [-2.6, -0.7] in years 1-2, earners -0.9%
  [-2.2, +0.5], median income +0.4% [-2.8, +3.7]. This repeats Experiment 7 Day 9 with the stricter same-SA4
  comparison. *The 24-month placebo cannot be estimated here: the PIA panel has only two years before the fire
  (2017-18, 2018-19), so the two fake terms add up to the area's own fixed effect and one is dropped. The +0.7%
  [-0.9, +2.4] in `ALL_RESULTS.csv` is only the one-year pre-trend term, not the pre-specified placebo (found by the
  audit, deviation D2).
- Severity dose (share of homes on land burned at high or extreme severity): total income -2.9% per 10 pp
  [-8.1, +2.6]: larger point estimate than H, but too few severely burned areas to tell apart from zero.
- Pre-COVID fires: no fall (+0.8% [-2.7, +4.4]); the CI is wide (few exposed postcodes). Because the pre-COVID sign
  differs, the pre-registered rule says the Black Summer income fall **cannot be separated from COVID/regional shocks**.
  The postcode version survives the same-SA4 comparison and the placebo; the SA2 version has no usable placebo.
- Literature check: Black Saturday studies report about -8% for employed people in affected areas (Ulubasoglu &
  Beaini 2019). For a fully burned area our Black Summer CI is -27% to +8% (postcode, years 1-2) and -23% to -7%
  (SA2 PIA): consistent with falls of that size. Pre-COVID postcodes: -24% to +54%: uninformative.
- Business income (secondary): pre-COVID fires -6.5% [-11.9, -0.8] (placebo passes); Black Summer +1.8% [-8.0, +12.7].
  One of many secondary tests; not adjusted for multiple testing.

### 2. Unemployment and under-employment
- SA2 unemployment rate (SA2 count grows from 439 to 623 over time as SALM coverage widens; every SA2 with homes
  inside a fire has data from 2010-11): not detected in either sample; Black Summer upper limit +0.12 points per 10 pp (about +1.2
  points for a fully burned SA2). The Black Summer placebo fails slightly (exposed SA2s were already drifting down
  relative to their region), so even this null should be read with care.
- Under-employment and hours worked: **not available below state level** (ABS publishes them for states and capital
  city / rest of state only; SA4 has only modelled labour force status). Not tested.

### 3. Businesses by industry (SA2, June counts 2015-2025)
Black Summer, per 10 pp, years 1-2: accommodation & food **+3.6%** [-1.2, +8.6]; construction +1.3% [-1.3, +4.0];
agriculture +1.7% [-0.3, +3.7] (placebo fails); retail +1.9% [-2.7, +6.7]; all industries -0.4% [-2.1, +1.3];
non-employing share -0.4 points [-1.0, +0.2]. Sectors do not cancel out: none moves clearly. Entries and exits are
not published below state level (only counts), so business turnover cannot be seen. Pre-COVID: all CIs wide.

### 4. Domestic violence (BOCSAR, suburb; 4,348 of 4,520 suburbs matched)
- DV assault: not detected in either sample. Black Summer upper limit +2.4% per 10 pp.
- Reporting check (fixed in the prespec): in the Black Summer fire year itself DV assault was -3.1% [-7.7, +1.7] per
  10 pp, while non-DV assault rose (+5.7% [+0.0, +11.7]) and malicious damage barely moved (-1.6% [-5.7, +2.7]).
  They did not all fall together, so there is no clear sign of a reporting collapse at suburb level.
- AVO breaches (secondary): pre-COVID fires **+13.4% [+2.0, +26.1]** per 10 pp (placebo passes); Black Summer -2.4%
  [-9.3, +5.0]. Not adjusted for multiple testing and not repeated in Black Summer; worth a dedicated test, not a
  finding.
- Postcode level (secondary): Black Summer DV assault -7.0% [-13.8, +0.4]: if anything fewer recorded incidents,
  consistent with displacement or reduced reporting.
- Limit: suburb names shared by two NSW suburbs were dropped (rule fixed in advance); this loses e.g. Yellow Rock
  (Blue Mountains), one of the most exposed suburbs in October 2013. Post-hoc (audit): BOCSAR writes such names as
  "Back Creek (Bland)" and the SAL file as "Back Creek (Bland - NSW)"; matching them adds 172 suburbs (8 with Black
  Summer homes inside the fire) and moves the Black Summer DV estimate to -0.9% [-3.6, +1.8]: still not detected.

### 5. Property values: not done
Decision 3 Oct 2026 (relayed from Ray via the main session): the Valuer General sales files will not be downloaded;
measurement is frozen. The property model in PRESPEC 4.5 was never run, so the primary family stays at 10 tests.

### 6. Local GDP
No official GDP exists below state level. Council GRP from economy.id / NIEIR is modelled from jobs and industry
mix, so it is not independent evidence; not used (`coarse_gaps/GAPS.md`).

### 7. Coarse-only channels (gaps)
Mental health (AIHW, SA3) and smoke health (HealthStats, health district) are far coarser than fire footprints; not
tested. See `coarse_gaps/GAPS.md`.

## What it means
- Measured where homes were actually inside the fire, and compared within the same region and year, the
  socioeconomic channels are still **not detected at this scale**, but the limits are now much tighter and specific.
- The one consistent signal is **income in Black Summer areas**: postcode and SA2 data both point down (about -1 to
  -2% per 10 pp of homes inside the fire, growing to about -2.7% by year 3 at postcode level), driven by fewer
  earners more than lower pay. It passes the same-region and placebo checks but **not** the pre-COVID check
  (pre-COVID fires were too small to show it either way). Honest reading: plausible, not proven.
- No evidence that unemployment, tourism businesses or recorded domestic violence rose in the exposed small areas.

## Deviations and post-hoc items
- C1 (code fix, no spec change): businesses crashed on `p.ne` (a pandas method name); fixed to `p['ne']`.
- D1: verdict wording. The COVID-check column in `ALL_RESULTS.csv` is filled for every Black Summer row, but it is
  only meaningful for results whose CI excludes 0.
- D2 (found by the audit): when a model drops one of the two placebo terms, `e13lib.run_channel` averaged the term
  that remained instead of stopping. This affects only the PIA (SA2 income) placebos, now marked "not estimable".
  The code was not changed after the audit; the write-up was corrected.
- Year labels in `ALL_RESULTS.csv` use the starting year (e.g. "2014-2022" = 2014-15 to 2022-23).
- Binary-dose rows (H >= 10%) report the effect of the indicator ("full" columns), not per 10 pp. Several have only
  1-3 exposed units before COVID and should be ignored.

## Audit (`audit/AUDIT.md`)
A fresh reviewer re-derived, with its own code, the exposure doses (exact match), the ATO panel (8,215
postcode-years, exact), ATO income in both samples, suburb DV in Black Summer, SA2 PIA income and SA2 unemployment,
with their placebos. All match to the reported decimals. The exception is the PIA placebo, which cannot be estimated
(D2). The lock was intact except for the logged business fix C1. No issue changes a primary verdict.
