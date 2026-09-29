"""Power check for Experiment 6.

Question: if a council-block effect of a known size existed, would our data and our test detect it?

X side: REAL. The same 218 council x fire rows with their real pre-fire block scores (H, E, V, F).
Y side: FAKE. Real Y is shuffled between councils inside a stratum: Black Summer rows among themselves,
all other rows among rows of the same start year. That keeps Y's real distribution and its
Black Summer / year clustering but destroys any link to X. (A first version shuffled within each
fire only; most non-Black-Summer fires hit one council, so those rows kept their real Y and leaked the
real V-Y link: false alarms of 9-50% at rho = 0. Do not use that version.)
Then a known effect is planted:  Y* = sqrt(1 - rho^2) * z(shuffled Y) + rho * z(target block).
Test: the same one used on the real data, Spearman with a council-cluster bootstrap; "detected" =
the 95% interval excludes 0 with the planted sign.
Subsets (as in the real analysis): all rows; fires burning >= 5% of the council; the same excluding Black Summer.
rho = 0 is the false-alarm check (should be near 5%).

Run: python3 power_check.py   (writes results/POWER_CHECK.csv)
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
SEED = 20260930
N_SIM = 300
N_BOOT = 200
RHOS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
TARGETS = ['F', 'V']
BLACK_SUMMER = '871'


def z(a):
    return (a - a.mean()) / a.std()


def spearman_fast(x, y):
    return np.corrcoef(rankdata(x), rankdata(y))[0, 1]


def detects(x, y, clusters, rng):
    """cluster bootstrap CI for Spearman; returns (rho_hat, lo, hi)."""
    est = spearman_fast(x, y)
    keys, inv = np.unique(clusters, return_inverse=True)
    members = [np.flatnonzero(inv == k) for k in range(len(keys))]
    if len(keys) < 4:
        return est, np.nan, np.nan
    bs = []
    for _ in range(N_BOOT):
        pick = rng.integers(0, len(keys), len(keys))
        idx = np.concatenate([members[i] for i in pick])
        if np.unique(x[idx]).size > 2 and np.unique(y[idx]).size > 2:
            bs.append(spearman_fast(x[idx], y[idx]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, lo, hi


def main():
    rng = np.random.default_rng(SEED)
    d = pd.read_csv(OUT / 'ROWS_WITH_SCORE.csv').dropna(subset=['Y']).reset_index(drop=True)
    d['agrn'] = d.agrn.astype(str)
    d['year'] = pd.to_datetime(d.first_fire_start).dt.year if 'first_fire_start' in d else d.year
    stratum = np.where(d.agrn == BLACK_SUMMER, 'BS', d.year.astype(str))
    fire_groups = [np.flatnonzero(stratum == k) for k in np.unique(stratum)]
    subsets = {
        'all rows': np.ones(len(d), bool),
        'fires >= 5% burned': (d.share >= 0.05).to_numpy(),
        '>= 5% excl. Black Summer': ((d.share >= 0.05) & (d.agrn != BLACK_SUMMER)).to_numpy(),
    }
    print({k: int(v.sum()) for k, v in subsets.items()}, flush=True)
    Y0 = d.Y.to_numpy()
    rows = []
    t0 = time.time()
    for tgt in TARGETS:
        zt = z(d[tgt].to_numpy())
        for rho in RHOS:
            hits = {s: [] for s in subsets}
            est = {s: [] for s in subsets}
            for sim in range(N_SIM):
                shuffled = Y0.copy()
                for g in fire_groups:                       # permute Y within stratum
                    shuffled[g] = Y0[rng.permutation(g)]
                y = np.sqrt(1 - rho ** 2) * z(shuffled) + rho * zt
                for s, m in subsets.items():
                    e, lo, hi = detects(zt[m], y[m], d.region_id.to_numpy()[m], rng)
                    est[s].append(e)
                    hits[s].append(bool(lo > 0))            # planted sign is positive
            for s in subsets:
                rows.append(dict(planted_on=tgt, planted_rho=rho, subset=s, rows=int(subsets[s].sum()),
                                 power_pct=100 * np.mean(hits[s]), mean_estimated_rho=np.mean(est[s]),
                                 sims=N_SIM))
            print(tgt, rho, {s: round(rows[-3 + i]['power_pct']) for i, s in enumerate(subsets)},
                  round(time.time() - t0), 's', flush=True)
    pd.DataFrame(rows).to_csv(OUT / 'POWER_CHECK.csv', index=False)


if __name__ == '__main__':
    main()
