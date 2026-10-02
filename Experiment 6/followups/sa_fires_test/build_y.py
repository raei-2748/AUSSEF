"""Step 2c (SA fires): Y side. Indicators, master-referenced percentiles, pillars, Y_new for the SA rows, with a source flag per cell.
Frozen rules: PRESPEC.md sections 4-5 and 7, Amendment 1. Reads results/SCORES_new_rows.csv only for keys and score columns (no test is run here).
Every SA council is keyed internally by its ASGS 2018 code (Mallala 43920 = Adelaide Plains 40150, same geometry).

Inputs (all on disk): PIA (dataset_phase1 income csv), CABEE (fire_event_dataset/data/cabee), LGGC items (results/lggc_items_all_councils.csv),
DSS (approved SA workbooks + on-disk national CSVs), ERP (32180DS0004), Census 2011 B31 (approved 2011 pack) and 2016 G32 (approved 2016 pack),
homes destroyed from inputs_dl/dl_homes_sourced.csv.
Outputs: results/Y_indicators_new_rows.csv, EXTRA/sa_fire_rows.csv (git-ignored data folder) and a copy in results/, results/y_build_log.json.
Run: /Users/ray/.venv/bin/python build_y.py
"""
import io
import json
import re
import sys
import warnings
import zipfile

import numpy as np
import openpyxl
import pandas as pd
import xlrd

from nf_lib import EXTRA, FED, HERE, INP, P1, RAW, RES, norm_name, place_signed

warnings.filterwarnings('ignore')
EXTRA.mkdir(parents=True, exist_ok=True)
S = pd.read_csv(RES / 'SCORES_new_rows.csv', dtype={'region_id': str, 'code_lga2018': str})
CG = pd.read_csv(RES / 'comparison_groups.csv', dtype={'lga_code': str, 'lga_vintage': str})
CG = CG[(CG.lga_vintage == '2018') & ~CG.lga_name.str.startswith(('Unincorporated', 'Migratory', 'No usual'))]
REFY = pd.read_csv(INP / 'master_reference_indicators.csv')
log = {}
FYBASE = {'SA_2015_sampson_flat': 2014, 'SA_2015_pinery': 2015, 'SA_2019_cudlee_creek': 2019, 'SA_2019_20_kangaroo_island': 2019, 'SA_2019_20_keilira': 2019}
Q0 = {'SA_2015_sampson_flat': '2015Q1', 'SA_2015_pinery': '2015Q4', 'SA_2019_cudlee_creek': '2019Q4', 'SA_2019_20_kangaroo_island': '2019Q4', 'SA_2019_20_keilira': '2019Q4'}


def k(code):
    """Mallala (43920) and Adelaide Plains (40150) are one council."""
    code = str(code).split('.')[0]
    return '40150' if code == '43920' else code


def win_label(ev, kind):
    fy = FYBASE[ev]
    return {'fy': f'FY{fy}-{str(fy + 1)[2:]}', 'fy2': f'FY{fy}-{str(fy + 1)[2:]}..FY{fy + 1}-{str(fy + 2)[2:]}', 'sl': 'SL_5Q'}[kind]


def nofire_codes(ev, kind):
    g = CG[(CG.event == ev) & (CG.window == win_label(ev, kind))]
    return set(g[~g.has_fire_100ha].lga_code.map(k)), set(g.lga_code.map(k))


def excess(change, comp, label):
    c = change[change.index.isin(comp)].dropna()
    med = float(c.median()) if len(c) else np.nan
    log[label] = dict(comparison_n=int(len(c)), median_change=med, councils_in_table=int(change.notna().sum()))
    return change - med, c


# ------------------------------------------------------------------ dwellings
z11 = zipfile.ZipFile(RAW / 'p1_nsw2013/2011_BCP_LGA_for_AUST_short-header.zip')
b31 = pd.read_csv(io.BytesIO(z11.read([n for n in z11.namelist() if n.endswith('2011Census_B31_AUST_LGA_short.csv')][0])))
dw11 = b31.assign(code=b31.region_id.astype(str).str.replace('LGA', '', regex=False).map(k)).set_index('code').Total_PDs_Dwellings
z16 = zipfile.ZipFile(RAW / 'p0_census2016/2016_GCP_LGA_for_AUS_short-header.zip')
g32 = pd.read_csv(io.BytesIO(z16.read('2016 Census GCP Local Government Areas for AUST/2016Census_G32_AUS_LGA.csv')))
dw16 = g32.assign(code=g32.LGA_CODE_2016.astype(str).str.replace('LGA', '', regex=False).map(k)).set_index('code').Total_PDs_Dwellings

