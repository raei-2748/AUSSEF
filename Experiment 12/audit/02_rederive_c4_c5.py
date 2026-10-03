"""Audit check (b): independent re-derivation of Experiment 11 primary results C4 (grants per resident, FY F+1)
and C5 (fire-related grant share, FY F+1). Written from Experiment 11/PRESPEC.md, not importing project code.
Writes rederived_c4_c5_rows.csv and prints n / rho, plus variants that isolate each difference."""
import re
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path('/Users/ray/Research/AUSSEF - Local'); OUT = Path(__file__).resolve().parent

# ---------------- rows, F, dose
m = pd.read_excel(ROOT / 'data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx', sheet_name='master', header=2,
                  keep_default_na=False, na_values=[''])
m = m[['agrn', 'region_id', 'region_name', 'first_fire_start']].copy()
m['agrn'] = m.agrn.astype(str); m['region_id'] = m.region_id.astype(int).astype(str)
t0 = pd.to_datetime(m.first_fire_start)
m['F'] = np.where(t0.dt.month >= 7, t0.dt.year, t0.dt.year - 1)
A = pd.read_csv(ROOT / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
A['dose_check'] = np.log1p(A.dwellings_in_fire / A.dwellings * 1000)
print('dose column = log1p(dwellings_in_fire/dwellings*1000)?', np.allclose(A.dose_check, A.log_homes_in_fire_per_1000, equal_nan=True))
m = m.merge(A[['agrn', 'region_id', 'log_homes_in_fire_per_1000']], on=['agrn', 'region_id'], how='left', validate='1:1')
D = m.log_homes_in_fire_per_1000
print('rows', len(m), 'dose missing', D.isna().sum())

# ---------------- council universe (129 incl. Unincorporated) and burned sets
cl = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})[['region_id', 'region_name_x']]
ALL = set(cl.region_id)
burned_in = m.groupby('F').region_id.apply(set).to_dict()

# ---------------- C4: OLG grants per resident
o = pd.read_parquet(ROOT / 'fire_event_dataset/data/olg/olg_long.parquet')
w = o.pivot_table(index=['council_name_norm', 'fy_start'], columns='metric', values='value', aggfunc='first').reset_index()
w['gpc'] = w['grants_contributions_revenue_pct'] / 100 * w['total_revenue_continuing_ops_aud'] / w['population']
# own name map: tokenised names (my rule): lowercase, drop parenthetical, drop generic words, join tokens with space
GEN = {'city', 'council', 'shire', 'regional', 'municipal', 'of', 'the', 'area'}
def key(s):
    s = re.sub(r'\(.*?\)', ' ', str(s).lower()).replace('-', ' ')
    return ' '.join(x for x in re.findall(r'[a-z]+', s) if x not in GEN)
k2id = {key(n): r for r, n in zip(cl.region_id, cl.region_name_x)}
w['region_id'] = w.council_name_norm.map(key).map(k2id)
# pre-2016 names that share a key with a post-2016 council but are a different (pre-amalgamation) entity
PRE_AMALG_SAME_NAME = {'dubbo', 'murrumbidgee', 'parramatta'}
w['pre_amalg_same_name'] = w.council_name_norm.isin(PRE_AMALG_SAME_NAME) & (w.fy_start <= 2015)
print('OLG names unmatched:', sorted(w[w.region_id.isna()].council_name_norm.unique()))
w = w.dropna(subset=['region_id'])
assert not w.duplicated(['region_id', 'fy_start']).any()

def c4_values(wv, k=1):
    L = np.log(wv[wv.gpc > 0].set_index(['region_id', 'fy_start']).gpc)
    def ch(cid, F):
        post = L.get((cid, F + k), np.nan)
        pre = [L.get((cid, y), np.nan) for y in (F - 2, F - 1)]; pre = [x for x in pre if pd.notna(x)]
        return post - np.mean(pre) if pd.notna(post) and pre else np.nan
    out = []
    for r in m.itertuples():
        own = ch(r.region_id, r.F)
        comp = [ch(c, r.F) for c in ALL - burned_in[r.F]]; comp = [x for x in comp if pd.notna(x)]
        out.append(own - np.median(comp) if pd.notna(own) and comp else np.nan)
    return pd.Series(out, index=m.index)

def sp(x, y, label):
    ok = x.notna() & y.notna()
    rho = spearmanr(x[ok], y[ok])[0]
    print(f'{label}: n={ok.sum()} rho={rho:+.3f}')
    return ok.sum(), rho

res = {}
m['C4_H1'] = c4_values(w); res['C4 as prespec'] = sp(D, m.C4_H1, 'C4 grants per resident FY F+1 (re-derived)')
m['C4_H1_noamalg'] = c4_values(w[~w.pre_amalg_same_name]); res['C4 drop pre-2016 Dubbo/Murrumbidgee/Parramatta'] = sp(D, m.C4_H1_noamalg, 'C4, pre-2016 same-name entities dropped')
for k, h in ((0, 'H0'), (2, 'H2'), (3, 'H3')):
    sp(D, c4_values(w, k), f'C4 {h}')
nb = m.F != 2019
sp(D[nb], m.C4_H1[nb], 'C4 H1 no Black Summer')

