"""Audit check (a)/(f) for C1 traffic: re-derive C1 H0 (months 0-3) with
 (1) the project's name rule (current council names only),
 (2) old (pre-2016) TfNSW lga names mapped to the council that absorbed them,
 (3) as (2) but dropping station-days where a two-direction station reported only one direction.
Own code; prints n, rho, within-season permutation p. Writes c1_variants.csv."""
import re
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path('/Users/ray/Research/AUSSEF - Local'); OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(1)
m = pd.read_csv(OUT / 'rederived_c4_c5_rows.csv', dtype={'agrn': str, 'region_id': str})
m['m0'] = pd.to_datetime(m.first_fire_start).dt.to_period('M')
cl = pd.read_csv(ROOT / 'Experiment 6/results/COUNCIL_ITEMS_v2.csv', dtype={'region_id': str})[['region_id', 'region_name_x']]
ALL = set(cl.region_id); burned_in = m.groupby('F').region_id.apply(set).to_dict()
def norm(s):  # project rule
    s = str(s).lower().replace('&', 'and'); s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'\b(city of|the|council|shire|regional|municipal|city|area)\b', ' ', s)
    return re.sub(r'[^a-z]', '', s)
k2id = dict(zip(cl.region_name_x.map(norm), cl.region_id)); n2id = dict(zip(cl.region_name_x, cl.region_id))
OLD = {'Armidale Dumaresq': 'Armidale Regional', 'Guyra': 'Armidale Regional', 'Ashfield': 'Inner West', 'Leichhardt': 'Inner West',
       'Marrickville': 'Inner West', 'Auburn': 'Cumberland', 'Holroyd': 'Cumberland', 'Bankstown': 'Canterbury-Bankstown',
       'Canterbury': 'Canterbury-Bankstown', 'Bombala': 'Snowy Monaro Regional', 'Cooma-Monaro': 'Snowy Monaro Regional',
       'Snowy River': 'Snowy Monaro Regional', 'Boorowa': 'Hilltops', 'Harden': 'Hilltops', 'Young': 'Hilltops',
       'Botany Bay': 'Bayside (NSW)', 'Rockdale': 'Bayside (NSW)', 'Conargo': 'Edward River', 'Deniliquin': 'Edward River',
       'Cootamundra': 'Cootamundra-Gundagai Regional', 'Gundagai': 'Cootamundra-Gundagai Regional', 'Corowa': 'Federation',
       'Urana': 'Federation', 'Gloucester': 'Mid-Coast', 'Great Lakes': 'Mid-Coast', 'Greater Taree': 'Mid-Coast',
       'Gosford': 'Central Coast (NSW)', 'Wyong': 'Central Coast (NSW)', 'Hurstville': 'Georges River', 'Kogarah': 'Georges River',
       'Jerilderie': 'Murrumbidgee', 'Manly': 'Northern Beaches', 'Pittwater': 'Northern Beaches', 'Warringah': 'Northern Beaches',
       'Murray': 'Murray River', 'Wakool': 'Murray River', 'Nambucca': 'Nambucca Valley', 'Palerang': 'Queanbeyan-Palerang Regional',
       'Queanbeyan': 'Queanbeyan-Palerang Regional', 'Tumbarumba': 'Snowy Valleys', 'Tumut': 'Snowy Valleys',
       'Wellington': 'Dubbo Regional', 'Unincorporated Far West': 'Unincorporated NSW'}

con = duckdb.connect(str(ROOT / 'data/aussef.duckdb'), read_only=True)
parts = ' union all '.join(f'select station_key, classification_seq, traffic_direction_seq, date, daily_total from raw.manual_traffic_hourly_permanent_{i}' for i in range(5))
d = con.execute(f"""with h as ({parts}), c as (select station_key, min(classification_seq) as cmin from h group by 1)
  select h.station_key, cast(h.date as date) as dd, sum(try_cast(h.daily_total as double)) as vol,
         count(distinct h.traffic_direction_seq) as ndir
  from h join c on h.station_key = c.station_key and h.classification_seq = c.cmin group by 1, 2""").df()
ref = con.execute('select distinct station_key, lga from raw.manual_traffic_station_reference').df()
d = d.merge(ref, on='station_key', how='left')
d['month'] = pd.to_datetime(d.dd).dt.to_period('M')
modal = d.groupby('station_key').ndir.agg(lambda s: s.mode()[0])
d['full'] = d.ndir >= d.station_key.map(modal)

