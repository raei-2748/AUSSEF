# How many BOCSAR suburbs with a bracketed qualifier (dropped by the PRESPEC rule) could be matched exactly?
import pandas as pd, zipfile
sal = pd.read_parquet('../exposure/out/sal_names.parquet')
k = sal.SAL_NAME_2021.str.replace(' - NSW)', ')', regex=False).str.replace(r'\s*\(NSW\)$', '', regex=True).str.upper().str.strip()
full = pd.Series(sal.SAL_CODE_2021.values, index=k)
full = full[~full.index.duplicated(keep=False)]
d = pd.read_csv(zipfile.ZipFile('../dv/raw/SuburbData.zip').open('SuburbData.csv'), usecols=['Suburb'])
s = pd.Series(d.Suburb.unique()); b = s[s.str.contains(r'\(')]
m = b.str.upper().str.strip().map(full)
u = pd.read_parquet('../exposure/out/units_sal.parquet').set_index('unit')
dz = pd.read_parquet('../exposure/out/dose_sal.parquet'); h = dz[dz.fy == 2019].set_index('unit').H
mm = m.dropna(); ok = mm[mm.map(u.dwellings).fillna(0) >= 50]
print('bracketed BOCSAR names', len(b), '| exact match after dropping " - NSW"', int(m.notna().sum()),
      '| with >=50 dwellings', len(ok), '| Black Summer H>=1%', int((ok.map(h).fillna(0) >= 0.01).sum()),
      '| H>=10%', int((ok.map(h).fillna(0) >= 0.10).sum()))
dd = dz[dz.fy == 2019]; kept = pd.read_parquet('audit_dv.parquet').unit.astype(str).unique()
print('for scale: kept suburbs with BS H>=1%:', int((dd.set_index('unit').H.reindex(kept).fillna(0) >= 0.01).sum()),
      ' H>=10%:', int((dd.set_index('unit').H.reindex(kept).fillna(0) >= 0.10).sum()))
