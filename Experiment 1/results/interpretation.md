### Primary: operating_ratio_pct — NO-GO
Across 3 future-year folds (370 held-out rows), tree MAE/RMSE/R² = 7.400 / 9.291 / 0.063. Mean baseline = 7.517 / 9.991 / -0.083; persistence = 6.938 / 9.028 / 0.116. The tree beat both baselines on MAE in 0/3 individual future years. It did not beat both baselines on both pooled error measures.

Variables used across folds: debt_service_cover__prior, maintenance_ratio_pct__prior, operating_ratio_pct__prior, own_source_pct__prior, population__prior. Latest tree: operating_ratio_pct__prior, own_source_pct__prior. Disaster variables used in any fold: none. Use in a split does not establish a causal effect or incremental predictive benefit; absence does not establish that disasters have no effect. An exposure-free comparison would be needed to isolate incremental predictive value.

### Secondary: cash_cover_months — NO-GO
Across 3 future-year folds (370 held-out rows), tree MAE/RMSE/R² = 4.317 / 5.928 / 0.411. Mean baseline = 5.685 / 7.869 / -0.037; persistence = 3.799 / 5.177 / 0.551. The tree beat both baselines on MAE in 0/3 individual future years. It did not beat both baselines on both pooled error measures.

Variables used across folds: cash_cover_months__prior, debt_service_cover__prior, own_source_pct__prior. Latest tree: cash_cover_months__prior, debt_service_cover__prior, own_source_pct__prior. Disaster variables used in any fold: none. Use in a split does not establish a causal effect or incremental predictive benefit; absence does not establish that disasters have no effect. An exposure-free comparison would be needed to isolate incremental predictive value.

### Secondary: maintenance_ratio_pct — CONDITIONAL GO
Across 4 future-year folds (485 held-out rows), tree MAE/RMSE/R² = 20.903 / 30.787 / 0.088. Mean baseline = 22.166 / 32.332 / -0.006; persistence = 22.082 / 39.303 / -0.487. The tree beat both baselines on MAE in 2/4 individual future years. It did beat both baselines on both pooled error measures.

Variables used across folds: maintenance_ratio_pct__prior, operating_ratio_pct__prior, population__prior, road_km__prior. Latest tree: maintenance_ratio_pct__prior, operating_ratio_pct__prior, population__prior, road_km__prior. Disaster variables used in any fold: none. Use in a split does not establish a causal effect or incremental predictive benefit; absence does not establish that disasters have no effect. An exposure-free comparison would be needed to isolate incremental predictive value.

## Overall verdict: NO-GO for further predictive modelling
This verdict follows the primary operating-ratio forward-validation rule, not training fit or secondary results. A NO-GO means do not advance this specification to more complex predictive models on the strength of these results; it does not rule out a better-measured future dataset. A conditional or full GO supports further validation only, not deployment or causal claims.

Limitations: few independent future years; repeated councils and shared disasters; unverified accounting definitions and publication dates; changing fire-mapping thresholds and unverified polygon vintage; declaration onsets rather than flood intensity/duration; unmeasured later shocks during t+1; missing fiscal outcomes; a common persistence-observed cohort; and potentially influential fiscal extremes. There is no claim to predict previously unseen councils. No causal feature importance is reported.