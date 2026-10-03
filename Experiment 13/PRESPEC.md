# Experiment 13 pre-specification: fine-grained, COVID-robust tests of the socioeconomic channels

Written 2 Oct 2026 BEFORE any outcome (income, unemployment, business count, crime count, sale price) was read for
any fire-exposed area or related to fire exposure in this experiment. Hash-locked in `LOCK.txt` (SHA-256).
Anything decided after the lock is a numbered deviation in `FINDINGS.md`; post-hoc checks are labelled "post-hoc".

## 0. What I knew or looked at before freezing (disclosure)
- Earlier results are known: Experiment 7 (SA2 income, unemployment, welfare, businesses: mostly not detected; total
  income -1.6% per 10 pp of homes inside the fire at year 2, mostly fewer earners), Experiment 11 (impact clock),
  Experiment 12 (spillover). So the SA2 channels here are not "blind"; the new parts are the postcode and suburb
  data, the pre-COVID fires (2009-2018), the same-region comparison and the 24-month placebo.
- Looked at: column headers and the first data rows (ACT postcodes only) of the ATO Table 6 files; header rows of
  ABS PIA Table 1, POA/SAL allocation files, BOCSAR suburb/postcode CSVs (offence list), CABEE cube headers.
- Computed before freezing (outcome-free): the exposure table (`exposure/build_exposure.py`): how many postcodes,
  suburbs and SA2s had homes inside fire outlines in each fire year (`exposure/out/exposure_summary_*.csv`). Seen:
  Black Summer put 15,149 Census-2021 dwellings inside outlines (65 postcodes with H >= 1%, 16 with H >= 10%;
  632 suburbs >= 1%, 419 >= 10%; 54 SA2s >= 1%, 19 >= 10%). Pre-COVID fire years 2009-10 to 2018-19 are much
  smaller at postcode level (0-12 postcodes >= 1% per year; only 2013-14 and 2018-19 have any postcode >= 10%,
  2 each) but not at suburb level (2013-14: 125 suburbs >= 1%, 45 >= 10%). So sample P is expected to be weak for
  postcode and SA2 channels and informative mainly for suburb channels (DV, property). This is stated now so that
  wide pre-COVID CIs are not later read as anything but low power.

## 1. Exposure (dose), all channels
Census 2021 mesh blocks (MB), residents and dwellings spread evenly over each MB's area.
- **H (primary)**: share of a small area's dwellings inside the union of the outlines of fires that started in fire
  year t (July-June, labelled by starting year). "Homes inside the fire".
- **R (secondary)**: share of residents inside or within 1 km of the outlines (Experiment 7 method).
- **S (secondary, income channel, Black Summer only)**: share of dwellings on land mapped high or extreme severity
  (FESM 2019-20 classes 4-5). No FESM exists for the 2013 fires.
- Fire outlines: Geoscience Australia historical boundaries (NSW, non-prescribed) for fires starting before
  1 Jan 2015; project master fire file from 1 Jan 2015. Fire years 2006-07 to 2024-25.
- Small areas: postcode (POA 2021, matched to ATO/BOCSAR postcode by code), suburb (SAL 2021, matched to BOCSAR
  suburb names, rule in 4.4), SA2 (ASGS 2021). Each area's region (SA3, SA4, GCCSA) = the one holding most of its
  dwellings. NSW only. Areas with zero Census dwellings are dropped.
- Known limit: Census 2021 counts were taken after Black Summer, so dwellings already destroyed are missing; H
  understates the worst-hit areas (also true in Experiment 7 Day 9).

## 2. Model (same for every channel)
Annual panel of small area a and outcome year y (financial year, July-June, unless stated):

  outcome[a,y] = area effect[a] + (SA4 region x year) effect + sum over k of beta_k x dose[a, y-k] + error

- **SA4 x year effects** = the COVID solution (b): exposed areas are compared only with unexposed areas in the same
  SA4 region in the same year, which cancels regional COVID, JobKeeper, tourism-boom, flood and drought shocks that
  hit the whole region.
- k = 0 (fire year) to 3. Continuous dose (0-1); results reported **per 10 percentage points** of the dose
  (coefficient x 0.1), and also scaled to a fully exposed area (x 1.0) to compare with the literature.
- Linear outcomes (log or rate): OLS with fixed effects (pyfixest feols). Count outcomes (businesses, crimes, sales):
  Poisson pseudo-maximum likelihood with the same fixed effects (pyfixest fepois); effect reported as % change
  = exp(coef x 0.1) - 1.
- Standard errors clustered by SA3 (CRV1). 95% CIs.
- **Primary estimand** for each channel and sample: the average of beta_1 and beta_2 (the two years after the fire
  year), per 10 pp. beta_0 and beta_3 are reported as the time path.

