# Fully independent estimator (no pyfixest): alternating-projection FE + CRV1 by SA3, for ATO Y1 sample B.
import pandas as pd, numpy as np
from scipy import stats
from alib import add_lags, load_dose, units
a = pd.read_parquet('audit_ato.parquet').rename(columns={'pc': 'unit'}); U = units('poa'); D = load_dose('poa')
a = a[a.unit.isin(U.index) & (a.year.between(2014, 2022))]
ok = a[(a.n_ind >= 100) & (a.ti > 0)].groupby('unit').year.nunique(); a = a[a.unit.isin(ok[ok == 9].index)]
a['ly'] = np.log(a.ti); a['SA3'] = a.unit.map(U.SA3); a['SA4'] = a.unit.map(U.SA4)
q, names, est = add_lags(a[['unit', 'year', 'ly', 'SA3', 'SA4']], D, 'B', K_bs=3)
q = q.reset_index(drop=True); q['g2'] = q.SA4 + '_' + q.year.astype(str)
M = q[['ly'] + names].to_numpy(float).copy()
for _ in range(2000):
    old = M.copy()
    for g in ('unit', 'g2'):
        M -= pd.DataFrame(M).groupby(q[g].values).transform('mean').to_numpy()
    if np.abs(M - old).max() < 1e-13: break
yv, X = M[:, 0], M[:, 1:]
b = np.linalg.lstsq(X, yv, rcond=None)[0]; e = yv - X @ b
XtXi = np.linalg.inv(X.T @ X)
cl = q.SA3.values; G = len(set(cl)); N = len(q); k = X.shape[1]
meat = sum(np.outer(X[cl == c].T @ e[cl == c], X[cl == c].T @ e[cl == c]) for c in set(cl))
w = np.zeros(k); w[[names.index(c) for c in est]] = 0.5
nfe_unit = q.unit.nunique()  # unit FE nested in SA3 clusters
for lab, kk in (('K=slopes only', k), ('K=slopes+SA4xyear FE (unit FE nested)', k + q.g2.nunique() - 1)):
    V = G / (G - 1) * (N - 1) / (N - kk) * XtXi @ meat @ XtXi
    c = w @ b; se = np.sqrt(w @ V @ w); t = stats.t.ppf(0.975, G - 1)
    f = lambda x: 100 * (np.exp(0.1 * x) - 1)
    print(f'{lab}: {f(c):+.2f}% [{f(c - t * se):+.2f}, {f(c + t * se):+.2f}]  (N={N}, G={G})')
