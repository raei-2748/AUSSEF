# What goes into Y: literature review and proposed composition

Prepared 2026-09-26 in response to Bowen: 继续找一下数据 / 然后看literature / 确定Y的构成要素.
**This is a proposal for discussion, not a decision.** No model has been fitted.

- `literature/` holds four annotated bibliographies (about 110 entries, roughly 90 distinct sources after overlap). Each citation was checked against Crossref/OpenAlex or the official PDF, and partly verified items are marked:
  - `A_frameworks.md`: damage/loss typologies, composite-index method, counterfactual measurement
  - `B_bushfire_economics.md`: direct and indirect bushfire losses, Australia and the US
  - `C_fiscal.md`: disaster effects on local and sub-national government finances, DRFA
  - `D_social.md`: social vulnerability vs social impact, bushfire social outcomes
- `signal_check.py` reproduces the data check in section 3.

## 1. What the literature says (short version)

1. **The four pillars match the standard typology, with one caveat.** Every major framework separates damage to assets (a stock) from losses in economic flows, and market from non-market impacts. Frameworks: ECLAC/DaLA, PDNA, Sendai, BTE 2001 Report 103, Meyer et al. 2013 (NHESS), Deloitte/ABR 2016. DL = direct tangible damage, IL = indirect flow losses until recovery, SL = human and intangible losses.
   - **FP is the non-standard pillar.** BTE 2001 treats government assistance as a *transfer*, not an economic cost.
   - FP is defensible if defined as **public-sector burden**: excess public outlays relative to the council's fiscal capacity, with the viewpoint stated (council). It must not be added on top as more loss. Deryugina 2017 (AEJ: Policy) shows these costs are real and mostly hidden in transfers.
2. **SL must not be small.** Deloitte/ABR 2016 put Black Saturday's intangible costs at about A$3.9b against A$3.1b tangible. Johnston et al. 2021 (*Nature Sustainability*) value Black Summer smoke health costs at A$1.95b. The mentor's class-note weight of 10% on SL is hard to defend from the literature.
3. **Local labour-market effects are usually small or null at LGA/county scale.** Walls & Wibbenmeyer 2023; Meier, Elliott & Strobl 2023; Hickson & Marshan 2022 (*Economic Record*). Tourism and retail losses are offset by rebuilding and firefighting activity.
   - Effects are clearer for **income and business activity close to the fire**: Black Saturday income fell 8–18% at SA2 level (Ulubaşoğlu & Beaini 2019, a practitioner summary of a BNHCRC study; partly verified); NSW Black Summer nightlights fell about 30% (Akter 2023).
   - They get diluted at LGA level, so treatment intensity should be the *share of the council burned*.
4. **Council fiscal stress shows up in cash and spending reallocation, not debt.** Liao & Kousky 2022 (JAERE) on California wildfires; Jerch, Kahn & Lin 2023 (JUE); NSW Audit Office 2023; NSW Legislative Council Report 52 (2024).
   - Councils pay for repairs up front and wait more than a year for DRFA reimbursement.
   - Debt is flat or falls, because DRFA substitutes for borrowing.
   - Own-source revenue share falls because grants arrive, so it measures transfer dependence, not stress.
5. **Vulnerability is X, not Y.** SoVI, BRIC, ADRI and SEIFA are pre-event capacity measures (Cutter et al. 2003; Parsons et al. 2021). Putting them in Y would make the X→Y relationship true by construction. Akter & Grafton 2021 show disadvantage is also correlated with fire exposure, so treat IRSD as both a confounder and an interaction.
6. **Measure with/without, not before/after.** A before/after change overstates cost because it picks up trends (BTE 2001). Our `_excess` columns (change minus the change in unburned councils) follow the difference-in-differences logic of Cavallo et al. 2013 and Belasen & Polachek 2009.
7. **Weighting has no consensus.** For hierarchical indices, weighting is the most influential design choice (Tate 2012). Nominal weights ≠ realised importance (Becker et al. 2017). Entropy weights reward dispersion, not importance. Best practice: a headline Y plus uncertainty and sensitivity analysis over normalisation × weighting × aggregation (OECD/JRC 2008 Handbook; Saisana et al. 2005), with severity reported as a class plus rank interval.
8. **No peer-reviewed composite economic–fiscal–social index for bushfire events was found.** Tedim et al. 2018's fire classes are hazard-based, not impact-based. This supports the project's stated novelty, but the search was not exhaustive.

## 2. Double-counting rules to adopt

