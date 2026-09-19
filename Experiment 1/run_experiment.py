"""Original decision-tree experiment. Run from any directory; writes Experiment 1/results."""

# Step 2
from pathlib import Path
import hashlib, json, platform
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn
from IPython.display import display, Markdown
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

_start = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd().resolve()
ROOT = next((p for p in [_start, *_start.parents] if (p/'NSW Data Panel.csv').is_file()), None)
assert ROOT is not None, 'Run from within the AUSSEF repository.'
SOURCE = ROOT / 'NSW Data Panel.csv'
assert SOURCE.exists(), 'Run this notebook with AUSSEF as the working directory.'
OUT = ROOT / 'Experiment 1' / 'results'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE_HASH = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
SEED, MAX_DEPTH, MIN_LEAF, MIN_TRAIN = 42, 3, 20, 100
TARGETS = {'operating_ratio_pct': 'percentage points',
           'cash_cover_months': 'months',
           'maintenance_ratio_pct': 'percentage points'}
pd.set_option('display.max_rows', 60)
pd.set_option('display.max_colwidth', 95)
raw = pd.read_csv(SOURCE)
assert not raw.duplicated(['council_key', 'year_start']).any()
assert raw[['council_key', 'year_start']].notna().all().all()
assert (raw.financial_year == raw.year_start.map(lambda y: f'{y}-{str(y+1)[-2:]}')).all()
print(f'{len(raw):,} rows; {len(raw.columns)} columns; {raw.council_key.nunique()} council keys')
print('Financial years:', ', '.join(sorted(raw.financial_year.unique())))
print('Source SHA-256:', SOURCE_HASH)

# Step 4
def unit_for(c):
    if c.endswith('_aud'): return 'AUD (nominal; price basis not supplied)'
    if c.endswith('_pct') or c == 'fesm_burned_pct_raw': return 'percent (raw fire share may be censored)'
    if c.endswith('_ha') or c == 'fesm_min_fire_size_ha_exclusive': return 'hectares'
    if c == 'cash_cover_months': return 'months'
    if c in ['current_ratio', 'debt_service_cover']: return 'ratio / multiple; exact definition unverified'
    if c == 'population': return 'persons'
    if c == 'area_km2': return 'square kilometres'
    if c == 'road_km': return 'kilometres'
    if c.endswith('_count'): return 'listed events / counts'
    if c == 'year_start': return 'financial-year start (calendar year)'
    if c.endswith('_row'): return 'source spreadsheet row number'
    if raw[c].dtype == bool: return 'Boolean quality / scope flag'
    return 'identifier, category, provenance or evidence text'

audit = pd.DataFrame([{'column': c, 'dtype': str(raw[c].dtype), 'unit': unit_for(c),
    'missing_n': int(raw[c].isna().sum()), 'missing_pct': raw[c].isna().mean()*100,
    'distinct_nonmissing': raw[c].nunique(),
    'min': raw[c].min() if pd.api.types.is_numeric_dtype(raw[c]) else None,
    'max': raw[c].max() if pd.api.types.is_numeric_dtype(raw[c]) else None}
    for c in raw])
audit.to_csv(OUT/'column_audit.csv', index=False)
display(audit)
missing_by_year = raw.groupby('financial_year').agg(rows=('council_key','size'))
for c in raw:
    missing_by_year[c + '__missing'] = raw.groupby('financial_year')[c].apply(lambda s: s.isna().sum())
missing_by_year.to_csv(OUT/'missingness_by_year.csv')
display(raw.groupby('financial_year')[list(TARGETS) + ['fesm_burned_ha']].count().rename_axis('FY (nonmissing counts)'))
identifiers = raw.groupby('council_key').agg(display_names=('council', lambda s: ' | '.join(sorted(s.unique()))),
    rows=('year_start','size'), first_year=('year_start','min'), last_year=('year_start','max'))
identifiers.to_csv(OUT/'council_identifiers.csv')
print('Rows per council:', identifiers.rows.value_counts().to_dict())
print('Keys with multiple display names:', (identifiers.display_names.str.contains(' | ', regex=False)).sum())

# Step 5
flag_cols = [c for c in raw if raw[c].dtype == bool or any(x in c for x in
    ['status', 'compatibility', 'disagreement', 'open_ended', 'carryover', 'damage_documented'])]
