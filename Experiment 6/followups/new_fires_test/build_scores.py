"""Step 2b: X side only. Score blocks and risk_add_avail for the new-fire rows. NO Y is read or computed here.
Frozen rules: PRESPEC.md sections 1-3 and Amendment 1. Output: results/SCORES_new_rows.csv, results/SCORE_ITEMS_new_rows.csv,
logs (comparability check for the OLG items, placement self-check).

Run: PYTHONPATH=<dir containing xlrd> python3 build_scores.py     (anaconda python; reads .xls via xlrd)
"""
import json
import warnings

import numpy as np
import pandas as pd

from nf_lib import EXTRA, INP, P1, RAW, RES, FED, load_olg_module, norm_name, place

warnings.filterwarnings('ignore')
orig = pd.read_csv(INP / 'COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})
roster = pd.read_csv(RES / 'roster.csv', dtype={'lga_code': str})
roster = roster[roster.lga_name != 'Unincorporated Vic'].reset_index(drop=True)
log = {}

# ---------------------------------------------------------------- original reference distributions (129 NSW councils)
ITEM_SPEC = {   # item -> (column in COUNCIL_ITEMS_v2, higher_is_worse, scaled by the median of the column?)
    'seifa_irsd': ('seifa_irsd', False, False),
    'median_income': ('median_income_aud_fy', False, True),
    'unemp_rate': ('unemp_rate', True, True),
    'unrestricted_current_ratio': ('fiscal_unrestricted_current_ratio_fy', False, False),
    'operating_ratio': ('fiscal_operating_ratio_pct_fy', False, False),
    'infra_backlog_ratio': ('fiscal_infra_backlog_ratio_pct_fy', True, False),
}
REF = {}
for k, (col, hw, scaled) in ITEM_SPEC.items():
    x = orig[col].dropna().astype(float)
    REF[k] = x / x.median() if scaled else x
    log[f'ref_{k}'] = dict(n=int(len(x)), median=float(x.median()))


def pct_item(item, v, denom=None):
    _, hw, scaled = ITEM_SPEC[item]
    if scaled:
        if denom is None or pd.isna(v):
            return np.nan
        v = v / denom
    return place(v, REF[item], hw)


# placement self-check: placing each original value among the originals must reproduce the original percentile ranks within one rank step
chk = {}
for k, (col, hw, scaled) in ITEM_SPEC.items():
    x = orig[col].astype(float)
    ref = REF[k]
    got = pd.Series([place((v / x.dropna().median() if scaled else v) if pd.notna(v) else np.nan, ref, hw) for v in x])
    r = x.rank(pct=True)
    want = r if hw else 1 - r + 1 / x.notna().sum()
    chk[k] = float((got - want).abs().max())
log['placement_selfcheck_max_abs_diff'] = chk
assert max(chk.values()) < 0.02, chk

# ---------------------------------------------------------------- NSW 2013: V items (pre-fire vintage)
seifa11 = pd.read_excel(RAW / 'p1_nsw2013/2033.0.55.001_lga_indexes_2011.xls', sheet_name='Table 3', header=None).iloc[6:, [0, 1, 3]]
seifa11.columns = ['code', 'name', 'score']
seifa11 = seifa11.dropna(subset=['code'])
seifa11['code'] = seifa11.code.astype(str).str.replace(r'\.0$', '', regex=True)
seifa11['score'] = pd.to_numeric(seifa11.score, errors='coerce')
seifa06 = pd.read_excel(RAW / 'p3b_vic2009/2033055001_seifa_lga_2006.xls', sheet_name='Table 3', header=None).iloc[6:, [0, 1, 2]]
seifa06.columns = ['code', 'name', 'score']
seifa06 = seifa06.dropna(subset=['code'])
seifa06['code'] = seifa06.code.astype(str).str.replace(r'\.0$', '', regex=True)
seifa06['score'] = pd.to_numeric(seifa06.score, errors='coerce')

pia = pd.read_csv(P1 / 'data/income_area_year_by_release.csv', dtype={'geographic_id': str})
pia12 = pia[(pia.source_id == 'PIA_2020') & (pia.fy_start == 2012) & pia.geographic_id.str.fullmatch(r'\d{5}')].set_index('geographic_id')
pia12_nsw_median = float(pia12[pia12.index.str[0] == '1'].median_income_aud.median())
log['pia_fy2012_13_nsw_council_median_income'] = pia12_nsw_median
log['pia_fy2012_13_nsw_council_n'] = int((pia12.index.str[0] == '1').sum())

sal = pd.read_csv(FED / 'data/salm/salm_lga.csv', skiprows=2, dtype=str).dropna(subset=['LGA Code (2025 ASGS)'])
sal = sal[sal['Data Item'] == 'Smoothed unemployment rate (%)'].set_index('LGA Code (2025 ASGS)')
sal_jun13 = pd.to_numeric(sal['Jun-13'].str.replace(',', ''), errors='coerce')
sal_jun13_nsw_median = float(sal_jun13[sal_jun13.index.str[0] == '1'].median())
log['salm_jun13_nsw_median_rate'] = sal_jun13_nsw_median

# ---------------------------------------------------------------- NSW 2013: F items, FY2012-13 (NSW OLG Time Series)
olg = load_olg_module()
o12 = olg.parse_sheet('time-series-data-2011-12-2013-14.xlsx', '2012-13 Time Series Data ', 2012)
o12 = o12.pivot(index='council_name', columns='metric', values='value')
o12.index = [norm_name(x) for x in o12.index]
orig['key'] = orig.region_name.map(norm_name)
F_ITEMS = {'unrestricted_current_ratio': 'unrestricted_current_ratio', 'operating_ratio': 'operating_performance_ratio_pct',
           'infra_backlog_ratio': 'infrastructure_backlog_ratio_pct'}
comp = {}
f_keep = {}
for item, met in F_ITEMS.items():
    col = ITEM_SPEC[item][0]
    m = orig.set_index('key')[col].dropna()
    common = m.index.intersection(o12[met].dropna().index)
    a, b = float(o12.loc[common, met].median()), float(m.loc[common].median())
    ratio = a / b if b else np.nan
    keep = bool(np.isfinite(ratio) and abs(ratio - 1) <= 0.30)
    comp[item] = dict(n_common=int(len(common)), median_fy2012_13=a, median_original_snapshot=b, ratio=ratio, kept=keep)
    f_keep[item] = keep
log['f_item_comparability_30pct_rule'] = comp
dropped_by_documentation = ['cash_cover (definition break FY2012-13 to FY2013-14)', 'own_source_pct (definition break)',
                            'debt_service_ratio (not published for FY2012-13)']
log['f_dropped_by_documentation'] = dropped_by_documentation
n_f = sum(f_keep.values())
use_F = n_f >= 2
log['f_items_kept'] = [k for k, v in f_keep.items() if v]
log['F_used_for_NSW_2013'] = use_F

# ---------------------------------------------------------------- Victoria: EPISA average total income, FY2007-08
epi_raw = {}
for sh in ('Table_1', 'Table_2'):
    d = pd.read_excel(RAW / 'p3b_vic2009/6524055002do003_200506201011.xls', sheet_name=sh, header=None)
    grp_col = [c for c in range(d.shape[1]) if str(d.iloc[5, c]).startswith('Average Total Income from all sources')][0]
    year_cols = {str(d.iloc[6, c]): c for c in range(grp_col, grp_col + 6)}
    assert '2007-08' in year_cols and '2008-09' in year_cols, year_cols
    t = d.iloc[7:, [1, 3]].copy()
    t.columns = ['code', 'name']
    t['avg_total_income_2007_08'] = pd.to_numeric(d.iloc[7:, year_cols['2007-08']], errors='coerce')
    t = t.dropna(subset=['code'])
    t = t[pd.to_numeric(t.code, errors='coerce').notna()]
    t['code'] = t.code.astype(int).astype(str)
    epi_raw[sh] = t.set_index('code')
epi_nsw_median = float(epi_raw['Table_1'].avg_total_income_2007_08.median())
log['episa_fy2007_08_nsw_lga_median_of_average_total_income'] = epi_nsw_median
log['episa_nsw_lga_n'] = int(epi_raw['Table_1'].avg_total_income_2007_08.notna().sum())

# ---------------------------------------------------------------- assemble rows
rows, items = [], []
for r in roster.itertuples():
    base = dict(event=r.event, state=r.state, region_id=r.lga_code, region_name=r.lga_name, first_fire_start=r.first_fire_start,
                share_burned=r.share, burn_area_ha=r.burned_km2 * 100, lga_area_km2=r.lga_area_km2,
                scoreable_in_nsw_129=bool(r.scoreable_in_nsw_129))
    it = {}
    flags, notes = {}, []
    if r.state == 'NSW':
        if not r.scoreable_in_nsw_129:
            base.update(H=np.nan, E=np.nan, V=np.nan, F=np.nan, blocks_n=0, risk_add_avail=np.nan, S1_V=np.nan, S2_HV=np.nan)
            base['score_flags'] = 'unavailable: council merged in 2016 (no like-for-like council in the original 129)'
            rows.append(base)
            continue
        o = orig[orig.region_id == r.lga_code].iloc[0]
        H, E = float(o.H), float(o.E)                       # published percentiles, unchanged (time-invariant maps)
        # V (pre-fire vintage)
        s = seifa11[seifa11.code == r.lga_code]
        it['seifa_irsd'] = (float(s.score.iloc[0]) if len(s) else np.nan)
        pv = pia12.median_income_aud.get(r.lga_code, np.nan)
        it['median_income'] = (float(pv) if pd.notna(pv) else np.nan)
        it['unemp_rate'] = float(sal_jun13.get(r.lga_code, np.nan))
        pcts = {'seifa_irsd': pct_item('seifa_irsd', it['seifa_irsd']),
                'median_income': pct_item('median_income', it['median_income'], pia12_nsw_median),
                'unemp_rate': pct_item('unemp_rate', it['unemp_rate'], sal_jun13_nsw_median)}
        # F (pre-fire vintage, comparable items only)
        key = norm_name(r.lga_name)
        fpct = {}
        if use_F and key in o12.index:
            for item, met in F_ITEMS.items():
                if f_keep[item]:
                    v = o12.loc[key, met]
                    it[item] = float(v) if pd.notna(v) else np.nan
                    fpct[item] = pct_item(item, it[item])
        elif use_F:
            notes.append('council not found in OLG FY2012-13 sheet')
        Vb = np.nanmean([pcts[k] for k in pcts]) if any(pd.notna(pcts[k]) for k in pcts) else np.nan
        Fb = np.nanmean(list(fpct.values())) if fpct and any(pd.notna(x) for x in fpct.values()) else np.nan
        flags.update(H='published (Experiment 6, BFPL current post-2019 map)', E='published (Experiment 6, BFPL current, Census 2016)',
                     V='computed (SEIFA 2011; PIA FY2012-13; SALM Jun-13)',
                     F=('computed (OLG FY2012-13: ' + ', '.join(fpct) + ')') if fpct else 'unavailable')
        for k, v in pcts.items():
            items.append(dict(event=r.event, region_id=r.lga_code, region_name=r.lga_name, block='V', item=k, raw=it.get(k), pct=v))
        for k, v in fpct.items():
            items.append(dict(event=r.event, region_id=r.lga_code, region_name=r.lga_name, block='F', item=k, raw=it.get(k), pct=v))
    else:                                                     # Victoria: V only
        H = E = Fb = np.nan
        s = seifa06[seifa06.code == r.lga_code]
        it['seifa_irsd'] = float(s.score.iloc[0]) if len(s) else np.nan
        e = epi_raw['Table_2']
        it['median_income'] = float(e.avg_total_income_2007_08.get(r.lga_code, np.nan))   # AMENDMENT 1: average, not median
        pcts = {'seifa_irsd': pct_item('seifa_irsd', it['seifa_irsd']),
                'median_income': pct_item('median_income', it['median_income'], epi_nsw_median)}
        Vb = np.nanmean(list(pcts.values())) if any(pd.notna(x) for x in pcts.values()) else np.nan
        flags.update(H='unavailable (no BFPL-equivalent hazard layer)', E='unavailable (needs BFPL)', V='computed (SEIFA 2006; EPISA average total income FY2007-08, substitute for median)',
                     F='unavailable (Victorian finance ratios not comparable)')
        notes.append('unemployment item omitted (SALM starts Dec 2010)')
        for k, v in pcts.items():
            items.append(dict(event=r.event, region_id=r.lga_code, region_name=r.lga_name, block='V', item=k, raw=it.get(k), pct=v))
    blocks = {'H': H, 'E': E, 'V': Vb, 'F': Fb}
    present = {k: v for k, v in blocks.items() if pd.notna(v)}
    base.update(H=H, E=E, V=Vb, F=Fb, blocks_n=len(present),
                risk_add_avail=float(np.mean(list(present.values()))) if present else np.nan,
                S1_V=Vb, S2_HV=(float(np.mean([H, Vb])) if pd.notna(H) and pd.notna(Vb) else np.nan))
    base['score_flags'] = ' | '.join(f'{k}: {v}' for k, v in flags.items())
    base['score_notes'] = '; '.join(notes)
    rows.append(base)

S = pd.DataFrame(rows)
S.to_csv(RES / 'SCORES_new_rows.csv', index=False)
pd.DataFrame(items).to_csv(RES / 'SCORE_ITEMS_new_rows.csv', index=False)
json.dump(log, open(RES / 'score_build_log.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in log.items() if k.startswith(('f_', 'F_', 'placement', 'pia', 'salm', 'episa'))}, indent=1, default=str))
print(S[['event', 'region_name', 'share_burned', 'H', 'E', 'V', 'F', 'blocks_n', 'risk_add_avail']].round(3).to_string())
