"""Experiment 7, Day 3: build the new Y and X table and test fire weather (PRESPEC_DAY3.md, LOCK_DAY3.txt).
Run: python3 day3_new_y_x.py   (after day2_consequence.py)"""
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import build_y2 as B
import day2_consequence as C

OUT = B.OUT
TARGET = 'homes_per_1000_v2_inferred'
rng = np.random.default_rng(20261001)
MODELS = {'M2': ['log_share', 'E2', 'V'], 'M4': ['log_share', 'E2', 'V', 'FFDI']}


def severity(homes, deaths):
    cls = pd.Series(np.nan, index=homes.index)
    known = homes.notna() | (deaths >= 1)
    h, dd = homes.fillna(0), deaths.fillna(0)
    cls[known] = 1
    cls[known & ((h >= 1) | (dd >= 1))] = 2
    cls[known & ((h >= 10) | (dd >= 2))] = 3
    cls[known & (h >= 100)] = 4
    return cls


def main():
    m, _ = B.load()
    traits = C.council_traits()
    r = C.rows_table(m, traits)
    r['FFDI_raw'] = m.X_fire_max_ffdi.to_numpy()
    r['FFDI'] = (r.FFDI_raw - r.FFDI_raw.mean()) / r.FFDI_raw.std(ddof=1)
    r['homes'] = r[TARGET] * r.dwellings / 1000
    deaths = m.SL_deaths_sourced.fillna(m.info_reported_deaths)
    r['deaths'] = deaths.to_numpy()
    r['Y_class_v3'] = severity(r.homes, r.deaths)
    r['Y_class_v3_label'] = r.Y_class_v3.map({1: 'Light', 2: 'Moderate', 3: 'Severe', 4: 'Extreme'}).fillna('Unknown')
    r['Y_class_v1'] = m.Y_class.to_numpy()

    # ---- the new Y / X table
    cols = ['agrn', 'region_id', 'region_name', 'F', 'share', 'homes', TARGET, 'deaths', 'Y_class_v3',
            'Y_class_v3_label', 'Y_class_v1', 'FFDI_raw', 'E2_raw', 'V_raw', 'H_raw', 'log_share', 'FFDI', 'E2', 'V', 'H',
            'DL_fill_flag']
    tab = r[cols].rename(columns={TARGET: 'Y_homes_per_1000', 'F': 'fire_fy_start'})
    tab.to_csv(OUT / 'NEW_Y_X_TABLE.csv', index=False)
    xt = pd.crosstab(tab.Y_class_v1.fillna(0).astype(int), tab.Y_class_v3_label)
    xt.to_csv(OUT / 'DAY3_CLASS_V1_VS_V3.csv')
    print(tab.Y_class_v3_label.value_counts())
    print(xt)

    # ---- weather test
    d = r.dropna(subset=[TARGET, 'E2', 'V', 'FFDI', 'dwellings']).copy()
    for name, cols_ in MODELS.items():
        pred = pd.Series(np.nan, index=d.index)
        for f in sorted(d.F.unique()):
            tr, te = d[d.F != f], d[d.F == f]
            pred[te.index] = C.predict_rate(C.fit(tr, cols_, TARGET), te, cols_)
        d[f'pred_{name}'] = pred
    y = d[TARGET] * d.dwellings / 1000
    res = dict(rows=int(len(d)), positives=int((d[TARGET] > 0).sum()))
    for n in MODELS:
        res[f'cv_rho_{n}'] = float(spearmanr(d[f'pred_{n}'], d[TARGET])[0])
        res[f'cv_deviance_{n}'] = C.deviance(y, d[f'pred_{n}'] * d.dwellings / 1000)
    e, lo, hi = C.paired_boot(d, 'pred_M4', 'pred_M2', TARGET, rng)
    res.update(M4_minus_M2=e, ci_low=lo, ci_high=hi)
    bs = d.F == 2019
    res['black_summer_observed'] = float(y[bs].sum())
    for n in MODELS:
        res[f'black_summer_pred_{n}'] = float((d[f'pred_{n}'] * d.dwellings / 1000)[bs].sum())
        res[f'other_pred_{n}'] = float((d[f'pred_{n}'] * d.dwellings / 1000)[~bs].sum())
    res['other_observed'] = float(y[~bs].sum())
    dev_down = res['cv_deviance_M4'] < res['cv_deviance_M2']
    rank_up = lo > 0
    res['verdict'] = 'weather helps' if dev_down and rank_up else ('partly' if dev_down or rank_up else 'no')
    res['ffdi_mean_black_summer'] = float(d.FFDI_raw[bs].mean())
    res['ffdi_mean_other'] = float(d.FFDI_raw[~bs].mean())
    # in-sample rate ratios with council-cluster bootstrap
    dd = d.reset_index(drop=True)
    base = C.fit(dd, MODELS['M4'], TARGET).params
    gs = [s.index.to_numpy() for _, s in dd.groupby('region_id')]
    bsr = []
    for _ in range(1000):
        idx = np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))])
        try:
            bsr.append(C.fit(dd.loc[idx].reset_index(drop=True), MODELS['M4'], TARGET).params.to_numpy())
        except Exception:
            pass
    bsr = np.array(bsr)
    rr = []
    for k, t in enumerate(['const'] + MODELS['M4']):
        lo_, hi_ = np.percentile(bsr[:, k], [2.5, 97.5])
        rr.append(dict(term=t, rate_ratio=float(np.exp(base[t])), ci_low=float(np.exp(lo_)), ci_high=float(np.exp(hi_))))
    res['M4_rate_ratios'] = rr
    json.dump(res, open(OUT / 'DAY3_WEATHER.json', 'w'), indent=2)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
