# Post-run notes

No modelling protocol deviations, target changes, new models or expanded tuning were introduced after the test results.

The independent validator exported a portable sklearn-only model bundle from the saved primary model, verified its predictions and verified that it loads in a fresh Python process. The original custom-object model save is retained as an internal run artifact; use `results/RF_MODEL.joblib` for the portable bundle.

After completion, the report added an explicitly exploratory table of target distributions and available pillars in older versus recent cohorts. These diagnostics do not establish a cause for model failure and were not used to select a model. The FY detail is in `results/COHORT_DIAGNOSTICS.csv`.

The runner emits undefined-R² warnings for sensitivity slices with a single row. Those R² values remain missing; they are not treated as zero or successful predictions.
