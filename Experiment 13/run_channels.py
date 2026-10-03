"""Experiment 13: build each channel's panel and run the locked models (PRESPEC.md sections 2 and 4).
Run (after LOCK.txt exists):
  uv run --no-project --with pyfixest --with pandas --with pyarrow --with openpyxl --with scipy python run_channels.py <channel>
channel in: income, pia, unemployment, businesses, dv, dv_postcode
Writes results/<channel>.json"""
import io
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

import e13lib as L

E13 = L.E13
RES = E13 / 'results'
RES.mkdir(exist_ok=True)
ROOT = E13.parent
PIA_OLD = Path('/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw/pia_2024.xlsx')

WINDOWS = {  # channel -> {sample: (first outcome year, last outcome year)}
    'income': {'P': (2010, 2018), 'B': (2014, 2022)},
    'pia': {'B': (2017, 2022)},
    'unemployment': {'P': (2010, 2018), 'B': (2014, None)},
    'businesses': {'P': (2014, 2018), 'B': (2015, 2024)},
    'dv': {'P': (2009, 2018), 'B': (2014, 2024)},
    'dv_postcode': {'P': (2009, 2018), 'B': (2014, 2024)},
}


def window(p, ch, s):
    a, b = WINDOWS[ch][s]
    b = int(p.year.max()) if b is None else b
    return p[(p.year >= a) & (p.year <= b)].copy()


def specs(sample, extra_s=False):
    """(label, kwargs) for the primary and the fixed secondary runs (PRESPEC 6)."""
    out = [('primary', {}), ('R_dose', dict(dose='R')), ('binary_H10', dict(binary=True))]
    if sample == 'B':
        out.append(('GCCSA_fe', dict(fe='GCCSA')))
        if extra_s:
            out.append(('S_dose', dict(dose='S')))
    return out


def run_outcomes(ch, panel, unit_kind, outcomes, model_of, scale_of, primary_outcomes, extra_s=False):
    res = []
    for s in WINDOWS[ch]:
        for yname in outcomes:
            p = window(panel, ch, s)[['unit', 'year', yname]].rename(columns={yname: 'y'}).dropna()
            if ch == 'income':           # balanced: keep postcodes present in every year of the window
                ny = p.year.nunique()
                p = p[p.groupby('unit').year.transform('nunique') == ny]
            labs = specs(s, extra_s and yname in primary_outcomes) if yname in primary_outcomes else [('primary', {})]
            for lab, kw in labs:
                r = L.run_channel(p, unit_kind, model_of(yname), scale_of(yname), s,
                                  extra=dict(channel=ch, outcome=yname, spec=lab,
                                             primary=(lab == 'primary' and yname in primary_outcomes)), **kw)
                print(ch, s, yname, lab, {k: round(v, 3) for k, v in r.items()
                                          if k in ('main_per10', 'main_lo', 'main_hi', 'placebo_per10',
                                                   'placebo_lo', 'placebo_hi')}, r['n_obs'], r['n_exposed_units'],
                      flush=True)
                res.append(r)
    L.save(res, RES / f'{ch}.json')


# ---------------------------------------------------------------- income (ATO postcode)
def income():
    d = pd.read_parquet(E13 / 'income_ato/panel_ato.parquet')
    d = d[(d.individuals >= 100)].copy()
    pos = lambda c: np.log(d[c].where(d[c] > 0))   # noqa: E731
    d['Y1_log_taxable_income'] = pos('taxinc')
    d['Y2_log_wage_earners'] = pos('sw_n')
    d['Y3_log_individuals'] = pos('individuals')
    d['Y4_log_wage_income'] = pos('sw_amt')
    d['Y5_log_income_per_person'] = np.log((d.taxinc / d.individuals).where(d.taxinc > 0))
    d['Y6_asinh_business_income'] = np.arcsinh(d.bus_total)
    d = d.rename(columns={'postcode': 'unit'})
    outs = ['Y1_log_taxable_income', 'Y2_log_wage_earners', 'Y3_log_individuals', 'Y4_log_wage_income',
            'Y5_log_income_per_person', 'Y6_asinh_business_income']
    run_outcomes('income', d, 'poa', outs, lambda y: 'ols', lambda y: 'log',
                 ['Y1_log_taxable_income', 'Y2_log_wage_earners'], extra_s=True)


