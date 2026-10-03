"""Experiment 9, v3: build the fire-matched pillar indicators and X23 defined in PRESPEC.md (Addendum v3).
No model is fitted here. Writes inputs/v3_indicators.csv (one row per master row: agrn, region_id + indicators),
inputs/x23_councils.csv (all NSW councils, both Census years) and results/V3_BUILD_LOG.json (coverage).

Run: uv run python build_v3_indicators.py   (needs duckdb + geopandas from the project environment)
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / 'fire_event_dataset/data/raw'
E7 = ROOT / 'Experiment 7'
E10 = ROOT / 'Experiment 10'
sys.path.insert(0, str(E7))
import build_y2 as B  # noqa: E402

LOG = {}


def norm(s):
    s = str(s).lower().replace('&', 'and')
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'\b(city of|the|council|shire|regional|municipal|city|area)\b', ' ', s)
    return re.sub(r'[^a-z]', '', s)


def councils():
    it = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})
    c = it[['region_id', 'region_name_x']].rename(columns={'region_name_x': 'name'})
    c['key'] = c.name.map(norm)
    return c


def master():
    m, _ = B.load()
    m = m[['agrn', 'region_id', 'region_name', 'F', 'first_fire_start']].copy()
    m['agrn'] = m.agrn.astype(str)
    m['region_id'] = m.region_id.astype(str)
    m['m0'] = pd.to_datetime(m.first_fire_start).dt.to_period('M')
    return m


def unburned(m, F):
    """region_ids with no master row in fire financial year F."""
    return set(councils().region_id) - set(m.loc[m.F == F, 'region_id'])


def excess_monthly(m, series, fn, name):
    """series: DataFrame index=month Period, columns=region_id (monthly values). fn(col, m0) -> change or nan.
    Row value = own change - median change of unburned councils (same m0)."""
    out = []
    for r in m.itertuples():
        if r.region_id not in series.columns:
            out.append(np.nan); continue
        own = fn(series[r.region_id], r.m0)
        if np.isnan(own):
            out.append(np.nan); continue
        comp = [fn(series[c], r.m0) for c in unburned(m, r.F) if c in series.columns]
        comp = [v for v in comp if not np.isnan(v)]
        out.append(own - np.median(comp) if comp else np.nan)
    v = pd.Series(out, index=m.index)
    LOG[name] = int(v.notna().sum())
    return v


# ------------------------------------------------------------------ IL1 tourism traffic
def traffic_monthly():
    import duckdb
    con = duckdb.connect(str(ROOT / 'data/aussef.duckdb'), read_only=True)
    parts = ' union all '.join(f'select station_key, classification_seq, date, daily_total from raw.manual_traffic_hourly_permanent_{i}'
                               for i in range(5))
    d = con.execute(f"""
        with h as ({parts}),
        cls as (select station_key, min(classification_seq) as cmin from h group by 1)
        select h.station_key, cast(h.date as date) as day, sum(try_cast(h.daily_total as double)) as vol
        from h join cls on h.station_key = cls.station_key and h.classification_seq = cls.cmin
        group by 1, 2""").df()
    ref = con.execute('select distinct station_key, lga from raw.manual_traffic_station_reference').df()
    d = d.merge(ref, on='station_key', how='left')
    LOG['traffic_classification_note'] = 'per station the lowest classification_seq present (all vehicles where recorded)'
    return d


def il1_traffic(m):
    d = traffic_monthly()
    c = councils()
    d['region_id'] = d.lga.map(norm).map(c.set_index('key').region_id)
    LOG['traffic_stations_matched'] = int(d.dropna(subset=['region_id']).station_key.nunique())
    d = d.dropna(subset=['region_id', 'vol'])
    d['month'] = pd.to_datetime(d.day).dt.to_period('M')
    days = d.groupby(['station_key', 'month']).agg(vol=('vol', 'mean'), n=('vol', 'size')).reset_index()
    days['ndays'] = days.month.map(lambda p: p.days_in_month)
    days['ok'] = days.n >= 0.5 * days.ndays
    st_reg = d.drop_duplicates('station_key').set_index('station_key').region_id

    def station_change(g, m0):
        g = g.set_index('month')
        W = [m0 + k for k in range(4)]
        Bm = [m0 - 12 + k for k in range(4)] + [m0 - 24 + k for k in range(4)]
        w, b = g.reindex(W), g.reindex(Bm)
        if (w.ok == True).sum() < 2 or (b.ok == True).sum() < 4:  # noqa: E712
            return np.nan
        wv, bv = w.loc[w.ok == True, 'vol'].mean(), b.loc[b.ok == True, 'vol'].mean()  # noqa: E712
        return np.log(wv / bv) if wv > 0 and bv > 0 else np.nan

    groups = {k: g for k, g in days.groupby('station_key')}
    by_reg = {}
    for k, reg in st_reg.items():
        by_reg.setdefault(reg, []).append(k)
    cache = {}

    def council_change(reg, m0):
        key = (reg, m0)
        if key not in cache:
            v = [station_change(groups[k], m0) for k in by_reg.get(reg, []) if k in groups]
            v = [x for x in v if not np.isnan(x)]
            cache[key] = np.median(v) if v else np.nan
        return cache[key]

    out = []
    for r in m.itertuples():
        own = council_change(r.region_id, r.m0)
        if np.isnan(own):
            out.append(np.nan); continue
        comp = [council_change(c, r.m0) for c in unburned(m, r.F) if c in by_reg]
        comp = [v for v in comp if not np.isnan(v)]
        out.append(own - np.median(comp) if comp else np.nan)
    v = pd.Series(out, index=m.index)
    LOG['IL1_traffic_rows'] = int(v.notna().sum())
    return v


# ------------------------------------------------------------------ IL2 / IL3 affected small areas
def sa2_to_council():
    mb = pd.read_excel(RAW / 'grp_insurance/asgs/MB_2021_AUST.xlsx', dtype=str,
                       usecols=['MB_CODE_2021', 'SA2_CODE_2021', 'STATE_CODE_2021'])
    lga = pd.read_excel(RAW / 'grp_insurance/asgs/LGA_2021_AUST.xlsx', dtype=str)
    lga = lga[[c for c in lga.columns if c in ('MB_CODE_2021', 'LGA_CODE_2021')]]
    cnt = pd.concat([pd.read_excel(RAW / 'grp_insurance/asgs/Mesh_Block_Counts_2021.xlsx', sheet_name=t, header=6,
                                   dtype={'MB_CODE_2021': str}) for t in ('Table 1', 'Table 1.1')], ignore_index=True)
    cnt = cnt[cnt.MB_CODE_2021.astype(str).str.fullmatch(r'\d{11}', na=False)][['MB_CODE_2021', 'Person']]
    x = mb[mb.STATE_CODE_2021 == '1'].merge(lga, on='MB_CODE_2021').merge(cnt, on='MB_CODE_2021', how='left')
    x['Person'] = pd.to_numeric(x.Person, errors='coerce').fillna(0)
    s = x.groupby(['SA2_CODE_2021', 'LGA_CODE_2021']).Person.sum().reset_index()
    s = s.sort_values('Person').drop_duplicates('SA2_CODE_2021', keep='last')
    return s.set_index('SA2_CODE_2021').LGA_CODE_2021


def il_sa2(m):
    sys.path.insert(0, str(E7))
    import day5_sa2_income as D5
    s2c = sa2_to_council()
    info = pd.read_parquet(E7 / 'panels/sa2_info.parquet')
    dose = pd.read_parquet(E7 / 'panels/sa2_fy_dose.parquet')
    inc, _ = D5.panel()
    inc = inc.merge(info[['SA2', 'pop', 'GCCSA']], on='SA2')
    inc = inc[(inc['pop'] >= 100) & (inc['sum'] > 0)]
    I = inc.set_index(['SA2', 'fy'])['sum']
    b = pd.read_parquet(E7 / 'panels/sa2_businesses.parquet')
    b = b[b.in_sa2_info & (b.value > 0)]
    Bz = b.set_index(['SA2', 'june']).value
    gcc = info.set_index('SA2').GCCSA
    D = dose[dose.dose > 0]
    dosed = D.groupby('SA2').fy.apply(set).to_dict()
    def zero_dose(sa2, years):
        return not (dosed.get(sa2, set()) & set(years))

    def change(series, sa2, a, b_):
        try:
            x, y = series.loc[(sa2, a)], series.loc[(sa2, b_)]
        except KeyError:
            return np.nan
        return np.log(y / x) if x > 0 and y > 0 else np.nan

    sa2s = info.SA2.tolist()
    ctrl_cache = {}

    def control(kind, F, g):
        k = (kind, F, g)
        if k not in ctrl_cache:
            if kind == 'inc':
                v = [change(I, s, F - 1, F + 2) for s in sa2s if gcc.get(s) == g and zero_dose(s, range(F - 1, F + 3))]
            else:
                v = [change(Bz, s, F, F + 2) for s in sa2s if gcc.get(s) == g and zero_dose(s, range(F - 1, F + 3))]
            v = [x for x in v if not np.isnan(x)]
            ctrl_cache[k] = np.mean(v) if v else np.nan
        return ctrl_cache[k]

    il2, il3 = [], []
    for r in m.itertuples():
        aff = D[(D.fy == r.F) & (D.SA2.map(s2c) == r.region_id)]
        vals2, vals3 = [], []
        for a in aff.itertuples():
            g = gcc.get(a.SA2)
            c2 = change(I, a.SA2, r.F - 1, r.F + 2)
            if not np.isnan(c2):
                vals2.append((c2 - control('inc', r.F, g), a.persons))
            c3 = change(Bz, a.SA2, r.F, r.F + 2)
            if not np.isnan(c3):
                vals3.append((c3 - control('biz', r.F, g), a.persons))
        w = lambda v: np.average([x for x, _ in v], weights=[max(p, 1e-9) for _, p in v]) if v else np.nan  # noqa: E731
        il2.append(w(vals2)); il3.append(w(vals3))
    il2, il3 = pd.Series(il2, index=m.index), pd.Series(il3, index=m.index)
    LOG['IL2_income_rows'], LOG['IL3_business_rows'] = int(il2.notna().sum()), int(il3.notna().sum())
    return il2, il3


# ------------------------------------------------------------------ FP2 / FP3 audited statements
FIRE_PAT = re.compile(r'bush ?fire|rural fire|fire protection|fire service|emergency services|disaster recover|'
                      r'natural disaster|bushfire relief|bushfire recovery', re.I)
EXCL_PAT = re.compile(r'storm|flood', re.I)


def statement_shares(path, items):
    t = pd.read_csv(path, dtype={'region_id': str})
    t['F'] = t.fy.str[:4].astype(int)
    lines = t[t['item'].isin(items) & t.label.fillna('').str.contains(FIRE_PAT) & ~t.label.fillna('').str.contains(EXCL_PAT)]
    fire = lines.groupby(['region_id', 'F']).value_aud.sum()
    te = t[t['item'] == 'total_expenses'].groupby(['region_id', 'F']).value_aud.sum()
    cap = t[t['item'] == 'capex_ippe'].groupby(['region_id', 'F']).value_aud.sum()
    s = pd.DataFrame({'te': te, 'fire': fire, 'cap': cap})
    s = s[s.te > 0]
    s['fire_share'] = s.fire.fillna(0) / s.te
    s['cap_share'] = s.cap / s.te
    return s


def jump(s, reg, F, col):
    def val(y):
        try:
            return s.loc[(reg, y), col]
        except KeyError:
            return np.nan
    post = [val(F), val(F + 1)]
    pre = [val(F - 2), val(F - 1)]
    post, pre = [x for x in post if pd.notna(x)], [x for x in pre if pd.notna(x)]
    return np.mean(post) - np.mean(pre) if post and pre else np.nan


def fp_statements(m):
    fs = statement_shares(E10 / 'A_fire_councils/statements_tidy.csv', ['disaster_grant_operating', 'disaster_grant_capital'])
    cs = statement_shares(E10 / 'A_comparison_councils/statements_tidy.csv',
                          ['disaster_grant_operating', 'disaster_grant_capital', 'bushfire_emergency_services_grant'])
    # fire councils whose fire-grant item was never extracted but have core items: fire share 0 only if a grants note
    # was read; we cannot tell, so rows with no disaster lines at all in a statement year keep fire_share = 0 only when
    # that council has disaster lines in some other year (grants note was extracted for this council).
    has_lines = set(fs[fs.fire.notna()].index.get_level_values(0))
    fs.loc[~fs.index.get_level_values(0).isin(has_lines), 'fire_share'] = np.nan
    comp_regs = cs.index.get_level_values(0).unique()
    out2, out3 = [], []
    for r in m.itertuples():
        own2, own3 = jump(fs, r.region_id, r.F, 'fire_share'), jump(fs, r.region_id, r.F, 'cap_share')
        c2 = [jump(cs, c, r.F, 'fire_share') for c in comp_regs]
        c3 = [jump(cs, c, r.F, 'cap_share') for c in comp_regs]
        c2, c3 = [x for x in c2 if pd.notna(x)], [x for x in c3 if pd.notna(x)]
        out2.append(own2 - np.median(c2) if pd.notna(own2) and c2 else np.nan)
        out3.append(own3 - np.median(c3) if pd.notna(own3) and c3 else np.nan)
    a, b = pd.Series(out2, index=m.index), pd.Series(out3, index=m.index)
    LOG['FP2_fire_grant_rows'], LOG['FP3_capex_rows'] = int(a.notna().sum()), int(b.notna().sum())
    return a, b


# ------------------------------------------------------------------ SL2 domestic violence
def sl2_dv(m):
    import openpyxl
    wb = openpyxl.load_workbook(RAW / 'bocsar/RCI_offencebymonth.xlsm', read_only=True)
    rows = wb['Data'].iter_rows(values_only=True)
    hdr = next(rows)
    months = [pd.Period(h, 'M') for h in hdr[3:]]
    data = {}
    for r in rows:
        if r[2] == 'Domestic violence related assault':
            data[r[0]] = r[3:]
    df = pd.DataFrame(data, index=months).apply(pd.to_numeric, errors='coerce')
    c = councils().set_index('key').region_id
    df.columns = [c.get(norm(x)) for x in df.columns]
    LOG['SL2_bocsar_lgas_matched'] = int(pd.Series(df.columns).notna().sum())
    df = df.loc[:, pd.Series(df.columns).notna().to_numpy()]
    df = df.T.groupby(level=0).sum().T
    last = df.index.max()

    def fn(col, m0):
        post = col.reindex([m0 + k for k in range(6, 25) if m0 + k <= last])
        pre = col.reindex([m0 - k for k in range(1, 25)])
        if post.notna().sum() < 12 or pre.notna().sum() < 12:
            return np.nan
        a, b = post.mean(), pre.mean()
        return np.log(a / b) if a > 0 and b > 0 else np.nan
    return excess_monthly(m, df, fn, 'SL2_dv_rows')


# ------------------------------------------------------------------ SL3 rebuild gap
def sl3_rebuild(m):
    fr = []
    for f in sorted((RAW / 'abs_building_approvals').glob('BA_LGA20*.csv')):
        d = pd.read_csv(f, dtype=str)
        if 'REGION_TYPE' not in d:
            continue
        d = d[d.REGION_TYPE.str.startswith('LGA') & d.REGION.str.startswith('1')]
        fr.append(d[['REGION', 'TIME_PERIOD', 'OBS_VALUE']])
    d = pd.concat(fr)
    d['month'] = pd.PeriodIndex(d.TIME_PERIOD, freq='M')
    d['v'] = pd.to_numeric(d.OBS_VALUE, errors='coerce')
    ba = d.pivot_table(index='month', columns='REGION', values='v', aggfunc='last')
    dl = pd.read_csv(ROOT / 'Experiment 6/followups/dl_fill/DL_FILLED.csv', dtype={'agrn': str, 'region_id': str})
    homes = m[['agrn', 'region_id']].merge(dl, on=['agrn', 'region_id'], how='left')
    homes = (homes.homes_per_1000_v2_inferred * homes.dwellings / 1000).to_numpy()
    out = []
    for i, r in enumerate(m.itertuples()):
        h = homes[i]
        if not (h >= 5) or r.region_id not in ba.columns:
            out.append(np.nan); continue
        col = ba[r.region_id]
        pre = col.reindex([r.m0 - k for k in range(1, 13)])
        post = col.reindex([r.m0 + k for k in range(1, 25)])
        if pre.notna().sum() < 6 or post.notna().sum() < 24:
            out.append(np.nan); continue
        extra = post.sum() - 24 * pre.mean()
        out.append(1 - np.clip(extra / h, 0, 1))
    v = pd.Series(out, index=m.index)
    LOG['SL3_rebuild_rows'] = int(v.notna().sum())
    return v


# ------------------------------------------------------------------ X23
def x23():
    """Share of occupied private dwellings owned outright, by council, Census 2016 (G33) and 2021 (G37)."""
    out = {}
    base = ROOT / 'fire_event_dataset/data/abs'
    for yr, pat, tab in [(2016, 'gcp2016/*/2016Census_G33_NSW_LGA.csv', 'G33'), (2021, 'gcp2021/*/2021Census_G37_NSW_LGA.csv', 'G37')]:
        fs = sorted(base.glob(pat))
        if not fs:
            LOG[f'x23_{yr}'] = 'file not found'; continue
        g = pd.read_csv(fs[0])
        code = [c for c in g.columns if c.startswith('LGA_CODE')][0]
        oo = [c for c in g.columns if re.match(r'^(O_OR|Owned_outright)_Total$', c, re.I)]
        tot = [c for c in g.columns if re.match(r'^Total_Total$', c, re.I)]
        if not oo or not tot:
            LOG[f'x23_{yr}'] = f'columns not found: {list(g.columns)[:12]}'; continue
        s = pd.DataFrame({'region_id': g[code].astype(str).str.replace('LGA', ''), 'x23': g[oo[0]] / g[tot[0]]})
        out[yr] = s.set_index('region_id').x23
        LOG[f'x23_{yr}'] = f'{fs[0].name}: {oo[0]} / {tot[0]}, {len(s)} councils'
    return pd.DataFrame(out)


def main():
    m = master()
    T = m[['agrn', 'region_id']].copy()
    cache = HERE / 'inputs/_il1_cache.csv'
    if cache.exists():
        T['IL1_traffic_excess'] = pd.read_csv(cache).IL1_traffic_excess.to_numpy()
        LOG['IL1_traffic_rows'] = int(T.IL1_traffic_excess.notna().sum())
    else:
        T['IL1_traffic_excess'] = il1_traffic(m)
        T[['IL1_traffic_excess']].to_csv(cache, index=False)
    T['IL2_income_affected_excess'], T['IL3_business_affected_excess'] = il_sa2(m)
    T['FP2_fire_grant_jump_excess'], T['FP3_capex_jump_excess'] = fp_statements(m)
    T['SL2_dv_excess'] = sl2_dv(m)
    T['SL3_rebuild_gap'] = sl3_rebuild(m)
    X = x23()
    X.to_csv(HERE / 'inputs/x23_councils.csv')
    yr = np.where(m.F <= 2020, 2016, 2021)
    T['X23'] = [X[y].get(r) if y in X else np.nan for y, r in zip(yr, m.region_id)]
    # deviation 1 (v3): councils whose 2016 code is not in the 2016 file (renamed/re-coded) fall back to Census 2021
    miss = T.X23.isna()
    T.loc[miss, 'X23'] = [X[2021].get(r) for r in m.region_id[miss]]
    LOG['X23_fallback_2021_rows'] = int(miss.sum())
    LOG['X23_rows'] = int(T.X23.notna().sum())
    T.to_csv(HERE / 'inputs/v3_indicators.csv', index=False)
    json.dump(LOG, open(HERE / 'results/V3_BUILD_LOG.json', 'w'), indent=1)
    print(json.dumps(LOG, indent=1))


if __name__ == '__main__':
    (HERE / 'inputs').mkdir(exist_ok=True)
    main()
