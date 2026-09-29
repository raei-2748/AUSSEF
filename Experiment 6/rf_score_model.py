"""Experiment 6, step 1: does a random forest on the pre-fire inputs beat the fixed equal-weight score?

Design fixed before running (see the plan in the report):
  Rows      218 council x fire rows (results/ROWS_WITH_SCORE_v2.csv), council items from results/COUNCIL_ITEMS_v2.csv.
  Features  A = the four block scores (H, E, V, F; exposure v2).
            B = 15 item-level inputs (BFPL cat1, cat12, forest, dwellings/residents in BFPL, log pop, SEIFA, income,
                unemployment, six fiscal ratios). Neither uses anything known only after ignition.
            'not pre-fire' reference models add the fire's burned share of the council (an upper bound).
  Targets   Y (primary); DL, IL, FP, SL (secondary).
  Split     5-fold GroupKFold by COUNCIL, repeated REPEATS times with different council-to-fold assignments;
            no council is ever in train and test at once (asserted). Inner grouped 3-fold CV picks the RF settings
            (min_samples_leaf 2/5/10 x max_features 0.33/0.7/1.0, as in Experiment 5).
  Compare   global training mean; the fixed equal-weight score (no fitting); V block alone; ridge on blocks; RF A; RF B.
  Metrics   Spearman(out-of-fold prediction minus that fold's training mean, target) [centred; raw pooled
            predictions gave a negative artifact even for shuffled Y, run 1 kept as *_uncentered_run1.csv] overall and on fires burning >= 5%, >= 2%, >= 5,000 ha; MAE;
            council-cluster bootstrap 95% CI; paired gain over the fixed score.
  Extras    train on >= 2% fires only vs all rows; train non-Black-Summer, test Black Summer (councils disjoint);
            permutation importance (B); shuffled-Y sanity check.

Run: python3 rf_score_model.py [REPEATS] [SEED]      (writes results/RF_*.csv, results/rf_importance.png)
"""
import sys
import time
import warnings
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
REPEATS = int(sys.argv[1]) if len(sys.argv) > 1 else 5
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20260930
TAG = '' if SEED == 20260930 else f'_seed{SEED}'
N_TREES = 200
N_BOOT = 1000
GRID = [dict(min_samples_leaf=l, max_features=f) for l in (2, 5, 10) for f in (0.33, 0.7, 1.0)]
BLOCKS = ['H', 'E', 'V', 'F']
ITEMS_B = ['bfpl_share_cat1', 'bfpl_share_cat12', 'nvis_forest_share', 'dwellings_in_bfpl12_share',
           'residents_in_bfpl12_share', 'log_pop', 'seifa_irsd', 'median_income_aud_fy', 'unemp_rate',
           'fiscal_cash_cover_months_fy', 'fiscal_own_source_pct_fy', 'fiscal_debt_service_ratio_pct_fy',
           'fiscal_operating_ratio_pct_fy', 'fiscal_infra_backlog_ratio_pct_fy',
           'fiscal_unrestricted_current_ratio_fy']
TARGETS = ['Y', 'DL', 'IL', 'FP', 'SL']
BLACK_SUMMER = '871'


def load():
    rows = pd.read_csv(OUT / 'ROWS_WITH_SCORE_v2.csv')
    items = pd.read_csv(OUT / 'COUNCIL_ITEMS_v2.csv')[['region_id'] + ITEMS_B]
    d = rows.merge(items, on='region_id', how='left', validate='m:1')
    d['agrn'] = d.agrn.astype(str)
    d['burn_share'] = d.share
    return d


def rf(params, seed):
    return make_pipeline(SimpleImputer(strategy='median'),
                         RandomForestRegressor(n_estimators=N_TREES, random_state=seed, n_jobs=-1, **params))


def tuned_rf(X, y, groups, seed):
    """Inner grouped 3-fold CV over GRID (MAE); returns a model fitted on all of X, y."""
    ug = np.unique(groups)
    r = np.random.default_rng(seed)
    fold_of = dict(zip(ug, r.permutation(len(ug)) % 3))
    f = np.array([fold_of[g] for g in groups])
    best, best_mae = None, np.inf
    for p in GRID:
        errs = []
        for k in range(3):
            tr, te = f != k, f == k
            if tr.sum() < 10 or te.sum() < 1:
                continue
            m = rf(p, seed).fit(X[tr], y[tr])
            errs.append(np.abs(m.predict(X[te]) - y[te]))
        mae = np.concatenate(errs).mean()
        if mae < best_mae:
            best, best_mae = p, mae
    return rf(best, seed).fit(X, y), best


