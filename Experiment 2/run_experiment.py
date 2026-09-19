# %% [markdown]
# # AUSSEF V2: retrospective out-of-time fiscal prediction
#
# Can the longer matched history beat persistence consistently? Operating performance is primary;
# cash cover and maintenance are separate secondary outcomes. This is a retrospective evaluation
# of current data vintages, not a historically executable forecast or a causal disaster study.

# %%
from pathlib import Path
import hashlib, json, platform, math, warnings
import numpy as np
import pandas as pd
import matplotlib
from IPython import get_ipython
if get_ipython() is not None:
    get_ipython().run_line_magic('matplotlib', 'inline')
else:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sklearn
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from IPython.display import display, Markdown

# Locate shared source panels from the notebook folder or the script location.
_start = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd().resolve()
ROOT = next((p for p in [_start, *_start.parents] if (p/'NSW Data Panel.csv').is_file()), None)
assert ROOT is not None, 'Run the notebook from within the AUSSEF repository.'
OUT = ROOT/'Experiment 2/results'
OUT.mkdir(parents=True, exist_ok=True)
FISCAL = ROOT/'Experiment 2/data/fiscal_panel_v2/NSW_Fiscal_Panel_V2_candidate.csv'
EXPOSURE = ROOT/'Experiment 2/data/disaster_exposure_v2/NSW_Disaster_Exposure_V2_candidate.csv'
NOTEBOOK = ROOT/'Experiment 2/experiment.ipynb'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
# Graphify is an index maintained by repository instructions, not a research input/output.
frozen = {str(p.relative_to(ROOT)):digest(p) for p in ROOT.rglob('*')
          if p.is_file() and OUT not in p.parents and p != NOTEBOOK
          and 'graphify-out' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts}

TARGETS = {'operating_ratio_pct':'percentage points', 'cash_cover_months':'months',
           'maintenance_ratio_pct':'percentage points'}
PRIOR = ['operating_ratio_pct','cash_cover_months','current_ratio','own_source_pct',
         'debt_service_cover','maintenance_ratio_pct','population','road_km']
NUMERIC = [c+'__prior' for c in PRIOR]
FIRE = 'fesm_burned_ha__event'
DECLARATIONS = ['bushfire_declared__event','flood_declared__event']
SPECS = ['fiscal_only','fiscal_plus_fire','fiscal_plus_disaster']
SEED, MIN_TRAIN, MAX_DEPTH, MIN_LEAF = 42, 100, 3, 20
ALPHAS, DEFAULT_ALPHA = [0.1, 1.0, 10.0, 100.0], 10.0
CONFIG = dict(targets=TARGETS, fiscal_predictors=PRIOR, disaster_predictors=[FIRE]+DECLARATIONS,
    specs=SPECS, min_train=MIN_TRAIN, min_test=2, max_depth=MAX_DEPTH,
    min_samples_leaf=MIN_LEAF, seed=SEED, ridge_alphas=ALPHAS, earliest_fold_alpha=DEFAULT_ALPHA,
    temporal_rule='prior=t-1; exposure=t; target=t+1; train target < test target-1',
    tuning='inner expanding target-year folds with same embargo; fixed alpha10 if none',
    short_history_rule='prior financial year >=2017; same V2 councils, targets and quality rules',
    consistency_rule='MAE and RMSE both beat persistence in >=75% of held-out years and both pooled errors improve',
    primary_metric='MAE; RMSE and R2 retained; no outcome trimming or test-year selection',
    interpretation='retrospective current-vintage data; no ex-ante or causal claim')
(OUT/'experiment_specification.json').write_text(json.dumps(CONFIG,indent=2))
pd.set_option('display.max_columns',12)
pd.set_option('display.max_rows',30)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'figure.dpi':110,'savefig.dpi':170})
def fy(y): return f'{int(y)}-{str(int(y)+1)[-2:]}'

# %% [markdown]
# ## 1. Merge without silently reusing the old exposure columns
# Fiscal V2 already contains an older exposure layer. Retain those columns under a `legacy_`
# prefix, and make exposure V2 authoritative. A one-to-one outer-join audit must show the same
# 103 council keys and all 13 years in both inputs. No source file is changed.

# %%
fiscal = pd.read_csv(FISCAL)
exposure = pd.read_csv(EXPOSURE)
selection = pd.read_csv(ROOT/'Experiment 2/data/fiscal_panel_v2/council_selection.csv')
keys = set(selection.loc[selection.included,'council_key'])
join_keys = ['council_key','year_start']
assert len(keys)==103
for frame in [fiscal,exposure]:
    assert not frame.duplicated(join_keys).any()
    assert set(frame.council_key)==keys and len(frame)==1339
    assert frame.groupby('year_start').size().eq(103).all()
