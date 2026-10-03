"""Experiment 14 (Y v4, post-v3) models, copied from Experiment 9 run_models.py with only the target list changed: RF + baselines, leave-one-fire-season-out and council-grouped CV, metrics with council
cluster bootstrap, permutation importance on held-out folds, shuffled-Y check. Rules: PRESPEC.md (LOCK.txt).

Run: python3 run_models.py [--skip-shuffle]     (after data.py)
"""
import json
import sys
import time
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from data import CFG, OUT

warnings.filterwarnings('ignore')
SEED = CFG['meta']['seed']
V = CFG['validation']
XSETS = {'PRE': CFG['x']['pre'], 'PRE+FIRE': CFG['x']['pre'] + CFG['x']['fire']}
MAIN_TARGETS = ['Y_v4', 'DL', 'IL', 'FP', 'SL']
SENS_TARGETS = ['Y_v4_mag', 'Y_v4_H0', 'Y_v4_H12', 'Y_v4_H3', 'Y_v4_olg', 'Y_v4_resident_deaths']


def rf(seed=SEED):
    c = CFG['rf']
    return make_pipeline(SimpleImputer(strategy='median'),
                         RandomForestRegressor(n_estimators=c['n_estimators'], max_features=c['max_features'],
                                               min_samples_leaf=c['min_samples_leaf'], random_state=seed, n_jobs=-1))


def ridge():
    return make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), RidgeCV(alphas=CFG['ridge']['alphas']))


def folds(d, scheme):
    if scheme == 'season':
        return [(np.where(d.season != s)[0], np.where(d.season == s)[0]) for s in sorted(d.season.unique())]
    g = GroupKFold(n_splits=V['council_folds'], shuffle=True, random_state=SEED)
    return list(g.split(d, groups=d.region_id))


def poisson_pred(tr, te):
    """Experiment 7 M1: homes ~ log share + E2, offset log dwellings; rate mapped to 0-1 by the training ECDF."""
    cols = ['log_share', 'E2']
    tr = tr.dropna(subset=['homes_v2'])
    res = sm.GLM(tr.homes_v2, sm.add_constant(tr[cols]), family=sm.families.Poisson(),
                 offset=np.log(tr.dwellings)).fit()
    rate_te = np.exp(sm.add_constant(te[cols], has_constant='add').to_numpy() @ res.params.to_numpy()) * 1000
    rate_tr = tr.homes_v2 / tr.dwellings * 1000
    r = np.sort(rate_tr.to_numpy())
    lo, hi = np.searchsorted(r, rate_te, 'left'), np.searchsorted(r, rate_te, 'right')
    return (lo + 0.5 * (hi - lo)) / len(r)


def cv_run(d, target, xcols, scheme, keep_models=False, models=('mean', 'ridge', 'size_line', 'rf', 'poisson')):
    y = d[target].to_numpy()
    X = d[xcols]
    P = {k: np.full(len(d), np.nan) for k in models}
    kept = []
    for tr, te in folds(d, scheme):
        if 'mean' in P:
            P['mean'][te] = y[tr].mean()
        if 'ridge' in P:
            P['ridge'][te] = ridge().fit(X.iloc[tr], y[tr]).predict(X.iloc[te])
        if 'size_line' in P:
            P['size_line'][te] = LinearRegression().fit(d[['log_share']].iloc[tr], y[tr]).predict(d[['log_share']].iloc[te])
        if 'rf' in P:
            m = rf().fit(X.iloc[tr], y[tr])
            P['rf'][te] = m.predict(X.iloc[te])
            if keep_models:
                kept.append((m, te))
        if 'poisson' in P:
            P['poisson'][te] = poisson_pred(d.iloc[tr], d.iloc[te])
    return P, kept


def clusters(d):
    return [np.where(d.region_id.to_numpy() == r)[0] for r in d.region_id.unique()]


def metrics(d, target, P, rng):
    y = d[target].to_numpy()
    gs = clusters(d)
    names = list(P)
    boot = {k: [] for k in [f'rho_{n}' for n in names] + [f'mae_{n}' for n in names] + [f'dmae_rf_{n}' for n in names if n != 'rf']}
    for _ in range(V['n_boot']):
        idx = np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))])
        mae = {n: np.mean(np.abs(P[n][idx] - y[idx])) for n in names}
        for n in names:
            boot[f'rho_{n}'].append(spearmanr(P[n][idx], y[idx])[0])
            boot[f'mae_{n}'].append(mae[n])
            if n != 'rf':
                boot[f'dmae_rf_{n}'].append(mae['rf'] - mae[n])
    rows = []
    for n in names:
        rho = spearmanr(P[n], y)[0]
        mae = float(np.mean(np.abs(P[n] - y)))
        r = dict(model=n, n=len(y), councils=d.region_id.nunique(), seasons=d.season.nunique(), rho=rho,
                 rho_lo=np.nanpercentile(boot[f'rho_{n}'], 2.5), rho_hi=np.nanpercentile(boot[f'rho_{n}'], 97.5),
                 mae=mae, mae_lo=np.percentile(boot[f'mae_{n}'], 2.5), mae_hi=np.percentile(boot[f'mae_{n}'], 97.5))
        if n != 'rf':
            dm = float(np.mean(np.abs(P['rf'] - y))) - mae
            lo, hi = np.percentile(boot[f'dmae_rf_{n}'], [2.5, 97.5])
            r.update(rf_minus_this_mae=dm, rf_minus_this_lo=lo, rf_minus_this_hi=hi, rf_beats_this=bool(hi < 0))
        rows.append(r)
    return rows