| Overlap | Rule |
|---|---|
| Asset destroyed (DL) and its lost income (IL) | Count the asset in DL. IL uses local economy-wide flows, not the income of destroyed assets |
| Income in IL and in SL | IL uses total income and business activity (size of the local economy). SL uses hardship measures only. Median income is a robustness check, not a core SL indicator |
| Income support in SL and FP | FP viewpoint = the **council**. Commonwealth income support counts only in SL |
| DRFA transfers | Not a loss. Report "gross" and "net-of-transfers" FP, or use grant revenue as a control |
| Area burnt, FFDI, severity | Hazard = **X**. Never part of Y |
| Deaths / injuries | SL (human loss), not DL |

## 3. What our own data says

`signal_check.py`, 218 declared-event × council rows:

| Candidate | ρ with share burned | Black Summer, ≥20% burned (n=23) | Black Summer, <20% (n=34) | Other years (n=161) |
|---|---|---|---|---|
| Homes destroyed per 1,000 dwellings (n=55) | **+0.40** | **1.31** | 0.21 | 0.24 |
| Income-support recipients /1,000, excess | +0.06 | **+3.01** | +1.46 | +1.06 |
| Services share of spending, t+1 excess (pp) | −0.01 | **−1.76** | +0.15 | −0.32 |
| Cash expense cover, t+1 excess (months) | −0.14 | **−1.75** | −1.75 | −0.89 |
| Median income, excess (%) | +0.23 | +0.43 | −0.42 | −0.52 |
| Business count, excess (%) | +0.09 | +0.05 | −0.19 | −0.69 |
| Unemployment rate, excess (pp) | −0.12 | −0.45 | −0.30 | −0.40 |
| Operating ratio, t+1 excess (pp) | +0.03 | +0.84 | +2.08 | +1.13 |
| Debt service ratio change (pp) | −0.07 | +0.03 | +0.11 | −0.12 |
| *New 2026-09-26:* Renewals ratio, t+1 excess (pp) | +0.18 | **+12.1** | −7.1 | −11.6 |
| *New:* Grants per resident, t+1 excess (A$) | +0.02 | **+374** | +224 | +72 |
| *New:* Cash expense cover, event-FY excess (months) | −0.08 | **−1.12** | −0.36 | +0.29 |
| *New:* Total income, excess (%) | +0.28 | +0.14 | −0.09 | −1.09 |
| *New:* Median rent, excess (%) | −0.04 | 0.00 | +1.93 | 0.00 |

What this shows:

- **Only direct loss tracks exposure across the whole sample.** The council-level indicators respond only for the heaviest events, and the direction matches the literature for three of them: income-support rise, crowd-out, cash drawdown.
- **Unemployment, business counts and the debt ratio show no fire signal.** This matches the null LGA-level findings in the literature. COVID (JobKeeper, the JobSeeker supplement) also contaminates the 2019-20 post-period.
- **The indicators are almost uncorrelated with each other.** Excluding pairs that are the same measure in two windows (cash cover t vs t+1, ρ = 0.62) and median vs total income (ρ = 0.52, the IL/SL overlap in §2), the maximum |ρ| is 0.30. A data-driven weight (entropy or PCA) would therefore mostly weight noise. This is an empirical reason to prefer theory-based weights with sensitivity analysis.
- **The roads share of operating spend did not rise.** In the 25 councils with ≥50,000 ha burned it went from 19.0% to 17.4%, while governance/admin rose. Reconstruction is mostly *capital* spending, which operating-expense shares miss. FP therefore needs capital-side measures. Added 2026-09-26: the renewals ratio (renewal spending ÷ depreciation) rises about 12 pp above comparison councils in heavily burned Black Summer councils in the year after, and grants per resident rise about A$374.
- **Rent shows no fire signal in the quarter after.** Heavily burned councils: median 0% change, the same as comparison councils. DCJ medians are rounded to $5–10, which makes quarterly changes lumpy. Akter & Grafton's +A$20 a week is Census 2016→2021, a longer window that also includes the COVID regional rent boom. Rent stays secondary.
- **The "unburned" comparison councils are mostly metropolitan** and have a very different spending mix. Excess measures should compare within OLG council categories, or within the same region.

## 4. Proposed Y composition

**Unit (decided).** Declared event × council: the 218 rows in `event_council` / `key_event_council.csv`.

- IL, FP and SL are council-year quantities, so every fire in the same council-year shares them. A per-fire Y would reuse the same council values for every fire in that council-year.
- Per-fire rows remain the unit for X and DL.

**Direction.** Every indicator is signed so that higher = worse.

**Timing.** IL and SL: quarter after and FY t, with t+1 as a check. FP: t and t+1, with t+2 when available. For Black Summer, cut the SL/IL window at 2020Q1 or add a COVID control.

