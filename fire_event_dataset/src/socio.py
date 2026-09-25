"""Council-level socioeconomic, fiscal and disaster-history variables already on disk, joined to fire × LGA rows."""
import re

import duckdb
import numpy as np
import pandas as pd

from src.common import DATA, REPO, AUSSEF_DB, PHASE1


def norm(name):
    s = str(name).lower().replace("(nsw)", "")
    s = re.sub(r"\((a|c|s|m|rc|t)\)", " ", s)
    s = re.sub(r"\b(city|council|shire|regional|municipal|of|the)\b", " ", s)
    return re.sub(r"[^a-z]", "", s)


def fy_start(ts):
    ts = pd.to_datetime(ts)
    return np.where(ts.dt.month >= 7, ts.dt.year, ts.dt.year - 1)


ERP_2025 = DATA / "abs/32180DS0004_2001-25.xlsx"  # ABS Regional population 2024-25, LGA ERP 2001–2025 (2025 LGAs)


def population():
    """LGA ERP at 30 June by (code, year): ABS 2024-25 release first, the older phase-1 series for codes it lacks."""
    old = pd.read_csv(PHASE1 / "data/population_area_year.csv", dtype={"geographic_id": str})
    old = old.set_index(["geographic_id", "year"]).population
    if not ERP_2025.exists():
        return old
    d = pd.read_excel(ERP_2025, "Table 1", header=None)
    years = d.iloc[4, 2:].astype(int).tolist()
    body = d.iloc[6:, :2 + len(years)].dropna(subset=[0])
    body = body[body[0].astype(str).str.fullmatch(r"\d{5}")]
    body.columns = ["code", "name"] + years
    new = body.melt(id_vars=["code", "name"], var_name="year", value_name="population")
    new = new.assign(code=new.code.astype(str), year=new.year.astype(int),
                     population=pd.to_numeric(new.population, errors="coerce")).set_index(["code", "year"]).population
    return new.combine_first(old.rename_axis(["code", "year"]))


def income():
    """Latest release per (LGA code, financial-year start)."""
    i = pd.read_csv(PHASE1 / "data/income_area_year_by_release.csv", dtype={"geographic_id": str})
    rank = {"PIA_2020": 0, "PIA_2022": 1, "PIA_2024": 2, "PIA_2025": 3}
    i["r"] = i.source_id.map(rank)
    i = i.sort_values("r").groupby(["geographic_id", "fy_start"]).last()
    return i[["median_income_aud", "income_earners", "total_income_aud", "mean_income_aud", "source_id"]]


SEIFA_ALIASES = {"dubbo regional": "western plains regional"}  # renamed after the 2016 Census


def seifa():
    s = pd.read_csv(PHASE1 / "data/seifa_baselines.csv", dtype={"geographic_id": str})
    return s.set_index(["geographic_id", "boundary_vintage"]).irsd_score


def seifa_by_name():
    """IRSD by (normalised name, vintage), for councils whose code changed between the 2016 and 2021 vintages."""
    s = pd.read_csv(PHASE1 / "data/seifa_baselines.csv", dtype={"geographic_id": str})
    s["n"] = s.geographic_name.str.replace(r"\s*\(.*\)$", "", regex=True).str.strip().str.lower()
    return s.drop_duplicates(["n", "boundary_vintage"]).set_index(["n", "boundary_vintage"]).irsd_score


def fiscal():
    con = duckdb.connect(str(AUSSEF_DB), read_only=True)
    ext = con.sql("""select council_name, year_start, cash_cover_months, own_source_pct, grants_pct,
                     operating_ratio_pct, debt_service_ratio_pct, debt_service_cover, maintenance_ratio_pct,
                     maintenance_gap_aud, total_revenue_including_capital_aud, total_expenses_aud, road_km,
                     population as council_population from master.fiscal_panel_extended""").df()
    leg = con.sql("""select council as council_name, year_start, cash_cover_months, own_source_pct, grants_pct,
                     operating_ratio_pct, debt_service_cover, maintenance_ratio_pct, maintenance_gap_aud, road_km,
                     population as council_population from master.fiscal_panel_legacy""").df()
    con.close()
    ext["fiscal_source"], leg["fiscal_source"] = "fiscal_panel_extended", "fiscal_panel_legacy"
    ext["key"], leg["key"] = ext.council_name.map(norm), leg.council_name.map(norm)
    both = pd.concat([ext, leg[~leg.set_index(["key", "year_start"]).index.isin(ext.set_index(["key", "year_start"]).index)]])
    both = both.groupby(["key", "year_start"]).first()
    olg = olg_fiscal()
    if olg is None:
        return both
    # OLG Time Series Data take priority; AUSSEF panels fill council-years OLG does not publish
    out = olg.combine_first(both)
    out.loc[olg.index, "fiscal_source"] = "olg_time_series"
    return out