def ridge(X, y):
    m = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                      RidgeCV(alphas=np.logspace(-2, 4, 25)))
    return m.fit(X, y)


def folds(councils, r):
    ug = np.unique(councils)
    rng = np.random.default_rng(SEED + 1000 * r)
    assign = dict(zip(ug, rng.permutation(len(ug)) % 5))
    return np.array([assign[c] for c in councils])


def run_cv(d, target, train_filter='all', with_importance=False):
    """Returns dict model -> mean out-of-fold prediction (over repeats), tuned settings, importance frame."""
    dd = d[d[target].notna()].reset_index(drop=True)
    y = dd[target].to_numpy(float)
    council = dd.region_id.to_numpy()
    XA, XB = dd[BLOCKS].to_numpy(float), dd[ITEMS_B].to_numpy(float)
    XAf = np.column_stack([XA, dd.burn_share.to_numpy(float)])
    XBf = np.column_stack([XB, dd.burn_share.to_numpy(float)])
    eligible = np.ones(len(dd), bool) if train_filter == 'all' else (dd.burn_share >= 0.02).to_numpy()
    names = ['global_mean', 'ridge_blocks', 'rf_A', 'rf_B', 'ridge_blocks+burn (not pre-fire)',
             'rf_B+burn (not pre-fire)']
    preds = {n: np.zeros((REPEATS, len(dd))) for n in names}
    trmean = np.zeros((REPEATS, len(dd)))          # training mean of the fold that predicted each row
    chosen, imps = [], []
    for r in range(REPEATS):
        f = folds(council, r)
        for k in range(5):
            te = f == k
            tr = (~te) & eligible
            assert not set(council[tr]) & set(council[te]), 'council in both train and test'
            if tr.sum() < 15:
                for n in names:
                    preds[n][r, te] = np.nan
                continue
            gtr = council[tr]
            trmean[r, te] = y[tr].mean()
            preds['global_mean'][r, te] = y[tr].mean()
            preds['ridge_blocks'][r, te] = ridge(XA[tr], y[tr]).predict(XA[te])
            preds['ridge_blocks+burn (not pre-fire)'][r, te] = ridge(XAf[tr], y[tr]).predict(XAf[te])
            mA, pA = tuned_rf(XA[tr], y[tr], gtr, SEED + r * 10 + k)
            mB, pB = tuned_rf(XB[tr], y[tr], gtr, SEED + r * 10 + k)
            mBf, _ = tuned_rf(XBf[tr], y[tr], gtr, SEED + r * 10 + k)
            preds['rf_A'][r, te] = mA.predict(XA[te])
            preds['rf_B'][r, te] = mB.predict(XB[te])
            preds['rf_B+burn (not pre-fire)'][r, te] = mBf.predict(XBf[te])
            chosen.append(dict(repeat=r, fold=k, A=str(pA), B=str(pB)))
            if with_importance and r == 0 and te.sum() > 5:
                pi = permutation_importance(mB, XB[te], y[te], n_repeats=10, random_state=SEED,
                                            scoring='neg_mean_absolute_error')
                imps.append(pd.DataFrame({'feature': ITEMS_B, 'mae_increase': pi.importances_mean, 'fold': k}))
    mean_pred = {n: np.nanmean(p, axis=0) for n, p in preds.items()}
    # centred = prediction minus that fold's training mean; removes the pooled-fold artifact (a fold whose held-out
    # rows have high Y has a LOW training mean, which makes raw pooled predictions anti-correlate with the truth)
    centred = {n: np.nanmean(p - trmean, axis=0) for n, p in preds.items() if n != 'global_mean'}
    mean_pred['_centred'] = centred
    imp = pd.concat(imps) if imps else None
    return dd, y, mean_pred, pd.DataFrame(chosen), imp