join_audit = fiscal[join_keys].merge(exposure[join_keys],on=join_keys,how='outer',indicator=True,validate='one_to_one')
assert join_audit['_merge'].eq('both').all()
assert fiscal.set_index(join_keys).financial_year.sort_index().equals(exposure.set_index(join_keys).financial_year.sort_index())
assert fiscal.set_index(join_keys).council_name.sort_index().equals(exposure.set_index(join_keys).council_name.sort_index())
legacy = fiscal.columns[fiscal.columns.get_loc('fesm_burned_ha'):fiscal.columns.get_loc('exposure_coverage_status')+1].tolist()
fiscal = fiscal.rename(columns={c:'legacy_'+c for c in legacy})
fiscal = fiscal.rename(columns={'historical_extension':'fiscal_historical_extension'})
exposure = exposure.rename(columns={'historical_extension':'exposure_historical_extension'})
merged = fiscal.merge(exposure.drop(columns=['council_name','financial_year']),on=join_keys,validate='one_to_one')
assert not any(c.endswith(('_x','_y')) for c in merged)
merged.to_csv(OUT/'NSW_Matched_Fiscal_Disaster_V2.csv',index=False)
join_audit.to_csv(OUT/'merge_audit.csv',index=False)
# Fiscal quality rules are applied to a working copy, never to the merged evidence file.
clean = merged.copy()
clean.loc[clean.debt_service_cover_requires_review,'debt_service_cover'] = np.nan
clean.loc[clean.maintenance_conflict | clean.required_maintenance_aud.le(0),'maintenance_ratio_pct'] = np.nan
clean.loc[clean.year_start.eq(2012),'cash_cover_months'] = np.nan
assert clean.loc[clean.year_start.eq(2012),'cash_cover_months'].isna().all()
input_audit = pd.DataFrame([dict(variable=c,year=int(y),rows=len(g),known=int(g[c].notna().sum()),
    zero=int(g[c].eq(0).sum()),missing=int(g[c].isna().sum()))
    for y,g in clean.groupby('year_start') for c in PRIOR+['fesm_burned_ha','bushfire_declared','flood_declared']])
input_audit.to_csv(OUT/'input_coverage.csv',index=False)
display(clean.groupby('financial_year')[list(TARGETS)+['fesm_burned_ha','bushfire_declared','flood_declared']].count())
print(f'Matched {len(merged):,} annual rows for {len(keys)} councils; no unmatched rows.')

# %% [markdown]
# ## 2. Predictor decisions and exact year alignment
# Persistence predicts the outcome in t+1 using the council's value in t−1, a two-year fiscal gap.
# Cash cover starts with comparable t−1 observations in 2013–14. Maintenance uses only valid,
# positive required-spending denominators and V2's arithmetic-quality filter. This harmonises
# the ratio calculation, not councils' underlying engineering assessments.
#
# Keep the original eight fiscal predictors. Sparse statement components, realised grants,
# future-year fields, council identifiers, source metadata and exact historical declaration
# counts are not predictors. Counts cannot be pooled with partial lower bounds. The disaster
# specification instead uses mapped hectares and explicit yes/no/unknown declaration states.
# A fire-only intermediate ablation separates fire information from declaration/coverage patterns.

# %%
rationale = {
'operating_ratio_pct':'Prior recurring operating balance relative to revenue',
'cash_cover_months':'Prior liquidity buffer; common-definition column only',
'current_ratio':'Prior unrestricted short-term financial capacity',
'own_source_pct':'Prior revenue autonomy',
'debt_service_cover':'Prior debt-service capacity; flagged denominator cases withheld',
'maintenance_ratio_pct':'Prior spending adequacy; quality-filtered ratio only',
'population':'Prior council scale', 'road_km':'Prior comparable local/regional road burden; early broader scope withheld',
'fesm_burned_ha':'Event-year mapped vegetation burn; physical scope and sensor changes remain',
'bushfire_declared':'Event-year bushfire declaration presence, absence within inventory, or unknown',
'flood_declared':'Event-year explicitly flood-labelled declaration presence, scoped absence, or unknown'}
pd.DataFrame([dict(variable=k,timing='t-1' if k in PRIOR else 't',reason=v) for k,v in rationale.items()]).to_csv(OUT/'predictor_dictionary.csv',index=False)
prior_cols = ['council_key','year_start']+PRIOR+['reporting_months','cash_definition_status','maintenance_conflict','operating_definition_regime']
prior = clean[prior_cols].rename(columns={c:c+'__prior' for c in prior_cols if c!='council_key'})
prior['event_year'] = prior.year_start__prior+1
future_cols = ['council_key','year_start']+list(TARGETS)+['reporting_months','maintenance_conflict','operating_definition_regime']
future = clean[future_cols].rename(columns={c:c+'__future' for c in future_cols if c!='council_key'})
future['event_year'] = future.year_start__future-1
excols = ['fesm_burned_ha','bushfire_declared','flood_declared','fesm_status','fesm_min_fire_size_ha_exclusive',
          'fesm_sensor','bushfire_declaration_status','flood_declaration_status']
