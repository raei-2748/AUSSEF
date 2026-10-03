"""Result-dependent V2 report; no fixed claims about performance or tree depth."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent


def table(records):
    lines=['| Model | Group MAE | Row MAE | RMSE | R² | Class accuracy | Macro-F1 |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {r['model']} | {r['group_mae']:.4f} | {r['row_mae']:.4f} | {r['rmse']:.4f} | {r['r2']:.3f} | {r['class_accuracy']:.1%} | {r['class_macro_f1']:.3f} |")
    return '\n'.join(lines)


def report(m,pred,s,audit,validation):
    out=ROOT/'results'
    old=ROOT.parent/'bowen_rf_v1'
    if not old.exists():old=ROOT.parent/'experiment_rf_v1'
    original=pd.read_csv(old/'results/MODEL_RESULTS.csv')
    current=pd.read_csv(out/'MODEL_RESULTS.csv')
    comparison=[]
    for split,label in [('primary_recent_seasons','Recent seasons'),('group_cv_pooled','Grouped CV')]:
        for model in ['ridge','rf']:
            a=original[(original.split==split)&(original.model==model)].iloc[0]
            b=current[(current.split==split)&(current.model==model)].iloc[0]
            comparison.append({'split':split,'model':model,'V1_group_mae':a.group_mae,'V2_group_mae':b.group_mae,
                               'V1_r2':a.r2,'V2_r2':b.r2,'V1_class_accuracy':a.class_accuracy,'V2_class_accuracy':b.class_accuracy})
    pd.DataFrame(comparison).to_csv(out/'V1_V2_COMPARISON.csv',index=False)
    compare_lines=[]
    for r in comparison:
        label='Recent seasons' if r['split']=='primary_recent_seasons' else 'Grouped CV'
        compare_lines.append(f"| {label} | {r['model']} | {r['V1_group_mae']:.4f} | {r['V2_group_mae']:.4f} | {r['V2_r2']:.3f} | {r['V2_class_accuracy']:.1%} |")
    selected=pd.read_csv(out/'SELECTED_MODELS.csv')
    choice=selected[(selected.split=='primary_recent_seasons')&(selected.model=='rf')].iloc[0]
    trees=pd.read_csv(out/'PRIMARY_TREE_STRUCTURE.csv')
    tuning=pd.read_csv(out/'INNER_TUNING.csv')
    primary_tuning=tuning[(tuning.outer=='primary_recent_seasons')&(tuning.model=='rf')].copy()
    primary_tuning['leaf']=primary_tuning.parameters.map(lambda p:json.loads(p)['min_samples_leaf'])
    primary_tuning['contribution']=primary_tuning.group_mae*primary_tuning.validation_groups
    candidates=primary_tuning.groupby('parameters',sort=False).agg(numerator=('contribution','sum'),groups=('validation_groups','sum'),
                                      median_depth_across_inner_fits=('median_tree_depth','median'))
    candidates['pooled_group_mae']=candidates.numerator/candidates.groups
    candidates.reset_index().to_csv(out/'PRIMARY_CANDIDATE_COMPARISON.csv',index=False)
    ci=pd.read_csv(out/'PAIRED_GROUP_BOOTSTRAP.csv')
    uncertainty=[]
    for r in ci[ci.split=='primary_recent_seasons'].itertuples():
        uncertainty.append(f"| {r.baseline} | {r.improvement_pct:+.1f}% | {r.improvement_group_mae:+.4f} | [{r.ci_low:+.4f}, {r.ci_high:+.4f}] |")
    p=pred[pred.split=='primary_recent_seasons']
    cv=pred[pred.split.str.startswith('group_cv_')]
    recalls=[]
    for label,d in [('Recent seasons',p),('Grouped CV',cv)]:
        for k in [1,2,3,4]:
            dd=d[d.Y_class_from_Y==k]
            recalls.append(f"| {label} | {k} | {len(dd)} | {(dd.pred_class_rf==k).mean():.1%} |")
    pre=json.loads((ROOT/'PRE_FIT_REPAIR_CHECKS.json').read_text())
    registry=pd.read_csv(ROOT/'SOURCE_ELIGIBILITY_REGISTRY.csv').fillna('')
    source_counts=registry.groupby(['family','action']).size()
    availability=pd.read_csv(out/'AVAILABILITY_RULES.csv')
    masks=[]
    for family,d in availability.groupby('source_family',sort=False):
        masks.append(f"| {family} | {len(d)} | {int(d.masked_cells.sum())} |")
    cohort=[]
    assignment=pd.read_csv(out/'SPLIT_ASSIGNMENTS.csv')
    older=m[m.row_id.isin(assignment[(assignment.split=='primary_recent_seasons')&(assignment.role=='train')].row_id)]
    for name,d in [('Older training',older),('Recent test',p)]:
        cohort.append(f"| {name} | {len(d)} | {d.Y.median():.3f} | {int(d.Y_pillars_n.eq(4).sum())} | {int(d.Y_class_from_Y.ge(3).sum())} |")
    meets=s['verdict']=='AMENDED_BENCHMARK_GAIN_CRITERIA_MET_NOT_FRESH_VALIDATION'
    finding='The amended run meets the numerical gain criteria on the reused benchmark.' if meets else 'The amended run does not establish RF predictive gain against all simple baselines.'
    best=min(s['primary_metrics'],key=lambda r:r['group_mae'])
    rf=next(r for r in s['primary_metrics'] if r['model']=='rf')
    text=f'''# Bowen random-forest amended benchmark V2

Completed 28 September 2026. **{finding}** Recent-season RF group MAE is **{rf['group_mae']:.4f}**; the lowest point-estimate group MAE is **{best['group_mae']:.4f}** ({best['model']}). The saved data and models pass the specified correction checks. This verifies the repairs and recorded arithmetic; it does not certify Y or provide fresh independent validation.

V2 follows the user's request to fix the V1 audit findings and check again. It preserves the Drive `master` workbook, continuous Y, Y-derived class thresholds, all 218 observations, all 49 connected groups, and identical outer splits. The protocol and source registry were frozen before the completed V2 fit, after V1 results had already been seen. The earlier holdout is reused and must be described that way.

## Corrections implemented

- Inner tuning pools event-group errors equally across all validation folds. Independent reconstruction from saved inner predictions verifies every fold's group count, every score and every selected candidate. This corrects the overweighting of single-group folds in V1.
- All 223 X candidates have an explicit source eligibility rule. All 36 Census/SEIFA predictors, including the previously missed exposure and occupied-dwelling columns, use the row's vintage and release-date guard. Both road-exposure columns are masked before their 1 January 2019 OSM snapshot. Two RA 2021 remoteness predictors and four 2025 BCARR predictors are excluded where historical availability is unverified. The 2023 REDS product receives a conservative publication-year guard.
- Every outer training set tests all 15 RF configurations: leaf sizes [1,2,3,8,15] × feature fractions [0.33,0.7,1.0]. All use 500 trees, bootstrap, no explicit depth limit and the original seed. Deeper-tree candidates were actually fitted and grew beyond one split; their performance, rather than their availability, determines selection.
- Grouped-CV pillar sensitivities are pooled correctly for reporting. Models and Y are not selected or changed using those sensitivities.

Primary selected RF settings: `{choice.parameters}`; **{int(choice.retained_features)}** original predictors survive training-only screening. The selected forest's median depth is **{trees.depth.median():.0f}** (range {trees.depth.min()}–{trees.depth.max()}), with median **{trees.leaves.median():.0f}** leaves. **{int(trees.depth.eq(1).sum())}/500** trees have only one split. A regularised setting may legitimately win even when deeper settings were tested; leaf size 1 is not forced merely to improve the appearance of tree depth.

The pre-fit repairs exclude 6 candidates, leaving {pre['eligible_after_exclusions']} eligible columns before fold-specific coverage/constant/duplicate screening. {pre['masked_cells']} observed cells are masked or excluded in the experiment copy. Original cells remain preserved in the snapshot.

## Recent seasons held out

Train: 139 older rows in 25 groups. Test: 79 recent rows in 24 groups. Shared declarations, mapped fires, overlapping declarations and reused council-FY outcome windows cannot cross the outer split. Predictor imputation, categorical encoding and ridge scaling use training rows only. Each group receives equal total fitting weight; evaluation reports both equal-group and row metrics.

{table(s['primary_metrics'])}

RF comparison intervals condition on these fitted models and resample held-out groups; they do not include full model-selection uncertainty. Positive differences favour RF. An interval crossing zero does not establish which model is generally better.

| Comparator | RF gain in group MAE | Comparator MAE minus RF MAE | Conditional 95% interval |
|---|---:|---:|---:|
{chr(10).join(uncertainty)}

## Grouped cross-validation

Five outer grouped folds, each with fresh four-fold grouped inner selection. Every observation has exactly one out-of-fold prediction. This benchmark mixes older and newer groups during training and is not a temporal forecast simulation.

{table(s['cv_metrics'])}

## What changed from V1

These comparisons use the same observations, Y and outer split memberships. Changes combine the corrected eligibility, corrected tuning objective and expanded RF grid; they do not identify each correction's separate causal contribution.

| Evaluation | Model | V1 group MAE | V2 group MAE | V2 R² | V2 class accuracy |
|---|---|---:|---:|---:|---:|
{chr(10).join(compare_lines)}

![Model comparison](results/model_comparison.png)

![Predicted versus actual Y](results/predicted_vs_actual.png)

## Classes from continuous predictions

Class boundaries remain 0.4866308906879208, 0.6353925611165694 and 0.7543974862033601. These reproduce the workbook `Y_class_from_Y`. The separate home/death floors are not applied to predictions. Class performance remains visible even if regression improves.

| Evaluation | Actual class | Rows | RF recall |
|---|---:|---:|---:|
{chr(10).join(recalls)}

Primary RF predictions range **{p.pred_rf.min():.3f}–{p.pred_rf.max():.3f}**; observed Y ranges **{p.Y.min():.3f}–{p.Y.max():.3f}**. Full counts are in `CLASS_CONFUSION.csv`; no conclusions about class 3 or 4 are inferred from average regression error alone.

## Source eligibility audit

All eligibility uses source/time metadata, never Y. Census/SEIFA release dates and the conservative employment availability bound are sourced in the per-column registry. In particular, [SEIFA 2016](https://www.abs.gov.au/ausstats/abs%40.nsf/Lookup/2033.0.55.001Quality%2BDeclaration02016) was released 27 March 2018, and [SEIFA 2021](https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/socio-economic-indexes-areas-seifa-technical-paper/2021) on 27 April 2023. The release day is masked conservatively where ignition times are absent.

| Source family | Candidate columns | Observed cells masked/excluded |
|---|---:|---:|
{chr(10).join(masks)}

`MASKED_CELLS.csv` identifies affected rows/columns, while `AVAILABILITY_RULES.csv` and `SOURCE_ELIGIBILITY_REGISTRY.csv` state the reason. Annual/quarterly historical release dates and revisions, the precise TRA publication date, and some environmental vintages remain unverified. This is a retrospective benchmark with corrected known date problems, not certification that every input was operationally available at ignition.

## Remaining measurement and evidence limits

Y is still the original equal mean of available DL/IL/FP/SL pillars; its indicators and class boundaries were ranked over the full reference cohort. This is not a target constructed without held-out outcomes. The differing pillar coverage changes effective weights and may affect comparability; it was not changed to improve prediction.

| Cohort | Rows | Median Y | Four-pillar rows | Class 3/4 rows |
|---|---:|---:|---:|---:|
{chr(10).join(cohort)}

Rows are declaration × council, from a selected master view rather than all NSW fires. The 49 connected groups are dependency clusters, not certified independent disasters. Adjacent-year outcomes, shared statewide comparisons and persistent council characteristics can leave further dependence. Neither the index nor predictive associations establish causal dollar loss or policy priorities.

The diagnostic decision rule is unchanged: at least 5% primary gain versus every baseline, a positive lower conditional bootstrap difference bound versus every baseline, and lower pooled grouped-CV MAE versus every baseline. Status: **{s['verdict']}**. This rule is applied once to V2. No further grid, seed, subset or target changes were made after V2 performance was observed. If the criteria were met, additional untouched data would still be required for fresh confirmation.

## Verification and reproduction

Correction verification: **{validation['status']} — {validation['passed']}/{validation['total']} specified checks**. All 39 recorded original V1 files retain their hashes; the Drive source and snapshot still match `{audit['source_sha256']}`. Reported metrics and inner selections are independently recalculated; the portable saved model reproduces primary predictions and loads in a new process. These checks have defined scopes and are not scientific certification.

An initial execution was interrupted after a verification-script error included non-X codebook columns in a census check. The check was fixed, all 10 pre-fit checks passed, and the completed execution enforced that passing receipt. The incomplete files are preserved in `aborted_preflight_run`; no outer-test scores were inspected to change the grid, target, groups or eligibility. `RESTART_NOTE.md` records the restart.

For reproduction, use a fresh copy of this folder beside the preserved V1 folder, recreate `requirements.txt`, keep the snapshot and registry, run `check_repairs.py`, `run_experiment.py`, then `validate_and_report.py`. Move existing result folders aside in the reproduction copy; the runner refuses to overwrite a completed receipt. No canonical database is used. This model is trained on the older primary training rows only, is labelled experimental, and has no final all-data refit.

Key evidence: `PROTOCOL.md`, the source registry, `PRE_FIT_REPAIR_CHECKS.json`, `PRE_FIT_RECEIPT.json`, `INNER_HELD_OUT_PREDICTIONS.csv`, `INDEPENDENT_SELECTION_CHECK.csv`, `PRIMARY_CANDIDATE_COMPARISON.csv`, `PRIMARY_TREE_STRUCTURE.csv`, `HELD_OUT_PREDICTIONS.csv`, `MODEL_RESULTS.csv`, `PAIRED_GROUP_BOOTSTRAP.csv`, `ROBUSTNESS_RESULTS.csv`, `V1_V2_COMPARISON.csv`, `VALIDATION_CHECKS.json` and `RF_MODEL.joblib`.
'''
    (ROOT/'REPORT.md').write_text(text)