OLG_WIDE = DATA / "olg/olg_wide.parquet"
OLG_ALIASES = {"nambucca": "nambuccavalley"}  # OLG used the old name to 2017-18


def olg_fiscal():
    """NSW OLG Time Series Data (src/olg.py) mapped to the fiscal-panel column names, by (norm name, FY start)."""
    if not OLG_WIDE.exists():
        return None
    o = pd.read_parquet(OLG_WIDE)
    o["key"] = o.council_name.map(norm).replace(OLG_ALIASES)
    o = o.rename(columns={"fy_start": "year_start", "cash_expense_cover_ratio_months": "cash_cover_months",
                          "own_source_revenue_pct": "own_source_pct",
                          "operating_performance_ratio_pct": "operating_ratio_pct",
                          "asset_maintenance_ratio_pct": "maintenance_ratio_pct",
                          "total_revenue_continuing_ops_aud": "total_revenue_including_capital_aud",
                          "population": "council_population"})
    keep = ["cash_cover_months", "own_source_pct", "operating_ratio_pct", "debt_service_ratio_pct",
            "debt_service_cover_ratio", "maintenance_ratio_pct", "unrestricted_current_ratio",
            "building_infrastructure_renewals_ratio_pct", "infrastructure_backlog_ratio_pct",
            "total_revenue_including_capital_aud", "council_population", "total_expenses_continuing_ops_aud",
            "net_operating_result_before_capital_aud", "exp_governance_admin_aud",
            "exp_public_order_health_water_sewer_aud", "exp_environment_aud", "exp_community_services_housing_aud",
            "exp_recreation_culture_aud", "exp_roads_bridges_footpaths_aud", "exp_other_services_aud"]
    o = o.groupby(["key", "year_start"])[[c for c in keep if c in o.columns]].first()
    # spending mix (share of total expenses): everyday services vs roads & bridges (where reconstruction goes)
    tot = o.total_expenses_continuing_ops_aud
    o["service_share_pct"] = 100 * (o.exp_community_services_housing_aud + o.exp_recreation_culture_aud
                                    + o.exp_environment_aud) / tot
    o["roads_share_pct"] = 100 * o.exp_roads_bridges_footpaths_aud / tot
    # a debt service COVER ratio of 0 means no debt (the ratio is undefined), not zero cover
    o.loc[o.debt_service_cover_ratio == 0, "debt_service_cover_ratio"] = np.nan
    return o


DECL_OPEN_DAYS, DECL_SINGLE_DAYS = 180, 30  # 'X onwards' vs a single-date declaration name


def disasters():
    """Declared disasters per council key with start dates and hazard."""
    con = duckdb.connect(str(AUSSEF_DB), read_only=True)
    d = con.sql("""select l.council_id, c.council_name, d.agrn, d.event_name, d.hazard,
                   cast(d.event_start_lower as date) start_lo, cast(d.event_start_upper as date) start_hi
                   from master.disaster_council_links l join master.disasters d using (disaster_id)
                   join master.councils c using (council_id)""").df()
    con.close()
    d["key"] = d.council_name.map(norm)
    parsed = d.event_name.map(name_dates)
    d["name_start"], d["name_end"] = parsed.str[0], parsed.str[1]
    d["start"] = pd.to_datetime(d.start_lo).fillna(pd.to_datetime(d.start_hi)).fillna(d.name_start)
    d["end"] = d.name_end
    d["decl_source"] = "aussef_disasters"
    e2 = e2_declarations()
    if e2 is not None:
        d = pd.concat([d, e2], ignore_index=True)
    return d