# ---------------- C5: fire-related grant share, audited statements
FIRE = re.compile(r'bush\s?fire|rural fire|fire protection|fire service|emergency service|disaster recover|natural disaster', re.I)
NOT = re.compile(r'storm|flood', re.I)
def shares(path, items):
    t = pd.read_csv(path, dtype={'region_id': str})
    t['Fy'] = t.fy.str.slice(0, 4).astype(int)
    lab = t.label.fillna('')
    fire = t[t['item'].isin(items) & lab.str.contains(FIRE) & ~lab.str.contains(NOT)].groupby(['region_id', 'Fy']).value_aud.sum()
    te = t[t['item'] == 'total_expenses'].groupby(['region_id', 'Fy']).value_aud.sum()
    s = pd.DataFrame({'te': te}).join(fire.rename('fire'))
    s = s[s.te > 0]
    s['share'] = s.fire.fillna(0) / s.te
    s['any_line_council'] = s.index.get_level_values(0).isin(set(fire.index.get_level_values(0)))
    return s
E10 = ROOT / 'Experiment 10'
fs = shares(E10 / 'A_fire_councils/statements_tidy.csv', ['disaster_grant_operating', 'disaster_grant_capital'])
cs = shares(E10 / 'A_comparison_councils/statements_tidy.csv', ['disaster_grant_operating', 'disaster_grant_capital', 'bushfire_emergency_services_grant'])
print('statement total_expenses median (AUD):', fs.te.median(), cs.te.median())

def c5_values(fs_, cs_, k=1, exclude_burned_comp=False):
    def ch(s, cid, F):
        def v(y):
            return s.share.get((cid, y), np.nan)
        post = v(F + k); pre = [x for x in (v(F - 2), v(F - 1)) if pd.notna(x)]
        return post - np.mean(pre) if pd.notna(post) and pre else np.nan
    comp_ids = sorted(set(cs_.index.get_level_values(0)))
    out = []
    for r in m.itertuples():
        own = ch(fs_, r.region_id, r.F)
        cids = [c for c in comp_ids if not (exclude_burned_comp and c in burned_in[r.F])]
        comp = [x for x in (ch(cs_, c, r.F) for c in cids) if pd.notna(x)]
        out.append(own - np.median(comp) if pd.notna(own) and comp else np.nan)
    return pd.Series(out, index=m.index)

fs_rule = fs.copy(); fs_rule.loc[~fs_rule.any_line_council, 'share'] = np.nan
m['C5_H1'] = c5_values(fs_rule, cs); res['C5 with has-lines rule'] = sp(D, m.C5_H1, 'C5 fire-grant share FY F+1 (with code has-lines rule)')
m['C5_H1_prespec'] = c5_values(fs, cs); res['C5 literal prespec (no has-lines rule)'] = sp(D, m.C5_H1_prespec, 'C5 literal prespec, councils with no fire line kept as share 0')
m['C5_H1_xb'] = c5_values(fs_rule, cs, exclude_burned_comp=True); res['C5 comparison excl. burned in F'] = sp(D, m.C5_H1_xb, 'C5, comparison councils with a master row in F removed')
sp(D[nb], m.C5_H1[nb], 'C5 H1 no Black Summer')
# raw own change (no comparison subtraction) to see whether the comparison matters
def own_only(fs_):
    out = []
    for r in m.itertuples():
        g = lambda y: fs_.share.get((r.region_id, y), np.nan)
        pre = [x for x in (g(r.F - 2), g(r.F - 1)) if pd.notna(x)]
        out.append(g(r.F + 1) - np.mean(pre) if pd.notna(g(r.F + 1)) and pre else np.nan)
    return pd.Series(out, index=m.index)
sp(D, own_only(fs_rule), 'C5 own change only (no comparison)')
# which fire councils were dropped by the has-lines rule
nol = sorted(set(fs.index.get_level_values(0)) - set(fs[fs.any_line_council].index.get_level_values(0)))
print('fire councils with statements but no fire-related line in any year (set missing by code):', nol)
print('rows affected by has-lines rule at H1:', int((m.C5_H1.isna() & m.C5_H1_prespec.notna()).sum()))
# comparison councils burned in some F
cids = set(cs.index.get_level_values(0))
print('comparison councils that have a master row:', sorted({(c, F) for F, s in burned_in.items() for c in s & cids}))
# Compare with Experiment 11 CLOCK_ROWS
R = pd.read_csv(ROOT / 'Experiment 11/results/CLOCK_ROWS.csv', dtype={'agrn': str, 'region_id': str})
R = m.merge(R[['agrn', 'region_id', 'C4_grants_pc_H1', 'C5_fire_grant_share_H1']], on=['agrn', 'region_id'])
for a, b in (('C4_H1', 'C4_grants_pc_H1'), ('C5_H1', 'C5_fire_grant_share_H1')):
    both = R[a].notna() & R[b].notna()
    print(f'{a} vs Exp11: rows present mine {R[a].notna().sum()} theirs {R[b].notna().sum()} both {both.sum()}, '
          f'max abs diff {np.abs(R[a] - R[b])[both].max():.2e}')
m.to_csv(OUT / 'rederived_c4_c5_rows.csv', index=False)
pd.DataFrame([(k, *v) for k, v in res.items()], columns=['variant', 'n', 'rho']).to_csv(OUT / 'rederived_c4_c5_summary.csv', index=False)