flags = pd.concat([raw[c].fillna('<missing>').value_counts(dropna=False).rename_axis('value')
                   .reset_index(name='rows').assign(column=c) for c in flag_cols], ignore_index=True)
flags[['column','value','rows']].to_csv(OUT/'quality_flag_counts.csv', index=False)
display(flags[['column','value','rows']])
print('Boundary-flagged keys:', sorted(raw.loc[raw.boundary_change_flag, 'council_key'].unique()))
print('Fire-share censored entries:', raw.fesm_burned_pct_raw.astype(str).str.startswith('<').sum())
print('Fire mapping minimum size by FY:')
display(raw.groupby('financial_year').fesm_min_fire_size_ha_exclusive.first())
# Check that the generic outcome flags refer to maintenance in this file.
assert (raw.outcome_observed == raw.maintenance_ratio_pct.notna()).all()
assert (raw.outcome_quality_eligible == (raw.outcome_observed & ~raw.maintenance_conflict)).all()
ratio = 100 * raw.actual_maintenance_aud / raw.required_maintenance_aud.replace(0, np.nan)
assert np.allclose(ratio, raw.maintenance_ratio_pct, equal_nan=True)
print('Maintenance ratio = 100 × actual / required maintenance; quality flags match its availability/conflicts.')

# Step 8
rationale = {
'operating_ratio_pct': 'Prior operating balance relative to revenue; fiscal persistence',
'cash_cover_months': 'Prior liquidity buffer measured in months',
'current_ratio': 'Prior current-asset/current-liability liquidity proxy; exact definition unverified',
'own_source_pct': 'Prior revenue autonomy / composition',
'debt_service_cover': 'Prior capacity to cover debt service',
'maintenance_ratio_pct': 'Prior actual-to-required maintenance adequacy',
'population': 'Prior council population / service scale',
'road_km': 'Prior road network / infrastructure scale'}
exposure_rationale = {
'fesm_burned_ha': 'Mapped burned hectares during t; scoped physical exposure, not damage',
'bushfire_declared_event_count': 'Listed bushfire event onsets during t',
'flood_declared_event_count': 'Listed flood event onsets during t; not inundated area'}
prior_cols = list(rationale)
exposure_cols = list(exposure_rationale)
features = [c+'__prior' for c in prior_cols] + [c+'__event' for c in exposure_cols]
predictor_table = pd.DataFrame(
    [{'predictor':c+'__prior', 'source_column':c, 'timing':'t−1', 'unit':unit_for(c), 'reason':r} for c,r in rationale.items()] +
    [{'predictor':c+'__event', 'source_column':c, 'timing':'t', 'unit':unit_for(c), 'reason':r} for c,r in exposure_rationale.items()])
predictor_table.to_csv(OUT/'predictor_rationale.csv', index=False)
display(predictor_table)
exclusions = audit[['column']].copy()
exclusions['role'] = exclusions.column.map(lambda c: 'prior predictor and/or target' if c in prior_cols else
    'event predictor' if c in exposure_cols else 'audit / alignment only; excluded from tree')
exclusions.to_csv(OUT/'source_column_roles.csv', index=False)

# Step 11
prior = raw[['council_key','year_start'] + prior_cols + ['boundary_change_flag','outcome_quality_eligible']].copy()
prior.loc[~prior.outcome_quality_eligible, 'maintenance_ratio_pct'] = np.nan
prior = prior.rename(columns={c:c+'__prior' for c in prior if c != 'council_key'})
prior['event_year'] = prior.year_start__prior + 1
future = raw[['council_key','year_start'] + list(TARGETS) + ['boundary_change_flag','outcome_quality_eligible']].copy()
future = future.rename(columns={c:c+'__future' for c in future if c != 'council_key'})
future['event_year'] = future.year_start__future - 1
panel = raw[['council_key','year_start'] + exposure_cols + ['boundary_change_flag']].rename(
    columns={'year_start':'event_year', **{c:c+'__event' for c in exposure_cols}})
