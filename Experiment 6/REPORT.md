# Experiment 6: pre-fire council risk score, tested against the real fires

Bowen's change of angle: score every NSW council **before** any fire, using only pre-fire X plus the new
NSW Bush Fire Prone Land (BFPL) layer, then test the score against the DL/IL/FP/SL impact (Y) of the 96 real fires.
No Y is used to build the score. Y, the indicators and the master sheet are unchanged.

## Findings log (2026-09-29)

**Status: promising, unconfirmed.**

- **Where fires happen (well-studied, works as a sanity check):** a pre-fire council score built from BFPL land, forest, exposure, vulnerability and council-finance inputs finds the councils that later get a big fire (AUC about 0.95).
- **Who is hurt (the under-studied part):** on the 2015-25 NSW fires, council vulnerability (SEIFA, income, unemployment) is associated with heavier impact (Spearman +0.25 on all rows, +0.58 on fires burning 5% or more of a council; intervals exclude zero). Real housing exposure (share of homes inside BFPL land, a post-hoc fix) lifts the whole score to +0.58 on large fires.
- **Not confirmed on fresh fires:** on two independent earlier fires (NSW Oct 2013, Victoria Black Saturday 2009; 26 council rows, rule frozen in advance) the score's correlation with impact was +0.00 [-0.40, +0.40]: verdict "cannot tell". The test could detect a true correlation of 0.4 only 52% of the time. About 45-50 comparable council rows from independent fires are needed to settle it.
- **Council finances:** no link to impact or to the fiscal-pressure pillar (FP). The fiscal null is informative on all 218 rows (94% power at rho 0.3), not on the large fires alone (18%). It is not explained by overlap with vulnerability or by disaster grants masking damage. A better fiscal measure built from NSW's own official benchmarks also shows nothing, and the FP outcome itself is mostly ordinary budget movement, so finances cannot be judged until the outcome is better defined.
- **Model and fire size:** a random forest does not beat the fixed score (Black Summer hold-out: fixed +0.61, best RF +0.44). Using all rows with burned share as a continuous term finds no effect that grows with fire size (vulnerability matters about equally at every size, about +0.25 SD of Y per SD of V), so the +0.58 on large fires mostly reflects Black Summer councils having a less spread-out Y.
- **Caveats:** most large-fire evidence is Black Summer; many tests were run; the exposure fix and the hazard + vulnerability structure were chosen after seeing results; the cross-validation on large-fire subsets is biased against fitted models (shuffled-Y check failed), so those RF comparisons are unreliable. Details are in the sections below and in the follow-ups section.

## What was built

| Block | Inputs (all 129 NSW LGAs, 2014 snapshot; 2015/16 if 2014 missing) | Direction |
|---|---|---|
| **H** hazard | BFPL share Cat 1, BFPL share Cat 1+2, NVIS forest/woodland share | more = worse |
| **E** exposure | log population, log people inside BFPL Cat 1-2 (population x BFPL share; assumes even density) | more = worse |
| **V** vulnerability | SEIFA IRSD, median income, unemployment rate | poorer = worse |
| **F** fiscal | cash cover, own-source %, debt-service ratio, operating ratio, infrastructure backlog, unrestricted current ratio | weaker = worse |

Each item is a 0-1 percentile rank across NSW councils. A block is the mean of its items. The **pre-specified score**
`risk_add` is the equal-weight mean of H, E, V, F (`risk_mult` = H x E x mean(V, F), rank-scaled, is the multiplicative version).
Output: `results/COUNCIL_RISK_SCORE.csv` (all 129 councils), `results/risk_map.png`.

**BFPL data:** NSW RFS/DPHI *NSW Bush Fire Prone Land* (CC-BY), official ePlanning service layer 229, 235,537 polygons,
118 pages, 214 MB, generalised to about 30 m (`fetch_bfpl.py`; cached in `fire_event_dataset/data/bfpl/`).

**BFPL choice that matters:** Category 3 (grassland) covers 480,000 km2 of the west. "Any BFPL" is about 100% of most rural councils
and does not separate them, so the hazard block uses Cat 1 and Cat 1+2 only. "Any BFPL" alone scores AUC 0.72; Cat 1 alone scores 0.95
(table below).