# ---------------------------------------------------------------- PIA SA2 (B only, secondary)
def read_pia(path):
    d = pd.read_excel(path, 'Table 1.4', header=None)
    hdr_row = next(i for i in range(4, 12) if str(d.iloc[i, 2]).startswith('20'))
    years = [str(v) for v in d.iloc[hdr_row, 2:7]]
    body = d.iloc[hdr_row + 1:]
    body = body[body[0].astype(str).str.fullmatch(r'1\d{8}')]
    out = []
    for k, y in enumerate(years):
        rec = pd.DataFrame({'unit': body[0].astype(str).values, 'year': int(y[:4])})
        for name, c in {'earners': 2, 'sum': 12, 'median': 17}.items():
            rec[name] = pd.to_numeric(body[c + k].astype(str).str.replace(',', ''), errors='coerce').values
        out.append(rec)
    return pd.concat(out, ignore_index=True)


def pia():
    new = read_pia(E13 / 'income_ato/raw/pia2023_table1_total_income.xlsx')
    old = read_pia(PIA_OLD)
    d = pd.concat([old[old.year == 2017], new], ignore_index=True)
    for c in ('earners', 'sum', 'median'):
        d[f'log_{c}'] = np.log(d[c].where(d[c] > 0))
    run_outcomes('pia', d, 'sa2', ['log_sum', 'log_earners', 'log_median'], lambda y: 'ols', lambda y: 'log', [])


# ---------------------------------------------------------------- unemployment (SALM SA2)
def unemployment():
    u = pd.read_parquet(ROOT / 'Experiment 7/panels/sa2_unemployment.parquet')
    q = u.period.str.extract(r'(\d{4})Q(\d)').astype(int)
    u['year'] = np.where(q[1] >= 3, q[0], q[0] - 1)
    g = u.groupby(['SA2', 'year']).agg(un=('unemployed', 'sum'), lf=('labour_force', 'sum'),
                                       nq=('unemployed', 'count')).reset_index()
    g = g[(g.nq == 4) & (g.lf > 0)]
    g['rate'] = 100 * g.un / g.lf
    g = g.rename(columns={'SA2': 'unit'})
    g['unit'] = g.unit.astype(str)
    run_outcomes('unemployment', g, 'sa2', ['rate'], lambda y: 'ols', lambda y: 'level', ['rate'])


# ---------------------------------------------------------------- businesses (CABEE SA2 by industry)
CABEE = ROOT / 'fire_event_dataset/data/raw/sa2/businesses'
SOURCES = [
    ('jul2021-jun2025_8165DC08.xlsx', 'Table 1', 2025, 'Jul2021-Jun2025', 2021),
    ('jul2021-jun2025_8165DC08.xlsx', 'Table 2', 2024, 'Jul2021-Jun2025', 2021),
    ('jul2021-jun2025_8165DC08.xlsx', 'Table 3 ', 2023, 'Jul2021-Jun2025', 2021),
    ('jul2019-jun2023_8165DC08_revised.xlsx', 'Table 2', 2022, 'Jul2019-Jun2023', 2021),
    ('jul2019-jun2023_8165DC08_revised.xlsx', 'Table 3', 2021, 'Jul2019-Jun2023', 2021),
    ('jul2017-jun2021_816508.xlsx', '2020 a', 2020, 'Jul2017-Jun2021', 2021),
    ('jul2017-jun2021_816508.xlsx', '2019', 2019, 'Jul2017-Jun2021', 2021),
    ('jul2015-jun2019_816508.xls', 'June 2019', 2019, 'Jul2015-Jun2019', 2016),
    ('jul2015-jun2019_816508.xls', 'June 2018', 2018, 'Jul2015-Jun2019', 2016),
    ('jul2015-jun2019_816508.xls', 'June 2017', 2017, 'Jul2015-Jun2019', 2016),
    ('jun2013-jun2017_816508.xls', 'June 2017', 2017, 'Jun2013-Jun2017', 2016),
    ('jun2013-jun2017_816508.xls', 'June 2016', 2016, 'Jun2013-Jun2017', 2016),
    ('jun2013-jun2017_816508.xls', 'June 2015', 2015, 'Jun2013-Jun2017', 2016),
]
USE = {2025: 'Jul2021-Jun2025', 2024: 'Jul2021-Jun2025', 2023: 'Jul2021-Jun2025', 2022: 'Jul2019-Jun2023',
       2021: 'Jul2019-Jun2023', 2020: 'Jul2017-Jun2021', 2019: 'Jul2017-Jun2021', 2018: 'Jul2015-Jun2019',
       2017: 'Jul2015-Jun2019', 2016: 'Jun2013-Jun2017', 2015: 'Jun2013-Jun2017'}