panel = panel.merge(prior, on=['council_key','event_year'], how='left', validate='one_to_one')
panel = panel.merge(future, on=['council_key','event_year'], how='left', validate='one_to_one')
panel['target_year'] = panel.event_year + 1
panel['prior_year'] = panel.event_year - 1
assert set(features).issubset(panel.columns)
assert all(c.endswith(('__prior','__event')) for c in features)
assert (panel.loc[panel.year_start__prior.notna(), 'year_start__prior'] == panel.loc[panel.year_start__prior.notna(), 'prior_year']).all()
assert (panel.loc[panel.year_start__future.notna(), 'year_start__future'] == panel.loc[panel.year_start__future.notna(), 'target_year']).all()

# One mutually exclusive first-failure reason per target and row.
cohorts = {}
for target in TARGETS:
    d = panel.copy()
    checks = [
        ('no_exact_prior_year', d.year_start__prior.isna()),
        ('no_exact_future_year', d.year_start__future.isna()),
        ('boundary_flag', d.boundary_change_flag | d.boundary_change_flag__prior.eq(True) | d.boundary_change_flag__future.eq(True)),
        ('missing_target', ~np.isfinite(d[target+'__future'])),
    ]
    if target == 'maintenance_ratio_pct':
        checks.append(('target_maintenance_quality', ~d.outcome_quality_eligible__future.eq(True)))
    checks.append(('missing_or_ineligible_persistence', ~np.isfinite(d[target+'__prior'])))
    d['exclusion_reason'] = np.select([m for _,m in checks], [r for r,_ in checks], default='eligible')
    d['eligible'] = d.exclusion_reason.eq('eligible')
    cohorts[target] = d
alignment_audit = pd.concat([d[['council_key','prior_year','event_year','target_year','exclusion_reason']].assign(target=t)
                             for t,d in cohorts.items()], ignore_index=True)
alignment_audit.to_csv(OUT/'row_eligibility.csv', index=False)
coverage = alignment_audit.groupby(['target','target_year','exclusion_reason']).size().rename('rows').reset_index()
coverage.to_csv(OUT/'alignment_exclusions_by_year.csv', index=False)
display(coverage.pivot_table(index=['target','target_year'], columns='exclusion_reason', values='rows', fill_value=0))

# Step 13
def metrics(y, pred):
    return {'MAE': mean_absolute_error(y, pred),
            'RMSE': np.sqrt(mean_squared_error(y, pred)),
            'R2': r2_score(y, pred, force_finite=False) if len(y)>1 and np.var(y)>0 else np.nan}

def fy(y): return f'{int(y)}-{str(int(y)+1)[-2:]}'

fold_rows, metric_rows, prediction_rows, imputation_rows = [], [], [], []
latest, used_rows = {}, []
for target, d in cohorts.items():
    for test_year in sorted(d.target_year.unique()):
        event_year = test_year - 1
        # Exclude unavailable source years from the training candidate pool.
        train_pool = d[(d.target_year < event_year) & d.year_start__future.notna() & d.year_start__prior.notna()]
        test_pool = d[d.target_year == test_year]
        train, test = train_pool[train_pool.eligible], test_pool[test_pool.eligible]
        status = 'evaluated' if len(train)>=MIN_TRAIN and len(test)>=2 else 'skipped: insufficient eligible training/test rows'
        fold = {'target':target, 'test_year':test_year, 'test_fy':fy(test_year),
                'event_fy':fy(event_year), 'status':status,
                'train_candidate_n':len(train_pool), 'train_n':len(train), 'train_excluded_n':len(train_pool)-len(train),
                'test_candidate_n':len(test_pool), 'test_n':len(test), 'test_excluded_n':len(test_pool)-len(test),
                'training_target_years': '|'.join(map(str, sorted(train.target_year.unique()))),
                'embargoed_rows':int(((d.target_year == event_year) & d.year_start__future.notna()).sum())}
        for name, pool in [('train',train_pool),('test',test_pool)]:
            for reason, n in pool.loc[~pool.eligible,'exclusion_reason'].value_counts().items():
                fold[f'{name}_excluded__{reason}'] = n
        fold_rows.append(fold)
        if status != 'evaluated': continue
        assert train.target_year.max() < test.event_year.min()
        assert set(train.target_year).isdisjoint(test.target_year)
        assert train[features].notna().any().all(), 'All-missing training feature needs explicit review.'
        model = Pipeline([('imputer', SimpleImputer(strategy='median')),
                          ('tree', DecisionTreeRegressor(max_depth=MAX_DEPTH, min_samples_leaf=MIN_LEAF, random_state=SEED))])
        model.fit(train[features], train[target+'__future'])
        predictions = {'training_mean':np.repeat(train[target+'__future'].mean(), len(test)),
                       'persistence':test[target+'__prior'].to_numpy(),
                       'decision_tree':model.predict(test[features])}
        for name, pred in predictions.items():
            metric_rows.append({'target':target, 'test_year':test_year, 'test_fy':fy(test_year),
                                'model':name, 'n':len(test), **metrics(test[target+'__future'], pred)})
            prediction_rows.extend([{'target':target, 'test_year':test_year, 'council_key':k, 'model':name,
                                     'observed':y, 'predicted':p} for k,y,p in zip(test.council_key, test[target+'__future'], pred)])
        for feature, median in zip(features, model['imputer'].statistics_):
            imputation_rows.append({'target':target,'test_year':test_year,'feature':feature,'training_median':median,
                                    'train_missing':train[feature].isna().sum(),'test_missing':test[feature].isna().sum()})
        used = sorted({features[i] for i in model['tree'].tree_.feature if i >= 0})
        used_rows.extend([{'target':target,'test_year':test_year,'feature':f,'disaster_variable':f.endswith('__event')} for f in used])
        latest[target] = (test_year, model)
