"""Excess-change ("abnormal") versions of the council-level Y components.

Bowen: Y should be the abnormal impact around a fire, not the natural movement of the economic or fiscal variable.
Each raw change (after vs before) also contains statewide movements (COVID in 2020, drought, rate cycles). Here each
council's change is compared with the median change, over the same period, of NSW councils that had NO fire of
COMPARE_HA or more burning inside them in that period:

    excess = change in this council − median change in comparison councils

This is a descriptive comparison, not a causal estimate. Columns end in `_excess`; the raw columns are kept.
"""
import numpy as np
import pandas as pd

from src import economy, socio

COMPARE_HA = 100  # a council-period counts as "with fire" if a fire burned >= this many ha inside it


def _fy(ts):
    ts = pd.Timestamp(ts)
    return ts.year if ts.month >= 7 else ts.year - 1


def add(r, ev, pieces):
    start = ev.set_index("event_id").start
    p = pd.DataFrame(pieces[["event_id", "LGA_CODE21", "LGA_NAME21", "region_burn_area_ha"]])
    p = p[p.region_burn_area_ha >= COMPARE_HA]
    p["start"] = p.event_id.map(start)
    p["code"] = p.LGA_CODE21.astype(str)
    p["key"] = p.LGA_NAME21.map(socio.norm)
    p["fy"] = p.start.map(_fy)
    p["q"] = p.start.dt.to_period("Q")
    fire_fy_code = set(zip(p.code, p.fy))
    fire_fy_key = set(zip(p.key, p.fy))
    fire_q = set(zip(p.code, p.q))

    lga = socio.population().reset_index()  # all NSW LGA codes present in ERP
    nsw_codes = sorted({c for c in r.region_id.astype(str)} | {c for c in lga.code.astype(str) if c.startswith("1")})

    # --- unemployment (quarterly SALM): change in rate, quarter after the fire-start quarter vs a year earlier
    sa = economy.salm().unemployment_rate
    ur = sa.unstack("period")
    ur = ur[ur.index.isin(nsw_codes)]
    cache = {}

    def ur_bench(q0):
        if q0 not in cache:
            ch = ur.get(q0 + 1) - ur.get(q0 - 3) if (q0 + 1) in ur.columns and (q0 - 3) in ur.columns else None
            if ch is None:
                cache[q0] = np.nan
            else:
                window = {q0 - 3 + k for k in range(5)}
                comp = [c for c in ch.index if not any((c, q) in fire_q for q in window)]
                cache[q0] = float(ch.loc[comp].median()) if comp else np.nan
        return cache[q0]

    q = r.event_id.map(start).dt.to_period("Q")
    r["IL_unemployment_rate_change_excess_pp"] = r.unemployment_rate_change_pp - [ur_bench(x) for x in q]

    # --- income (ABS PIA, by LGA code and FY): % change event FY vs previous, and FY+1 vs previous
    inc = socio.income()
    med = inc.median_income_aud.unstack(1)
    tot = inc.total_income_aud.unstack(1)

    def pct(tab, a, b):
        return (tab.get(a) - tab.get(b)) / tab.get(b) * 100 if a in tab.columns and b in tab.columns else None

    def bench(tab, fy, lag, key_set, idx_is_code=True):
        ch = pct(tab, fy + lag, fy - 1)
        if ch is None:
            return np.nan
        ch = ch[ch.index.astype(str).isin(nsw_codes)] if idx_is_code else ch
        comp = [c for c in ch.index if not any((str(c), fy + k) in key_set for k in range(0, lag + 1))]
        return float(ch.loc[comp].median()) if comp else np.nan

    fy = r.fy if "fy" in r else r.event_id.map(start).map(_fy)
    for col, tab, raw in (("SL_income_drop_excess_pct", med, "SL_income_drop_raw"),
                          ("IL_total_income_change_excess_pct", tot, "IL_total_income_change_pct_proxy")):
        b = {f: bench(tab, f, 0, fire_fy_code) for f in set(fy)}
        r[col] = r[raw] - fy.map(b)
    b1 = {f: bench(med, f, 1, fire_fy_code) for f in set(fy)}
    r["SL_income_change_plus1_pct"] = (r.median_income_aud_plus1 - r.median_income_aud_pre) / r.median_income_aud_pre * 100
    r["SL_income_change_plus1_excess_pct"] = r.SL_income_change_plus1_pct - fy.map(b1)

    # --- council finances (by normalised council name and FY): event FY vs previous, and FY+1 vs previous
    f = socio.fiscal()
    for metric, short in (("debt_service_ratio_pct", "debt_ratio"), ("operating_ratio_pct", "operating_ratio"),
                          ("cash_cover_months", "cash_cover"), ("service_share_pct", "service_share"),
                          ("roads_share_pct", "roads_share"),
                          ("building_infrastructure_renewals_ratio_pct", "renewals_ratio"),
                          ("grants_per_capita_aud", "grants_per_capita")):
        if metric not in f.columns:
            continue
        tab = f[metric].unstack(1)
        for lag, lab in ((0, "event"), (1, "plus1")):
            bm = {}
            for x in set(fy):
                if (x + lag) in tab.columns and (x - 1) in tab.columns:
                    ch = tab[x + lag] - tab[x - 1]
                    comp = [k for k in ch.index if not any((k, x + j) in fire_fy_key for j in range(0, lag + 1))]
                    bm[x] = float(ch.loc[comp].median()) if comp else np.nan
                else:
                    bm[x] = np.nan
            own = r[f"fiscal_{metric}_{lab}"] - r[f"fiscal_{metric}_pre"]
            r[f"FP_{short}_change_{lab}_excess"] = own - fy.map(bm)
    return r