E2_DIR = REPO / "Experiment 2/data/disaster_exposure_v2"


def e2_declarations():
    """Declarations July 2012 – June 2017 from AUSSEF Experiment 2 (NSW Rural Assistance Authority annual reports),
    which the AUSSEF disasters table lacks. They carry no AGRN, so the ID is 'RAA-<record_id>'. Councils are given
    under pre-2016 names and are mapped to their 2016 successors (e.g. Palerang -> Queanbeyan-Palerang)."""
    led, lnk = E2_DIR / "declaration_event_ledger.csv", E2_DIR / "declaration_council_links.csv"
    if not (led.exists() and lnk.exists()):
        return None
    from src.olg import PREDECESSORS
    succ = {norm(k): norm(v) for k, v in PREDECESSORS.items()}
    L = pd.read_csv(led)
    L = L[L.include_in_historical_panel.astype(bool)]
    K = pd.read_csv(lnk)
    K = K[K.include_in_historical_panel.astype(bool)]
    k = K.council_key.fillna(K.council_name_source.map(norm)).map(norm)
    K["key"] = k.map(lambda x: succ.get(x, x))
    m = K[["record_id", "key", "council_name_source"]].merge(L, on="record_id", how="inner")
    lo = pd.to_datetime(m.onset_date_lower_bound, errors="coerce")
    hi = pd.to_datetime(m.onset_date_upper_bound, errors="coerce")
    end = pd.to_datetime(m.reported_end_date, errors="coerce")
    out = pd.DataFrame({
        "council_name": m.council_name_source, "key": m.key, "agrn": "RAA-" + m.record_id,
        "event_name": m.reported_hazard.astype(str) + " (NSW RAA annual report, onset " + lo.dt.date.astype(str) + ")",
        "hazard": m.reported_hazard, "start": lo, "end": end.fillna(hi.where(hi > lo)),
        "decl_source": "e2_raa_annual_reports"})
    return out.drop_duplicates(["key", "agrn"])


_MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                        "september", "october", "november", "december"], 1)}
_TOKEN = re.compile(r"\b(\d{1,2})\b(?:\s+(january|february|march|april|may|june|july|august|september|october|"
                    r"november|december))?(?:\s+(\d{4}))?", re.I)


def name_dates(name):
    """(start, end) from a declaration name such as '8 – 18 December 2023', 'from 6 to 9 October 2025' or
    '31 August 2019 onwards'; missing month/year are taken from the next date in the name. End is NaT if open-ended."""
    toks = [[int(dd), (m or "").lower(), int(y) if y else None] for dd, m, y in _TOKEN.findall(str(name).replace("\xa0", " "))]
    for i in range(len(toks) - 2, -1, -1):  # carry month and year backwards
        toks[i][1] = toks[i][1] or toks[i + 1][1]
        toks[i][2] = toks[i][2] or toks[i + 1][2]
    dates = []
    for dd, m, y in toks:
        try:
            dates.append(pd.Timestamp(year=y, month=_MONTHS[m], day=dd))
        except (KeyError, TypeError, ValueError):
            pass
    if not dates:
        return (pd.NaT, pd.NaT)
    return (dates[0], dates[-1] if len(dates) > 1 else pd.NaT)


