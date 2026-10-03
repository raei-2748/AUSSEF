"""Build the analysis table (all Y versions + X) from config.toml. No model is fitted here.

Run: python3 data.py      -> results/ANALYSIS_TABLE.csv, results/WEIGHTS.json, reproduction check printed
"""
import json
import sys
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
CFG = tomllib.loads((HERE / 'config.toml').read_text())
sys.path.insert(0, str(HERE.parent / 'Experiment 7'))
import build_y2 as B  # noqa: E402  (master workbook path + reader)

WORKBOOK = B.WORKBOOK
PILLARS = ['DL', 'IL', 'FP', 'SL']
KEY = ['agrn', 'region_id']


def src(name):
    return (HERE / CFG['sources'][name]).resolve()


def keyed(d):
    d = d.copy()
    d['agrn'] = d.agrn.astype(str)
    d['region_id'] = d.region_id.astype(str)
    return d


def load_master():
    m, _ = B.load()
    return m


def indicator_values(m, ind, cache):
    s = ind['source']
    if s == 'master':
        t = m
    elif s == 'council_fy':
        # council x financial-year table (e.g. Experiment 10 audited statements), joined on region_id and the fire FY.
        # fy_col holds the FY label; fy_label = "start" (2019 = Jul 2019-Jun 2020) or "end" (2020 = same FY);
        # fy_offset = 0 for the fire FY, 1 for the FY after, ...; several offsets in a list are averaged.
        raw = pd.read_parquet(HERE / ind['path']) if ind['path'].endswith('.parquet') else pd.read_csv(HERE / ind['path'])
        raw['region_id'] = raw.region_id.astype(str)
        shift = 1 if ind.get('fy_label', 'start') == 'end' else 0
        offs = ind.get('fy_offset', 0)
        parts = []
        for o in (offs if isinstance(offs, list) else [offs]):
            k = m[['region_id']].assign(_fy=(m.F + o + shift).astype(int).to_numpy())
            r = raw.rename(columns={ind['fy_col']: '_fy'})
            r['_fy'] = pd.to_numeric(r._fy, errors='coerce')
            parts.append(k.merge(r, on=['region_id', '_fy'], how='left', validate='m:1')[ind['columns']]
                         .apply(pd.to_numeric, errors='coerce').mean(axis=1).to_numpy())
        return pd.Series(np.nanmean(np.vstack(parts), axis=0) if len(parts) > 1 else parts[0], index=m.index)
    else:
        if s not in cache:
            p = src(s) if s in CFG['sources'] else (HERE / ind['path'])
            raw = pd.read_parquet(p) if str(p).endswith('.parquet') else pd.read_csv(p)
            cache[s] = m[KEY].merge(keyed(raw), on=KEY, how='left', validate='1:1')
        t = cache[s]
    vals = t[ind['columns']].apply(pd.to_numeric, errors='coerce').mean(axis=1)
    return pd.Series(vals.to_numpy(), index=m.index)


def pillar_table(m):
    """Indicator ranks and pillar scores from config, on the 218 master rows."""
    cache, out = {}, pd.DataFrame(index=m.index)
    for ind in CFG['indicator']:
        out[f"ind_{ind['name']}"] = (ind['sign'] * indicator_values(m, ind, cache)).rank(pct=True)
    for p in PILLARS:
        cols = [f"ind_{i['name']}" for i in CFG['indicator'] if i['pillar'] == p]
        out[p] = out[cols].mean(axis=1) if cols else np.nan
    return out


def composite(P, w):
    w = pd.Series(w, index=PILLARS)
    present = P[PILLARS].notna()
    num = (P[PILLARS].fillna(0) * w).sum(axis=1)
    den = (present * w).sum(axis=1)
    return (num / den).where(den > 0)


def entropy_weights(P):
    X = P[PILLARS].dropna().to_numpy()
    p = X / X.sum(axis=0)
    e = -(np.where(p > 0, p * np.log(p), 0)).sum(axis=0) / np.log(len(X))
    d = 1 - e
    return (d / d.sum()).tolist(), int(len(X))


def reproduction_check(m, P):
    """Config rebuild must equal the workbook pillars (DL checked against the v1 original-only rank)."""
    diffs = {p: float((P[p] - m[p]).abs().max()) for p in ['IL', 'FP', 'SL']}
    dl = pd.read_csv(src('dl_filled'))
    dl = m[KEY].merge(keyed(dl), on=KEY, how='left', validate='1:1')
    diffs['DL_v0_vs_workbook'] = float((dl.homes_per_1000_v0_original.rank(pct=True).to_numpy() - m.DL.to_numpy())[m.DL.notna().to_numpy()].__abs__().max())
    diffs['Y_v1_rule'] = float((composite(m[PILLARS], CFG['weights']['equal']) - m.Y).abs().max())
    return diffs


