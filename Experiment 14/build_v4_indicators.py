"""Experiment 14: build the v4 indicators defined in PRESPEC.md (locked in LOCK_PRESPEC.txt). No model is fitted.
v4 was chosen AFTER seeing the v3 results.

Writes inputs/v4_indicators.csv (one row per master row: agrn, region_id + every indicator column used by any Y
version), inputs/FAR_SETS.csv (comparison councils per fire year) and results/V4_BUILD_LOG.json (coverage).
Experiment 9's build_v3_indicators.py is imported read-only for its helpers (master rows, council names, statements).

Run: python3 build_v4_indicators.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'Experiment 9'))
import build_v3_indicators as V  # noqa: E402  (read-only helpers)

LOG = {}
MIN_COMP = 5


# ------------------------------------------------------------------ rows and comparison sets
def master():
    m = V.master()
    w = V.B.load()[0]
    extra = w[['agrn', 'region_id', 'SL_deaths_sourced', 'SL_deaths_responders', 'SL_injuries_sourced',
               'X_council_council_population_pre']].copy()
    extra['agrn'] = extra.agrn.astype(str); extra['region_id'] = extra.region_id.astype(str)
    return m.merge(extra, on=['agrn', 'region_id'], how='left', validate='1:1')


def olg_groups():
    """Metro / Regional / Rural per council (same source and mapping as Experiment 12 audit script 05)."""
    x = pd.read_excel(ROOT / 'fire_event_dataset/data/olg/time-series-data-2018-2019.xlsx', sheet_name='2018_19_Councils',
                      header=None).iloc[3:, :3]
    x.columns = ['council', 'grp', 'cls']
    G = {'Metropolitan': 'Metro', 'Metropolitan Fringe': 'Metro', 'Regional Town/City': 'Regional', 'Rural': 'Rural',
         'Large Rural': 'Rural'}
    key = V.councils().set_index('key').region_id
    x['rid'] = x.council.map(V.norm).map(key)
    x['G'] = x.cls.map(G)
    g = x.dropna(subset=['rid', 'G']).drop_duplicates('rid').set_index('rid').G.to_dict()
    LOG['olg_group_councils'] = len(g)
    return g


class Comparison:
    """FAR councils per fire year F: no master row in F, not adjacent to a council with a master row in F,
    < 0.5% of area burned in FY F. mode 'olg' further restricts to the row council's OLG group."""

    def __init__(self, m):
        self.all = set(V.councils().region_id)
        adj = pd.read_csv(ROOT / 'Experiment 12/results/ADJACENCY.csv', dtype=str)
        nb = adj.groupby('region_id').neighbour_id.apply(set).to_dict()
        f = pd.read_csv(ROOT / 'fire_event_dataset/out/fires.csv', low_memory=False, dtype={'region_id': str})
        t = pd.to_datetime(f.date_start)
        f['fy'] = np.where(t.dt.month >= 7, t.dt.year, t.dt.year - 1)
        b = f.groupby(['region_id', 'fy']).share_of_region_burned.sum()
        self.far = {}
        rows = []
        for F, g in m.groupby('F'):
            burned = set(g.region_id)
            near = set().union(*[nb.get(c, set()) for c in burned])
            hot = set(b[(b.index.get_level_values(1) == F) & (b >= 0.005)].index.get_level_values(0))
            far = self.all - burned - near - hot
            self.far[F] = far
            rows.append(dict(F=F, councils=len(self.all), master=len(burned), neighbours=len(near - burned),
                             burned_ge_0_5pct_not_master_not_neighbour=len(hot - burned - near), far=len(far),
                             far_ids=' '.join(sorted(far))))
        self.table = pd.DataFrame(rows)
        self.grp = olg_groups()

    def ids(self, F, region_id, mode='far'):
        s = self.far[F]
        if mode == 'olg':
            g = self.grp.get(region_id)
            s = {c for c in s if g is not None and self.grp.get(c) == g}
        return s


