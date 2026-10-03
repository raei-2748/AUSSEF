"""Experiment 5: panel random forest (within-council, tested on later fires).

Panel: i = council (region_id), t = each declared fire the council went through.
Design A (within-council): Y and X are expressed as deviations from the council's
own mean over its TRAINING-period fires, so fixed council traits drop out.
Test by time: train on fires starting 2015-2019, test on fires starting 2023-2025
in councils that also had a training-period fire.

Source: master + codebook sheets of the Drive workbook nsw_bushfires_2015_2025_XY.xlsx.
Predictor availability masks: SOURCE_ELIGIBILITY_REGISTRY.csv, reused unchanged
from ChatGPT's Bowen_RF_Experiment_V2.

Run: python3 run_panel_rf.py   (writes results/ and REPORT.md)
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
WORKBOOK = Path('/Users/ray/Research/AUSSEF - Local/data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx')
SEED = 20260928
TRAIN_YEARS = (2015, 2019)
TEST_YEARS = (2023, 2025)
# Rules fixed before fitting
MIN_TRAIN_COVERAGE = 0.5      # X must be observed in >= 50% of training rows
MIN_WITHIN_SHARE = 0.05       # >= 5% of the X's training variance must be within-council
RF_GRID = [dict(min_samples_leaf=l, max_features=f) for l in (2, 5, 10) for f in (0.33, 0.7, 1.0)]
RIDGE_ALPHAS = [0.1, 1, 10, 100, 1000]
CLASS_CUTS = [0.4866308906879208, 0.6353925611165694, 0.7543974862033601]  # Y_class_from_Y
N_BOOT = 2000


# ---------- load ----------
def load():
    master = pd.read_excel(WORKBOOK, sheet_name='master', header=2, keep_default_na=False,
                           na_values=[''])
    codebook = pd.read_excel(WORKBOOK, sheet_name='codebook')
    codebook = codebook[codebook.sheet == 'master']
    master['row_id'] = master.agrn.astype(str) + '|' + master.region_id.astype(str)
    return master, codebook


def apply_registry(master, codebook):
    """Mask predictor cells not yet published at the fire's start (same rules as V2)."""
    candidates = codebook.loc[codebook.role_if_Y_sum == 'X', 'column'].tolist()
    registry = pd.read_csv(ROOT / 'SOURCE_ELIGIBILITY_REGISTRY.csv').fillna('')
    assert registry.column.is_unique and set(registry.column) == set(candidates)
    x = master[candidates].copy().mask(master[candidates].eq('N/A'))
    starts = pd.to_datetime(master.first_fire_start)
    vintage = pd.to_numeric(master.info_pop_census_year, errors='coerce')
    exclude, masked = [], 0
    for rule in registry.itertuples(index=False):
        bad = pd.Series(False, index=master.index)
        if rule.action == 'exclude':
            exclude.append(rule.column)
            bad[:] = True
        elif rule.action == 'census_release':
            dates = pd.to_datetime(vintage.map({2016: rule.date_2016, 2021: rule.date_2021}),
                                   errors='coerce')
            bad = dates.isna() | starts.le(dates)
        elif rule.action == 'not_before':
            bad = starts.lt(pd.Timestamp(rule.not_before))
        elif rule.action != 'retain':
            raise ValueError(f'Unreviewed eligibility action: {rule.action}')
        masked += int((bad & x[rule.column].notna()).sum())
        x.loc[bad, rule.column] = np.nan
    return x.drop(columns=exclude), exclude, masked


# ---------- panel transforms ----------
def within(df, council, ref_mask):
    """Deviation from each council's mean over the reference (training) rows."""
    means = df[ref_mask].groupby(council[ref_mask]).mean()
    return df - means.reindex(council.values).set_axis(df.index)


def within_share(s, council):
    s = s.dropna()
    total = ((s - s.mean()) ** 2).sum()
    if total == 0:
        return 0.0
    return float(((s - s.groupby(council[s.index]).transform('mean')) ** 2).sum() / total)


def to_class(y):
    return np.digitize(y, CLASS_CUTS) + 1


def fit_predict(kind, params, x_tr, y_tr, x_ap):
    if kind == 'rf':
        m = RandomForestRegressor(n_estimators=500, random_state=SEED, n_jobs=-1, **params)
        m.fit(x_tr, y_tr)
        return m, m.predict(x_ap)
    # ridge: demeaned X, missing -> 0 (= council's usual level), scaled on training rows
    mu, sd = x_tr.mean(), x_tr.std().replace(0, 1)
    z = lambda d: ((d.fillna(0) - mu) / sd).fillna(0)
    m = Ridge(alpha=params['alpha']).fit(z(x_tr), y_tr)
    return m, m.predict(z(x_ap))


