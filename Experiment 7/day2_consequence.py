"""Experiment 7, Day 2: consequence model for homes destroyed, and the map layers. Rules: PRESPEC_DAY2.md
(hash in LOCK_DAY2.txt).

Run: python3 day2_consequence.py      (after build_y2.py and deviations_day1.py)
"""
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr, rankdata

import build_y2 as B
import deviations_day1 as D

warnings.filterwarnings('ignore')
HERE = B.HERE
OUT = B.OUT
EXP6 = HERE.parent / 'Experiment 6'
SEED = 20260930
N_BOOT = 2000
N_REFIT = 1000
MODELS = {'M0': ['log_share'], 'M1': ['log_share', 'E2'], 'M2': ['log_share', 'E2', 'V'],
          'M3': ['log_share', 'E2', 'V', 'H', 'F']}
SCENARIO_SHARE = 0.20


def council_traits():
    it = pd.read_csv(EXP6 / 'results/COUNCIL_ITEMS_v2.csv')
    it['region_id'] = it.region_id.astype(str)
    t = it[['region_id', 'region_name', 'dwellings_in_bfpl12_share', 'H', 'V', 'F']].rename(
        columns={'dwellings_in_bfpl12_share': 'E2_raw', 'H': 'H_raw', 'V': 'V_raw', 'F': 'F_raw'})
    for c in ('E2', 'H', 'V', 'F'):
        x = t[f'{c}_raw']
        t[c] = (x - x.mean()) / x.std(ddof=1)
    ex = pd.read_csv(EXP6 / 'results/COUNCIL_EXPOSURE_BFPL.csv')
    ex['region_id'] = ex.region_id.astype(str)
    return t.merge(ex[['region_id', 'dwellings_mb']], on='region_id', how='left')


def rows_table(m, traits):
    dl = pd.read_csv(EXP6 / 'followups/dl_fill/DL_FILLED.csv')
    dl['agrn'] = dl.agrn.astype(str)
    dl['region_id'] = dl.region_id.astype(str)
    keep = ['agrn', 'region_id', 'dwellings', 'homes_per_1000_v1_reported', 'homes_per_1000_v2_inferred',
            'homes_per_1000_v3_estimated', 'DL_fill_flag']
    r = m[['agrn', 'region_id', 'region_name', 'F', 'share', 'IL', 'FP', 'SL']].merge(dl[keep], on=['agrn', 'region_id'],
                                                                                    how='left', validate='1:1')
    r = r.merge(traits, on='region_id', how='left', suffixes=('', '_t'))
    r['log_share'] = np.log(r.share.clip(lower=1e-6))
    r['S_v1'] = r[['IL', 'FP', 'SL']].mean(axis=1).where(r[['IL', 'FP', 'SL']].notna().sum(axis=1) >= 2)
    return r


def fit(d, cols, target):
    y = d[target] * d.dwellings / 1000.0
    X = sm.add_constant(d[cols], has_constant='add')
    return sm.GLM(y, X, family=sm.families.Poisson(), offset=np.log(d.dwellings)).fit()


def predict_rate(res, d, cols):
    X = sm.add_constant(d[cols], has_constant='add')
    return np.exp(X.to_numpy() @ res.params.to_numpy()) * 1000.0


def cv_predictions(d, target):
    """Leave-one-fire-season-out predictions (rate per 1,000 dwellings) for every model."""
    pred = pd.DataFrame(index=d.index, columns=list(MODELS), dtype=float)
    for f in sorted(d.F.unique()):
        tr, te = d[d.F != f], d[d.F == f]
        for name, cols in MODELS.items():
            pred.loc[te.index, name] = predict_rate(fit(tr, cols, target), te, cols)
    return pred


def deviance(y, mu):
    y, mu = np.asarray(y, float), np.asarray(mu, float)
    t = np.where(y > 0, y * np.log(np.where(y > 0, y, 1) / mu), 0.0)
    return float(2 * np.sum(t - (y - mu)))


def paired_boot(d, a, b, target, rng, n=N_BOOT):
    gs = [sub.index.to_numpy() for _, sub in d.groupby('region_id')]
    est = spearmanr(d[a], d[target])[0] - spearmanr(d[b], d[target])[0]
    bs = []
    for _ in range(n):
        idx = np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))])
        s = d.loc[idx]
        bs.append(spearmanr(s[a], s[target])[0] - spearmanr(s[b], s[target])[0])
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return est, lo, hi