# ------------------------------------------------------------------ IL income (PIA): total income, fire FY vs previous FY, one release
pia = pd.read_csv(P1 / 'data/income_area_year_by_release.csv', dtype={'geographic_id': str})
pia = pia[pia.geographic_id.str.fullmatch(r'\d{5}')]


def pia_release(fy, prev):
    have = pia.groupby('source_id').fy_start.apply(set)
    ok = [r for r, s in have.items() if {fy, prev} <= s]
    pub = pia.groupby('source_id').publication_date.max()
    return max(ok, key=lambda r: pub[r])


inc_ex, inc_release = {}, {}
for ev, fy in FYBASE.items():
    rel = pia_release(fy, fy - 1)
    t = pia[pia.source_id == rel].pivot(index='geographic_id', columns='fy_start', values='total_income_aud')
    t = t[t.index.str[0] == '4']
    t.index = t.index.map(k)
    chg = (t[fy] - t[fy - 1]) / t[fy - 1] * 100
    ex, _ = excess(chg, nofire_codes(ev, 'fy')[0], f'{ev}_income')
    inc_ex[ev] = ex
    inc_release[ev] = rel

# ------------------------------------------------------------------ IL business counts (CABEE): total businesses, June t-1 -> June t, one release
CAB = FED / 'data/cabee'
BIZ = {   # event -> (file, sheet at t-1, sheet at t); None = no single release on disk has both June dates
    'SA_2015_sampson_flat': None,
    'SA_2015_pinery': ('jun2013-jun2017_8165010.xls', 'June 2015', 'June 2016'),
    'SA_2019_cudlee_creek': ('jul2016-jun2020_816510.xls', 'June 2019 a', 'June 2020 a'),
    'SA_2019_20_kangaroo_island': ('jul2016-jun2020_816510.xls', 'June 2019 a', 'June 2020 a'),
    'SA_2019_20_keilira': ('jul2016-jun2020_816510.xls', 'June 2019 a', 'June 2020 a'),
}


def cabee_totals(fn, sheet):
    wb = xlrd.open_workbook(CAB / fn)
    s = wb.sheet_by_name(sheet)
    hdr = [str(x).strip() for x in s.row_values(5)]
    tot_col = len(hdr) - 1 if hdr[-1] == 'Total' else hdr.index('Total')
    out = {}
    for r in range(7, s.nrows):
        row = s.row_values(r)
        code, ind = row[1], str(row[3]).strip()
        if isinstance(code, float) and str(int(code))[0] == '4' and ind == '':
            out[k(int(code))] = float(row[tot_col]) if isinstance(row[tot_col], (int, float)) else np.nan
    return pd.Series(out)


biz_ex, biz_src = {}, {}
for ev, spec in BIZ.items():
    if spec is None:
        biz_ex[ev], biz_src[ev] = None, 'N/A: no release on disk contains both June 2014 and June 2015'
        continue
    fn, s0, s1 = spec
    a, b = cabee_totals(fn, s0), cabee_totals(fn, s1)
    chg = (b - a) / a * 100
    ex, _ = excess(chg, nofire_codes(ev, 'fy')[0], f'{ev}_business')
    biz_ex[ev], biz_src[ev] = ex, f'{fn} {s0} -> {s1}'
    log[f'{ev}_business_councils_with_totals'] = int(len(a))

