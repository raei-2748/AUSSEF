# Audit: BOCSAR suburb DV-related assault -> suburb (SAL 2021) x FY counts
import pandas as pd, numpy as np, zipfile, re
z = zipfile.ZipFile('../dv/raw/SuburbData.zip')
d = pd.read_csv(z.open('SuburbData.csv'), dtype={'Suburb': str})
print(d.shape); print(d['Offence category'].unique()[:40])
a = d[d['Offence category'].str.strip().str.lower() == 'assault']
print(a.Subcategory.unique())
dv = a[a.Subcategory.str.strip().str.lower() == 'domestic violence related assault'].copy()
months = [c for c in d.columns if re.match(r'^[A-Z][a-z]{2} \d{4}$', c)]
last = months[-1]; print('first/last month', months[0], last)
m = dv.melt(id_vars=['Suburb'], value_vars=months, var_name='m', value_name='n')
m['date'] = pd.to_datetime(m.m, format='%b %Y')
m['fy'] = np.where(m.date.dt.month >= 7, m.date.dt.year, m.date.dt.year - 1)
m['n'] = pd.to_numeric(m.n, errors='coerce').fillna(0)
cnt_months = m.groupby('fy').m.nunique()
full = cnt_months[cnt_months == 12].index
y = m[m.fy.isin(full)].groupby(['Suburb', 'fy']).n.sum().reset_index()
print('complete FYs', full.min(), full.max())
# name match to SAL 2021
sal = pd.read_parquet('../exposure/out/sal_names.parquet')
sal['key'] = sal.SAL_NAME_2021.str.replace(r'\s*\([^)]*\)\s*$', '', regex=True).str.upper().str.strip()
cnt = sal.key.value_counts(); uniq = sal[sal.key.map(cnt) == 1].set_index('key').SAL_CODE_2021
amb = set(cnt[cnt > 1].index)
y['key'] = y.Suburb.str.upper().str.strip()
subs = pd.Series(y.key.unique())
print('BOCSAR suburbs', len(subs), 'matched', subs.isin(uniq.index).sum(), 'ambiguous', subs.isin(amb).sum())
y = y[y.key.isin(uniq.index)]
y['unit'] = y.key.map(uniq)
units = pd.read_parquet('../exposure/out/units_sal.parquet').set_index('unit')
y = y[y.unit.isin(units.index[units.dwellings >= 50])]
tot = y.groupby('unit').n.sum(); y = y[y.unit.isin(tot[tot >= 1].index)]
print('suburbs kept', y.unit.nunique())
y[['unit', 'fy', 'n']].to_parquet('audit_dv.parquet')
