"""Experiment 14: build the analysis table (Y v4 versions + X + v1/v3 Ys carried from Experiment 9). No model fitted.
Run: python3 data.py   -> results/ANALYSIS_TABLE.csv, results/COVERAGE.csv
"""
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
CFG = tomllib.loads((HERE / 'config.toml').read_text())
PILLARS = ['DL', 'IL', 'FP', 'SL']
KEY = ['agrn', 'region_id']
VERSIONS = {'main': 'Y_v4', 'olg': 'Y_v4_olg', 'resdeaths': 'Y_v4_resident_deaths', 'h0': 'Y_v4_H0',
            'h12': 'Y_v4_H12', 'h3': 'Y_v4_H3'}
E9_KEEP = ['region_name', 'season', 'share', 'H', 'V', 'F', 'E2', 'dwellings', 'homes_per_1000_v2_inferred',
           'dwellings_in_fire', 'dwellings_within_1km', 'X23', 'log_share', 'peak_ffdi', 'severity_high_extreme',
           'log_homes_in_fire_per_1000', 'log_homes_within_1km_per_1000', 'homes_v2',
           'Y_v1', 'Y_comp_cfgv1', 'DL_cfgv1', 'IL_cfgv1', 'FP_cfgv1', 'SL_cfgv1', 'Y_comp', 'DL', 'IL', 'FP', 'SL']


def src(k):
    return (HERE / CFG['sources'][k]).resolve()


def composite(P, w=CFG['weights']['main']):
    w = pd.Series(w, index=PILLARS)
    present = P[PILLARS].notna()
    num = (P[PILLARS].fillna(0) * w).sum(axis=1)
    den = (present * w).sum(axis=1)
    return (num / den).where(den > 0)


def pillars(T, version, how='rank'):
    out = pd.DataFrame(index=T.index)
    for ind in CFG['indicator']:
        col = ind.get(version)
        if col is None:
            continue
        x = ind['sign'] * pd.to_numeric(T[col], errors='coerce')
        if how == 'rank':
            out[ind['name']] = x.rank(pct=True)
        else:   # magnitude: z-score over rows present, clipped to [-3, 3]
            out[ind['name']] = ((x - x.mean()) / x.std()).clip(-3, 3)
    for p in PILLARS:
        cols = [i['name'] for i in CFG['indicator'] if i['pillar'] == p and i.get(version) is not None]
        out[p] = out[cols].mean(axis=1) if cols else np.nan
    return out


def build():
    e9 = pd.read_csv(src('exp9_table'), dtype={'agrn': str, 'region_id': str})
    T = e9[KEY + E9_KEEP].rename(columns={'Y_comp': 'Y_v3', 'DL': 'DL_v3', 'IL': 'IL_v3', 'FP': 'FP_v3', 'SL': 'SL_v3',
                                         'Y_comp_cfgv1': 'Y_v1cfg', 'DL_cfgv1': 'DL_v1', 'IL_cfgv1': 'IL_v1',
                                         'FP_cfgv1': 'FP_v1', 'SL_cfgv1': 'SL_v1'})
    v4 = pd.read_csv(src('indicators'), dtype={'agrn': str, 'region_id': str})
    T = T.merge(v4, on=KEY, how='left', validate='1:1')
    assert len(T) == 218
    cov = []
    for ver, yname in VERSIONS.items():
        P = pillars(T, ver)
        if ver == 'main':
            for c in P.columns:
                T[f'ind_{c}' if c not in PILLARS else c] = P[c].to_numpy()
        else:
            for p in PILLARS:
                T[f'{p}_{yname}'] = P[p].to_numpy()
        T[yname] = composite(P).to_numpy()
        for c in P.columns:
            cov.append(dict(version=yname, item=c, rows=int(P[c].notna().sum())))
        cov.append(dict(version=yname, item='Y', rows=int(T[yname].notna().sum())))
    M = pillars(T, 'main', how='mag')
    T['Y_v4_mag'] = composite(M).to_numpy()
    for p in PILLARS:
        T[f'{p}_mag'] = M[p].to_numpy()
    cov.append(dict(version='Y_v4_mag', item='Y', rows=int(T.Y_v4_mag.notna().sum())))
    return T, pd.DataFrame(cov)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    T, cov = build()
    T.to_csv(OUT / 'ANALYSIS_TABLE.csv', index=False)
    cov.to_csv(OUT / 'COVERAGE.csv', index=False)
    print(cov.pivot(index='item', columns='version', values='rows').to_string())