def inner_select(kind, grid, x_raw, y_raw, council, event):
    """Grouped (by fire) inner CV on training rows; demeaning redone inside each fold."""
    scores = []
    folds = list(GroupKFold(n_splits=5).split(x_raw, groups=event))
    for params in grid:
        errs = []
        for tr, va in folds:
            ref = pd.Series(False, index=x_raw.index)
            ref.iloc[tr] = True
            ok = council.isin(council[ref])            # validation councils need history
            dx, dy = within(x_raw, council, ref), within(y_raw.to_frame(), council, ref).iloc[:, 0]
            va_idx = x_raw.index[va][ok.iloc[va].values]
            _, p = fit_predict(kind, params, dx[ref], dy[ref], dx.loc[va_idx])
            errs.extend(np.abs(dy.loc[va_idx] - p))
        scores.append({**params, 'kind': kind, 'inner_mae_deviation': float(np.mean(errs))})
    table = pd.DataFrame(scores)
    best = table.loc[table.inner_mae_deviation.idxmin()]
    return {k: best[k].item() for k in grid[0]}, table


def metrics(y, p, base):
    y, p = np.asarray(y), np.asarray(p)
    return {'MAE': np.mean(np.abs(y - p)), 'RMSE': np.sqrt(np.mean((y - p) ** 2)),
            'R2': 1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2),
            'Spearman(pred,Y)': pd.Series(p).corr(pd.Series(y), method='spearman'),
            'Spearman(pred dev,actual dev)': pd.Series(p - base).corr(pd.Series(y - base), method='spearman'),
            'Class accuracy': np.mean(to_class(p) == to_class(y)),
            'Class 3-4 recall': np.mean(to_class(p)[to_class(y) >= 3] >= 3)}


