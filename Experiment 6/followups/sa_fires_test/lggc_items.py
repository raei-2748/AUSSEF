"""Extract the LGGC items the frozen SA recipes need (PRESPEC 2.1, 4), by HEADER LABEL not by position, for FY2013-14 ... FY2020-21.
Writes data/extra_fires/lggc_items.csv (one row per fy x council, $000 and %), lggc_column_map.csv and identity checks to logs/lggc_items.log.
No fire council is singled out; this is the whole-state table.
Run: /Users/ray/.venv/bin/python lggc_items.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lggc_lib as L

OUT = Path('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/extra_fires')
WANT = {   # item -> (report, header regex)
    'grants': (2, r'^Grants'),
    'total_op_revenue': (2, r'Total Operating Revenue|\(3\) Total Operating|Total\s+Operating\s+Revenue'),
    'employee': (3, r'^Employee'), 'materials': (3, r'^Materials'), 'finance_costs': (3, r'^Finance Costs'),
    'depreciation': (3, r'^Depreciation'), 'total_op_expenses': (3, r'Total Operating'), 'op_surplus': (3, r'^Operating Surplus'),
    'cash': (5, r'^Cash and'), 'other_fin_assets': (5, r'^Other Financial'), 'borrowings': (5, r'^Borrowings'),
    'osr_published': (8, r'^Operating Surplus Ratio'), 'last_r8': (8, None),
}
FUNCS = ['Community Support', 'Community Amenities', 'Library Services', 'Cultural Services', 'Recreation', 'Waste Management', 'Other Environment']
log = []
rows, cmap = [], []
for fy in L.FILES:
    rep, nc = L.read_reports(fy)
    lab = {rn: L.col_labels(fy, rn) for rn in (2, 3, 5, 8, 9)}
    cols = {}
    for k, (rn, pat) in WANT.items():
        labels, n = lab[rn]
        if k == 'last_r8':
            j = n - 1
        elif k in ('grants', 'total_op_revenue') and rn == 2:
            j = n - 6 if k == 'grants' else n - 1          # 6th from right / last (header labels of Report 2 are ambiguous)
        else:
            j = L.find_col(labels, pat)
        assert isinstance(j, int), (fy, k, j, labels)
        cols[k] = j
        cmap.append(dict(fy=fy, item=k, report=rn, cluster=j, header=labels.get(j, '(right-most column)')))
    for f in FUNCS:
        j = L.find_col(lab[9][0], r'^' + f.replace(' ', r'\s*'))
        assert isinstance(j, int), (fy, f, j)
        cols['fn_' + f] = j
        cmap.append(dict(fy=fy, item='fn_' + f, report=9, cluster=j, header=lab[9][0][j]))
    tot9 = L.find_col(lab[9][0], r'Total\s+Operating') if any('Total' in t and 'Operating' in t for t in lab[9][0].values()) else None
    r8_last_label = lab[8][0].get(cols['last_r8'], '')
    councils = sorted(rep[2])
    for c in councils:
        rec = dict(fy=fy, council=c)
        for k, j in cols.items():
            rn = WANT[k][0] if k in WANT else 9
            rec[k] = rep[rn].get(c, {}).get(j, np.nan)
        rec['r8_last_label'] = r8_last_label
        rec['fn_total_r9'] = rep[9].get(c, {}).get(tot9, np.nan) if isinstance(tot9, int) else np.nan
        rows.append(rec)
    # identity checks (Y-blind, whole state)
    d = pd.DataFrame([r for r in rows if r['fy'] == fy])
    e1 = (d.total_op_revenue - d.total_op_expenses - d.op_surplus).abs()
    e2 = (d.employee + d.materials + d.finance_costs + d.depreciation - d.total_op_expenses).abs()
    log.append(f'FY{fy}-{str(fy+1)[2:]}: councils {len(d)}; |revenue - expenses - surplus| > 1: {(e1>1).sum()}; |employee+materials+finance+depreciation - total expenses| > 5% of total: {(e2 > 0.05*d.total_op_expenses).sum()}; '
               f'Report 8 last column = "{r8_last_label}"; Report 9 has total column: {isinstance(tot9, int)}; missing cash {d.cash.isna().sum()}, grants {d.grants.isna().sum()}')
df = pd.DataFrame(rows)
df.to_csv(OUT / 'lggc_items.csv', index=False)
pd.DataFrame(cmap).to_csv(OUT / 'lggc_column_map.csv', index=False)
Path('logs').mkdir(exist_ok=True)
Path('logs/lggc_items.log').write_text('\n'.join(log) + '\n')
print('\n'.join(log))
