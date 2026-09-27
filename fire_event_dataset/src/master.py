"""One row per declared event × council with every variable (Bowen: "a row includes all the variables").

Row = the 218 rows of key_event_council (Y hierarchy from src/xy_format.build_y, extras from src/panel_extra).
Columns added here:
1. Per-fire variables aggregated over the event's fires inside the council (fires.csv rows whose
   official_declaration_agrn lists the AGRN, as src/key_events.py links them): sums for counts, max/min for
   intensity and weather, burned-area-weighted means for shares and terrain. Whole-fire totals (hotspot counts,
   the ICA loss proxy) are multiplied by the fire's share inside the council before summing ("share_sum"), so a fire
   that barely touches a council adds almost nothing and council values add up to the fire total.
2. Every lga_year council variable in three windows around the fire:
     _pre    the period before the fire                      -> X (council conditions)
     _event  the fire's own period                            -> Y source data
     _plus1  the period after                                 -> Y source data
   Periods: `_fy` columns by financial year (fire FY = FY holding the first fire start); `_june` columns and ERP
   population (a 30 June figure) by the 30 June before the fire FY (pre), at its end (event) and a year later
   (plus1); calendar-year columns (annual means of quarterly SALM, DSS, rent): pre = the calendar year before the
   fire year (wholly before the fire), event = the fire year if the fire started January–June, else the next year
   (so the event window lies mostly after the start), plus1 = the year after that.
   One-off columns (Census counts and shares, SEIFA, area, TRA 2017, REDS 2020, BCARR average growth) are taken
   once: the latest value dated at or before the fire's calendar year, else the earliest one after it (flagged in
   the variables sheet). Census columns therefore follow X17: 2016 Census for fires up to 2020, 2021 after.
Nothing is modelled.
"""
import numpy as np
import pandas as pd

from src.common import OUT

# (source column in fires.csv, aggregation, new name). Weights = burned area of the fire inside this council.
FIRE_AGG = [
    ("X5_hotspot_density", "max", "X_fire_hotspot_density_max"),
    ("hotspot_viirs_count", "share_sum", "X_fire_hotspot_viirs_count_in_council"),
    ("X4_fire_duration", "wmean", "X_fire_duration_days_wmean"),
    ("X2_FFDI", "wmean", "X_fire_ffdi_wmean"),
    ("kbdi_at_start", "max", "X_fire_kbdi_at_start_max"),
    ("drought_factor_at_start", "max", "X_fire_drought_factor_at_start_max"),
    ("rain_during_fire_mm", "min", "X_fire_rain_during_fire_mm_min"),
    ("X7_temp_max", "wmean", "X_fire_temp_max_wmean"),
    ("X8_humidity_min", "wmean", "X_fire_humidity_min_wmean"),
    ("X9_wind_max", "wmean", "X_fire_wind_max_wmean"),
    ("severity_share_low", "wmean", "X_fire_severity_share_low_wmean"),
    ("severity_share_moderate", "wmean", "X_fire_severity_share_moderate_wmean"),
    ("severity_share_high", "wmean", "X_fire_severity_share_high_wmean"),
    ("severity_share_extreme", "wmean", "X_fire_severity_share_extreme_wmean"),
    ("X10_elevation", "wmean", "X_env_elevation_wmean"),
    ("elevation_min", "min", "X_env_elevation_min"),
    ("elevation_max", "max", "X_env_elevation_max"),
    ("slope_p90", "max", "X_env_slope_p90_max"),
    ("X13_canopy_cover", "wmean", "X_env_canopy_cover_wmean"),
    ("canopy_cover_share_over_30pct", "wmean", "X_env_canopy_cover_share_over_30pct_wmean"),
    ("vegetation_forest_share", "wmean", "X_env_vegetation_forest_share_wmean"),
    ("vegetation_cleared_share", "wmean", "X_env_vegetation_cleared_share_wmean"),
    ("road_km_within_100m", "sum", "X_env_road_km_within_100m_sum"),
    ("X18_remoteness", "max", "X_socio_remoteness_class_max"),
    ("DL_insurance_loss_area_share_proxy", "share_sum", "DL_insurance_loss_area_share_proxy_in_council"),
]
FIRE_TEXT = [("ignition_cause", "X_fire_ignition_causes"), ("X12_vegetation", "X_env_vegetation_groups")]

