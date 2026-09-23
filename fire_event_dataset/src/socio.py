"""Council-level socioeconomic, fiscal and disaster-history variables already on disk, joined to fire × LGA rows."""
import re

import duckdb
import numpy as np
import pandas as pd

from src.common import DATA, AUSSEF_DB, PHASE1


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


def seifa():
    s = pd.read_csv(PHASE1 / "data/seifa_baselines.csv", dtype={"geographic_id": str})
    return s.set_index(["geographic_id", "boundary_vintage"]).irsd_score


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
    return both.groupby(["key", "year_start"]).first()


def disasters():
    """Declared disasters per council key with start dates and hazard."""
    con = duckdb.connect(str(AUSSEF_DB), read_only=True)
    d = con.sql("""select l.council_id, c.council_name, d.agrn, d.event_name, d.hazard,
                   cast(d.event_start_lower as date) start_lo, cast(d.event_start_upper as date) start_hi
                   from master.disaster_council_links l join master.disasters d using (disaster_id)
                   join master.councils c using (council_id)""").df()
    con.close()
    d["key"] = d.council_name.map(norm)
    d["start"] = pd.to_datetime(d.start_lo).fillna(pd.to_datetime(d.start_hi))
    return d


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
    r["X17_SEIFA"] = [s.get((c, 2016 if y <= 2020 else 2021), np.nan) for c, y in zip(code, r.start.dt.year)]

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
        m = g[(g.hazard.astype(str).str.contains("fire", case=False)) & (g.start >= s0 - pd.Timedelta(days=30)) & (g.start <= e1)]
        agrn.append(";".join(sorted({str(x) for x in m.agrn.dropna()})))
        dname.append(" | ".join(sorted({str(x) for x in m.event_name.dropna()})))
    r["X22_historical_disaster_count"] = hist
    r["historical_bushfire_declarations_10y"] = hist_bf
    r["official_declaration_agrn"] = agrn
    r["official_declaration_name"] = dname
    return r.drop(columns=["start", "end"])