aligned = clean[['council_key','council_name','year_start']+excols].rename(columns={'year_start':'event_year',**{c:c+'__event' for c in excols}})
aligned = aligned.merge(prior,on=['council_key','event_year'],how='left',validate='one_to_one').merge(future,on=['council_key','event_year'],how='left',validate='one_to_one')
aligned['prior_year'], aligned['target_year'] = aligned.event_year-1, aligned.event_year+1
assert aligned.loc[aligned.year_start__prior.notna(),'year_start__prior'].eq(aligned.loc[aligned.year_start__prior.notna(),'prior_year']).all()
assert aligned.loc[aligned.year_start__future.notna(),'year_start__future'].eq(aligned.loc[aligned.year_start__future.notna(),'target_year']).all()
aligned.to_csv(OUT/'aligned_forecasting_panel.csv',index=False)
cohorts = {}
for target in TARGETS:
    d=aligned.copy()
    checks=[('no_exact_prior_year',d.year_start__prior.isna()),('no_exact_target_year',d.year_start__future.isna()),
            ('non_annual_prior_or_target',d.reporting_months__prior.ne(12)|d.reporting_months__future.ne(12))]
    if target=='cash_cover_months': checks += [('cash_definition_not_comparable',d.prior_year.lt(2013))]
    if target=='maintenance_ratio_pct':
        checks += [('maintenance_target_conflict',d.maintenance_conflict__future.eq(True)),
                   ('maintenance_prior_conflict',d.maintenance_conflict__prior.eq(True))]
    checks += [('missing_target',~np.isfinite(d[target+'__future'])),
               ('missing_eligible_persistence',~np.isfinite(d[target+'__prior']))]
    d['exclusion_reason']=np.select([m for _,m in checks],[r for r,_ in checks],default='eligible')
    d['eligible']=d.exclusion_reason.eq('eligible');cohorts[target]=d
eligibility=pd.concat([d[['council_key','prior_year','event_year','target_year','exclusion_reason']].assign(target=t)
                       for t,d in cohorts.items()],ignore_index=True)
eligibility.to_csv(OUT/'row_eligibility.csv',index=False)
eligibility.groupby(['target','target_year','exclusion_reason']).size().rename('rows').reset_index().to_csv(OUT/'exclusions_by_target_year.csv',index=False)
display(eligibility.groupby(['target','exclusion_reason']).size().unstack(fill_value=0))

# %% [markdown]
# ## 3. Training-fold preprocessing only
# Numeric missing values receive that training fold's median, plus an explicit missing indicator.
# A numeric variable entirely missing in training is withheld for that fold; no test value helps
# choose its fill. For declarations, separate fixed indicators encode listed / no-listed / unknown.
# Unknown exposure therefore never becomes a claimed observed zero. Ridge standardisation is
# learned on the training rows. Trees use unstandardised values for readable thresholds.

# %%
class FoldPreprocessor:
    def __init__(self,spec): self.spec=spec
    def fit(self,train):
        self.numeric=NUMERIC+([FIRE] if self.spec!='fiscal_only' else [])
        self.active=[c for c in self.numeric if train[c].notna().any()]
        self.medians=train[self.active].median()
        self.names=self.active+[c+'__missing' for c in self.numeric]
        self.declarations=DECLARATIONS if self.spec=='fiscal_plus_disaster' else []
        for c in self.declarations: self.names += [c+'__listed',c+'__no_listed',c+'__unknown']
        X=self.transform(train)
        self.mean=X.mean(axis=0);self.scale=X.std(axis=0)
        self.scale[self.scale==0]=1.0
        return self
    def transform(self,frame,standardise=False):
        chunks=[frame[self.active].fillna(self.medians).to_numpy(float),frame[self.numeric].isna().to_numpy(float)]
        for c in self.declarations:
            assert frame[c].dropna().isin([0,1]).all()
            chunks += [np.column_stack([frame[c].eq(1),frame[c].eq(0),frame[c].isna()]).astype(float)]
        X=np.column_stack(chunks)
        assert np.isfinite(X).all() and X.shape[1]==len(self.names)
        return (X-self.mean)/self.scale if standardise else X

def metric(y,p):
    return dict(MAE=float(mean_absolute_error(y,p)),RMSE=float(np.sqrt(mean_squared_error(y,p))),
                R2=float(r2_score(y,p,force_finite=False)) if len(y)>1 and np.var(y)>0 else np.nan)

# %% [markdown]
# ## 4. Ridge selection uses earlier years only
# Four predeclared alpha values reproduce the earlier diagnostic search size. Inner validation
# uses whole future years and the same one-year embargo. If no inner forward fold exists,
# alpha=10 is fixed in advance. There is no grouped/random fallback and no test-year tuning.

# %%
tuning_rows=[]; inner_rows=[]
def choose_alpha(train,target,spec,history,outer_year):
    inner=[]
    for year in sorted(train.target_year.unique()):
        a=train[train.target_year<year-1];b=train[train.target_year==year]
        if len(a)>=MIN_TRAIN and len(b)>=2:
            assert a.target_year.max()<b.event_year.min()
            inner.append((year,a,b))
            inner_rows.append(dict(target=target,spec=spec,history=history,outer_year=outer_year,
                inner_year=int(year),train_n=len(a),validation_n=len(b),train_target_max=int(a.target_year.max()),
                validation_event_year=int(year-1)))
    if not inner:return DEFAULT_ALPHA,'fixed_no_inner_forward_fold'
    errors={a:[] for a in ALPHAS}
    for year,a,b in inner:
        prep=FoldPreprocessor(spec).fit(a);X=prep.transform(a,True);V=prep.transform(b,True)
        for alpha in ALPHAS:
            model=Ridge(alpha=alpha).fit(X,a[target+'__future'])
            mae=mean_absolute_error(b[target+'__future'],model.predict(V));errors[alpha].append(mae)
            tuning_rows.append(dict(target=target,spec=spec,history=history,outer_year=outer_year,
                inner_year=int(year),alpha=alpha,MAE=float(mae),validation_n=len(b)))
    # Equal weight per inner year; ties prefer stronger regularisation.
    return min(ALPHAS,key=lambda a:(np.mean(errors[a]),-a)),'inner_forward_equal_year_MAE'

