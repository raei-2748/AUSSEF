"""Join the 2026-09-27 enrichments onto the lga_year panel and the declared event × council rows.

Inputs (build them first; each module documents its own sources):
  data/enrich/il_sector.parquet (+ _all_releases)  src/il_sector.py    CABEE by industry, business entries/exits, Jobs
                                                                        in Australia, insolvencies, PIA, TRA 2017 tourism
  data/enrich/grp_insurance.parquet                src/grp_insurance.py BCARR SA4 GRP, REDS 2020 GRP, Census tenure
  data/enrich/fp_funding.parquet                   src/fp_funding.py    bushfire recovery grants by council, OLG $
Used by src/xy_format.py; nothing here is modelled.

Panel year convention (same as lga_year): `_fy` columns sit on the year the financial year STARTS (2019 = 2019-20);
`_june` columns on the year of that 30 June; `_census` on the Census year.
"""
import json
import re

import numpy as np
import pandas as pd

from src.common import DATA

ENRICH = DATA / "enrich"

FP_SHORT = {  # program -> short column stem
    "Audit Office of NSW, Report on Local Government 2020 (council examples)": "audit_lg2020",
    "BCRRF Stream 1 (Bushfire Community Recovery and Resilience Fund)": "bcrrf1",
    "BLER Fund (Fast-Tracked + SDG + Open round), projects located in LGA": "bler",
    "Black Summer Bushfire Recovery (BSBR) Grants": "bsbr",
    "NBRA Local Government Area Grants Package (initial $1m + $17m distribution)": "nbra_lga_package",
    "NSW EPA Bushfire Recovery Program for Council Landfills (Phase 2)": "epa_landfills",
    "NSW EPA Bushfire-generated green waste clean-up (Stream B)": "epa_green_waste",
    "NSW OLG Time Series Data": "olg",
}
AFFECTED_COLS = ["pop_in_fire", "pop_within_1km", "pop_within_5km", "pop_within_5km_all_councils", "dwellings_in_fire",
                 "dwellings_within_1km", "dwellings_within_5km"]
BLACK_SUMMER_AGRN = "871"

# ---------------------------------------------------------------- quarterly activity (src/econ_quarterly.py)
ECON_BASE = {"ntl_mean_exfire": ("mean VIIRS night-time light radiance of the council, pixels inside fires burning that "
                                 "month removed", "nW/cm²/sr", "council", "IL"),
             "ntl_mean": ("mean VIIRS night-time light radiance of the council (a proxy of local economic activity; "
                          "flames themselves are bright, so q0 and q+1 are contaminated)", "nW/cm²/sr", "council", "IL"),
             "payroll": ("ABS payroll jobs index (14 Mar 2020 = 100), SA3 values weighted by the council's residents; "
                         "weeks ending 4 Jan 2020 - 13 May 2023 only", "index", "council", "IL"),
             "nsw_sfd_sa_aud_m": ("NSW State Final Demand, chain volume, seasonally adjusted (whole state, not the "
                                  "council)", "AUD m", "state", "IL"),
             "nsw_sfd": ("NSW State Final Demand (whole state, not the council)", "%", "state", "IL")}
ECON_SRC = {"ntl": ("EOG VIIRS DNB monthly composites (stray-light excluded) via World Bank 'Light Every Night' "
                    "open data (s3://globalnightlight), clipped to ABS LGA 2021; src/econ_quarterly.py",
                    "https://registry.opendata.aws/wb-light-every-night/"),
            "payroll": ("ABS Weekly Payroll Jobs, Table 5 (SA4/SA3), release of 8 Jun 2023; src/econ_quarterly.py",
                        "https://www.abs.gov.au/statistics/labour/jobs/weekly-payroll-jobs"),
            "nsw_sfd": ("ABS Australian National Accounts 5206.0, Table 25 (NSW State Final Demand); "
                        "src/econ_quarterly.py", "https://www.abs.gov.au/statistics/economy/national-accounts/"
                                                 "australian-national-accounts-national-income-expenditure-and-product")}