def primary(r, target, rng):
    d = r.dropna(subset=[target, 'E2', 'V', 'H', 'F', 'dwellings']).copy()
    pred = cv_predictions(d, target)
    for c in MODELS:
        d[f'pred_{c}'] = pred[c].astype(float)
    rho = {c: spearmanr(d[f'pred_{c}'], d[target])[0] for c in MODELS}
    y = d[target] * d.dwellings / 1000
    dev = {c: deviance(y, d[f'pred_{c}'] * d.dwellings / 1000) for c in MODELS}
    est, lo, hi = paired_boot(d, 'pred_M1', 'pred_M0', target, rng)
    e2, lo2, hi2 = paired_boot(d, 'pred_M2', 'pred_M1', target, rng)
    return d, dict(target=target, rows=int(len(d)), councils=int(d.region_id.nunique()), seasons=int(d.F.nunique()),
                   positives=int((d[target] > 0).sum()), **{f'cv_rho_{c}': rho[c] for c in MODELS},
                   **{f'cv_deviance_{c}': dev[c] for c in MODELS},
                   M1_minus_M0=est, M1_minus_M0_ci_low=lo, M1_minus_M0_ci_high=hi,
                   M2_minus_M1=e2, M2_minus_M1_ci_low=lo2, M2_minus_M1_ci_high=hi2,
                   verdict='Consequence confirmed' if lo > 0 else 'Not confirmed')


def coefs(d, target, rng):
    gs = [sub.index.to_numpy() for _, sub in d.groupby('region_id')]
    rows = []
    for name in ('M1', 'M2', 'M3'):
        cols = MODELS[name]
        base = fit(d, cols, target).params
        bs = []
        for _ in range(N_REFIT):
            idx = np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))])
            try:
                bs.append(fit(d.loc[idx].reset_index(drop=True), cols, target).params.to_numpy())
            except Exception:
                continue
        bs = np.array(bs)
        for k, c in enumerate(['const'] + cols):
            lo, hi = np.nanpercentile(bs[:, k], [2.5, 97.5])
            rows.append(dict(model=name, term=c, coef=base[c], ci_low=lo, ci_high=hi,
                             rate_ratio=np.exp(base[c]), rr_ci_low=np.exp(lo), rr_ci_high=np.exp(hi), refits=len(bs)))
    return pd.DataFrame(rows)


def partial_spearman(d, x, target, rng, n=N_BOOT):
    def pr(s):
        rs, rx, ry = rankdata(s.share), rankdata(s[x]), rankdata(s[target])
        A = np.column_stack([np.ones(len(s)), rs])
        ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]
        ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
        return np.corrcoef(ex, ey)[0, 1]
    est = pr(d)
    gs = [sub.index.to_numpy() for _, sub in d.groupby('region_id')]
    bs = [pr(d.loc[np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))])]) for _ in range(n)]
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return est, lo, hi


def nsw2013(r, traits, target):
    d = r.dropna(subset=[target, 'E2', 'dwellings'])
    x = pd.read_csv(B.DATASET / 'data/extra_fires/extra_fire_rows.csv', dtype={'region_id': str})
    x = x[(x.event == 'NSW_2013_oct') & x.homes_destroyed.notna()].copy()
    x = x.merge(traits[['region_id', 'E2', 'V', 'H', 'F', 'E2_raw']], on='region_id', how='inner')
    x['dwellings'] = x.dwellings_census2011
    x['share'] = x.share_burned
    x['log_share'] = np.log(x.share)
    x['observed'] = x.homes_destroyed / x.dwellings * 1000
    for name in ('M0', 'M1'):
        x[f'pred_{name}'] = predict_rate(fit(d, MODELS[name], target), x, MODELS[name])
        x[f'pred_homes_{name}'] = x[f'pred_{name}'] * x.dwellings / 1000
    summ = dict(rows=int(len(x)), observed_total=float(x.homes_destroyed.sum()),
                **{f'rho_{n}': (spearmanr(x[f'pred_{n}'], x.observed)[0] if len(x) > 2 else np.nan) for n in ('M0', 'M1')},
                **{f'pred_total_{n}': float(x[f'pred_homes_{n}'].sum()) for n in ('M0', 'M1')})
    return x[['region_id', 'region_name', 'share', 'E2_raw', 'homes_destroyed', 'flag_DL', 'observed', 'pred_M0',
              'pred_M1', 'pred_homes_M0', 'pred_homes_M1']], summ