# ------------------------------------------------------------------ FP (LGGC)
LG = pd.read_csv(RES / 'lggc_items_all_councils.csv')
LG = LG[LG.council != 'State Totals'].copy()
LG['key'] = LG.council.map(norm_name).replace({'mallala': 'adelaide plains'})
LG['cash_cover'] = (LG.cash + LG.other_fin_assets) / ((LG.total_op_expenses - LG.depreciation) / 12)
fn_cols = [c for c in LG.columns if c.startswith('fn_') and c != 'fn_total_r9']
LG['service_share'] = 100 * LG[fn_cols].sum(axis=1, min_count=len(fn_cols)) / LG.total_op_expenses
LG['asr'] = np.where(LG.r8_last_label.str.contains('Asset Sustainability'), LG.last_r8, np.nan)
# Report 9 total vs Report 3 total (Amendment 1, A2.1)
r9 = LG.dropna(subset=['fn_total_r9'])
log['report9_total_vs_report3_total_max_rel_diff'] = float(((r9.fn_total_r9 - r9.total_op_expenses).abs() / r9.total_op_expenses).max()) if len(r9) else None
LGT = {m: LG.pivot(index='key', columns='fy', values=m) for m in ('cash_cover', 'service_share', 'asr')}
# ABS name keys of the SA comparison councils
names = CG[['lga_code', 'lga_name']].drop_duplicates()
names['code'] = names.lga_code.map(k)
names['key'] = names.lga_name.map(norm_name)
ALIAS = {'berri and barmera': 'berri barmera', 'naracoorte and lucindale': 'naracoorte lucindale',
         'norwood payneham st peters': 'norwood payneham and st peters', 'port pirie and dists': 'port pirie'}   # ABS name -> LGGC name (name pairs only)
names['key'] = names.key.replace(ALIAS)
key_of = names.set_index('code').key
unm = sorted(set(names.key) - set(LGT['cash_cover'].index))
log['comparison_councils_without_lggc_match'] = unm
if unm:
    print('UNMATCHED ABS names (no LGGC council after normalisation):', unm)
FP_YEARS = {'SA_2015_sampson_flat': 2013, 'SA_2015_pinery': 2014, 'SA_2019_cudlee_creek': 2018, 'SA_2019_20_kangaroo_island': 2018, 'SA_2019_20_keilira': 2018}
MASTER_IQR = {c: float(REFY[c].dropna().quantile(.75) - REFY[c].dropna().quantile(.25)) for c in
              ('FP_cash_cover_excess_signed', 'FP_services_crowd_out_excess_signed', 'FP_renewals_excess_signed')}
log['master_iqr'] = MASTER_IQR
fp_ex, fp_kept = {}, {}
for ev, t1 in FP_YEARS.items():
    comp_e, _ = nofire_codes(ev, 'fy')
    comp_p, _ = nofire_codes(ev, 'fy2')
    ke = set(key_of.reindex(list(comp_e)).dropna())
    kp = set(key_of.reindex(list(comp_p)).dropna())
    # FP years: t-1 = t1, fire FY t = t1 + 1, t+1 = t1 + 2  (t1 is the fy_start of the previous FY)
    T = {m: LGT[m] for m in LGT}
    d_cash_e = T['cash_cover'][t1 + 1] - T['cash_cover'][t1]
    d_cash_p = T['cash_cover'][t1 + 2] - T['cash_cover'][t1]
    d_svc_p = T['service_share'][t1 + 2] - T['service_share'][t1]
    d_asr_p = T['asr'][t1 + 2] - T['asr'][t1]
    ce, _ = excess(d_cash_e, ke, f'{ev}_cash_event')
    cp, _ = excess(d_cash_p, kp, f'{ev}_cash_plus1')
    sp, _ = excess(d_svc_p, kp, f'{ev}_service_share_plus1')
    rp, _ = excess(d_asr_p, kp, f'{ev}_asr_plus1')
    cash_mean = pd.concat([ce, cp], axis=1).mean(axis=1, skipna=True).where(pd.concat([ce, cp], axis=1).notna().any(axis=1))
    ex = {'cash': cash_mean, 'serv': sp, 'renew': rp}
    kept = {}
    for name, ser, mcol in (('cash', cash_mean, 'FP_cash_cover_excess_signed'), ('serv', sp, 'FP_services_crowd_out_excess_signed'), ('renew', rp, 'FP_renewals_excess_signed')):
        grp = ser[ser.index.isin(kp)].dropna()
        iqr = float(grp.quantile(.75) - grp.quantile(.25)) if len(grp) >= 8 else np.nan
        ratio = iqr / MASTER_IQR[mcol] if MASTER_IQR[mcol] else np.nan
        ok = bool(np.isfinite(ratio) and 0.5 <= ratio <= 2.0)
        if name == 'renew' and t1 >= 2018:
            ok, why = False, 'ratio definition changed (Asset Renewal Funding Ratio from FY2018-19; Amendment 1 A2.2)'
        else:
            why = 'scale check' if not ok else ''
        kept[name] = dict(sa_iqr=iqr, master_iqr=MASTER_IQR[mcol], ratio=ratio, kept=ok, reason=why, n_group=int(len(grp)))
    fp_ex[ev], fp_kept[ev] = ex, kept