### 2.1 Two samples
- **P (pre-COVID, primary for credibility)**: outcome years up to 2018-19 (ending June 2019); dose = all fires in fire
  years up to 2018-19 (outcome-year windows per channel in section 4). Includes the January 2013 fires (Warrumbungle
  etc.), the October 2013 Blue Mountains / Lithgow / Port Stephens fires, and the 2015-2018 fires (Tathra 2018,
  Sir Ivan 2017 etc.). No COVID, no Black Summer, no 2022 floods in any post-fire year.
- **B (Black Summer)**: outcome years from 2014-15 to the last full year available; two doses: Black Summer
  (fire year 2019-20) with its own lags k = 0..K (K = last year - 2019, up to 5), and all other fire years with lags
  0..3 as controls. Primary = average of the Black Summer beta_1 and beta_2 (2020-21 and 2021-22).

### 2.2 Placebo (COVID solution c): fire dates moved 24 months earlier
- Fake dose[a, t] = real dose[a, t+2]. Same model, fake lags k = 0 and 1 only (both fall before the real fire).
- P: drop every area-year that falls 0-3 years after a real fire year in which the area had H >= 0.001 (so the
  fake effect is never estimated on post-fire years). Fake doses use only fires up to 2018-19. B: outcome years up to 2018-19 only, other-fire doses kept as controls.
- **Placebo estimand** = average of fake beta_0 and fake beta_1, per 10 pp. Passes if its 95% CI includes 0.

### 2.3 Verdicts (fixed now)
For each primary test:
- **Detected**: CI excludes 0, Holm-adjusted p < 0.05 across the primary family (section 5), AND the placebo passes.
  The direction (harm or the opposite) is stated.
- **Suggestive**: CI excludes 0 but Holm p >= 0.05, or the placebo fails.
- **Not detected at this scale**: CI includes 0. The write-up gives the CI and the largest effect the CI allows for
  a fully exposed area. The words "no impact" are never used.
- **Survives the COVID checks** (B results only): same-SA4 comparison (built in), placebo passes, AND the P estimate
  has the same sign (it need not be significant). A B result that fails any of these is reported as "not separable
  from COVID / regional shocks".

## 3. Literature benchmarks to compare against (stated before seeing results)
- Black Saturday studies: incomes of affected people -8% to -18% (individual panels). At area level the expected
  effect is that share times the exposed share; with H = 100% the area-level fall should be of that order if every
  resident were affected. A CI excluding falls of 8% at H = 100% is reported as "inconsistent with the Black
  Saturday individual-level falls at area level".
- Akter & Grafton 2025: losses concentrated in severely burned peri-urban areas -> the S (severity) dose.

## 4. Channels, data and outcomes

### 4.1 Income and earners: ATO Taxation Statistics, Individuals Table 6, by postcode
- Files: 2010-11 to 2022-23 (13 files, downloaded 2 Oct 2026). The "all individuals by postcode" sheet of each
  file (2010-11 sheet 6a; 2011-12 sheet 6A; 2012-13 "Postcode only"; 2013-14 onward Table 6B).
- Outcomes (postcode x income year): **Y1 log total taxable income ($)** [primary]; **Y2 log number of
  salary/wage earners** [primary]; Y3 log individuals lodging; Y4 log salary/wage income ($); Y5 log taxable income
  per individual; Y6 asinh(total business income $, primary + non-primary production) [secondary].
- NSW postcodes (state = NSW) matched to POA 2021. Keep postcodes with >= 100 individuals in every year of the
  sample window (balanced; suppressed or missing cells drop the postcode, missing stays missing).
- Windows: P = 2010-11 to 2018-19; B = 2014-15 to 2022-23.
- Secondary (B only): S dose; ABS Personal Income in Australia (PIA) by SA2, 2017-18 to 2022-23 (2017-18 from the
  2024 release already on disk, 2018-19 to 2022-23 from the 2025 release Table 1; ASGS 2021): log total income,
  log earners, log median income. This extends Experiment 7's SA2 income to year 3 (2022-23).

### 4.2 Unemployment: DEWR SALM unsmoothed SA2 (on disk)
- Outcome: **unemployment rate (%) per SA2 per financial year** = sum of unemployed over the four quarters / sum of
  labour force (quarters Sep, Dec, Mar, Jun) [primary]. Linear model, effect in percentage points per 10 pp.
- Windows: P = 2010-11 to 2018-19; B = 2014-15 to the last financial year with all four quarters.
- Underemployment / hours: checked 2 Oct 2026 (ABS Labour Force Detailed cube list): hours worked and
  underemployment are published only for Australia, states and capital city / rest of state; SA4 has only modelled
  labour force status. No small-area under-employment data exist; reported as a gap, not tested.