folds = pd.DataFrame(fold_rows).fillna({k:0 for k in pd.DataFrame(fold_rows) if '_excluded__' in k})
scores = pd.DataFrame(metric_rows)
predictions = pd.DataFrame(prediction_rows)
folds.to_csv(OUT/'fold_sample_sizes_and_exclusions.csv', index=False)
scores.to_csv(OUT/'validation_metrics_long.csv', index=False)
predictions.to_csv(OUT/'held_out_predictions.csv', index=False)
pd.DataFrame(imputation_rows).to_csv(OUT/'fold_imputation_audit.csv', index=False)
pd.DataFrame(used_rows).to_csv(OUT/'split_variables_all_folds.csv', index=False)
validation = scores.pivot(index=['target','test_year','test_fy'], columns='model', values=['MAE','RMSE','R2'])
validation.columns = ['__'.join(x) for x in validation.columns]
validation = folds.merge(validation.reset_index(), on=['target','test_year','test_fy'], how='left')
validation.to_csv(OUT/'year_by_year_validation.csv', index=False)
display(folds[['target','test_fy','status','train_n','train_excluded_n','test_n','test_excluded_n','training_target_years']])
for target in TARGETS:
    display(Markdown(f'### {target} — {TARGETS[target]}'))
    display(validation.loc[(validation.target==target) & validation.status.eq('evaluated'),
        ['test_fy','train_n','test_n'] + [c for c in validation if '__' in c and c.startswith(('MAE','RMSE','R2'))]].round(3))

# Step 15
node_records = []
for target, (test_year, model) in latest.items():
    tree = model['tree'].tree_
    def walk(node, depth=0, rule='all training rows'):
        leaf = tree.children_left[node] == tree.children_right[node]
        f = '' if leaf else features[tree.feature[node]]
        threshold = np.nan if leaf else tree.threshold[node]
        node_records.append({'target':target,'test_fy':fy(test_year),'node':node,'depth':depth,
            'is_leaf':leaf,'split_variable':f,'threshold':threshold,'training_n':tree.n_node_samples[node],
            'prediction':float(tree.value[node].ravel()[0]),'prediction_unit':TARGETS[target], 'path':rule})
        if not leaf:
            walk(tree.children_left[node],depth+1,rule+f' AND {f} <= {threshold:.6g}')
            walk(tree.children_right[node],depth+1,rule+f' AND {f} > {threshold:.6g}')
    walk(0)
    fig, ax = plt.subplots(figsize=(23, 10))
    plot_tree(model['tree'], feature_names=features, filled=True, rounded=True, precision=2, fontsize=9, ax=ax)
    ax.set_title(f'{target}: trained before event FY {fy(test_year-1)}; held-out outcome FY {fy(test_year)}', fontsize=15)
    fig.tight_layout()
    fig.savefig(OUT/f'{target}_latest_tree.png', dpi=160, bbox_inches='tight')
    fig.savefig(OUT/f'{target}_latest_tree.svg', bbox_inches='tight')
    plt.show()
    plt.close(fig)