log['fp_scale_check'] = fp_kept

# ------------------------------------------------------------------ SL (DSS)
COMP = {   # component -> regex on a lower-case, alphanumeric-only header
    'newstart': r'^newstart', 'sickness': r'^sickness', 'partner': r'^partnerallowance', 'widow': r'^widowallowance', 'widowb': r'^widowb',
    'wife_age': r'^wifepensionpartneronagepension', 'wife_dsp': r'^wifepensionpartnerondisability', 'youth_other': r'^youthallowanceother',
    'pp_single': r'^parentingpayment(single)', 'pp_partnered': r'^parentingpayment(partnered)', 'dsp': r'^disabilitysupportpension',
    'carer': r'^carerpayment', 'special': r'^specialbenefit'}


def norm_hdr(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def comp_cols(headers):
    out = {}
    for c, pat in COMP.items():
        hit = [h for h in headers if re.search(pat, norm_hdr(h))]
        hit = [h for h in hit if 'card' not in norm_hdr(h) and 'allowanceb' not in norm_hdr(h)] if c in ('carer',) else hit
        if len(hit) == 1:
            out[c] = hit[0]
        elif c == 'carer':
            hit2 = [h for h in headers if norm_hdr(h) == 'carerpayment']
            if len(hit2) == 1:
                out[c] = hit2[0]
    return out


def dss_xlsx(path, sheet):
    ws = openpyxl.load_workbook(path, read_only=True)[sheet]
    rows = list(ws.iter_rows(min_row=3, values_only=True))
    hdr = [h for h in rows[0] if h is not None]
    df = pd.DataFrame([r[:len(hdr)] for r in rows[1:]], columns=hdr)
    df = df[pd.to_numeric(df['LGA'], errors='coerce').notna()].copy()
    df['code'] = df['LGA'].astype(float).astype(int).astype(str).map(k)
    return df[df.code.str[0] == '4'].set_index('code'), hdr


def dss_csv(fn, date, codecol):
    d = pd.read_csv(FED / 'data/dss' / fn, dtype={codecol: str})
    d = d[d.date == date].copy()
    d['code'] = d[codecol].map(k)
    return d[d.code.str[0] == '4'].set_index('code'), [c for c in d.columns if c not in ('date', codecol)]


SL_PAIR = {   # event -> ((source, args) before, (source, args) after, ERP year)
    'SA_2015_sampson_flat': (('x', 'p2_sa_dss/dss-demographics-june-2014-jan-2020-edit.xlsx', 'LGA '), ('x', 'p2_sa_dss/dss-demographics-june-2015.xlsx', 'LGA'), 2014),
    'SA_2015_pinery': (('x', 'p2_sa_dss/dss-demogrphics-march-2015.xlsx', 'LGA'), ('c', 'dss-payments-mar-2016-to-dec-2018-by-2014-lga.csv', '2016-03', 'LGA_Code_2014'), 2014),
    'SA_2019_cudlee_creek': (('c', 'dss-payments-mar-2019-to-dec-2020-by-2018-lga.csv', '2019-03', 'LGA_Code_2018'), ('c', 'dss-payments-mar-2019-to-dec-2020-by-2018-lga.csv', '2020-03', 'LGA_Code_2018'), 2018),
}
SL_PAIR['SA_2019_20_kangaroo_island'] = SL_PAIR['SA_2019_20_keilira'] = SL_PAIR['SA_2019_cudlee_creek']
erp = pd.read_excel(FED / 'data/abs/32180DS0004_2001-25.xlsx', sheet_name='Table 1', header=None, skiprows=6)
erp_t = erp.iloc[:, [0] + list(range(2, 27))]
erp_t.columns = ['code'] + list(range(2001, 2026))
erp_t = erp_t[pd.to_numeric(erp_t.code, errors='coerce').notna()].copy()
erp_t['code'] = erp_t.code.astype(float).astype(int).astype(str).map(k)
erp_t = erp_t.set_index('code').apply(pd.to_numeric, errors='coerce')


def load_side(spec):
    if spec[0] == 'x':
        return dss_xlsx(RAW / spec[1], spec[2])
    return dss_csv(spec[1], spec[2], spec[3])


sl_ex, sl_info = {}, {}
for ev, (b, a, ey) in SL_PAIR.items():
    B, hb = load_side(b)
    A, ha = load_side(a)
    cb, ca = comp_cols(hb), comp_cols(ha)
    common = [c for c in COMP if c in cb and c in ca]

    def total(df, cols):
        m = df[[cols[c] for c in common]].copy()
        n_imp = m.apply(lambda col: col.astype(str).str.strip().eq('<20')).sum(axis=1)
        m = m.apply(lambda col: pd.to_numeric(col.astype(str).str.strip().replace({'<20': '10'}).str.replace(',', ''), errors='coerce'))
        return m.sum(axis=1, min_count=len(common)), n_imp
    tb, ib = total(B, cb)
    ta, ia = total(A, ca)
    pop = erp_t[ey] / 1000
    per = (ta - tb) / pop.reindex(ta.index)
    ex, _ = excess(per, nofire_codes(ev, 'sl')[0], f'{ev}_sl')
    sl_ex[ev] = ex
    imp = (ib.reindex(ex.index).fillna(0) + ia.reindex(ex.index).fillna(0))
    sl_info[ev] = dict(components=common, n_components=len(common), imputed=imp)
    log[f'{ev}_sl_components'] = common

# ------------------------------------------------------------------ DL numerators
DL = pd.read_csv(INP.parent / 'inputs_dl/dl_homes_sourced.csv', dtype={'region_id': str})

# ------------------------------------------------------------------ assemble
EVENT_NAME = {'SA_2015_sampson_flat': 'Sampson Flat bushfire, Adelaide Hills, January 2015', 'SA_2015_pinery': 'Pinery bushfire, 25 November 2015',
              'SA_2019_cudlee_creek': 'Cudlee Creek bushfire, 20 December 2019', 'SA_2019_20_kangaroo_island': 'Kangaroo Island bushfires, December 2019 - January 2020',
              'SA_2019_20_keilira': 'Keilira bushfire, 30 December 2019'}
rows = []
for r in S.itertuples():
    row = r._asdict()
    row.pop('Index', None)
    ev, code = r.event, k(r.code_lga2018)
    key = key_of.get(code, norm_name(r.region_name))
    ind, flag, note = {}, {}, []
    d = DL[(DL.event == ev) & (DL.region_id == r.region_id)]
    homes = float(d.homes_destroyed.iloc[0]) if len(d) and pd.notna(d.homes_destroyed.iloc[0]) else np.nan
    dw = dw11 if FYBASE[ev] < 2018 else dw16
    dwell = float(dw.get(code, np.nan))
    row['homes_destroyed'], row['dwellings_census'] = homes, dwell
    row['census_vintage'] = 2011 if FYBASE[ev] < 2018 else 2016
    row['event_name'] = EVENT_NAME[ev]
    row['dl_source_url'] = d.url.iloc[0] if len(d) else ''
    if len(d) and str(d.note.iloc[0]) != 'nan':
        note.append('DL: ' + str(d.note.iloc[0]))
    if pd.notna(homes) and pd.notna(dwell) and dwell > 0:
        ind['DL'], flag['DL'] = homes / dwell * 1000, d.status.iloc[0]
    else:
        ind['DL'], flag['DL'] = np.nan, 'unavailable'
    # IL
    ind['IL_inc'] = -inc_ex[ev].get(code, np.nan)
    flag['IL_inc'] = 'computed' if pd.notna(ind['IL_inc']) else 'unavailable'
    if biz_ex[ev] is None:
        ind['IL_biz'], flag['IL_biz'] = np.nan, 'N/A (no single-release June 2014-June 2015 pair on disk)'
    else:
        ind['IL_biz'] = -biz_ex[ev].get(code, np.nan)
        flag['IL_biz'] = 'computed' if pd.notna(ind['IL_biz']) else 'unavailable'
    # FP
    fe, fk = fp_ex[ev], fp_kept[ev]
    for name, col in (('cash', 'FP_cash'), ('serv', 'FP_serv'), ('renew', 'FP_renew')):
        v = fe[name].get(key, np.nan)
        sign = {'cash': -1, 'serv': -1, 'renew': +1}[name]
        if not fk[name]['kept']:
            ind[col], flag[col] = np.nan, f"N/A ({fk[name]['reason'] or 'scale check'})"
        elif pd.isna(v):
            ind[col], flag[col] = np.nan, 'unavailable'
        else:
            ind[col], flag[col] = sign * v, 'computed_substitute'
    # SL
    v = sl_ex[ev].get(code, np.nan)
    ind['SL'] = v
    if pd.notna(v):
        imp = sl_info[ev]['imputed'].get(code, 0)
        flag['SL'] = 'computed_low_confidence' if imp > 0 else 'computed'
        if imp > 0:
            note.append(f'SL: {int(imp)} suppressed "<20" cell(s) counted as 10 in the row sum')
    else:
        flag['SL'] = 'unavailable'
    note.append(f"IL income release {inc_release[ev]}; IL business: {biz_src[ev]}")
    note.append('FP/IL/SL comparison group = SA councils with no GA fire >= 100 ha in the window (GA SA coverage of 100 ha fires not verified)')
    row['note'] = ' | '.join(note)
    for kk, vv in ind.items():
        row[f'raw_{kk}'] = vv
        row[f'flag_{kk}'] = flag[kk]
    rows.append(row)
Y = pd.DataFrame(rows)
refcol = {'DL': 'DL_homes_per_1000_dwellings_signed', 'IL_inc': 'IL_total_income_excess_signed', 'IL_biz': 'IL_biz_count_excess_signed',
          'FP_cash': 'FP_cash_cover_excess_signed', 'FP_serv': 'FP_services_crowd_out_excess_signed', 'FP_renew': 'FP_renewals_excess_signed',
          'SL': 'SL_income_support_excess_signed'}
for kk, c in refcol.items():
    Y[f'pct_{kk}'] = [place_signed(v, REFY[c]) for v in Y[f'raw_{kk}']]
Y['DL'] = Y.pct_DL
Y['IL'] = Y[['pct_IL_inc', 'pct_IL_biz']].mean(axis=1, skipna=True)
Y['FP'] = Y[['pct_FP_cash', 'pct_FP_serv', 'pct_FP_renew']].mean(axis=1, skipna=True)
Y['SL'] = Y.pct_SL
PIL = ['DL', 'IL', 'FP', 'SL']
Y['pillars_n'] = Y[PIL].notna().sum(axis=1)
Y['Y_new'] = Y[PIL].mean(axis=1, skipna=True).where(Y.pillars_n >= 1)
Y['Y_new_ge2pillars'] = Y.Y_new.where(Y.pillars_n >= 2)
Y['Y_new_noFP'] = Y[['DL', 'IL', 'SL']].mean(axis=1, skipna=True).where(Y[['DL', 'IL', 'SL']].notna().sum(axis=1) >= 1)
Y['DL_reported_only'] = Y.pct_DL.where(Y.flag_DL == 'reported')
Y.to_csv(RES / 'Y_indicators_new_rows.csv', index=False)

keep = ['event', 'event_name', 'region_id', 'region_name', 'code_lga2018', 'first_fire_start', 'share_burned', 'burn_area_ha', 'H', 'E', 'V', 'F', 'blocks_n', 'risk_add_avail', 'S1_V', 'S2_HV',
        'homes_destroyed', 'dwellings_census', 'census_vintage', 'DL', 'IL', 'FP', 'SL', 'pillars_n', 'Y_new',
        'flag_DL', 'flag_IL_inc', 'flag_IL_biz', 'flag_FP_cash', 'flag_FP_serv', 'flag_FP_renew', 'flag_SL', 'dl_source_url', 'score_flags', 'score_notes', 'note']
out = Y[[c for c in keep if c in Y.columns]].copy()
out.to_csv(EXTRA / 'sa_fire_rows.csv', index=False)
out.to_csv(RES / 'sa_fire_rows.csv', index=False)
json.dump(log, open(RES / 'y_build_log.json', 'w'), indent=1, default=str)
print('rows', len(Y), 'with Y_new', int(Y.Y_new.notna().sum()))
print(Y[['event', 'region_name', 'pillars_n']].assign(DL=Y.flag_DL, IL_biz=Y.flag_IL_biz.str[:12], FP=Y.flag_FP_cash.str[:12], SL=Y.flag_SL).to_string())
