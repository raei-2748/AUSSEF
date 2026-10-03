"""Read-only audit of completed V1. Reuses saved scores; never fits a model."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import warnings

ROOT = Path(__file__).resolve().parent
V1 = ROOT.parent / 'bowen_rf_v1'
if not V1.exists():
    V1 = ROOT.parent / 'experiment_rf_v1'
os.environ.setdefault('MPLCONFIGDIR', str(V1 / '.mplconfig'))
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    spec = importlib.util.spec_from_file_location('v1_runner', V1 / 'run_experiment.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    m = pd.read_csv(V1 / 'snapshot/master.csv')
    cb = pd.read_csv(V1 / 'snapshot/codebook.csv').query("sheet == 'master'")
    x, rules = runner.mask_inputs(m, cb)
    audit = json.loads((V1 / 'AUDIT.json').read_text())
    assignments = pd.read_csv(V1 / 'results/SPLIT_ASSIGNMENTS.csv')
    tuning = pd.read_csv(V1 / 'results/INNER_TUNING.csv')
    pred = pd.read_csv(V1 / 'results/HELD_OUT_PREDICTIONS.csv')
    metrics = pd.read_csv(V1 / 'results/MODEL_RESULTS.csv')

    folds, scores, selections = [], [], []
    for outer, d in assignments[assignments.role == 'train'].groupby('split', sort=False):
        train = m.set_index('row_id').loc[d.row_id].reset_index().copy()
        groups = train.event_group.to_numpy()
        counts = {}
        for fold, (_, te) in enumerate(GroupKFold(4).split(train, train.Y, groups), 1):
            count = len(np.unique(groups[te]))
            counts[fold] = count
            folds.append({'outer': outer, 'inner_fold': fold, 'validation_rows': len(te),
                          'validation_groups': count, 'original_fold_weight': .25,
                          'correct_equal_group_fold_weight': count / len(np.unique(groups))})
        tt = tuning[tuning.outer == outer].copy()
        tt['n_groups'] = tt.inner_fold.map(counts)
        tt['weighted_score'] = tt.group_mae * tt.n_groups
        ss = tt.groupby(['model', 'parameters'], sort=False).agg(
            original=('group_mae', 'mean'), total=('weighted_score', 'sum'), n=('n_groups', 'sum'))
        ss['equal_group_score'] = ss.total / ss.n
        ss = ss.reset_index()
        scores.append(ss.assign(outer=outer))
        for model, s in ss.groupby('model'):
            original = s.loc[s.original.idxmin(), 'parameters']
            corrected = s.loc[s.equal_group_score.idxmin(), 'parameters']
            selections.append({'outer': outer, 'model': model, 'original': original,
                               'corrected': corrected, 'choice_changed': original != corrected})
    pd.DataFrame(folds).to_csv(ROOT / 'INNER_FOLD_WEIGHTS.csv', index=False)
    pd.concat(scores).to_csv(ROOT / 'REAGGREGATED_TUNING.csv', index=False)
    pd.DataFrame(selections).to_csv(ROOT / 'SELECTION_AUDIT.csv', index=False)

    bundle = joblib.load(V1 / 'results/RF_MODEL.joblib')
    forest = bundle['pipeline'].named_steps['model']
    trees = pd.DataFrame([{'tree': i, 'depth': t.get_depth(), 'leaves': t.get_n_leaves(),
                           'unique_sampled_rows': t.tree_.n_node_samples[0]}
                          for i, t in enumerate(forest.estimators_)])
    trees.to_csv(ROOT / 'PRIMARY_TREE_STRUCTURE.csv', index=False)

    year = pd.to_datetime(m.first_fire_start).dt.year
    vintage = pd.to_numeric(m.info_pop_census_year, errors='coerce')
    exposures = ['X_socio_pop_in_fire', 'X_socio_pop_within_1km', 'X_socio_pop_within_5km',
                 'X_socio_pop_within_5km_all_councils', 'X_socio_dwellings_in_fire',
                 'X_socio_dwellings_within_1km', 'X_socio_dwellings_within_5km',
                 'X_socio_dwellings_occupied']
    dated = []
    for column in exposures + ['X_env_road_km_within_100m_sum', 'X_socio_remoteness',
                               'X_socio_remoteness_class_max']:
        reference = vintage if column in exposures else pd.Series(
            2019 if column.startswith('X_env_road') else 2021, index=m.index)
        affected = reference.gt(year) & x[column].notna()
        entry = cb[cb.column == column].iloc[0]
        dated.append({'column': column, 'source': entry.source,
                      'v1_rule': rules[rules.column == column].iloc[0]['rule'],
                      'retained_future_reference_cells': int(affected.sum()),
                      'row_ids': ';'.join(m.loc[affected, 'row_id']),
                      'interpretation': 'reference-period mismatch; not verified target leakage'})
    pd.DataFrame(dated).to_csv(ROOT / 'MISSED_REFERENCE_PERIODS.csv', index=False)

    discrepancies = []
    for split in ['primary_recent_seasons', 'group_cv_pooled']:
        d = pred[pred.split == split] if split != 'group_cv_pooled' else pred[pred.split.str.startswith('group_cv_')]
        for model in ['mean', 'median', 'ridge', 'rf']:
            p = d[f'pred_{model}']
            computed = {'group_mae': runner.group_mae(d.Y, p, d.event_group),
                        'row_mae': mean_absolute_error(d.Y, p),
                        'rmse': np.sqrt(mean_squared_error(d.Y, p)), 'r2': r2_score(d.Y, p)}
            recorded = metrics[(metrics.split == split) & (metrics.model == model)].iloc[0]
            discrepancies.extend(abs(value - recorded[key]) for key, value in computed.items())
    primary = pred[pred.split == 'primary_recent_seasons']
    test = m.set_index('row_id').loc[primary.row_id].copy()
    xx = x.loc[test.index.map(dict(zip(m.row_id, m.index)))].copy()
    for column in bundle['numeric_columns']:
        xx[column] = pd.to_numeric(xx[column], errors='coerce').astype(float)
    for column in bundle['categorical_columns']:
        xx[column] = xx[column].map(lambda v: np.nan if pd.isna(v) else str(v)).astype(object)
    reproduced = np.clip(bundle['pipeline'].predict(xx[bundle['columns']]), 0, 1)

    summary = {
        'status': 'V1_REPRODUCIBLE_BUT_METHOD_CORRECTIONS_REQUIRED',
        'no_new_fits_or_target_changes': True,
        'source_hash_unchanged': digest(Path(audit['source'])) == audit['source_sha256'],
        'snapshot_hash_matches_source': digest(V1 / 'snapshot/nsw_bushfires_2015_2025_XY.xlsx') == audit['source_sha256'],
        'maximum_recomputed_metric_difference': float(max(discrepancies)),
        'maximum_saved_model_prediction_difference': float(np.max(np.abs(reproduced - primary.pred_rf.to_numpy()))),
        'primary_selection_changes': [s for s in selections if s['outer'] == 'primary_recent_seasons' and s['choice_changed']],
        'secondary_selection_changes': [s for s in selections if s['outer'] != 'primary_recent_seasons' and s['choice_changed']],
        'primary_tree_depth_min_median_max': [int(trees.depth.min()), float(trees.depth.median()), int(trees.depth.max())],
        'primary_tree_leaves_min_median_max': [int(trees.leaves.min()), float(trees.leaves.median()), int(trees.leaves.max())],
        'primary_one_split_tree_count': int(trees.depth.eq(1).sum()),
        'primary_unique_sampled_rows_min_median_max': [int(trees.unique_sampled_rows.min()), float(trees.unique_sampled_rows.median()), int(trees.unique_sampled_rows.max())],
        'missed_reference_columns': dated,
        'interpretation': 'Original primary scores reproduce. Equal-group retuning does not change primary choice, but changes CV fold 3. Corrected predictions not fitted. Narrow RF grid and source-vintage gaps prevent a conclusive RF feasibility claim.',
        'audited_input_hashes': {str(p.relative_to(V1)): digest(p) for p in [V1 / 'PROTOCOL.md', V1 / 'run_experiment.py', V1 / 'results/INNER_TUNING.csv', V1 / 'results/HELD_OUT_PREDICTIONS.csv', V1 / 'results/RF_MODEL.joblib']},
    }
    (ROOT / 'AUDIT_RESULTS.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ['missed_reference_columns', 'audited_input_hashes']}, indent=2))


if __name__ == '__main__':
    main()