# %% [markdown]
# ## 5. Expanding-year evaluation and the short-history control
# For test target year Y, train only on target years <Y−1. Thus even the preceding year's
# outcome is embargoed, retaining the original experiment's conservative timing. A fold needs
# at least 100 eligible training rows and two test rows. All skipped folds and exclusions remain.
# Each model and ablation is scored on identical rows. Short history restricts t−1 to 2017–18
# onward; comparisons with long history are made only on common later test rows.

# %%
fold_rows=[]; score_rows=[]; prediction_rows=[]; preprocessing_rows=[]; node_rows=[]; split_rows=[]; coefficient_rows=[]
latest_trees={}
for target,d0 in cohorts.items():
    for history in ['long','short_2017_onward']:
        d=d0.copy()
        history_allowed=pd.Series(True,index=d.index) if history=='long' else d.prior_year.ge(2017)
        for year in sorted(d.target_year.unique()):
            rawtrain=d[(d.target_year<year-1)&d.year_start__prior.notna()&d.year_start__future.notna()]
            testpool=d[d.target_year==year]
            train=rawtrain[rawtrain.eligible & history_allowed.loc[rawtrain.index]]
            test=testpool[testpool.eligible & history_allowed.loc[testpool.index]]
            reason='evaluated' if len(train)>=MIN_TRAIN and len(test)>=2 else 'skipped_insufficient_train_or_test'
            row=dict(target=target,history=history,test_year=int(year),test_fy=fy(year),status=reason,
                train_candidate_n=len(rawtrain),train_n=len(train),train_excluded_n=len(rawtrain)-len(train),
                test_candidate_n=len(testpool),test_n=len(test),test_excluded_n=len(testpool)-len(test),
                training_target_years='|'.join(map(str,sorted(train.target_year.unique()))),
                train_target_max=int(train.target_year.max()) if len(train) else np.nan,
                embargoed_eligible_rows=int((d.target_year.eq(year-1)&d.eligible&history_allowed).sum()))
            for label,pool in [('train',rawtrain),('test',testpool)]:
                reasons=pool.exclusion_reason.copy();reasons.loc[~history_allowed.loc[pool.index]]='outside_history_window'
                for why,n in reasons[reasons.ne('eligible')].value_counts().items():row[f'{label}_excluded__{why}']=int(n)
            fold_rows.append(row)
            if reason!='evaluated':continue
            assert train.target_year.max()<test.event_year.min()
            truth=test[target+'__future'].to_numpy();preds=[('baseline','persistence',test[target+'__prior'].to_numpy(),np.nan),
                ('baseline','training_mean',np.repeat(train[target+'__future'].mean(),len(test)),np.nan)]
            for spec in SPECS:
                alpha,tuning=choose_alpha(train,target,spec,history,int(year))
                prep=FoldPreprocessor(spec).fit(train)
                ridge=Ridge(alpha=alpha).fit(prep.transform(train,True),train[target+'__future'])
                tree=DecisionTreeRegressor(max_depth=MAX_DEPTH,min_samples_leaf=MIN_LEAF,random_state=SEED).fit(prep.transform(train),train[target+'__future'])
                preds += [(spec,'ridge',ridge.predict(prep.transform(test,True)),alpha),
                          (spec,'tree',tree.predict(prep.transform(test)),np.nan)]
                for c in prep.numeric:
                    preprocessing_rows.append(dict(target=target,history=history,test_year=int(year),spec=spec,
                        feature=c,training_missing=int(train[c].isna().sum()),test_missing=int(test[c].isna().sum()),
                        training_median=float(prep.medians[c]) if c in prep.active else np.nan,
                        value_withheld_all_training_missing=c not in prep.active,missing_indicator_retained=True))
                for j,c in enumerate(prep.names):
                    coefficient_rows.append(dict(target=target,history=history,test_year=int(year),spec=spec,feature=c,
                        ridge_alpha=alpha,tuning_mode=tuning,coefficient_per_training_sd=float(ridge.coef_[j]),
                        training_mean=float(prep.mean[j]),training_sd=float(prep.scale[j])))
                for j in sorted(set(tree.tree_.feature)-{-2}):
                    split_rows.append(dict(target=target,history=history,test_year=int(year),spec=spec,
                        feature=prep.names[j],disaster_feature=prep.names[j].startswith(('fesm_','bushfire_','flood_'))))
                if history=='long':latest_trees[(target,spec)]=(int(year),prep,tree)
            for spec,model,pred,alpha in preds:
                score_rows.append(dict(target=target,history=history,test_year=int(year),test_fy=fy(year),spec=spec,model=model,
                    n=len(test),train_n=len(train),ridge_alpha=alpha,**metric(truth,pred)))
                for i,(_,r) in enumerate(test.iterrows()):
                    prediction_rows.append(dict(target=target,history=history,test_year=int(year),prior_year=int(r.prior_year),
                        event_year=int(r.event_year),council_key=r.council_key,spec=spec,model=model,observed=truth[i],
                        predicted=float(pred[i]),prior_value=float(r[target+'__prior']),
                        prior_operating_regime=r.operating_definition_regime__prior,
                        target_operating_regime=r.operating_definition_regime__future))
