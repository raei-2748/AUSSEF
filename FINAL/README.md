# Where does a bushfire's cost go, and can we see it coming?

The project on one page (3 Oct 2026). Every number below is a row in `CORE_NUMBERS.csv` (N01-N32), checked against
its source file and its bibliography entry by `check_numbers.py` (32 of 32 pass). Figures are in `figures/`
(rebuild them with `make_figures.py`; figures 0, 1, 2 and 6 are drawn there to the dataviz rules, the rest are copies). Setting: NSW, 218 council x fire rows, 69 councils, fire seasons 2014-2024.
Framework: Bowen's impact index Y = Direct Loss (DL) + Indirect Loss (IL) + Fiscal Pressure (FP) + Social Loss (SL).

## The rule behind every choice: receipts first, a model only where there is no receipt

| Cost | Who wrote it down | What we use | Why |
|---|---|---|---|
| Homes and property (DL) | insurers, RFS damage counts | real dollars and counts | a record exists |
| Government spending (FP) | audited council statements, government payments | real dollars | audited records |
| People (SL) | crime, rent and health records | real counts | recorded; turning them into dollars adds guesses |
| Lost sales of local businesses (IL) | nobody, at council level | a standard input-output model, checked against measured income | the only cost with no receipt, and lost sales are what this model is built for |

Model outputs never go into the prediction target. The modelled IL is built from the same fire-size inputs the random
forest uses, so it would be circular.

## Finding 1: who pays (receipts; figures 1-3)
- Black Summer (NSW) losses we can count: **A$2.44bn** (N01).
  - Insurers carried **77%** (N02).
  - Households carried **A$293m (12%)**, the uninsured part of rebuilding (N03).
  - Governments paid **A$265m (11%)** for clean-up (N04).
- Governments then paid **A$0.94bn** in recovery money, 73% of it from the Commonwealth (N05, N06). This is kept as a
  separate account: some of it goes back to the same households, so adding it to the losses would count it twice.
- Council money keeps arriving for years. The link between fire size and council grants per resident is +0.21 the
  year after the fire and **+0.42 three years after** (N07, N08). Fire-related grant lines in audited statements show
  +0.44 the year after (N09). A one-year window misses most of it.

## Finding 2: seeing it coming (Bowen's random forest + SHAP; figures 4-5)
- A map built only from data before 2019 picks the councils that went on to lose homes in Black Summer: **AUC 0.91**
  [0.86, 0.96] (N10).
- Random forest, tested on fire seasons it never saw:
  - ranks **Direct Loss with rho +0.73**, about 77% of council pairs in the right order (N11);
  - ranks **Bowen's composite Y with rho +0.43** (N12; shuffled-Y p = 0.01, N13).
- SHAP shows what drives the predictions:
  - homes inside the fire outline (29% of the model's attention, N14);
  - then hazard, the underinsurance proxy (11%, N15), council finances and vulnerability.
- Only Direct Loss is predictable. The other pillars are not detected (see the "checked" table below).

## Finding 3: lost sales, the one cost with no receipt (model, checked fairly; figures 6-7)
- A standard input-output model was checked only against what it actually predicts: income in the burned areas.
- **531 of 1,620** model settings agree with both measured income checks (N16).
- Over those settings, Black Summer **lost sales** in the first 2 years are:
  - **A$411m to A$2.71bn**, middle **A$960m** (N17-N19);
  - **A$640m** with default settings (N20).
- The range is the spread over model settings (assumptions), not a statistical confidence interval.
- Lost sales are a real loss, carried mostly by local businesses and workers, but they are not in Finding 1's payer
  accounts. They are gross output, not value added, so they sit beside Finding 1 and are never added to it.
- Business counts and the unemployment rate **cannot** test this model:
  - a business that loses months of sales is still counted;
  - firms keep staff through short dips, and JobKeeper held them from March 2020.
  An earlier version used those checks and wrongly concluded the model "overstates". That conclusion is withdrawn
  (Experiment 18, FINDINGS correction).
- Satellite night lights inside the South Coast fire outlines were about 9-10% darker for 18 months (N22, N23). This is
  consistent with long disruption, mostly from homes lost.

## What we checked and did not detect (Black Summer, effect per 10 percentage points of homes inside the fire)
| Channel | Result [95% CI] | Reading |
|---|---|---|
| Total income, postcode | -1.2% [-3.1, +0.8] (N21) | not detected at this scale; consistent with falls of several % in fully burned areas |
| Unemployment rate, small area | -0.09 pts [-0.29, +0.12] (N24) | not detected; placebo fails |
| Accommodation & food business count | +3.6% [-1.2, +8.6] (N25) | not detected |
| Domestic-violence assault, suburb | -0.5% [-3.2, +2.4] (N26) | not detected |
| Rents, burned councils, year 2 | rho +0.18 [+0.01, +0.36] (N27) | suggestive only: Black Summer-specific, overlaps the COVID regional rent boom |

"Not detected" means the data cannot rule out effects inside the interval. It does not mean "no effect".

## Limits
- Black Summer dominates (57 of 218 rows), and COVID overlaps its later years.
- The lost-sales range is wide because measured income pins down only one slope. Its low end rests on the ABS
  small-area income check, which has no placebo test, and COVID overlaps both income checks. Farm losses are missing,
  and only 36 of 57 Black Summer rows have model inputs.
- Night lights also dim when homes are gone, so they are not a clean measure of business activity.
- Novelty wording, from a limited search of about 15 sources: "We are not aware of a study that checks an input-output
  estimate of bushfire lost sales against fire-matched measured income in Australia." Never "first".

## Figures
0. `fig0_graphical_abstract.png`: the study on one image (drawn in `make_figures.py`).
1. `fig1_who_pays.png`: losses and recovery money, two separate accounts (Exp 17 data).
2. `fig2_council_money_clock.png`: council grants rise for 3 years (Exp 11).
3. `fig3_nsw_cost_map.png`: where the cost landed (Exp 11).
4. `fig4_prefire_map_black_summer.png`: the pre-2019 map vs what happened (Exp 7).
5. `fig5_shap_drivers.png`: what drives the random forest (Exp 18 / Exp 14 pipeline).
6. `fig6_lost_sales_fair_check.png`: the fair check and the lost-sales range (Exp 18 addendum B).
7. `fig7_night_lights_south_coast.png`: night lights inside and around the South Coast fires (Exp 15).

## Where the work lives
Exp 7 (pre-fire map), Exp 11 (impact clock), Exp 13 (fine-grained channels), Exp 14 (Y v4 pipeline),
Exp 15 (night lights), Exp 17 (cost accounts), Exp 18 (random forest re-run, SHAP, lost-sales model). Each has a
locked PRESPEC, FINDINGS and an independent audit.