def council_series(mapping, full_only, scale=False):
    x = d.copy(); x['rid'] = x.lga.map(mapping)
    if scale: x['vol'] = x.vol / x.ndir * x.station_key.map(modal)
    x = x.dropna(subset=['rid', 'vol'])
    if full_only: x = x[x.full]
    g = x.groupby(['station_key', 'month']).agg(v=('vol', 'mean'), n=('vol', 'size')).reset_index()
    g = g[g.n >= 0.5 * g.month.map(lambda p: p.days_in_month)]
    S = g.pivot(index='month', columns='station_key', values='v')
    st = x.drop_duplicates('station_key').set_index('station_key').rid
    return S, st.groupby(st).apply(lambda s: list(s.index)).to_dict()

def c1(S, stations, H=range(0, 4)):
    cache = {}
    def ch(cid, m0):
        if (cid, m0) in cache: return cache[(cid, m0)]
        W = [m0 + k for k in H]; B = [p - 12 for p in W] + [p - 24 for p in W]
        v = []
        for s in [s for s in stations.get(cid, []) if s in S]:
            w, b = S[s].reindex(W), S[s].reindex(B)
            if w.notna().sum() >= 0.5 * len(W) and b.notna().sum() >= 0.5 * len(B) and w.mean() > 0 and b.mean() > 0:
                v.append(np.log(w.mean() / b.mean()))
        cache[(cid, m0)] = np.median(v) if v else np.nan
        return cache[(cid, m0)]
    out = []
    for r in m.itertuples():
        own = ch(r.region_id, r.m0)
        comp = [x for x in (ch(c, r.m0) for c in ALL - burned_in[r.F]) if pd.notna(x)]
        out.append(own - np.median(comp) if pd.notna(own) and comp else np.nan)
    return pd.Series(out, index=m.index)

def test(y, label, nperm=5000):
    x = m.log_homes_in_fire_per_1000; ok = y.notna()
    xx, yy, ss = x[ok].to_numpy(), y[ok].to_numpy(), m.F[ok].to_numpy()
    rho = spearmanr(xx, yy)[0]; perm = []
    for _ in range(nperm):
        xp = xx.copy()
        for s in np.unique(ss):
            i = np.where(ss == s)[0]; xp[i] = rng.permutation(xx[i])
        perm.append(spearmanr(xp, yy)[0])
    p = (1 + (np.abs(perm) >= abs(rho)).sum()) / (1 + nperm)
    print(f'{label}: n={ok.sum()} rho={rho:+.3f} p_perm={p:.4f}')
    return dict(variant=label, n=int(ok.sum()), rho=rho, p_perm=p)

proj = lambda l: k2id.get(norm(l))
fixed = lambda l: n2id.get(OLD[l]) if l in OLD else k2id.get(norm(l))
res = []
for lab, mp, full, sc in (('1 project name rule', proj, False, False), ('2 old names mapped', fixed, False, False),
                      ('3 old names mapped + full-direction days only', fixed, True, False),
                      ('4 old names mapped + one-direction days scaled to all directions', fixed, False, True),
                      ('5 project name rule + full-direction days only', proj, True, False)):
    S, st = council_series(mp, full, sc)
    y = c1(S, st); m[f'C1_H0_v{lab[0]}'] = y
    res.append(test(y, 'C1 H0 ' + lab))
    nb = m.F != 2019
    print('   no Black Summer: n=%d rho=%+.3f' % (y[nb].notna().sum(), spearmanr(m.log_homes_in_fire_per_1000[nb][y[nb].notna()], y[nb].dropna())[0]))
R = pd.read_csv(ROOT / 'Experiment 11/results/CLOCK_ROWS.csv', dtype={'agrn': str, 'region_id': str})
both = m.C1_H0_v1.notna() & R.C1_traffic_H0.notna()
print('variant 1 vs Exp11 C1_traffic_H0: present', m.C1_H0_v1.notna().sum(), R.C1_traffic_H0.notna().sum(), 'max diff', np.abs(m.C1_H0_v1 - R.C1_traffic_H0)[both].max())
gained = m[m.C1_H0_v2.notna() & m.C1_H0_v1.isna()]
print('rows gained by old-name mapping:', len(gained), gained.groupby('region_name').size().to_dict())
pd.DataFrame(res).to_csv(OUT / 'c1_variants.csv', index=False)
m[['agrn', 'region_id', 'region_name', 'F'] + [f'C1_H0_v{i}' for i in range(1, 6)]].to_csv(OUT / 'c1_rows.csv', index=False)
