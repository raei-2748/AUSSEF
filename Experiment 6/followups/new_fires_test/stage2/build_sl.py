"""Stage 2 (exploratory): NSW Oct 2013 social-loss (SL) pillar from DSS, recipe in PRESPEC_STAGE2.md section 1.2.
Writes results_stage2/SL_nsw2013.csv (and prints only counts)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from nf_lib import FED, INP, RAW, RES, place_signed  # noqa: E402

OUT = HERE / 'results_stage2'
OUT.mkdir(exist_ok=True)
COMPONENTS = ['Newstart_Allowance', 'Youth_Allowance_other', 'Parenting_Payment_Single', 'Parenting_Payment_Partnered', 'Disability_Support_Pension',
              'Carer_Payment', 'Special_Benefit', 'Sickness_Allowance', 'Partner_Allowance', 'Widow_Allowance', 'Widow_B_Pension',
              'Wife_Pension_Partner_on_Age_Pension', 'Wife_Pension_Partner_on_Disability_Support_Pension']


def total(f):
    d = pd.read_csv(RAW / 'p_stage2_dss' / f, dtype=str)
    d = d[d.LGA.str.fullmatch(r'\d{5}') & d.LGA.str.startswith('1')].copy()
    supp = d[COMPONENTS].apply(lambda s: s.str.strip() == '<20')          # Amendment 1: suppressed "<20" counts as 10
    num = d[COMPONENTS].apply(lambda s: pd.to_numeric(s.str.replace(',', ''), errors='coerce')).mask(supp, 10)
    d['income_support_total'] = num.sum(axis=1, min_count=len(COMPONENTS)).where(num.notna().all(axis=1))
    d['n_imputed'] = supp.sum(axis=1)
    return d.set_index('LGA')[['LGA name', 'income_support_total', 'n_imputed']]


before, after = total('dss_sep2013_by2013lga_and_payment.csv'), total('dss_mar2014_by2014lga_and_payment.csv')
e = pd.read_excel(FED / 'data/abs/32180DS0004_2001-25.xlsx', 'Table 1', header=None)
years = e.iloc[4, 2:].astype(int).tolist()
body = e.iloc[6:, :2 + len(years)].dropna(subset=[0])
body = body[body[0].astype(str).str.fullmatch(r'\d{5}')]
body.columns = ['code', 'name'] + years
erp = pd.to_numeric(body.set_index(body.code.astype(str))[2012], errors='coerce')

t = before.join(after, lsuffix='_before', rsuffix='_after', how='outer')
t['erp2012'] = erp.reindex(t.index)
t['change'] = t.income_support_total_after - t.income_support_total_before
t['per1000'] = t.change / (t.erp2012 / 1000)
CG = pd.read_csv(RES / 'comparison_groups.csv', dtype={'lga_code': str, 'lga_vintage': str})
g = CG[(CG.event == 'NSW_2013_oct') & (CG.window == 'FY2013-14') & (CG.lga_vintage == '2015')]
nofire = set(g[~g.has_fire_100ha].lga_code)
comp = t.loc[t.index.isin(nofire), 'per1000'].dropna()
med = float(comp.median())
t['excess'] = t.per1000 - med
t['raw_SL_signed'] = t.excess
ref = pd.read_csv(INP / 'master_reference_indicators.csv').SL_income_support_excess_signed
t['pct_SL'] = [place_signed(v, ref) for v in t.excess]
roster = pd.read_csv(RES / 'roster.csv', dtype={'lga_code': str})
roster = roster[roster.event == 'NSW_2013_oct']
o = roster[['lga_code', 'lga_name']].merge(t.reset_index().rename(columns={'LGA': 'lga_code'}), on='lga_code', how='left')
o.to_csv(OUT / 'SL_nsw2013.csv', index=False)
print('comparison councils', len(comp), 'median per-1000 change', round(med, 3), '| roster rows with SL', int(o.pct_SL.notna().sum()), 'of', len(o))
print('quarters: Sep 2013 -> Mar 2014; components', len(COMPONENTS))
