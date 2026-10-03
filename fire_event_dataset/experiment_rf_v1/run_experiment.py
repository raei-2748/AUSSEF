"""Frozen RF benchmark. Run prepare.py first. No writes to external inputs."""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 20260928
OUT = ROOT / 'results'
SNAP = ROOT / 'snapshot'
RF_GRID = [{'min_samples_leaf': leaf, 'max_features': feat} for leaf in [3, 8, 15] for feat in [.33, .7]]
RIDGE_GRID = [{'alpha': a} for a in [.1, 1, 10, 100]]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def group_mae(y, pred, groups):
    return float(pd.Series(np.abs(np.asarray(y) - np.asarray(pred))).groupby(np.asarray(groups)).mean().mean())


def weights(groups):
    count = pd.Series(groups).value_counts()
    w = np.array([1 / count[g] for g in groups], dtype=float)
    return w / w.mean()


def mask_inputs(m, cb):
    """Availability rules depend on source metadata/time only, never target values."""
    candidates = cb.loc[cb.role_if_Y_sum == 'X', 'column'].tolist()
    x = m[candidates].copy()
    x = x.mask(x.eq('N/A'))
    start_year = pd.to_datetime(m.first_fire_start).dt.year
    vintage = pd.to_numeric(m.info_pop_census_year, errors='coerce')
    masks = []
    remove = []
    for c in candidates:
        bad = pd.Series(False, index=m.index)
        reason = ''
        if c in ['X_socio_grp_sa4_nominal_growth_pct', 'X_socio_grp_sa4_real_growth_pct']:
            remove.append(c)
            masks.append({'column': c, 'rule': 'excluded: full 2015-2021 reference growth window', 'masked_cells': int(x[c].notna().sum())})
            continue
        if ('census' in c or c.startswith('X_socio_ind_share_') or c in ['X_socio_SEIFA', 'X_socio_seifa_irsd', 'X_council_insurance_proxy_share']):
            bad |= vintage.gt(start_year) | vintage.isna()
            reason = 'Census reference year after fire start or vintage unavailable'
        if '_tra_' in c:
            bad |= start_year.lt(2018)
            reason = 'TRA 2014-2017 averages used only from 2018'
        if '_reds_' in c:
            bad |= start_year.lt(2021)
            reason = 'REDS 2020 reference used only from 2021'
        if c in ['X_socio_grp_sa4_proxy_aud_m', 'X_socio_grp_per_capita_sa4_aud']:
            fy_base = pd.to_numeric(m.info_grp_base_fy.astype(str).str[:4], errors='coerce')
            bad |= fy_base.add(1).gt(start_year) | fy_base.isna()
            reason = 'SA4 GRP reference financial year ends after fire start or vintage unavailable'
        masks.append({'column': c, 'rule': reason or 'eligible X; no special reference-year mask', 'masked_cells': int((bad & x[c].notna()).sum())})
        x.loc[bad, c] = np.nan
    return x.drop(columns=remove), pd.DataFrame(masks)


