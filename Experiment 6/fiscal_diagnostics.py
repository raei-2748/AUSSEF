"""Why did the pre-fire fiscal block (F) show nothing? Three checks, all read-only on existing data.

1. Overlap: is F just vulnerability (V) in disguise?  (F vs V; F vs Y after removing V)
2. Blur: do the six fiscal ratios agree with each other?  (mean off-diagonal Spearman)
3. Disaster money: do hit councils get more grants/revenue, and does controlling for it change how
   FP (council fiscal-pressure pillar) responds to damage?  Also Black Summer reported damage vs funding.

Not significance-tested; descriptive Spearman correlations. Writes results/FISCAL_DIAGNOSTICS.txt.
Run: python3 fiscal_diagnostics.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
WORKBOOK = Path('/Users/ray/Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/Master Workbook (read by the analysis scripts)/nsw_bushfires_2015_2025_XY.xlsx')
FISCAL = ['fiscal_cash_cover_months_fy', 'fiscal_own_source_pct_fy', 'fiscal_debt_service_ratio_pct_fy',
          'fiscal_operating_ratio_pct_fy', 'fiscal_infra_backlog_ratio_pct_fy',
          'fiscal_unrestricted_current_ratio_fy']
lines = []


def log(s=''):
    print(s)
    lines.append(str(s))


def rho(a, b):
    d = pd.concat([a, b], axis=1).dropna()
    return (round(spearmanr(d.iloc[:, 0], d.iloc[:, 1])[0], 2), len(d)) if len(d) >= 8 else (None, len(d))


def partial(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    res = lambda a: a - np.polyval(np.polyfit(rz, a, 1), rz)
    return round(np.corrcoef(res(rx), res(ry))[0, 1], 2)


def main():
    items = pd.read_csv(OUT / 'COUNCIL_ITEMS_v2.csv')
    rows = pd.read_csv(OUT / 'ROWS_WITH_SCORE_v2.csv')
    log('== 1. overlap of fiscal (F) and vulnerability (V) blocks')
    aff = items[items.region_id.isin(rows.region_id)]
    log(f'F vs V, all {len(items)} councils: {spearmanr(items.F, items.V)[0]:.2f}; '
        f'{len(aff)} councils with a fire: {spearmanr(aff.F, aff.V)[0]:.2f}')
    d = rows.dropna(subset=['Y', 'F', 'V'])
    for lab, sub in [('all rows', d), ('>= 5% burned', d[d.share >= 0.05])]:
        log(f'{lab} (n={len(sub)}): F vs Y raw {spearmanr(sub.F, sub.Y)[0]:+.2f}, '
            f'controlling V {partial(sub.F, sub.Y, sub.V):+.2f}; V vs Y controlling F '
            f'{partial(sub.V, sub.Y, sub.F):+.2f}')
    log('\n== 2. do the six fiscal ratios agree?')
    c = items[FISCAL].corr('spearman')
    c.index = c.columns = [x.replace('fiscal_', '').replace('_fy', '') for x in FISCAL]
    log(c.round(2).to_string())
    log(f'mean off-diagonal |rho| = {np.abs(c.values[np.triu_indices(6, 1)]).mean():.2f}')

    log('\n== 3. disaster money')
    m = pd.read_excel(WORKBOOK, sheet_name='master', header=2, keep_default_na=False, na_values=[''])
    num = ['X_fire_share_of_council_burned', 'DL', 'Y', 'FP', 'FP_total_revenue_change_event_pct',
           'FP_total_revenue_change_plus1_pct', 'FP_grants_per_capita_change_plus1_excess',
           'FP_own_source_revenue_change_plus1_pct', 'FP_rank_cash_cover_drawdown_excess_t_t1',
           'FP_rank_services_crowd_out_excess_t_1', 'FP_rank_renewals_ratio_rise_excess_t_1',
           'FP_reported_audit_lg2020_damage_estimate_aud', 'FP_reported_audit_lg2020_funding_received_aud']
    for col in num:
        m[col] = pd.to_numeric(m[col], errors='coerce')     # 'N/A' text -> missing
    m['share'] = m.X_fire_share_of_council_burned
    cols = ['FP_total_revenue_change_event_pct', 'FP_total_revenue_change_plus1_pct',
            'FP_grants_per_capita_change_plus1_excess', 'FP_own_source_revenue_change_plus1_pct']
    for col in cols:
        log(f'{col.replace("FP_", "")}: vs burned share {rho(m[col], m.share)}, vs DL {rho(m[col], m.DL)}, '
            f'vs Y {rho(m[col], m.Y)}')
    big, small = m.share >= 0.05, m.share < 0.02
    log('median by group')
    log(pd.DataFrame({'>=5% burned': m.loc[big, cols].median(), '<2% burned': m.loc[small, cols].median()})
        .round(2).to_string())
    log(f'n big {int(big.sum())}, small {int(small.sum())}')
    rev = 'FP_total_revenue_change_plus1_pct'
    d1 = m.dropna(subset=['FP', 'DL', rev])
    log(f'FP vs DL raw {spearmanr(d1.FP, d1.DL)[0]:+.2f}, controlling revenue change '
        f'{partial(d1.FP, d1.DL, d1[rev]):+.2f} (n={len(d1)})')
    d2 = m.dropna(subset=['FP', 'share', rev])
    log(f'FP vs burned share raw {spearmanr(d2.FP, d2.share)[0]:+.2f}, controlling '
        f'{partial(d2.FP, d2.share, d2[rev]):+.2f} (n={len(d2)})')
    d3 = d2[d2.share >= 0.05]
    log(f'  >= 5% burned only: raw {spearmanr(d3.FP, d3.share)[0]:+.2f}, controlling '
        f'{partial(d3.FP, d3.share, d3[rev]):+.2f} (n={len(d3)})')
    bs = m[m.agrn.astype(str) == '871'][['region_name', 'FP_reported_audit_lg2020_damage_estimate_aud',
                                        'FP_reported_audit_lg2020_funding_received_aud']].dropna()
    bs['funding_to_damage'] = (bs.FP_reported_audit_lg2020_funding_received_aud
                               / bs.FP_reported_audit_lg2020_damage_estimate_aud)
    log(f'Black Summer councils with reported damage AND funding: {len(bs)}')
    log(bs.round(2).to_string())
    (OUT / 'FISCAL_DIAGNOSTICS.txt').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
