import pandas as pd, numpy as np
u = pd.read_parquet('../../Experiment 7/panels/sa2_unemployment.parquet')
first = u.groupby('SA2').period.min()
dz = pd.read_parquet('../exposure/out/dose_sa2.parquet'); h = dz[dz.fy == 2019].set_index('unit').H
un = pd.read_parquet('../exposure/out/units_sa2.parquet').set_index('unit')
f = first.reindex(un.index.astype(str)).dropna(); hh = h.reindex(f.index).fillna(0)
for lab, msk in (('all NSW SA2s', hh >= 0), ('BS H>0', hh > 0), ('BS H>=1%', hh >= 0.01), ('BS H>=10%', hh >= 0.10)):
    print(f'{lab:12s}: n={int(msk.sum())}, first data in 2010Q1: {int((f[msk]=="2010Q1").sum())}, from 2019: {int(f[msk].between("2019Q1","2019Q4").sum())}, from 2023: {int((f[msk]>="2023Q1").sum())}')
