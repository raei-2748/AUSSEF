"""Step 2c: Y side. Indicators, master-referenced percentiles, pillars, Y_new for the new-fire rows, with a source flag per cell.
Frozen rules: PRESPEC.md sections 4-5 and 7, Amendment 1. Reads results/SCORES_new_rows.csv only for keys and score columns (no test is run here).

Inputs (all on disk; the 8 approved downloads are read straight from their zip/xls files, nothing is extracted):
  NSW 2013: ABS PIA (dataset_phase1 income csv, PIA_2020 release), NRP economy 2010-14 (June 2013 -> June 2014), OLG Time Series FY2012-13 / 2013-14 / 2014-15,
            Census 2011 BCP B31 (dwellings), homes destroyed from inputs_dl/dl_homes_sourced.csv (sourced, with URLs).
  Vic 2009: EPISA total income FY2007-08 -> FY2008-09 (series break flagged), NRP economy 2008-12 (June 2008 -> June 2009), Census 2011 BCP B31, homes destroyed as above.
Outputs: results/Y_indicators_new_rows.csv, EXTRA/extra_fire_rows.csv (the requested table, git-ignored data folder) and a copy in results/.
Run: PYTHONPATH=<dir containing xlrd> python3 build_y.py
"""
import io
import json
import warnings
import zipfile

import numpy as np
import pandas as pd

from nf_lib import EXTRA, FED, HERE, INP, P1, RAW, RES, load_olg_module, norm_name, place_signed

warnings.filterwarnings('ignore')
EXTRA.mkdir(parents=True, exist_ok=True)
S = pd.read_csv(RES / 'SCORES_new_rows.csv', dtype={'region_id': str})
CG = pd.read_csv(RES / 'comparison_groups.csv', dtype={'lga_code': str, 'lga_vintage': str})
REFY = pd.read_csv(INP / 'master_reference_indicators.csv')
log = {}

# ------------------------------------------------------------------ helpers
def comparison_codes(event, window, vint):
    g = CG[(CG.event == event) & (CG.window == window) & (CG.lga_vintage == vint)]
    g = g[~g.lga_name.str.startswith(('Unincorporated', 'Migratory', 'No usual'))]
    return set(g[~g.has_fire_100ha].lga_code), set(g.lga_code)


def excess(change, comp_codes, all_codes, label):
    """change: Series indexed by code. Excess = change minus median over comparison councils (in this table and in the group)."""
    comp = change[change.index.isin(comp_codes)].dropna()
    med = float(comp.median()) if len(comp) else np.nan
    log[label] = dict(comparison_n=int(len(comp)), median_change=med, councils_in_table=int(change.notna().sum()),
                      in_group_frame=int(change.index.isin(all_codes).sum()))
    return change - med


# ------------------------------------------------------------------ dwellings, Census 2011 B31 (private dwellings, occupied + unoccupied)
z = zipfile.ZipFile(RAW / 'p1_nsw2013/2011_BCP_LGA_for_AUST_short-header.zip')
b31 = pd.read_csv(io.BytesIO(z.read([n for n in z.namelist() if n.endswith('2011Census_B31_AUST_LGA_short.csv')][0])))
b31['code'] = b31.region_id.astype(str).str.replace('LGA', '', regex=False)
dw = b31.set_index('code').Total_PDs_Dwellings

# ------------------------------------------------------------------ NSW 2013 IL: PIA total income, FY2013-14 vs FY2012-13
pia = pd.read_csv(P1 / 'data/income_area_year_by_release.csv', dtype={'geographic_id': str})
pia = pia[(pia.source_id == 'PIA_2020') & pia.geographic_id.str.fullmatch(r'\d{5}')].pivot(index='geographic_id', columns='fy_start', values='total_income_aud')
nsw_inc_chg = (pia[2013] - pia[2012]) / pia[2012] * 100
nsw_inc_chg = nsw_inc_chg[nsw_inc_chg.index.str[0] == '1']
cc, ca = comparison_codes('NSW_2013_oct', 'FY2013-14', '2018')
nsw_inc_ex = excess(nsw_inc_chg, cc, ca, 'nsw2013_income')

# ------------------------------------------------------------------ NSW 2013 IL: NRP business counts June 2013 -> June 2014
def nrp_xls(zipf, name):
    d = pd.read_excel(io.BytesIO(zipfile.ZipFile(zipf).read(name)), header=None)
    t = d.iloc[8:, [0, 1, 2, 7]].copy()
    t.columns = ['code', 'name', 'year', 'biz']
    t = t[pd.to_numeric(t.code, errors='coerce').notna()]
    t['code'] = t.code.astype(int).astype(str)
    t['year'] = pd.to_numeric(t.year, errors='coerce')
    t['biz'] = pd.to_numeric(t.biz, errors='coerce')
    return t


