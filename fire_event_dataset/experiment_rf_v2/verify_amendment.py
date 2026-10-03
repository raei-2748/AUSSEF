"""Independent arithmetic and split reconstruction for V2 correction checks."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold


def verify(root, master, codebook, x, receipt, model):
    from hashlib import sha256
    digest = lambda p: sha256(p.read_bytes()).hexdigest()
    out = root / 'results'
    splits = pd.read_csv(out / 'SPLIT_ASSIGNMENTS.csv')
    inner = pd.read_csv(out / 'INNER_HELD_OUT_PREDICTIONS.csv')
    tuning = pd.read_csv(out / 'INNER_TUNING.csv')
    selected = pd.read_csv(out / 'SELECTED_MODELS.csv')
    reg = pd.read_csv(root / 'SOURCE_ELIGIBILITY_REGISTRY.csv').fillna('')
    checks = {
        'eligibility_registry_unchanged_since_before_fit': digest(root / 'SOURCE_ELIGIBILITY_REGISTRY.csv')==receipt['registry_sha256'],
        'eligibility_implementation_unchanged_since_before_fit': digest(root / 'eligibility.py')==receipt['eligibility_code_sha256'],
        'passing_repair_checks_frozen_before_fit': digest(root / 'PRE_FIT_REPAIR_CHECKS.json')==receipt['pre_fit_checks_sha256'] and json.loads((root/'PRE_FIT_REPAIR_CHECKS.json').read_text())['status']=='PASS',
    }
    old = root.parent / 'bowen_rf_v1'
    if not old.exists(): old=root.parent/'experiment_rf_v1'
    checks['same_outer_splits_as_V1'] = digest(out/'SPLIT_ASSIGNMENTS.csv')==digest(old/'results/SPLIT_ASSIGNMENTS.csv')
    original = json.loads((root/'V1_BASELINE_HASHES.json').read_text())
    checks['all_original_V1_files_unchanged'] = all(digest(old/path)==value for path,value in original.items())
    keyed = master.set_index('row_id')
    split_ok, count_ok, target_ok, score_ok, selection_ok, grid_ok = [True]*6
    selections = []
    for outer, assignment in splits[splits.role=='train'].groupby('split',sort=False):
        train=keyed.loc[assignment.row_id].reset_index().copy()
        expected={i:(tr,te) for i,(tr,te) in enumerate(GroupKFold(4).split(train,train.Y,train.event_group),1)}
        for fold,(tr,te) in expected.items():
            split_ok &= set(train.event_group.iloc[tr]).isdisjoint(train.event_group.iloc[te])
        s=inner[inner.outer==outer]
        for (kind,parameters,fold),d in s.groupby(['model','parameters','inner_fold']):
            tr,te=expected[fold]
            want=train.iloc[te]
            dd=d.sort_values('training_position')
            split_ok &= list(dd.training_position)==list(te)
            target_ok &= list(dd.event_group)==list(want.event_group) and bool(np.allclose(dd.Y,want.Y,rtol=0,atol=1e-15))
            got=tuning[(tuning.outer==outer)&(tuning.model==kind)&(tuning.parameters==parameters)&(tuning.inner_fold==fold)].iloc[0]
            error=dd.Y.to_numpy()-dd.prediction.to_numpy()
            recomputed=pd.Series(np.abs(error)).groupby(dd.event_group.to_numpy()).mean().mean()
            count_ok &= got.validation_groups==want.event_group.nunique()
            score_ok &= bool(np.isclose(got.group_mae,recomputed,rtol=0,atol=1e-14))
        ss=[]
        for (kind,params),d in s.groupby(['model','parameters'],sort=False):
            errors=np.abs(d.Y.to_numpy()-d.prediction.to_numpy())
            # Pool all individual group errors directly; do not reuse tuning's fold aggregation.
            score=float(pd.Series(errors).groupby(d.event_group.to_numpy()).mean().mean())
            ss.append({'model':kind,'parameters':params,'score':score})
        candidates=pd.DataFrame(ss)
        for kind,ds in candidates.groupby('model',sort=False):
            winner=ds.loc[ds.score.idxmin()]
            chosen=selected[(selected.split==outer)&(selected.model==kind)].iloc[0]
            selection_ok &= json.loads(winner.parameters)==json.loads(chosen.parameters) and bool(np.isclose(winner.score,chosen.inner_group_mae,atol=1e-14,rtol=0))
            selections.append({'split':outer,'model':kind,'independently_selected_parameters':winner.parameters,'pooled_inner_group_mae':winner.score})
            grid_ok &= len(ds)==(15 if kind=='rf' else 4)
    pd.DataFrame(selections).to_csv(out/'INDEPENDENT_SELECTION_CHECK.csv',index=False)
    checks.update({
        'all_inner_training_validation_groups_disjoint': bool(split_ok),
        'recorded_inner_group_counts_match_reconstructed_splits': bool(count_ok),
        'inner_targets_and_groups_match_only_outer_training_rows': bool(target_ok),
        'every_inner_score_recomputed_from_saved_predictions': bool(score_ok),
        'every_selected_model_minimises_pooled_equal_group_inner_MAE': bool(selection_ok),
        'all_15_RF_and_4_ridge_candidates_tested_in_every_outer_training_set': bool(grid_ok),
    })
    c=codebook[(codebook.role_if_Y_sum=='X')&codebook.source.astype(str).str.contains('Census|SEIFA',case=False)].column
    rr=reg.set_index('column')
    checks['all_census_source_columns_have_release_rules'] = set(c).issubset(rr.index) and bool(rr.loc[c,'action'].eq('census_release').all())
    vintage=pd.to_numeric(master.info_pop_census_year,errors='coerce')
    starts=pd.to_datetime(master.first_fire_start)
    date_ok=True
    for column in c:
        rule=rr.loc[column]
        release=pd.to_datetime(vintage.map({2016:rule.date_2016,2021:rule.date_2021}),errors='coerce')
        bad=release.isna()|starts.le(release)
        date_ok &= x.loc[bad,column].isna().all()
    checks['no_census_or_SEIFA_cells_retained_before_release_guard'] = bool(date_ok)
    checks['neither_OSM_column_retains_pre_2019_values'] = bool(x.loc[starts<pd.Timestamp('2019-01-01'),['X_env_road_km_burned','X_env_road_km_within_100m_sum']].isna().all().all())
    excluded=rr[rr.family.isin(['remoteness_2021','bcarr_2025'])].index
    checks['unverified_remoteness_and_BCARR_vintages_excluded'] = all(column not in x for column in excluded)
    rf=tuning[tuning.model=='rf'].copy()
    leaf1=rf[rf.parameters.map(lambda p:json.loads(p)['min_samples_leaf']==1)]
    checks['leaf_1_candidates_actually_grew_deeper_than_one_split'] = bool(len(leaf1)>0 and leaf1.median_tree_depth.gt(1).all())
    trees=model.pipeline.named_steps['model'].estimators_
    structure=pd.DataFrame([{'tree':i,'depth':t.get_depth(),'leaves':t.get_n_leaves(), 'unique_sampled_rows':int(t.tree_.n_node_samples[0])} for i,t in enumerate(trees)])
    structure.to_csv(out/'PRIMARY_TREE_STRUCTURE.csv',index=False)
    checks['selected_primary_RF_has_500_inspected_trees'] = len(structure)==500
    return checks
