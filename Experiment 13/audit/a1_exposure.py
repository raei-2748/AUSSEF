# Audit check 1: rebuild postcode H from mesh-block shares; check region assignment.
import pandas as pd, numpy as np
E = '../exposure/out/'
sh = pd.read_parquet(E+'mb_fy_shares.parquet')
info = pd.read_parquet(E+'mb_info.parquet')
dose = pd.read_parquet(E+'dose_poa.parquet')
units = pd.read_parquet(E+'units_poa.parquet')
info = info[info.POA_CODE_2021.notna()]
pdw = info.groupby('POA_CODE_2021').dwelling.sum()
out = {}
for fy in sorted(sh.fy.unique()):
    s = sh[sh.fy == fy].merge(info[['MB_CODE','dwelling','POA_CODE_2021']], on='MB_CODE')
    s['dw_in'] = s.share_in * s.dwelling
    H = (s.groupby('POA_CODE_2021').dw_in.sum() / pdw).dropna()
    H = H.reindex(pdw[pdw > 0].index).fillna(0)
    m = dose[dose.fy == fy].set_index('unit').H.reindex(H.index).fillna(0)
    out[fy] = (np.abs(H - m).max(), int((H > 0.01).sum()), int((H > 0.1).sum()))
for fy in (2013, 2019):
    print(f'fy{fy}: max|H_audit - H_main| = {out[fy][0]:.2e}; postcodes H>=1%: {out[fy][1]}, >=10%: {out[fy][2]}')
print('all fy max diff:', max(v[0] for v in out.values()))
# region = SA3/SA4 holding most dwellings
rng = np.random.default_rng(13)
g3 = info.groupby(['POA_CODE_2021','SA3_CODE_2021']).dwelling.sum().reset_index().sort_values('dwelling', ascending=False).drop_duplicates('POA_CODE_2021').set_index('POA_CODE_2021').SA3_CODE_2021
g4 = info.groupby(['POA_CODE_2021','SA4_CODE_2021']).dwelling.sum().reset_index().sort_values('dwelling', ascending=False).drop_duplicates('POA_CODE_2021').set_index('POA_CODE_2021').SA4_CODE_2021
u = units.set_index('unit')
pick = rng.choice(u.index.values, 20, replace=False)
bad3 = [p for p in pick if g3[p] != u.loc[p,'SA3']]; bad4 = [p for p in pick if g4[p] != u.loc[p,'SA4']]
print('20 random postcodes, SA3 mismatches:', bad3, 'SA4 mismatches:', bad4)
allbad3 = (g3.reindex(u.index) != u.SA3).sum(); allbad4 = (g4.reindex(u.index) != u.SA4).sum()
print('all', len(u), 'postcodes: SA3 mismatches', allbad3, 'SA4 mismatches', allbad4)
# note: SA4 of postcode taken directly (most dwellings) vs SA4 of the chosen SA3 - can differ
sa3to4 = info.drop_duplicates('SA3_CODE_2021').set_index('SA3_CODE_2021').SA4_CODE_2021
print('postcodes whose SA4 is not the parent of their SA3:', int((u.SA3.map(sa3to4) != u.SA4).sum()))
print('postcodes in units with 0 dwellings:', int((u.dwellings<=0).sum()), '; units count', len(u), 'vs nonzero-dwelling POAs', int((pdw>0).sum()))