## Result 1 (strong): the score finds the councils that get hit

AUC for "this council later had a fire burning at least X% of it" (129 councils, 34 positives at 5%):

| Score | >=2% (45) | >=5% (34) | >=10% (27) | >=20% (23) |
|---|---:|---:|---:|---:|
| **H hazard block** | 0.944 | 0.953 | 0.969 | 0.959 |
| BFPL Cat 1 share alone | 0.939 | 0.953 | 0.966 | 0.953 |
| NVIS forest share alone | 0.912 | 0.923 | 0.958 | 0.953 |
| BFPL "any" (incl. grassland) | 0.730 | 0.716 | 0.715 | 0.700 |
| Pre-specified `risk_add` | 0.903 | 0.910 | 0.911 | 0.920 |
| E / V / F alone | 0.65-0.70 | 0.63-0.72 | 0.64-0.70 | 0.67-0.71 |

The hazard block does the work. BFPL Cat 1 is a little better than forest share alone at 2% and 5% (0.939 vs 0.912; 0.953 vs 0.923),
but the two are highly correlated (Spearman 0.84), so **BFPL adds only a small increment** over vegetation data we already had. In the
full score BFPL makes no visible difference (0.910 vs 0.904 without it).

## Result 2 (mixed): does a higher score mean heavier damage once a fire hits?

Spearman(score, Y), council-cluster bootstrap 95% CI. All 218 council x fire rows, and only fires burning >=5% of the council (38 rows, 8 fires):

| Score | Y, all rows | Y, >=5% fires | DL (>=5%) | IL | FP | SL |
|---|---|---|---|---|---|---|
| Pre-specified `risk_add` | -0.07 [-0.25, +0.11] | +0.34 [+0.00, +0.62] | +0.22 | +0.27 | -0.20 | +0.32 |
| H (hazard) | -0.07 | +0.14 | +0.17 | +0.02 | +0.11 | -0.01 |
| E (exposure) | **-0.33** [-0.50, -0.16] | -0.33 | -0.31 | -0.20 | -0.07 | -0.31 |
| **V (vulnerability)** | +0.25 [+0.06, +0.43] | **+0.58** [+0.30, +0.76] | +0.39 | +0.44 | -0.27 | +0.60 |
| F (fiscal) | +0.03 | +0.00 | -0.14 | +0.29 | -0.07 | -0.02 |

- **Vulnerability (SEIFA, income, unemployment) is the block that tracks impact.** At council level (69 councils with a fire) V vs the council's
  worst fire: rho +0.52 [+0.31, +0.68].
- **Exposure points the wrong way**: bigger councils (more people in BFPL) get *lower* Y. Y is relative (homes destroyed per 1,000 dwellings,
  % income change, rank-based), so a large economy absorbs the same fire better. E is a count, not a rate.
- **Hazard predicts DL** (homes destroyed, all rows rho +0.37 [+0.14, +0.58]) but not IL/SL/FP.
- **Fiscal stress before the fire (F) does not predict FP, or Y overall.** Only a weak hint for IL at >=5% (+0.29, CI crosses 0). This is the
  gap Bowen wanted to fill, so it needs a plain statement: with these fiscal indicators the pre-fire signal is not there.
- The equal-weight `risk_add` is diluted by E's negative sign and F's nothing, so overall it is about zero (-0.07) and only moderate on large fires.

## Exploratory (not pre-specified): hazard + vulnerability

After seeing the block results, `risk_HV_mean` = mean(H, V), a likelihood + consequence structure, was tested. **This choice was made after looking at Y,
so treat the numbers as a hypothesis for Bowen, not a confirmed result.** Two H+V variants were tried (mean and product, both in `VALIDATION_ROW_LEVEL.csv`); they behave the same.

