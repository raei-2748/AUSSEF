"""Bowen's format: every column labelled ID / Y / X, and the Y hierarchy filled on the event × council sheet.

Y levels (docs/y_composition/README.md §4):
  indicator (raw, signed so higher = worse) -> percentile rank 0-1 -> pillar DL / IL / FP / SL (mean of its indicators)
  -> composite Y (equal-weight mean of available pillars) -> Y_class 1-4.
Y_class: 1 Light, 2 Moderate, 3 Severe, 4 Extreme. Base class from Y's position in the sample (bottom 50% / next 30% /
next 15% / top 5%), raised to a floor by reported direct losses so a catastrophic pillar cannot be averaged away:
homes destroyed in the council >= 10 or any death -> at least 3; homes destroyed >= 100 -> 4.

Reads out/nsw_bushfires_2015_2025_combined.xlsx (build it first); writes out/nsw_bushfires_2015_2025_XY.xlsx and
out/key_event_council_Y.csv. No model is fitted.
Run: uv run --no-sync --with openpyxl python -m src.xy_format
"""
import re

import numpy as np
import pandas as pd

from src.common import OUT

SRC = OUT / "nsw_bushfires_2015_2025_combined.xlsx"
DEST = OUT / "nsw_bushfires_2015_2025_XY.xlsx"
Y_CSV = OUT / "key_event_council_Y.csv"
MASTER_CSV = OUT / "master_event_council.csv"

# ---------------------------------------------------------------- column roles
GROUPS = {  # group -> (role, band label, fill colour)
    "ID": ("ID", "ID · keys and dates", "D9D9D9"),
    "Y": ("Y", "Y · composite and class", "E6A0A0"),
    "DL": ("Y", "Y · DL direct loss", "F8CBAD"),
    "IL": ("Y", "Y · IL indirect loss", "FFE699"),
    "FP": ("Y", "Y · FP fiscal pressure", "F4C7DE"),
    "SL": ("Y", "Y · SL social loss", "FCE4D6"),
    "fire": ("X", "X · fire and weather", "9DC3E6"),
    "env": ("X", "X · terrain, vegetation, location", "C6E0B4"),
    "socio": ("X", "X · people and economy", "BDD7EE"),
    "council": ("X", "X · council finance and history", "D9D2E9"),
    "panel_socio": ("Panel", "Panel · people and economy (X before a fire, Y source after)", "DDEBF7"),
    "panel_council": ("Panel", "Panel · council finance (X before a fire, Y source after)", "E4DFEC"),
    "info": ("Info", "Info · provenance and notes", "F2F2F2"),
}
PREFIX = {"fire": "X_fire_", "env": "X_env_", "socio": "X_socio_", "council": "X_council_", "info": "info_"}
X_NUM = {**{i: "fire" for i in range(1, 10)}, **{i: "env" for i in range(10, 15)},
         **{i: "socio" for i in range(15, 19)}, **{i: "council" for i in range(19, 24)}}

ID_COLS = {"event_id", "event_name", "region_id", "region_name", "year", "date_start", "date_end", "split", "agrn",
           "declaration_name", "hazard", "decl_start", "decl_end", "first_fire_start", "last_fire_end",
           "official_declaration_agrn", "official_declaration_name"}
FIRE = {"region_burn_area_ha", "region_share_of_fire", "share_of_region_burned", "hotspot_count",
        "hotspot_viirs_count", "hotspot_viirs_density", "kbdi_at_start", "drought_factor_at_start",
        "rain_during_fire_mm", "ignition_cause", "fire_type_flag", "burn_area_in_council_ha",
        "share_of_council_burned", "largest_fire_total_area_ha", "max_fire_duration_days", "max_ffdi", "min_spei3",
        "max_temp_c", "min_rh_pct", "max_wind_kmh", "hotspots_n", "severity_high_extreme_share", "fires_n",
        "linked_burn_area_ha", "burn_area_ha", "councils_with_fires", "n_councils", "reported_area_burned_ha",
        "reported_cause", "reported_fire_danger_rating"}
ENV = {"road_km_within_100m", "elevation_min", "elevation_max", "slope_p90", "vegetation_mvg_code",
       "vegetation_dominant_share", "vegetation_forest_share", "vegetation_cleared_share",
       "canopy_cover_share_over_30pct", "centroid_lat", "centroid_lon", "mean_slope_deg", "dominant_vegetation",
       "mean_canopy_pct", "road_km_burned"}
SOCIO = {"population_prev_year", "employed_persons_census", "dwellings_census", "dwellings_occupied_census",
         "unemployment_rate_pre", "labour_force_pre", "unemployed_pre", "businesses_total_pre",
         "rent_median_weekly_pre", "income_support_recipients_pre", "income_support_per_1000_pre", "remoteness_name",
         "median_income_aud_pre", "total_income_aud_pre", "income_earners_pre", "pop_in_fire", "pop_within_1km",
         "pop_within_5km", "pop_within_5km_all_councils", "dwellings_in_fire", "dwellings_within_1km",
         "dwellings_within_5km"}
COUNCIL = {"historical_bushfire_declarations_10y"}
# Y source data: the raw levels a Y indicator is computed from (pillar, new name)
Y_SRC = {"unemployment_rate_after": "IL", "unemployed_after": "IL", "unemployment_rate_change_pp": "IL",
         "total_income_aud_event": "IL", "total_income_aud_plus1": "IL",
         "median_income_aud_event": "SL", "median_income_aud_plus1": "SL", "income_earners_event": "SL",
         "income_earners_plus1": "SL", "ica_normalised_loss_2022": "DL", "ica_claims_count": "DL",
         "homes_destroyed_by_these_fires": "DL", "homes_destroyed_area_share": "DL"}
