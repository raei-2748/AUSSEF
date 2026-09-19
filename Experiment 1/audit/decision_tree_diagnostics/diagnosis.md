# Fiscal prediction failure: evidence-based diagnosis

## Verdict
**NO-GO for escalating this specification to more complex predictive models.** The diagnosis does not establish that fiscal conditions are intrinsically unpredictable. It shows that this small historical panel and shallow tree do not consistently improve on a council's own earlier fiscal value. All original held-out predictions were reproduced, and the source CSV is unchanged.

## What the diagnostics establish

### 1. The tree throws away useful council-specific persistence
A regression tree assigns the same prediction to every council in a leaf. The primary tree produced only four, six and five different predictions in the three held-out years. Its adjustment from each council's prior operating ratio worsened absolute error for **56.8%** of held-out rows and improved it for 43.2%.

A concrete example is **Warren, outcome FY 2022–23**: the pre-event operating ratio was 32.79%, the actual outcome was 32.93%, and the tree predicted 9.19%. Persistence missed by only 0.14 percentage points; the tree missed by 23.74. Group averaging sometimes discards precisely the information that makes persistence strong. This is an observed mechanism, not an argument to remove Warren or increase tree depth until it fits.

### 2. The direction of fiscal change did not transfer across years
For FY 2021–22, the sample's actual mean two-year change was **+1.96 pp**, but the tree's mean adjustment was **−2.27 pp**. For FY 2022–23 the actual change was **+5.40 pp**, but the prediction was **−1.66 pp**, yielding mean underprediction of **7.07 pp**. FY 2023–24 was much closer: mean bias −0.84 pp.

Training MAE was 5.50, 5.40 and 5.39 pp; corresponding future-year MAE was 6.99, 8.58 and 6.65 pp. This documents a training-to-future gap and a missed year-level shift. It is consistent with fitting sample-specific patterns and changing conditions, but the CSV cannot identify which economic or accounting mechanisms caused the shifts. Claims about grants, COVID, rebuilding or other mechanisms would require evidence not present here.

### 3. The supplied disaster features add nothing to these fitted predictions
Removing mapped burned hectares, bushfire declarations and flood declarations produced **identical held-out predictions to numerical precision in all 10 original target/year folds**. Neither the original level trees nor the diagnostic change trees selected exposure variables. This is direct evidence that these inputs made no predictive contribution to the fitted trees; it is not evidence that disasters have no fiscal effect or that all other models must ignore them.

Exposure is also measured coarsely: declaration counts describe onsets rather than local damage intensity; no physical inundation inventory is present; fire mapping has changing size thresholds and unverified polygon vintage. The primary held-out sample has only **19 bushfire-declared rows out of 370**. Its event years are 2020–21 to 2022–23, not a held-out Black Summer test. Those limitations constrain what can be learned but do not, by themselves, prove the reason exposure was unused.

### 4. There are very few independent years, and the forecast spans two years from the baseline
The primary training folds contain 121, 243 and 367 observations, but only **one, two and three outcome years**. Evaluation covers three later outcome years. Repeated councils and shared shocks mean row counts overstate the amount of independent temporal experience.

The requested t−1 → t+1 design spans two financial years from the fiscal baseline. Median absolute observed operating-ratio change over that interval is **5.20 pp**; the 90th percentile is **14.64 pp**. The tree must anticipate large changes while lacking t fiscal information and information about shocks during t+1. Those are genuine information limits of the requested forecast, not permission to add future data.

### 5. The failure is not mainly a missing-value-imputation issue, and is not confined to one outlier
Within the selected primary cohorts, only prior maintenance has missing predictor values: 2, 3 and 4 training values across the folds, and 1, 2 and 2 test values. The selected operating, cash, liquidity, debt, scale and exposure predictors otherwise have no missing values in these cohorts. This makes widespread imputation an implausible main explanation, although excluded outcomes and the missing 2024–25 operating data still limit coverage.

The worst 10% of primary forecasts account for **25.2% of absolute error** and **41.6% of squared error**. Extreme errors matter, especially for RMSE, but most absolute error remains outside that group. No observations were dropped. In all six overlapping hazard-flag subgroups inspected, primary-tree MAE also exceeds persistence MAE; this is not a single subgroup failure. Hazard-negative rows are not certified unexposed controls.

## Did a better target representation fix it?
A diagnostic tree predicting change, then adding it to the council's prior value, improved pooled operating-ratio MAE from **7.40 to 7.22 pp**, but persistence remained better at **6.94 pp**. Corresponding RMSEs are 9.29, 9.26 and 9.03 pp. The change tree beat persistence on MAE in only one of three years. A training-average-change baseline was worse still, at 8.03 pp MAE. Thus group averaging explains part of the problem, but changing the target does not resolve it.

For cash cover, the change tree improves on the original tree (3.94 versus 4.32 months MAE), but still loses to persistence (3.80 months). For maintenance it worsens MAE from 20.90 to 24.63 pp. All comparisons reuse already examined future years and are diagnostics, not independent confirmation.

## What remains unknown and what to do next
The CSV does not provide the operating-ratio numerator and denominator, fiscal release timestamps, grant timing details, or complete physical damage/intensity measurements. We cannot attribute the large fiscal movements to particular economic causes using this source alone. Nor have we tested every possible predictive model or shown an irreducible error bound.

The highest-value next step is a **source/accounting audit of the largest unexpected movements and their publication dates**, if additional sources are authorised, followed by more comparable years and better-timed exposure measurements. Keep persistence as the benchmark. Do not tune on these repeatedly examined years and then call the improvement validation; a revised specification would need a genuinely untouched future evaluation period. Maintain the existing NO-GO for predictive escalation, while retaining descriptive analysis as a viable project output.
