"""Audit check (a): council name matching used by Experiment 9 v3 / Experiment 11.
Re-implements the norm() rule verbatim (copied, not imported) and lists unmatched names per source.
Writes name_matching.txt and unmatched_*.csv in this folder."""
import re
from pathlib import Path
import duckdb, openpyxl, pandas as pd

ROOT = Path('/Users/ray/Research/AUSSEF - Local'); OUT = Path(__file__).resolve().parent
def norm(s):  # copy of Experiment 9/build_v3_indicators.py norm()
    s = str(s).lower().replace('&', 'and')
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'\b(city of|the|council|shire|regional|municipal|city|area)\b', ' ', s)
    return re.sub(r'[^a-z]', '', s)

it = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})
C = it[['region_id', 'region_name_x']].rename(columns={'region_name_x': 'name'}); C['key'] = C.name.map(norm)
dup = C[C.key.duplicated(keep=False)]
A = pd.read_csv(ROOT / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'region_id': str})
fire_ids = set(A.region_id); print('fire councils', len(fire_ids), 'rows', len(A))
name_of = C.set_index('region_id').name
key2id = C.set_index('key').region_id
lines = [f'129 councils; duplicate keys inside council list: {dup.to_dict("records")}']

con = duckdb.connect(str(ROOT / 'data/aussef.duckdb'), read_only=True)
ref = con.execute('select distinct station_key, lga from raw.manual_traffic_station_reference').df()
perm = set()
for i in range(5):
    perm |= set(con.execute(f'select distinct station_key from raw.manual_traffic_hourly_permanent_{i}').df().station_key)
ref['perm'] = ref.station_key.isin(perm)
wb = openpyxl.load_workbook(ROOT / 'fire_event_dataset/data/raw/bocsar/RCI_offencebymonth.xlsm', read_only=True)
boc = sorted({r[0] for r in wb['Data'].iter_rows(min_row=2, values_only=True) if r[0]})
olg = pd.read_parquet(ROOT / 'fire_event_dataset/data/olg/olg_long.parquet')
rent = pd.read_parquet(ROOT / 'fire_event_dataset/data/rent/rent_lga_quarter.parquet')

def report(src, names, counts=None):
    d = pd.DataFrame({'source_name': names}); d['key'] = d.source_name.map(norm); d['region_id'] = d.key.map(key2id)
    d['matched_to'] = d.region_id.map(name_of)
    if counts is not None: d['n'] = d.source_name.map(counts)
    un = d[d.region_id.isna()]; un.to_csv(OUT / f'unmatched_{src}.csv', index=False)
    matched = set(d.region_id.dropna())
    many = d.dropna(subset=['region_id']).groupby('region_id').source_name.apply(list)
    many = many[many.map(len) > 1]
    miss_all = sorted(name_of[sorted(set(C.region_id) - matched)])
    miss_fire = sorted(name_of[sorted(fire_ids - matched)])
    lines.append(f'\n## {src}: {len(d)} source names, {len(un)} unmatched, councils matched {len(matched)}/129')
    lines.append('UNMATCHED source names: ' + '; '.join(f"{a}" + (f" (n={int(n)})" if counts is not None else '') for a, n in zip(un.source_name, un.get('n', [0]*len(un)))))
    lines.append(f'Councils (of 129) with no match ({len(miss_all)}): ' + '; '.join(miss_all))
    lines.append(f'FIRE councils (of {len(fire_ids)}) with no match ({len(miss_fire)}): ' + '; '.join(miss_fire))
    lines.append('Several source names -> one council: ' + '; '.join(f'{name_of[k]} <- {v}' for k, v in many.items()))
    return d

t = report('traffic_lga_all_stations', sorted(ref.lga.dropna().astype(str).unique()), ref.groupby('lga').station_key.nunique())
tp = report('traffic_lga_permanent_stations', sorted(ref[ref.perm].lga.dropna().astype(str).unique()), ref[ref.perm].groupby('lga').station_key.nunique())
lines.append(f'traffic: {ref.lga.isna().sum()} station rows with lga NULL; permanent stations total {len(perm)}, '
             f'with matched lga {ref[ref.perm & ref.lga.map(norm).map(key2id).notna()].station_key.nunique()}')
report('bocsar', boc)
on = olg.drop_duplicates(['council_name_norm', 'fy_start'])
report('olg_all_years', sorted(olg.council_name_norm.unique()))
o2 = on[on.fy_start >= 2016]
report('olg_fy2016plus', sorted(o2.council_name_norm.unique()))
# within-year collisions in OLG
on = on.assign(rid=on.council_name_norm.map(norm).map(key2id))
coll = on.dropna(subset=['rid']).groupby(['rid', 'fy_start']).council_name_norm.apply(list)
coll = coll[coll.map(len) > 1]
lines.append('OLG collisions within one FY: ' + str(coll.to_dict()))
# OLG name continuity: councils whose OLG key exists only from some year
yrs = on.dropna(subset=['rid']).groupby('rid').fy_start.agg(['min', 'max', 'count'])
lines.append('OLG councils not covering all 12 FYs 2013-2024: ' + '; '.join(f'{name_of[k]} {r["min"]}-{r["max"]} ({r["count"]})' for k, r in yrs[yrs['count'] < 12].iterrows()))
# rent: uses region_id directly
rr = set(rent.region_id.astype(str))
lines.append(f'\n## rent (region_id direct): {len(rr)} ids; not in 129 councils: {sorted(rr - set(C.region_id))}; '
             f'councils missing: {sorted(name_of[sorted(set(C.region_id) - rr)])}; fire councils missing: {sorted(name_of[sorted(fire_ids - rr)])}')
# rent name vs id check
rn = rent.drop_duplicates('region_id')[['region_id', 'lga_name']].astype(str)
rn['council'] = rn.region_id.map(name_of); rn['ok'] = rn.lga_name.map(norm) == rn.council.map(norm)
lines.append('rent id/name disagreements: ' + str(rn[~rn.ok].values.tolist()))
open(OUT / 'name_matching.txt', 'w').write('\n'.join(lines)); print('\n'.join(lines))