WIN = {"q-4": "4 quarters before the fire-start quarter", "q-1": "the quarter before the fire-start quarter",
       "q+0": "the fire-start quarter", "q+1": "the quarter after the fire-start quarter",
       "q+2": "2 quarters after the fire-start quarter", "q+4": "the same quarter a year after the fire-start quarter"}


def econ_doc(col):
    """For an econ_quarterly column: (group, new name, meaning, unit, source, url), or None."""
    if col in ("fire_start_quarter", "ntl_window_product_change"):
        m = {"fire_start_quarter": "Calendar quarter of the (first) fire start = q0 of the quarterly windows",
             "ntl_window_product_change": "True if the q-4..q+4 night-lights window spans two product versions "
                                          "(levels can shift)"}[col]
        src = ECON_SRC["ntl"] if "ntl" in col else ("computed from the fire start date (GA)", "")
        return ("info", "info_" + col, m, "text", *src)
    base = next((b for b in ECON_BASE if col.startswith(b + "_")), None)
    if base is None:
        return None
    rest = col[len(base) + 1:]
    what, unit, geo, pillar = ECON_BASE[base]
    if geo == "state":  # one value for all of NSW in a quarter: economic context, not a council impact
        pillar = "socio"
    flame = base.startswith("ntl") and ("q+0" in rest or "q+1" in rest)  # flames/glow brighten these quarters
    src = ECON_SRC["ntl" if base.startswith("ntl") else "payroll" if base == "payroll" else "nsw_sfd"]
    safe = col.replace("+", "p").replace("-", "m")
    m = re.fullmatch(r"q([+-]\d)", rest)
    if m:
        w = "q" + m.group(1)
        pre = m.group(1).startswith("-")
        if flame:
            return ("info", f"info_{safe}", f"{what}, {WIN[w]}. Contaminated by light from the fires themselves: not "
                    "a loss measure", unit, *src)
        group = "socio" if (pre or pillar == "socio") else pillar
        name = f"X_socio_{safe}" if group == "socio" else f"{pillar}_src_{safe}"
        return (group, name, f"{what}, {WIN[w]}", unit, *src)
    if rest == "yoy_pct_q0":
        return (pillar, f"X_socio_{safe}" if pillar == "socio" else f"{pillar}_{safe}", f"{what}: % change in the fire-start quarter vs a year earlier", "%", *src)
    text = {"chg_pct_q+1_vs_q-1": "% change, quarter after vs quarter before the fire-start quarter",
            "yoy_pct_q+1": "% change, quarter after the fire vs the same quarter a year earlier",
            "yoy_pct_q+4_vs_q0": "% change, the same quarter a year after vs the fire-start quarter",
            "yoy_pct_q+1_ctrl_median": "median of the same year-on-year change in NSW councils with no fire >= 100 ha "
                                       "starting in q-4..q+1 (comparison)",
            "yoy_pct_q+1_excess": "year-on-year change (q+1) minus the comparison-council median"}.get(rest)
    if text is None:
        return None
    unit = "pp" if rest.endswith("excess") else "%"
    if rest.endswith("ctrl_median"):
        return ("info", f"info_{safe}", f"{what}: {text}. A benchmark, not this council's value", unit, *src)
    if flame or (base.startswith("ntl") and "q0" in rest):
        return ("info", f"info_{safe}", f"{what}: {text}. Uses a quarter contaminated by light from the fires "
                "themselves (night lights rise, not fall): not a loss measure", unit, *src)
    if pillar == "socio":
        return ("socio", f"X_socio_{safe}", f"{what}: {text}", unit, *src)
    return (pillar, f"{pillar}_{safe}", f"{what}: {text}", unit, *src)  # the 2019-20 recovery programs attach to this declaration only (880 overlaps it)


def _fy_start(fy):
    """'FY2019-20' or '2019-20' -> 2019."""
    return int(str(fy).replace("FY", "")[:4])


def _event_fy(ts):
    return np.where(ts.dt.month >= 7, ts.dt.year, ts.dt.year - 1)


