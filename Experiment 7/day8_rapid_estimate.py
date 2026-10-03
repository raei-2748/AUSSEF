"""Experiment 7, Day 8: rapid post-fire estimate of homes destroyed (PRESPEC_DAY8.md, LOCK_DAY8.txt).
Run: python3 day8_rapid_estimate.py"""
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import build_y2 as B
import day2_consequence as C

OUT = B.OUT
TARGET = 'homes_per_1000_v2_inferred'
rng = np.random.default_rng(20261001)
MODELS = {'R0': ['log_share'], 'R1': ['A', 'I'], 'R2': ['A', 'I', 'S'], 'R3': ['A', 'I', 'S', 'W']}


def main():
    m, _ = B.load()
    traits = C.council_traits()
    r = C.rows_table(m, traits)
    ap = pd.read_parquet(B.DATASET / 'data/enrich/affected_pop_event_council.parquet')
    ap['agrn'], ap['region_id'] = ap.agrn.astype(str), ap.region_id.astype(str)
    r = r.merge(ap[['agrn', 'region_id', 'dwellings_in_fire', 'dwellings_within_1km']], on=['agrn', 'region_id'],
                how='left', validate='1:1')
    r['A'] = np.log((r.dwellings_within_1km / r.dwellings).clip(lower=1e-6))
    r['I'] = np.log((r.dwellings_in_fire / r.dwellings).clip(lower=1e-6))
    sev = m.X_fire_severity_high_extreme_share.to_numpy()
    r['S'] = (sev - np.nanmean(sev)) / np.nanstd(sev, ddof=1)
    w = m.X_fire_max_ffdi.to_numpy()
    r['W'] = (w - w.mean()) / w.std(ddof=1)
    d = r.dropna(subset=[TARGET, 'dwellings', 'A', 'I', 'S', 'W', 'log_share']).copy()
    for n, cols in MODELS.items():
        pred = pd.Series(np.nan, index=d.index)
        for f in sorted(d.F.unique()):
            tr, te = d[d.F != f], d[d.F == f]
            pred[te.index] = C.predict_rate(C.fit(tr, cols, TARGET), te, cols)
        d[f'pred_{n}'] = pred
        d[f'pred_homes_{n}'] = pred * d.dwellings / 1000
    d['homes'] = d[TARGET] * d.dwellings / 1000
    res = dict(rows=int(len(d)), positives=int((d.homes > 0).sum()), homes_total=float(d.homes.sum()))
    for n in MODELS:
        res[f'cv_rho_{n}'] = float(spearmanr(d[f'pred_{n}'], d[TARGET])[0])
        res[f'cv_deviance_{n}'] = C.deviance(d.homes, d[f'pred_homes_{n}'])
    e, lo, hi = C.paired_boot(d, 'pred_R2', 'pred_R0', TARGET, rng)
    res.update(R2_minus_R0=e, ci_low=lo, ci_high=hi)
    dev_down = res['cv_deviance_R2'] < res['cv_deviance_R0']
    res['verdict'] = 'Rapid estimate works' if (lo > 0 and dev_down) else ('partly' if (lo > 0 or dev_down) else 'no')
    bs = d.F == 2019
    res['black_summer_observed'] = float(d.homes[bs].sum())
    res['other_observed'] = float(d.homes[~bs].sum())
    for n in MODELS:
        res[f'black_summer_pred_{n}'] = float(d[f'pred_homes_{n}'][bs].sum())
        res[f'other_pred_{n}'] = float(d[f'pred_homes_{n}'][~bs].sum())
    pos = d.homes >= 1
    ratio = d.loc[pos, 'pred_homes_R2'] / d.loc[pos, 'homes']
    res['R2_within_factor2_share'] = float(((ratio >= 0.5) & (ratio <= 2)).mean())
    res['R0_within_factor2_share'] = float((((d.loc[pos, 'pred_homes_R0'] / d.loc[pos, 'homes']).between(0.5, 2))).mean())
    full = C.fit(d.reset_index(drop=True), MODELS['R3'], TARGET)
    res['R3_in_sample_rate_ratios'] = {k: float(np.exp(v)) for k, v in full.params.items()}
    full2 = C.fit(d.reset_index(drop=True), MODELS['R2'], TARGET)
    res['R2_in_sample_rate_ratios'] = {k: float(np.exp(v)) for k, v in full2.params.items()}
    json.dump(res, open(OUT / 'DAY8_RAPID.json', 'w'), indent=2)
    d[['agrn', 'region_id', 'region_name', 'F', 'share', 'dwellings_in_fire', 'dwellings_within_1km', 'homes'] +
      [f'pred_homes_{n}' for n in MODELS]].to_csv(OUT / 'DAY8_ROWS.csv', index=False)
    print(json.dumps(res, indent=1))
    top = d.sort_values('homes', ascending=False).head(12)
    print(top[['region_name', 'F', 'homes', 'pred_homes_R0', 'pred_homes_R2', 'pred_homes_R3']].round(0).to_string())


if __name__ == '__main__':
    main()
