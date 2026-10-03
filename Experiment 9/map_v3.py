"""Experiment 9 v3 map data (PRESPEC Addendum v3, "Map"). Descriptive.

1. RF with the PRE X set (H, E2, V, F, X23), fitted on all 218 rows, target Y_comp (v3); predicted for every NSW
   council from its pre-fire traits (X23 from Census 2021, the latest pre-fire value for a future fire).
2. Observed mean Y_comp (v3) over each council's fire rows.
Writes results/MAP_COUNCILS_V3.csv. Plot: make_map_v3_plot.py.

Run: python3 map_v3.py     (after data.py)
"""
import numpy as np
import pandas as pd

from data import CFG, HERE, OUT, src
from run_models import rf

T = pd.read_csv(OUT / 'ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
pre = CFG['x']['pre']
ok = T.Y_comp.notna()
model = rf().fit(T.loc[ok, pre], T.loc[ok, 'Y_comp'])

it = pd.read_csv(src('council_items'), dtype={'region_id': str})
C = it[['region_id', 'region_name_x', 'H', 'V', 'F', 'dwellings_in_bfpl12_share']].rename(
    columns={'region_name_x': 'council', 'dwellings_in_bfpl12_share': 'E2'})
x23 = pd.read_csv(HERE / 'inputs/x23_councils.csv', dtype={'region_id': str}).set_index('region_id')
C['X23'] = C.region_id.map(x23['2021']).fillna(C.region_id.map(x23['2016']))
C['pred_Y_v3_prefire'] = model.predict(C[pre])
obs = T.groupby('region_id').agg(obs_Y_v3_mean=('Y_comp', 'mean'), n_fire_rows=('Y_comp', 'size'),
                                 obs_Y_v1cfg_mean=('Y_comp_cfgv1', 'mean')).reset_index()
C = C.merge(obs, on='region_id', how='left')
C['pred_rank_pct'] = C.pred_Y_v3_prefire.rank(pct=True)
C.to_csv(OUT / 'MAP_COUNCILS_V3.csv', index=False)
print(C.sort_values('pred_Y_v3_prefire', ascending=False).head(15)[['council', 'pred_Y_v3_prefire', 'obs_Y_v3_mean', 'n_fire_rows']].round(3).to_string(index=False))
print('councils:', len(C), 'with X missing:', int(C[pre].isna().any(axis=1).sum()))
