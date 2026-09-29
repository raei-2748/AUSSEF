"""Shared definitions for the benchmark-count fiscal measure. PRE-SPECIFIED 2026-09-29, before any Y was read.

Nothing in this file, in 01_build_measure.py or in 02_face_validity.py reads Y, DL, IL, FP or SL. Only
03_validate_vs_Y.py does, and it is run after the measure and the face-validity table are on disk.

==== BENCHMARKS (NSW Office of Local Government; verified from the documents, see FINDINGS.md) ====
  operating performance ratio      > 0 %        Audit Office 2018 App. 9: "greater than zero per cent"; yourcouncil.nsw.gov.au: "0% or greater"
  own source operating revenue     > 60 %       "greater than 60 per cent"
  unrestricted current ratio       > 1.5 x      "greater than 1.5 times"
  debt service cover ratio         > 2 x        "greater than two times"
  cash expense cover ratio         > 3 months   "greater than three months"
  building & infrastructure renewals ratio  > 100 %   Code of Accounting Practice s.4: "benchmark is greater than 100%"
  infrastructure backlog ratio     < 2 %        "benchmark is less than 2%"
  asset maintenance ratio          > 100 %      "benchmark is greater than 100%"
NOT used: rates & annual charges outstanding (<5% metro / <10% rural: not in the workbook and the metro/rural
split is ambiguous between OLG documents); debt service ratio (>0 and <20%: a Fit-for-the-Future-only test that
would penalise debt-free councils); real operating expenditure per capita (a trend test).

==== RULES (fixed now; none is tuned) ====
  * lga_year.year is the financial-year START year (checked against the raw OLG file: year 2014 = FY2014-15).
  * Fire financial year f = year(first_fire_start) if month >= 7 else year - 1. The three pre-fire years are
    f-1, f-2, f-3 (the fire's own FY is excluded). Source: lga_year (same source as the old F), FY2014-2023.
  * A benchmark is 'measurable' in a year if its ratio is not blank. A blank debt service cover ratio with a
    debt service ratio of exactly 0 (no debt) counts as MET. Any other blank is dropped, not counted as failed.
  * A council-year is 'usable' if >= 5 of the 8 benchmarks are measurable. A council-window is usable if >= 2 of
    its 3 pre-fire years are usable; otherwise the row has no measure and is dropped from the tests.
  * bench_share (PRIMARY, higher = healthier) = benchmark-years met / benchmark-years measurable, pooled over the
    usable pre-fire years. It equals (average number of benchmarks met per year, scaled to 8) / 8 and it equals the
    average share of years in which each benchmark was met, so it covers both 'number met' and 'share of years met'.
  * stress_bench = 1 - bench_share (higher = weaker finances, same orientation as the old F block). The
    pre-specified hypothesis is rho(stress_bench, impact) > 0.
  Secondary (reported, not used to choose): years_share = share of usable years meeting more than half of the
  measurable benchmarks; avg3_share = Fit-for-the-Future style, each benchmark judged on the mean of its ratio over
  the usable years; fin5_share (first five benchmarks) and infra3_share (last three); F_tm = the OLD six-ratio
  percentile block recomputed inside each financial year and averaged over the same pre-fire years (isolates
  'stale 2014/15 snapshot' from 'benchmark counting').
"""
import numpy as np
import pandas as pd

