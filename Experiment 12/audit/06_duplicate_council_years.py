"""Audit check (f): several master rows can share one council and one fire year F (different AGRN fires in the same
FY). For the FY-based channels C4/C5 these rows carry the SAME outcome value but different doses. The within-season
permutation test treats them as independent. Here: count them, and recompute rho and a within-season permutation p
with one row per (council, F) (dose = max over that council's rows in F, or sum of homes in fire)."""
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
OUT = Path(__file__).resolve().parent; rng = np.random.default_rng(7)
m = pd.read_csv(OUT / 'rederived_c4_c5_rows.csv', dtype={'agrn': str, 'region_id': str})
A = pd.read_csv('/Users/ray/Research/AUSSEF - Local/Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
m = m.merge(A[['agrn', 'region_id', 'dwellings_in_fire', 'dwellings']], on=['agrn', 'region_id'])
def perm_p(x, y, s, n=10000):
    rho = spearmanr(x, y)[0]; c = 0
    for _ in range(n):
        xp = x.copy()
        for v in np.unique(s):
            i = np.where(s == v)[0]; xp[i] = rng.permutation(x[i])
        c += abs(spearmanr(xp, y)[0]) >= abs(rho)
    return rho, (1 + c) / (1 + n)
out = []
for col in ('C4_H1', 'C5_H1'):
    d = m[m[col].notna()]
    dup = d.duplicated(['region_id', 'F'], keep=False)
    print(f'{col}: rows {len(d)}, rows sharing a council-year with another row {dup.sum()}, distinct council-years {d.groupby(["region_id", "F"]).ngroups}')
    rho, p = perm_p(d.log_homes_in_fire_per_1000.to_numpy(), d[col].to_numpy(), d.F.to_numpy())
    out.append(dict(channel=col, version='all rows (as Exp11)', n=len(d), rho=rho, p_perm=p))
    for how in ('max', 'sum'):
        if how == 'max':
            g = d.groupby(['region_id', 'F']).agg(x=('log_homes_in_fire_per_1000', 'max'), y=(col, 'first')).reset_index()
        else:
            g = d.groupby(['region_id', 'F']).agg(h=('dwellings_in_fire', 'sum'), dw=('dwellings', 'first'), y=(col, 'first')).reset_index()
            g['x'] = np.log1p(g.h / g.dw * 1000)
        rho, p = perm_p(g.x.to_numpy(), g.y.to_numpy(), g.F.to_numpy())
        out.append(dict(channel=col, version=f'one row per council-year (dose {how})', n=len(g), rho=rho, p_perm=p))
R = pd.DataFrame(out); print(R.round(4).to_string(index=False)); R.to_csv(OUT / 'council_year_dedup.csv', index=False)
# Holm across the five primary tests using the de-duplicated p for C4/C5 and Experiment 11's p for the other three
C = pd.read_csv('/Users/ray/Research/AUSSEF - Local/Experiment 11/results/CLOCK.csv'); P = C[C.primary].set_index('channel').p_perm.to_dict()
for v in ('one row per council-year (dose max)', 'one row per council-year (dose sum)'):
    p = dict(P); p['C4_grants_pc'] = R[(R.channel == 'C4_H1') & (R.version == v)].p_perm.iloc[0]
    p['C5_fire_grant_share'] = R[(R.channel == 'C5_H1') & (R.version == v)].p_perm.iloc[0]
    s = sorted(p.items(), key=lambda kv: kv[1]); run = 0; h = {}
    for i, (k, pv) in enumerate(s):
        run = max(run, min(1, (len(s) - i) * pv)); h[k] = run
    print(v, 'Holm:', {k: round(x, 4) for k, x in h.items()})