| `risk_HV_mean` | Y | DL | IL | FP | SL |
|---|---|---|---|---|---|
| all rows | +0.13 [-0.06, +0.32] | +0.48 [+0.26, +0.65] | +0.13 | -0.07 | +0.02 |
| >=2% burned (62 rows) | +0.42 [+0.19, +0.63] | +0.46 | +0.38 | -0.09 | +0.27 |
| >=5% burned (38 rows) | **+0.59** [+0.31, +0.77] | +0.46 | +0.41 | -0.21 | +0.55 |
| Black Summer only (50 rows) | +0.62 [+0.41, +0.77] | +0.60 | +0.15 | -0.18 | +0.41 |
| excluding Black Summer (168 rows) | +0.03 [-0.20, +0.28] | +0.56 [+0.23, +0.77] | +0.13 | -0.02 | -0.09 |

Council-level, `risk_HV_mean` vs the council's worst-fire Y: +0.40 [+0.17, +0.59].

## Bowen's question: can "large fire" be redefined?

Yes, and it helps. Only Black Summer has a council share >=20%. Definitions by physical size (not by Y, so no circularity):

| Definition | Rows | Fires | Councils | Years | Black Summer rows |
|---|---:|---:|---:|---|---:|
| share burned >= 20% (old) | 23 | 1 | 23 | 2019 | 23 |
| share burned >= 10% | 28 | 2 | 27 | 2019, 2023 | 27 |
| **share burned >= 5%** | 38 | 8 | 34 | 2016, 2018, 2019, 2023 | 30 |
| share burned >= 2% | 62 | 19 | 45 | 2016-2019, 2023 | 39 |
| burned >= 5,000 ha in council | 84 | 32 | 44 | 2015-19, 2023, 2025 | 39 |
| burned >= 1,000 ha in council | 151 | 71 | 58 | 2015-19, 2023-25 | 45 |
| Y class Severe/Extreme (circular) | 63 | 29 | 40 | 2016-19, 2023-25 | 27 |

Going from 20% to 5% takes large fires from 1 to 8 (and to 19 at 2%). The catch: **Black Summer is still 30 of the 38 rows at 5%**,
so the >=5% tests remain mostly a Black Summer result. The 2% and 5,000 ha cuts spread it more (39 of 62 and 39 of 84). Full grid
of every score x definition x pillar: `results/VALIDATION_ROW_LEVEL.csv`.

## Power check: could our data have found an effect if it existed?

`power_check.py` -> `results/POWER_CHECK.csv`. X is the real X (the same 218 council x fire rows and real block scores). Y is fake: real Y
shuffled within Black Summer and within each year (keeps its spread and clustering, breaks any link to X), then a known effect
(correlation rho) is planted on the fiscal block F or the vulnerability block V. The same test as the real analysis is applied
(Spearman, council-cluster bootstrap, "detected" = interval above 0). 300 simulations per cell, 200 bootstrap draws each.

Percent of simulations in which the planted effect was detected:

| Planted on | Rows tested | rho 0 (false alarm) | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
|---|---|---:|---:|---:|---:|---:|---:|
| F fiscal | all rows (218) | 0 | 11 | 52 | 94 | 100 | 100 |
| F fiscal | fires >= 5% burned (38) | 1 | 5 | 10 | 18 | 33 | 60 |
| V vulnerability | all rows (218) | 0 | 15 | 72 | 99 | 100 | 100 |
| V vulnerability | fires >= 5% burned (38) | 7 | 15 | 46 | 78 | 93 | 100 |

What this says:
- **On all 218 rows the fiscal null is informative.** The real F-vs-Y correlation was +0.03 [-0.17, +0.21]. With about 94% power at rho 0.3, an effect that large would have been caught. Effects of about 0.1-0.2 could still hide (11-52% power).
- **On the >=5% fires the fiscal null is not informative.** Power is only 18% at rho 0.3 and 60% at 0.5, so "no fiscal signal" among large fires cannot separate "no effect" from "too few fires".
- **The vulnerability result on >=5% fires is testable:** 78% power at rho 0.3, 93% at 0.4. A real effect of that size would usually be seen, which supports taking the +0.58 seriously. It does not remove the Black Summer and forking-path caveats.
- **Excluding Black Summer cannot be tested.** Only 8 rows. Even with nothing planted, V is "detected" 13% of the time (mean estimated rho +0.36), because the Y shuffle keeps year-level differences that line up with V. Power for that subset is not reported as meaningful.
- The planted rho is a correlation across all rows, so the subset numbers show what a fixed underlying effect looks like when tested on fewer rows. False alarms at rho 0 are 0-1% (F) and 0-7% (V), close to the expected 2.5% for a one-sided rule, except the 7% at V and >=5%.