def main():
    OUT.mkdir(exist_ok=True)
    wb_hash = hashlib.sha256(WORKBOOK.read_bytes()).hexdigest()
    master, codebook = load()
    x_all, excluded, n_masked = apply_registry(master, codebook)

    # ---- panel structure ----
    start = pd.to_datetime(master.first_fire_start)
    master['year'] = start.dt.year
    n_fires = master.groupby('region_id').row_id.transform('size')
    in_train = master.year.between(*TRAIN_YEARS)
    in_test = master.year.between(*TEST_YEARS)
    train_councils = set(master.region_id[in_train & (n_fires >= 2)])
    panel = master[(n_fires >= 2) & (in_train | (in_test & master.region_id.isin(train_councils)))].copy()
    panel = panel.sort_values(['region_id', 'first_fire_start', 'agrn'])
    panel['t'] = panel.groupby('region_id').cumcount() + 1
    panel['split'] = np.where(panel.year.between(*TRAIN_YEARS), 'train', 'test')
    tr, te = panel.split.eq('train'), panel.split.eq('test')
    council, event = panel.region_id, panel.agrn.astype(str)

    structure = panel.groupby(['region_id', 'region_name']).agg(
        fires=('t', 'size'), train_fires=('split', lambda s: (s == 'train').sum()),
        test_fires=('split', lambda s: (s == 'test').sum()),
        Y_min=('Y', 'min'), Y_max=('Y', 'max')).reset_index()
    structure.to_csv(OUT / 'PANEL_STRUCTURE.csv', index=False)
    panel[['row_id', 'region_name', 'agrn', 'first_fire_start', 't', 'split', 'Y', 'Y_class',
           'Y_pillars_n']].to_csv(OUT / 'PANEL_ROWS.csv', index=False)

    # ---- X review (training rows only) ----
    x = x_all.loc[panel.index].apply(pd.to_numeric, errors='coerce')
    categorical = [c for c in x_all
                   if pd.to_numeric(x_all[c], errors='coerce').notna().sum() < x_all[c].notna().sum()]
    review = []
    for c in x_all.columns:
        s = x.loc[tr, c]
        cov = s.notna().mean()
        ws = within_share(s, council[tr]) if s.notna().sum() >= 10 else np.nan
        if c in categorical:
            dec = 'drop: text/categorical (cannot be demeaned)'
        elif cov < MIN_TRAIN_COVERAGE:
            dec = f'drop: training coverage < {MIN_TRAIN_COVERAGE:.0%}'
        elif not ws >= MIN_WITHIN_SHARE:
            dec = f'drop: within-council share < {MIN_WITHIN_SHARE:.0%} (a council trait, absorbed)'
        else:
            dec = 'keep'
        review.append({'column': c, 'train_coverage': round(cov, 3), 'within_council_share':
                       None if pd.isna(ws) else round(ws, 3), 'decision': dec})
    review = pd.DataFrame(review)
    review.to_csv(OUT / 'X_REVIEW.csv', index=False)
    feats = review.loc[review.decision.eq('keep'), 'column'].tolist()
    x = x[feats]

    # ---- within transformation (training-period council means) ----
    y = panel.Y.astype(float)
    dx = within(x, council, tr)
    base = y[tr].groupby(council[tr]).mean().reindex(council.values).set_axis(panel.index)
    dy = y - base

    # ---- tune + fit ----
    rf_params, rf_tab = inner_select('rf', RF_GRID, x[tr], y[tr], council[tr], event[tr])
    rg_params, rg_tab = inner_select('ridge', [{'alpha': a} for a in RIDGE_ALPHAS],
                                     x[tr], y[tr], council[tr], event[tr])
    pd.concat([rf_tab, rg_tab]).to_csv(OUT / 'INNER_TUNING.csv', index=False)
    rf, p_rf = fit_predict('rf', rf_params, dx[tr], dy[tr], dx[te])
    _, p_rg = fit_predict('ridge', rg_params, dx[tr], dy[tr], dx[te])

    yt, bt = y[te].values, base[te].values
    preds = {'Global training mean': np.full(te.sum(), y[tr].mean()),
             'Council own past mean': bt, 'Ridge (within)': bt + p_rg, 'RF (within)': bt + p_rf}
    res = pd.DataFrame({k: metrics(yt, v, bt) for k, v in preds.items()}).T
    res.to_csv(OUT / 'MODEL_RESULTS.csv')
    out = panel.loc[te, ['row_id', 'region_name', 'agrn', 'first_fire_start', 'Y', 'Y_pillars_n']].copy()
    for k, v in preds.items():
        out['pred: ' + k] = v
    out.to_csv(OUT / 'TEST_PREDICTIONS.csv', index=False)

    # ---- paired bootstrap over test fires ----
    rng = np.random.default_rng(SEED)
    ev = event[te].values
    uniq = np.unique(ev)
    err = {k: np.abs(yt - v) for k, v in preds.items()}
    boots = []
    for comp in ['Global training mean', 'Council own past mean', 'Ridge (within)']:
        d = err[comp] - err['RF (within)']          # positive = RF better
        ev_sum = pd.Series(d).groupby(ev).sum()
        ev_n = pd.Series(d).groupby(ev).size()
        draws = []
        for _ in range(N_BOOT):
            pick = rng.choice(uniq, len(uniq))
            draws.append(ev_sum[pick].sum() / ev_n[pick].sum())
        boots.append({'comparator': comp, 'MAE gain for RF': d.mean(),
                      'CI low': np.percentile(draws, 2.5), 'CI high': np.percentile(draws, 97.5)})
    boots = pd.DataFrame(boots)
    boots.to_csv(OUT / 'BOOTSTRAP_VS_RF.csv', index=False)

    # ---- level shift diagnostic ----
    shift = pd.DataFrame({'dev': dy[te], 'pillars': panel.Y_pillars_n[te]}).groupby('pillars').dev.agg(
        ['size', 'mean']).rename(columns={'size': 'test rows', 'mean': 'mean Y above council past mean'})
    shift.to_csv(OUT / 'TEST_LEVEL_SHIFT.csv')

    # ---- importance + PDP ----
    pi = permutation_importance(rf, dx[te], dy[te], scoring='neg_mean_absolute_error',
                                n_repeats=30, random_state=SEED, n_jobs=-1)
    imp = pd.DataFrame({'column': feats, 'test_MAE_increase': pi.importances_mean,
                        'sd': pi.importances_std,
                        'impurity_importance': rf.feature_importances_}).sort_values(
        'test_MAE_increase', ascending=False)
    imp.to_csv(OUT / 'VARIABLE_IMPORTANCE.csv', index=False)
    top = imp.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top.column, top.test_MAE_increase, xerr=top.sd, color='#4a7ab5')
    ax.axvline(0, color='k', lw=0.8)
    ax.set_xlabel('Increase in test MAE when shuffled (higher = more important)')
    ax.set_title('Panel RF: permutation importance on 2023-25 test fires')
    fig.tight_layout(); fig.savefig(OUT / 'variable_importance.png', dpi=150); plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    PartialDependenceDisplay.from_estimator(rf, dx[tr], imp.column.head(3).tolist(), ax=axes)
    fig.suptitle('Partial dependence (X and Y as deviations from the council\'s usual level)')
    fig.tight_layout(); fig.savefig(OUT / 'partial_dependence.png', dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.scatter(yt - bt, p_rf, s=18, color='#4a7ab5')
    lim = [min(yt - bt), max(yt - bt)]
    ax.plot(lim, lim, 'k--', lw=0.8)
    ax.set_xlabel('Actual: Y minus council past mean'); ax.set_ylabel('RF predicted deviation')
    ax.set_title('Test fires 2023-25')
    fig.tight_layout(); fig.savefig(OUT / 'predicted_vs_actual.png', dpi=150); plt.close(fig)

    # ---- where does the within-council signal come from? ----
    bs = event.eq('871')                                  # Black Summer declaration
    ex = tr & ~bs
    dx_ex = within(x, council, ex)
    dy_ex = y - y[ex].groupby(council[ex]).mean().reindex(council.values).set_axis(panel.index)
    signal = pd.DataFrame({
        'train 2015-19': dx[tr].corrwith(dy[tr], method='spearman'),
        'train excl. Black Summer': dx_ex[ex].corrwith(dy_ex[ex], method='spearman'),
        'test 2023-25': dx[te].corrwith(dy[te], method='spearman'),
        'train max': x[tr].max(), 'test max': x[te].max()})
    signal = signal.loc[imp.column.head(3).tolist() + ['X_fire_max_ffdi']]
    signal.to_csv(OUT / 'WITHIN_SIGNAL.csv')

    summary = {'workbook_sha256': wb_hash, 'panel_rows': len(panel), 'councils': council.nunique(),
               'train_rows': int(tr.sum()), 'train_councils': council[tr].nunique(),
               'train_fires': event[tr].nunique(), 'test_rows': int(te.sum()),
               'test_councils': council[te].nunique(), 'test_fires': event[te].nunique(),
               'x_candidates': x_all.shape[1] + len(excluded), 'x_excluded_by_registry': excluded,
               'cells_masked_by_registry': n_masked, 'x_kept': len(feats),
               'black_summer_train_rows': int((tr & bs).sum()),
               'rf_params': rf_params, 'ridge_params': rg_params,
               'rf_pred_dev_range': [float(p_rf.min()), float(p_rf.max())]}
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary, indent=2, default=str))
    write_report(summary, review, res, boots, shift, imp, signal)