STATIC_PREFIX = ("industry_share_",)
STATIC = {"area_km2", "seifa_irsd", "dwellings_census", "dwellings_occupied_census", "employed_persons_census"}
STATIC_SUFFIX = ("_census", "_2017", "_2014_17avg", "_2020", "_avg_annual_change_pct_fy")
JUNE_DATED = {"population", "population_density"}  # ABS ERP at 30 June
SL_STEMS = ("income_support", "jobseeker", "rent_", "median_income", "income_earners", "dw_", "population")
SKIP = ("fiscal_council_name_fy", "fiscal_fiscal_source_fy")  # bookkeeping, not variables


def skip_var(v):
    """lga_year columns left out of the master windows: bookkeeping; the program grant columns (council-year totals
    that would land on any event in the same council-year; FP_reported_* carries them for the Black Summer rows
    only); BCARR GRP levels (two years only; the event-level X16 columns take the latest year before the fire)."""
    return (v in SKIP or (v.startswith("fp_") and not v.startswith("fp_olg_"))
            or v in {"grp_sa4_aud_m_fy", "grp_lga_popshare_proxy_aud_m_fy", "grp_per_capita_sa4_aud_fy"})
FP_STEMS = ("fiscal_", "fp_")


def fire_aggregates(k):
    fires = pd.read_csv(OUT / "fires.csv", low_memory=False, dtype={"region_id": str})
    fires["agrn"] = fires.official_declaration_agrn.fillna("").astype(str).str.split(";")
    fx = fires.explode("agrn")
    fx = fx[fx.agrn != ""]
    rows = {}
    for (agrn, code), g in fx.groupby(["agrn", "region_id"]):
        w = g.region_burn_area_ha.fillna(0).clip(lower=1e-9)
        r = {}
        for col, how, new in FIRE_AGG:
            v = pd.to_numeric(g[col], errors="coerce")
            ok = v.notna()
            if not ok.any():
                r[new] = np.nan
            elif how == "wmean":
                r[new] = float(np.average(v[ok], weights=w[ok]))
            elif how == "sum":
                r[new] = v[ok].sum()
            elif how == "share_sum":
                r[new] = (v[ok] * g.region_share_of_fire[ok]).sum()
            else:
                r[new] = getattr(v[ok], how)()
        for col, new in FIRE_TEXT:
            r[new] = "; ".join(sorted(set(g[col].dropna().astype(str)))) or np.nan
        r["info_fire_event_ids"] = "; ".join(sorted(set(g.event_id.astype(str))))
        rows[(str(agrn), str(code))] = r
    agg = pd.DataFrame.from_dict(rows, orient="index")
    key = list(zip(k.agrn.astype(str), k.region_id.astype(str)))
    missing = [x for x in key if x not in agg.index]
    assert not missing, f"event × council rows with no linked fires: {missing[:5]}"
    return agg.reindex(key).set_axis(k.index)


def time_kind(v):
    if v in STATIC or v.startswith(STATIC_PREFIX) or v.endswith(STATIC_SUFFIX):
        return "static"
    if v.endswith("_fy"):
        return "fy"
    if v.endswith("_june") or v in JUNE_DATED:
        return "june"
    return "cal"


def pillar(v):
    if v.startswith(FP_STEMS):
        return "FP"
    if any(v.startswith(s) for s in SL_STEMS):
        return "SL"
    return "IL"


def _static_value(series, rid, year):
    """Latest value dated at or before `year` for this council, else the earliest one after it."""
    s = series.get(rid)
    if s is None or s.empty:
        return np.nan
    before = s[s.index <= year]
    return before.iloc[-1] if len(before) else s.iloc[0]