# reported facts from declarations / inquiries, by pillar (deaths and injuries are human loss -> SL)
REPORTED = {"reported_homes_destroyed": "DL", "reported_homes_damaged": "DL", "reported_facilities_destroyed": "DL",
            "reported_outbuildings_destroyed": "DL", "reported_fencing_km_lost": "DL",
            "reported_livestock_lost": "DL", "reported_insured_loss_aud": "DL", "reported_deaths": "SL",
            "reported_injuries": "SL", "reported_power_customers_without_supply": "IL",
            "reported_recovery_funding_aud": "FP"}
Y_OWN = {"homes_damaged": "DL_homes_damaged"}
FISCAL_INFO = ("council_name", "fiscal_source", "council_population")


def classify(col, panel=False):
    """(group, new column name) for one column. Raises on anything not covered, so no column goes unlabelled."""
    if col in ID_COLS:
        return "ID", col
    if panel:
        if col.startswith(("fiscal_", "fp_")):
            return ("info" if any(k in col for k in FISCAL_INFO) else "panel_council"), col
        return "panel_socio", col
    if col in {"Y", "Y_class", "Y_class_label", "DL", "IL", "FP", "SL"} or col.startswith("Y_"):
        return "Y", col
    m = re.match(r"^(DL|IL|FP|SL)_", col)
    if m:
        return m.group(1), col
    for group in ("fire", "env", "socio", "council", "info"):
        if col.startswith(PREFIX[group]):
            return group, col
    m = re.match(r"^X(\d+)_", col)
    if m:
        return X_NUM[int(m.group(1))], col
    from src.panel_extra import econ_doc
    ed = econ_doc(col)
    if ed:
        return ed[0], ed[1]
    if col in Y_OWN:
        return Y_OWN[col][:2], Y_OWN[col]
    if col in REPORTED:
        return REPORTED[col], f"{REPORTED[col]}_{col}"
    if col in Y_SRC:
        return Y_SRC[col], f"{Y_SRC[col]}_src_{col}"
    m = re.match(r"^fiscal_(.+)_(pre|event|plus1)$", col)
    if m:
        name, when = m.groups()
        if any(k in name for k in FISCAL_INFO):
            return "info", PREFIX["info"] + col
        return ("council", f"X_council_{name}_pre") if when == "pre" else ("FP", f"FP_src_{name}_{when}")
    for group, names in (("fire", FIRE), ("env", ENV), ("socio", SOCIO), ("council", COUNCIL)):
        if col in names or (group == "socio" and col.startswith("industry_share_")) \
                or (group == "fire" and col.startswith("severity_share_") and col != "severity_share_unburnt"):
            return group, PREFIX[group] + col
    if col in INFO:
        return "info", PREFIX["info"] + col
    raise KeyError(f"unclassified column: {col}")


INFO = {"date_end_note", "agency", "capture_method", "ga_fire_ids", "merged_record_count", "merged_event_ids",
        "merged_event_names", "ga_source", "business_count_release", "dwellings_census_vintage", "census_vintage",
        "hotspot_first_utc", "hotspot_last_utc", "hotspot_note", "house_loss_source", "house_loss_url",
        "house_loss_match_confidence", "house_loss_all_sources", "ica_cat", "ica_event_name", "ica_event_start",
        "ica_event_finish", "ica_states", "ica_linked_fires", "rent_change_basis", "severity_note",
        "severity_mapped_share", "severity_season", "severity_decimation", "severity_share_unburnt", "terrain_pixels",
        "terrain_note", "vegetation_note", "power_cell", "weather_days", "ffdi_peak_date", "fire_names",
        "also_under_declarations", "reported_other", "source", "declaration_source_url", "councils", "linked_fires",
        "main_fires", "key_facts", "real_agrn_if_found", "official_name_if_found", "towns_affected", "summary",
        "key_sources", "links_removed", "census_year", "pop_census_year"}

# ---------------------------------------------------------------- Y hierarchy
# (pillar, indicator name, sign, source columns averaged before ranking) — sign +1 means higher = worse already
INDICATORS = [
    ("DL", "homes destroyed per 1,000 dwellings", +1, ["DL_homes_destroyed_per_1000_dwellings"]),
    ("IL", "total personal income fall, excess", -1, ["IL_total_income_change_excess_pct"]),
    ("IL", "business count fall, excess", -1, ["IL_business_count_change_excess_pct"]),
    ("FP", "cash cover drawdown, excess (FY t and t+1)", -1,
     ["FP_cash_cover_change_event_excess", "FP_cash_cover_change_plus1_excess"]),
    ("FP", "services crowd-out, excess (t+1)", -1, ["FP_service_share_change_plus1_excess"]),
    ("FP", "renewals ratio rise, excess (t+1)", +1, ["FP_renewals_ratio_change_plus1_excess"]),
    ("SL", "income-support recipients rise, excess", +1, ["SL_vulnerable_loss_excess"]),
]
PILLARS = ["DL", "IL", "FP", "SL"]
Y_INPUTS = {c for _, _, _, cols in INDICATORS for c in cols} | {"DL_homes_destroyed_in_council", "SL_deaths_sourced",
                                                                 "reported_deaths"}
