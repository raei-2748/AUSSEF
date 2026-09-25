"""Key-events dataset: declared NSW bushfire disasters since 2015 (the mentor's "key information" view).

Workbook out/nsw_key_bushfire_events.xlsx:
- events         one row per declaration: name, dates, councils, summary, headline facts (from news/official reports)
- event_council  one row per declaration × council: fire features summed/maxed over the declared event's fires in that
                 council (from out/fires.csv), council context (X15–X22) and Y components for that council-year,
                 and council-level facts where reported
- facts          every reported fact with its source, quote and date (data/key_events/facts_*.csv)
- dictionary     column meanings
Headline facts: for each (event, council, fact) the preferred value is the latest-dated official source, else the
latest-dated news source; every value is also kept in `facts`. Nothing is summed across sources or estimated.
"""
import glob

import numpy as np
import pandas as pd

from src.common import DATA, OUT

KE = DATA / "key_events"
FACTS = ["homes_destroyed", "homes_damaged", "deaths", "injuries", "people_evacuated", "livestock_lost",
         "agricultural_loss_aud", "fencing_km_lost", "businesses_affected", "power_customers_without_supply",
         "roads_closed", "area_burned_ha", "insured_loss_aud", "recovery_funding_aud", "emergency_warning_level",
         "fire_danger_rating", "cause"]
TEMPLATE_X = ["X15_pop_density", "X16_regional_GDP_proxy_total_income_aud", "X17_SEIFA", "X18_remoteness",
              "X19_cash_reserve", "X20_own_source_revenue_ratio", "X21_debt_burden", "X22_historical_disaster_count"]
Y_COLS = ["IL_job_loss_raw", "IL_unemployment_rate_change_excess_pp", "IL_business_count_change_pct",
          "IL_business_count_change_excess_pct", "SL_income_drop_raw", "SL_income_drop_excess_pct",
          "SL_vulnerable_loss_raw", "SL_vulnerable_loss_excess", "FP_budget_crowd_out_raw",
          "FP_service_share_change_plus1_excess", "FP_debt_ratio_change_raw", "FP_operating_ratio_change_plus1_excess",
          "FP_cash_cover_change_plus1_excess", "DL_insurance_loss_raw"]


def load_facts():
    parts = [pd.read_csv(f, dtype=str) for f in sorted(glob.glob(str(KE / "facts_*.csv")))]
    if not parts:
        return pd.DataFrame(columns=["agrn", "council", "fact", "value"])
    f = pd.concat(parts, ignore_index=True)
    f["council"] = f.council.fillna("ALL").str.strip()
    f["as_of"] = pd.to_datetime(f.as_of_date, errors="coerce")
    f["official"] = f.source_type.str.lower().eq("official")
    return f


def headline(f):
    """(agrn, council, fact) -> preferred value and its source."""
    if f.empty:
        return pd.DataFrame(columns=["agrn", "council", "fact", "value", "source_url"])
    g = f[f.value.notna() & (f.value.astype(str).str.strip() != "")]
    g = g.sort_values(["official", "as_of"], ascending=[False, False])
    return g.drop_duplicates(["agrn", "council", "fact"])[["agrn", "council", "fact", "value", "source_url"]]


