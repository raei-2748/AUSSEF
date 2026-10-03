# Post-hoc sensitivity: add the 172 bracketed BOCSAR suburbs matched exactly to SAL (after removing " - NSW")
import pandas as pd, numpy as np, zipfile, re
from alib import *
z = zipfile.ZipFile('../dv/raw/SuburbData.zip')
d = pd.read_csv(z.open('SuburbData.csv'), dtype={'Suburb': str})
d = d[d.Subcategory == 'Domestic violence related assault']
months = [c for c in d.columns if re.match(r'^[A-Z][a-z]{2} \d{4}$', c)]
m = d.melt(id_vars=['Suburb'], value_vars=months, var_name='m', value_name='n')
dt = pd.to_datetime(m.m, format='%b %Y'); m['year'] = np.where(dt.dt.month >= 7, dt.dt.year, dt.dt.year - 1)
m['n'] = pd.to_numeric(m.n, errors='coerce').fillna(0)
y = m[m.year <= 2025].groupby(['Suburb', 'year']).n.sum().reset_index()
sal = pd.read_parquet('../exposure/out/sal_names.parquet')
k = sal.SAL_NAME_2021.str.replace(' - NSW)', ')', regex=False).str.replace(r'\s*\(NSW\)$', '', regex=True).str.upper().str.strip()
full = pd.Series(sal.SAL_CODE_2021.values, index=k); full = full[~full.index.duplicated(keep=False)]
y['unit'] = y.Suburb.str.upper().str.strip().map(full); y = y.dropna(subset=['unit'])
U = units('sal'); D = load_dose('sal')
y = y[y.unit.isin(U.index[U.dwellings >= 50])]
y = y[y.groupby('unit').n.transform('sum') > 0]
y['SA3'] = y.unit.map(U.SA3); y['SA4'] = y.unit.map(U.SA4)
print('suburbs', y.unit.nunique())
p = y[(y.year >= 2014) & (y.year <= 2024)]
q, names, est = add_lags(p, D, 'B', K_bs=5); r = fit(q, 'n', names, est, model='pois')
print('DV B with qualified names added:', pct(r))
