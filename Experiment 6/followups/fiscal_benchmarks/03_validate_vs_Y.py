"""Step 3: test the pre-fixed benchmark measure against Y, DL, IL, FP, SL. Run ONLY after 01 and 02* are on disk.

PRE-SPECIFIED (2026-09-29, before this script was first run; see bench_common.py for the measure):
  * PRIMARY score  = stress_bench = 1 - bench_share (higher = weaker finances). Hypothesis: Spearman(stress_bench,
    impact) > 0, same sign convention as the old F block. Two-sided 95% CI reported.
  * Secondary (reported, none used to pick a winner): stress_years, stress_avg3, stress_fin5, stress_infra3, F_tm.
  * Comparator: old F block (static 2014/15 snapshot, from ROWS_WITH_SCORE_v2.csv), evaluated on the SAME rows.
  * Targets: Y, DL, IL, FP, SL.  Subsets: all rows with the measure; fires burning >= 5% of the council
    (X_fire_share_of_council_burned >= 0.05); each also excluding Black Summer (AGRN 871); Black Summer only as a reference.
  * Spearman with a council-cluster bootstrap (2,000 draws, seed 20260929, same routine as build_and_validate_score.py).
    The difference (new - old F) uses the same bootstrap draws.
  * 5 targets x 4 subsets x 1 primary score = 20 headline cells, no multiplicity adjustment: read a lone CI that
    just clears 0 with caution.
Writes VALIDATION_VS_Y.csv and VALIDATION_VS_Y.txt.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

HERE = Path(__file__).resolve().parent
ROWS = Path('/Users/ray/Research/AUSSEF - Local/Experiment 6/results/ROWS_WITH_SCORE_v2.csv')
SEED = 20260929
N_BOOT = 2000
TARGETS = ['Y', 'DL', 'IL', 'FP', 'SL']
NEW = ['stress_bench', 'stress_years', 'stress_avg3', 'stress_fin5', 'stress_infra3', 'F_tm']
SCORES = NEW + ['F_old']
BS = '871'


def rho(a, b):
    return np.corrcoef(rankdata(a), rankdata(b))[0, 1]


def cell(d, tgt, rng):
    """d: rows with all SCORES + tgt non-null. Returns {score: (rho, lo, hi)} and {score: (diff, lo, hi)} vs F_old."""
    est = {s: spearmanr(d[s], d[tgt])[0] for s in SCORES}
    keys = list(d.region_id.unique())
    grp = {k: d.loc[d.region_id == k, SCORES + [tgt]].to_numpy() for k in keys}
    bs = {s: [] for s in SCORES}
    diff = {s: [] for s in NEW}
    for _ in range(N_BOOT):
        pick = rng.choice(len(keys), len(keys))
        a = np.vstack([grp[keys[i]] for i in pick])
        if len(np.unique(a[:, -1])) <= 2:
            continue
        ok = True
        r = {}
        for j, s in enumerate(SCORES):
            if len(np.unique(a[:, j])) <= 2:
                ok = False
                break
            r[s] = rho(a[:, j], a[:, -1])
        if not ok:
            continue
        for s in SCORES:
            bs[s].append(r[s])
        for s in NEW:
            diff[s].append(r[s] - r['F_old'])
    ci = {s: tuple(np.percentile(bs[s], [2.5, 97.5])) if len(bs[s]) > 50 else (np.nan, np.nan) for s in SCORES}
    dci = {s: (est[s] - est['F_old'],) + (tuple(np.percentile(diff[s], [2.5, 97.5])) if len(diff[s]) > 50 else (np.nan, np.nan))
           for s in NEW}
    return est, ci, dci, len(bs['stress_bench'])


def main():
    rng = np.random.default_rng(SEED)
    meas = pd.read_csv(HERE / 'BENCHMARK_MEASURE_ROWS.csv', dtype={'agrn': str})
    rows = pd.read_csv(ROWS, dtype={'agrn': str}).rename(columns={'F': 'F_old'})
    assert not rows.duplicated(['agrn', 'region_id']).any() and not meas.duplicated(['agrn', 'region_id']).any()
    d0 = rows.merge(meas[['agrn', 'region_id', 'fire_fy_start', 'years_usable'] + NEW + ['bench_share', 'bench_n_met_of8']],
                    on=['agrn', 'region_id'], how='left')
    assert len(d0) == len(rows) == 218
    d0 = d0.dropna(subset=SCORES).copy()
    print('rows with the new measure and F_old:', len(d0), 'of', len(rows))
    subsets = {
        'all rows': np.ones(len(d0), bool),
        'fires >= 5% burned': (d0.share >= 0.05).to_numpy(),
        'all rows excl. Black Summer': (d0.agrn != BS).to_numpy(),
        '>= 5% burned excl. Black Summer': ((d0.share >= 0.05) & (d0.agrn != BS)).to_numpy(),
        'Black Summer only (reference)': (d0.agrn == BS).to_numpy(),
    }
    out = []
    for sname, mask in subsets.items():
        sub = d0[mask]
        for tgt in TARGETS:
            dd = sub.dropna(subset=[tgt])
            if len(dd) < 8:
                continue
            est, ci, dci, nb = cell(dd, tgt, rng)
            for s in SCORES:
                r = dict(subset=sname, target=tgt, n=len(dd), councils=int(dd.region_id.nunique()),
                         fires=int(dd.agrn.nunique()), score=s, spearman=est[s], ci_low=ci[s][0], ci_high=ci[s][1],
                         boot_draws=nb)
                if s in dci:
                    r.update(diff_vs_F_old=dci[s][0], diff_low=dci[s][1], diff_high=dci[s][2])
                out.append(r)
        print('done', sname, flush=True)
    val = pd.DataFrame(out)
    val.to_csv(HERE / 'VALIDATION_VS_Y.csv', index=False)

    lines = []
    fmt = lambda r: f'{r.spearman:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}]'
    for sc in ['stress_bench', 'F_old', 'F_tm']:
        lines.append(f'\n=== {sc}: Spearman with impact (95% cluster-bootstrap CI); n in brackets')
        t = val[val.score == sc]
        tab = t.pivot_table(index='subset', columns='target', values='spearman', aggfunc='first')
        for sname in subsets:
            cells = []
            for tgt in TARGETS:
                r = t[(t.subset == sname) & (t.target == tgt)]
                cells.append(f'{tgt} {fmt(r.iloc[0])} (n={r.iloc[0].n})' if len(r) else f'{tgt} n/a')
            lines.append(f'{sname:34s} ' + ' | '.join(cells))
    lines.append('\n=== difference stress_bench - F_old (same rows)')
    t = val[val.score == 'stress_bench']
    for sname in subsets:
        cells = []
        for tgt in TARGETS:
            r = t[(t.subset == sname) & (t.target == tgt)]
            cells.append(f'{tgt} {r.iloc[0].diff_vs_F_old:+.2f} [{r.iloc[0].diff_low:+.2f}, {r.iloc[0].diff_high:+.2f}]'
                         if len(r) else f'{tgt} n/a')
        lines.append(f'{sname:34s} ' + ' | '.join(cells))
    lines.append('\n=== overlap of the scores across the rows used (Spearman)')
    lines.append(d0[SCORES].corr('spearman').round(2).to_string())
    txt = '\n'.join(lines)
    print(txt)
    (HERE / 'VALIDATION_VS_Y.txt').write_text(txt + '\n')


if __name__ == '__main__':
    main()