nrp13 = nrp_xls(RAW / 'p1_nsw2013/1379055001_economy_2010-2014_lga_201606.zip', '1379055001_ECONOMY_2010-2014_LGA_201606.xls')
bz = nrp13.pivot(index='code', columns='year', values='biz')
nsw_biz_chg = ((bz[2014] - bz[2013]) / bz[2013] * 100)
nsw_biz_chg = nsw_biz_chg[nsw_biz_chg.index.str[0] == '1']
cc, ca = comparison_codes('NSW_2013_oct', 'FY2013-14', '2015')
nsw_biz_ex = excess(nsw_biz_chg, cc, ca, 'nsw2013_business')

# ------------------------------------------------------------------ NSW 2013 FP: NSW OLG Time Series, FY2012-13 (t-1), 2013-14 (t), 2014-15 (t+1)
olg = load_olg_module()
parts = {2012: ('time-series-data-2011-12-2013-14.xlsx', '2012-13 Time Series Data '),
         2013: ('time-series-data-2011-12-2013-14.xlsx', '2013-14 Time Series Data '),
         2014: ('time-series-data-2014-15_1.xls', '2014-15 Time Series Data')}
O = {}
for fy, (fn, sh) in parts.items():
    t = olg.parse_sheet(fn, sh, fy).pivot(index='council_name', columns='metric', values='value')
    t.index = [norm_name(x) for x in t.index]
    t = t[~t.index.duplicated()]
    O[fy] = t


def service_share(t):
    funcs = ['exp_governance_admin_aud', 'exp_public_order_health_water_sewer_aud', 'exp_environment_aud', 'exp_community_services_housing_aud',
             'exp_recreation_culture_aud', 'exp_roads_bridges_footpaths_aud', 'exp_other_services_aud']
    t = t.copy()
    t.loc[t.exp_roads_bridges_footpaths_aud == 0, 'exp_roads_bridges_footpaths_aud'] = np.nan
    tot = t[funcs].sum(axis=1, min_count=len(funcs))
    return 100 * (t.exp_community_services_housing_aud + t.exp_recreation_culture_aud + t.exp_environment_aud) / tot


cash = {fy: O[fy].cash_expense_cover_ratio_months for fy in O}
ren = {fy: O[fy].building_infrastructure_renewals_ratio_pct for fy in O}
svc = {fy: service_share(O[fy]) for fy in O}
d_cash_event = cash[2013] - cash[2012]
d_cash_plus1 = cash[2014] - cash[2012]
d_svc_plus1 = svc[2014] - svc[2012]
d_ren_plus1 = ren[2014] - ren[2012]
# comparison councils by normalised name (OLG pre-merger names = ABS LGA 2015 names)
g15 = {}
for label in ('FY2013-14', 'FY2013-14..FY2014-15'):
    g = CG[(CG.event == 'NSW_2013_oct') & (CG.window == label) & (CG.lga_vintage == '2015')].copy()
    g['key'] = g.lga_name.map(norm_name)
    g15[label] = (set(g[~g.has_fire_100ha].key), set(g.key))
ex_cash_event = excess(d_cash_event, *g15['FY2013-14'], 'nsw2013_cash_event')
ex_cash_plus1 = excess(d_cash_plus1, *g15['FY2013-14..FY2014-15'], 'nsw2013_cash_plus1')
ex_svc_plus1 = excess(d_svc_plus1, *g15['FY2013-14..FY2014-15'], 'nsw2013_service_share_plus1')
ex_ren_plus1 = excess(d_ren_plus1, *g15['FY2013-14..FY2014-15'], 'nsw2013_renewals_plus1')

# ------------------------------------------------------------------ Victoria 2009 IL
epi = pd.read_excel(RAW / 'p3b_vic2009/6524055002do003_200506201011.xls', sheet_name='Table_2', header=None)
gc = [c for c in range(epi.shape[1]) if str(epi.iloc[5, c]).startswith('Total Income from all sources') and 'Income ($)' in str(epi.iloc[5, c]) and 'Average' not in str(epi.iloc[5, c])][0]
yc = {str(epi.iloc[6, c]): c for c in range(gc, gc + 6)}
assert '2007-08' in yc and '2008-09' in yc, yc
e = epi.iloc[7:, [1]].copy()
e.columns = ['code']
e['ti07'] = pd.to_numeric(epi.iloc[7:, yc['2007-08']], errors='coerce')
e['ti08'] = pd.to_numeric(epi.iloc[7:, yc['2008-09']], errors='coerce')
e = e[pd.to_numeric(e.code, errors='coerce').notna()]
e['code'] = e.code.astype(int).astype(str)
e = e.set_index('code')
vic_inc_chg = (e.ti08 - e.ti07) / e.ti07 * 100
cc, ca = comparison_codes('VIC_2009_black_saturday', 'FY2008-09', '2015')
vic_inc_ex = excess(vic_inc_chg, cc, ca, 'vic2009_income')