folds=pd.DataFrame(fold_rows);scores=pd.DataFrame(score_rows);predictions=pd.DataFrame(prediction_rows)
for frame,name in [(folds,'fold_samples_and_exclusions'),(scores,'year_by_year_metrics'),(predictions,'held_out_predictions'),
                   (pd.DataFrame(preprocessing_rows),'fold_preprocessing_audit'),(pd.DataFrame(inner_rows),'inner_forward_folds'),
                   (pd.DataFrame(tuning_rows),'ridge_tuning_audit'),(pd.DataFrame(coefficient_rows),'ridge_coefficients'),
                   (pd.DataFrame(split_rows),'tree_split_variables')]:frame.to_csv(OUT/(name+'.csv'),index=False)
assert scores.groupby(['target','history','test_year']).n.nunique().eq(1).all()
assert not predictions.duplicated(['target','history','test_year','council_key','spec','model']).any()
assert folds.train_candidate_n.eq(folds.train_n+folds.train_excluded_n).all()
assert folds.test_candidate_n.eq(folds.test_n+folds.test_excluded_n).all()
display(folds[(folds.history=='long') & (folds.status=='evaluated')][['target','test_fy','train_n','test_n','train_excluded_n','test_excluded_n']])

# %% [markdown]
# ## 6. Pooled errors, equal-year averages and wins against persistence
# MAE and RMSE retain each target's natural units. Out-of-sample R² uses the observed held-out
# mean in its denominator, as usual; negative values are retained. Pooled R² and mean yearly R²
# differ and are labelled separately. A lower MAE with a higher RMSE is a trade-off, not an
# unqualified improvement. Consistency requires both errors to improve in at least 75% of years.

# %%
pooled=pd.DataFrame([dict(target=t,history=h,spec=s,model=m,n=len(g),**metric(g.observed,g.predicted))
    for (t,h,s,m),g in predictions.groupby(['target','history','spec','model'])])
macro=scores.groupby(['target','history','spec','model']).agg(folds=('test_year','nunique'),
    macro_MAE=('MAE','mean'),macro_RMSE=('RMSE','mean'),macro_R2=('R2','mean')).reset_index()
summary=pooled.merge(macro,on=['target','history','spec','model'],validate='one_to_one')
base=scores[scores.model.eq('persistence')][['target','history','test_year','MAE','RMSE','R2']].rename(columns={c:'persistence_'+c for c in ['MAE','RMSE','R2']})
annual=scores.merge(base,on=['target','history','test_year'],validate='many_to_one')
for m in ['MAE','RMSE']:
    annual[m+'_improvement_vs_persistence']=annual['persistence_'+m]-annual[m]
    annual[m+'_improvement_pct_vs_persistence']=100*annual[m+'_improvement_vs_persistence']/annual['persistence_'+m]
annual['wins_both_errors']=annual.MAE_improvement_vs_persistence.gt(1e-12)&annual.RMSE_improvement_vs_persistence.gt(1e-12)
wins=annual.groupby(['target','history','spec','model']).agg(MAE_years_won=('MAE_improvement_vs_persistence',lambda x:int((x>1e-12).sum())),
    RMSE_years_won=('RMSE_improvement_vs_persistence',lambda x:int((x>1e-12).sum())),both_years_won=('wins_both_errors','sum')).reset_index()
summary=summary.merge(wins,on=['target','history','spec','model'])
pbase=summary[summary.model.eq('persistence')][['target','history','MAE','RMSE']].rename(columns={'MAE':'persistence_MAE','RMSE':'persistence_RMSE'})
summary=summary.merge(pbase,on=['target','history'],validate='many_to_one')
summary['consistent_vs_persistence']=(summary.MAE<summary.persistence_MAE)&(summary.RMSE<summary.persistence_RMSE)&(summary.both_years_won>=np.ceil(.75*summary.folds))
wide=scores.pivot(index=['target','history','test_year'],columns=['spec','model'],values=['MAE','RMSE','R2'])
wide.columns=['__'.join(c) for c in wide.columns]
folds.merge(wide.reset_index(),on=['target','history','test_year'],how='left').to_csv(OUT/'year_by_year_validation_wide.csv',index=False)
summary.to_csv(OUT/'pooled_and_equal_year_summary.csv',index=False);annual.to_csv(OUT/'annual_persistence_comparison.csv',index=False)
for target in TARGETS:
    display(Markdown(f'### {target} — {TARGETS[target]}'))
    display(summary[(summary.target==target)&(summary.history=='long')][['spec','model','n','MAE','RMSE','R2','folds','MAE_years_won','both_years_won','consistent_vs_persistence']].round(3))

