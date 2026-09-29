"""Step 3: run the FROZEN test once (PRESPEC.md sections 6, 6.1, 6.2; Amendment 1).

Refuses to run if PRESPEC.md, its amendment, or the X-side files no longer match their lock files, or if a frozen output already exists.
`--fake-y` runs the same code on random Y purely to test the code (writes to results/dryrun_fake_y/, never to the frozen output).

Rows: burned share >= 1% (all rows in results/Y_indicators_new_rows.csv), with a score and (for the primary test) a Y_new from >= 1 pillar.
Statistic: Spearman rho; council-cluster bootstrap (5,000 draws, percentile 95% CI, seed 20261001). Power check: seed 20261002.
Verdict rule (pooled primary interval [lo, hi]): REPLICATED if lo > 0; NOT REPLICATED if hi < 0.30; otherwise CANNOT TELL.

Run: python3 run_frozen_test.py
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
SEED_BOOT, SEED_POWER = 20261001, 20261002
N_BOOT, N_SIM, N_BOOT_SIM = 5000, 1000, 500
REPL_UPPER = 0.30
RHOS = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify_locks():
    lock = (HERE / 'PRESPEC.lock').read_text()
    assert sha(HERE / 'PRESPEC.md') in lock, 'PRESPEC.md changed since it was locked'
    am = HERE / 'PRESPEC_AMENDMENT_1.md'
    assert sha(am) in (HERE / 'PRESPEC_AMENDMENT_1.lock').read_text(), 'Amendment 1 changed since it was locked'
    sl = (HERE / 'SCORES.lock').read_text()
    for line in sl.splitlines():
        if ' sha256: ' in line:
            f, h = line.split(' sha256: ')
            assert sha(HERE / f) == h.strip(), f'{f} changed since SCORES.lock'
    yl = HERE / 'Y.lock'
    if not FAKE:
        assert yl.exists(), 'Y.lock missing: lock the Y inputs before the frozen run'
        for line in yl.read_text().splitlines():
            if ' sha256: ' in line:
                f, h = line.split(' sha256: ')
                assert f == 'run_frozen_test.py' or sha(HERE / f) == h.strip(), f'{f} changed since Y.lock'
    # further amendments (if any) must have their own lock
    for a in sorted(HERE.glob('PRESPEC_AMENDMENT_*.md')):
        assert a.with_suffix('.lock').exists() and sha(a) in a.with_suffix('.lock').read_text(), f'{a.name} not locked'
    return sorted(p.name for p in HERE.glob('PRESPEC*.lock')) + ['SCORES.lock', 'Y.lock']


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


def main():
    locks = verify_locks()
    if OUT.exists() and not FAKE:
        sys.exit(f'{OUT} exists: the frozen test has already been run. Changes need a dated amendment; earlier output is kept.')
    OUT.mkdir(parents=True, exist_ok=True)
    D = pd.read_csv(RES / 'Y_indicators_new_rows.csv', dtype={'region_id': str})
    D['is_vic'] = D.event.str.startswith('VIC')
    if FAKE:
        rng0 = np.random.default_rng(1)
        for c in ('Y_new', 'DL', 'IL', 'FP', 'Y_new_ge2pillars', 'Y_new_noFP', 'DL_reported_only', 'Y_new_vic_IL_biz_only'):
            D[c] = rng0.random(len(D))
        print('FAKE Y: code test only')
    D = D[D.risk_add_avail.notna()].copy()
    rng = np.random.default_rng(SEED_BOOT)

    def T(tid, scope, sub, score, target, note=''):
        n, est, lo, hi = boot(sub[score], sub[target], sub.region_id, rng)
        return dict(test=tid, scope=scope, score=score, target=target, n=n, spearman=est, ci_low=lo, ci_high=hi, note=note)

    scopes = {'pooled': D, 'NSW_2013': D[~D.is_vic], 'VIC_2009': D[D.is_vic]}
    res = []
    for sc, sub in scopes.items():                                # primary + per-event + DL-only + pillars
        res.append(T('PRIMARY' if sc == 'pooled' else 'primary_by_event', sc, sub, 'risk_add_avail', 'Y_new'))
        res.append(T('DL_only', sc, sub, 'risk_add_avail', 'DL'))
        for p in ('IL', 'FP'):
            res.append(T('pillar', sc, sub, 'risk_add_avail', p))
    for sc, sub in scopes.items():                                # secondary scores
        res.append(T('secondary_S1_V', sc, sub, 'S1_V', 'Y_new'))
        res.append(T('secondary_S1_V_DL', sc, sub, 'S1_V', 'DL'))
        if sc != 'VIC_2009':
            res.append(T('secondary_S2_HV', sc, sub, 'S2_HV', 'Y_new'))
    big = D.share_burned >= 0.05                                  # descriptive sensitivities
    for sc, sub in scopes.items():
        sb = sub[sub.share_burned >= 0.05]
        res.append(T('sens_a_share_ge5pct', sc, sb, 'risk_add_avail', 'Y_new', 'descriptive'))
        res.append(T('sens_a_share_ge5pct_S1_V', sc, sb, 'S1_V', 'Y_new', 'descriptive'))
        res.append(T('sens_b_ge2_pillars', sc, sub, 'risk_add_avail', 'Y_new_ge2pillars', 'descriptive'))
        res.append(T('sens_c_no_FP', sc, sub, 'risk_add_avail', 'Y_new_noFP', 'descriptive'))
        res.append(T('sens_d_DL_reported_only', sc, sub, 'risk_add_avail', 'DL_reported_only', 'descriptive'))
        if sc != 'NSW_2013':
            res.append(T('sens_f_vic_IL_biz_only', sc, sub, 'risk_add_avail', 'Y_new_vic_IL_biz_only', 'descriptive'))
    R = pd.DataFrame(res)
    R.to_csv(OUT / 'TEST_RESULTS.csv', index=False)

    prim = R[(R.test == 'PRIMARY')].iloc[0]
    lo, hi, est = prim.ci_low, prim.ci_high, prim.spearman
    if np.isnan(lo):
        verdict = 'CANNOT TELL (primary interval not estimable)'
    elif lo > 0:
        verdict = 'REPLICATED'
    elif hi < REPL_UPPER:
        verdict = 'NOT REPLICATED'
    else:
        verdict = 'CANNOT TELL'
    ev = R[R.test == 'primary_by_event'].set_index('scope').spearman.to_dict()
    json.dump(dict(fake_y=FAKE, verdict=verdict, primary=dict(n=int(prim.n), spearman=est, ci_low=lo, ci_high=hi), per_event_estimates=ev,
                   locks_verified=locks, rows_in_analysis=int(len(D)), rows_with_y=int(D.Y_new.notna().sum()),
                   rows_by_event=D.groupby('event').size().to_dict(), rule='REPLICATED lo>0; NOT REPLICATED hi<0.30; else CANNOT TELL'),
              open(OUT / 'VERDICT.json', 'w'), indent=1, default=str)
    print(R.round(3).to_string())
    print('VERDICT:', verdict)

    # ---- planted-effect power check (uses no real Y): rows that enter the primary test
    rngp = np.random.default_rng(SEED_POWER)
    P = D[D.Y_new.notna()]
    rows = power_table(P.risk_add_avail.to_numpy(float), 'pooled primary rows', rngp)
    rows += power_table(P[P.share_burned >= 0.05].risk_add_avail.to_numpy(float), 'rows with share >= 5%', rngp)
    for nm, g in P.groupby('is_vic'):
        rows += power_table(g.risk_add_avail.to_numpy(float), 'VIC rows' if nm else 'NSW rows', rngp)
    pd.DataFrame(rows).to_csv(OUT / 'POWER_CHECK.csv', index=False)
    print(pd.DataFrame(rows).round(3).to_string())


if __name__ == '__main__':
    main()