nrp09 = pd.read_csv(io.StringIO(zipfile.ZipFile(RAW / 'p3b_vic2009/nrp_economy_lga_2008-2012.zip').read('National Regional Profile, Economy, LGA, 2008-2012.csv').decode('latin-1')), low_memory=False)
bcol = [c for c in nrp09.columns if c.startswith('NUMBER OF BUSINESSES - Total number of businesses')][0]
n9 = nrp09[['Geography - Codes', 'Year - Labels', bcol]].copy()
n9.columns = ['code', 'year', 'biz']
n9 = n9[pd.to_numeric(n9.code, errors='coerce').notna() & pd.to_numeric(n9.year, errors='coerce').notna()].copy()
n9['code'] = n9.code.astype(float).astype(int).astype(str)
n9['year'] = n9.year.astype(float).astype(int)
n9['biz'] = pd.to_numeric(n9.biz, errors='coerce')
bz9 = n9.pivot(index='code', columns='year', values='biz')
vic_biz_chg = (bz9[2009] - bz9[2008]) / bz9[2008] * 100
cc, ca = comparison_codes('VIC_2009_black_saturday', 'FY2008-09', '2015')
vic_biz_ex = excess(vic_biz_chg, cc, ca, 'vic2009_business')

# ------------------------------------------------------------------ DL numerators (sourced file, may be partly blank)
dlf = INP.parent / 'inputs_dl/dl_homes_sourced.csv'
DL = pd.read_csv(dlf, dtype={'region_id': str}) if dlf.exists() else pd.DataFrame(columns=['event', 'region_id', 'homes_destroyed', 'status'])

# ------------------------------------------------------------------ assemble
EVENT_NAME = {'NSW_2013_oct': "NSW October 2013 fires ('Red October')", 'VIC_2009_black_saturday': 'Victoria Black Saturday fires, 7 February 2009'}
rows = []
for r in S.itertuples():
    row = r._asdict()
    row.pop('Index', None)
    code, key, ev = r.region_id, norm_name(r.region_name), r.event
    ind = {}
    flag = {}
    note = []
    d = DL[(DL.event == ev) & (DL.region_id == code)]
    homes = float(d.homes_destroyed.iloc[0]) if len(d) and pd.notna(d.homes_destroyed.iloc[0]) else np.nan
    dwell = float(dw.get(code, np.nan))
    row['homes_destroyed'], row['dwellings_census2011'] = homes, dwell
    row['event_name'] = EVENT_NAME[ev]
    row['dl_source_url'] = d.url.iloc[0] if len(d) else ''
    if len(d) and str(d.note.iloc[0]) != 'nan':
        note.append('DL: ' + str(d.note.iloc[0]))
    if pd.notna(homes) and pd.notna(dwell) and dwell > 0:
        ind['DL'] = homes / dwell * 1000
        flag['DL'] = d.status.iloc[0]
    else:
        ind['DL'] = np.nan
        flag['DL'] = 'unavailable'
    if ev.startswith('NSW'):
        code18 = code
        ind['IL_inc'] = -nsw_inc_ex.get(code18, np.nan)
        flag['IL_inc'] = 'computed' if pd.notna(ind['IL_inc']) else 'unavailable'
        ind['IL_biz'] = -nsw_biz_ex.get(code, np.nan)
        flag['IL_biz'] = 'computed' if pd.notna(ind['IL_biz']) else 'unavailable'
        ce, cp = ex_cash_event.get(key, np.nan), ex_cash_plus1.get(key, np.nan)
        ind['FP_cash'] = -np.nanmean([ce, cp]) if pd.notna(ce) or pd.notna(cp) else np.nan
        ind['FP_serv'] = -ex_svc_plus1.get(key, np.nan)
        ind['FP_renew'] = ex_ren_plus1.get(key, np.nan)
        for k in ('FP_cash', 'FP_serv', 'FP_renew'):
            flag[k] = 'computed_low_confidence' if pd.notna(ind[k]) else 'unavailable'
        if key not in O[2012].index:
            note.append('council not found in OLG sheets')
    else:
        ind['IL_inc'] = -vic_inc_ex.get(code, np.nan)
        flag['IL_inc'] = 'computed_low_confidence' if pd.notna(ind['IL_inc']) else 'unavailable'
        ind['IL_biz'] = -vic_biz_ex.get(code, np.nan)
        flag['IL_biz'] = 'computed' if pd.notna(ind['IL_biz']) else 'unavailable'
        for k in ('FP_cash', 'FP_serv', 'FP_renew'):
            ind[k] = np.nan
            flag[k] = 'N/A (Victorian finance ratios not comparable)'
    ind['SL'] = np.nan
    flag['SL'] = 'N/A'
    if ev.startswith('NSW'):
        note.append('FP: OLG definition break FY2012-13 to FY2013-14 (cash cover); excess design removes only a uniform shift')
        note.append('IL/FP comparison group = NSW councils with no GA fire >= 100 ha in the window (GA NSW outlines are NPWS-mapped, private-land fires under-mapped)')
    else:
        note.append('IL income: EPISA series break across FY2007-08/2008-09; total income excludes government pensions/allowances')
        note.append('FP N/A: Victorian finance ratios not comparable; SL N/A')
    row['note'] = ' | '.join(note)
    for k, v in ind.items():
        row[f'raw_{k}'] = v
        row[f'flag_{k}'] = flag[k]
    rows.append(row)