Y_HEAD = ["Y_class", "Y_class_label", "Y", "Y_norm", "Y_FFDI", "Y_class_reason", "Y_class_from_Y",
          "Y_class_excl_responder_deaths", "Y_pillars_n",
          *PILLARS]
# Bowen's three ways of measuring Y (2026-09-27): each is a separate target; see role_if_Y_* on the variables sheet
Y_OPTIONS = {"class": ["Y_class", "Y_class_label"], "sum": ["Y", "Y_norm"], "FFDI": ["Y_FFDI"]}
FFDI_INPUTS = ("temp", "humid", "rh_pct", "wind", "drought_factor", "kbdi", "rain_during")  # FFDI is computed from these
MIN_PILLARS = 2
CLASS_CUTS = [0.50, 0.80, 0.95]  # Y percentile: below 50% -> 1, 50-80 -> 2, 80-95 -> 3, top 5% -> 4
CLASS_LABEL = {1: "Light", 2: "Moderate", 3: "Severe", 4: "Extreme"}


def floor_class(base, homes, deaths):
    """Direct-loss floor on the class from Y, so a catastrophic loss is not averaged away:
    >=100 homes destroyed -> 4; >=10 homes or >=2 deaths -> at least 3; exactly one death -> one level up, at most 3.
    Deaths count everyone the fire killed in the council, residents and responders alike (as EM-DAT and the Sendai
    mortality indicator do); see Y_class_excl_responder_deaths for the class without firefighter / aircrew deaths."""
    out = base.copy()
    one = (deaths >= 1) & (deaths < 2)
    out = out.where(~one, np.fmin(np.fmax(out, out + 1), np.fmax(out, 3)))
    out = out.where(~((homes >= 10) | (deaths >= 2)), np.fmax(out, 3))
    out = out.where(~(homes >= 100), 4)
    return out.where(base.notna())


def build_y(k):
    """Add rank indicators, pillar scores, composite Y and Y_class to the event × council rows."""
    k = k.copy()
    for pillar, name, sign, cols in INDICATORS:
        raw = sign * k[cols].mean(axis=1, skipna=True)
        k[f"{pillar}_rank_{slug(name)}"] = raw.rank(pct=True)  # ties share the average rank; NaN stays NaN
    for p in PILLARS:
        ranks = [c for c in k.columns if c.startswith(f"{p}_rank_")]
        k[p] = k[ranks].mean(axis=1, skipna=True)
    k["Y_pillars_n"] = k[PILLARS].notna().sum(axis=1)
    k["Y"] = k[PILLARS].mean(axis=1, skipna=True).where(k["Y_pillars_n"] >= MIN_PILLARS)
    pct = k["Y"].rank(pct=True)
    base = pd.Series(np.select([pct >= CLASS_CUTS[2], pct >= CLASS_CUTS[1], pct >= CLASS_CUTS[0]], [4, 3, 2], 1),
                     index=k.index).where(k["Y"].notna())
    homes = k["DL_homes_destroyed_in_council"]
    deaths = k["SL_deaths_sourced"].fillna(k["reported_deaths"]) if "SL_deaths_sourced" in k else k["reported_deaths"]
    k["Y_class_from_Y"] = base
    k["Y_class"] = floor_class(base, homes, deaths)
    # sensitivity: the same rule counting only deaths that were not firefighters / aircrew
    k["Y_class_excl_responder_deaths"] = floor_class(base, homes, deaths - k["SL_deaths_responders"].fillna(0))
    k["Y_class_label"] = k["Y_class"].map(CLASS_LABEL)
    k["Y_norm"] = (k.Y - k.Y.min()) / (k.Y.max() - k.Y.min())  # the pillar sum, rescaled to 0 (lowest) - 1 (highest)
    k["Y_FFDI"] = k["max_ffdi"]  # Bowen's option 3: highest FFDI of the event's fires in this council
    k["Y_class_reason"] = np.where(
        k["Y_class"].isna(), f"fewer than {MIN_PILLARS} pillars with data",
        np.where(k["Y_class"] > k["Y_class_from_Y"].fillna(0),
                 np.select([homes >= 100, homes >= 10, deaths >= 2],
                           ["raised: >=100 homes destroyed", "raised: >=10 homes destroyed", "raised: >=2 deaths"],
                           "raised one level: one death"),
                 "from composite Y"))
    return k


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# ---------------------------------------------------------------- workbook
def order(labels):
    """ID first, then Y (composite, DL, IL, FP, SL), then X groups, then panel, then info; stable within a group."""
    rank = {g: i for i, g in enumerate(GROUPS)}
    head = {c: i for i, c in enumerate(Y_HEAD)}
    return sorted(range(len(labels)), key=lambda i: (rank[labels[i][0]], head.get(labels[i][1], len(head)), i))


def relabel(d, panel=False):
    labels = [classify(c, panel) for c in d.columns]
    idx = order(labels)
    out = d.iloc[:, idx].copy()
    out.columns = [labels[i][1] for i in idx]
    table = pd.DataFrame({"column": out.columns, "original_column": [d.columns[i] for i in idx],
                          "group": [labels[i][0] for i in idx]})
    assert out.columns.is_unique, out.columns[out.columns.duplicated()].tolist()
    return out, table