### 4.3 Businesses by industry: ABS CABEE SA2 counts (on disk, June stocks)
- Industries separately: **H Accommodation and food services (tourism)** [primary]; E Construction, A Agriculture,
  forestry and fishing, G Retail trade, all industries, and the non-employing share (OLS, level) [secondary, always
  reported next to the primary so sectors that move in opposite directions are visible].
- June y count is the end of financial year y-1 (so June of the year after the fire's June = k = 1).
- Each June from the latest release holding it (Experiment 7 Day 7 rule); ASGS 2016 years kept only for SA2s with
  identical code and name in ASGS 2021 and ratio-linked per SA2 x industry at the overlap Junes (2019, 2017) as in
  Experiment 7; if the overlap count is 0 the earlier years are dropped for that SA2 x industry.
- Poisson model. Windows: P = June 2015 to June 2019 (fire years 2014-15 to 2017-18 identify it; short); B = June
  2016 to June 2025.
- Entries and exits: checked 2 Oct 2026, ABS publishes entries/exits only for Australia and states (data cube 1);
  SA2 and LGA cubes give counts only. Net change in counts is what can be tested; reported as a gap.

### 4.4 Domestic violence: BOCSAR recorded incidents by month, by suburb (primary) and postcode (secondary)
- Outcomes: **domestic-violence-related assault incidents** per suburb per financial year [primary]; breach of
  apprehended violence order [secondary]; non-domestic assault and malicious damage [reporting check, see below].
- Suburb matching: BOCSAR suburb name, upper case, matched to SAL 2021 NSW names with any bracketed qualifier
  removed (e.g. "Bellevue (NSW)" -> "BELLEVUE"); names matching more than one SAL are dropped. Match rate reported.
- Keep suburbs with Census dwellings >= 50 and at least one DV incident over the whole data period. Complete
  financial years only.
- Poisson model. Windows: P = 2009-10 to 2018-19; B = 2014-15 to 2024-25.
- Reporting check (fixed now): if DV, non-DV assault and malicious damage all fall in the fire year (k = 0) in
  exposed suburbs, the fall is read as disrupted policing/reporting, not fewer incidents.

### 4.5 Property values: NSW Valuer General bulk sales (Ray downloads yearly zips 2010-2022 in a browser)
- Records: residential sales (the record's primary purpose / nature marked residential, or zoning residential),
  contract date, price, locality and postcode. Sales < $10,000 dropped.
- Outcomes: **log sale price** at sale level with suburb (locality matched to SAL as in 4.4) and SA4 x year effects
  and the suburb's dose lags [primary]; number of residential sales per suburb-year and number of vacant-land sales
  per suburb-year (Poisson) [secondary; vacant-land sales are where burned lots would appear].
- Windows: P = 2010-11 to 2018-19; B = 2015-16 to 2021-22 (last complete year in 2010-2022 files).
- Runs only when the files arrive; same rules.

### 4.6 Local GDP
There is no official ABS GDP by council or small area. Council "gross regional product" from economy.id / NIEIR is
modelled (it allocates state output to councils using jobs and industry mixes), so it cannot show a local fire
effect independently of the inputs. Not used as evidence unless Ray decides otherwise.

### 4.7 Coarse-only channels (known gaps unless a fire-matched version is found)
Mental health (AIHW Medicare mental-health services, SA3, annual) and smoke health (NSW HealthStats, local health
district) are only available at areas far larger than fire footprints; listed as gaps, not tested here.

## 5. Primary family and multiple testing
Primary tests (each in sample P and sample B = 10 tests, 12 when property runs): income Y1, earners Y2,
unemployment rate, accommodation-and-food businesses, DV assault (suburb), and (later) log sale price.
The first ten are Holm-adjusted together when they are run; when property runs, Holm is recomputed over twelve and
both versions are reported.
Holm adjustment over all primary tests that run. Placebos are not part of the family.

## 6. Secondary checks (fixed now, reported but not used for verdicts)
1. R dose instead of H. 2. S dose (income, B). 3. GCCSA x year instead of SA4 x year effects (shows how much the
same-region comparison changes the B estimates). 4. Binary dose: indicator H >= 10% in place of H (areas below 10% count as unexposed), same model.
5. Postcode-level DV. 6. Other ATO and PIA outcomes, other industries, AVO breaches, longer Black Summer path
(k = 3..5).

## 7. Audit
Before results are reported, a fresh reviewer agent re-derives the primary numbers from the raw files with its own
code; differences are reported in `audit/AUDIT.md`.