def read_cabee(fname, sheet):
    sys.path.insert(0, str(ROOT / 'Experiment 7'))
    from xls_reader import read_xls, to_rows
    import openpyxl
    path = CABEE / fname
    if fname.endswith('.xlsx'):
        rows = list(openpyxl.load_workbook(path, read_only=True)[sheet].iter_rows(values_only=True))
    else:
        rows = to_rows(read_xls(path, sheets={sheet})[sheet])
    hdr = next(i for i, r in enumerate(rows) if r and r[0] == 'Industry' and r[2] == 'SA2')
    assert rows[hdr][9] == 'Total', rows[hdr]
    title = next(str(r[0]) for r in rows[:hdr] if r and r[0] and 'Statistical Area Level 2' in str(r[0]))
    d = pd.DataFrame([r[:10] for r in rows[hdr + 2:] if r and r[0] is not None and r[2] is not None],
                     columns=['ind', 'ind_label', 'SA2', 'name', 'ne', 'e1', 'e5', 'e20', 'e200', 'total'])
    d['SA2'] = pd.to_numeric(d.SA2, errors='coerce')
    d = d[d.SA2.notna()].copy()
    d['SA2'] = d.SA2.astype('int64').astype(str)
    for c in ('ne', 'total'):
        d[c] = pd.to_numeric(d[c], errors='coerce')
    return d[['ind', 'SA2', 'name', 'ne', 'total']], title


def business_panel():
    cache = E13 / 'businesses/panel_cabee_industry.parquet'
    if cache.exists():
        return pd.read_parquet(cache)
    tabs = []
    for fname, sheet, june, rel, asgs in SOURCES:
        d, title = read_cabee(fname, sheet)
        assert f'June {june}' in title, (fname, sheet, title)
        d['june'], d['release'], d['asgs'] = june, rel, asgs
        tabs.append(d)
    t = pd.concat(tabs, ignore_index=True)
    t['ind'] = t.ind.astype(str).str.strip().str[:1]
    tot = t.groupby(['SA2', 'name', 'june', 'release', 'asgs'], as_index=False)[['ne', 'total']].sum(min_count=1)
    tot['ind'] = 'ALL'
    t = pd.concat([t[t.ind.isin(['A', 'E', 'G', 'H'])], tot], ignore_index=True)
    same = (t[t.asgs == 2021][['SA2', 'name']].drop_duplicates()
            .merge(t[t.asgs == 2016][['SA2', 'name']].drop_duplicates(), on=['SA2', 'name']))
    keep16 = set(same.SA2)
    key = t.set_index(['SA2', 'ind', 'release', 'june']).total
    f19 = key.xs(('Jul2017-Jun2021', 2019), level=['release', 'june']) / key.xs(('Jul2015-Jun2019', 2019),
                                                                               level=['release', 'june'])
    f17 = key.xs(('Jul2015-Jun2019', 2017), level=['release', 'june']) / key.xs(('Jun2013-Jun2017', 2017),
                                                                               level=['release', 'june'])
    p = t[[USE[j] == r for j, r in zip(t.june, t.release)]].copy()
    p = p[(p.asgs == 2021) | p.SA2.isin(keep16)].copy()
    idx = list(zip(p.SA2, p.ind))
    p['link'] = 1.0
    o = (p.asgs == 2016).values
    p.loc[o, 'link'] = [f19.get(k, np.nan) for k, oo in zip(idx, o) if oo]
    o15 = p.june.isin([2015, 2016]).values
    p.loc[o15, 'link'] = p.loc[o15, 'link'].values * np.array([f17.get(k, np.nan) for k, oo in zip(idx, o15) if oo])
    p['link'] = p.link.where(np.isfinite(p.link))
    p['count'] = p.total * p.link
    p['ne_share'] = p['ne'] / p['total'].where(p['total'] > 0)
    p['year'] = p.june - 1                       # June y = end of financial year y-1
    p = p.rename(columns={'SA2': 'unit'})
    p.to_parquet(cache, index=False)
    return p