| Pillar | Core indicators | Secondary / robustness | Data status |
|---|---|---|---|
| **DL**: direct physical damage | Homes destroyed per 1,000 dwellings, log(1+x) | Homes damaged (×0.25–0.5); ICA insured loss (event-level area-share proxy); fencing / livestock / facilities from `facts` | `DL_homes_destroyed_per_1000_dwellings`: 55 of 218 rows (12 from council reports, 43 from the area share of whole-fire figures). Dwellings: **collected** (100%). Damaged: still needed |
| **IL**: indirect economic loss | Excess total personal income change (%); excess business-count change, t and t+1 | Excess unemployment-rate change (expected ≈0); tourism-sector business counts; VIIRS nightlights | Income: have (57%, ends FY22-23). Business: have (99%). Sector counts and nightlights: **need** |
| **FP**: council fiscal burden | Excess cash expense cover change, t and t+1; excess services share of spend (crowd-out); excess renewals ratio change, t+1 | Operating performance ratio; debt service change (down-weight); own-source revenue share, reread as transfer dependence; grants per resident (control / gross vs net) | Ratios and function shares: have (80–95%). Renewals ratio and grants per resident: **collected** (199 of 218 rows). OLG publishes no capital expenditure in dollars; the renewals ratio is the capital-side proxy |
| **SL**: human and social loss | Excess income-support recipients per 1,000 (quarter after); deaths + injuries (log, from `facts`) | Excess median income change; excess median rent change; ERP change as a composition diagnostic | Recipients: have (95%). Deaths: have (declared events). Rent: **collected**, 196 of 218 rows (fires from mid-2017) |

**Deliberately left out of Y (report separately as known omissions, so Y is a lower bound):**
- **Smoke health costs.** Smoke exposure does not follow the burnt footprint and would dominate urban LGAs.
- **Mental health.** No public LGA series.
- **Environmental and biodiversity loss.**
- **Economy-wide supply-chain multipliers** (Wang et al. 2021). Most of those losses fall outside the fire region.

**Normalisation.**
- Winsorise at the 1st and 99th percentiles, then take the percentile rank within the sample (robust to heavy tails and the 0.26-correlation noise).
- Log₁₀ breaks for DL counts, following Caldera & Wirasinghe 2022.
- Test min–max and z-score as alternatives.

**Aggregation and weights.**
1. **Within each pillar:** equal weights over core indicators. Missing indicators are re-weighted, and a pillar needs at least one core indicator to count.
2. **Headline Y:** equal pillar weights (25% each). This is the transparent default; the literature does not justify a better one.
3. **Severity class:** non-compensatory, so a catastrophic pillar cannot be averaged away.
   - Class = the higher of (the class from Y's quantile) and (the class implied by DL thresholds, e.g. ≥1 death or homes destroyed ≥10 → at least "heavy").
   - EM-DAT uses the same kind of OR-threshold for inclusion.
4. **Sensitivity (required).** Report class stability and rank intervals across all of these:
   - the mentor weights 35/25/30/10 and 30/25/25/20;
   - AHP (CR < 0.1);
   - entropy;
   - PCA;
   - geometric aggregation;
   - Monte Carlo ±5/10/15% weight perturbation, with Kendall's W.
5. **Validation (criterion check).** Y should be higher for events that were formally declared, drew large DRFA payments, or have large reported losses in `facts`. If it isn't, the indicators are measuring noise.

## 5. Data

**Collected 2026-09-26** (pipeline modules in `fire_event_dataset/src/`):
1. **ABS Census private dwellings by LGA** (2016 G32, 2021 G36): `src/dwellings.py`. The 2016 interim codes of merged councils are recoded to 2021.
2. **OLG grants & contributions and the renewals ratio**: `src/socio.py` and `src/anomaly.py`. The OLG Time Series has no capital expenditure in dollars.
3. **NSW DCJ Rent and Sales Report**, 36 quarterly files, Sep 2017 – Jun 2026: `src/rent.py`.

**Still worth finding**, in priority order:
1. **Capital expenditure in dollars by council**: council audited financial statements, or DRFA payments by council. Not in the OLG Time Series.
2. **Homes damaged** (RFS building impact figures in inquiry and council reports): the DL secondary indicator.
3. **ABS Counts of Australian Businesses by industry × LGA** (accommodation and food, retail): the sectoral IL most sensitive to fire.
4. (Optional) **VIIRS monthly nightlights**, clipped to LGA: a high-frequency IL indicator (Akter 2023 method).

## 6. Decisions for Bowen

1. ~~Unit of Y~~ **Decided 2026-09-26: declared event × council.**
2. Is the FP viewpoint the council only (recommended), or does it include state and Commonwealth transfers?
3. Income: in IL only, with SL = hardship (recommended), or in both?
4. ~~Headline weights~~ **Decided 2026-09-26: equal pillar weights, with the sensitivity checks in §4.**
5. Severity class: non-compensatory with DL thresholds (recommended), or pure Y quantiles?