def attach(rows, ev):
    """rows: fire × LGA DataFrame with event_id, LGA_CODE21, LGA_NAME21; ev: fire table."""
    r = rows.merge(ev[["event_id", "start", "end"]], on="event_id", how="left")
    r["fy"] = fy_start(r.start)
    r["key"] = r.LGA_NAME21.map(norm)
    code = r.LGA_CODE21.astype(str)

    pop = population()
    r["population_prev_year"] = [pop.get((c, y - 1), np.nan) for c, y in zip(code, r.start.dt.year)]
    r["X15_pop_density"] = r.population_prev_year / r.AREASQKM21

    inc = income()
    for lag, lab in ((-1, "pre"), (0, "event"), (1, "plus1")):
        vals = [inc.loc[(c, f + lag)] if (c, f + lag) in inc.index else None for c, f in zip(code, r.fy)]
        for col in ("median_income_aud", "total_income_aud", "income_earners"):
            r[f"{col}_{lab}"] = [v[col] if v is not None else np.nan for v in vals]
    r["SL_income_drop_raw"] = (r.median_income_aud_event - r.median_income_aud_pre) / r.median_income_aud_pre * 100
    r["IL_total_income_change_pct_proxy"] = (r.total_income_aud_event - r.total_income_aud_pre) / r.total_income_aud_pre * 100
    r["X16_regional_GDP_proxy_total_income_aud"] = r.total_income_aud_pre

    s = seifa()
    sn = seifa_by_name()
    x17 = []
    for c, nm, y in zip(code, r.LGA_NAME21, r.start.dt.year):
        v = 2016 if y <= 2020 else 2021
        n = str(nm).replace(" (NSW)", "").strip().lower()
        x17.append(s.get((c, v), sn.get((n, v), sn.get((SEIFA_ALIASES.get(n, n), v), np.nan))))
    r["X17_SEIFA"] = x17

    f = fiscal()
    for lag, lab in ((-1, "pre"), (0, "event"), (1, "plus1")):
        idx = list(zip(r.key, r.fy + lag))
        sub = f.reindex(idx)
        sub.index = r.index
        for col in f.columns:
            r[f"fiscal_{col}_{lab}"] = sub[col].values
    r["X19_cash_reserve"] = r.fiscal_cash_cover_months_pre
    r["X20_own_source_revenue_ratio"] = r.fiscal_own_source_pct_pre
    r["X21_debt_burden"] = r.fiscal_debt_service_ratio_pct_pre
    r["FP_debt_ratio_change_raw"] = r.fiscal_debt_service_ratio_pct_event - r.fiscal_debt_service_ratio_pct_pre
    r["FP_operating_ratio_change_proxy"] = r.fiscal_operating_ratio_pct_event - r.fiscal_operating_ratio_pct_pre
    r["FP_cash_cover_change_proxy"] = r.fiscal_cash_cover_months_event - r.fiscal_cash_cover_months_pre
    # budget crowd-out: fall in the share of spending on everyday services (community, recreation, environment)
    # from the FY before the fire to the FY after (positive = services squeezed); roads share rises with rebuilding
    if "fiscal_service_share_pct_pre" in r:
        r["FP_budget_crowd_out_raw"] = r.fiscal_service_share_pct_pre - r.fiscal_service_share_pct_plus1
        r["FP_roads_share_change_plus1_pp"] = r.fiscal_roads_share_pct_plus1 - r.fiscal_roads_share_pct_pre

    d = disasters()
    by = {k: g for k, g in d.groupby("key")}
    hist, hist_bf, agrn, dname = [], [], [], []
    for k, s0, e0 in zip(r.key, r.start, r.end):
        g = by.get(k)
        if g is None:
            hist.append(np.nan); hist_bf.append(np.nan); agrn.append(""); dname.append(""); continue
        prior = g[(g.start < s0) & (g.start >= s0 - pd.DateOffset(years=10))]
        hist.append(int(prior.agrn.nunique()))
        hist_bf.append(int(prior[prior.hazard.astype(str).str.contains("fire", case=False)].agrn.nunique()))
        e1 = e0 if pd.notna(e0) else s0 + pd.Timedelta(days=30)
        # fire declaration for this council whose period overlaps the fire: starts no later than the fire ends and
        # ends no earlier than a week before it starts; open-ended ("onwards") declarations cover 180 days
        onwards = g.event_name.astype(str).str.contains("onward|commenc", case=False)
        dend = g.end.fillna(g.start + pd.to_timedelta(np.where(onwards, DECL_OPEN_DAYS, DECL_SINGLE_DAYS), unit="D"))
        m = g[(g.hazard.astype(str).str.contains("fire", case=False)) & (g.start <= e1)
              & (dend >= s0 - pd.Timedelta(days=7))]
        agrn.append(";".join(sorted({str(x) for x in m.agrn.dropna()})))
        dname.append(" | ".join(sorted({str(x) for x in m.event_name.dropna()})))
    r["X22_historical_disaster_count"] = hist
    r["historical_bushfire_declarations_10y"] = hist_bf
    r["official_declaration_agrn"] = agrn
    r["official_declaration_name"] = dname
    return r.drop(columns=["start", "end"])