DOC = {
    "IL_unemployment_rate_change_excess_pp": (
        "Unemployment-rate change (quarter after vs same quarter a year before) minus the median change in NSW councils "
        "with no fire >= 100 ha in that window", "pp", "DEWR SALM", "positive = unemployment rose more than comparison"),
    "SL_income_drop_excess_pct": (
        "Median-income % change (fire FY vs previous FY) minus the median change in councils with no fire >= 100 ha that FY",
        "%", "ABS PIA", "negative = income grew less than comparison"),
    "IL_total_income_change_excess_pct": (
        "Total-income % change (fire FY vs previous) minus comparison-council median", "%", "ABS PIA", "GRP proxy"),
    "SL_income_change_plus1_pct": ("Median-income % change, FY after the fire vs FY before", "%", "ABS PIA", "lagged"),
    "SL_income_change_plus1_excess_pct": ("As above minus comparison-council median", "%", "ABS PIA", "lagged"),
    "FP_debt_ratio_change_event_excess": ("Debt service ratio change (fire FY vs previous) minus comparison median", "pp",
                                          "council finance panel", ""),
    "FP_debt_ratio_change_plus1_excess": ("Debt service ratio change (FY after vs FY before) minus comparison median", "pp",
                                          "council finance panel", "lagged"),
    "FP_operating_ratio_change_event_excess": ("Operating ratio change (fire FY vs previous) minus comparison median", "pp",
                                               "council finance panel", ""),
    "FP_operating_ratio_change_plus1_excess": ("Operating ratio change (FY after vs FY before) minus comparison median",
                                               "pp", "council finance panel", "lagged"),
    "FP_cash_cover_change_event_excess": ("Cash cover change (fire FY vs previous) minus comparison median", "months",
                                          "council finance panel", ""),
    "FP_service_share_change_event_excess": ("Everyday-services share of spending, change (fire FY vs previous) minus "
                                             "comparison median", "pp", "NSW OLG", "negative = services squeezed"),
    "FP_service_share_change_plus1_excess": ("Everyday-services share of spending, change (FY after vs FY before) minus "
                                             "comparison median", "pp", "NSW OLG", "negative = services squeezed; crowd-out"),
    "FP_roads_share_change_event_excess": ("Roads & bridges share of spending, change (fire FY vs previous) minus comparison "
                                           "median", "pp", "NSW OLG", ""),
    "FP_roads_share_change_plus1_excess": ("Roads & bridges share of spending, change (FY after vs FY before) minus "
                                           "comparison median", "pp", "NSW OLG", "rebuilding shows up here"),
    "FP_renewals_ratio_change_event_excess": ("Building & infrastructure renewals ratio (renewal spending ÷ depreciation) "
                                              "change, fire FY vs previous, minus comparison median", "pp", "NSW OLG",
                                              "capital-side rebuilding, which operating-expense shares miss"),
    "FP_renewals_ratio_change_plus1_excess": ("Renewals ratio change (FY after vs FY before) minus comparison median", "pp",
                                              "NSW OLG", "rebuilding peaks a year or more after the fire"),
    "FP_grants_per_capita_change_event_excess": ("Grants & contributions per resident, change (fire FY vs previous) minus "
                                                 "comparison median", "AUD", "NSW OLG (grants % × total revenue ÷ population)",
                                                 "transfer intensity: DRFA and other grants; not a loss, a control"),
    "FP_grants_per_capita_change_plus1_excess": ("Grants & contributions per resident, change (FY after vs FY before) minus "
                                                 "comparison median", "AUD", "NSW OLG", "reimbursement lags the fire"),
    "FP_cash_cover_change_plus1_excess": ("Cash cover change (FY after vs FY before) minus comparison median", "months",
                                          "council finance panel", "lagged"),
}
