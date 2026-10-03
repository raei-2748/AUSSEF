import pandas as pd, numpy as np, json
from alib import *
d = pd.read_parquet('audit_dv.parquet'); d['unit'] = d.unit.astype(str)
U = units('sal'); D = load_dose('sal')
d = d[d.unit.isin(U.index)].rename(columns={'fy': 'year'})
d['SA3'] = d.unit.map(U.SA3); d['SA4'] = d.unit.map(U.SA4)
res = {}
for S, (y0, y1) in {'B': (2014, 2024), 'P': (2009, 2018)}.items():
    p = d[(d.year >= y0) & (d.year <= y1)][['unit', 'year', 'n', 'SA3', 'SA4']]
    q, names, est = add_lags(p, D, S, K_bs=y1 - 2019)
    r = fit(q, 'n', names, est, model='pois')
    if S == 'B':
        qp, n2, e2 = add_lags(p[p.year <= 2018], D, 'B', placebo=True)
    else:
        qp, n2, e2 = add_lags(p_placebo_drop(p, D), D, 'P', placebo=True)
    rp = fit(qp, 'n', n2, e2, model='pois')
    print(S, 'suburbs', p.unit.nunique(), 'obs used', r['n'], 'units used', r['units'], 'G', r['G'])
    print('  main   ', pct(r), r['coefs'])
    print('  placebo', pct(rp), 'n', rp.get('n'), rp.get('coefs'))
    res[S] = dict(main=r, placebo=rp)
json.dump(res, open('out_dv.json', 'w'), indent=1, default=str)
