"""Step 3 (SA fires): run the FROZEN test once (PRESPEC.md sections 6, 6.1, 6.2; Amendment 1).

Refuses to run if PRESPEC.md, its amendment(s), the X-side files or the Y-side files no longer match their lock files, or if a frozen output exists.
`--fake-y` runs the same code on random Y purely to test the code (writes to results/dryrun_fake_y/, never to the frozen output).

Rows: burned share >= 1%, with a score (risk_add_avail) and (primary) a Y_new from >= 1 pillar.
  SA rows      = results/Y_indicators_new_rows.csv (this round)
  earlier rows = inputs/stage1_extra_fire_rows.csv (frozen stage-1 outcomes of the previous round: NSW Oct 2013 and Victoria 2009; 26 scored rows)
Statistic: Spearman rho; council-cluster bootstrap (clusters = ABS LGA code), 5,000 draws, percentile 95% CI, seed 20261101. Power check: seed 20261102.
Verdict rule (pooled primary interval [lo, hi]): REPLICATED if lo > 0; NOT REPLICATED if hi < 0.30; otherwise CANNOT TELL.

Run: python3 run_frozen_test.py     (anaconda python with scipy)
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

HERE = Path(__file__).resolve().parent
RES = HERE / 'results'
FAKE = '--fake-y' in sys.argv
OUT = RES / ('dryrun_fake_y' if FAKE else 'frozen_test')
SEED_BOOT, SEED_POWER = 20261101, 20261102
N_BOOT, N_SIM, N_BOOT_SIM = 5000, 1000, 500
REPL_UPPER = 0.30
RHOS = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
SA2019 = ['SA_2019_cudlee_creek', 'SA_2019_20_kangaroo_island', 'SA_2019_20_keilira']
SA2015 = ['SA_2015_sampson_flat', 'SA_2015_pinery']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify_locks():
    lock = (HERE / 'PRESPEC.lock').read_text()
    assert sha(HERE / 'PRESPEC.md') in lock, 'PRESPEC.md changed since it was locked'
    for line in lock.splitlines():                       # inputs/ files (incl. the frozen stage-1 rows) hashed at lock time
        if line.startswith('inputs/') and ' sha256: ' in line:
            f, h = line.split(' sha256: ')
            assert sha(HERE / f) == h.strip(), f'{f} changed since PRESPEC.lock'
    for a in sorted(HERE.glob('PRESPEC_AMENDMENT_*.md')):
        assert a.with_suffix('.lock').exists() and sha(a) in a.with_suffix('.lock').read_text(), f'{a.name} not locked / changed'
    for line in (HERE / 'SCORES.lock').read_text().splitlines():
        if ' sha256: ' in line:
            f, h = line.split(' sha256: ')
            assert sha(HERE / f) == h.strip(), f'{f} changed since SCORES.lock'
    if not FAKE:
        yl = HERE / 'Y.lock'
        assert yl.exists(), 'Y.lock missing: lock the Y inputs before the frozen run'
        for line in yl.read_text().splitlines():
            if ' sha256: ' in line:
                f, h = line.split(' sha256: ')
                assert f == 'run_frozen_test.py' or sha(HERE / f) == h.strip(), f'{f} changed since Y.lock'
    return sorted(p.name for p in HERE.glob('*.lock'))


def boot(x, y, groups, rng, n=N_BOOT):
    d = pd.DataFrame({'x': x, 'y': y, 'g': groups}).dropna()
    if len(d) < 6 or d.x.nunique() < 3 or d.y.nunique() < 3:
        return len(d), np.nan, np.nan, np.nan
    est = spearmanr(d.x, d.y)[0]
    gs = {g: sub[['x', 'y']].to_numpy() for g, sub in d.groupby('g')}
    keys = list(gs)
    if len(keys) < 6:
        return len(d), est, np.nan, np.nan
    bs = []
    for _ in range(n):
        pick = rng.choice(len(keys), len(keys))
        a = np.vstack([gs[keys[i]] for i in pick])
        if np.unique(a[:, 0]).size > 2 and np.unique(a[:, 1]).size > 2:
            bs.append(spearmanr(a[:, 0], a[:, 1])[0])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return len(d), float(est), float(lo), float(hi)


def fast_boot_ci(x, y, rng, n=N_BOOT_SIM):
    """Row bootstrap (each council once): vectorised Spearman over resamples, percentile CI."""
    m = len(x)
    idx = rng.integers(0, m, size=(n, m))
    xr, yr = rankdata(x[idx], axis=1), rankdata(y[idx], axis=1)
    xr -= xr.mean(axis=1, keepdims=True)
    yr -= yr.mean(axis=1, keepdims=True)
    den = np.sqrt((xr ** 2).sum(axis=1) * (yr ** 2).sum(axis=1))
    ok = den > 0
    r = (xr * yr).sum(axis=1)[ok] / den[ok]
    return np.percentile(r, [2.5, 97.5])


def power_table(x, label, rng):
    rows = []
    zx = (rankdata(x) - rankdata(x).mean()) / rankdata(x).std()
    for rho in RHOS:
        lo_pos = hi_low = 0
        for _ in range(N_SIM):
            y = rho * zx + np.sqrt(1 - rho ** 2) * rng.standard_normal(len(x))
            lo, hi = fast_boot_ci(x, y, rng)
            lo_pos += lo > 0
            hi_low += hi < REPL_UPPER
        rows.append(dict(rows_set=label, n=len(x), planted_rho=rho, power_lo_gt0=lo_pos / N_SIM, chance_hi_lt_030=hi_low / N_SIM))
    return rows


def load_rows():
    sa = pd.read_csv(RES / 'Y_indicators_new_rows.csv', dtype={'region_id': str})
    sa['group'] = np.where(sa.event.isin(SA2019), 'SA_2019_20', 'SA_2015')
    s1 = pd.read_csv(HERE / 'inputs/stage1_extra_fire_rows.csv', dtype={'region_id': str})
    s1['group'] = 'STAGE1'
    for c in ('DL', 'IL', 'FP', 'SL'):
        s1[c] = pd.to_numeric(s1[c], errors='coerce')
    s1['Y_new_ge2pillars'] = s1.Y_new.where(s1.pillars_n >= 2)
    s1['Y_new_noFP'] = s1[['DL', 'IL', 'SL']].mean(axis=1, skipna=True).where(s1[['DL', 'IL', 'SL']].notna().sum(axis=1) >= 1)
    s1['DL_reported_only'] = s1.DL.where(s1.flag_DL == 'reported')
    cols = ['group', 'event', 'region_id', 'region_name', 'share_burned', 'H', 'E', 'V', 'F', 'blocks_n', 'risk_add_avail', 'S1_V', 'S2_HV',
            'DL', 'IL', 'FP', 'SL', 'pillars_n', 'Y_new', 'Y_new_ge2pillars', 'Y_new_noFP', 'DL_reported_only']
    D = pd.concat([s1[cols], sa[cols]], ignore_index=True)
    return D


def main():
    locks = verify_locks()
    if OUT.exists() and not FAKE:
        sys.exit(f'{OUT} exists: the frozen test has already been run. Changes need a dated amendment; earlier output is kept.')
    OUT.mkdir(parents=True, exist_ok=True)
    D = load_rows()
    if FAKE:
        rng0 = np.random.default_rng(1)
        for c in ('Y_new', 'DL', 'IL', 'FP', 'SL', 'Y_new_ge2pillars', 'Y_new_noFP', 'DL_reported_only'):
            D[c] = rng0.random(len(D))
        print('FAKE Y: code test only')
    D = D[D.risk_add_avail.notna()].copy()
    rng = np.random.default_rng(SEED_BOOT)

    def T(tid, scope, sub, score, target, note=''):
        n, est, lo, hi = boot(sub[score], sub[target], sub.region_id, rng)
        return dict(test=tid, scope=scope, score=score, target=target, n=n, spearman=est, ci_low=lo, ci_high=hi, note=note)

    pooled = D
    sa = D[D.group != 'STAGE1']
    scopes = {'pooled': pooled, 'SA_all': sa, 'stage1_only(reproduction check)': D[D.group == 'STAGE1'],
              'pooled_without_SA_2019_20': D[D.group != 'SA_2019_20'], 'SA_2015_events_only': D[D.group == 'SA_2015']}
    for ev in SA2015 + SA2019:
        scopes[f'event:{ev}'] = D[D.event == ev]
    res = []
    for sc, sub in scopes.items():                                         # primary test in every scope
        res.append(T('PRIMARY' if sc == 'pooled' else 'primary_other_scope', sc, sub, 'risk_add_avail', 'Y_new'))
    for sc in ('pooled', 'SA_all', 'pooled_without_SA_2019_20', 'SA_2015_events_only'):    # pillars, secondary scores
        sub = scopes[sc]
        for p in ('DL', 'IL', 'FP', 'SL'):
            res.append(T('pillar', sc, sub, 'risk_add_avail', p))
        res.append(T('secondary_S1_V', sc, sub, 'S1_V', 'Y_new'))
        res.append(T('secondary_S2_HV', sc, sub, 'S2_HV', 'Y_new'))
        res.append(T('secondary_S1_V_DL', sc, sub, 'S1_V', 'DL'))
    for sc in ('pooled', 'SA_all', 'pooled_without_SA_2019_20'):           # descriptive sensitivities
        sub = scopes[sc]
        sb = sub[sub.share_burned >= 0.05]
        res.append(T('sens_a_share_ge5pct', sc, sb, 'risk_add_avail', 'Y_new', 'descriptive'))
        res.append(T('sens_a_share_ge5pct_S1_V', sc, sb, 'S1_V', 'Y_new', 'descriptive'))
        res.append(T('sens_b_ge2_pillars', sc, sub, 'risk_add_avail', 'Y_new_ge2pillars', 'descriptive'))
        res.append(T('sens_c_no_FP', sc, sub, 'risk_add_avail', 'Y_new_noFP', 'descriptive'))
        res.append(T('sens_d_DL_reported_only', sc, sub, 'risk_add_avail', 'DL_reported_only', 'descriptive'))
    for ev in SA2015 + SA2019:                                             # (f) leave one SA event out of the pooled set
        res.append(T('sens_f_leave_out', f'pooled minus {ev}', D[D.event != ev], 'risk_add_avail', 'Y_new', 'descriptive'))
    R = pd.DataFrame(res)
    R.to_csv(OUT / 'TEST_RESULTS.csv', index=False)

    prim = R[R.test == 'PRIMARY'].iloc[0]
    lo, hi, est = prim.ci_low, prim.ci_high, prim.spearman
    if np.isnan(lo):
        verdict = 'CANNOT TELL (primary interval not estimable)'
    elif lo > 0:
        verdict = 'REPLICATED'
    elif hi < REPL_UPPER:
        verdict = 'NOT REPLICATED'
    else:
        verdict = 'CANNOT TELL'
    sa_row = R[(R.test == 'primary_other_scope') & (R.scope == 'SA_all')].iloc[0]
    json.dump(dict(fake_y=FAKE, verdict=verdict, primary=dict(n=int(prim.n), spearman=est, ci_low=lo, ci_high=hi),
                   sa_alone=dict(n=int(sa_row.n), spearman=sa_row.spearman, ci_low=sa_row.ci_low, ci_high=sa_row.ci_high),
                   locks_verified=locks, rows_in_analysis=int(len(D)), rows_with_y=int(D.Y_new.notna().sum()),
                   rows_by_event=D.groupby('event').size().to_dict(), rule='REPLICATED lo>0; NOT REPLICATED hi<0.30; else CANNOT TELL'),
              open(OUT / 'VERDICT.json', 'w'), indent=1, default=str)
    print(R.round(3).to_string())
    print('VERDICT:', verdict)

    # ---- planted-effect power check (uses no real Y): rows that enter the primary test
    rngp = np.random.default_rng(SEED_POWER)
    P = D[D.Y_new.notna()]
    rows = power_table(P.risk_add_avail.to_numpy(float), 'pooled primary rows', rngp)
    rows += power_table(P[P.group != 'STAGE1'].risk_add_avail.to_numpy(float), 'SA rows', rngp)
    rows += power_table(P[P.group != 'SA_2019_20'].risk_add_avail.to_numpy(float), 'pooled without SA 2019-20', rngp)
    pt = pd.DataFrame(rows)
    pt.to_csv(OUT / 'POWER_CHECK.csv', index=False)
    print(pt.round(3).to_string())

    # ---- rows still needed (Fisher approximation, 80% power, two-sided 5% lower-bound test)
    n_now = int(len(P))
    need = []
    for rho in (0.3, 0.4, 0.5):
        n_req = int(np.ceil(((1.96 + 0.8416) / np.arctanh(rho)) ** 2 + 3))
        need.append(dict(true_rho=rho, rows_needed_for_80pct_power=n_req, pooled_rows_now=n_now, further_rows_needed=max(0, n_req - n_now)))
    nd = pd.DataFrame(need)
    nd.to_csv(OUT / 'ROWS_NEEDED.csv', index=False)
    print(nd.to_string())


if __name__ == '__main__':
    main()