def excess(m, own_fn, comp, mode, name, key_fn):
    """own_fn(council_id, row) -> value or nan. Excess = own - median over comparison councils (>= MIN_COMP values).
    key_fn(row) -> cache key for the comparison median (must include everything own_fn depends on, plus F)."""
    out, cache = [], {}
    for r in m.itertuples():
        own = own_fn(r.region_id, r)
        if pd.isna(own):
            out.append(np.nan); continue
        ids = comp(r)
        k = (key_fn(r), mode, frozenset(ids))
        if k not in cache:
            v = [own_fn(c, r) for c in ids]
            v = [x for x in v if pd.notna(x)]
            cache[k] = np.median(v) if len(v) >= MIN_COMP else np.nan
        out.append(own - cache[k] if pd.notna(cache[k]) else np.nan)
    s = pd.Series(out, index=m.index)
    LOG[f'{name}_rows'] = int(s.notna().sum())
    return s


def fy_change(table, cid, F, post_offsets, log=False):
    """mean(table[cid] over available post FYs) - mean over available pre FYs (F-2, F-1)."""
    if cid not in table:
        return np.nan
    col = table[cid]
    post = col.reindex([F + k for k in post_offsets]).dropna()
    pre = col.reindex([F - 2, F - 1]).dropna()
    if post.empty or pre.empty:
        return np.nan
    return post.mean() - pre.mean()


FP_WINDOWS = {'main': [1, 2, 3], 'h0': [0], 'h12': [1, 2], 'h3': [3]}


# ------------------------------------------------------------------ FP1 grants per resident, FP4 cash cover (OLG)
def olg_tables():
    o = pd.read_parquet(ROOT / 'fire_event_dataset/data/olg/olg_long.parquet')
    # deviation 2 (audit a2): pre-2016 entities that share a name key with a post-merger council are different councils
    o = o[~o.council_name.isin(['Dubbo City Council', 'Murrumbidgee Shire Council', 'Parramatta City Council'])]
    w = o.pivot_table(index=['council_name_norm', 'fy_start'], columns='metric', values='value', aggfunc='first').reset_index()
    w['gpc'] = w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population
    c = V.councils()
    w['region_id'] = w.council_name_norm.map(V.norm).map(c.set_index('key').region_id)
    LOG['olg_names_unmatched'] = sorted(w.loc[w.region_id.isna(), 'council_name_norm'].unique().tolist())
    w = w.dropna(subset=['region_id'])
    G = np.log(w[w.gpc > 0].pivot_table(index='fy_start', columns='region_id', values='gpc', aggfunc='mean'))
    C = w.pivot_table(index='fy_start', columns='region_id', values='cash_expense_cover_ratio_months', aggfunc='mean')
    LOG['olg_councils_gpc'], LOG['olg_councils_cash'] = int(G.shape[1]), int(C.shape[1])
    return G, C


# ------------------------------------------------------------------ IL2 / IL3 with FAR control SA2s
def il_sa2(m, cmp, mode):
    sys.path.insert(0, str(V.E7))
    import day5_sa2_income as D5
    s2c = V.sa2_to_council()
    info = pd.read_parquet(V.E7 / 'panels/sa2_info.parquet')
    dose = pd.read_parquet(V.E7 / 'panels/sa2_fy_dose.parquet')
    inc, _ = D5.panel()
    inc = inc.merge(info[['SA2', 'pop', 'GCCSA']], on='SA2')
    inc = inc[(inc['pop'] >= 100) & (inc['sum'] > 0)]
    I = inc.set_index(['SA2', 'fy'])['sum']
    b = pd.read_parquet(V.E7 / 'panels/sa2_businesses.parquet')
    b = b[b.in_sa2_info & (b.value > 0)]
    Bz = b.set_index(['SA2', 'june']).value
    gcc = info.set_index('SA2').GCCSA
    D = dose[dose.dose > 0]
    dosed = D.groupby('SA2').fy.apply(set).to_dict()
    sa2s = info.SA2.tolist()

    def change(series, sa2, a, b_):
        try:
            x, y = series.loc[(sa2, a)], series.loc[(sa2, b_)]
        except KeyError:
            return np.nan
        return np.log(y / x) if x > 0 and y > 0 else np.nan

    cache = {}

    def control(kind, F, g, councils_ok):
        k = (kind, F, g, councils_ok)
        if k not in cache:
            yrs = set(range(F - 1, F + 3))
            ok = [s for s in sa2s if gcc.get(s) == g and not (dosed.get(s, set()) & yrs) and s2c.get(s) in councils_ok]
            v = [change(I, s, F - 1, F + 2) if kind == 'inc' else change(Bz, s, F, F + 2) for s in ok]
            v = [x for x in v if not np.isnan(x)]
            cache[k] = np.mean(v) if len(v) >= MIN_COMP else np.nan
        return cache[k]

    il2, il3 = [], []
    for r in m.itertuples():
        okc = frozenset(cmp.ids(r.F, r.region_id, mode))
        aff = D[(D.fy == r.F) & (D.SA2.map(s2c) == r.region_id)]
        v2, v3 = [], []
        for a in aff.itertuples():
            g = gcc.get(a.SA2)
            c2 = change(I, a.SA2, r.F - 1, r.F + 2)
            k2 = control('inc', r.F, g, okc)
            if not np.isnan(c2) and not np.isnan(k2):
                v2.append((c2 - k2, a.persons))
            c3 = change(Bz, a.SA2, r.F, r.F + 2)
            k3 = control('biz', r.F, g, okc)
            if not np.isnan(c3) and not np.isnan(k3):
                v3.append((c3 - k3, a.persons))
        wavg = lambda v: np.average([x for x, _ in v], weights=[max(p, 1e-9) for _, p in v]) if v else np.nan  # noqa: E731
        il2.append(wavg(v2)); il3.append(wavg(v3))
    a, b_ = pd.Series(il2, index=m.index), pd.Series(il3, index=m.index)
    LOG[f'IL2_{mode}_rows'], LOG[f'IL3_{mode}_rows'] = int(a.notna().sum()), int(b_.notna().sum())
    return a, b_


