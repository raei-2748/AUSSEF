import pandas as pd, numpy as np, json
from alib import *
a = pd.read_parquet('audit_ato.parquet').rename(columns={'pc': 'unit'})
U = units('poa'); D = load_dose('poa')
a = a[a.unit.isin(U.index)]
a['ly'] = np.log(a.ti.where(a.ti > 0))
res = {}
for S, (y0, y1) in {'B': (2014, 2022), 'P': (2010, 2018)}.items():
    w = a[(a.year >= y0) & (a.year <= y1)]
    ok = w[(w.n_ind >= 100) & w.ly.notna()].groupby('unit').year.nunique()
    keep = ok[ok == y1 - y0 + 1].index
    p = w[w.unit.isin(keep)][['unit', 'year', 'ly']].copy()
    p['SA3'] = p.unit.map(U.SA3); p['SA4'] = p.unit.map(U.SA4)
    q, names, est = add_lags(p, D, S, K_bs=y1 - 2019)
    r = fit(q, 'ly', names, est)
    nexp = int((q[names[:4] if S=='B' else names].max(axis=1) > 0).groupby(q.unit).max().sum())
    # placebo
    if S == 'B':
        pp = p[p.year <= 2018]
        qp, n2, e2 = add_lags(pp, D, 'B', placebo=True); rp = fit(qp, 'ly', n2, e2)
    else:
        pp = p_placebo_drop(p, D)
        qp, n2, e2 = add_lags(pp, D, 'P', placebo=True); rp = fit(qp, 'ly', n2, e2)
        # variant: also include real dose lags 0..3 as controls
        qv, n3, _ = add_lags(qp[['unit','year','ly','SA3','SA4'] + n2], D, 'P')
        rpv = fit(qv, 'ly', n2 + n3, e2)
        print('P placebo with real-lag controls:', pct(rpv), 'n', rpv.get('n'))
    print(S, 'units', len(keep), 'obs', r['n'], 'G', r['G'], 'exposed(primary dose>0)', nexp)
    print('  main   ', pct(r), 'p=%.3f' % r['p'], r['coefs'])
    print('  placebo', pct(rp), 'n', rp.get('n'), rp.get('coefs'))
    res[S] = dict(main=r, placebo=rp)
json.dump(res, open('out_income.json', 'w'), indent=1, default=str)
