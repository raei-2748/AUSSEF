"""Shared loaders for the FP-outcome follow-up (Experiment 6).

Everything here is read-only on existing data:
  - master sheet of the XY workbook (218 council x fire rows, header=2, 'N/A' text coerced to missing)
  - inputs/fiscal_panel_by_council_name.csv : the council fiscal panel exactly as the dataset builder sees it
    (src/socio.py fiscal(): NSW OLG Time Series Data first, AUSSEF fiscal panels to fill gaps), keyed by normalised
    council name and financial-year START year. Dumped once from the main checkout, read-only.
  - inputs/fire_pieces_all.csv : every fire x council piece (6,484) with the hectares burned inside the council,
    from fire_event_dataset/out/fires.csv. Used only to say which council-years had a fire of 100 ha or more.
  - Experiment 6 results/ROWS_WITH_SCORE_v2.csv (main checkout): the pre-fire block scores F (fiscal), V (vulnerability).

The excess rule is the dataset's own (fire_event_dataset/src/anomaly.py):
    excess = council change - median change over the same period in NSW councils with no fire of >= 100 ha inside them
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INPUTS = HERE / 'inputs'
RESULTS = HERE / 'results'
MAIN = Path('/Users/ray/Research/AUSSEF - Local')
ROWS_V2 = MAIN / 'Experiment 6/results/ROWS_WITH_SCORE_v2.csv'
WORKBOOK = Path('/Users/ray/Research/AUSSEF - Local/data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx')
COMPARE_HA = 100
SEED = 20260929          # same seed and 2,000 cluster-bootstrap draws as Experiment 6
N_BOOT = 2000


def norm(name):
    """Same council-name key as fire_event_dataset/src/socio.py."""
    s = str(name).lower().replace('(nsw)', '')
    s = re.sub(r'\((a|c|s|m|rc|t)\)', ' ', s)
    s = re.sub(r'\b(city|council|shire|regional|municipal|of|the)\b', ' ', s)
    return re.sub(r'[^a-z]', '', s)


def fy_start(ts):
    ts = pd.Timestamp(ts)
    return ts.year if ts.month >= 7 else ts.year - 1


def load_master():
    m = pd.read_excel(WORKBOOK, sheet_name='master', header=2, keep_default_na=False, na_values=[''])
    m['region_id'] = m.region_id.astype(int)
    m['agrn'] = m.agrn.astype(str)
    m['fy'] = pd.to_datetime(m.first_fire_start).map(fy_start)
    m['key'] = m.region_name.map(norm)
    m['share'] = pd.to_numeric(m.X_fire_share_of_council_burned, errors='coerce')
    m['black_summer'] = m.agrn == '871'
    for c in m.columns:
        if c.startswith(('FP', 'DL', 'IL', 'SL')) or c == 'Y':
            m[c] = pd.to_numeric(m[c], errors='coerce')     # 'N/A' text -> missing
    return m


def load_panel():
    """Council fiscal panel by (normalised name, FY start). Adds derived columns used by the audit."""
    p = pd.read_csv(INPUTS / 'fiscal_panel_by_council_name.csv')
    p['own_source_rev_aud'] = p.own_source_pct / 100 * p.total_revenue_including_capital_aud
    return p


def load_fire_flags():
    """Set of (normalised council name, FY start) with a fire >= COMPARE_HA ha burning inside the council."""
    f = pd.read_csv(INPUTS / 'fire_pieces_all.csv', parse_dates=['date_start'])
    f = f[f.region_burn_area_ha >= COMPARE_HA].copy()
    f['fy'] = f.date_start.map(fy_start)
    f['key'] = f.region_name.map(norm)
    return set(zip(f.key, f.fy))


def wide(panel, metric):
    return panel.pivot_table(index='key', columns='year_start', values=metric, aggfunc='first')


def excess_for_rows(panel, flags, rows, metric, lag, kind='diff'):
    """Dataset rule, vectorised. kind='diff': change in the metric; kind='pct': % change (metric is a $ amount).
    Returns a Series indexed like `rows`; the comparison median is per fire FY (as in anomaly.py)."""
    tab = wide(panel, metric)
    med = {}
    for x in sorted(set(rows.fy)):
        if (x + lag) in tab.columns and (x - 1) in tab.columns:
            base = tab[x - 1]
            ch = (tab[x + lag] - base) if kind == 'diff' else (tab[x + lag] - base) / base * 100
            comp = [k for k in ch.index if not any((k, x + j) in flags for j in range(0, lag + 1))]
            med[x] = float(ch.loc[comp].median())
        else:
            med[x] = np.nan
    out = []
    for k, x in zip(rows.key, rows.fy):
        if k in tab.index and (x + lag) in tab.columns and (x - 1) in tab.columns:
            a, b = tab.at[k, x + lag], tab.at[k, x - 1]
            ch = (a - b) if kind == 'diff' else ((a - b) / b * 100 if b else np.nan)
            out.append(ch - med[x])
        else:
            out.append(np.nan)
    return pd.Series(out, index=rows.index)


def spearman_fast(x, y):
    """Spearman rho on paired arrays (no NaNs)."""
    from scipy.stats import rankdata
    if len(x) < 4:
        return np.nan
    rx, ry = rankdata(x), rankdata(y)
    sx, sy = rx.std(), ry.std()
    if sx == 0 or sy == 0:
        return np.nan
    return float(np.corrcoef(rx, ry)[0, 1])
