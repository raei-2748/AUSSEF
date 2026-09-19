# V2 retrospective forecasting results

**Primary answer: the longer matched history does not produce a consistent win over persistence for operating performance.** Maintenance is a secondary exception versus persistence, but its training-mean baseline remains better on MAE. Cash-cover gains are mixed.

Eight primary target years (2016–17 through 2023–24) are evaluated, with 818 held-out council-years per configuration. Cash has seven years; maintenance has nine. All conclusions are retrospective out-of-time, not real-time or causal.

## Primary: operating_ratio_pct
8 held-out years; 818 council-year predictions per configuration. Units: percentage points.

| Specification | Model | MAE | RMSE | Pooled R² | MAE wins | Both-error wins |
|---|---|---:|---:|---:|---:|---:|
| baseline | persistence | 7.334 | 9.848 | -0.050 | 0/8 | 0/8 |
| baseline | training_mean | 7.409 | 10.123 | -0.109 | 2/8 | 2/8 |
| fiscal_only | ridge | 7.690 | 10.167 | -0.119 | 5/8 | 4/8 |
| fiscal_only | tree | 7.921 | 10.418 | -0.175 | 1/8 | 1/8 |
| fiscal_plus_disaster | ridge | 7.393 | 9.761 | -0.031 | 2/8 | 1/8 |
| fiscal_plus_disaster | tree | 7.764 | 10.331 | -0.155 | 2/8 | 2/8 |
| fiscal_plus_fire | ridge | 8.010 | 10.651 | -0.228 | 4/8 | 3/8 |
| fiscal_plus_fire | tree | 7.921 | 10.418 | -0.175 | 1/8 | 1/8 |

No ridge/tree specification met the predeclared consistency rule against persistence.
Adding disaster fields to ridge reduced MAE in 4/8 years; mean annual MAE reduction 0.295 (negative means worse).
Adding disaster fields to tree reduced MAE in 4/8 years; mean annual MAE reduction 0.158 (negative means worse).

## Secondary: cash_cover_months
7 held-out years; 716 council-year predictions per configuration. Units: months.

| Specification | Model | MAE | RMSE | Pooled R² | MAE wins | Both-error wins |
|---|---|---:|---:|---:|---:|---:|
| baseline | persistence | 3.346 | 4.681 | 0.549 | 0/7 | 0/7 |
| baseline | training_mean | 5.244 | 7.067 | -0.028 | 0/7 | 0/7 |
| fiscal_only | ridge | 3.364 | 4.590 | 0.566 | 3/7 | 3/7 |
| fiscal_only | tree | 3.527 | 4.985 | 0.488 | 1/7 | 1/7 |
| fiscal_plus_disaster | ridge | 3.493 | 4.729 | 0.540 | 4/7 | 4/7 |
| fiscal_plus_disaster | tree | 3.527 | 4.985 | 0.488 | 1/7 | 1/7 |
| fiscal_plus_fire | ridge | 3.361 | 4.585 | 0.567 | 4/7 | 4/7 |
| fiscal_plus_fire | tree | 3.527 | 4.985 | 0.488 | 1/7 | 1/7 |

No ridge/tree specification met the predeclared consistency rule against persistence.
Adding disaster fields to ridge reduced MAE in 4/7 years; mean annual MAE reduction -0.129 (negative means worse).
Adding disaster fields to tree reduced MAE in 0/7 years; mean annual MAE reduction -0.000 (negative means worse).

## Secondary: maintenance_ratio_pct
9 held-out years; 910 council-year predictions per configuration. Units: percentage points.

| Specification | Model | MAE | RMSE | Pooled R² | MAE wins | Both-error wins |
|---|---|---:|---:|---:|---:|---:|
| baseline | persistence | 21.894 | 43.023 | -0.532 | 0/9 | 0/9 |
| baseline | training_mean | 19.520 | 34.828 | -0.004 | 7/9 | 7/9 |
| fiscal_only | ridge | 19.544 | 36.119 | -0.079 | 8/9 | 7/9 |
| fiscal_only | tree | 19.845 | 34.327 | 0.025 | 8/9 | 7/9 |
| fiscal_plus_disaster | ridge | 20.233 | 36.377 | -0.095 | 7/9 | 6/9 |
| fiscal_plus_disaster | tree | 19.845 | 34.327 | 0.025 | 8/9 | 7/9 |
| fiscal_plus_fire | ridge | 20.419 | 37.040 | -0.135 | 7/9 | 6/9 |
| fiscal_plus_fire | tree | 19.845 | 34.327 | 0.025 | 8/9 | 7/9 |