def x_table(m):
    it = pd.read_csv(src('council_items'))
    it['region_id'] = it.region_id.astype(str)
    it = it[['region_id', 'H', 'V', 'F', 'dwellings_in_bfpl12_share']].rename(columns={'dwellings_in_bfpl12_share': 'E2'})
    dl = keyed(pd.read_csv(src('dl_filled')))[KEY + ['dwellings', 'homes_per_1000_v2_inferred']]
    af = keyed(pd.read_parquet(src('affected')))[KEY + ['dwellings_in_fire', 'dwellings_within_1km']]
    x = m[KEY + ['region_name', 'F', 'share', 'X_fire_max_ffdi', 'X_fire_severity_high_extreme_share']].rename(
        columns={'F': 'season'})
    x = x.merge(it, on='region_id', how='left', validate='m:1').merge(dl, on=KEY, how='left', validate='1:1')
    x = x.merge(af, on=KEY, how='left', validate='1:1')
    if 'v3' in CFG['sources']:   # v3: Bowen's X23 (underinsurance proxy), PRESPEC Addendum v3
        x = x.merge(keyed(pd.read_csv(src('v3')))[KEY + ['X23']], on=KEY, how='left', validate='1:1')
    x['log_share'] = np.log(x.share.clip(lower=1e-6))
    x['peak_ffdi'] = x.X_fire_max_ffdi
    x['severity_high_extreme'] = x.X_fire_severity_high_extreme_share
    x['log_homes_in_fire_per_1000'] = np.log1p(x.dwellings_in_fire / x.dwellings * 1000)
    x['log_homes_within_1km_per_1000'] = np.log1p(x.dwellings_within_1km / x.dwellings * 1000)
    x['homes_v2'] = x.homes_per_1000_v2_inferred * x.dwellings / 1000      # count, for the Poisson baseline
    return x.drop(columns=['X_fire_max_ffdi', 'X_fire_severity_high_extreme_share'])


def build():
    m = load_master()
    P = pillar_table(m)
    X = x_table(m)
    W = {k: CFG['weights'][k] for k in ('equal', 'class_note', 'deck')}
    W['entropy'], n_ent = entropy_weights(P)
    T = X.copy()
    for c in P.columns:
        T[c] = P[c].to_numpy()
    T['Y_v1'] = m.Y.to_numpy()
    if (HERE / 'results_v1/ANALYSIS_TABLE.csv').exists():   # v3: carry the config-v1 composite for side-by-side reporting
        v1 = keyed(pd.read_csv(HERE / 'results_v1/ANALYSIS_TABLE.csv'))
        v1 = T[KEY].merge(v1[KEY + ['Y_comp', 'DL', 'IL', 'FP', 'SL']].rename(columns=lambda c: c if c in KEY else c + '_cfgv1'),
                          on=KEY, how='left', validate='1:1')
        for c in v1.columns[2:]:
            T[c] = v1[c].to_numpy()
    T['Y_comp'] = composite(P, W[CFG['weights']['main']]).to_numpy()
    for k in ('class_note', 'deck', 'entropy'):
        T[f'Y_comp_w_{k}'] = composite(P, W[k]).to_numpy()
    for p in PILLARS:
        w = [0 if q == p else 1 / 3 for q in PILLARS]
        T[f'Y_comp_drop_{p}'] = composite(P, w).to_numpy()
    T['Y_comp_complete'] = T.Y_comp.where(P[PILLARS].notna().all(axis=1).to_numpy())
    return T, W, n_ent, reproduction_check(m, pillar_table(m))


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    T, W, n_ent, chk = build()
    T.to_csv(OUT / 'ANALYSIS_TABLE.csv', index=False)
    json.dump({'weights_DL_IL_FP_SL': W, 'entropy_rows': n_ent, 'reproduction_max_abs_diff': chk,
               'config_version': CFG['meta']['version']}, open(OUT / 'WEIGHTS.json', 'w'), indent=2)
    print(json.dumps(chk, indent=1)); print(W)
    print(T[['Y_v1', 'Y_comp', 'DL', 'IL', 'FP', 'SL']].describe().round(3).to_string())
    print(T.isna().sum()[T.isna().sum() > 0].to_string())