nodes = pd.DataFrame(node_records)
nodes.to_csv(OUT/'latest_tree_nodes.csv', index=False)
for target in TARGETS:
    display(nodes.loc[nodes.target==target, ['test_fy','node','is_leaf','split_variable','threshold','training_n','prediction']].round(3))

# Step 17
pooled = pd.DataFrame([{'target':t,'model':m,'n':len(g),**metrics(g.observed,g.predicted)}
    for (t,m),g in predictions.groupby(['target','model'])])
pooled.to_csv(OUT/'pooled_validation_metrics.csv', index=False)
display(pooled.round(3))
interpretation = []
verdicts = {}
for target in TARGETS:
    p = pooled[pooled.target==target].set_index('model')
    annual = scores[scores.target==target].pivot(index='test_year',columns='model',values='MAE')
    wins = ((annual.decision_tree < annual.training_mean) & (annual.decision_tree < annual.persistence))
    beats = all(p.loc['decision_tree',metric] < p.loc[b,metric]
                for metric in ['MAE','RMSE'] for b in ['training_mean','persistence'])
    positive = p.loc['decision_tree','R2'] > 0
    nfold = len(annual)
    verdict = ('GO' if beats and positive and nfold>=3 and wins.all() else
               'CONDITIONAL GO' if beats and positive and nfold>=2 and wins.sum()>=np.ceil(nfold/2) else 'NO-GO')
    verdicts[target] = verdict
    used = pd.DataFrame(used_rows)
    used = used[used.target==target]
    all_used = sorted(used.feature.unique())
    disaster = sorted(used.loc[used.disaster_variable,'feature'].unique())
    latest_used = sorted(used.loc[used.test_year==latest[target][0], 'feature'].unique())
    text = (f"### {'Primary' if target=='operating_ratio_pct' else 'Secondary'}: {target} — {verdict}\n"
            f"Across {nfold} future-year folds ({int(p.loc['decision_tree','n'])} held-out rows), "
            f"tree MAE/RMSE/R² = {p.loc['decision_tree','MAE']:.3f} / {p.loc['decision_tree','RMSE']:.3f} / {p.loc['decision_tree','R2']:.3f}. "
            f"Mean baseline = {p.loc['training_mean','MAE']:.3f} / {p.loc['training_mean','RMSE']:.3f} / {p.loc['training_mean','R2']:.3f}; "
            f"persistence = {p.loc['persistence','MAE']:.3f} / {p.loc['persistence','RMSE']:.3f} / {p.loc['persistence','R2']:.3f}. "
            f"The tree beat both baselines on MAE in {int(wins.sum())}/{nfold} individual future years. "
            f"It {'did' if beats else 'did not'} beat both baselines on both pooled error measures.\n\n"
            f"Variables used across folds: {', '.join(all_used) or 'none'}. "
            f"Latest tree: {', '.join(latest_used) or 'none'}. "
            f"Disaster variables used in any fold: {', '.join(disaster) or 'none'}. "
            "Use in a split does not establish a causal effect or incremental predictive benefit; absence does not establish that disasters have no effect. "
            "An exposure-free comparison would be needed to isolate incremental predictive value.\n")
    interpretation.append(text)
primary_verdict = verdicts['operating_ratio_pct']
conclusion = (f'## Overall verdict: {primary_verdict} for further predictive modelling\n'
    'This verdict follows the primary operating-ratio forward-validation rule, not training fit or secondary results. '
    'A NO-GO means do not advance this specification to more complex predictive models on the strength of these results; '
    'it does not rule out a better-measured future dataset. A conditional or full GO supports further validation only, not deployment or causal claims.\n\n'
    'Limitations: few independent future years; repeated councils and shared disasters; unverified accounting definitions and publication dates; '
    'changing fire-mapping thresholds and unverified polygon vintage; declaration onsets rather than flood intensity/duration; '
    'unmeasured later shocks during t+1; missing fiscal outcomes; a common persistence-observed cohort; and potentially influential fiscal extremes. '
    'There is no claim to predict previously unseen councils. No causal feature importance is reported.')