# %% [markdown]
# ## 7. Does disaster information help, and does longer history help?
# Compare each ablation on identical rows, within the same learner. The fire-only step avoids
# attributing changes caused by declaration-record availability to physical fire information.
# Longer-history effects are assessed on the short-history model's exact held-out council-years.

# %%
a=[]
for (target,history,year,model),g in scores[scores.model.isin(['ridge','tree'])].groupby(['target','history','test_year','model']):
    g=g.set_index('spec')
    for aug,reference in [('fiscal_plus_fire','fiscal_only'),('fiscal_plus_disaster','fiscal_only'),('fiscal_plus_disaster','fiscal_plus_fire')]:
        a.append(dict(target=target,history=history,test_year=int(year),model=model,augmented=aug,reference=reference,n=int(g.loc[aug,'n']),
            **{m+'_improvement':float(g.loc[reference,m]-g.loc[aug,m]) for m in ['MAE','RMSE']},
            R2_improvement=float(g.loc[aug,'R2']-g.loc[reference,'R2'])))
ablation=pd.DataFrame(a);ablation.to_csv(OUT/'year_by_year_ablation.csv',index=False)
absum=ablation.groupby(['target','history','model','augmented','reference']).agg(folds=('test_year','size'),
    MAE_years_improved=('MAE_improvement',lambda x:int((x>1e-12).sum())),mean_annual_MAE_improvement=('MAE_improvement','mean'),
    RMSE_years_improved=('RMSE_improvement',lambda x:int((x>1e-12).sum())),mean_annual_RMSE_improvement=('RMSE_improvement','mean')).reset_index()
absum.to_csv(OUT/'ablation_summary.csv',index=False)
common=predictions[predictions.history=='long'].merge(predictions[predictions.history=='short_2017_onward'],
    on=['target','test_year','council_key','spec','model'],suffixes=('_long','_short'),validate='one_to_one')
assert np.array_equal(common.observed_long,common.observed_short)
histcomp=[]
for (t,s,m),g in common.groupby(['target','spec','model']):
    for period,hist in [('all_common_years',g)]+[(str(y),z) for y,z in g.groupby('test_year')]:
        lm=metric(hist.observed_long,hist.predicted_long);sm=metric(hist.observed_short,hist.predicted_short)
        histcomp.append(dict(target=t,spec=s,model=m,period=period,n=len(hist),years=hist.test_year.nunique(),
            **{'long_'+k:v for k,v in lm.items()},**{'short_'+k:v for k,v in sm.items()},
            MAE_improvement_with_longer_history=sm['MAE']-lm['MAE'],RMSE_improvement_with_longer_history=sm['RMSE']-lm['RMSE']))
history_comparison=pd.DataFrame(histcomp);history_comparison.to_csv(OUT/'matched_history_comparison.csv',index=False)
display(absum[(absum.history=='long')&(absum.augmented=='fiscal_plus_disaster')&(absum.reference=='fiscal_only')].round(3))
display(history_comparison[(history_comparison.target=='operating_ratio_pct')&(history_comparison.period=='all_common_years')].round(3))

# %% [markdown]
# ## 8. Annual performance figures
# Positive error reduction means better than persistence. Every eligible held-out year is shown;
# none is omitted for poor performance. Fiscal-only and fiscal-plus-disaster use the same rows.

# %%
COLORS={'ridge':'#2563a6','tree':'#bc6425'}
for target in TARGETS:
    fig,axes=plt.subplots(1,2,figsize=(12.5,4.5),sharex=True)
    g=annual[(annual.target==target)&(annual.history=='long')]
    for ax,measure in zip(axes,['MAE','RMSE']):
        for model in ['ridge','tree']:
            for spec,style,marker in [('fiscal_only','--','o'),('fiscal_plus_disaster','-','s')]:
                q=g[(g.model==model)&(g.spec==spec)].sort_values('test_year')
                ax.plot(q.test_year,q[measure+'_improvement_pct_vs_persistence'],color=COLORS[model],ls=style,marker=marker,
                        label=f'{model.title()} — '+('fiscal only' if spec=='fiscal_only' else '+ disaster'),lw=1.6,markersize=4)
        ax.axhline(0,color='#555555',lw=1);ax.set_title(measure+' reduction versus persistence');ax.set_ylabel('Error reduction (%)')
        years=sorted(g.test_year.unique());ax.set_xticks(years,[str(y)+'\n'+str(y+1)[-2:] for y in years]);ax.set_xlabel('Held-out financial year');ax.grid(axis='y',alpha=.18)
    fig.suptitle(target.replace('_',' ')+' | retrospective expanding-year validation',fontsize=13)
    axes[0].legend(fontsize=8,loc='best');fig.tight_layout();fig.savefig(OUT/f'{target}_annual_skill.png',bbox_inches='tight');plt.show();plt.close(fig)

# %% [markdown]
# ## 9. Latest shallow tree: inspect the actual splits
# The plots and node table describe the latest held-out fiscal-plus-disaster fold for each target.
# A split identifies a predictive partition in training data, not a causal disaster effect.
# Thresholds use original units; missing fiscal values have the audited training median.