# ---------------------------------------------------------------- loaders with the 2026-09-27 audit fixes
def load_il(name="il_sector.parquet"):
    """il_sector without its parse artifact (cabee_businesses_nan_nan_*: one unlabelled June-2016 row) and without
    TRA's 'Gundagai (A)' profile, which covers only the former Gundagai shire, not Cootamundra-Gundagai Regional."""
    il = pd.read_parquet(ENRICH / name)
    il = il[~il.variable.str.contains("nan_nan")]
    return il[~(il.variable.str.startswith("tra2017_") & il.source_file.astype(str).str.contains("Gundagai"))]


def load_fp():
    """fp_funding with only bushfire amounts from the Audit Office report (its flood and 'bushfire and flood' rows
    are dropped: e.g. Bega's $8.0m flood damage, Clarence Valley's $7.0m flood grants) and no multi-council rows."""
    f = pd.read_parquet(ENRICH / "fp_funding.parquet")
    audit = f.program.str.startswith("Audit Office")
    f = f[~audit | (f.hazard == "bushfire")]
    return f[~f.measure.str.startswith("multi_lga")]


# ---------------------------------------------------------------- council × year panel
def il_panel():
    il = load_il()
    il = il[il.value.notna()].copy()
    p = il.period.astype(str)
    june = p.str.match(r"^\d{4}-06-30$")
    fy = p.str.startswith("FY")
    tra = il.variable.str.startswith("tra2017_")
    il["year"] = np.select([june, fy, tra], [p.str[:4].where(june, "0").astype(int),
                                             p.where(fy, "FY0000").map(_fy_start), 2017], -1)
    il["col"] = il.variable + np.select([june, fy, tra & p.str.contains("average")], ["_june", "_fy", "_2014_17avg"],
                                        "_2017")
    il = il[il.year > 0]
    return il.pivot_table(index=["region_id", "year"], columns="col", values="value", aggfunc="first")


def grp_panel():
    g = pd.read_parquet(ENRICH / "grp_insurance.parquet")
    g["region_id"] = g.region_id.astype(str)
    fycols = ["grp_sa4_aud_m", "grp_lga_popshare_proxy_aud_m", "grp_per_capita_sa4_aud",
              "grp_sa4_nominal_avg_annual_change_pct", "grp_sa4_real_avg_annual_change_pct"]
    census = ["X23_insurance_proxy_building_cover_required_share", "dw_owned_mortgage_share",
              "dw_owned_outright_share", "dw_rented_share", "dw_flat_apartment_share"]
    a = g[g.fy_grp.fillna("").str.match(r"^\d{4}-\d{2}$")].assign(year=lambda d: d.fy_grp.map(_fy_start))
    a = a.set_index(["region_id", "year"])[fycols].add_suffix("_fy")
    b = g[g.year.isin([2016, 2021])].set_index(["region_id", "year"])[census].dropna(how="all")
    b.columns = [c.replace("X23_insurance_proxy_", "insurance_proxy_") + "_census" for c in b.columns]
    c = g[g.year == 2020].set_index(["region_id", "year"])[["grp_fer_reds_aud_m"]].add_suffix("_2020").dropna()
    return pd.concat([a, b, c], axis=1)


def fp_panel():
    f = load_fp()
    f = f[f.fy.notna() & f.region_id.notna() & f.amount_aud.notna()].copy()
    f["year"] = f.fy.map(_fy_start)
    f["col"] = "fp_" + f.program.map(FP_SHORT) + "_" + f.measure.str.replace("_aud$", "", regex=True) + "_aud_fy"
    return f.pivot_table(index=["region_id", "year"], columns="col", values="amount_aud", aggfunc="sum")


def extend_lga_year(ly):
    """lga_year plus every new council × year column (outer join keeps council-years new sources add)."""
    ly = ly.copy()
    ly["region_id"] = ly.region_id.astype(str)
    extra = pd.concat([il_panel(), grp_panel(), fp_panel()], axis=1).reset_index()
    extra["region_id"] = extra.region_id.astype(str)
    extra = extra[extra.region_id.isin(set(ly.region_id))]
    out = ly.merge(extra, on=["region_id", "year"], how="left")
    return out