def write_sheet(w, name, d, table):
    """Band row (role · group, coloured) above the column names; data from row 3."""
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from src import combine
    d.to_excel(w, sheet_name=name, index=False)
    ws = w.sheets[name]
    combine.format_sheet(ws, d)
    ws.auto_filter.ref = None
    ws.insert_rows(1)
    for j, g in enumerate(table["group"], start=1):
        fill = PatternFill("solid", fgColor=GROUPS[g][2])
        top = ws.cell(row=1, column=j, value=GROUPS[g][1])
        top.fill, top.font = fill, Font(bold=True, size=9)
        top.alignment = Alignment(wrap_text=True, vertical="bottom")
        ws.cell(row=2, column=j).fill = fill
    ws.row_dimensions[1].height, ws.row_dimensions[2].height = 42, 30
    ws.freeze_panes = "C3"
    ws.auto_filter.ref = f"A2:{get_column_letter(len(d.columns))}{len(d) + 2}"


# columns that repeat another column under a second name; dropped only when identical in every row. Different
# variables that merely happen to be equal here (e.g. counts of 200+ employee businesses that are 0 or blank in all
# these councils) are kept
ALIASES = [r"insurance_proxy_building_cover_required_share_census$", r"grp_fer_reds_aud_m_2020$",
           r"business_(entries|exits)_total_fy_event$", r"insolvency_debtors_business_related_fy_event$",
           r"cabee_businesses_all_(total|non_employing)_june_"]


def prune(d, keep=()):
    """Drop all-blank columns (except Bowen's template columns) and known aliases identical to an earlier column (the
    earlier, canonical one is kept). Returns (frame, table of what was removed and why)."""
    gone, seen = [], {}
    for c in d.columns:
        if c not in keep and d[c].isna().all():
            gone.append((c, "no data in any row"))
            continue
        if c in keep or c in Y_HEAD or "_rank_" in c:  # template and Y-hierarchy columns are never pruned
            continue
        key = tuple(d[c].astype(str))
        if key in seen and any(re.search(p_, c) for p_ in ALIASES):
            gone.append((c, f"same variable as {seen[key]} (identical in every row)"))
        elif key not in seen:
            seen[key] = c
    return d.drop(columns=[c for c, _ in gone]), pd.DataFrame(gone, columns=["original_column", "why removed"])


OVERRIDE = {  # original column -> {field: value}: fixes to inherited dictionary entries (2026-09-27 audit)
    "X19_cash_reserve": {"unit": "months"},
    "DL_homes_destroyed_in_council": {
        "meaning": "Homes destroyed in this council by this event: sourced figures only (the per-council fact of "
                   "src/dl_council.py, else a council fact in key_facts); feeds DL and the class floor. The area-share "
                   "estimate is NOT used (see homes_destroyed_area_share)", "unit": "homes",
        "source": "per-council facts: see DL_homes_destroyed_sourced_source and key_facts"},
    "X20_own_source_revenue_ratio": {"unit": "%"},
    "X21_debt_burden": {"unit": "%"},
    "area_km2": {"source": "ABS LGA 2021 boundaries"},
    "DL_insurance_loss_raw": {
        "meaning": "Insured loss of the whole linked ICA catastrophe (all states), repeated on every council row of "
                   "the event: NOT a council value", "unit": "AUD"},
    "hotspots_n": {"meaning": "Satellite hotspots of the event's fires inside this council: each fire's hotspot count "
                              "× the fire's share inside the council, summed", "unit": "hotspots"},
    "FP_reported_bsbr_project_funding_in_lga_aud": {
        "note": "single-council projects only: multi-council projects are not split, so this undercounts"},
}


UNIT_OF = {"homes": "homes", "facilities": "buildings", "outbuildings": "buildings", "properties": "properties",
           "fencing_km": "km", "livestock": "head", "deaths": "persons", "injuries": "persons"}
