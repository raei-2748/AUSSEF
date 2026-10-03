import pandas as pd, numpy as np, json
from alib import *
def read(f, years):
    r = pd.read_excel(f, sheet_name='Table 1.4', header=None, dtype=object)
    blk = r.iloc[5].ffill(); yrs = r.iloc[6]
    cols = [i for i in range(r.shape[1]) if str(blk[i]).startswith('Sum') and str(yrs[i]) in years]
    b = r.iloc[7:]
    b = b[b[0].astype(str).str.fullmatch(r'1\d{8}')]
    out = []
    for i in cols:
        v = pd.to_numeric(b[i].astype(str).str.replace(',', ''), errors='coerce')
        out.append(pd.DataFrame({'unit': b[0].astype(str), 'year': int(str(yrs[i])[:4]), 'sum': v.values}))
    return pd.concat(out)
a = read('../income_ato/raw/pia2023_table1_total_income.xlsx', ['2018-19','2019-20','2020-21','2021-22','2022-23'])
b = read('/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw/pia_2024.xlsx', ['2017-18','2018-19'])
# consistency check of overlapping year 2018-19 between releases
ov = a[a.year == 2018].merge(b[b.year == 2018], on='unit')
print('2018-19 overlap: n', len(ov), 'max rel diff', float(((ov.sum_x - ov.sum_y).abs() / ov.sum_x).max()))
p = pd.concat([b[b.year == 2017], a])
U = units('sa2'); D = load_dose('sa2')
p = p[p.unit.isin(U.index)]
p['ly'] = np.log(p['sum'].where(p['sum'] > 0)); p = p[p.ly.notna()]
p['SA3'] = p.unit.map(U.SA3); p['SA4'] = p.unit.map(U.SA4)
q, names, est = add_lags(p, D, 'B', K_bs=3)
r = fit(q, 'ly', names, est)
print('PIA units', p.unit.nunique(), 'obs', r['n'], 'G', r['G']); print('  main', pct(r), r['coefs'])
pp = p[p.year <= 2018]
qp, n2, e2 = add_lags(pp, D, 'B', placebo=True)
print('placebo design: years', sorted(pp.year.unique()), '; corr(fk0+fk1 constant within unit?)',
      bool((qp.assign(s=qp.fk0 + qp.fk1).groupby('unit').s.nunique() <= 1).all()))
rp = fit(qp, 'ly', n2, e2)
print('  placebo', pct(rp), 'n', rp.get('n'), rp.get('coefs'))
json.dump(dict(main=r, placebo=rp), open('out_pia.json', 'w'), indent=1, default=str)