def spearman(a, b):
    m = ~(np.isnan(a) | np.isnan(b))
    if m.sum() < 6 or np.unique(a[m]).size < 3 or np.unique(b[m]).size < 3:
        return np.nan
    return np.corrcoef(rankdata(a[m]), rankdata(b[m]))[0, 1]


def cluster_boot(fn, clusters, rng, n=N_BOOT):
    """fn(idx) -> statistic; resample councils with replacement. Returns (lo, hi)."""
    keys, inv = np.unique(clusters, return_inverse=True)
    members = [np.flatnonzero(inv == k) for k in range(len(keys))]
    out = []
    for _ in range(n):
        pick = rng.integers(0, len(keys), len(keys))
        idx = np.concatenate([members[i] for i in pick])
        v = fn(idx)
        if not np.isnan(v):
            out.append(v)
    return (np.percentile(out, 2.5), np.percentile(out, 97.5)) if len(out) > 50 else (np.nan, np.nan)


def subsets(dd):
    return {'all rows': np.ones(len(dd), bool),
            'burned >= 2%': (dd.burn_share >= 0.02).to_numpy(),
            'burned >= 5%': (dd.burn_share >= 0.05).to_numpy(),
            'burned >= 5,000 ha': (dd.burn_ha >= 5000).to_numpy()}


def score_table(dd, y, mean_pred, target, rng, label):
    fixed = dd['risk_add'].to_numpy(float)
    centred = mean_pred['_centred']
    raw = {k: v for k, v in mean_pred.items() if k != '_centred'}
    models = {**{k: v for k, v in centred.items()}, 'global_mean': raw['global_mean']}
    models['fixed_score_risk_add'] = fixed
    models['V_block_alone'] = dd['V'].to_numpy(float)
    rows, gains = [], []
    for sname, mask in subsets(dd).items():
        if mask.sum() < 8:
            continue
        cl = dd.region_id.to_numpy()[mask]
        yy = y[mask]
        for mname, p in models.items():
            pp = p[mask]
            lo, hi = cluster_boot(lambda i: spearman(pp[i], yy[i]), cl, rng)
            mae = np.nan if mname in ('fixed_score_risk_add', 'V_block_alone') else float(np.nanmean(np.abs(raw[mname][mask] - yy)))
            rows.append(dict(setup=label, target=target, subset=sname, rows=int(mask.sum()), model=mname,
                             spearman=spearman(pp, yy), ci_low=lo, ci_high=hi, mae=mae))
        for mname in ['ridge_blocks', 'rf_A', 'rf_B']:
            pp, ff = models[mname][mask], fixed[mask]
            lo, hi = cluster_boot(lambda i: spearman(pp[i], yy[i]) - spearman(ff[i], yy[i]), cl, rng)
            gains.append(dict(setup=label, target=target, subset=sname, model=mname,
                              spearman_gain_over_fixed=spearman(pp, yy) - spearman(ff, yy), ci_low=lo, ci_high=hi))
    return rows, gains


def black_summer_holdout(d, rng):
    """Train on non-Black-Summer rows of councils that are NOT in Black Summer's rows; test on Black Summer."""
    bs = d.agrn == BLACK_SUMMER
    test = d[bs & d.Y.notna()]
    train = d[~bs & ~d.region_id.isin(test.region_id) & d.Y.notna()]
    y_tr, y_te = train.Y.to_numpy(float), test.Y.to_numpy(float)
    res = []
    cl = test.region_id.to_numpy()
    for fname, cols in [('A', BLOCKS), ('B', ITEMS_B)]:
        Xtr, Xte = train[cols].to_numpy(float), test[cols].to_numpy(float)
        m, params = tuned_rf(Xtr, y_tr, train.region_id.to_numpy(), SEED)
        preds = {'rf_' + fname: m.predict(Xte) - y_tr.mean()}          # centred on the training mean
        if fname == 'A':
            preds['ridge_blocks'] = ridge(Xtr, y_tr).predict(Xte) - y_tr.mean()
        for n, p in preds.items():
            lo, hi = cluster_boot(lambda i: spearman(p[i], y_te[i]), cl, rng)
            res.append(dict(model=n, train_rows=len(train), test_rows=len(test), spearman=spearman(p, y_te),
                            ci_low=lo, ci_high=hi, mae=float(np.abs(p + y_tr.mean() - y_te).mean())))
    f = test.risk_add.to_numpy(float)
    lo, hi = cluster_boot(lambda i: spearman(f[i], y_te[i]), cl, rng)
    res.append(dict(model='fixed_score_risk_add', train_rows=0, test_rows=len(test), spearman=spearman(f, y_te),
                    ci_low=lo, ci_high=hi, mae=np.nan))
    return pd.DataFrame(res)


