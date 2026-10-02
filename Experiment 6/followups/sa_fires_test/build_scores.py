"""Step 2b (SA fires): X side only. Score blocks and risk_add_avail for the SA rows. NO Y is read or computed here.
Frozen rules: PRESPEC.md sections 1-3 and Amendment 1. Output: results/SCORES_new_rows.csv, results/SCORE_ITEMS_new_rows.csv,
results/lggc_council_match.csv, results/score_build_log.json.
Run: /Users/ray/.venv/bin/python build_scores.py     (needs pandas, xlrd, openpyxl; reads results/geo_items_sa.csv from build_geo_items.py)
"""
import json
import warnings

import numpy as np
import pandas as pd

from nf_lib import FED, INP, P1, RAW, RES, norm_name, place

warnings.filterwarnings('ignore')
orig = pd.read_csv(INP / 'COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})
roster = pd.read_csv(RES / 'roster.csv', dtype={'lga_code': str, 'code_lga2018': str, 'code_lga2015': str, 'lga_vintage': str})
geo = pd.read_csv(RES / 'geo_items_sa.csv', dtype={'lga_code': str, 'lga_vintage': str})
geo['mapped'] = (geo.bpa_any_ha / (geo.council_area_km2 * 100)) >= 0.01           # Amendment 1, A1
log = {'bpa_mapped': geo[['lga_vintage', 'lga_code', 'lga_name', 'bpa_any_ha', 'mapped']].to_dict('records')}

ITEM_SPEC = {   # item -> (column in COUNCIL_ITEMS_v2, higher_is_worse, scaled by the median of the column?)
    'seifa_irsd': ('seifa_irsd', False, False), 'median_income': ('median_income_aud_fy', False, True), 'unemp_rate': ('unemp_rate', True, True),
    'cash_cover': ('fiscal_cash_cover_months_fy', False, False), 'own_source': ('fiscal_own_source_pct_fy', False, False),
    'operating_ratio': ('fiscal_operating_ratio_pct_fy', False, False),
    'h1': ('bfpl_share_cat1', True, False), 'h2': ('bfpl_share_cat12', True, False),
    'e1': ('dwellings_in_bfpl12_share', True, False), 'e2': ('residents_in_bfpl12_share', True, False),
}
REF = {}
for k, (col, hw, scaled) in ITEM_SPEC.items():
    x = orig[col].dropna().astype(float)
    REF[k] = x / x.median() if scaled else x
    log[f'ref_{k}'] = dict(n=int(len(x)), median=float(x.median()), min=float(x.min()), max=float(x.max()))


def pct_item(item, v, denom=None):
    _, hw, scaled = ITEM_SPEC[item]
    if pd.isna(v):
        return np.nan
    if scaled:
        if denom is None or pd.isna(denom):
            return np.nan
        v = v / denom
    return place(v, REF[item], hw)


chk = {}
for k, (col, hw, scaled) in ITEM_SPEC.items():        # placement self-check
    x = orig[col].astype(float)
    got = pd.Series([place((v / x.dropna().median() if scaled else v) if pd.notna(v) else np.nan, REF[k], hw) for v in x])
    r = x.rank(pct=True)
    want = r if hw else 1 - r + 1 / x.notna().sum()
    chk[k] = float((got - want).abs().max())
log['placement_selfcheck_max_abs_diff'] = chk
assert max(chk.values()) < 0.02, chk

EVENT = {   # event -> SEIFA edition, PIA (fire fy_start, previous fy_start), SALM column, LGGC fy_start of the vintage year
    'SA_2015_sampson_flat': dict(seifa='2011', pia=(2014, 2013), salm='Jun-14', lggc=2013),
    'SA_2015_pinery': dict(seifa='2011', pia=(2015, 2014), salm='Jun-15', lggc=2014),
    'SA_2019_cudlee_creek': dict(seifa='2016', pia=(2019, 2018), salm='Jun-19', lggc=2018),
    'SA_2019_20_kangaroo_island': dict(seifa='2016', pia=(2019, 2018), salm='Jun-19', lggc=2018),
    'SA_2019_20_keilira': dict(seifa='2016', pia=(2019, 2018), salm='Jun-19', lggc=2018),
}
# ---------------------------------------------------------------- V sources
s11 = pd.read_excel(RAW / 'p1_nsw2013/2033.0.55.001_lga_indexes_2011.xls', sheet_name='Table 3', header=None).iloc[6:, [0, 1, 3]]
s11.columns = ['code', 'name', 'score']
s16 = pd.read_excel(P1 / 'raw/seifa_2016.xls', sheet_name='Table 1', header=None).iloc[6:, [0, 1, 2]]
s16.columns = ['code', 'name', 'score']
SEIFA = {}
for k, s in (('2011', s11), ('2016', s16)):
    s = s.dropna(subset=['code']).copy()
    s['code'] = pd.to_numeric(s.code, errors='coerce').dropna().astype(int).astype(str)
    s['score'] = pd.to_numeric(s.score, errors='coerce')
    SEIFA[k] = s.dropna(subset=['code']).set_index('code').score

pia = pd.read_csv(P1 / 'data/income_area_year_by_release.csv', dtype={'geographic_id': str})
pia = pia[pia.geographic_id.str.fullmatch(r'\d{5}')]


def pia_release(fy, prev):
    have = pia.groupby('source_id').fy_start.apply(set)
    ok = [r for r, s in have.items() if {fy, prev} <= s]
    pub = pia.groupby('source_id').publication_date.max()
    return max(ok, key=lambda r: pub[r])


sal = pd.read_csv(FED / 'data/salm/salm_lga.csv', skiprows=2, dtype=str).dropna(subset=['LGA Code (2025 ASGS)'])
sal = sal[sal['Data Item'] == 'Smoothed unemployment rate (%)'].set_index('LGA Code (2025 ASGS)')

# ---------------------------------------------------------------- F sources (LGGC), whole-state table
L = pd.read_csv(FED / 'data/extra_fires/lggc_items.csv')
L['cash_cover'] = (L.cash + L.other_fin_assets) / ((L.total_op_expenses - L.depreciation) / 12)
L['own_source'] = 100 * (1 - L.grants / L.total_op_revenue)
L['operating_ratio'] = 100 * L.op_surplus / L.total_op_revenue
L['key'] = L.council.map(norm_name).replace({'mallala': 'adelaide plains'})
L = L[L.council != 'State Totals']
# cross-check of the own operating ratio with the published whole-number Report 8 value
L['osr_diff'] = (L.operating_ratio - L.osr_published).abs()
log['operating_ratio_vs_report8_max_abs_diff_pct_points'] = {int(fy): float(g.osr_diff.max()) for fy, g in L.groupby('fy')}
F_ITEMS = ['cash_cover', 'own_source', 'operating_ratio']
f_by_event = {}
for ev, info in EVENT.items():
    g = L[L.fy == info['lggc']]
    comp = {}
    for item in F_ITEMS:
        a = float(g[item].median())
        b = float(orig[ITEM_SPEC[item][0]].dropna().median())
        ratio = a / b if b else np.nan
        comp[item] = dict(n_sa=int(g[item].notna().sum()), median_sa=a, median_nsw_original=b, ratio=ratio, kept=bool(np.isfinite(ratio) and abs(ratio - 1) <= 0.30))
    kept = [k for k, v in comp.items() if v['kept']]
    f_by_event[ev] = dict(items=comp, kept=kept, F_used=len(kept) >= 2)
log['f_comparability_30pct_rule'] = f_by_event

# ---------------------------------------------------------------- assemble
rows, items, match = [], [], []
for r in roster.itertuples():
    info = EVENT[r.event]
    g = geo[(geo.lga_vintage == r.lga_vintage) & (geo.lga_code == r.lga_code)].iloc[0]
    code18, code15 = r.code_lga2018, r.code_lga2015
    flags, notes = {}, []
    # H, E
    hp, ep = {}, {}
    if g.mapped:
        hp = {'h1': pct_item('h1', g.h1_bpa_high_share), 'h2': pct_item('h2', g.h2_bpa_high_medium_share)}
        ep = {'e1': pct_item('e1', g.e1_dwellings_in_bpa_hm_share), 'e2': pct_item('e2', g.e2_residents_in_bpa_hm_share)}
        flags['H'] = 'computed_low_confidence (SA BPA High/Medium shares, different classification from NSW BFPL, placed in NSW scale; NVIS omitted)'
        flags['E'] = 'computed_low_confidence (BPA High+Medium, ABS 2021 mesh blocks)'
    else:
        flags['H'] = flags['E'] = 'unavailable (council not mapped by BPA: < 1% of area covered; Amendment 1)'
    H = np.nanmean(list(hp.values())) if hp else np.nan
    E = np.nanmean(list(ep.values())) if ep else np.nan
    # V
    it = {}
    it['seifa_irsd'] = float(SEIFA[info['seifa']].get(code15 if info['seifa'] == '2011' else code18, np.nan))
    fy, prev = info['pia']
    rel = pia_release(fy, prev)
    P = pia[(pia.source_id == rel) & (pia.fy_start == prev)]
    vint = int(P.boundary_vintage.iloc[0])
    pcode = code18 if vint >= 2018 else code15
    it['median_income'] = float(P.set_index('geographic_id').median_income_aud.get(pcode, np.nan))
    nsw_med_income = float(P[P.geographic_id.str[0] == '1'].median_income_aud.median())
    sv = pd.to_numeric(sal[info['salm']].str.replace(',', ''), errors='coerce')
    it['unemp_rate'] = float(sv.get(code18, np.nan))
    nsw_med_unemp = float(sv[sv.index.str[0] == '1'].median())
    vp = {'seifa_irsd': pct_item('seifa_irsd', it['seifa_irsd']), 'median_income': pct_item('median_income', it['median_income'], nsw_med_income),
          'unemp_rate': pct_item('unemp_rate', it['unemp_rate'], nsw_med_unemp)}
    V = np.nanmean(list(vp.values())) if any(pd.notna(x) for x in vp.values()) else np.nan
    flags['V'] = f"computed (SEIFA {info['seifa']}; PIA {rel} FY{prev}-{str(prev + 1)[2:]}; SALM {info['salm']})"
    # F
    fp = {}
    fe = f_by_event[r.event]
    key = norm_name(r.lga_name).replace('mallala', 'adelaide plains')
    lrow = L[(L.fy == info['lggc']) & (L.key == key)]
    match.append(dict(event=r.event, lga_code=r.lga_code, lga_name=r.lga_name, key=key, lggc_matches=len(lrow), lggc_name=(lrow.council.iloc[0] if len(lrow) else '')))
    if fe['F_used'] and len(lrow) == 1:
        for item in fe['kept']:
            v = float(lrow[item].iloc[0])
            it[item] = v
            fp[item] = pct_item(item, v)
        flags['F'] = 'computed_substitute (LGGC ' + ', '.join(fe['kept']) + f"; FY{info['lggc']}-{str(info['lggc'] + 1)[2:]})"
    else:
        flags['F'] = 'unavailable (' + ('fewer than 2 items pass the 30% rule' if not fe['F_used'] else 'council not found in LGGC') + ')'
    F = np.nanmean(list(fp.values())) if fp and any(pd.notna(x) for x in fp.values()) else np.nan
    for blk, d in (('H', hp), ('E', ep), ('V', vp), ('F', fp)):
        for k, v in d.items():
            items.append(dict(event=r.event, region_id=r.lga_code, region_name=r.lga_name, block=blk, item=k, raw=it.get(k), pct=v))
    blocks = {'H': H, 'E': E, 'V': V, 'F': F}
    present = {k: v for k, v in blocks.items() if pd.notna(v)}
    rows.append(dict(event=r.event, state='SA', region_id=r.lga_code, region_name=r.lga_name, code_lga2018=code18, first_fire_start=r.first_fire_start,
                     share_burned=r.share, burn_area_ha=r.burned_km2 * 100, lga_area_km2=r.lga_area_km2, bpa_mapped=bool(g.mapped),
                     H=H, E=E, V=V, F=F, blocks_n=len(present), risk_add_avail=float(np.mean(list(present.values()))) if present else np.nan,
                     S1_V=V, S2_HV=(float(np.mean([H, V])) if pd.notna(H) and pd.notna(V) else np.nan),
                     score_flags=' | '.join(f'{k}: {v}' for k, v in flags.items()), score_notes='; '.join(notes)))
S = pd.DataFrame(rows)
S.to_csv(RES / 'SCORES_new_rows.csv', index=False)
pd.DataFrame(items).to_csv(RES / 'SCORE_ITEMS_new_rows.csv', index=False)
pd.DataFrame(match).to_csv(RES / 'lggc_council_match.csv', index=False)
json.dump(log, open(RES / 'score_build_log.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in log.items() if k.startswith(('f_', 'placement', 'operating'))}, indent=1, default=str))
print(S[['event', 'region_name', 'share_burned', 'bpa_mapped', 'H', 'E', 'V', 'F', 'blocks_n', 'risk_add_avail']].round(3).to_string())
