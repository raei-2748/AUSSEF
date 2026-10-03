"""Diagnostic for C1: do one-direction (half-counted) days cluster in the post-fire window of high-dose rows?
Per row: share of one-direction days at the council's two-direction stations in months m0..m0+3 minus the share in
the same months 12 and 24 months earlier; Spearman with dose. Uses the project's name rule (as in Experiment 11)."""
import re
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from scipy.stats import spearmanr
ROOT = Path('/Users/ray/Research/AUSSEF - Local'); OUT = Path(__file__).resolve().parent
m = pd.read_csv(OUT / 'rederived_c4_c5_rows.csv', dtype={'agrn': str, 'region_id': str})
m['m0'] = pd.to_datetime(m.first_fire_start).dt.to_period('M')
cl = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})
def norm(s):
    s = str(s).lower().replace('&', 'and'); s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'\b(city of|the|council|shire|regional|municipal|city|area)\b', ' ', s); return re.sub(r'[^a-z]', '', s)
k2id = dict(zip(cl.region_name_x.map(norm), cl.region_id))
con = duckdb.connect(str(ROOT / 'data/aussef.duckdb'), read_only=True)
parts = ' union all '.join(f'select station_key, classification_seq, traffic_direction_seq, date from raw.manual_traffic_hourly_permanent_{i}' for i in range(5))
d = con.execute(f"""with h as ({parts}), c as (select station_key, min(classification_seq) as cmin from h group by 1)
  select h.station_key, cast(h.date as date) as dd, count(distinct traffic_direction_seq) as ndir
  from h join c on h.station_key=c.station_key and h.classification_seq=c.cmin group by 1,2""").df()
ref = con.execute('select distinct station_key, lga from raw.manual_traffic_station_reference').df()
d = d.merge(ref, on='station_key'); d['rid'] = d.lga.map(lambda l: k2id.get(norm(l)))
modal = d.groupby('station_key').ndir.agg(lambda s: s.mode()[0]); d = d[d.station_key.map(modal) == 2]
d['one'] = d.ndir == 1; d['month'] = pd.to_datetime(d.dd).dt.to_period('M')
sh = d.groupby(['rid', 'month']).one.mean()
out = []
for r in m.itertuples():
    W = [r.m0 + k for k in range(4)]; B = [p - 12 for p in W] + [p - 24 for p in W]
    w = [sh.get((r.region_id, p), np.nan) for p in W]; b = [sh.get((r.region_id, p), np.nan) for p in B]
    out.append(np.nanmean(w) - np.nanmean(b) if np.isfinite(w).any() and np.isfinite(b).any() else np.nan)
m['one_dir_share_change'] = out
ok = m.one_dir_share_change.notna()
print('rows', ok.sum(), 'rho(dose, change in one-direction-day share) = %+.3f' % spearmanr(m.log_homes_in_fire_per_1000[ok], m.one_dir_share_change[ok])[0])
print(m[ok].groupby(pd.qcut(m.log_homes_in_fire_per_1000[ok], 3, labels=['low', 'mid', 'high'])).one_dir_share_change.mean().round(3))
m.loc[ok, ['agrn', 'region_id', 'region_name', 'F', 'log_homes_in_fire_per_1000', 'one_dir_share_change']].to_csv(OUT / 'c1_one_direction_diag.csv', index=False)