def panel_windows(k, ly, start):
    """Every lga_year variable at pre / event / plus1 for each row; returns (frame, {new name: (var, window, kind)})."""
    ly = ly.copy()
    ly["region_id"] = ly.region_id.astype(str)
    assert not ly.duplicated(["region_id", "year"]).any(), "lga_year has duplicate council-years"
    tab = ly.set_index(["region_id", "year"]).drop(columns=["region_name"])
    tab = tab[[v for v in tab.columns if not skip_var(v)]]
    rid = k.region_id.astype(str).to_numpy()
    cal = start.dt.year.to_numpy()
    cal_event = np.where(start.dt.month <= 6, cal, cal + 1)  # calendar year lying mostly after the fire start
    fy = np.where(start.dt.month >= 7, start.dt.year, start.dt.year - 1)
    years = {"cal": {"_pre": cal - 1, "_event": cal_event, "_plus1": cal_event + 1},
             "fy": {"_pre": fy - 1, "_event": fy, "_plus1": fy + 1},
             "june": {"_pre": fy, "_event": fy + 1, "_plus1": fy + 2}}  # 30 June before / ending / after the fire FY
    kinds = {v: time_kind(v) for v in tab.columns}
    out, meta = {}, {}
    static = [v for v in tab.columns if kinds[v] == "static" and v not in k.columns]
    for v in static:
        by = {r: g.droplevel(0).sort_index() for r, g in tab[v].dropna().groupby(level=0)}
        name = ("X_council_" if v.startswith(FP_STEMS) else "X_socio_") + v
        out[name] = [_static_value(by, r, y) for r, y in zip(rid, cal)]
        meta[name] = (v, "one-off value", "static")
    for kind in ("cal", "fy", "june"):
        cols = [v for v in tab.columns if kinds[v] == kind]
        for suf, yrs in years[kind].items():
            vals = tab[cols].reindex(pd.MultiIndex.from_arrays([rid, yrs]))
            for v in cols:
                if suf == "_pre":
                    name = ("X_council_" if v.startswith(FP_STEMS) else "X_socio_") + v + suf
                else:
                    name = f"{pillar(v)}_src_{v}{suf}"
                out[name] = vals[v].to_numpy()
                meta[name] = (v, suf.strip("_"), kind)
    return pd.DataFrame(out, index=k.index), meta


def revenue_change(panel):
    """Bowen's 'fiscal revenue change': council revenue in the fire FY and the FY after vs the FY before (NSW OLG).
    Total revenue includes capital grants (where recovery money arrives); own-source revenue = total × own-source %."""
    out = pd.DataFrame(index=panel.index)
    tot = {w: panel[f"{p}fiscal_total_revenue_including_capital_aud_fy_{w}"] for w, p in
           [("pre", "X_council_"), ("event", "FP_src_"), ("plus1", "FP_src_")]}
    own = {w: tot[w] * panel[f"{p}fiscal_own_source_pct_fy_{w}"] / 100 for w, p in
           [("pre", "X_council_"), ("event", "FP_src_"), ("plus1", "FP_src_")]}
    for w in ("event", "plus1"):
        out[f"FP_total_revenue_change_{w}_pct"] = (tot[w] / tot["pre"] - 1) * 100
        out[f"FP_own_source_revenue_change_{w}_pct"] = (own[w] / own["pre"] - 1) * 100
    return out


def build(kec, ly, decl_start):
    start = pd.to_datetime(kec.first_fire_start).fillna(pd.to_datetime(decl_start))
    assert start.notna().all(), "rows without a fire or declaration start"
    fire = fire_aggregates(kec)
    panel, meta = panel_windows(kec, ly, start)
    base = kec.assign(info_fire_fy=[f"{y}-{str(y + 1)[2:]}" for y in np.where(start.dt.month >= 7, start.dt.year,
                                                                              start.dt.year - 1)])
    panel = pd.concat([panel, revenue_change(panel)], axis=1)
    clash = set(panel.columns) & set(base.columns) | set(fire.columns) & set(base.columns)
    assert not clash, f"duplicate column names: {sorted(clash)[:10]}"
    return pd.concat([base, fire, panel], axis=1), meta