# ------------------------------------------------------------------ FP2 / FP3 statements
def statements():
    fs = V.statement_shares(V.E10 / 'A_fire_councils/statements_tidy.csv', ['disaster_grant_operating', 'disaster_grant_capital'])
    cs = V.statement_shares(V.E10 / 'A_comparison_councils/statements_tidy.csv',
                            ['disaster_grant_operating', 'disaster_grant_capital', 'bushfire_emergency_services_grant'])
    has = set(fs[fs.fire.notna()].index.get_level_values(0))
    LOG['FP2_councils_without_fire_lines_set_missing'] = sorted(set(fs.index.get_level_values(0)) - has)
    fs.loc[~fs.index.get_level_values(0).isin(has), 'fire_share'] = np.nan
    wide = lambda s, col: s[col].unstack(0)  # noqa: E731   index FY, columns region_id
    return {c: (wide(fs, c), wide(cs, c)) for c in ('fire_share', 'cap_share')}, set(cs.index.get_level_values(0))


def fp_statement(m, cmp, mode, tabs, comp_ids, col, win, name):
    own_t, comp_t = tabs[col]
    out, cache = [], {}
    for r in m.itertuples():
        own = fy_change(own_t, r.region_id, r.F, FP_WINDOWS[win])
        if pd.isna(own):
            out.append(np.nan); continue
        ids = comp_ids & cmp.ids(r.F, r.region_id, mode)
        k = (r.F, frozenset(ids))
        if k not in cache:
            v = [fy_change(comp_t, c, r.F, FP_WINDOWS[win]) for c in ids]
            v = [x for x in v if pd.notna(x)]
            cache[k] = (np.median(v) if len(v) >= MIN_COMP else np.nan, len(v))
        out.append(own - cache[k][0] if pd.notna(cache[k][0]) else np.nan)
    s = pd.Series(out, index=m.index)
    LOG[f'{name}_rows'] = int(s.notna().sum())
    LOG[f'{name}_comparison_n_min_max'] = [int(min(v[1] for v in cache.values())), int(max(v[1] for v in cache.values()))] if cache else None
    return s


# ------------------------------------------------------------------ SL1 rents, SL2 DV, SL3 rebuild
def rent_table():
    r = pd.read_parquet(ROOT / 'fire_event_dataset/data/rent/rent_lga_quarter.parquet')
    r['q'] = pd.PeriodIndex(r.quarter.astype(str), freq='Q')
    r['region_id'] = r.region_id.astype(str)
    return np.log(r.pivot_table(index='q', columns='region_id', values='median_rent', aggfunc='mean'))