Limits: the fake Y keeps real Y's spread and clustering but not council persistence over time; the bootstrap clusters by council, not by fire (same as the real analysis).

## Exposure v2: real housing locations (`build_exposure_bfpl.py`)

v1 exposure was a population count with an even-density guess, and it pointed the wrong way on Y (-0.33). v2 uses the **share of a council's dwellings
and residents that sit inside BFPL Category 1-2 land**, from 2016 Census Mesh Block counts split at council lines and weighted by the area inside BFPL
(same allocation rule and 2016 vintage as the dataset's other people-in-fire columns). Checks: council dwellings match the census within 2-32% (median 7%; the MB counts are
randomly adjusted by the ABS); Blue Mountains 19%, Kempsey 20%, Kyogle 30%, Waverley/Woollahra/Sydney 0%. v1 result files are byte-identical; v2 files carry a `_v2` suffix.

**This fix was made after seeing E's negative sign, so treat it as a labelled v2 choice, not a confirmed result.**

| Spearman with Y (95% CI) | v1 score | **v2 score** | E block v1 | **E block v2** |
|---|---|---|---|---|
| all 218 rows | -0.07 [-0.25, +0.11] | **+0.12** [-0.09, +0.30] | -0.33 [-0.50, -0.15] | **+0.14** [-0.08, +0.32] |
| fires >= 2% burned (62 rows) | +0.18 [-0.04, +0.38] | **+0.36** [+0.10, +0.58] | -0.26 | +0.34 [+0.00, +0.58] |
| fires >= 5% burned (38 rows) | +0.34 [+0.01, +0.62] | **+0.58** [+0.25, +0.82] | -0.33 | +0.45 [+0.08, +0.74] |
| DL, all rows | +0.28 [+0.05, +0.48] | **+0.43** [+0.22, +0.61] | -0.13 | +0.41 [+0.15, +0.62] |

- Exposure now points the right way. Councils with more of their housing in bush-prone land had heavier direct loss (homes destroyed) and, on large fires, heavier indirect loss (IL +0.47 [+0.10, +0.74]).
- It also finds which councils get hit: E v2 alone AUC 0.88-0.94 (v1 0.70); the v2 multiplicative score reaches 0.94-0.96 (v1 0.92).
- Still true: excluding Black Summer the v2 score on Y is +0.01 [-0.22, +0.23] (DL +0.48 survives); FP is unrelated (-0.14 on >=5% fires).
- The v2 score on >=5% fires (+0.58) now equals the vulnerability block alone (+0.58). Exposure v2 and BFPL share are correlated (0.76), so part of the gain is hazard information by another route.
- Files: `results/*_v2.csv`, `COUNCIL_EXPOSURE_BFPL.csv`.

## RF on the pre-fire inputs (`rf_score_model.py`)

Question: does a random forest on the pre-fire inputs beat the fixed equal-weight score? Feature set A = the four v2 block scores; B = 15 item-level inputs (BFPL Cat 1 and 1-2, forest,
dwellings/residents in BFPL, log population, SEIFA, income, unemployment, six council-finance ratios). Nothing known only after ignition. 5-fold cross-validation grouped by council
(no council in both train and test, asserted), 5 repeats with different splits, RF settings chosen by inner grouped CV, 200 trees. Compared with the fixed score, the V block alone, ridge on the blocks, and
a "not pre-fire" reference that adds the fire's burned share.

**Sanity check failed on the large-fire subset.** With Y shuffled (no real signal), every fitted model still scored negative on fires burning >= 5% (-0.14 to -0.48; raw -0.16 to -0.52). This is the
known negative bias of cross-validated correlations in small samples (a held-out group with high Y leaves a lower training mean). Centring predictions on each fold's training mean did not remove it.
On all 218 rows the shuffled check is fine (-0.16 to +0.21). **So the fitted-model numbers on >=5%, >=2% and >=5,000 ha subsets are biased downward against the RF and ridge and cannot be compared fairly with the fixed score there.**
The fixed score has no fitted step, so it is not affected. Run 1 (uncentred) is kept as `*_uncentered_run1.csv`.