KEY_DOCS = {  # original column -> (meaning, unit) where the inherited dictionaries have none
    "agrn": (None, "id"), "first_fire_start": ("Earliest start date of the event's fires in this council", "date"),
    "last_fire_end": ("Latest end date of the event's fires in this council", "date"),
    "Y_class_label": (None, "text"), "Y_class_reason": (None, "text"), "DL_homes_destroyed_basis": (None, "text"),
    "homes_destroyed_by_these_fires": (None, "homes"), "homes_destroyed_area_share": (
        "Proxy, not used in Y: whole-fire homes-destroyed figures × each fire's share inside this council, summed; "
        "double counts where a source already assigns a fire's losses to one council", "homes"),
    "DL_homes_destroyed_per_1000_dwellings": (None, "homes per 1,000 dwellings"),
    "fires_n": ("Number of the event's fires burning in this council", "fires"),
    "burn_area_in_council_ha": (None, "ha"), "share_of_council_burned": (None, "share 0-1"),
    "largest_fire_total_area_ha": ("Total area (whole fire, all councils) of the largest of these fires", "ha"),
    "max_fire_duration_days": ("Longest duration among these fires", "days"), "max_ffdi": (None, "FFDI"),
    "min_spei3": ("Lowest SPEI-3 at ignition among these fires (negative = drier than normal)", "index"),
    "max_temp_c": ("Highest daily maximum temperature during these fires", "°C"),
    "min_rh_pct": ("Lowest daily minimum relative humidity during these fires", "%"),
    "max_wind_kmh": ("Highest daily maximum wind speed during these fires", "km/h"),
    "severity_high_extreme_share": (None, "share 0-1"),
    "reported_area_burned_ha": ("Area burned as reported by the declaration / inquiry facts (key_facts)", "ha"),
    "reported_cause": ("Cause as reported in the facts (key_facts)", "text"),
    "reported_fire_danger_rating": ("Fire danger rating as reported in the facts (key_facts)", "text"),
    "X_fire_ignition_causes": ("Recorded ignition causes of these fires (GA)", "text"),
    "mean_slope_deg": ("Burned-area-weighted mean slope of these fires", "degrees"),
    "dominant_vegetation": ("NVIS major vegetation group of the largest fire", "text"),
    "mean_canopy_pct": ("Mean tree canopy cover of the largest fire", "%"),
    "road_km_burned": ("Road km inside these fires within this council", "km"),
    "X_env_vegetation_groups": ("NVIS major vegetation groups of these fires", "text"),
    "X16_grp_base_fy": (None, "financial year"), "fire_names": ("Names of up to 8 of these fires, largest first",
                                                              "text"),
    "also_under_declarations": (None, "text"), "reported_other": ("Other reported facts (key_facts)", "text"),
    "info_fire_fy": (None, "financial year"), "info_fire_event_ids": (None, "text"),
    **{f"FP_total_revenue_change_{w}_pct": (f"Council total revenue (incl. capital grants), {lab} vs the FY before the "
                                            "fire", "%") for w, lab in [("event", "fire FY"), ("plus1", "FY after")]},
    **{f"FP_own_source_revenue_change_{w}_pct": (f"Council own-source revenue (total revenue × own-source share), {lab} "
                                                 "vs the FY before the fire", "%")
       for w, lab in [("event", "fire FY"), ("plus1", "FY after")]},
    "SL_deaths_type": ("Who died: resident, civilian (not stated as resident), responder (firefighter / aircrew), "
                       "unknown", "text"),
    "SL_deaths_responders": ("Deaths of firefighters / aircrew among SL_deaths_sourced", "persons"),
    "SL_deaths_type_basis": ("Source and quote behind SL_deaths_type (data/key_events/death_types.csv)", "text"),
    "reported_power_customers_without_supply": ("Power customers without supply, reported in the facts (key_facts)",
                                                "customers"),
}


def key_doc(o):
    """(meaning, unit) for event × council columns without an inherited dictionary entry."""
    if o in KEY_DOCS:
        return KEY_DOCS[o]
    m = re.match(r"^(DL|SL)_(\w+?)_sourced(_scope|_source_type|_source)?$", o)
    if m:
        metric = m.group(2)
        unit = next((u for k, u in UNIT_OF.items() if metric.startswith(k)), "count")
        return {None: (f"{metric.replace('_', ' ')} in this council for this event: one preferred, quote-checked "
                       f"value (council total unless the _scope column says one fire only)", unit),
                "_scope": ("council_total, fire_in_council (one fire: a lower bound) or statewide_zero (a "
                           "season-wide 'no deaths' statement)", "text"),
                "_source_type": ("official or news", "text"),
                "_source": ("Source of the value: title | URL | page or section | verbatim quote", "text")}[m.group(3)]
    m = re.match(r"^reported_(\w+)$", o)
    if m:
        metric = m.group(1)
        unit = next((u for k, u in UNIT_OF.items() if metric.startswith(k)), "count")
        return (f"{metric.replace('_', ' ')} reported for this council in the declaration / inquiry facts "
                "(key_facts, one source per value)", unit)
    m = re.match(r"^FP_reported_(\w+?)_(grant_allocated|grant_awarded|project_funding_in_lga|"
                 r"council_reported_damage_cost_estimate|disaster_funding_received|infrastructure_impairment)_aud$", o)
    if m:
        return (f"{m.group(2).replace('_', ' ')}, program {m.group(1)} (2019-20 bushfire recovery; AGRN 871 rows "
                "only; Audit Office rows: bushfire-only amounts)", "AUD")
    return (None, None)


def option_role(col, role, opt):
    """Role of a master column when Y is measured as `opt` (class 1-4, pillar sum, or FFDI)."""
    if col in Y_OPTIONS[opt]:
        return "Y (target)"
    if col in sum(Y_OPTIONS.values(), []) or col in Y_HEAD or "_rank_" in col:
        return "not a predictor: another Y measure or part of one"
    ffdi = "ffdi" in col.lower()
    if opt == "FFDI":
        if ffdi:
            return "not a predictor: it is the target"
        if role == "X" and any(k in col for k in FFDI_INPUTS):
            return "not a predictor: FFDI is computed from it"
        if role == "Y":
            return ("X per Bowen's slides (an impact variable used as a predictor of FFDI; note the causal direction "
                    "runs from fire weather to impact)")
        return role
    if role == "Y":
        if col in Y_INPUTS:
            return "not a predictor: Y is built from it"
        return "not a predictor: an impact (outcome) variable, same side as Y"
    return role


def link_note(url):
    """Say when a link is a sample request or one file of many rather than the whole dataset."""
    u = str(url)
    if any(k in u for k in ("open-meteo", "hotspots.dea", "power.larc", "elevation-tiles", "gis.mdba")):
        return "example API request (the dataset is queried per fire)"
    if any(k in u for k in ("seed.nsw.gov.au", "GFC-2023", "earthenginepartners", "8165DC10", "rent-tables",
                            "rent_tables", "dss-", "time-series-data", "14100DO")):
        return "one file of several (one per year, season, tile or release); all are listed on download_links"
    return ""


