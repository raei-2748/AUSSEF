"""Experiment 7, Day 5: SA2 income vs resident fire exposure (PRESPEC_DAY5.md, LOCK_DAY5.txt).
Run: python3 day5_sa2_income.py   (after prep_sa2_dose.py)"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
PIA = Path('/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw')
BLOCKS = {'earners': 2, 'median_age': 7, 'sum': 12, 'median': 17, 'mean': 22}


def read_pia(path):
    d = pd.read_excel(path, 'Table 1.4', header=None)
    years = [str(v) for v in d.iloc[6, 2:7]]
    body = d.iloc[7:]
    body = body[body[0].astype(str).str.fullmatch(r'1\d{8}')]
    out = []
    for k, y in enumerate(years):
        rec = pd.DataFrame({'SA2': body[0].astype(str).values, 'name': body[1].astype(str).values,
                            'fy': int(y[:4])})
        for name, c in BLOCKS.items():
            rec[name] = pd.to_numeric(body[c + k].astype(str).str.replace(',', ''), errors='coerce').values
        out.append(rec)
    return pd.concat(out, ignore_index=True)


def panel():
    new = read_pia(PIA / 'pia_2024.xlsx')                       # 2017-18..2021-22, ASGS 2021
    old = read_pia(PIA / 'project_inputs/pia_old_total.xlsx')   # 2015-16..2019-20, ASGS 2016
    same = set(new[['SA2', 'name']].drop_duplicates().itertuples(index=False, name=None)) & \
        set(old[['SA2', 'name']].drop_duplicates().itertuples(index=False, name=None))
    keep = {s for s, _ in same}
    link = new[new.fy == 2017].set_index('SA2')[['earners', 'sum']].div(
        old[old.fy == 2017].set_index('SA2')[['earners', 'sum']])
    early = old[old.fy.isin([2015, 2016]) & old.SA2.isin(keep)].copy()
    for c in ('earners', 'sum'):
        early[c] = early[c] * early.SA2.map(link[c])
    early['mean'] = early['sum'] / early['earners']
    early['median'] = early['median'] * early.SA2.map(new[new.fy == 2017].set_index('SA2')['median'] /
                                                      old[old.fy == 2017].set_index('SA2')['median'])
    p = pd.concat([early, new], ignore_index=True)
    p['mean'] = p['sum'] / p['earners']
    return p, len(keep)


def main():
    p, n_linked = panel()
    dose = pd.read_parquet(HERE / 'panels/sa2_fy_dose.parquet')
    info = pd.read_parquet(HERE / 'panels/sa2_info.parquet')
    D = dose.set_index(['SA2', 'fy']).dose
    p = p.merge(info[['SA2', 'SA3', 'GCCSA', 'pop']], on='SA2', how='inner')
    p = p[(p['pop'] >= 100) & (p.earners > 0) & (p['sum'] > 0)].copy()
    for k, lab in ((0, 'D0'), (1, 'L1'), (2, 'L2'), (-1, 'F1'), (-2, 'F2')):
        p[lab] = [D.get((s, t - k), 0.0) for s, t in zip(p.SA2, p.fy)]
    for c in ('sum', 'earners', 'mean', 'median'):
        p[f'log_{c}'] = np.log(p[c])
    p['gt'] = p.GCCSA.astype(str) + '_' + p.fy.astype(str)
    res = {'panel_rows': int(len(p)), 'sa2s': int(p.SA2.nunique()), 'sa2s_linked_back_to_2015': n_linked,
           'years': sorted(map(int, p.fy.unique()))}
    tab = []
    for y in ('log_sum', 'log_earners', 'log_mean', 'log_median'):
        m = smf.ols(f'{y} ~ D0 + L1 + L2 + F1 + F2 + C(SA2) + C(gt)', data=p).fit(
            cov_type='cluster', cov_kwds={'groups': p.SA3.astype(str)})
        def comb(names):
            w = pd.Series(0.0, index=m.params.index)
            w[names] = 0.1          # per 10 percentage points of residents affected
            est = float(w @ m.params)
            se = float(np.sqrt(w @ m.cov_params() @ w))
            return est * 100, (est - 1.96 * se) * 100, (est + 1.96 * se) * 100   # in % (log points × 100)
        rec = dict(outcome=y)
        for lab, names in (('cumulative_t_t1', ['D0', 'L1']), ('fire_year', ['D0']), ('year_after', ['L1']),
                           ('two_years_after', ['L2']), ('placebo_leads', ['F1', 'F2'])):
            e, lo, hi = comb(names)
            rec.update({f'{lab}_pct': e, f'{lab}_lo': lo, f'{lab}_hi': hi})
        tab.append(rec)
    tab = pd.DataFrame(tab)
    tab.to_csv(OUT / 'DAY5_SA2_INCOME.csv', index=False)
    print(json.dumps(res))
    print(tab.round(2).to_string())
    prim = tab.iloc[0]
    res['verdict'] = ('Income effect detected' if prim.cumulative_t_t1_hi < 0 and prim.placebo_leads_lo <= 0 <= prim.placebo_leads_hi
                      else ('Not claimed: placebo fails' if prim.cumulative_t_t1_hi < 0 else 'Not detected'))
    # descriptive: heavily affected SA2s, event-time mean of residual vs comparison
    big = dose[(dose.dose >= 0.25) & dose.fy.between(2016, 2020)].sort_values('dose').groupby('SA2').tail(1)
    res['heavily_affected_sa2s'] = int(len(big))
    pp = p[p.SA2.isin(big.SA2)].merge(big[['SA2', 'fy']].rename(columns={'fy': 'fire_fy'}), on='SA2')
    # simpler: within each heavily affected SA2, demean log_sum by its own pre-fire mean minus the comparison path
    comp = p[~p.SA2.isin(big.SA2)].groupby(['GCCSA', 'fy']).log_sum.mean()
    pp['adj'] = pp.log_sum - [comp.get((g, t), np.nan) for g, t in zip(pp.GCCSA, pp.fy)]
    pp['rel'] = pp.fy - pp.fire_fy
    pre = pp[pp.rel < 0].groupby('SA2').adj.mean()
    pp['dev_pct'] = (pp.adj - pp.SA2.map(pre)) * 100
    ev = pp.groupby('rel').dev_pct.agg(['mean', 'count', 'std']).reset_index()
    ev['se'] = ev['std'] / np.sqrt(ev['count'])
    ev.to_csv(OUT / 'DAY5_HEAVY_EVENT.csv', index=False)
    print(ev.round(2).to_string())
    json.dump(res, open(OUT / 'DAY5_META.json', 'w'), indent=2)
    print(res['verdict'])


if __name__ == '__main__':
    main()