def shuffled_sanity(d, n_shuffles=3):
    """Shuffle Y within Black Summer / start-year strata; a working pipeline should give Spearman near 0."""
    rng = np.random.default_rng(SEED + 7)
    dd = d[d.Y.notna()].reset_index(drop=True)
    stratum = np.where(dd.agrn == BLACK_SUMMER, 'BS', dd.year.astype(str))
    out = []
    for s in range(n_shuffles):
        sh = dd.copy()
        y = dd.Y.to_numpy(float).copy()
        for k in np.unique(stratum):
            idx = np.flatnonzero(stratum == k)
            y[idx] = dd.Y.to_numpy(float)[rng.permutation(idx)]
        sh['Y'] = y
        d2, y2, mp, _, _ = run_cv(sh, 'Y')
        c = mp['_centred']
        for m in ['rf_A', 'rf_B', 'ridge_blocks']:
            out.append(dict(shuffle=s, model=m, spearman_all_rows=spearman(c[m], y2),
                            spearman_burned_ge5=spearman(c[m][d2.burn_share >= 0.05], y2[d2.burn_share >= 0.05]),
                            raw_spearman_burned_ge5=spearman(mp[m][d2.burn_share >= 0.05], y2[d2.burn_share >= 0.05])))
    return pd.DataFrame(out)


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    d = load()
    print('rows', len(d), 'councils', d.region_id.nunique(), 'repeats', REPEATS, 'seed', SEED, flush=True)
    all_rows, all_gains, tuned, imps = [], [], [], []
    for target in TARGETS:
        dd, y, mp, chosen, imp = run_cv(d, target, 'all', with_importance=(target == 'Y'))
        r, g = score_table(dd, y, mp, target, rng, 'train on all rows')
        all_rows += r; all_gains += g
        chosen['target'] = target
        tuned.append(chosen)
        if imp is not None:
            imps.append(imp)
        print(target, 'done', round(time.time() - t0), 's', flush=True)
    pd.DataFrame(all_rows).to_csv(OUT / f'RF_MAIN{TAG}.csv', index=False)
    pd.DataFrame(all_gains).to_csv(OUT / f'RF_GAIN_OVER_FIXED{TAG}.csv', index=False)
    pd.concat(tuned).to_csv(OUT / f'RF_TUNED_SETTINGS{TAG}.csv', index=False)
    if TAG:
        return
    # ---- train on >= 2% fires only (Y)
    dd, y, mp, _, _ = run_cv(d, 'Y', 'ge2')
    r, g = score_table(dd, y, mp, 'Y', rng, 'train on fires >= 2% burned only')
    pd.DataFrame(r).to_csv(OUT / 'RF_TRAIN_ON_LARGE.csv', index=False)
    print('large-train done', round(time.time() - t0), 's', flush=True)
    # ---- Black Summer hold-out
    black_summer_holdout(d, rng).to_csv(OUT / 'RF_BLACK_SUMMER_HOLDOUT.csv', index=False)
    # ---- importance
    imp = pd.concat(imps).groupby('feature').mae_increase.agg(['mean', 'std']).sort_values('mean', ascending=False)
    imp.to_csv(OUT / 'RF_IMPORTANCE_B.csv')
    fig, ax = plt.subplots(figsize=(7, 5))
    imp['mean'][::-1].plot.barh(ax=ax, xerr=imp['std'][::-1], color='#2c7fb8')
    ax.set_xlabel('increase in MAE when the input is shuffled (held-out councils, Y)')
    ax.set_title('RF feature set B: permutation importance')
    plt.tight_layout(); plt.savefig(OUT / 'rf_importance.png', dpi=130); plt.close()
    # ---- shuffled-Y sanity
    shuffled_sanity(d).to_csv(OUT / 'RF_SANITY_SHUFFLED_Y.csv', index=False)
    print('all done', round(time.time() - t0), 's', flush=True)


if __name__ == '__main__':
    main()