GENERIC = {"float", "int", "str", "bool", "number", "numeric"}
UNIT_BY_WORD = [("hotspots per km", "hotspots per km²"), ("(°C)", "°C"), ("(km/h)", "km/h"), ("(days)", "days"), ("(degrees)", "degrees"),
                ("(m)", "m"), ("per km²", "persons per km²"), ("IRSD", "index score"), ("Remoteness", "class 0-4"),
                ("FFDI", "FFDI"), ("%", "%"), ("unemployed persons", "persons"), ("income-support", "per 1,000 residents"),
                ("recipients", "persons"), ("disasters", "declarations"), ("ha", "ha"), ("km", "km")]


def fix_unit(unit, meaning):
    """Replace a data-type 'unit' (float, int) with the real unit, read from the meaning."""
    if not isinstance(unit, str) or unit.strip().lower() not in GENERIC:
        return unit
    if unit == "str":
        return "text"
    m = str(meaning)
    return next((u for w, u in UNIT_BY_WORD if w in m), unit)


def _panel_meaning(v, pdocs):
    stem = next((k for k in pdocs if v.startswith(k.split("<")[0].split(" ")[0].rstrip("*_"))), None)
    return str(pdocs[stem])[:300] if stem else None


def main():
    from src import combine
    book = {s: pd.read_excel(SRC, sheet_name=s) for s in
            ["README", "key_events", "key_event_council", "key_facts", "key_dictionary", "key_sources", "all_fires",
             "lga_year", "all_fires_dictionary", "lga_year_dictionary", "download_links", "data_sources"]}

    from src import panel_extra
    decl = book["key_event_council"].agrn.astype(str).map(book["key_events"].assign(
        agrn=book["key_events"].agrn.astype(str)).set_index("agrn").decl_start)
    kec = build_y(panel_extra.event_extras(book["key_event_council"], decl))
    book["lga_year"] = panel_extra.extend_lga_year(book["lga_year"])
    kec.to_csv(Y_CSV, index=False)
    from src import master
    mst, mmeta = master.build(kec, book["lga_year"], decl)
    template = set(book["all_fires_dictionary"].query("in_template == 'yes'").column)
    mst, removed = prune(mst, keep=template | {"DL_homes_destroyed_in_council", "DL_homes_destroyed_per_1000_dwellings"})

    meaning = {}  # original column -> (meaning, unit, source, note, coverage)
    for s in ["all_fires_dictionary", "lga_year_dictionary", "key_dictionary"]:
        for _, r in book[s].iterrows():
            meaning.setdefault(r["column"], {k: r.get(k) for k in ["meaning", "unit", "source", "note",
                                                                   "coverage_pct"]})
    ind = {f"{p}_rank_{slug(n)}": (f"Percentile rank (0-1, higher = worse) of: {n}; source " + ", ".join(c),
                                   "rank 0-1") for p, n, _, c in INDICATORS}
    new_meaning = {
        **{p: (f"{p} pillar score: mean of its indicator ranks", "0-1") for p in PILLARS},
        "Y": ("Composite impact: equal-weight mean of the available pillar scores (DL, IL, FP, SL)", "0-1"),
        "Y_pillars_n": ("Pillars with data behind Y", "count"),
        "Y_class_from_Y": ("Class from Y's percentile alone: <50% 1, 50-80% 2, 80-95% 3, top 5% 4", "1-4"),
        "Y_class": ("Final severity class: Y class raised to the direct-loss floor (see README)", "1-4"),
        "Y_class_excl_responder_deaths": ("Sensitivity: Y_class with firefighter / aircrew deaths left out of the "
                                          "floor", "1-4"),
        "Y_class_label": ("1 Light, 2 Moderate, 3 Severe, 4 Extreme", ""),
        "Y_class_reason": ("Why the class is what it is", ""),
        "Y_norm": ("Y option 2: Y (the equal-weight mean of the 2-4 pillar scores a row has; equals their sum ÷ 4 when "
                   "all four exist) rescaled min-max so the lowest row is 0 and the highest 1", "0-1"),
        "Y_FFDI": ("Y option 3: highest daily McArthur FFDI during any of the event's fires in this council (reanalysis "
                   "weather; same value as X_fire_max_ffdi, which is then not a predictor)", "FFDI"),
        **ind,
        **{c: v[:2] for c, v in panel_extra.EVENT_DOCS.items()}}
    src_of = {c: v[2] for c, v in panel_extra.EVENT_DOCS.items()}
    pdocs = panel_extra.panel_docs()

    sheets, tables = {}, []
    fire_how = {"wmean": "Burned-area-weighted mean", "share_sum": "Sum of (whole-fire value × the fire's share inside "
                "the council)", "sum": "Sum", "max": "Maximum", "min": "Minimum"}
    fire_doc = {new: (f"{fire_how[how]} over the event's fires in this council of fires.{col}", col)
                for col, how, new in master.FIRE_AGG}
    from src import col_docs
    from src.panel_extra import econ_doc, ENRICH as _EN
    cd = col_docs.lookup()
    ECON_COLS = [c for c in pd.read_parquet(_EN / "econ_quarterly_events.parquet").columns if econ_doc(c)]
    insured = pd.read_parquet(_EN / "insured_loss.parquet")
    for name, panel in [("master", False), ("key_events", False), ("all_fires", False), ("lga_year", True)]:
        d = mst if name == "master" else book[name]
        out, t = relabel(d, panel)
        t.insert(0, "sheet", name)
        t["role"] = t["group"].map(lambda g: GROUPS[g][0])
        t["group_label"] = t["group"].map(lambda g: GROUPS[g][1])
        for f in ["meaning", "unit", "source", "note", "coverage_pct"]:
            t[f] = [meaning.get(o, {}).get(f) for o in t["original_column"]]
        for i, o in enumerate(t["original_column"]):
            if o in new_meaning:
                t.loc[i, ["meaning", "unit", "source"]] = [*new_meaning[o], src_of.get(o, "computed in src/xy_format.py")]
            elif name == "master" and o in mmeta:
                v, win, kind = mmeta[o]
                base = meaning.get(v, {})
                m_, u_ = col_docs.describe(v, *cd)
                t.loc[i, ["unit", "source", "note"]] = [u_ or base.get("unit"), base.get("source"), base.get("note")]
                period = {"static": "one-off source: latest value dated at or before the fire year, else the earliest "
                                    "after it (TRA 2017, REDS 2020 and BCARR growth can postdate the fire)",
                          "cal": "calendar year; pre = year before the fire year, event = fire year if the fire "
                                 "started Jan-Jun else the next year",
                          "fy": "financial year; pre = FY before the fire FY", "june": "30 June; pre = 30 June "
                                "before the fire FY, event = 30 June ending it"}[kind]
                t.loc[i, "meaning"] = (f"lga_year.{v}, {win} ({period}). "
                                       + str(m_ or base.get("meaning") or _panel_meaning(v, pdocs) or ""))
            elif name == "master" and o in fire_doc:
                text, col = fire_doc[o]
                base = meaning.get(col, {})
                t.loc[i, ["meaning", "unit", "source"]] = [f"{text}: {base.get('meaning', '')}", base.get("unit"),
                                                           base.get("source")]
            elif name == "master" and o in ("info_fire_event_ids", "info_fire_fy"):
                t.loc[i, "meaning"] = {"info_fire_event_ids": "GA event IDs of the fires aggregated into this row",
                                       "info_fire_fy": "Financial year of the first fire start (anchors _fy windows)"}[o]
            elif name == "lga_year":
                m_, u_ = col_docs.describe(o, *cd)
                if m_:
                    t.loc[i, "meaning"] = m_
                if u_:
                    t.loc[i, "unit"] = u_
            ed = econ_doc(o) if name != "master" else next(
                (econ_doc(c) for c in ECON_COLS if econ_doc(c)[1] == o), None)
            if ed:
                t.loc[i, ["meaning", "unit", "source"]] = [ed[2], ed[3], ed[4]]
            if name == "master":
                km, ku = key_doc(o)
                if km and (pd.isna(t.loc[i, "meaning"]) or str(t.loc[i, "meaning"]).endswith("nan")):
                    t.loc[i, "meaning"] = km
                if ku and (pd.isna(t.loc[i, "unit"]) or t.loc[i, "unit"] == ""):
                    t.loc[i, "unit"] = ku
            ov = OVERRIDE.get(o) or (OVERRIDE.get(mmeta[o][0], {}) if name == "master" and o in mmeta else {})
            for field, val in ov.items():
                t.loc[i, field] = val
        from src import col_sources
        stems = [mmeta[o][0] if name == "master" and o in mmeta else
                 fire_doc[o][1] if name == "master" and o in fire_doc else o for o in t["original_column"]]
        found = [col_sources.lookup(st) for st in stems]
        t["source"] = [s if isinstance(s, str) and s.strip() else f for s, (f, _) in zip(t["source"], found)]
        t["source_url"] = [u for _, u in found]
        t["link_note"] = [link_note(u) for u in t["source_url"]]
        t["unit"] = [fix_unit(u, m_) for u, m_ in zip(t["unit"], t["meaning"])]
        t["coverage_pct"] = (out.notna().mean().round(3) * 100).values
        sheets[name], tables = (out, t), tables + [t]
    sheets["master"][0].to_csv(MASTER_CSV, index=False)  # labelled names, as in the workbook
    variables = pd.concat(tables, ignore_index=True)[
        ["sheet", "column", "role", "group_label", "original_column", "meaning", "unit", "source", "source_url",
         "link_note", "note", "coverage_pct"]]

    for opt in Y_OPTIONS:
        variables[f"role_if_Y_{opt}"] = [option_role(c, r, opt) if sh == "master" else ""
                                         for sh, c, r in zip(variables.sheet, variables.column, variables.role)]
    variables.to_csv(OUT / "master_variables.csv", index=False)
    removed = removed.assign(sheet="master")
    counts = kec.groupby(["Y_class", "Y_class_label"]).size().rename("rows").reset_index()
    ind_tab = pd.DataFrame([(p, n, "higher = worse" if s > 0 else "sign flipped (fall = worse)", ", ".join(c),
                             int(kec[f"{p}_rank_{slug(n)}"].notna().sum())) for p, n, s, c in INDICATORS],
                           columns=["pillar", "indicator", "direction", "source columns", "rows with data"])
    readme = pd.DataFrame({"item": [
        "What this file is", "Y: three measures", "", "", "", "Labels", "", "", "", "", "Y levels", "", "", "", "", "Y_class", "", "", "",
        "Where Y is filled", "master sheet", "", "", "Blank vs zero", "Sheets"],
        "detail": [
        "The combined NSW bushfire workbook reformatted for Bowen: every column labelled X or Y. Same data, "
        "nothing dropped; only column names, column order and labels changed (see variables for old names).",
        "Recommended: sum the four pillars (DL+IL+FP+SL) -> normalise (Y, Y_norm 0-1) -> grade (Y_class 1-4).",
        "Option 1: Y_class, the 1-4 grade. Option 2: Y / Y_norm, the continuous pillar sum. Option 3 (the easy way): "
        "Y_FFDI, the highest fire danger index of the event's fires in the council.",
        "Which columns may be predictors depends on the option: see role_if_Y_class / role_if_Y_sum / role_if_Y_FFDI "
        "on the variables sheet (e.g. with Y_FFDI, the weather columns FFDI is computed from are not predictors).",
        "The band row on each data sheet shows the default roles (options 1 and 2).",
        "Row 1 of each data sheet is a coloured band: ID, Y (DL / IL / FP / SL), X (fire / env / socio / council), "
        "Info. Row 2 holds the column names; data start on row 3.",
        "Y columns start with DL_, IL_, FP_ or SL_. DL_src_ / IL_src_ / FP_src_ / SL_src_ = raw levels an indicator "
        "is computed from. DL_reported_ etc. = figures reported in declarations and inquiries.",
        "X columns: X1-X23 = Bowen's template; X_fire_, X_env_, X_socio_, X_council_ = the extra X variables.",
        "info_ columns = provenance, notes, links. lga_year is a council × year panel: its values are X before a fire "
        "and Y source data after it, so it is labelled Panel.",
        "Colours: warm = Y, cool = X, grey = ID / info.",
        "Level 1 indicators: raw measures signed so higher = worse (see the indicators sheet).",
        "Level 2: each indicator -> percentile rank 0-1 across the 218 declared event × council rows.",
        "Level 3: pillar scores DL, IL, FP, SL = mean of that pillar's indicator ranks (missing ones skipped).",
        "Level 4: composite Y = equal-weight mean of the pillars with data (at least 2 needed). Higher = worse.",
        "Deaths and reported losses are not averaged in (too few rows); they set the class floor below.",
        "1 Light, 2 Moderate, 3 Severe, 4 Extreme. From Y: bottom 50% -> 1, next 30% -> 2, next 15% -> 3, top 5% -> 4.",
        "Floor so one catastrophic loss is not averaged away (sourced figures only): >=100 homes destroyed -> 4; >=10 homes "
        "destroyed or >=2 deaths -> at least 3; one death -> one level up (at most 3). Deaths include firefighters and "
        "aircrew; Y_class_excl_responder_deaths shows the class without them (SL_deaths_type says who died).",
        "Y is relative to this sample of declared events (every row is already a declared disaster), so 1 Light "
        "means light among declared disasters.",
        "Counts by class are on the indicators sheet.",
        "master (unit decided 2026-09-26: declared event × council). In all_fires the Y columns stay blank: "
        "council-level Y belongs to the declared event, not to each fire.",
        "master: one row per declared event × council (218 rows) with every variable: the Y hierarchy, the event's "
        "fire variables aggregated over its fires in the council, and every lga_year council variable in three windows.",
        "_pre = period before the fire (X). _event = the fire's period and _plus1 = the period after (Y source data). "
        "_fy columns use financial years (fire FY = FY of the first fire start), _june columns the 30 June counts, "
        "others calendar years. Census / one-off columns are taken once, for the fire's year.",
        "Every column's meaning, unit and source are on the variables sheet; download links on download_links.",
        "Blank means no data; 0 means the source was checked and the value is zero.",
        "README, variables, removed_columns, insured_loss_reported (every published insured-loss figure, with quote; none is by council), indicators, master, key_events, all_fires, lga_year, key_facts, key_sources, "
        "download_links, data_sources"]})

    with pd.ExcelWriter(DEST, engine="openpyxl") as w:
        readme.to_excel(w, sheet_name="README", index=False)
        g = w.sheets["README"]
        combine.format_sheet(g, readme)
        g.column_dimensions["A"].width, g.column_dimensions["B"].width = 20, 120
        g.auto_filter.ref = None
        variables.to_excel(w, sheet_name="variables", index=False)
        combine.format_sheet(w.sheets["variables"], variables)
        insured.to_excel(w, sheet_name="insured_loss_reported", index=False)
        combine.format_sheet(w.sheets["insured_loss_reported"], insured)
        removed.to_excel(w, sheet_name="removed_columns", index=False)
        combine.format_sheet(w.sheets["removed_columns"], removed)
        ind_tab.to_excel(w, sheet_name="indicators", index=False)
        counts.to_excel(w, sheet_name="indicators", index=False, startrow=len(ind_tab) + 3)
        combine.format_sheet(w.sheets["indicators"], ind_tab)
        w.sheets["indicators"].auto_filter.ref = None
        for name in ["master", "key_events", "all_fires", "lga_year"]:
            out, t = sheets[name]
            write_sheet(w, name, out, t)
        for name in ["key_facts", "key_sources", "download_links", "data_sources"]:
            book[name].to_excel(w, sheet_name=name, index=False)
            combine.format_sheet(w.sheets[name], book[name])
    return DEST, kec


if __name__ == "__main__":
    dest, kec = main()
    print(dest)
    print(kec.groupby(["Y_class", "Y_class_label", "Y_class_reason"]).size())