# name: (lga_year column, direction, threshold, group)
BENCH = {
    'operating_performance': ('fiscal_operating_ratio_pct_fy', '>', 0.0, 'fin'),
    'own_source_revenue': ('fiscal_own_source_pct_fy', '>', 60.0, 'fin'),
    'unrestricted_current': ('fiscal_unrestricted_current_ratio_fy', '>', 1.5, 'fin'),
    'debt_service_cover': ('fiscal_debt_service_cover_ratio_fy', '>', 2.0, 'fin'),
    'cash_expense_cover': ('fiscal_cash_cover_months_fy', '>', 3.0, 'fin'),
    'renewals': ('fiscal_renewals_ratio_pct_fy', '>', 100.0, 'infra'),
    'infra_backlog': ('fiscal_infra_backlog_ratio_pct_fy', '<', 2.0, 'infra'),
    'asset_maintenance': ('fiscal_maintenance_ratio_pct_fy', '>', 100.0, 'infra'),
}
FIN = [k for k, v in BENCH.items() if v[3] == 'fin']
INFRA = [k for k, v in BENCH.items() if v[3] == 'infra']
MIN_MEASURABLE = 5          # of 8, for a usable council-year
MIN_YEARS = 2               # of 3, for a usable window
N_PRE = 3
# old F block items: lga_year column -> orientation (+1 higher is worse)
OLD_F_ITEMS = {'fiscal_cash_cover_months_fy': -1, 'fiscal_own_source_pct_fy': -1,
               'fiscal_debt_service_ratio_pct_fy': +1, 'fiscal_operating_ratio_pct_fy': -1,
               'fiscal_infra_backlog_ratio_pct_fy': +1, 'fiscal_unrestricted_current_ratio_fy': -1}


def _pass(x, direction, thr):
    return (x > thr) if direction == '>' else (x < thr)


def year_table(d, colmap=None):
    """d: one row per council-year with the lga_year fiscal columns (or a renamed copy via colmap
    {benchmark name: column}). Returns d plus <bench>_met (1/0/NaN), n_measurable, n_met, usable."""
    d = d.copy()
    for name, (col, direction, thr, _) in BENCH.items():
        c = (colmap or {}).get(name, col)
        x = d[c]
        met = pd.Series(np.where(x.isna(), np.nan, _pass(x, direction, thr).astype(float)), index=d.index)
        if name == 'debt_service_cover':                  # no debt: cover ratio blank and debt service ratio == 0
            dsr = d[(colmap or {}).get('debt_service_ratio', 'fiscal_debt_service_ratio_pct_fy')]
            met = met.mask(x.isna() & (dsr == 0), 1.0)
        d[f'{name}_met'] = met
    m = d[[f'{k}_met' for k in BENCH]]
    d['n_measurable'] = m.notna().sum(axis=1)
    d['n_met'] = m.sum(axis=1)
    d['usable'] = d.n_measurable >= MIN_MEASURABLE
    return d


def window_measure(yt, region_id, years):
    """Benchmark measures for one council over the given financial-year start years (year_table output)."""
    w = yt[(yt.region_id == region_id) & yt.year.isin(years) & yt.usable]
    out = dict(years_usable=len(w))
    if len(w) < MIN_YEARS:
        return out
    meas, met = w.n_measurable.sum(), w.n_met.sum()
    out['bench_share'] = met / meas
    out['bench_n_met_of8'] = 8 * met / meas
    out['years_share'] = ((w.n_met / w.n_measurable) > 0.5).mean()
    for grp, names in (('fin5_share', FIN), ('infra3_share', INFRA)):
        mm = w[[f'{k}_met' for k in names]]
        out[grp] = mm.sum().sum() / mm.notna().sum().sum() if mm.notna().sum().sum() else np.nan
    passes = []                                            # Fit-for-the-Future style: judge the multi-year mean
    for name, (col, direction, thr, _) in BENCH.items():
        x = w[col].dropna()
        if name == 'debt_service_cover' and len(x) == 0 and (w.fiscal_debt_service_ratio_pct_fy == 0).all():
            passes.append(1.0)
        elif len(x):
            passes.append(float(_pass(x.mean(), direction, thr)))
    out['avg3_share'] = float(np.mean(passes)) if passes else np.nan
    return out


def pct(s, sign):
    """0-1 percentile rank across councils, oriented so 1 = worse (same rule as build_and_validate_score.py)."""
    r = s.rank(pct=True)
    return r if sign > 0 else 1 - r + 1 / s.notna().sum()
