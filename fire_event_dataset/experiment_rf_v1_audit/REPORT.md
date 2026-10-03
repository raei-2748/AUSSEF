# Audit of Bowen RF experiment V1

28 September 2026. This report qualifies the earlier V1 report. The source workbook, frozen experiment, models and original results remain preserved. This audit reads saved outputs and models; it fits no new models and changes no target.

**Assessment: V1 is reproducible, but methodological corrections are required before treating it as a conclusive test of random forest.** The earlier 25/25 PASS concerned the listed software/data checks. It was not certification of target validity, complete historical availability, adequate model capacity or a definitive negative result.

## What survives the audit

The source Drive workbook hash still matches its snapshot. Recalculated regression metrics agree with the saved predictions to numerical precision (largest difference 6.7e-16). Loading the saved forest reproduces its primary test predictions (largest difference 5.6e-17). Continuous Y and class conversion follow the agreed workbook definition. Connected event groups remain intact across outer splits, and preprocessing and tuning use outer-training data only.

The reported primary group MAE remains 0.1323 for RF versus 0.1213 for ridge, for the models actually fitted. The paired interval for their difference crosses zero: the experiment does not establish that ridge is generally superior. It establishes that this RF run did not meet its chosen success rule.

## Confirmed tuning mismatch

The intended final metric gives every event group equal weight. The tuning code instead averages four fold scores equally, after averaging groups within each fold. Those quantities agree only when the folds contain the same number of groups.

The primary validation folds contain **1, 6, 8 and 10 groups**. The single group in fold 1 therefore receives 25% of tuning weight rather than the intended 4%; each group in fold 4 receives 2.5%. This is a mismatch between tuning and evaluation, even though equal-fold averaging was explicitly written into V1's protocol.

The repair is to weight each fold's group-MAE by its number of validation groups, then divide by the total groups. Reaggregating the existing tuning scores requires no refitting and uses no outer-test outcomes. It leaves the primary RF and ridge selections unchanged. It changes the RF selection in secondary outer fold 3 from leaf size 3 to 15, both with feature fraction 0.33. Thus the original pooled CV score is the score of V1's original selection procedure, not the corrected procedure. No corrected CV predictions or scores are claimed here.

Evidence: `INNER_FOLD_WEIGHTS.csv`, `REAGGREGATED_TUNING.csv`, `SELECTION_AUDIT.csv`.

## Forest capacity was too narrowly explored

The RF grid tested minimum leaf sizes 3, 8 and 15, never 1 or 2. The selected primary model used 15. Inspecting all 500 fitted trees finds **273 trees with only one split**; the median depth is 1 and the maximum is 2. The median number of leaves is 2. Weighted bootstrapping in the installed runtime yields a median of 49 distinct sampled rows per tree from the 139 training rows.

Slide 14 of the supplied `Significance&RF.pptx` describes deep unpruned trees; slide 16 recommends tuning the feature fraction. Although `max_depth=None` was set, the leaf restriction strongly limited the actual fitted tree depth. Official [RandomForestRegressor documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html) describes leaf size as a smoothing control and gives a default of 1.

This is evidence of a restricted capacity search, not proof that deeper trees would generalise better. A corrected comparison should include standard deeper-tree candidates alongside regularised ones, with selection confined to training groups. It must disclose that the amendment follows inspection of V1 results; the same reused outer test cannot be represented as a newly untouched confirmatory test.

Evidence: `PRIMARY_TREE_STRUCTURE.csv`, V1 `PROTOCOL.md`, the fitted model bundle, and the supplied class notes.

## Historical source checks missed columns

V1 applied several date masks by column-name patterns. The codebook shows additional relevant sources that those patterns missed:

- Seven population/dwelling exposure columns use Census Mesh Block counts. All retain 2016-reference values for four fires starting in 2015. The occupied-dwellings column also retains four such cells. These should have received the census-vintage check.
- `X_env_road_km_within_100m_sum` explicitly uses a 2019 OSM network, yet retains 68 observations from fires starting before 2019 without a special date rule.
- Two remoteness columns use ABS RA 2021 for older events. These can be explicitly defined as fixed geography in a retrospective study, but do not demonstrate historically available regional information. The date of the other OSM road column remains unresolved.

These are confirmed reference-period inconsistencies or unverified timing, not proof that the columns directly encode Y. The defect is in the experiment's temporal-eligibility checks; no source cells have been changed. The repair needs an explicit source-based registry, rather than assuming that a name containing `census` identifies all census-derived columns. Reference year and historical release date also need to be distinguished.

Evidence: `MISSED_REFERENCE_PERIODS.csv`, the workbook codebook, V1 `AVAILABILITY_RULES.csv` and the input masking function.

## Target limitations remain separate from these defects

By the user's decision, V1 preserves the workbook Y. Its indicator ranks and class thresholds use the full reference cohort, including held-out rows. This supports a frozen-index benchmark, not a target constructed without future observations. The mean uses whichever two, three or four pillars are present, so the effective definition differs with missingness. Four-pillar coverage is 74/139 older training rows and 10/79 recent test rows.

Neither a software check nor model fitting validates that this index measures comparable economic/social impact across periods. These are measurement limitations to discuss with Bowen, not permission for this audit to replace Y or invent missing outcomes.

## What to do next

Correct the group-weighted tuning aggregation and source-based eligibility rules, then run one clearly labelled amended benchmark with the same continuous Y and Y-derived classes and a training-selected RF grid that includes standard deeper-tree settings. Preserve V1 and disclose every amendment. Do not interpret a more favourable score on the reused holdout as fresh independent confirmation; that requires additional untouched data.

The current defensible statement is: **this first RF configuration performed poorly, and the pipeline needs corrections; RF feasibility is not settled.**

`AUDIT_RESULTS.json` records the evidence and hashes. `audit.py` reproduces the audit from the preserved V1 outputs. No memory files, synced references, Drive workbook or canonical database were edited.