def disadvantage(r, m, rng):
    out = []
    for lab, sel in {'all rows': r.share > -1, '< 1% burned': r.share < .01, '>= 5% burned': r.share >= .05}.items():
        n, e, lo, hi = B.boot_rho(r.V_raw[sel], r.S_v1[sel], r.region_id[sel], rng)
        out.append(dict(check=f'V vs socioeconomic part of Y v1, {lab}', rows=n, spearman=e, ci_low=lo, ci_high=hi))
    # trend-robust counterfactual (Day 1 D1): real vs placebo
    ly = B.load()[1]
    groups = B.olg_groups(ly)
    aff, master, _ = B.affected_fys(m)
    panels = B.series(ly, groups)
    res = D.fit_all(D.FETrend, panels, groups, m, aff | master)
    inds = [i[0] for i in D.INDS]
    _, S, _ = B.rank_y({i: res[i]['sign'] * res[i]['tau'] for i in inds}, m.DL, inds)
    _, pS, _ = B.rank_y({i: res[i]['placebo_z'] for i in inds}, pd.Series(np.nan, index=m.index), inds)
    V = r.V_raw.to_numpy()
    for lab, s in {'V vs socioeconomic part (trend-robust), real fires': S,
                   'V vs socioeconomic part (trend-robust), placebo 3 years earlier': pS}.items():
        n, e, lo, hi = B.boot_rho(V, s.to_numpy(), r.region_id.to_numpy(), rng)
        out.append(dict(check=lab, rows=n, spearman=e, ci_low=lo, ci_high=hi))
    return pd.DataFrame(out)


def map_layers(r, traits, target, use_model):
    m6 = r.groupby('region_id').share.max()
    t = traits.copy()
    t['had_5pct_fire'] = t.region_id.map(m6).fillna(0).ge(0.05).astype(int)
    X = sm.add_constant(t[['H']])
    lg = sm.Logit(t.had_5pct_fire, X).fit(disp=0)
    t['L'] = lg.predict(X)
    loo = []
    for i in t.index:
        tr = t.drop(index=i)
        f = sm.Logit(tr.had_5pct_fire, sm.add_constant(tr[['H']])).fit(disp=0)
        loo.append(float(f.predict(pd.DataFrame({'const': [1.0], 'H': [t.at[i, 'H']]}))[0]))
    t['L_loo'] = loo
    pos = t.had_5pct_fire.to_numpy() == 1
    auc = B.__dict__.get('auc')
    rk = rankdata(t.L_loo)
    auc_loo = (rk[pos].sum() - pos.sum() * (pos.sum() + 1) / 2) / (pos.sum() * (~pos).sum())
    d = r.dropna(subset=[target, 'E2', 'V', 'H', 'F', 'dwellings'])
    cols = MODELS[use_model]
    res = fit(d, cols, target)
    sc = t.copy()
    sc['log_share'] = np.log(SCENARIO_SHARE)
    t['C'] = predict_rate(res, sc, cols)
    t['expected_loss_index'] = t.L * t.C
    t['L_tercile'] = pd.qcut(t.L.rank(method='first'), 3, labels=[1, 2, 3]).astype(int)
    t['C_tercile'] = pd.qcut(t.C.rank(method='first'), 3, labels=[1, 2, 3]).astype(int)
    # realised 2015-25 homes destroyed per 1,000 dwellings (rows with a figure; councils without rows = 0)
    rr = r.dropna(subset=[target, 'dwellings']).assign(homes=lambda x: x[target] * x.dwellings / 1000)
    homes = rr.groupby('region_id').homes.sum()
    any_rows = set(r.region_id)
    t['realised_homes_2015_25'] = [homes.get(k, 0.0 if k not in any_rows else np.nan) for k in t.region_id]
    t['realised_per_1000'] = t.realised_homes_2015_25 / t.dwellings_mb * 1000
    chk = []
    ok = t.dropna(subset=['realised_per_1000'])
    for c in ('H', 'E2', 'V', 'L', 'C', 'expected_loss_index'):
        chk.append(dict(layer=c, councils=len(ok), spearman_with_realised=spearmanr(ok[c], ok.realised_per_1000)[0]))
    lost = ok.realised_per_1000 >= 1.0
    for c in ('H', 'E2', 'L', 'C', 'expected_loss_index'):
        rk = rankdata(ok[c])
        a = (rk[lost.to_numpy()].sum() - lost.sum() * (lost.sum() + 1) / 2) / (lost.sum() * (~lost).sum())
        chk.append(dict(layer=c, councils=len(ok), auc_lost_1_per_1000=a, positives=int(lost.sum())))
    return t, dict(likelihood_coef_H=float(lg.params.H), likelihood_auc_in_sample=None, likelihood_auc_loo=float(auc_loo),
                   positives=int(pos.sum()), consequence_model=use_model,
                   consequence_params={k: float(v) for k, v in res.params.items()}), pd.DataFrame(chk)