def perm_importance(d, target, xcols, kept, rng):
    y = d[target].to_numpy()
    X = d[xcols]
    base = np.full(len(d), np.nan)
    for m, te in kept:
        base[te] = m.predict(X.iloc[te])
    mae0 = np.mean(np.abs(base - y))
    rows = []
    R = V['perm_repeats']
    for c in xcols:
        p = np.full((R, len(d)), np.nan)
        for m, te in kept:                      # one predict call per fold: all repeats stacked
            Xt = pd.concat([X.iloc[te]] * R, ignore_index=True)
            Xt[c] = np.concatenate([rng.permutation(X[c].to_numpy()[te]) for _ in range(R)])
            p[:, te] = m.predict(Xt).reshape(R, len(te))
        inc = np.mean(np.abs(p - y), axis=1) - mae0
        rows.append(dict(feature=c, mae_increase=np.mean(inc), lo=np.percentile(inc, 2.5), hi=np.percentile(inc, 97.5),
                         base_mae=mae0))
    return rows


def shuffle_check(d, target, xcols, n, rng, real_rho):
    null = []
    for k in range(n):
        dd = d.copy()
        dd[target] = rng.permutation(dd[target].to_numpy())
        P, _ = cv_run(dd, target, xcols, 'season', models=('rf',))
        null.append(spearmanr(P['rf'], dd[target])[0])
    null = np.array(null)
    return dict(shuffles=n, real_rho=real_rho, null_mean=float(null.mean()), null_p95=float(np.percentile(null, 95)),
                p=float((1 + (null >= real_rho).sum()) / (1 + n))), null


def main(skip_shuffle=False):
    T = pd.read_csv(OUT / 'ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
    rng = np.random.default_rng(SEED)
    met, imp, oof, real = [], [], [], {}
    t0 = time.time()
    for target in MAIN_TARGETS + SENS_TARGETS:
        d = T.dropna(subset=[target]).reset_index(drop=True)
        for xs, xcols in XSETS.items():
            for scheme in ('season', 'council'):
                models = ('mean', 'ridge', 'size_line', 'rf') + (('poisson',) if target == 'DL' else ())
                P, kept = cv_run(d, target, xcols, scheme, keep_models=(scheme == 'season'), models=models)
                for r in metrics(d, target, P, rng):
                    met.append(dict(target=target, xset=xs, cv=scheme, **r))
                if scheme == 'season':
                    real[(target, xs)] = spearmanr(P['rf'], d[target])[0]
                    for r in perm_importance(d, target, xcols, kept, rng):
                        imp.append(dict(target=target, xset=xs, **r))
                    if target in MAIN_TARGETS:
                        o = d[['agrn', 'region_id', 'region_name', 'season', target]].rename(columns={target: 'actual'})
                        for n, p in P.items():
                            o[f'pred_{n}'] = p
                        oof.append(o.assign(target=target, xset=xs))
        print(f'{target} done {time.time() - t0:.0f}s', flush=True)
    pd.DataFrame(met).to_csv(OUT / 'METRICS.csv', index=False)
    pd.DataFrame(imp).to_csv(OUT / 'PERM_IMPORTANCE.csv', index=False)
    pd.concat(oof).to_csv(OUT / 'OOF_PREDICTIONS.csv', index=False)
    if skip_shuffle:
        return
    sh, nulls = [], {}
    jobs = [('Y_v4', 'PRE+FIRE', V['shuffle_main']), ('Y_v4', 'PRE', V['shuffle_main'])] + \
           [(p, 'PRE+FIRE', V['shuffle_pillar']) for p in ['DL', 'IL', 'FP', 'SL']]
    for target, xs, n in jobs:
        d = T.dropna(subset=[target]).reset_index(drop=True)
        r, null = shuffle_check(d, target, XSETS[xs], n, rng, real[(target, xs)])
        sh.append(dict(target=target, xset=xs, **r))
        nulls[f'{target}|{xs}'] = null.tolist()
        print(f'shuffle {target} {xs} p={r["p"]:.3f} {time.time() - t0:.0f}s', flush=True)
    pd.DataFrame(sh).to_csv(OUT / 'SHUFFLE_CHECK.csv', index=False)
    json.dump(nulls, open(OUT / 'SHUFFLE_NULLS.json', 'w'))


if __name__ == '__main__':
    main(skip_shuffle='--skip-shuffle' in sys.argv)