# %%
for (target,spec),(year,prep,tree) in latest_trees.items():
    if spec!='fiscal_plus_disaster':continue
    tr=tree.tree_
    def walk(node,depth=0,path='all training rows'):
        leaf=tr.children_left[node]==tr.children_right[node];name='' if leaf else prep.names[tr.feature[node]]
        threshold=np.nan if leaf else float(tr.threshold[node])
        node_rows.append(dict(target=target,spec=spec,test_year=year,node=int(node),depth=depth,is_leaf=bool(leaf),split_variable=name,
            threshold=threshold,training_n=int(tr.n_node_samples[node]),prediction=float(tr.value[node].ravel()[0]),path=path))
        if not leaf:
            walk(tr.children_left[node],depth+1,path+f'; {name} <= {threshold:.6g}')
            walk(tr.children_right[node],depth+1,path+f'; {name} > {threshold:.6g}')
    walk(0)
    names=[s.replace('__prior',' (t-1)').replace('__event',' (t)').replace('__',' ').replace('_',' ') for s in prep.names]
    fig,ax=plt.subplots(figsize=(20,8.5));plot_tree(tree,feature_names=names,filled=False,rounded=True,precision=2,fontsize=9,ax=ax)
    ax.set_title(f'{target}: latest held-out {fy(year)} | depth ≤3, minimum leaf 20',fontsize=14)
    fig.tight_layout();fig.savefig(OUT/f'{target}_latest_tree.png',bbox_inches='tight');plt.show();plt.close(fig)
nodes=pd.DataFrame(node_rows);nodes.to_csv(OUT/'latest_tree_nodes.csv',index=False)
display(nodes[(nodes.target=='operating_ratio_pct')][['node','split_variable','threshold','training_n','prediction','is_leaf']].round(3))

# %% [markdown]
# ## 10. Evidence-based interpretation
# Consistency is assessed per model, not by selecting the best model separately in each test year.
# Many council-years share councils and disaster events; eight yearly folds are not eight hundred
# independent temporal replications. No claim about unseen councils or causality is made.

# %%
report=['# V2 retrospective forecasting results','',
    '**Primary answer: the longer matched history does not produce a consistent win over persistence for operating performance.** Maintenance is a secondary exception versus persistence, but its training-mean baseline remains better on MAE. Cash-cover gains are mixed.',
    '', 'Eight primary target years (2016–17 through 2023–24) are evaluated, with 818 held-out council-years per configuration. Cash has seven years; maintenance has nine. All conclusions are retrospective out-of-time, not real-time or causal.', '']
for target in TARGETS:
    s=summary[(summary.target==target)&(summary.history=='long')];persist=s[s.model=='persistence'].iloc[0]
    report += [f"## {'Primary' if target=='operating_ratio_pct' else 'Secondary'}: {target}",
        f"{int(persist.folds)} held-out years; {int(persist.n)} council-year predictions per configuration. Units: {TARGETS[target]}.",
        '', '| Specification | Model | MAE | RMSE | Pooled R² | MAE wins | Both-error wins |',
        '|---|---|---:|---:|---:|---:|---:|']
    for r in s.itertuples():report.append(f'| {r.spec} | {r.model} | {r.MAE:.3f} | {r.RMSE:.3f} | {r.R2:.3f} | {r.MAE_years_won}/{r.folds} | {r.both_years_won}/{r.folds} |')
    winners=s[s.consistent_vs_persistence & s.model.isin(['ridge','tree'])]
    report += ['',('Consistency rule met by: '+', '.join(winners.spec+' / '+winners.model)+'.') if len(winners) else 'No ridge/tree specification met the predeclared consistency rule against persistence.']
    for model in ['ridge','tree']:
        q=absum[(absum.target==target)&(absum.history=='long')&(absum.model==model)&(absum.augmented=='fiscal_plus_disaster')&(absum.reference=='fiscal_only')].iloc[0]
        report.append(f"Adding disaster fields to {model} reduced MAE in {q.MAE_years_improved}/{q.folds} years; mean annual MAE reduction {q.mean_annual_MAE_improvement:.3f} (negative means worse).")
    report += ['']
primary=summary[(summary.target=='operating_ratio_pct')&(summary.history=='long')&summary.model.isin(['ridge','tree'])]
consistent=primary[primary.consistent_vs_persistence]
# Verdict is about further investigation, never deployment; no secondary result rescues the primary.
verdict='GO for further retrospective validation' if len(consistent) else ('CONDITIONAL GO for limited validation' if ((primary.MAE<primary.persistence_MAE)&(primary.MAE_years_won>=np.ceil(primary.folds/2))).any() else 'NO-GO for escalating model complexity on this evidence')
report += [f'## Overall verdict: {verdict}',
    'The criterion is lower pooled MAE and RMSE and wins on both errors in at least 75% of future-year folds. It is a transparent practical rule, not a statistical significance test.',
    '', '## Did longer history help on the same later years?',
    '| Specification | Model | Matched rows | Long MAE | Short MAE | Long RMSE | Short RMSE |',
    '|---|---|---:|---:|---:|---:|---:|']
for r in history_comparison[(history_comparison.target=='operating_ratio_pct')&(history_comparison.period=='all_common_years')].itertuples():
    report.append(f'| {r.spec} | {r.model} | {r.n} | {r.long_MAE:.3f} | {r.short_MAE:.3f} | {r.long_RMSE:.3f} | {r.short_RMSE:.3f} |')