Spearman with Y, out-of-fold (centred), all rows and gain over the fixed score (95% CI, cluster bootstrap):

| Model | Y, all rows | gain over fixed score | DL | IL | FP | SL |
|---|---|---|---|---|---|---|
| Fixed equal-weight score (v2) | +0.12 | - | +0.43 | +0.09 | -0.08 | +0.02 |
| Ridge on blocks | +0.21 | +0.09 [-0.08, +0.27] | +0.50 | +0.34 | -0.05 | +0.14 |
| RF, blocks (A) | +0.04 | -0.08 [-0.29, +0.14] | +0.56 | +0.20 | -0.04 | +0.06 |
| RF, 15 items (B) | +0.23 [+0.01, +0.44] | +0.11 [-0.06, +0.29] | +0.44 | +0.29 | -0.09 | +0.05 |
| RF B + burned share (not pre-fire) | +0.30 | - | +0.74 | +0.35 | +0.09 | +0.14 |

- **The RF does not clearly beat the fixed score.** Gains over the fixed score are small and their intervals include zero, except ridge and RF-B on IL (+0.25 [+0.04, +0.46], +0.20 [+0.01, +0.44]), one of 15 comparisons
  and not adjusted for testing many.
- **Black Summer hold-out (the clean test, no fold artifact):** train on 34 rows from other councils and fires, test on the 50 Black Summer rows. Fixed score +0.61 [+0.35, +0.78]; RF-B +0.44 [+0.19, +0.64]; RF-A +0.25; ridge +0.10.
  Models fitted on small fires do not transfer to Black Summer better than the hand-built score.