def rent_fn(R, qq):
    def own(cid, row):
        if cid not in R:
            return np.nan
        q0 = row.m0.asfreq('Q')
        post = R[cid].reindex([q0 + k for k in qq]); pre = R[cid].reindex([q0 - k for k in range(1, 5)])
        return post.mean() - pre.mean() if post.notna().any() and pre.notna().sum() >= 2 else np.nan
    return own


def dv_table():
    import openpyxl
    wb = openpyxl.load_workbook(V.RAW / 'bocsar/RCI_offencebymonth.xlsm', read_only=True)
    it = wb['Data'].iter_rows(values_only=True)
    hdr = next(it)
    months = [pd.Period(x, 'M') for x in hdr[3:]]
    data = {r[0]: r[3:] for r in it if r[2] == 'Domestic violence related assault'}
    df = pd.DataFrame(data, index=months).apply(pd.to_numeric, errors='coerce')
    c = V.councils().set_index('key').region_id
    LOG['bocsar_unmatched'] = sorted(x for x in df.columns if c.get(V.norm(x)) is None)
    df.columns = [c.get(V.norm(x)) for x in df.columns]
    df = df.loc[:, pd.Series(df.columns).notna().to_numpy()]
    return df.T.groupby(level=0).sum().T


def dv_fn(D):
    last = D.index.max()

    def own(cid, row):
        if cid not in D:
            return np.nan
        post = D[cid].reindex([row.m0 + k for k in range(6, 25) if row.m0 + k <= last])
        pre = D[cid].reindex([row.m0 - k for k in range(1, 25)])
        if post.notna().sum() < 12 or pre.notna().sum() < 12:
            return np.nan
        a, b = post.mean(), pre.mean()
        return np.log(a / b) if a > 0 and b > 0 else np.nan
    return own


def approvals():
    fr = []
    for f in sorted((V.RAW / 'abs_building_approvals').glob('BA_LGA20*.csv')):
        d = pd.read_csv(f, dtype=str)
        if 'REGION_TYPE' not in d:
            continue
        d = d[d.REGION_TYPE.str.startswith('LGA') & d.REGION.str.startswith('1')]
        fr.append(d[['REGION', 'TIME_PERIOD', 'OBS_VALUE']])
    d = pd.concat(fr)
    # deviation 3 (audit x5): BA_LGA2018/2019 use older ABS codes for Armidale Regional and Inverell
    d['REGION'] = d.REGION.replace({'10130': '10180', '14200': '14220'})
    d['month'] = pd.PeriodIndex(d.TIME_PERIOD, freq='M')
    d['v'] = pd.to_numeric(d.OBS_VALUE, errors='coerce')
    return d.pivot_table(index='month', columns='REGION', values='v', aggfunc='last')


def sl3(m, cmp, mode):
    ba = approvals()
    dl = pd.read_csv(ROOT / 'Experiment 6/followups/dl_fill/DL_FILLED.csv', dtype={'agrn': str, 'region_id': str})
    hm = m[['agrn', 'region_id']].merge(dl, on=['agrn', 'region_id'], how='left')
    homes = (hm.homes_per_1000_v2_inferred * hm.dwellings / 1000).to_numpy()

    def pre_post(cid, m0):
        col = ba[cid]
        pre = col.reindex([m0 - k for k in range(1, 13)]); post = col.reindex([m0 + k for k in range(1, 25)])
        return pre, post

    gcache, out = {}, []
    for i, r in enumerate(m.itertuples()):
        h = homes[i]
        if not (h >= 5) or r.region_id not in ba.columns:
            out.append(np.nan); continue
        pre, post = pre_post(r.region_id, r.m0)
        if pre.notna().sum() < 6 or post.notna().sum() < 24:
            out.append(np.nan); continue
        ids = frozenset(c for c in cmp.ids(r.F, r.region_id, mode) if c in ba.columns)
        k = (r.m0, ids)
        if k not in gcache:
            gs = []
            for c in ids:
                p0, p1 = pre_post(c, r.m0)
                if p0.notna().sum() >= 6 and p1.notna().sum() == 24 and p0.mean() > 0:
                    gs.append(p1.mean() / p0.mean() - 1)
            gcache[k] = np.median(gs) if len(gs) >= MIN_COMP else np.nan
        g = gcache[k]
        if pd.isna(g):
            out.append(np.nan); continue
        extra = post.sum() - 24 * pre.mean() * (1 + g)
        out.append(1 - np.clip(extra / h, 0, 1))
    s = pd.Series(out, index=m.index)
    LOG[f'SL3_{mode}_rows'] = int(s.notna().sum())
    return s