def panel_docs():
    """Meaning per new lga_year column (from each module's doc.json), keyed by column-name stem."""
    docs = {}
    for name in ["il_sector", "grp_insurance", "fp_funding"]:
        d = json.load(open(ENRICH / f"{name}.doc.json"))
        for k, v in d.items():
            docs[k] = v[0] if isinstance(v, list) else v
    return docs


# ---------------------------------------------------------------- event × council attachments
def _same_release_change(al, var, y0, y1, ids):
    """% change var(y1) vs var(y0) per region, both from the newest release holding both years (as business.py)."""
    s = al[al.variable == var]
    t = s.set_index(["release", "region_id", "yr"]).value
    rel = s.groupby("release").yr.agg(["min", "max"])
    out = []
    for r, a, b in zip(ids, y0, y1):
        ok = [rl for rl in rel.index if (rl, r, a) in t.index and (rl, r, b) in t.index]
        if not ok:
            out.append(np.nan)
            continue
        rl = max(ok, key=lambda x: rel.loc[x, "max"])
        v0, v1 = t[(rl, r, a)], t[(rl, r, b)]
        out.append((v1 / v0 - 1) * 100 if v0 else np.nan)
    return out


def event_extras(k, decl_start):
    """New X and Y columns for the event × council rows, keyed to each event's financial year."""
    k = k.copy()
    rid = k.region_id.astype(str)
    start = pd.to_datetime(k.first_fire_start).fillna(pd.to_datetime(decl_start))
    fy = pd.Series(_event_fy(start), index=k.index)  # FY start year
    out = pd.DataFrame(index=k.index)

    # X: size of the economy before the fire (latest BCARR year at or before the fire FY), insurance proxy, tourism
    g = grp_panel()
    for col, new in [("grp_lga_popshare_proxy_aud_m_fy", "X16_regional_GDP_sa4_popshare_proxy_aud_m"),
                     ("grp_per_capita_sa4_aud_fy", "X16_grp_per_capita_sa4_aud")]:
        ser = g[col].dropna()
        out[new] = [next((ser[(r, y)] for y in (2020, 2015) if y <= f and (r, y) in ser.index), np.nan)
                    for r, f in zip(rid, fy)]
    out["X16_grp_base_fy"] = [next((f"{y}-{str(y + 1)[2:]}" for y in (2020, 2015) if y <= f), None) for f in fy]
    ins = g["insurance_proxy_building_cover_required_share_census"].dropna()
    vint = np.where(start.dt.year <= 2020, 2016, 2021)
    out["X23_insurance_proxy_building_cover_required_share"] = [ins.get((r, v), np.nan) for r, v in zip(rid, vint)]
    reds = g["grp_fer_reds_aud_m_2020"].dropna()
    out["X_socio_grp_reds_region_2020_aud_m"] = [reds.get((r, 2020), np.nan) for r in rid]

    il = load_il()
    june = il[il.period.astype(str).str.match(r"^\d{4}-06-30$")]
    june = june.assign(yr=june.period.astype(str).str[:4].astype(int)).set_index(["variable", "region_id", "yr"]).value
    a0 = june["cabee_businesses_H_accommodation_and_food_services_total"]
    b0 = june["cabee_businesses_all_total"]
    out["X_socio_accommodation_food_business_share_pre"] = [
        a0.get((r, f), np.nan) / b0.get((r, f), np.nan) if b0.get((r, f)) else np.nan for r, f in zip(rid, fy)]

    # IL: sector business counts June before the fire FY -> June at its end (same release), entries/exits, jobs
    al = load_il("il_sector_all_releases.parquet")
    al = al[al.value.notna()].copy()
    per = al.period.astype(str)
    al["yr"] = np.where(per.str.match(r"^\d{4}-06-30$"), per.str[:4], "0").astype(int)
    fym = per.str.startswith("FY")
    al.loc[fym, "yr"] = per[fym].map(_fy_start)
    y_june_before, y_june_end = fy, fy + 1  # FY starting July Y: June Y -> June Y+1
    for var, new in [("cabee_businesses_H_accommodation_and_food_services_total",
                      "IL_accommodation_food_business_change_pct"),
                     ("cabee_businesses_G_retail_trade_total", "IL_retail_business_change_pct"),
                     ("cabee_businesses_R_arts_and_recreation_services_total", "IL_arts_recreation_business_change_pct"),
                     ("cabee_businesses_A_agriculture_forestry_and_fishing_total",
                      "IL_agriculture_business_change_pct")]:
        out[new] = _same_release_change(al, var, y_june_before, y_june_end, rid)
    for var, new in [("jia_jobs_total", "IL_jobs_change_pct"),
                     ("jia_employee_jobs_H_accommodation_and_food_services", "IL_accommodation_food_jobs_change_pct"),
                     ("pia_own_business_income_total", "IL_own_business_income_change_pct"),
                     ("business_exits_total", "IL_business_exits_change_pct")]:
        out[new] = _same_release_change(al, var, fy - 1, fy, rid)  # fire FY vs the FY before
    cur = il.copy()
    cur = cur[cur.period.astype(str).str.startswith("FY")]
    cur["yr"] = cur.period.map(_fy_start)
    cur = cur.set_index(["variable", "region_id", "yr"]).value
    for var, new in [("business_exits_total", "IL_src_business_exits_event_fy"),
                     ("business_entries_total", "IL_src_business_entries_event_fy"),
                     ("insolvency_debtors_business_related", "IL_src_insolvency_business_debtors_event_fy")]:
        out[new] = [cur.get((var, r, f), np.nan) for r, f in zip(rid, fy)]

    # FP: 2019-20 bushfire recovery money by council (Black Summer declaration only) and Audit Office figures
    f = load_fp()
    bs = f[(f.program != "NSW OLG Time Series Data") & f.region_id.notna() & f.amount_aud.notna()]
    piv = bs.pivot_table(index="region_id", columns=[bs.program.map(FP_SHORT), "measure"], values="amount_aud",
                         aggfunc="sum")
    is_bs = k.agrn.astype(str) == BLACK_SUMMER_AGRN
    for (prog, meas) in piv.columns:
        name = f"FP_reported_{prog}_{meas.replace('_aud', '')}_aud"
        out[name] = np.where(is_bs, rid.map(piv[(prog, meas)]), np.nan)
    grants = [c for c in out.columns if c.startswith("FP_reported_") and "audit_lg2020" not in c]
    out["FP_reported_black_summer_recovery_grants_total_aud"] = out[grants].sum(axis=1, min_count=1)
    # X: people and dwellings exposed (Bowen's X2), declared event × council, from src/affected_pop.py
    ap = pd.read_parquet(ENRICH / "affected_pop_event_council.parquet")
    ap = ap.assign(agrn=ap.agrn.astype(str), region_id=ap.region_id.astype(str)).set_index(["agrn", "region_id"])
    key = pd.MultiIndex.from_arrays([k.agrn.astype(str), rid])
    for c in AFFECTED_COLS:
        out[f"X_socio_{c}"] = ap[c].reindex(key).to_numpy()
    out["info_pop_census_year"] = ap["census_year"].reindex(key).to_numpy()
    # who died (data/key_events/death_types.csv, one line per row with a sourced death; basis quoted there)
    dt = pd.read_csv(DATA / "key_events/death_types.csv", dtype={"agrn": str})
    dt = dt.set_index([dt.agrn, dt.region_name])
    dkey = pd.MultiIndex.from_arrays([k.agrn.astype(str), k.region_name])
    out["SL_deaths_type"] = dt["type"].reindex(dkey).to_numpy()
    out["SL_deaths_responders"] = dt["responders"].reindex(dkey).to_numpy()
    out["SL_deaths_type_basis"] = dt["basis"].reindex(dkey).to_numpy()
    # quarterly activity around the fire-start quarter (src/econ_quarterly.py): night lights, payroll, NSW SFD
    eq = pd.read_parquet(ENRICH / "econ_quarterly_events.parquet")
    eq = eq.assign(agrn=eq.agrn.astype(str), region_id=eq.region_id.astype(str)).set_index(["agrn", "region_id"])
    for c in eq.columns:
        d = econ_doc(c)
        if d:
            out[d[1]] = eq[c].reindex(key).to_numpy()
    return pd.concat([k, out], axis=1)