Y = pd.DataFrame(rows)

# percentile of each raw signed indicator in the existing 218-row master distribution
refcol = {'DL': 'DL_homes_per_1000_dwellings_signed', 'IL_inc': 'IL_total_income_excess_signed', 'IL_biz': 'IL_biz_count_excess_signed',
          'FP_cash': 'FP_cash_cover_excess_signed', 'FP_serv': 'FP_services_crowd_out_excess_signed', 'FP_renew': 'FP_renewals_excess_signed'}
for k, c in refcol.items():
    Y[f'pct_{k}'] = [place_signed(v, REFY[c]) for v in Y[f'raw_{k}']]
Y['DL'] = Y.pct_DL
Y['IL'] = Y[['pct_IL_inc', 'pct_IL_biz']].mean(axis=1, skipna=True)
Y['FP'] = Y[['pct_FP_cash', 'pct_FP_serv', 'pct_FP_renew']].mean(axis=1, skipna=True)
Y['SL'] = np.nan
PIL = ['DL', 'IL', 'FP', 'SL']
Y['pillars_n'] = Y[PIL].notna().sum(axis=1)
Y['Y_new'] = Y[PIL].mean(axis=1, skipna=True).where(Y.pillars_n >= 1)
# pre-declared descriptive sensitivities
Y['Y_new_ge2pillars'] = Y.Y_new.where(Y.pillars_n >= 2)
Y['Y_new_noFP'] = Y[['DL', 'IL']].mean(axis=1, skipna=True).where(Y[['DL', 'IL']].notna().sum(axis=1) >= 1)
DLrep = Y.pct_DL.where(Y.flag_DL == 'reported')
Y['DL_reported_only'] = DLrep
Y['IL_biz_only'] = Y.pct_IL_biz
Y['Y_new_vic_IL_biz_only'] = np.where(Y.event.str.startswith('VIC'),
                                      Y[['DL', 'IL_biz_only']].mean(axis=1, skipna=True).where(Y[['DL', 'IL_biz_only']].notna().sum(axis=1) >= 1), Y.Y_new)
Y.to_csv(RES / 'Y_indicators_new_rows.csv', index=False)

# requested table
keep = ['event', 'event_name', 'region_id', 'region_name', 'first_fire_start', 'share_burned', 'burn_area_ha', 'H', 'E', 'V', 'F', 'blocks_n', 'risk_add_avail', 'S1_V', 'S2_HV',
        'homes_destroyed', 'dwellings_census2011', 'DL', 'IL', 'FP', 'SL', 'pillars_n', 'Y_new',
        'flag_DL', 'flag_IL_inc', 'flag_IL_biz', 'flag_FP_cash', 'flag_FP_serv', 'flag_FP_renew', 'flag_SL', 'dl_source_url', 'score_flags', 'score_notes', 'note']
out = Y[[c for c in keep if c in Y.columns]].copy()
out.to_csv(EXTRA / 'extra_fire_rows.csv', index=False)
out.to_csv(RES / 'extra_fire_rows.csv', index=False)
json.dump(log, open(RES / 'y_build_log.json', 'w'), indent=1, default=str)
print(json.dumps(log, indent=1, default=str))
print(Y[['event', 'region_name', 'pillars_n', 'flag_DL']].to_string())
print('rows with Y_new:', int(Y.Y_new.notna().sum()), 'of', len(Y))
