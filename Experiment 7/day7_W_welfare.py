"""Experiment 7, Day 7, dataset W: DSS working-age income-support recipients per 1,000 residents, by SA2, quarterly,
vs share of residents within 1 km of fires (PRESPEC_DAY7.md, LOCK_DAY7.txt).

Source: data.gov.au "DSS Benefit and Payment Recipient Demographics - quarterly data" (dss-payment-demographic-data),
one xlsx per quarter (Mar 2016 .. Jun 2025), sheet "SA2" ("SA 2" in Sep 2021). Downloaded by day7_W_download.py into
fire_event_dataset/data/raw/sa2/W/ and logged in results/DAY7_DOWNLOADS.csv.

Outcome (same payment list as fire_event_dataset/src/dss.py income_support_total):
  Newstart / JobSeeker + Youth Allowance (other) + Parenting Payment Single + Parenting Payment Partnered
  + Disability Support Pension + Carer Payment + Special Benefit + legacy allowances while published
  (Sickness Allowance, Partner Allowance, Widow Allowance, Widow B Pension, Wife Pension (both types)),
  divided by Census 2021 SA2 persons (panels/sa2_info.parquet) x 1,000.

SA2 vintages in the files (detected from the NSW row count):
  Mar 2016 - Dec 2018: ASGS 2011, 5-digit codes (540 NSW rows)
  Mar 2019 - Mar 2023: ASGS 2016, 5-digit codes (576 NSW rows)
  Jun 2023          : ASGS 2021, 5-digit codes (642 NSW rows)
  Sep 2023 - Jun 2025: ASGS 2021, 9-digit codes (642 NSW rows)
  The 5-digit code is the state digit + the last 4 digits of the 9-digit code. A pre-2021 row is kept only where the
  code is unchanged: its 5-digit code equals the 5-digit form of an ASGS 2021 SA2 (PRESPEC: other vintages only
  where the code is unchanged; ABS gives a changed SA2 a new code). Rows whose code is unchanged but whose name
  differs are flagged (name_identical = False); checked by hand on 2026-10-01: all are renames
  ("X Region" -> "X Surrounds", "Blacktown (South)" -> "Blacktown - South", spelling fixes,
  "Badgerys Creek - Greendale" (2011) -> "Austral - Greendale").

Model (fixed by PRESPEC_DAY7, quarterly; identical implementation to day7_U_unemployment.py):
  y[s,q] = a[s,season] + b[GCCSA,q] + sum_{k=0..4} beta_k D[s,q-k] + sum_{k=1..4} lambda_k D[s,q+k]
  SEs clustered by SA3; sample 2016Q1..2025Q2. Primary = mean(beta_0..beta_4) per 10 pp of residents affected;
  placebo = mean(lambda_1..lambda_4). Worse direction for W: up.
Run: python3 day7_W_welfare.py   (rebuilds panels/sa2_welfare.parquet if missing; --rebuild forces it)"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
RAW = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/raw/sa2/W')
PANEL = HERE / 'panels/sa2_welfare.parquet'
START, END = pd.Period('2016Q1', 'Q'), pd.Period('2025Q2', 'Q')
LAGS, LEADS = range(0, 5), range(1, 5)
SCALE = 0.1   # per 10 percentage points of residents affected (dose is a 0-1 share)
MIN_POP = 100
MON = {'March': 1, 'June': 2, 'September': 3, 'December': 4}
VINTAGE = {540: 2011, 576: 2016, 642: 2021}

# Dec 2022 and Mar 2023 have two versions on data.gov.au ("historic" and "expanded"/"aligned"). Every file from
# Jun 2023 on is the expanded series, so the expanded/aligned versions are used to keep the series consistent from
# 2022Q4 onward (the method break then sits between 2022Q3 and 2022Q4).
SKIP = {'dss-demographics-december-2022.xlsx', 'dss-demographics-march-2023-historic.xlsx'}

INCOME_SUPPORT = {   # identical to fire_event_dataset/src/dss.py INCOME_SUPPORT
    'Newstart Allowance', 'Newstart Allowance / Jobseeker Payment', 'JobSeeker Payment',
    'Youth Allowance (other)', 'Parenting Payment Single', 'Parenting Payment Partnered',
    'Disability Support Pension', 'Carer Payment', 'Special Benefit',
    'Sickness Allowance', 'Partner Allowance', 'Widow Allowance', 'Widow B Pension',
    'Wife Pension (Partner on Age Pension)', 'Wife Pension (Partner on Disability Support Pension)',
}
MAIN = {'jobseeker_newstart': ('Newstart Allowance', 'JobSeeker Payment', 'Newstart Allowance / Jobseeker Payment'),
        'disability_support_pension': ('Disability Support Pension',),
        'parenting_payment_single': ('Parenting Payment Single',),
        'youth_allowance_other': ('Youth Allowance (other)',),
        'carer_payment': ('Carer Payment',)}


def norm(s):
    return re.sub(r'\s+', ' ', str(s)).strip().lower()


def read_file(path):
    x = pd.ExcelFile(path)
    sheet = [s for s in x.sheet_names if s.replace(' ', '').upper() == 'SA2'][0]
    title = str(pd.read_excel(x, sheet, header=None, nrows=1).iloc[0, 0])
    m = re.search(r'(March|June|September|December)\s+(\d{4})', title)
    period = pd.Period(year=int(m.group(2)), quarter=MON[m.group(1)], freq='Q')
    d = pd.read_excel(x, sheet, header=2, dtype=str)
    d.columns = [str(c).strip() for c in d.columns]
    d['SA2'] = d.SA2.astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    d = d[d.SA2.str.fullmatch(r'1\d{4}|1\d{8}')].copy()     # NSW SA2 rows (codes start with state digit 1)
    vint = VINTAGE[len(d)]
    comps = [c for c in d.columns if c in INCOME_SUPPORT]
    raw = d[comps].apply(lambda s: s.str.strip().str.replace(',', '', regex=False))
    num = raw.apply(lambda s: pd.to_numeric(s.where(s.str.fullmatch(r'\d+(\.\d+)?', na=False)), errors='coerce'))
    supp = raw.isin(['<5']).sum(axis=1)
    other_nonnum = (num.isna() & ~raw.isin(['<5'])).sum(axis=1)
    out = pd.DataFrame({'code_pub': d.SA2.values, 'name_pub': d['SA2 Name'].astype(str).str.strip().values,
                        'period': str(period), 'asgs_vintage': vint, 'source_file': path.name,
                        'recipients': num.sum(axis=1, min_count=1).values,
                        'recipients_lt5_as_2p5': (num.sum(axis=1, min_count=1) + 2.5 * supp).values,
                        'n_components_published': len(comps), 'n_lt5_cells': supp.values,
                        'n_other_nonnumeric_cells': other_nonnum.values})
    for k, names in MAIN.items():
        c = [n for n in names if n in num.columns]
        out[k] = num[c[0]].values if c else np.nan
    return out


def build_panel():
    files = sorted(p for p in RAW.glob('*.xlsx') if p.name not in SKIP)
    raw = pd.concat([read_file(p) for p in files], ignore_index=True)
    assert not raw.duplicated(['code_pub', 'period']).any(), 'two files for one quarter'
    # ASGS 2021 names keyed by 9-digit code (from the 9-digit files), and its 5-digit form
    r21 = raw[raw.code_pub.str.len() == 9][['code_pub', 'name_pub']].drop_duplicates('code_pub')
    r21 = r21.rename(columns={'code_pub': 'SA2', 'name_pub': 'name21'})
    r21['code5'] = r21.SA2.str[0] + r21.SA2.str[-4:]
    assert not r21.code5.duplicated().any()
    to9 = r21.set_index('code5')
    raw['SA2'] = np.where(raw.code_pub.str.len() == 9, raw.code_pub, raw.code_pub.map(to9.SA2))
    raw['name21'] = raw.SA2.map(r21.set_index('SA2').name21)
    raw['code_unchanged'] = raw.SA2.notna()      # ABS never reuses an SA2 code for a changed area
    raw['name_identical'] = raw.code_unchanged & (raw.name_pub.map(norm) == raw.name21.map(norm))
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    p = raw.merge(info[['SA2', 'pop']], on='SA2', how='left')
    p['in_sa2_info'] = p['pop'].notna()
    p['value'] = p.recipients / p['pop'] * 1000
    p['value_lt5_as_2p5'] = p.recipients_lt5_as_2p5 / p['pop'] * 1000
    p['measure'] = 'working-age income-support recipients per 1,000 residents (Census 2021 persons)'
    p['SA2'] = p.SA2.astype('string')
    cols = ['SA2', 'period', 'value', 'recipients', 'pop', 'code_unchanged', 'name_identical', 'in_sa2_info', 'asgs_vintage',
            'code_pub', 'name_pub', 'name21', 'source_file', 'n_components_published', 'n_lt5_cells',
            'n_other_nonnumeric_cells', 'recipients_lt5_as_2p5', 'value_lt5_as_2p5', *MAIN, 'measure']
    p = p[cols].sort_values(['period', 'code_pub'], ignore_index=True)
    p.to_parquet(PANEL, index=False)
    return p


def absorb(M, groups, tol=1e-10, maxit=2000):
    """Residualise columns of M on several sets of categorical fixed effects (alternating projections)."""
    M = M.copy()
    codes = [pd.factorize(g)[0] for g in groups]
    for _ in range(maxit):
        old = M.copy()
        for c in codes:
            n = np.bincount(c)
            for j in range(M.shape[1]):
                M[:, j] -= (np.bincount(c, weights=M[:, j]) / n)[c]
        if np.max(np.abs(M - old)) < tol:
            break
    return M


def fit(p, D):
    """p: panel rows (SA2, period Period, y, season, GCCSA, SA3); D: dict (SA2, Period) -> dose."""
    p = p.copy()
    names = [f'b{k}' for k in LAGS] + [f'l{k}' for k in LEADS]
    for k in LAGS:
        p[f'b{k}'] = [D.get((s, q - k), 0.0) for s, q in zip(p.SA2, p.period)]
    for k in LEADS:
        p[f'l{k}'] = [D.get((s, q + k), 0.0) for s, q in zip(p.SA2, p.period)]
    g1 = p.SA2 + '_' + p.season.astype(str)
    g2 = p.GCCSA + '_' + p.period.astype(str)
    M = absorb(p[['y'] + names].to_numpy(float), [g1.to_numpy(), g2.to_numpy()])
    y, X = M[:, 0], M[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    cl = pd.factorize(p.SA3)[0]
    G = cl.max() + 1
    S = np.zeros((G, X.shape[1]))
    np.add.at(S, cl, X * e[:, None])
    N = len(y)
    K = X.shape[1] + g2.nunique()     # SA2 x season FE are nested in SA3 clusters (not counted, as fixest)
    V = XtX_inv @ (S.T @ S) @ XtX_inv * G / (G - 1) * (N - 1) / (N - K)

    def comb(cols):
        w = np.zeros(len(names))
        for c in cols:
            w[names.index(c)] = SCALE / len(cols)
        est, se = float(w @ b), float(np.sqrt(w @ V @ w))
        return dict(est=est, se=se, ci_low=est - 1.96 * se, ci_high=est + 1.96 * se)
    return dict(n_obs=int(N), n_sa2=int(p.SA2.nunique()), n_clusters=int(G),
                n_treated_sa2=int(p.loc[p[names].abs().sum(axis=1) > 0, 'SA2'].nunique()),
                mean_y=float(p.y.mean()),
                primary=comb([f'b{k}' for k in LAGS]), placebo=comb([f'l{k}' for k in LEADS]),
                coefs_per10pp={n: float(b[i] * SCALE) for i, n in enumerate(names)},
                ses_per10pp={n: float(np.sqrt(V[i, i]) * SCALE) for i, n in enumerate(names)})


def verdict(r):   # worse = up
    pr, pl = r['primary'], r['placebo']
    placebo_ok = pl['ci_low'] <= 0 <= pl['ci_high']
    if pr['ci_low'] > 0 and placebo_ok:
        return 'Detected'
    if pr['ci_low'] > 0:
        return 'Not claimed: placebo fails'
    return 'Not detected'


def main():
    w = build_panel() if ('--rebuild' in sys.argv or not PANEL.exists()) else pd.read_parquet(PANEL)
    w['SA2'] = w.SA2.astype(object)
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    dq = pd.read_parquet(HERE / 'panels/sa2_quarter_dose.parquet')
    dq['q'] = dq.quarter.map(lambda s: pd.Period(s, 'Q'))
    D = {(s, q): v for s, q, v in zip(dq.SA2, dq.q, dq.dose)}

    ok = w[w.code_unchanged & w.in_sa2_info & w.value.notna()]
    by_v = w.groupby('asgs_vintage').agg(rows=('code_pub', 'size'), unchanged=('code_unchanged', 'sum'),
                                         name_identical=('name_identical', 'sum'),
                                         in_sa2_info=('in_sa2_info', 'sum'), quarters=('period', 'nunique'))
    match = dict(sa2_info_n=int(len(info)),
                 sa2_info_codes_in_2021_files=int(info.SA2.isin(set(w.loc[w.asgs_vintage == 2021, 'SA2'])).sum()),
                 sa2_info_codes_with_any_value=int(info.SA2.isin(set(ok.SA2)).sum()),
                 by_vintage={int(k): {c: int(v) for c, v in r.items()} for k, r in by_v.iterrows()},
                 per_quarter_sa2_info_matched=ok.groupby('period').SA2.nunique().astype(int).to_dict())
    match['match_rate_any_value'] = match['sa2_info_codes_with_any_value'] / match['sa2_info_n']
    match['match_rate_2021_files'] = match['sa2_info_codes_in_2021_files'] / match['sa2_info_n']
    for v in (2011, 2016):
        codes = set(w.loc[(w.asgs_vintage == v) & w.code_unchanged, 'SA2'])
        match[f'sa2_info_codes_unchanged_in_asgs{v}'] = int(info.SA2.isin(codes).sum())
    match['dose_sa2s_total'] = int(dq.SA2.nunique())
    match['dose_sa2s_with_value'] = int(dq.SA2.drop_duplicates().isin(set(ok.SA2)).sum())

    base = ok.merge(info[['SA2', 'SA3', 'GCCSA']], on='SA2', how='inner')
    base['period'] = base.period.map(lambda s: pd.Period(s, 'Q'))
    base = base[(base.period >= START) & (base.period <= END)].copy()
    base['season'] = base.period.map(lambda q: q.quarter)
    base['SA3'], base['GCCSA'] = base.SA3.astype(str), base.GCCSA.astype(str)
    p = base[base['pop'] >= MIN_POP].copy()
    p['y'] = p.value.astype(float)
    p = p.reset_index(drop=True)

    res = dict(dataset='W: DSS Benefit and Payment Recipient Demographics (data.gov.au dss-payment-demographic-data), '
                       'SA2 sheet, quarterly; working-age income-support recipients per 1,000 residents',
               source_dir=str(RAW),
               units='income-support recipients per 1,000 residents per 10 pp of residents within 1 km',
               worse_direction='up', period_range=f'{p.period.min()}..{p.period.max()}',
               panel_rows=int(len(p)), sa2s=int(p.SA2.nunique()), code_match=match)
    main_r = fit(p, D)
    res['main'] = main_r
    res['verdict'] = verdict(main_r)
    res['bound_in_worse_direction'] = main_r['primary']['ci_high']   # largest increase consistent with data

    # Also reported (PRESPEC): heavily affected SA2s (dose >= 25%) and Black Summer only (fire quarters 2019Q3-2020Q1)
    # (same definitions as day7_U_unemployment.py)
    mx = dq.groupby('SA2').dose.max()
    heavy = set(mx[mx >= 0.25].index)
    zero = set(p.SA2) - set(mx[mx > 0].index)
    ph = p[p.SA2.isin(heavy | zero)].reset_index(drop=True)
    res['heavy'] = dict(definition='sample = SA2s with any fire-quarter dose >= 25% plus SA2s with zero dose in '
                                   'every quarter; same model', **fit(ph, D))
    bs = {k: v for k, v in D.items() if pd.Period('2019Q3', 'Q') <= k[1] <= pd.Period('2020Q1', 'Q')}
    res['black_summer'] = dict(definition='dose kept only for fire quarters 2019Q3-2020Q1 (other quarters set to 0); '
                                          'full sample; same model', **fit(p, bs))
    for k in ('heavy', 'black_summer'):
        res[k]['verdict'] = verdict(res[k])

    # Data-handling sensitivities (not pre-specified; same model, only the outcome construction / sample changes)
    sens = {}
    q = base.copy()
    q['y'] = q.value.astype(float)
    r = fit(q.reset_index(drop=True), D)
    sens['no_min_pop_filter'] = dict(primary=r['primary'], placebo=r['placebo'], n_obs=r['n_obs'], verdict=verdict(r))
    q = p.copy()
    q['y'] = q.value_lt5_as_2p5.astype(float)
    r = fit(q, D)
    sens['lt5_cells_as_2p5'] = dict(primary=r['primary'], placebo=r['placebo'], n_obs=r['n_obs'], verdict=verdict(r))
    q = p[p.period <= pd.Period('2022Q3', 'Q')].copy()
    q['y'] = q.value.astype(float)
    r = fit(q.reset_index(drop=True), D)
    sens['before_expanded_series_2016Q1_2022Q3'] = dict(primary=r['primary'], placebo=r['placebo'],
                                                         n_obs=r['n_obs'], verdict=verdict(r))
    res['sensitivities_not_prespecified'] = sens

    res['deviations'] = [
        f'SA2s with Census 2021 population < {MIN_POP} excluded (per-1,000 rate explodes for near-empty SA2s; '
        'same rule as Day 5). Unfiltered result in sensitivities.',
        "Suppressed cells ('<5', i.e. 1-4 recipients) are excluded from the sum ('summed where available'), not "
        'turned into NaN totals as in dss.py (at SA2 level that rule would blank most SA2s because small legacy '
        "payments are '<5'). Sensitivity with '<5' = 2.5 reported.",
        'Dec 2022 and Mar 2023 use the expanded/aligned DSS versions (all later files are expanded only).',
    ]
    res['notes'] = [
        'DSS changed its method from Dec 2022 ("expanded" data): NSW JobSeeker count is +6.7% in the expanded '
        'Dec 2022 file vs the historic one (+14% Mar 2023). A common shift is absorbed by GCCSA x quarter effects; '
        'an SA2-proportional shift is not. Sensitivity truncated at 2022Q3 reported.',
        'Before Dec 2022 values 1-4 were published as <5; from Dec 2022 all cells are rounded to the nearest 5.',
        'Denominator is fixed Census 2021 population, so with SA2 x season effects the outcome moves only with '
        'recipient counts.',
        'JobSeeker replaced Newstart on 20 Mar 2020 (treated as one series, as in dss.py); COVID-19 surge in '
        '2020Q2-2021 is common to GCCSA x quarter effects only to the extent it is uniform.',
        'Leads for 2024Q3..2025Q2 reach beyond the dose panel end (2025Q2); later fires counted as 0.',
        'Primary and placebo are averages of the 5 lag / 4 lead coefficients, scaled to 10 pp of residents; CIs are '
        'normal (1.96) with CR1 small-sample correction (same code as day7_U_unemployment.py).']
    OUT.mkdir(exist_ok=True)
    json.dump(res, open(OUT / 'DAY7_W.json', 'w'), indent=2, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == '__main__':
    main()
