"""Step 1: which of the 218 declared-event x council rows have DL, and what is missing (by year, fire size, council)."""
import numpy as np
import pandas as pd

from common import OUT, load_key_events, load_master

pd.set_option('display.width', 250)
pd.set_option('display.max_rows', 300)

m = load_master()
ke = load_key_events()
d = m.merge(ke[['agrn', 'declaration_name', 'decl_start', 'decl_end']], on='agrn', how='left')
num = lambda c: pd.to_numeric(d[c], errors='coerce')
d['DL_present'] = d.DL.notna()
d['homes_destroyed'] = num('DL_homes_destroyed_in_council')
d['homes_damaged'] = num('DL_homes_damaged_sourced')
d['homes_per_1000'] = num('DL_homes_destroyed_per_1000_dwellings')
d['dwellings_census'] = num('X_socio_dwellings_census')
d['basis'] = d.info_DL_homes_destroyed_basis.fillna('').str.split(',').str[0]
d['ica_council_value'] = num('DL_insurance_loss_raw')
d['size_bin'] = pd.cut(d.share, [-1, .001, .01, .02, .05, .10, 1.01],
                       labels=['<0.1%', '0.1-1%', '1-2%', '2-5%', '5-10%', '>=10%'])
d['big5'] = d.share >= 0.05
d['black_summer'] = d.agrn == '871'

cols = ['agrn', 'declaration_name', 'region_id', 'region_name', 'year', 'first_fire_start', 'share', 'burn_ha', 'size_bin',
        'DL_present', 'homes_destroyed', 'homes_damaged', 'homes_per_1000', 'dwellings_census', 'basis',
        'ica_council_value', 'black_summer']
d[cols].to_csv(OUT / 'DL_ROW_STATUS.csv', index=False)

print('rows', len(d), 'DL present', d.DL_present.sum(), 'missing', (~d.DL_present).sum())
print('declared events', d.agrn.nunique(), '| events with >=1 DL row', d[d.DL_present].agrn.nunique(),
      '| events with no DL row', d.groupby('agrn').DL_present.any().eq(False).sum())
print('councils', d.region_id.nunique(), '| councils with >=1 DL row', d[d.DL_present].region_id.nunique())

print('\n-- basis of the present values')
print(d[d.DL_present].basis.value_counts())
print('present with homes_destroyed == 0:', ((d.homes_destroyed == 0) & d.DL_present).sum())
print('present with homes_destroyed > 0:', ((d.homes_destroyed > 0) & d.DL_present).sum())

def prof(g, name):
    t = d.groupby(g, observed=True).agg(rows=('DL_present', 'size'), with_DL=('DL_present', 'sum'),
                                        events=('agrn', 'nunique'), median_share=('share', 'median'),
                                        max_share=('share', 'max'), ha=('burn_ha', 'sum'))
    t['missing'] = t.rows - t.with_DL
    t['pct_missing'] = (100 * t.missing / t.rows).round(0)
    print(f'\n-- by {name}'); print(t.round(4).to_string())
    return t

t_year = prof('year', 'year of fire start')
t_size = prof('size_bin', 'share of council burned')
prof('black_summer', 'Black Summer (871) vs other')
t_cn = d.groupby(['region_id', 'region_name']).agg(rows=('DL_present', 'size'), with_DL=('DL_present', 'sum'),
                                                   max_share=('share', 'max'), tot_ha=('burn_ha', 'sum')).reset_index()
t_cn['missing'] = t_cn.rows - t_cn.with_DL
t_cn = t_cn.sort_values(['missing', 'tot_ha'], ascending=False)
print('\n-- councils with most missing rows'); print(t_cn.head(25).to_string())
print('councils with rows but no DL at all:', (t_cn.with_DL == 0).sum(), 'of', len(t_cn))

# missing by size on the 5% / 2% cut used in Experiment 6
for thr in (0.02, 0.05, 0.10):
    s = d[d.share >= thr]
    print(f'\nshare >= {thr:.0%}: rows {len(s)}, DL present {s.DL_present.sum()}, missing {(~s.DL_present).sum()}')
print('\nmissing rows >= 5% burned:')
print(d[(~d.DL_present) & (d.share >= .05)][['agrn', 'declaration_name', 'region_name', 'year', 'share', 'burn_ha']].to_string())

# is missingness related to size?
from scipy.stats import mannwhitneyu
a = d[d.DL_present].share; b = d[~d.DL_present].share
print('\nshare burned, DL present median %.4f vs missing median %.4f; MWU p=%.2g' % (a.median(), b.median(), mannwhitneyu(a, b).pvalue))
a = d[d.DL_present].burn_ha; b = d[~d.DL_present].burn_ha
print('burn_ha, DL present median %.0f vs missing median %.0f; MWU p=%.2g' % (a.median(), b.median(), mannwhitneyu(a, b).pvalue))

t_year.to_csv(OUT / 'PROFILE_BY_YEAR.csv')
t_size.to_csv(OUT / 'PROFILE_BY_SIZE.csv')
t_cn.to_csv(OUT / 'PROFILE_BY_COUNCIL.csv', index=False)
ev = d.groupby(['agrn', 'declaration_name']).agg(rows=('DL_present', 'size'), with_DL=('DL_present', 'sum'), year=('year', 'min'),
                                                 max_share=('share', 'max'), ha=('burn_ha', 'sum')).reset_index()
ev['missing'] = ev.rows - ev.with_DL
ev.sort_values(['missing', 'ha'], ascending=False).to_csv(OUT / 'PROFILE_BY_EVENT.csv', index=False)
print('\n-- events ranked by missing rows'); print(ev.sort_values(['missing', 'ha'], ascending=False).head(30).to_string())