def write_report(s, review, res, boots, shift, imp, signal):
    drops = review.decision.value_counts()
    f = lambda d: d.to_markdown(floatfmt='.3f')
    text = f"""# Experiment 5: panel random forest (within-council, by time)

Panel: **i = council**, **t = each fire the council went through**. Design A: Y and each X are
expressed as the deviation from that council's own mean over its 2015-2019 fires, so fixed council
traits drop out. The model learns *what makes a fire worse than usual for the same council*.
Tested by time: trained on fires starting 2015-2019, tested on fires starting 2023-2025.
Prediction for a test fire = council's past mean + predicted deviation.

## Data review

| | Rows | Councils | Fires |
|---|---:|---:|---:|
| Train (2015-19) | {s['train_rows']} | {s['train_councils']} | {s['train_fires']} |
| Test (2023-25) | {s['test_rows']} | {s['test_councils']} | {s['test_fires']} |

Only councils with 2+ fires and a training-period fire are in the panel. Per-council counts: `results/PANEL_STRUCTURE.csv`.

Predictors: {s['x_candidates']} codebook X candidates. {len(s['x_excluded_by_registry'])} excluded and
{s['cells_masked_by_registry']} cells masked by the V2 source-availability registry (data not yet published at the fire date).
Rules fixed before fitting, on training rows only:

{drops.to_frame('columns').to_markdown()}

**{s['x_kept']} predictors kept.** Full list with coverage and within-council share: `results/X_REVIEW.csv`.

## Results on 2023-25 test fires

{f(res)}

"Council own past mean" is the key panel baseline: it predicts each council will have its usual Y.
Spearman(pred dev, actual dev) asks whether the model ranks which fires are worse than usual.

RF settings chosen by grouped inner CV: `{s['rf_params']}`; ridge: `{s['ridge_params']}`.
RF predicted deviations range {s['rf_pred_dev_range'][0]:.3f} to {s['rf_pred_dev_range'][1]:.3f}.

### RF gain in MAE (positive = RF better), 95% bootstrap over test fires

{boots.to_markdown(index=False, floatfmt='.4f')}

### Level shift in the test years

{f(shift)}

Recent fires have fewer Y pillars (DL is often missing) and a different Y level. Part of any test
error is this shift in how Y is made up, not the fire itself.

## Where the within-council signal comes from

Spearman correlation between a council's deviation in X and its deviation in Y:

{f(signal)}

Black Summer (declaration 871) is {s['black_summer_train_rows']} of the {s['train_rows']} training rows.

## Variable importance (permutation on test fires)

{imp.head(15).to_markdown(index=False, floatfmt='.4f')}

![importance](results/variable_importance.png)
![PDP](results/partial_dependence.png)
![pred vs actual](results/predicted_vs_actual.png)

## Limits

- Y is the workbook's rank-based index built over all 218 rows; it is not rebuilt per split.
- Council means use only training-period fires, so test rows need a 2015-19 fire in the same council.
- Settings and rules were fixed before the test result was seen; nothing was re-tuned afterwards.
- Workbook SHA-256: `{s['workbook_sha256']}`.
"""
    (ROOT / 'REPORT.md').write_text(text)


if __name__ == '__main__':
    main()