- **Only two inputs matter to the RF** (permutation importance, Y): log population and SEIFA. BFPL, forest, dwellings-in-BFPL and all six council-finance ratios are at zero, consistent with the earlier fiscal null.
- **Training on the >=2% fires only** (Bowen's "more representative large fires" idea) gave RF-A +0.63 [+0.35, +0.82] and RF-B +0.53 on >=5% fires vs +0.58 for the fixed score. Not reliable: the sanity check was not run for this variant and the subset shares the bias above.
- The burned share adds most to DL (+0.44 -> +0.74 for RF-B on direct loss), as expected, but it is not known before a fire.
- Files: `results/RF_*.csv`, `results/rf_importance.png`.

## Why the fiscal block shows nothing (`fiscal_diagnostics.py` -> `results/FISCAL_DIAGNOSTICS.txt`)

Descriptive Spearman correlations, not significance-tested. Four candidate explanations were checked or considered:

1. **Not just vulnerability in disguise.** Fiscal (F) and vulnerability (V) blocks correlate 0.27 across all councils and 0.10 among the 69 councils that had a fire. F vs Y is +0.03 raw and -0.02 after removing V;
   V vs Y is +0.25 raw and +0.25 after removing F. They are separate things.
2. **The six fiscal ratios barely agree with each other** (mean off-diagonal |rho| 0.18; only cash cover and the unrestricted current ratio move together, 0.58), so an equal-weight average blends unrelated
   ratios. This is not the whole story: the item-level RF found zero importance for all six.
3. **Disaster money flows to hit councils but does not hide the damage.** The year after a fire, councils with >=5% burned had a median grants-per-resident rise of +$320 (vs comparison councils) against +$102 for
   councils <2% burned, and total revenue up 16.4% vs 11.8%; councils with more home loss got bigger jumps (rho +0.25 to +0.28 with DL). But controlling for the revenue jump barely changes how FP responds to damage
   (FP vs DL +0.20 -> +0.14; FP vs burned share on >=5% fires +0.30 -> +0.27), so masking does not explain the null. FP does rise weakly with damage; it is pre-fire finances (F) that do not predict FP.
   Black Summer reported damage vs funding exists for only 2 councils (Bega Valley funding 39% of damage, Eurobodalla 68%), too few to conclude anything.
4. **Not enough large fires** (power check: 18% power at rho 0.3 on >=5% fires) and **it may simply be true.**

Reading for now: "pre-fire finances do not predict damage in these data, and we cannot say why", not "finances do not matter".

## Dealing with the two limits: too few large fires, rough measures (proposals; several were then run, see the follow-ups section)

**Too few large fires**
- *Use every row, not a cut.* Model Y on the pre-fire inputs with burned share as a continuous term (and its interaction with the block), so 218 rows inform the answer instead of 38. This removes the arbitrary threshold and is cheap.
- *Add real large fires.* Earlier NSW fires (e.g. 2013) and other states (Victoria 2009 and 2019-20, SA, TAS, QLD). This is the biggest lever and the biggest effort: it needs comparable council-level Y and finance data per state.
- *Do not simulate fires to fill the gap:* simulated fires add no information about how councils are actually hurt (see the power-check discussion).

**Rough measures**
- *Fiscal:* replace the equal average of six unrelated ratios with a measure fixed in advance from a documented standard (NSW OLG's own performance benchmarks, e.g. operating ratio > 0, own-source revenue > 60%, unrestricted current ratio > 1.5,
  debt service cover > 2, cash expense cover > 3 months; count how many a council meets), averaged over several pre-fire years instead of one snapshot. Keep pre-fire capacity separate from post-fire recovery funding.
- *FP outcome:* it is built from three noisy change ratios; decide its composition in advance and treat grants as recovery funding, not a loss.
- *DL:* missing for 128 of 218 rows. Fill from RFS or Department house-damage assessments where they exist.
- *Face-validity check:* confirm the fiscal measure flags councils known to be in financial difficulty before using it.
Whichever version is chosen must be fixed before it is tested on any new fires.

## Follow-up sessions (2026-09-29): what each found

Six separate sessions ran after the proposals above. Each fixed its design in advance, wrote a `FINDINGS.md` in `followups/<name>/`, and left this report, the workbook and the DuckDB untouched (workbook and DuckDB SHA-256 checked before and after in the fresh-test session). Nothing changed the main conclusion.

| Follow-up | Question | Result |
|---|---|---|
| `allrows_continuous` | Does the score's link to impact grow with fire size, using all 218 rows and burned share as a continuous term? | No. All four interaction intervals include 0 (omnibus p = 0.31). Vulnerability is about +0.25 SD per SD at every size. Method false-alarm rate 2.4-6.1% on shuffled Y. One documented pre-fit amendment. |
| `fiscal_benchmarks` | Does meeting NSW OLG's own benchmarks (8 benchmarks, 3 pre-fire years) predict impact? | No: +0.10 [-0.10, +0.28] on all rows, +0.13 [-0.25, +0.46] on fires burning 5% or more. Benchmark thresholds verified against official documents (they also include asset maintenance > 100%). Moderate face validity (rho +0.41 with 2013 TCorp ratings, 4 of 5 councils with documented trouble in the weakest third). |
| `fp_outcome` | Is the fiscal-pressure outcome (FP) well built? | Mostly normal budget movement (76-87% of fire rows sit inside the unburned 10th-90th percentile band); its three ingredients do not agree (mean pairwise rho -0.04); the renewals-ratio ingredient is arguably scored backwards. Three literature-based alternatives frozen in advance; none clearly better (0 of 36 paired comparisons excluded zero). |
| `dl_fill` | Can the missing direct loss (DL, 128 of 218 rows) be filled? | Only 3 rows from stated figures; 42 more are zeros inferred from RFS statewide season totals; 27 flagged estimates. Coverage 90 to 93 reported, 135 with inferred zeros. Conclusions hold: risk score vs DL +0.43 before, +0.42 [+0.25, +0.54] after (reported + inferred). |
| `more_fires_scoping` | Which extra real large fires could be added? | Measured burned share from local outlines. Best value: NSW Oct 2013 (5 councils at 5% or more), South Australia (8 councils at 5% or more). Victoria's Black Saturday adds most (9 councils) but only a partial Y. Victorian, SA and Qld 2019 fires belong to the same season as Black Summer, so they add rows, not independent events. Council finance ratios are defined differently in every state. |
| `new_fires_test` | Fresh test on two independent fires, frozen in advance | **Cannot tell** (details below). |

### Fresh test on NSW Oct 2013 and Victoria Black Saturday 2009 (`followups/new_fires_test/`)

- **Design (frozen and hash-locked before any outcome):** the v2 equal-weight score, with new councils placed in the original 129-council NSW distribution; the outcome built like the master (each indicator ranked against the existing 218-row distribution); pooled Spearman with a council-cluster bootstrap. Replicated only if the lower bound is above 0; not replicated only if the upper bound is below +0.30.
- **Rows:** 26 council rows (NSW 13, Victoria 13); 14 at 5% or more burned.
- **Result:** pooled **+0.00 [-0.40, +0.40]** (NSW -0.07, Victoria +0.10): cannot tell. Power on these rows: 33% at rho 0.3, 52% at 0.4, 79% at 0.5.
- **What could be built:** NSW 2013 got hazard, exposure and vulnerability (the finance block was dropped by the frozen comparability rule); Victoria got vulnerability only (no BFPL equivalent, no comparable finances). No social-loss pillar in the frozen run. Homes destroyed: 13 of 28 rows, of which several NSW zeros are inferred.
- **Descriptive only (37 tests were run):** DL vs score -0.60 [-0.92, -0.04] on 11 rows (6 inferred zeros, Victoria only 2 councils); indirect loss +0.49 [+0.12, +0.75]. Neither is a verdict.
- **Stage 2 (exploratory, on rows already seen):** adding a social-loss pillar for NSW 2013 from two small DSS files (small cells counted as 10; low confidence) moved the pooled estimate to +0.12 [-0.27, +0.48]. Verdict unchanged. Victorian house loss per council was not found for 11 of 13 councils; the Victorian NV2005 vegetation layer was not downloaded (size unknown, offered through an order portal).
- **Source conflicts found:** RFS statewide total 216 vs the sum of its listed October 2013 fires 222; Murrindindi 1,397 vs 1,242 vs 538 homes; Churchill 145 vs 247 vs 133; statewide Black Saturday 2,029 vs 2,133.
- **New rows are kept separate** in `fire_event_dataset/data/extra_fires/extra_fire_rows.csv` (git-ignored), not in the master workbook, until the question is settled.

### What would settle it
About 45-50 comparable council rows from independent fires (about 30 if the true correlation is 0.5, about 85 if 0.3); the number of independent fires matters more than rows. Next candidates: South Australia, then other states. Victorian rows would need a hazard layer and council-level house-loss counts.

## Limits to keep in view

1. **Black Summer drives the severity signal.** Excluding it, `risk_add` on Y is -0.19 [-0.39, +0.02] and the exploratory H+V is +0.03; only DL (+0.56) survives.
2. The H+V structure was chosen after looking at results (see above). The forking-path risk is real with 96 fires.
3. BFPL is the current mapping (post-2019 updates), not a 2014 snapshot. It is a vegetation and slope hazard map, not a fire outcome, but councils remap over time.
4. "People inside BFPL" assumes uniform density inside each council, which overstates it for councils with bush and town separated.
5. No fire-weather (FFDI climatology) and no council-wide slope in the score yet: BFPL already builds vegetation and slope in, but the weather leg Bowen listed is missing. Source would be a pre-2015 ERA5 climatology per council.
6. Rows within one fire share the same weather and burn, and Y is a within-sample rank composite. CIs cluster by council but not by fire.
7. Y has DL for only 90 of 218 rows.

## Files

`fetch_bfpl.py` (download) -> `build_council_hazard.py` (BFPL, forest shares per council; `results/COUNCIL_HAZARD.csv`) ->
`build_and_validate_score.py` (score and every table in `results/`) -> `make_figures.py` (`risk_map.png`, `score_vs_Y.png`).
`build_exposure_bfpl.py` -> `build_and_validate_score.py v2` -> `rf_score_model.py` (about 35 min). Seeds fixed (`SEED = 20260929`, 2,000 bootstrap draws; RF seed 20260930).

Follow-up folders (each with its own `FINDINGS.md`): `followups/allrows_continuous/`, `followups/fiscal_benchmarks/`, `followups/fp_outcome/`, `followups/dl_fill/`, `followups/more_fires_scoping/`, `followups/new_fires_test/` (with `stage2/`). Reports for the fresh test locked with SHA-256 files (`*.lock`).
