"""Post-hoc (NOT pre-registered) checks of Part A: by season, and placebo with m0 shifted 24 months earlier."""
import numpy as np, pandas as pd
import run_spillover as S
U = pd.read_csv(S.OUT / 'NEIGHBOUR_UNITS.csv', dtype={'region_id': str})
units = S.U.copy()
print('neighbour units by season:', units.F.value_counts().sort_index().to_dict())
for k in ['rent', 'income_support', 'dv']:
    print(k, 'mean excess by season:', units.groupby('F')[k].mean().round(3).to_dict())
rows = []
for k, fn in S.OUTC.items():
    vals = []
    for u in units.itertuples():
        m0 = u.m0 - 24
        own = fn(u.region_id, m0)
        comp = [fn(c, m0) for c in u.far]; comp = [x for x in comp if pd.notna(x)]
        vals.append(own - np.median(comp) if pd.notna(own) and comp else np.nan)
    v = pd.Series(vals)
    n, nc, mean, lo, hi, p = S.cluster_mean(v, units.region_id.reset_index(drop=True))
    rows.append(dict(check='placebo_m0_minus_24m', outcome=k, n=n, mean_excess=mean, lo=lo, hi=hi, p=p))
    nb = units[units.F != 2019][k]
    if nb.notna().sum() >= 3:
        n, nc, mean, lo, hi, p = S.cluster_mean(nb, units[units.F != 2019].region_id)
        rows.append(dict(check='without_black_summer', outcome=k, n=n, mean_excess=mean, lo=lo, hi=hi, p=p))
R = pd.DataFrame(rows); R.to_csv(S.OUT / 'POSTHOC_CHECKS.csv', index=False); print(R.round(4).to_string(index=False))