def businesses():
    p = business_panel()
    w = p.pivot_table(index=['unit', 'year'], columns='ind', values='count').reset_index()
    w.columns = ['unit', 'year'] + [f'n_{c}' for c in w.columns[2:]]
    ne = p[p.ind == 'ALL'][['unit', 'year', 'ne_share']]
    w = w.merge(ne, on=['unit', 'year'], how='left')
    outs = ['n_H', 'n_E', 'n_A', 'n_G', 'n_ALL', 'ne_share']
    run_outcomes('businesses', w, 'sa2', outs, lambda y: 'ols' if y == 'ne_share' else 'pois',
                 lambda y: 'level' if y == 'ne_share' else 'pois', ['n_H'])


# ---------------------------------------------------------------- domestic violence (BOCSAR)
SUBCATS = {'Domestic violence related assault': 'dv_assault', 'Breach Apprehended Violence Order': 'avo_breach',
           'Non-domestic violence related assault': 'nondv_assault',
           'Malicious damage to property': 'malicious_damage'}


def read_bocsar(zname, key):
    with zipfile.ZipFile(E13 / f'dv/raw/{zname}') as z:
        name = z.namelist()[0]
        chunks = []
        for c in pd.read_csv(z.open(name), chunksize=50000, dtype={key: str}):
            chunks.append(c[c.Subcategory.isin(SUBCATS)])
    d = pd.concat(chunks, ignore_index=True)
    months = [c for c in d.columns if re.fullmatch(r'[A-Z][a-z]{2} \d{4}', c)]
    long = d.melt(id_vars=[key, 'Subcategory'], value_vars=months, var_name='m', value_name='n')
    dt = pd.to_datetime(long.m, format='%b %Y')
    long['year'] = np.where(dt.dt.month >= 7, dt.dt.year, dt.dt.year - 1)
    long['n'] = pd.to_numeric(long.n, errors='coerce')
    last = dt.max()
    full_last = last.year - 1 if last.month < 6 else (last.year - 1 if last.month == 6 else last.year - 1)
    g = long.groupby([key, 'Subcategory', 'year']).n.sum(min_count=1).reset_index()
    g = g[g.year <= (last.year - 1 if last.month >= 6 else last.year - 2)]   # complete financial years only
    g['out'] = g.Subcategory.map(SUBCATS)
    w = g.pivot_table(index=[key, 'year'], columns='out', values='n').reset_index()
    return w, str(last.date())


def norm_name(s):
    s = re.sub(r'\s*\(.*?\)\s*$', '', str(s)).upper()
    return re.sub(r'[^A-Z ]', '', s).strip()


def dv():
    w, last = read_bocsar('SuburbData.zip', 'Suburb')
    sal = pd.read_parquet(E13 / 'exposure/out/sal_names.parquet')
    sal['nm'] = sal.SAL_NAME_2021.map(norm_name)
    uniq = sal.groupby('nm').SAL_CODE_2021.nunique()
    sal = sal[sal.nm.map(uniq) == 1].drop_duplicates('nm')
    w['nm'] = w.Suburb.map(norm_name)
    n_sub = w.Suburb.nunique()
    w = w.merge(sal[['nm', 'SAL_CODE_2021']], on='nm', how='inner').rename(columns={'SAL_CODE_2021': 'unit'})
    match = dict(bocsar_suburbs=int(n_sub), matched=int(w.Suburb.nunique()), last_month=last)
    print('suburb match', match, flush=True)
    units = L.load_units('sal')
    w = w[w.unit.isin(set(units[units.dwellings >= 50].unit))]
    w = w[w.groupby('unit').dv_assault.transform('sum') > 0]
    (RES / 'dv_match.json').write_text(pd.Series(match).to_json())
    run_outcomes('dv', w, 'sal', ['dv_assault', 'avo_breach', 'nondv_assault', 'malicious_damage'],
                 lambda y: 'pois', lambda y: 'pois', ['dv_assault'])


def dv_postcode():
    w, last = read_bocsar('PostcodeData.zip', 'Postcode')
    w = w.rename(columns={'Postcode': 'unit'})
    w['unit'] = w.unit.astype(str).str.zfill(4)
    units = L.load_units('poa')
    w = w[w.unit.isin(set(units[units.dwellings >= 50].unit))]
    w = w[w.groupby('unit').dv_assault.transform('sum') > 0]
    run_outcomes('dv_postcode', w, 'poa', ['dv_assault', 'avo_breach'], lambda y: 'pois', lambda y: 'pois', [])


if __name__ == '__main__':
    L.check_lock()
    {'income': income, 'pia': pia, 'unemployment': unemployment, 'businesses': businesses, 'dv': dv,
     'dv_postcode': dv_postcode}[sys.argv[1]]()