class PreparedModel:
    """Training-only schema selection, followed by a fitted sklearn pipeline."""
    def __init__(self, kind, params):
        self.kind, self.params = kind, params

    def fit(self, x, y, groups):
        self.numeric, self.categorical, self.audit = [], [], []
        accepted = []
        fingerprints = {}
        for c in x.columns:
            v = x[c]
            reason = 'retained'
            if v.notna().mean() < .5:
                reason = 'less than 50% observed in training'
            elif v.nunique() < 2:
                reason = 'constant or no data in training'
            else:
                fingerprint = tuple('<MISSING>' if pd.isna(a) else str(a) for a in v)
                if fingerprint in fingerprints:
                    reason = 'duplicate in training: ' + fingerprints[fingerprint]
                else:
                    fingerprints[fingerprint] = c
            num = pd.to_numeric(v, errors='coerce')
            numeric = num.notna().sum() == v.notna().sum()
            if reason == 'retained':
                accepted.append(c)
                (self.numeric if numeric else self.categorical).append(c)
            self.audit.append({'column': c, 'training_coverage': float(v.notna().mean()), 'training_unique': int(v.nunique()),
                               'kind': 'numeric' if numeric else 'categorical', 'decision': reason})
        self.columns = accepted
        assert len(accepted) > 0
        transformers = []
        if self.numeric:
            stages = [('impute', SimpleImputer(strategy='median'))]
            if self.kind == 'ridge':
                stages.append(('scale', StandardScaler()))
            transformers.append(('num', Pipeline(stages), self.numeric))
        if self.categorical:
            transformers.append(('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                                                  ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), self.categorical))
        prep = ColumnTransformer(transformers, remainder='drop')
        if self.kind == 'rf':
            estimator = RandomForestRegressor(n_estimators=500, criterion='squared_error', max_depth=None,
                                              bootstrap=True, random_state=SEED, n_jobs=1, **self.params)
        elif self.kind == 'ridge':
            estimator = Ridge(**self.params)
        else:
            raise ValueError(self.kind)
        self.pipeline = Pipeline([('prepare', prep), ('model', estimator)])
        self.pipeline.fit(self.coerce(x), y, model__sample_weight=weights(groups))
        return self

    def coerce(self, x):
        frame = x[self.columns].copy()
        for c in self.numeric:
            frame[c] = pd.to_numeric(frame[c], errors='coerce').astype(float)
        for c in self.categorical:
            frame[c] = frame[c].map(lambda a: np.nan if pd.isna(a) else str(a)).astype(object)
        return frame

    def predict(self, x):
        return np.clip(self.pipeline.predict(self.coerce(x)), 0, 1)


def constant_predictions(y, groups, n):
    w = weights(groups)
    mean = float(np.average(y, weights=w))
    order = np.argsort(y)
    yy, ww = np.asarray(y)[order], w[order]
    median = float(yy[np.searchsorted(np.cumsum(ww), .5 * ww.sum())])
    return {'mean': np.full(n, mean), 'median': np.full(n, median)}


def choose(kind, grid, x, y, groups, outer_name, tuning):
    splitter = GroupKFold(n_splits=min(4, len(np.unique(groups))))
    splits = list(splitter.split(x, y, groups))
    best, best_score = None, np.inf
    for params in grid:
        scores = []
        for inner, (tr, te) in enumerate(splits, 1):
            model = PreparedModel(kind, params).fit(x.iloc[tr], y[tr], groups[tr])
            score = group_mae(y[te], model.predict(x.iloc[te]), groups[te])
            scores.append(score)
            tuning.append({'outer': outer_name, 'model': kind, 'parameters': json.dumps(params, sort_keys=True), 'inner_fold': inner,
                           'group_mae': score, 'features': len(model.columns)})
        score = float(np.mean(scores))
        if score < best_score:
            best, best_score = params, score
    return PreparedModel(kind, best).fit(x, y, groups), best, best_score


def metric_rows(predictions, cuts):
    rows = []
    for split, d in predictions.groupby('split', sort=False):
        for name in ['mean', 'median', 'ridge', 'rf']:
            pred = d[f'pred_{name}'].to_numpy()
            cl = np.digitize(pred, cuts, right=False) + 1
            rows.append({'split': split, 'model': name, 'rows': len(d), 'groups': int(d.event_group.nunique()),
                         'group_mae': group_mae(d.Y, pred, d.event_group), 'row_mae': mean_absolute_error(d.Y, pred),
                         'rmse': np.sqrt(mean_squared_error(d.Y, pred)), 'r2': r2_score(d.Y, pred),
                         'class_accuracy': accuracy_score(d.Y_class_from_Y, cl),
                         'class_macro_f1': f1_score(d.Y_class_from_Y, cl, labels=[1,2,3,4], average='macro', zero_division=0),
                         'class_mae': mean_absolute_error(d.Y_class_from_Y, cl)})
    return pd.DataFrame(rows)


def uncertainty(d):
    errors = pd.DataFrame({'event_group': d.event_group})
    for model in ['mean', 'median', 'ridge', 'rf']:
        errors[model] = np.abs(d.Y.to_numpy() - d[f'pred_{model}'].to_numpy())
    ge = errors.groupby('event_group').mean()
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, len(ge), size=(2000, len(ge)))
    rows = []
    for baseline in ['mean', 'median', 'ridge']:
        delta = (ge[baseline] - ge.rf).to_numpy()
        boot = delta[draws].mean(axis=1)
        lo, hi = np.quantile(boot, [.025, .975])
        rows.append({'baseline': baseline, 'improvement_group_mae': float(delta.mean()), 'ci_low': float(lo),
                     'ci_high': float(hi), 'improvement_pct': float(delta.mean() / ge[baseline].mean() * 100), 'groups': len(ge)})
    return rows


def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'RUN_RECEIPT.json').exists(), 'V1 already complete: preserve results; do not overwrite.'
    audit = json.loads((ROOT / 'AUDIT.json').read_text())
    input_hash = audit['source_sha256']
    assert digest(SNAP / 'nsw_bushfires_2015_2025_XY.xlsx') == input_hash
    assert digest(Path(audit['source'])) == input_hash
    m = pd.read_csv(SNAP / 'master.csv', dtype={'agrn': str, 'region_id': str}, keep_default_na=True)
    cb = pd.read_csv(SNAP / 'codebook.csv').query("sheet == 'master'")
    x, masks = mask_inputs(m, cb)
    y, groups = m.Y.to_numpy(), m.event_group.to_numpy()
    cuts = audit['reference_y_class_cutoffs']
    g = m.groupby('event_group').fire_fy_start.agg(['min', 'max'])
    tr = np.flatnonzero(m.event_group.isin(g.index[g['max'] <= 2019]))
    te = np.flatnonzero(m.event_group.isin(g.index[g['min'] >= 2022]))
    assert len(tr) >= 30 and len(te) >= 20
    assert set(groups[tr]).isdisjoint(groups[te])
    folds = [('primary_recent_seasons', tr, te)]
    folds += [(f'group_cv_{i}', a, b) for i, (a,b) in enumerate(GroupKFold(5).split(x, y, groups),1)]
    split_rows = []
    for name, tr, te in folds:
        for role, ii in [('train',tr),('test',te)]:
            split_rows.extend({'split':name, 'role':role, 'row_id':m.row_id[i], 'event_group':groups[i]} for i in ii)
    assignments = pd.DataFrame(split_rows)
    assignments.to_csv(OUT / 'SPLIT_ASSIGNMENTS.csv', index=False)
    masks.to_csv(OUT / 'AVAILABILITY_RULES.csv', index=False)
    receipt = {'started_utc':datetime.now(timezone.utc).isoformat(), 'protocol_sha256':digest(ROOT / 'PROTOCOL.md'),
               'source_sha256':input_hash, 'runner_sha256':digest(Path(__file__)), 'split_sha256':digest(OUT / 'SPLIT_ASSIGNMENTS.csv'),
               'versions':{'python':sys.version,'sklearn':sklearn.__version__,'numpy':np.__version__,'pandas':pd.__version__,
                           'scipy':scipy.__version__,'matplotlib':matplotlib.__version__}, 'seed':SEED,
               'rf_grid':RF_GRID, 'ridge_grid':RIDGE_GRID}
    (OUT / 'PRE_FIT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Protocol and splits frozen. Primary rows/groups:', len(folds[0][1]),len(np.unique(groups[folds[0][1]])),
          len(folds[0][2]),len(np.unique(groups[folds[0][2]])),flush=True)
    predictions, features, tuning, selections = [], [], [], []
    primary_model = None
    for name, tr, te in folds:
        print('Fitting',name,flush=True)
        p = m.iloc[te][['row_id','agrn','region_id','region_name','first_fire_start','event_group','Y','Y_norm',
                            'Y_class_from_Y','Y_class','Y_pillars_n','fire_fy_start']].copy()
        p['split'] = name
        cp = constant_predictions(y[tr], groups[tr], len(te))
        for k,v in cp.items(): p[f'pred_{k}'] = v
        for kind, grid in [('ridge',RIDGE_GRID),('rf',RF_GRID)]:
            model, params, val = choose(kind,grid,x.iloc[tr].reset_index(drop=True),y[tr],groups[tr],name,tuning)
            p[f'pred_{kind}'] = model.predict(x.iloc[te])
            p[f'pred_class_{kind}'] = np.digitize(p[f'pred_{kind}'], cuts, right=False)+1
            features.extend({'split':name,'model':kind,**r} for r in model.audit)
            selections.append({'split':name,'model':kind,'parameters':json.dumps(params),'inner_group_mae':val,'retained_features':len(model.columns)})
            if name == 'primary_recent_seasons' and kind == 'rf':
                primary_model = model
                joblib.dump({'model':model,'class_cutoffs':cuts,'source_sha256':input_hash,'training_row_ids':m.row_id.iloc[tr].tolist(),
                             'status':'experimental primary-holdout model; not a deployment'}, OUT / 'PRIMARY_RF_MODEL.joblib')
        predictions.append(p)
        print(name,'finished',flush=True)
    pred = pd.concat(predictions,ignore_index=True)
    cv = pred[pred.split.str.startswith('group_cv_')].copy()
    pooled_cv = cv.copy(); pooled_cv['split']='group_cv_pooled'
    pred.to_csv(OUT / 'HELD_OUT_PREDICTIONS.csv',index=False)
    metrics = metric_rows(pd.concat([pred,pooled_cv],ignore_index=True),cuts)
    metrics.to_csv(OUT / 'MODEL_RESULTS.csv',index=False)
    pd.DataFrame(features).to_csv(OUT / 'FEATURE_DECISIONS.csv',index=False)
    pd.DataFrame(tuning).to_csv(OUT / 'INNER_TUNING.csv',index=False)
    pd.DataFrame(selections).to_csv(OUT / 'SELECTED_MODELS.csv',index=False)
    ci=[]
    primary = pred[pred.split=='primary_recent_seasons'].copy()
    for name,d in [('primary_recent_seasons',primary),('group_cv_pooled',cv)]:
        ci.extend({'split':name,**r} for r in uncertainty(d))
    ci = pd.DataFrame(ci)
    ci.to_csv(OUT / 'PAIRED_GROUP_BOOTSTRAP.csv',index=False)
    robust=[]
    for name,d in [('primary_recent_seasons',primary),('group_cv_pooled',cv)]:
        for pillars,subset in d.groupby('Y_pillars_n'):
            met=metric_rows(subset,cuts);met['sensitivity']=f'{int(pillars)}_pillars'
            robust.append(met)
    known_councils=set(m.region_id.iloc[folds[0][1]])
    for seen in [True,False]:
        subset=primary[primary.region_id.isin(known_councils)==seen]
        if len(subset)>=2:
            met=metric_rows(subset,cuts);met['sensitivity']='seen_council' if seen else 'unseen_council';robust.append(met)
    pd.concat(robust,ignore_index=True).to_csv(OUT / 'ROBUSTNESS_RESULTS.csv',index=False)
    # Descriptive permutation importance on original feature columns. No tuning based on these results.
    rng=np.random.default_rng(SEED)
    test_x=x.iloc[folds[0][2]].copy()
    baseline=group_mae(primary.Y,primary.pred_rf,primary.event_group)
    imp=[]
    for col in primary_model.columns:
        effect=[]
        for repeat in range(10):
            altered=test_x.copy();altered[col]=rng.permutation(altered[col].to_numpy())
            effect.append(group_mae(primary.Y,primary_model.predict(altered),primary.event_group)-baseline)
        imp.append({'column':col,'group_mae_increase':float(np.mean(effect)),'repeat_sd':float(np.std(effect,ddof=1))})
    importance=pd.DataFrame(imp).sort_values('group_mae_increase',ascending=False)
    importance.to_csv(OUT / 'PERMUTATION_IMPORTANCE.csv',index=False)
    conf=[]
    for name,d in [('primary_recent_seasons',primary),('group_cv_pooled',cv)]:
        mat=confusion_matrix(d.Y_class_from_Y,d.pred_class_rf,labels=[1,2,3,4])
        for a in range(4):
            for b in range(4):conf.append({'split':name,'actual_class':a+1,'predicted_class':b+1,'rows':int(mat[a,b])})
    pd.DataFrame(conf).to_csv(OUT / 'CLASS_CONFUSION.csv',index=False)
    # Frozen decision rule, no further fitting or rescue.
    pci=ci[ci.split=='primary_recent_seasons']
    cvm=metrics[metrics.split=='group_cv_pooled'].set_index('model')
    passed=bool((pci.improvement_pct>=5).all() and (pci.ci_low>0).all() and all(cvm.loc['rf','group_mae']<cvm.loc[b,'group_mae'] for b in ['mean','median','ridge']))
    verdict='PREDICTIVE_GAIN_ESTABLISHED_FOR_FIXED_WORKBOOK_BENCHMARK' if passed else 'PREDICTIVE_GAIN_NOT_ESTABLISHED'
    summary={'verdict':verdict,'primary_rows':len(primary),'primary_groups':int(primary.event_group.nunique()),
             'cv_rows':len(cv),'cv_groups':int(cv.event_group.nunique()),'reference_class_cutoffs':cuts,
             'primary_metrics':metrics[metrics.split=='primary_recent_seasons'].to_dict('records'),
             'cv_metrics':metrics[metrics.split=='group_cv_pooled'].to_dict('records'), 'primary_bootstrap':pci.to_dict('records')}
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    plot(primary,cv,metrics,importance)
    assert digest(Path(audit['source']))==input_hash
    receipt.update({'finished_utc':datetime.now(timezone.utc).isoformat(),'verdict':verdict,
                    'source_unchanged':True,'protocol_unchanged':digest(ROOT / 'PROTOCOL.md')==receipt['protocol_sha256']})
    (OUT / 'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


def plot(primary,cv,metrics,importance):
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for ax,name,title in zip(axes,['primary_recent_seasons','group_cv_pooled'],['Recent seasons held out','All events: grouped cross-validation']):
        d=metrics[metrics.split==name].set_index('model').loc[['mean','median','ridge','rf']]
        bars=ax.bar(['Mean','Median','Ridge','Random forest'],d.group_mae,color=['#aaa','#aaa','#748ba2','#287b66'])
        ax.set_ylabel('MAE in Y units (equal weight per event group)');ax.set_title(title);ax.set_ylim(0,float(d.group_mae.max())*1.2)
        for b,v in zip(bars,d.group_mae):ax.text(b.get_x()+b.get_width()/2,v+.003,f'{v:.3f}',ha='center')
    fig.tight_layout();fig.savefig(OUT / 'model_comparison.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    for ax,d,title in zip(axes,[primary,cv],['Recent seasons held out','Grouped out-of-fold predictions']):
        sc=ax.scatter(d.Y,d.pred_rf,c=d.Y_pillars_n,cmap='viridis',vmin=2,vmax=4,alpha=.75,s=28)
        ax.plot([0,1],[0,1],color='#777',linestyle='--');ax.set(xlim=(0,1),ylim=(0,1),xlabel='Workbook Y',ylabel='Predicted Y',title=title)
    fig.colorbar(sc,ax=axes,label='Available pillars',ticks=[2,3,4],fraction=.025)
    fig.subplots_adjust(left=.07,right=.87,bottom=.15,wspace=.3);fig.savefig(OUT/'predicted_vs_actual.png',dpi=180);plt.close(fig)
    top=importance.head(12).iloc[::-1]
    fig,ax=plt.subplots(figsize=(10,5.7));ax.barh(top.column.str.replace('X_socio_','').str.replace('X_council_','').str.replace('X_fire_',''),top.group_mae_increase,color='#287b66')
    ax.axvline(0,color='#999');ax.set_xlabel('Increase in held-out group MAE after permutation');ax.set_title('Descriptive importance: recent-season holdout')
    fig.tight_layout();fig.savefig(OUT/'permutation_importance.png',dpi=180);plt.close(fig)


if __name__=='__main__':
    main()
