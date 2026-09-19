# Diagnostic findings for Bowen

The frozen experiment was reproduced: every held-out prediction and each year's MAE, RMSE and R² matched to numerical tolerance before new models were fitted. Source data and all first-experiment files are unchanged.

## 1. A smoother model helps somewhat, but does not beat persistence
Across 370 observations in three future years, operating-ratio MAE is 6.938 pp for persistence, 7.400 for the original tree and 7.104 for ridge predicting levels. Corresponding RMSEs are 9.028, 9.291 and 9.125 pp. Ridge therefore reduces the tree's error without establishing incremental performance over persistence. Ridge level wins on MAE and RMSE in 2021–22, loses in 2022–23 and loses in 2023–24. The latest-year tree RMSE is slightly better than persistence even though its MAE is slightly worse; this favourable result is retained.

## 2. Error concentration: years, councils and movements
The most difficult held-out year is 2022–23: persistence/tree/ridge-level MAE is 7.820/8.583/8.403 pp. In 2021–22 it is 6.394/6.988/6.294; in 2023–24 it is 6.615/6.647/6.635. Poor performance is therefore not uniform over time.

Carrathool and Warren have high mean tree errors across their three tests: 19.48 and 18.81 pp. Warren's persistence MAE is only 2.39 pp, while ridge-level MAE is 15.33 pp. This is a strong example of models pulling a persistently unusual council towards an inaccurate general prediction. Carrathool's persistence MAE is also high (14.50 pp), showing a different problem: large actual fiscal movement. These observations are retained, not dismissed as errors in the source.

The 37 worst tree forecasts (10% of rows) account for 25.2% of absolute error and 41.6% of squared error. Extremes matter, but most absolute error occurs elsewhere. By actual movement, trees improve on persistence for large declines (>10 pp: 11.86 versus 14.32 pp MAE) and large increases (>10 pp: 13.88 versus 15.29), but perform badly on modest increases (0–10 pp: 6.84 versus 4.27). This is a retrospective breakdown by an unknown future outcome, not a deployable rule for choosing models.

## 3. Disaster ablation and subgroup errors
Fiscal-only and fiscal-plus-disaster trees have the same splits and predictions within numerical tolerance in all three primary folds. No disaster split is used. The current disaster inputs therefore have no incremental predictive contribution in these trees. Ridge exposure ablation has not been tested, so do not generalise this to every model.

Persistence MAE is 7.28 pp among 131 mapped-fire-positive observations versus 6.75 among 239 verified scoped-zero observations. Flood declaration rows have MAE 7.16 (n=264), compared with 6.38 (n=106) without listed flood onset. Any new declaration gives 7.15 (n=265), versus 6.41 without a new listed declaration (n=105). These overlapping subgroup differences are descriptive and unadjusted for year/council composition. Neither the level tree nor the level ridge beats persistence on pooled MAE within any of these six subgroups.

Large deteriorations, defined descriptively as declines greater than 10 pp, occur in 14/131 mapped-fire-positive rows (10.7%) versus 12/239 scoped-zero rows (5.0%). Flood declaration rates are 20/264 (7.6%) versus 6/106 (5.7%); any declaration rates are 20/265 (7.5%) versus 6/105 (5.7%). These data show disproportionate frequency in the observed groups, not an identified disaster effect. There are only 26 such declines and three temporal blocks; groups share councils/events, and administrative negatives do not establish physical non-exposure. Quartiles, medians, 90th percentiles and yearly subgroup counts are supplied instead of misleading independent-row confidence intervals.

## 4. Change forecasting does not solve the problem
Tree change reduces MAE to 7.215 pp from 7.400 for tree level, but remains worse than persistence. Ridge change is worse than ridge level (7.328 versus 7.104). Both change models beat persistence MAE in only one year. Mean-change adjustment is worse still (8.032). Change and reconstructed-level MAE/RMSE are mathematically identical, but their R² values have different denominators and are separately reported.

## 5. What the evidence cannot establish
A ratio movement alone does not identify changes in underlying revenue, expenses, grant recognition or damage. Even large movements in the CSV cannot be attributed to grants, disasters or reconstruction without examining the underlying accounts and annual reports. The error-case table explicitly marks this limitation.

Only one, two and three primary outcome years enter the expanding training folds. Even a perfectly implemented method has very little evidence of how patterns transfer over time. The fiscal baseline is two years before the target, future shocks are unknown, and publication dates are unverified. The early ridge choices rely on training-only council groups; only the latest fold allows inner forward validation with the original embargo. All outer evaluations remain forward-year tests.

## Conclusion
**NO-GO for more complex ML on the strength of these results.** Ridge partly alleviates the tree's coarse representation, but neither levels nor changes outperform persistence overall. The tree exposure ablation is null. The next investment should be in comparable temporal history, availability/definition verification and an audit of the underlying accounts and funding timing, followed by physical flood/damage measurement where genuinely available at forecast time. Revised models need an untouched future evaluation period.
