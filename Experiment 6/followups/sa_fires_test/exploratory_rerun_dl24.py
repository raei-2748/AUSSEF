"""EXPLORATORY (post-run, 2026-09-30): re-estimate the pooled primary test with one extra DL cell (Adelaide Hills, Sampson Flat = 24 homes,
per ChatGPT-extracted council report quote, not verified by me). Frozen result is untouched; writes results/exploratory_dl24/ only."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, '.')
import run_frozen_test as R
from nf_lib import INP, place_signed

R.FAKE = True                       # code path only for load_rows; nothing is overwritten (we write our own folder)
D = R.load_rows()
Y = pd.read_csv(R.RES / 'Y_indicators_new_rows.csv', dtype={'region_id': str})
m = (D.event == 'SA_2015_sampson_flat') & (D.region_id == '40120')
row = Y[(Y.event == 'SA_2015_sampson_flat') & (Y.region_id == '40120')].iloc[0]
raw = 24 / row.dwellings_census * 1000
ref = pd.read_csv(INP / 'master_reference_indicators.csv').DL_homes_per_1000_dwellings_signed
dl = place_signed(raw, ref)
old_y = float(D.loc[m, 'Y_new'].iloc[0])
D.loc[m, 'DL'] = dl
D.loc[m, 'Y_new'] = D.loc[m, ['DL', 'IL', 'FP', 'SL']].mean(axis=1, skipna=True)
new_y = float(D.loc[m, 'Y_new'].iloc[0])
D = D[D.risk_add_avail.notna()]
out = Path(R.RES / 'exploratory_dl24'); out.mkdir(exist_ok=True)
rng = np.random.default_rng(R.SEED_BOOT)
res = {}
for name, sub, tgt in (('pooled_Y_new', D, 'Y_new'), ('SA_Y_new', D[D.group != 'STAGE1'], 'Y_new'), ('pooled_DL', D, 'DL'), ('pooled_without_SA2019_Y_new', D[D.group != 'SA_2019_20'], 'Y_new')):
    n, est, lo, hi = R.boot(sub.risk_add_avail, sub[tgt], sub.region_id, rng)
    res[name] = dict(n=n, spearman=est, ci_low=lo, ci_high=hi)
res['cell'] = dict(raw_DL_per_1000=raw, DL_percentile=dl, Y_new_before=old_y, Y_new_after=new_y)
json.dump(res, open(out / 'EXPLORATORY_DL24.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