# ------------------------------------------------------------------ main
def build(m, cmp, mode):
    """All excess-based indicator columns for one comparison mode ('far' main, 'olg' sensitivity)."""
    T = pd.DataFrame(index=m.index)
    comp = lambda r: cmp.ids(r.F, r.region_id, mode)  # noqa: E731
    sfx = '' if mode == 'far' else '_olg'
    T[f'IL2{sfx}'], T[f'IL3{sfx}'] = il_sa2(m, cmp, mode)
    G, C = olg_tables()
    for win, offs in FP_WINDOWS.items():
        T[f'FP1_{win}{sfx}'] = excess(m, lambda cid, r, offs=offs: fy_change(G, cid, r.F, offs), comp, mode,
                                     f'FP1_{win}{sfx}', lambda r: r.F)
    for win, offs in {'main': [0, 1], 'h0': [0], 'h12': [1]}.items():
        T[f'FP4_{win}{sfx}'] = excess(m, lambda cid, r, offs=offs: fy_change(C, cid, r.F, offs), comp, mode,
                                     f'FP4_{win}{sfx}', lambda r: r.F)
    tabs, comp_ids = statements()
    for col, nm in (('fire_share', 'FP2'), ('cap_share', 'FP3')):
        for win in FP_WINDOWS:
            T[f'{nm}_{win}{sfx}'] = fp_statement(m, cmp, mode, tabs, comp_ids, col, win, f'{nm}_{win}{sfx}')
    R = rent_table()
    T[f'SL1_main{sfx}'] = excess(m, rent_fn(R, range(5, 9)), comp, mode, f'SL1_main{sfx}', lambda r: (r.F, r.m0))
    T[f'SL1_h3{sfx}'] = excess(m, rent_fn(R, range(9, 17)), comp, mode, f'SL1_h3{sfx}', lambda r: (r.F, r.m0))
    T[f'SL2{sfx}'] = excess(m, dv_fn(dv_table()), comp, mode, f'SL2{sfx}', lambda r: (r.F, r.m0))
    T[f'SL3{sfx}'] = sl3(m, cmp, mode)
    return T


def main():
    m = master()
    cmp = Comparison(m)
    (HERE / 'inputs').mkdir(exist_ok=True); (HERE / 'results').mkdir(exist_ok=True)
    cmp.table.to_csv(HERE / 'inputs/FAR_SETS.csv', index=False)
    LOG['far_sets'] = cmp.table.drop(columns='far_ids').to_dict('records')
    T = m[['agrn', 'region_id', 'region_name', 'F']].copy()
    pop = pd.to_numeric(m.X_council_council_population_pre, errors='coerce')
    T['population_pre'] = pop
    T['SL4'] = pd.to_numeric(m.SL_deaths_sourced, errors='coerce') / pop * 1e5
    res = pd.to_numeric(m.SL_deaths_sourced, errors='coerce') - pd.to_numeric(m.SL_deaths_responders, errors='coerce').fillna(0)
    T['SL4_resident'] = res / pop * 1e5
    T['injuries_descriptive'] = pd.to_numeric(m.SL_injuries_sourced, errors='coerce')
    LOG['SL4_rows'], LOG['SL4_gt0'] = int(T.SL4.notna().sum()), int((T.SL4 > 0).sum())
    LOG['population_pre_missing'] = int(pop.isna().sum())
    for mode in ('far', 'olg'):
        B = build(m, cmp, mode)
        for c in B:
            T[c] = B[c].to_numpy()
    T.drop(columns=['region_name', 'F']).to_csv(HERE / 'inputs/v4_indicators.csv', index=False)
    json.dump(LOG, open(HERE / 'results/V4_BUILD_LOG.json', 'w'), indent=1, default=str)
    print(json.dumps({k: v for k, v in LOG.items() if k != 'far_sets'}, indent=1, default=str))
    print(cmp.table.drop(columns='far_ids').to_string(index=False))


if __name__ == '__main__':
    main()