report = '\n'.join(interpretation) + '\n' + conclusion
# Convert escaped newlines so the saved report is normal Markdown.
(OUT/'interpretation.md').write_text(report)
display(Markdown(report))

# Step 18
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH, 'Source changed!'
assert (folds.train_candidate_n == folds.train_n + folds.train_excluded_n).all()
assert (folds.test_candidate_n == folds.test_n + folds.test_excluded_n).all()
assert not predictions.duplicated(['target','test_year','council_key','model']).any()
assert scores.groupby(['target','test_year']).n.nunique().eq(1).all()
manifest = {'source':'NSW Data Panel.csv','sha256':SOURCE_HASH,'rows':len(raw),'columns':len(raw.columns),
    'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'sklearn':sklearn.__version__,
    'model':{'max_depth':MAX_DEPTH,'min_samples_leaf':MIN_LEAF,'random_state':SEED},
    'min_train_rows':MIN_TRAIN,'training_rule':'training outcome year < test event year', 'verdicts':verdicts}
(OUT/'run_manifest.json').write_text(json.dumps(manifest, indent=2))
readme = f"""# AUSSEF exploratory fiscal decision tree

Run `Experiment 1/run_experiment.py` from the AUSSEF directory with Python, pandas, NumPy, scikit-learn, matplotlib, IPython and a Jupyter kernel. The notebook uses only `NSW Data Panel.csv`, checks its SHA-256 before/after, and writes derived files here. Rerunning replaces these generated summaries/figures.

For each council_key, t−1 fiscal/scale variables plus t mapped burned hectares and bushfire/flood declaration counts predict t+1 operating ratio (primary), cash cover and maintenance ratio (separate secondary targets). Exact-year joins prevent gaps being bridged. No composite index. The fixed depth-3 tree has a minimum 20 observations per leaf. Medians are fitted within training folds only.

Expanding-window tests hold out whole financial years; training outcome years must be strictly before the test exposure year. Publication timestamps are unavailable, so this is retrospective feasibility evidence. Observed pre-event target values are required to compare persistence, training mean and tree on identical rows. Missing targets, boundary flags, and maintenance-specific quality failures are excluded with row-level reasons. Other missing predictors are median-imputed. No random split, tuning or advanced ensemble is used.

MAE is average absolute error; RMSE penalises large errors more; both use percentage points for ratios and months for cash cover. Out-of-sample R² compares squared errors to variation in held-out outcomes; negative values are retained. Pooled and individual-year results are both reported.

Start with `interpretation.md`, `year_by_year_validation.csv`, and `pooled_validation_metrics.csv`. `fold_sample_sizes_and_exclusions.csv` records evaluated/skipped folds. `row_eligibility.csv` and `alignment_exclusions_by_year.csv` document exclusions. `column_audit.csv`, `missingness_by_year.csv`, `quality_flag_counts.csv`, and `council_identifiers.csv` document the source. `predictor_rationale.csv` and `source_column_roles.csv` explain scope. `held_out_predictions.csv`, `fold_imputation_audit.csv`, and `split_variables_all_folds.csv` support audit. `latest_tree_nodes.csv` includes all splits and leaf paths; each target has PNG/SVG tree figures. `run_manifest.json` records configuration and source hash.

Verdict: **{primary_verdict}** under the notebook's predeclared primary-outcome rule. Secondary results do not override it. See interpretation for measured comparisons.

Limitations: a handful of future years; repeated councils/shared shocks; no certification of historical data availability or accounting definitions; boundary uncertainty and four excluded councils; changing mapped-fire scope; declaration counts do not establish physical flooding or zero disaster exposure; missing outcomes and selection into the persistence-observed cohort; fiscal extremes; no causal or unseen-council inference. No-disaster split use does not prove no disaster effect, and split use does not establish incremental exposure value.
"""
(OUT/'README.md').write_text(readme)
print('Source unchanged. Alignment, fold counts, common evaluation samples and prediction uniqueness checks passed.')
print('Overall verdict:', primary_verdict)