import pandas as pd, numpy as np, json
from alib import *
u = pd.read_parquet('../../Experiment 7/panels/sa2_unemployment.parquet')
print('duplicate SA2-period rows:', int(u.duplicated(['SA2', 'period']).sum()))
yr = u.period.str[:4].astype(int); q = u.period.str[-1].astype(int)
u['year'] = np.where(q >= 3, yr, yr - 1)       # Sep & Dec quarters start the FY
g = u.groupby(['SA2', 'year']).agg(un=('unemployed', 'sum'), lf=('labour_force', 'sum'), nq=('period', 'nunique')).reset_index()
g = g[(g.nq == 4) & (g.lf > 0)].rename(columns={'SA2': 'unit'})
g['rate'] = 100 * g.un / g.lf
U = units('sa2'); D = load_dose('sa2')
g = g[g.unit.astype(str).isin(U.index)]; g['unit'] = g.unit.astype(str)
g['SA3'] = g.unit.map(U.SA3); g['SA4'] = g.unit.map(U.SA4)
res = {}
for S, (y0, y1) in {'B': (2014, int(g.year.max())), 'P': (2010, 2018)}.items():
    p = g[(g.year >= y0) & (g.year <= y1)][['unit', 'year', 'rate', 'SA3', 'SA4']]
    qd, names, est = add_lags(p, D, S, K_bs=y1 - 2019)
    r = fit(qd, 'rate', names, est)
    if S == 'B': qp, n2, e2 = add_lags(p[p.year <= 2018], D, 'B', placebo=True)
    else: qp, n2, e2 = add_lags(p_placebo_drop(p, D), D, 'P', placebo=True)
    rp = fit(qp, 'rate', n2, e2)
    print(S, f'years {y0}-{y1}', 'units', p.unit.nunique(), 'obs', r['n'], 'G', r['G'])
    print('  main    pts per 10pp', lin(r), r['coefs'])
    print('  placebo pts per 10pp', lin(rp), 'n', rp.get('n'))
    res[S] = dict(main=r, placebo=rp)
json.dump(res, open('out_unemp.json', 'w'), indent=1, default=str)