Consistency rule met by: fiscal_only / ridge, fiscal_only / tree, fiscal_plus_disaster / tree, fiscal_plus_fire / tree.
Adding disaster fields to ridge reduced MAE in 3/9 years; mean annual MAE reduction -0.697 (negative means worse).
Adding disaster fields to tree reduced MAE in 0/9 years; mean annual MAE reduction 0.000 (negative means worse).

## Overall verdict: NO-GO for escalating model complexity on this evidence
The criterion is lower pooled MAE and RMSE and wins on both errors in at least 75% of future-year folds. It is a transparent practical rule, not a statistical significance test.

## Did longer history help on the same later years?
| Specification | Model | Matched rows | Long MAE | Short MAE | Long RMSE | Short RMSE |
|---|---|---:|---:|---:|---:|---:|
| baseline | persistence | 307 | 6.720 | 6.720 | 8.718 | 8.718 |
| baseline | training_mean | 307 | 7.177 | 7.558 | 9.756 | 10.014 |
| fiscal_only | ridge | 307 | 6.655 | 6.978 | 8.702 | 9.227 |
| fiscal_only | tree | 307 | 7.291 | 7.215 | 9.289 | 9.197 |
| fiscal_plus_disaster | ridge | 307 | 6.834 | 7.198 | 8.859 | 9.497 |
| fiscal_plus_disaster | tree | 307 | 6.949 | 7.215 | 9.009 | 9.197 |
| fiscal_plus_fire | ridge | 307 | 6.632 | 7.000 | 8.682 | 9.273 |
| fiscal_plus_fire | tree | 307 | 7.291 | 7.215 | 9.289 | 9.197 |

Longer history reduced operating-ratio fiscal-only ridge MAE from 6.978 to 6.655 on the same 307 later rows. Persistence on those rows is 6.720. That small recent-period edge does not survive as a consistent advantage over the full eight-year evaluation; it must not replace the full-history result.

## What did the trees actually use?
Across all long-history folds, the only disaster-related tree split was the **bushfire declaration unknown indicator**, in four operating-ratio folds. No tree split used mapped burned hectares or known bushfire/flood event presence. Cash and maintenance tree predictions are unchanged by adding disaster fields. The apparent operating-tree disaster gain is therefore a reporting-availability partition, not evidence of a physical disaster effect.

The latest operating tree uses prior operating ratio, prior maintenance ratio, population and the bushfire-unknown flag. Cash uses prior cash cover and own-source revenue. Maintenance uses prior maintenance, population, current ratio and cash cover. See the complete split/node tables for thresholds, sample sizes and predictions.

This control uses V2 for both histories, the same 103 councils and exactly matched test rows. It isolates the training-window difference within this specification, rather than comparing different cohorts or old published scores.

## Boundaries on interpretation
- Current-vintage retrospective prediction only: historical fire products and later declaration revisions were not available in their present form at historical forecast dates.
- Accounting standards, early operating-ratio adjustments, FESM sensors/thresholds and source geometry change over time. The maintenance denominator remains council-assessed; arithmetic comparability is not engineering invariance.
- Unknown declarations remain explicit categories. Any gain may partly reflect reporting coverage; the fire-only ablation and complete annual results are provided. No physical flood-intensity series was available.
- Cash 2012 is withheld. Flagged maintenance conflicts and debt-service denominator cases are withheld. No extreme outcomes are removed solely because they make prediction difficult.
- Operating/cash 2024–25 targets are missing and not scored; maintenance may extend one further year. All skipped folds, rows and reasons are retained.
- Repeated councils, common macroeconomic shocks and shared disasters limit effective independent temporal evidence. Neither split use nor ridge coefficients establish causality.
- Earlier years of this project were already explored; these are retrospective validation results, not a newly sealed prospective test set.

## Files and reproduction
Open `../experiment.ipynb` in the Experiment 2 folder. Outputs include the merged evidence table, aligned predictor/target table, row exclusions, every fold, tuning/preprocessing audits, held-out predictions, ablations, matched-history comparison and tree nodes. Run the notebook from the AUSSEF directory or any folder beneath it; the companion script also locates its repository from its own path. No Random Forest, XGBoost, neural network, random split or test-year hyperparameter selection is used.
