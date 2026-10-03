"""Experiment 7, Day 2B: prospective test of a pre-Black-Summer map (PRESPEC_DAY2B.md, hash in LOCK_DAY2B.txt).
Run: python3 day2b_prospective.py   (after day2_consequence.py)"""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import rankdata, spearmanr

import build_y2 as B
import day2_consequence as C

OUT = B.OUT
TARGET = 'homes_per_1000_v2_inferred'
rng = np.random.default_rng(20260930)


def auc(score, pos):
    r = rankdata(score)
    n1, n0 = pos.sum(), (~pos).sum()
    return (r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def boot_auc(score, pos, n=2000):
    idx = np.arange(len(score))
    bs = []
    for _ in range(n):
        s = rng.choice(idx, len(idx))
        if pos[s].sum() and (~pos[s]).sum():
            bs.append(auc(score[s], pos[s]))
    return np.percentile(bs, [2.5, 97.5])


def main():
    m, _ = B.load()
    traits = C.council_traits()
    r = C.rows_table(m, traits)
    pre = r[r.F <= 2018]
    t = traits.copy()
    occ = pre.groupby('region_id').share.max()
    t['had_5pct_pre'] = t.region_id.map(occ).fillna(0).ge(0.05).astype(int)
    lg = sm.Logit(t.had_5pct_pre, sm.add_constant(t[['H']])).fit(disp=0)
    t['L_pre'] = lg.predict(sm.add_constant(t[['H']]))
    d = pre.dropna(subset=[TARGET, 'E2', 'dwellings'])
    res = C.fit(d, C.MODELS['M1'], TARGET)
    sc = t.assign(log_share=np.log(C.SCENARIO_SHARE))
    t['C_pre'] = C.predict_rate(res, sc, C.MODELS['M1'])
    t['index_pre'] = t.L_pre * t.C_pre

    bs = r[r.F == 2019].copy()
    bs['homes'] = bs[TARGET] * bs.dwellings / 1000
    has_row = set(bs.region_id)
    got = bs.dropna(subset=[TARGET]).groupby('region_id').homes.sum()
    missing = set(bs[bs[TARGET].isna()].region_id) - set(got.index)
    t = t[~t.region_id.isin(missing)].copy()
    t['bs_homes'] = [got.get(k, 0.0) for k in t.region_id]
    t['bs_per_1000'] = t.bs_homes / t.dwellings_mb * 1000
    pos = (t.bs_per_1000 >= 1.0).to_numpy()
    out = dict(councils=int(len(t)), dropped_no_figure=sorted(missing), positives=int(pos.sum()),
               n_pre_fires_5pct=int(t.had_5pct_pre.sum()), pre_rows_for_M1=int(len(d)),
               M1_pre_params={k: float(v) for k, v in res.params.items()})
    for c in ('index_pre', 'H', 'E2', 'L_pre', 'C_pre'):
        a = auc(t[c].to_numpy(), pos)
        lo, hi = boot_auc(t[c].to_numpy(), pos)
        out[f'AUC_{c}'] = [float(a), float(lo), float(hi)]
        out[f'spearman_{c}_vs_bs_per_1000'] = float(spearmanr(t[c], t.bs_per_1000)[0])
    top = t.sort_values('index_pre', ascending=False).head(20)
    out['top20_that_lost_homes'] = int((top.bs_per_1000 >= 1).sum())
    out['losers_in_top20'] = f"{int((top.bs_per_1000 >= 1).sum())} of {int(pos.sum())}"
    big = bs[bs.share >= 0.05].dropna(subset=[TARGET]).merge(t[['region_id', 'C_pre']], on='region_id', how='left')
    out['bs_councils_ge5pct_with_figure'] = int(len(big))
    out['consequence_spearman_E2_given_ge5pct'] = float(spearmanr(big.E2_raw, big[TARGET])[0])
    out['consequence_spearman_Cpre_given_ge5pct'] = float(spearmanr(big.C_pre, big[TARGET])[0])
    n, e, lo, hi = B.boot_rho(big.E2_raw, big[TARGET], big.region_id, rng)
    out['consequence_E2_ci'] = [float(e), float(lo), float(hi)]
    n, e, lo, hi = B.boot_rho(big.share, big[TARGET], big.region_id, rng)
    out['share_spearman_given_ge5pct'] = [float(e), float(lo), float(hi)]
    json.dump(out, open(OUT / 'DAY2B_PROSPECTIVE.json', 'w'), indent=2)
    t.sort_values('index_pre', ascending=False)[['region_id', 'region_name', 'H', 'E2_raw', 'L_pre', 'C_pre', 'index_pre',
                                                 'bs_homes', 'bs_per_1000']].to_csv(OUT / 'DAY2B_COUNCILS.csv', index=False)
    print(json.dumps(out, indent=1))
    print(top[['region_name', 'index_pre', 'bs_homes', 'bs_per_1000']].round(2).to_string())
    lost = t[pos].sort_values('bs_per_1000', ascending=False)
    lost['rank_index_pre'] = t.index_pre.rank(ascending=False)[lost.index]
    print(lost[['region_name', 'bs_homes', 'bs_per_1000', 'rank_index_pre']].round(1).to_string())


if __name__ == '__main__':
    main()