report += ['', 'Longer history reduced operating-ratio fiscal-only ridge MAE from 6.978 to 6.655 on the same 307 later rows. Persistence on those rows is 6.720. That small recent-period edge does not survive as a consistent advantage over the full eight-year evaluation; it must not replace the full-history result.',
    '', '## What did the trees actually use?',
    'Across all long-history folds, the only disaster-related tree split was the **bushfire declaration unknown indicator**, in four operating-ratio folds. No tree split used mapped burned hectares or known bushfire/flood event presence. Cash and maintenance tree predictions are unchanged by adding disaster fields. The apparent operating-tree disaster gain is therefore a reporting-availability partition, not evidence of a physical disaster effect.',
    '', 'The latest operating tree uses prior operating ratio, prior maintenance ratio, population and the bushfire-unknown flag. Cash uses prior cash cover and own-source revenue. Maintenance uses prior maintenance, population, current ratio and cash cover. See the complete split/node tables for thresholds, sample sizes and predictions.',
    '', 'This control uses V2 for both histories, the same 103 councils and exactly matched test rows. It isolates the training-window difference within this specification, rather than comparing different cohorts or old published scores.',
    '', '## Boundaries on interpretation',
    '- Current-vintage retrospective prediction only: historical fire products and later declaration revisions were not available in their present form at historical forecast dates.',
    '- Accounting standards, early operating-ratio adjustments, FESM sensors/thresholds and source geometry change over time. The maintenance denominator remains council-assessed; arithmetic comparability is not engineering invariance.',
    '- Unknown declarations remain explicit categories. Any gain may partly reflect reporting coverage; the fire-only ablation and complete annual results are provided. No physical flood-intensity series was available.',
    '- Cash 2012 is withheld. Flagged maintenance conflicts and debt-service denominator cases are withheld. No extreme outcomes are removed solely because they make prediction difficult.',
    '- Operating/cash 2024–25 targets are missing and not scored; maintenance may extend one further year. All skipped folds, rows and reasons are retained.',
    '- Repeated councils, common macroeconomic shocks and shared disasters limit effective independent temporal evidence. Neither split use nor ridge coefficients establish causality.',
    '- Earlier years of this project were already explored; these are retrospective validation results, not a newly sealed prospective test set.',
    '', '## Files and reproduction',
    'Open `../experiment.ipynb` in the Experiment 2 folder. Outputs include the merged evidence table, aligned predictor/target table, row exclusions, every fold, tuning/preprocessing audits, held-out predictions, ablations, matched-history comparison and tree nodes. Run the notebook from the AUSSEF directory or any folder beneath it; the companion script also locates its repository from its own path. No Random Forest, XGBoost, neural network, random split or test-year hyperparameter selection is used.']
(OUT/'README.md').write_text('\n'.join(report)+'\n')
display(Markdown('\n'.join(report)))

# %% [markdown]
# ## 11. Final validation and input preservation
# The checks below cover temporal order, equal scoring cohorts, source preservation and metric
# arithmetic. Saved held-out predictions allow independent recalculation without refitting.

# %%
for key,g in predictions.groupby(['target','history','test_year']):
    rowsets=g.groupby(['spec','model']).council_key.apply(lambda x:tuple(sorted(x)))
    assert rowsets.nunique()==1
assert folds.loc[folds.status.eq('evaluated'),'train_target_max'].lt(folds.loc[folds.status.eq('evaluated'),'test_year']-1).all()
if inner_rows:
    inner=pd.DataFrame(inner_rows);assert inner.train_target_max.lt(inner.validation_event_year).all()
assert all(not c.endswith('__future') for c in NUMERIC+[FIRE]+DECLARATIONS)
assert merged[['bushfire_declared','flood_declared']].isna().sum().equals(exposure[['bushfire_declared','flood_declared']].isna().sum())
changed=[p for p,h in frozen.items() if digest(ROOT/p)!=h];assert not changed,changed
checks=dict(merged_rows=len(merged),councils=len(keys),one_to_one_join=True,source_files_unchanged=len(frozen),
    changed_files=changed,outer_and_inner_forward_only=True,original_one_year_embargo_retained=True,
    identical_test_rows_across_models_and_ablations=True,unknown_exposure_preserved=True,
    complete_case_target_and_persistence=True,negative_R2_count=int(scores.R2.lt(0).sum()),
    no_models_beyond_mean_persistence_ridge_shallow_tree=True,model_rows=len(predictions))
(OUT/'preserved_inputs_sha256.json').write_text(json.dumps(frozen,indent=2))
(OUT/'validation_checks.json').write_text(json.dumps(checks,indent=2))
manifest=dict(inputs={str(p.relative_to(ROOT)):digest(p) for p in [FISCAL,EXPOSURE,ROOT/'NSW Data Panel.csv']},
    specification=CONFIG,python=platform.python_version(),pandas=pd.__version__,numpy=np.__version__,sklearn=sklearn.__version__,
    verdict=verdict,primary_consistent_specifications=consistent[['spec','model']].to_dict('records'))
(OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(checks,indent=2))
