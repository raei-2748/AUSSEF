"""Step 4c: sensitivity of the before/after check.

A. Fires >= 5% burned: the one row that changes is 880 / Clarence Valley (7.9%, 82,668 ha). Its value is a lower bound (>= 9 homes,
   Bees Nest fire, three councils). Try 0, 9 (main), and 168 (the whole-season Clarence Valley figure the dataset holds for AGRN 871).
B. Excluding Black Summer (AGRN 871): the fill is 100% outside Black Summer, so this is where it can matter.
C. Multiple imputation: the estimated zeros (rules, not sources) are replaced by random draws from the homes-per-1000 rates of the KNOWN
   non-Black-Summer rows with share burned < 2% (a pool that over-represents fires with reported losses, so it leans towards more loss).
D. Ties: share of zero values in each variant (heavy ties cap how large Spearman can be).
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import E6_RESULTS, HERE, OUT
from spearman_check import N_BOOT, paired_boot

SCORES = ['risk_add', 'H', 'E', 'V']
rows = pd.read_csv(E6_RESULTS / 'ROWS_WITH_SCORE_v2.csv', dtype={'agrn': str})
f = pd.read_csv(HERE / 'DL_FILLED.csv', dtype={'agrn': str})
d = rows[['agrn', 'region_id', 'region_name', 'share'] + SCORES].merge(
    f[['agrn', 'region_id', 'year', 'dwellings', 'value', 'DL_fill_flag', 'homes_per_1000_v0_original', 'homes_per_1000_v3_estimated',
       'DL_v0_original', 'DL_v1_reported', 'DL_v2_inferred', 'DL_v3_estimated']], on=['agrn', 'region_id'], validate='1:1')
out = []


def rho(x, y):
    m = x.notna() & y.notna()
    return m.sum(), spearmanr(x[m], y[m])[0]


# ---- A. fires >= 5%: value of the 880 / Clarence Valley row
big = d[d.share >= 0.05].copy()
i = big.index[(big.agrn == '880') & (big.region_name == 'Clarence Valley')][0]
for label, homes in [('880 Clarence Valley = 0', 0.0), ('880 Clarence Valley = 9 (main, lower bound)', 9.0), ('880 Clarence Valley = 168 (whole-season council figure)', 168.0)]:
    b = big.copy()
    rate = (b.value / b.dwellings * 1000)
    rate.loc[i] = homes / b.at[i, 'dwellings'] * 1000
    b['DL_alt'] = rate.rank(pct=True)
    b['DL_orig_col'] = b.DL_v0_original
    for sc in SCORES:
        est, chg = paired_boot(b, sc, ['DL_orig_col', 'DL_alt'], n_boot=N_BOOT)
        n, r, lo, hi = est['DL_alt']
        out.append(dict(analysis='A: fires >=5%, Clarence Valley 880 value', case=label, score=sc, n_with_DL=n, rho=r, ci_low=lo, ci_high=hi,
                        change_vs_original=chg['DL_alt'][0], change_ci_low=chg['DL_alt'][1], change_ci_high=chg['DL_alt'][2]))
    # rank of the row among the 38
    print(label, '| rank pct of Clarence Valley 880 among the 38 rows:', round(float(b.at[i, 'DL_alt']), 2))

# ---- B. excluding Black Summer
nb = d[d.agrn != '871']
for sc in SCORES:
    est, chg = paired_boot(nb, sc, ['DL_v0_original', 'DL_v1_reported', 'DL_v2_inferred', 'DL_v3_estimated'], n_boot=N_BOOT)
    for v, (n, r, lo, hi) in est.items():
        c = chg.get(v, (np.nan, np.nan, np.nan))
        out.append(dict(analysis='B: excluding Black Summer', case=v, score=sc, n_with_DL=n, rho=r, ci_low=lo, ci_high=hi,
                        change_vs_original=c[0], change_ci_low=c[1], change_ci_high=c[2]))

# ---- C. multiple imputation of the estimated zeros
rng = np.random.default_rng(20260930)
pool = f[(f.DL_fill_flag == 'original_sourced') & (f.black_summer == False) & (f.share < 0.02)]
pool_rate = (pool.value / pool.dwellings * 1000).to_numpy()
print('imputation pool: n =', len(pool_rate), '| share zero =', round(float((pool_rate == 0).mean()), 2), '| mean rate =', round(float(pool_rate.mean()), 3))
est_mask = d.DL_fill_flag.isin(['estimated_zero_small_fire', 'estimated_zero_season_budget']).to_numpy()
base_rate = (d.value / d.dwellings * 1000)
draws = {sc: {'all': [], 'ge5': [], 'nobs': []} for sc in SCORES}
for _ in range(300):
    r = base_rate.copy()
    r[est_mask] = rng.choice(pool_rate, est_mask.sum())
    r = r.where(d.DL_v3_estimated.notna())
    rk = r.rank(pct=True)
    for sc in SCORES:
        draws[sc]['all'].append(rho(d[sc], rk)[1])
        draws[sc]['ge5'].append(rho(d[sc][d.share >= .05], rk[d.share >= .05])[1])
        draws[sc]['nobs'].append(rho(d[sc][d.agrn != '871'], rk[d.agrn != '871'])[1])
for sc in SCORES:
    for k, lab in [('all', 'all rows'), ('ge5', 'fires >=5%'), ('nobs', 'excluding Black Summer')]:
        a = np.array(draws[sc][k])
        out.append(dict(analysis='C: multiple imputation of estimated zeros (300 draws)', case=lab, score=sc, n_with_DL=int(d.DL_v3_estimated.notna().sum()),
                        rho=np.median(a), ci_low=np.percentile(a, 2.5), ci_high=np.percentile(a, 97.5)))

# ---- D. ties
tie = pd.DataFrame({v: [int(d[v.replace('DL_', 'DL_')].notna().sum())] for v in ['DL_v0_original', 'DL_v1_reported', 'DL_v2_inferred', 'DL_v3_estimated']}, index=['n'])
for v, hp in [('DL_v0_original', 'homes_per_1000_v0_original'), ('DL_v3_estimated', 'homes_per_1000_v3_estimated')]:
    x = f[hp].dropna()
    print(v, 'n', len(x), 'share zero', round(float((x == 0).mean()), 2), 'distinct values', x.nunique())
for v, name in [('DL_v1_reported', 'homes_per_1000_v1_reported'), ('DL_v2_inferred', 'homes_per_1000_v2_inferred')]:
    x = f[name].dropna()
    print(v, 'n', len(x), 'share zero', round(float((x == 0).mean()), 2), 'distinct values', x.nunique())

res = pd.DataFrame(out)
res.to_csv(OUT / 'SENSITIVITY.csv', index=False)
pd.set_option('display.width', 220)
res['txt'] = res.apply(lambda r: f'{r.rho:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}]', axis=1)
print(res[['analysis', 'case', 'score', 'n_with_DL', 'txt']].to_string(index=False))