def build():
    seed = pd.read_csv(KE / "seed_events.csv", dtype={"agrn": str})
    fires = pd.read_csv(OUT / "fires.csv", low_memory=False, dtype={"region_id": str})
    fires["agrn"] = fires.official_declaration_agrn.fillna("").astype(str).str.split(";")
    fx = fires.explode("agrn")
    fx = fx[fx.agrn != ""]
    facts = load_facts()
    head = headline(facts)
    summ = pd.concat([pd.read_csv(p, dtype=str) for p in glob.glob(str(KE / "summaries_*.csv"))], ignore_index=True) \
        if glob.glob(str(KE / "summaries_*.csv")) else pd.DataFrame(columns=["agrn"])

    # ---- event × council
    rows = []
    for a, g in fx.groupby(["agrn", "region_id"]):
        agrn, code = a
        g = g.copy()
        w = g.region_burn_area_ha.fillna(0)
        big = g.loc[w.idxmax()]
        one = g.drop_duplicates("event_id")
        r = dict(agrn=agrn, region_id=code, region_name=big.region_name, fires_n=g.event_id.nunique(),
                 fire_names="; ".join(one.sort_values("region_burn_area_ha", ascending=False).event_name.head(8)),
                 first_fire_start=g.date_start.dropna().astype(str).min(), last_fire_end=g.date_end.dropna().astype(str).max() if g.date_end.notna().any() else np.nan,
                 burn_area_in_council_ha=w.sum(), share_of_council_burned=g.share_of_region_burned.sum(),
                 largest_fire_total_area_ha=g.X1_burn_area.max(), max_fire_duration_days=g.X4_fire_duration.max(),
                 max_ffdi=g.X2_FFDI.max(), min_spei3=g.X3_SPEI.min(), max_temp_c=g.X7_temp_max.max(),
                 min_rh_pct=g.X8_humidity_min.min(), max_wind_kmh=g.X9_wind_max.max(),
                 hotspots_n=g.hotspot_count.sum(min_count=1) if "hotspot_count" in g else np.nan,
                 severity_high_extreme_share=(np.average(g.X6_severity.dropna(),
                                                         weights=w[g.X6_severity.notna()].clip(lower=1e-9))
                                              if g.X6_severity.notna().any() else np.nan),
                 mean_slope_deg=np.average(g.X11_slope.fillna(0), weights=w.clip(lower=1e-9)),
                 dominant_vegetation=big.X12_vegetation, mean_canopy_pct=big.X13_canopy_cover,
                 road_km_burned=g.X14_road_exposure.sum(),
                 homes_destroyed_by_these_fires=one.DL_house_loss_raw.sum(min_count=1) if "DL_house_loss_raw" in one else np.nan)
        for c in TEMPLATE_X + Y_COLS:  # council-year context: from the largest fire's row (same council & FY)
            r[c] = big.get(c, np.nan)
        rows.append(r)
    ec = pd.DataFrame(rows)
    # the same fires can sit under two overlapping declarations (e.g. AGRN 880 North Coast from July 2019 and AGRN 871
    # statewide from August 2019): list the other declarations so sums across events are not double counted
    multi = fx.groupby(["event_id", "region_id"]).agrn.apply(lambda s: set(s))
    other = {}
    for (eid, code), ags in multi.items():
        for a in ags:
            other.setdefault((a, code), set()).update(ags - {a})
    ec["also_under_declarations"] = ["; ".join(sorted(other.get((a, c), set()))) for a, c in zip(ec.agrn, ec.region_id)]
    if not head.empty:
        hc = head[head.council != "ALL"].copy()
        hc["key"] = hc.council.str.lower().str.replace(r"[^a-z]", "", regex=True)
        ec["key"] = ec.region_name.str.lower().str.replace(r"\(nsw\)", "", regex=True).str.replace(r"[^a-z]", "", regex=True)
        piv = hc.pivot_table(index=["agrn", "key"], columns="fact", values="value", aggfunc="first")
        piv.columns = [f"reported_{c}" for c in piv.columns]
        ec = ec.merge(piv.reset_index(), on=["agrn", "key"], how="left").drop(columns="key")

    # ---- events
    ev = seed.copy()
    agg = ec.groupby("agrn").agg(councils_with_fires=("region_id", "nunique"), fires_n=("fires_n", "sum"),
                                 burn_area_ha=("burn_area_in_council_ha", "sum"), max_ffdi=("max_ffdi", "max"))
    ev = ev.merge(agg, left_on="agrn", right_index=True, how="left")
    if not head.empty:
        ha = head[head.council == "ALL"].pivot_table(index="agrn", columns="fact", values="value", aggfunc="first")
        ha.columns = [f"reported_{c}" for c in ha.columns]
        ev = ev.merge(ha, left_on="agrn", right_index=True, how="left")
    keep = [c for c in ["agrn", "real_agrn_if_found", "official_name_if_found", "towns_affected", "summary", "key_sources"]
            if c in summ.columns]
    if keep:
        ev = ev.merge(summ[keep].drop_duplicates("agrn"), on="agrn", how="left")

    dic = pd.DataFrame([
        ("agrn", "Declaration ID (AGRN); 'RAA-' = from NSW Rural Assistance Authority annual reports without AGRN"),
        ("burn_area_in_council_ha", "Area burned inside this council by the declared event's fires (GA outlines)"),
        ("share_of_council_burned", "Share of the council area burned by these fires"),
        ("max_ffdi", "Highest daily FFDI during any of these fires (reanalysis; ranks fires, not official FFDI)"),
        ("severity_high_extreme_share", "Area-weighted share of burnt area in high/extreme severity (NSW FESM)"),
        ("homes_destroyed_by_these_fires", "Sum of official homes-destroyed figures of the fires touching this council "
                                           "(whole-fire figures; a fire spanning councils counts fully in each)"),
        ("also_under_declarations", "Other declarations covering some of the same fires in this council (avoid double counting)"),
        ("reported_*", "Headline fact from news/official reports: latest official source preferred; all in `facts`"),
        ("X15…X22, IL_*, SL_*, FP_*, DL_*", "Council context and Y components for this council and financial year "
                                            "(see the main dataset's dictionary); _excess = vs councils without a large fire"),
    ], columns=["column", "meaning"])
    path = OUT / "nsw_key_bushfire_events.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        ev.to_excel(w, sheet_name="events", index=False)
        ec.to_excel(w, sheet_name="event_council", index=False)
        facts.drop(columns=[c for c in ["as_of", "official"] if c in facts]).to_excel(w, sheet_name="facts", index=False)
        dic.to_excel(w, sheet_name="dictionary", index=False)
    ev.to_csv(OUT / "key_events.csv", index=False)
    ec.to_csv(OUT / "key_event_council.csv", index=False)
    return ev, ec, facts


if __name__ == "__main__":
    ev, ec, facts = build()
    print(len(ev), "events;", len(ec), "event×council rows;", len(facts), "facts")