def main():
    rng = np.random.default_rng(SEED)
    m, _ = B.load()
    traits = council_traits()
    r = rows_table(m, traits)
    print('rows', len(r), 'with v2 target', r.homes_per_1000_v2_inferred.notna().sum())

    target = 'homes_per_1000_v2_inferred'
    d, prim = primary(r, target, rng)
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in prim.items()}, indent=1))
    json.dump(prim, open(OUT / 'DAY2_PRIMARY.json', 'w'), indent=2)
    d.to_csv(OUT / 'DAY2_OOS_ROWS.csv', index=False)

    sens = [prim]
    for t in ('homes_per_1000_v1_reported', 'homes_per_1000_v3_estimated'):
        _, p = primary(r, t, rng)
        sens.append(p)
    sens = pd.DataFrame(sens)
    sens.to_csv(OUT / 'DAY2_SENSITIVITY.csv', index=False)
    print(sens[['target', 'rows', 'positives', 'cv_rho_M0', 'cv_rho_M1', 'cv_rho_M2', 'cv_rho_M3', 'M1_minus_M0',
                'M1_minus_M0_ci_low', 'M1_minus_M0_ci_high', 'verdict']].round(3).to_string())

    cf = coefs(d.reset_index(drop=True), target, rng)
    cf.to_csv(OUT / 'DAY2_COEFS.csv', index=False)
    print(cf[cf.term != 'const'][['model', 'term', 'rate_ratio', 'rr_ci_low', 'rr_ci_high']].round(2).to_string())

    part = []
    for x in ('E2_raw', 'V_raw', 'H_raw', 'F_raw'):
        e, lo, hi = partial_spearman(d.reset_index(drop=True), x, target, rng)
        part.append(dict(predictor=x, partial_spearman_given_share=e, ci_low=lo, ci_high=hi, rows=len(d)))
    part = pd.DataFrame(part)
    part.to_csv(OUT / 'DAY2_PARTIAL.csv', index=False)
    print(part.round(3).to_string())

    x13, s13 = nsw2013(r, traits, target)
    x13.to_csv(OUT / 'DAY2_NSW2013.csv', index=False)
    json.dump(s13, open(OUT / 'DAY2_NSW2013.json', 'w'), indent=2)
    print(x13.round(3).to_string())
    print(s13)

    dis = disadvantage(r, m, rng)
    dis.to_csv(OUT / 'DAY2_DISADVANTAGE.csv', index=False)
    print(dis.round(3).to_string())

    use = 'M2' if prim['cv_rho_M2'] - prim['cv_rho_M1'] >= 0.05 else 'M1'
    layers, meta, chk = map_layers(r, traits, target, use)
    layers.to_csv(OUT / 'COUNCIL_MAP_LAYERS.csv', index=False)
    json.dump(meta, open(OUT / 'DAY2_MAP_META.json', 'w'), indent=2)
    chk.to_csv(OUT / 'DAY2_COUNCIL_CHECK.csv', index=False)
    print(meta)
    print(chk.round(3).to_string())
    print(layers.sort_values('expected_loss_index', ascending=False)[
        ['region_name', 'L', 'C', 'expected_loss_index', 'E2_raw', 'realised_per_1000']].head(15).round(3).to_string())


if __name__ == '__main__':
    main()
