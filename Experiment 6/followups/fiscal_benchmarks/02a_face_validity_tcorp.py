"""Step 2a (no Y): face validity of the benchmark measure against NSW Treasury Corporation's 2013 Financial
Sustainability Rating (FSR), as reproduced council by council in IPART's October 2015 'Assessment of Council Fit
for the Future Proposals: Appendix C' (TCORP_FSR_2013_from_IPART_AppendixC.csv, parsed from that PDF).

The benchmark measure is computed from the raw OLG file (olg_wide.parquet) for FY2013-14 and FY2014-15 so that the
pre-2016 councils (before mergers) are covered. TCorp's ratings rest on earlier data (to about FY2012-13), so this
is a persistence check, not a same-period check.
Run: python3 02a_face_validity_tcorp.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

from bench_common import BENCH, year_table

HERE = Path(__file__).resolve().parent
sys.path.insert(0, '/Users/ray/Research/AUSSEF/fire_event_dataset/src')
from olg import norm_name  # noqa: E402

OLG_WIDE = Path('/Users/ray/Research/AUSSEF/fire_event_dataset/data/olg/olg_wide.parquet')
COLMAP = {'operating_performance': 'operating_performance_ratio_pct', 'own_source_revenue': 'own_source_revenue_pct',
          'unrestricted_current': 'unrestricted_current_ratio', 'debt_service_cover': 'debt_service_cover_ratio',
          'cash_expense_cover': 'cash_expense_cover_ratio_months',
          'renewals': 'building_infrastructure_renewals_ratio_pct', 'infra_backlog': 'infrastructure_backlog_ratio_pct',
          'asset_maintenance': 'asset_maintenance_ratio_pct', 'debt_service_ratio': 'debt_service_ratio_pct'}
FSR_ORD = {'Distressed': 1, 'Very Weak': 2, 'Weak': 3, 'Moderate': 4, 'Sound': 5, 'Strong': 6, 'Very Strong': 7}
lines = []


def log(s=''):
    print(s)
    lines.append(str(s))


def main():
    w = pd.read_parquet(OLG_WIDE)
    w = w[w.fy_start.isin([2013, 2014])].rename(columns={'fy_start': 'year'})
    w['region_id'] = w.council_name_norm
    yt = year_table(w, COLMAP)
    g = yt[yt.usable].groupby('council_name_norm').agg(met=('n_met', 'sum'), meas=('n_measurable', 'sum'),
                                                       years=('year', 'size'))
    g['bench_share'] = g.met / g.meas
    t = pd.read_csv(HERE / 'TCORP_FSR_2013_from_IPART_AppendixC.csv')
    t = t[t.n_tcorp == 1]
    t = t[~t.name.str.contains(r',| & | AND ', regex=True)]                # one council per page only
    t['fsr'] = t.tcorp.str.split('/').str[0]
    t['outlook'] = t.tcorp.str.split('/').str[1]
    t['key'] = t.name.map(norm_name)
    d = t.merge(g, left_on='key', right_index=True, how='left')
    d['fsr_ord'] = d.fsr.map(FSR_ORD)
    log('== TCorp 2013 FSR vs benchmark share (OLG raw FY2013-14 + FY2014-15), single-council IPART pages')
    log(f'IPART pages with a TCorp rating and one council: {len(t)}; matched to OLG data: {int(d.bench_share.notna().sum())}')
    dd = d.dropna(subset=['bench_share'])
    r = spearmanr(dd.fsr_ord, dd.bench_share)
    log(f'Spearman(TCorp FSR ordinal, benchmark share) = {r[0]:+.2f} (p={r[1]:.3g}, n={len(dd)})')
    log(dd.groupby('fsr').bench_share.agg(['count', 'mean', 'median']).reindex(
        ['Very Weak', 'Weak', 'Moderate', 'Sound', 'Strong']).round(3).to_string())
    weak = dd.fsr.isin(['Weak', 'Very Weak'])
    u = mannwhitneyu(dd.bench_share[weak], dd.bench_share[~weak], alternative='less')
    auc = 1 - u.statistic / (weak.sum() * (~weak).sum())
    log(f'AUC for spotting TCorp Weak/Very Weak ({int(weak.sum())} councils) vs others ({int((~weak).sum())}) by '
        f'LOW benchmark share: {auc:.2f} (0.5 = no signal); one-sided p={u.pvalue:.3g}')
    log('\nTCorp Weak / Very Weak councils and their benchmark share:')
    log(dd[weak][['name', 'fsr', 'outlook', 'bench_share', 'years']].sort_values('bench_share').round(3).to_string(index=False))
    log('\nlowest 12 benchmark shares among matched councils:')
    log(dd.sort_values('bench_share')[['name', 'fsr', 'outlook', 'bench_share']].head(12).round(3).to_string(index=False))
    dd.to_csv(HERE / 'FACE_VALIDITY_TCORP.csv', index=False)
    (HERE / 'FACE_VALIDITY_TCORP.txt').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
