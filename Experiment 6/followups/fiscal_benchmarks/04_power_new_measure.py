"""Step 4: power of the benchmark measure test (same design as Experiment 6/power_check.py, X = stress_bench).

Run after 03_validate_vs_Y.py; it does not change the measure or the tests, it only says how much a null can be trusted.
X: the real stress_bench of the rows that have it, RANKED WITHIN EACH FIRE FINANCIAL YEAR. (A first run with the raw
stress_bench gave 9% false alarms at rho 0 and 53% 'power' at rho 0.1, because the new measure drifts with the fire year
(Spearman +0.11) and the year-stratified Y shuffle keeps Y's year drift (+0.32): a year confound, not power. The partial
log of that run is kept in power_new_measure_raw_x_partial.log. The old static F had no year drift, so its earlier
power table did not have this problem.) Y: real Y shuffled between councils inside a stratum (Black Summer
rows among themselves, other rows within the same start year), then a correlation rho with z(stress_bench) is planted.
'Detected' = the 95% cluster-bootstrap interval lies above 0. 300 simulations, 200 bootstrap draws per test.
Writes POWER_NEW_MEASURE.csv.
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
ROWS = Path('/Users/ray/Research/AUSSEF - Local/Experiment 6/results/ROWS_WITH_SCORE_v2.csv')
SEED = 20260930
N_SIM = 300
N_BOOT = 200
RHOS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
BS = '871'


def z(a):
    return (a - a.mean()) / a.std()


def sp(x, y):
    return np.corrcoef(rankdata(x), rankdata(y))[0, 1]


def lo_bound(x, y, clusters, rng):
    keys, inv = np.unique(clusters, return_inverse=True)
    members = [np.flatnonzero(inv == k) for k in range(len(keys))]
    bs = []
    for _ in range(N_BOOT):
        pick = rng.integers(0, len(keys), len(keys))
        idx = np.concatenate([members[i] for i in pick])
        if np.unique(x[idx]).size > 2 and np.unique(y[idx]).size > 2:
            bs.append(sp(x[idx], y[idx]))
    return sp(x, y), np.percentile(bs, 2.5)


def main():
    rng = np.random.default_rng(SEED)
    meas = pd.read_csv(HERE / 'BENCHMARK_MEASURE_ROWS.csv', dtype={'agrn': str})[['agrn', 'region_id', 'stress_bench', 'fire_fy_start']]
    d = pd.read_csv(ROWS, dtype={'agrn': str}).merge(meas, on=['agrn', 'region_id']).dropna(subset=['Y', 'stress_bench'])
    d['stress_bench'] = d.groupby('fire_fy_start').stress_bench.rank(pct=True)
    d = d.reset_index(drop=True)
    stratum = np.where(d.agrn == BS, 'BS', d.year.astype(str))
    groups = [np.flatnonzero(stratum == k) for k in np.unique(stratum)]
    subsets = {'all rows': np.ones(len(d), bool), 'fires >= 5% burned': (d.share >= 0.05).to_numpy(),
               'all rows excl. Black Summer': (d.agrn != BS).to_numpy(),
               '>= 5% excl. Black Summer': ((d.share >= 0.05) & (d.agrn != BS)).to_numpy()}
    print({k: int(v.sum()) for k, v in subsets.items()}, flush=True)
    zt = z(d.stress_bench.to_numpy())
    Y0 = d.Y.to_numpy()
    cl = d.region_id.to_numpy()
    rows, t0 = [], time.time()
    for rho in RHOS:
        hits = {s: [] for s in subsets}
        est = {s: [] for s in subsets}
        for _ in range(N_SIM):
            sh = Y0.copy()
            for g in groups:
                sh[g] = Y0[rng.permutation(g)]
            y = np.sqrt(1 - rho ** 2) * z(sh) + rho * zt
            for s, m in subsets.items():
                if m.sum() < 8:
                    continue
                e, lo = lo_bound(zt[m], y[m], cl[m], rng)
                est[s].append(e)
                hits[s].append(bool(lo > 0))
        for s in subsets:
            if hits[s]:
                rows.append(dict(planted_rho=rho, subset=s, rows=int(subsets[s].sum()),
                                 power_pct=100 * np.mean(hits[s]), mean_estimated_rho=np.mean(est[s]), sims=N_SIM))
        print(rho, {r['subset']: round(r['power_pct']) for r in rows if r['planted_rho'] == rho}, round(time.time() - t0),
              's', flush=True)
    pd.DataFrame(rows).to_csv(HERE / 'POWER_NEW_MEASURE.csv', index=False)


if __name__ == '__main__':
    main()
