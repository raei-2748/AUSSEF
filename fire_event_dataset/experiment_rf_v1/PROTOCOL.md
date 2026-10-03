# Bowen random-forest experiment V1

Written before any model fit or predictive result, 28 September 2026.

The user-selected Drive workbook `nsw_bushfires_2015_2025_XY.xlsx`, master sheet, is the sole modelling input. Its SHA-256 is recorded in AUDIT.json and the snapshot is byte-identical. No canonical database, research data or source workbook is modified. Rows 1–3 are headers; each observation from row 4 is a declaration × council.

Question: can fire characteristics and pre-fire regional conditions predict the workbook's continuous Y in held-out fire groups, and therefore its class from Y? This is retrospective estimation after fire characteristics are known. It is not an early-warning, causal-impact or total-dollar-loss experiment. The model is fitted, not assumed feasible.

## Target and class

Keep the workbook's Y exactly as supplied. It is an equal mean of available DL/IL/FP/SL pillars (at least two). Do not impute outcome pillars, reweight Y or replace it with FFDI. Use the frozen reference score boundaries that reproduce `Y_class_from_Y` in all 218 rows: 0.4866308906879208, 0.6353925611165694, 0.7543974862033601. Apply these fixed boundaries to predicted Y. Do not re-rank each test batch. Death/home-loss floors in the separate `Y_class` are not applied to predictions.

The labels were percentile-ranked across this full workbook before the experiment. Thus this is a benchmark against a fixed reference-cohort index, not a fully forward-built measurement system. The benchmark must not be represented as independent validation of Y. True zeros, unavailable data and missing pillars remain distinct in the frozen input.

## Groups and splits

Connected groups join rows with the same declaration, any common mapped GA fire ID, explicit overlapping declarations, or the same council and fire financial year (reused outcome window). Group memberships are constructed using metadata only. All 49 groups and their connecting edges are saved. No random row split and no OOB accuracy claim.

Primary: train on complete groups with latest fire FY start <=2019; test on groups with earliest fire FY start >=2022. The years 2020 and 2021 form a temporal gap (there are no master rows in those FYs). The latest training t+1 outcome FY ends 30 June 2021, before the first test fire. Inner tuning is four-fold GroupKFold on training groups only.

Secondary: five-fold GroupKFold across all 218 rows. Every outer fold has fresh four-fold grouped inner tuning. This secondary test uses future and earlier groups in training and is a cross-event benchmark, not a forecast simulation. Save every outer split before fitting.

All folds keep connected groups intact. Persistent council characteristics may recur across folds; the experiment targets new events, not transfer to completely unseen councils. Correlations through shared statewide comparison benchmarks and adjacent outcome years may remain; this is not an assertion that 49 groups are fully independent disasters.

## Inputs and preparation

Eligible predictors are only master codebook columns with `role_if_Y_sum == X` (223 initially). Exclude all outcome-side columns, Y components/ranks/classes, IDs, dates, provenance text and the counts of pillars available. Never use the supplied missing-Y pattern as an input.

The two BCARR 2015–2021 average-growth columns are excluded because their reference window crosses historical fires. Census/SEIFA/industry-share/insurance-proxy reference years are taken from the workbook vintage metadata; cells from a later Census than the fire's start year are masked in the experiment copy. TRA 2014–2017 averages are unavailable before 2018, REDS 2020 before 2021, and SA4 GRP proxies before the end of their reference FY. This prevents obvious future reference periods; exact historical publication dates and later statistical revisions remain unverified. Annual pre-event statistics are not certified real-time available.

Within each training fold only: remove predictors with less than 50% observed values or fewer than two unique values; remove exactly duplicated columns; infer numeric/categorical type from training cells; median-impute numeric X, most-frequent-impute and one-hot-encode categorical X. No missingness flags. Feature selection, encoding, imputation and scaling for ridge are fitted on training only. Record the accepted/rejected feature list in every fold. Original cells and Y remain unchanged.

Each training group receives equal total weight (row weight inverse group size, normalised to mean 1). Main evaluation likewise averages absolute error within each group and then equally across groups. Report row-level MAE/RMSE/R² alongside the group metric.

## Models, tuning and baselines

Training-only constant weighted mean and weighted median are the simplest baselines. A ridge regression uses the same predictors, training-only preprocessing and alpha in [0.1, 1, 10, 100]. Predictions from ridge are clipped to the known Y support [0,1].

Random forest: 500 trees, bootstrap enabled, squared-error criterion, random seed 20260928, n_jobs=1. Grid: min_samples_leaf in [3,8,15], max_features in [0.33,0.7], max_depth=None. Six configurations only. Select by mean group MAE over the inner folds; deterministic grid order breaks ties. No additional tuning after outer-test results.

Diagnostics: group-level paired bootstrap of (baseline MAE − RF MAE), 2,000 draws, seed 20260928. Compare against each baseline separately. These are conditional descriptive intervals for fixed fitted models/splits, not confidence intervals for the whole model-selection procedure. Secondary intervals cluster each group once across out-of-fold predictions. Class accuracy, macro-F1, class MAE and confusion matrix are secondary; high/extreme class recall is reported even when low.

Required sensitivities, using the already-fitted outer models: performance by two/three/four available pillars; primary performance for councils not seen in training; row- versus group-weighted error. No target redesign or new model family. Permutation importance uses the primary held-out test set for descriptive interpretation only, 10 repeats per retained original feature, group-MAE degradation; it is not used for feature selection or a causal claim.

## Decision rule

Evidence of transferable predictive gain requires primary group MAE at least 5% better than every baseline, a positive 95% paired group-bootstrap improvement bound versus every baseline, and lower secondary grouped-CV MAE than every baseline. Otherwise report predictive gain not established and retain the best simple comparator. Class conversion is reported separately from regression success. A failed test will not be rescued by expanding the grid, choosing a favourable subset, changing Y, or switching to a more complex model.

Outputs: source/input and protocol hashes, feature audit, group/split assignments, tuning scores, held-out predictions, regression and class results, robustness tables, model bundle, validation checks, charts and a concise report. A final model fitted to all rows, if saved, is labelled experimental; it has no independent all-data test score and is not a deployment.

Methods references: [scikit-learn random forests](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html), [grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html), [training-only preprocessing](https://scikit-learn.org/stable/common_pitfalls.html).