_AP = json.load(open(ENRICH / "affected_pop_event_council.doc.json"))
EVENT_DOCS = {
    **{f"X_socio_{c}": (_AP[c][0] + ". " + _AP[c][3], _AP[c][1], _AP[c][2]) for c in AFFECTED_COLS},
    "info_pop_census_year": ("Census year of the X_socio_pop_* / dwellings_* counts (2016 for fires to 2020, 2021 "
                             "after)", "year", "ABS Census"),
    "X16_regional_GDP_sa4_popshare_proxy_aud_m": ("Council GRP proxy: SA4 GRP × council share of SA4 residents, latest "
                                                  "BCARR year (2015-16 or 2020-21) at or before the fire FY",
                                                  "AUD m", "BCARR Experimental GRP (2025) + ABS mesh blocks"),
    "X16_grp_per_capita_sa4_aud": ("GRP per resident of the council's main SA4, same year as above", "AUD",
                                   "BCARR Experimental GRP (2025)"),
    "X16_grp_base_fy": ("Financial year of the two X16 GRP columns", "", "BCARR"),
    "X23_insurance_proxy_building_cover_required_share": (
        "Proxy, not measured coverage: share of occupied dwellings mortgaged or flats (building cover normally "
        "required). Census 2016 for fires <= 2020, 2021 after", "share", "ABS Census G33 (2016) / G37 (2021)"),
    "X_socio_grp_reds_region_2020_aud_m": ("GRP of the council's REDS functional economic region, 2020 (whole region "
                                           "unless it has one council)", "AUD m", "NSW REDS 2023 updates (REMPLAN)"),
    "X_socio_accommodation_food_business_share_pre": ("Accommodation & food share of businesses, June before the fire "
                                                      "FY", "share", "ABS CABEE"),
    "IL_accommodation_food_business_change_pct": ("% change in accommodation & food businesses, June before the fire "
                                                  "FY -> June at its end (same ABS release)", "%", "ABS CABEE"),
    "IL_retail_business_change_pct": ("As above, retail trade", "%", "ABS CABEE"),
    "IL_arts_recreation_business_change_pct": ("As above, arts & recreation", "%", "ABS CABEE"),
    "IL_agriculture_business_change_pct": ("As above, agriculture, forestry & fishing", "%", "ABS CABEE"),
    "IL_jobs_change_pct": ("% change in jobs, fire FY vs FY before (same release)", "%",
                           "ABS Jobs in Australia (Data by Region)"),
    "IL_accommodation_food_jobs_change_pct": ("As above, accommodation & food employee jobs", "%",
                                              "ABS Jobs in Australia (Data by Region)"),
    "IL_own_business_income_change_pct": ("% change in total own unincorporated business income, fire FY vs FY "
                                          "before", "%", "ABS Personal Income in Australia (Data by Region)"),
    "IL_business_exits_change_pct": ("% change in business exits, fire FY vs FY before", "%",
                                     "ABS CABEE (Data by Region)"),
    "IL_src_business_exits_event_fy": ("Business exits in the fire FY", "businesses", "ABS CABEE (Data by Region)"),
    "IL_src_business_entries_event_fy": ("Business entries in the fire FY", "businesses",
                                         "ABS CABEE (Data by Region)"),
    "IL_src_insolvency_business_debtors_event_fy": ("Business-related personal insolvency debtors in the fire FY",
                                                    "debtors", "AFSA (Data by Region)"),
    "FP_reported_black_summer_recovery_grants_total_aud": (
        "Sum of the 2019-20 bushfire recovery grant columns for this council (AGRN 871 rows only). Programs can overlap "
        "(e.g. 'DRFA' in Audit Office = NBRA package); BLER / BSBR are project money located in the council, not "
        "council revenue", "AUD", "see FP_reported_* columns"),
}
