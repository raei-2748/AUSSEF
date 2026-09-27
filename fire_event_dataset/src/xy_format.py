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
MASTER_CODED_CSV = OUT / "master_event_council_coded.csv"
DETAIL_SHEETS = ("master", "post_fire_levels", "business_detail")  # the same 218 event × council rows  # same table, codes (Y1…, X1…) as column names

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
    if re.search(r"_sourced_(scope|source_type|source)$", col) or col in (
            "DL_homes_destroyed_basis", "SL_deaths_type", "SL_deaths_type_basis"):
        return "info", "info_" + col  # who / where / which source: descriptions, not measurements
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
    if col in REPORTED or col in ("reported_area_burned_ha", "reported_cause", "reported_fire_danger_rating"):
        # figures quoted in the older key-facts table: kept for reference; the *_sourced columns replace them
        return "info", "info_" + col
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
Y_HEAD = ["Y_class", "Y_class_label", "Y", "Y_norm", "Y_class_reason", "Y_class_from_Y",
          "Y_class_excl_responder_deaths", "Y_pillars_n",
          *PILLARS]
# Bowen's three ways of measuring Y (2026-09-27): each is a separate target; see role_if_Y_* on the variables sheet
Y_OPTIONS = {"class": ["Y_class", "Y_class_label"], "sum": ["Y", "Y_norm"]}  # FFDI as Y set aside (Ray, 2026-09-27)
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


DIVISIONS = {"A_agriculture_forestry_and_fishing": "A_agri", "C_manufacturing": "C_manuf",
             "D_electricity_gas_water_and_waste_services": "D_utilities", "E_construction": "E_constr",
             "F_wholesale_trade": "F_wholesale", "G_retail_trade": "G_retail",
             "H_accommodation_and_food_services": "H_accom_food", "I_transport_postal_and_warehousing": "I_transport",
             "J_information_media_and_telecommunications": "J_info_media", "K_financial_and_insurance_services":
             "K_finance", "L_rental_hiring_and_real_estate_services": "L_real_estate",
             "M_professional_scientific_and_technical_services": "M_professional",
             "N_administrative_and_support_services": "N_admin", "O_public_administration_and_safety": "O_public_admin",
             "P_education_and_training": "P_education", "Q_health_care_and_social_assistance": "Q_health",
             "R_arts_and_recreation_services": "R_arts_rec", "S_other_services": "S_other",
             "X_currently_unknown": "X_unknown", "K_finance_and_insurance_services": "K_finance"}
NEAT = [  # (old, new) substring replacements, in order; the original name stays on the variables sheet
    *DIVISIONS.items(),
    ("cabee_businesses_", "biz_"), ("jia_employee_jobs_", "jobs_emp_"), ("jia_jobs_", "jobs_"),
    ("business_entries", "biz_entries"), ("business_exits", "biz_exits"), ("tourism_businesses", "tourism_biz"),
    ("non_business_related", "nonbiz"), ("business_related", "biz"), ("insolvency_debtors_", "insolv_"),
    ("pia_own_business_income", "pia_own_biz_income"), ("pia_employee_income", "pia_emp_income"),
    ("businesses", "biz"), ("business", "biz"), ("_non_employing", "_nonemp"), ("_employing_sum", "_employing"),
    ("X_council_fiscal_", "X_council_"), ("FP_src_fiscal_", "FP_src_"), ("FP_src_fp_olg_", "FP_src_olg_"),
    ("X_council_fp_olg_", "X_council_olg_"), ("building_infrastructure_renewals_ratio", "renewals_ratio"),
    ("infrastructure", "infra"), ("_including_capital", "_incl_cap"), ("_continuing_ops", "_cont_ops"),
    ("net_operating_result_before_capital", "net_op_result_pre_cap"), ("asset_maintenance", "asset_maint"),
    ("exp_community_services_housing", "exp_community"), ("exp_public_order_health_water_sewer", "exp_public_order"),
    ("exp_roads_bridges_footpaths", "exp_roads"), ("exp_governance_admin", "exp_governance"),
    ("exp_recreation_culture", "exp_recreation"), ("exp_other_services", "exp_other"),
    ("industry_share_", "ind_share_"), ("income_support_recipients_mean", "income_support"),
    ("jobseeker_newstart_recipients_mean", "jobseeker"), ("unemployment_rate_annual_mean", "unemp_rate"),
    ("labour_force_annual_mean", "labour_force"), ("unemployed_annual_mean", "unemployed"),
    ("rent_median_weekly_mean", "rent_median_weekly"), ("unemployment_rate", "unemp_rate"),
    ("council_reported_damage_cost_estimate", "damage_estimate"), ("disaster_funding_received", "funding_received"),
    ("project_funding_in_lga", "project_funding"), ("grant_allocated", "grant"), ("grant_awarded", "grant"),
    ("_sourced_source_type", "_sourced_ref_type"), ("_sourced_source", "_sourced_ref"),
    ("X23_insurance_proxy_building_cover_required_share", "X23_insurance_proxy_share"),
    ("insurance_proxy_building_cover_required_share", "insurance_proxy_share"),
    ("X16_regional_GDP_sa4_popshare_proxy_aud_m", "X16_grp_sa4_proxy_aud_m"),
    ("X16_regional_GDP_proxy_total_income_aud", "X16_income_proxy_aud"),
    ("nominal_avg_annual_change_pct", "nominal_growth_pct"), ("real_avg_annual_change_pct", "real_growth_pct"),
    ("accommodation_food", "accom_food"), ("dwellings_occupied_census", "dwellings_occupied"),
    ("capital_grants_contributions_aud_derived_aud", "capital_grants_derived_aud"),
    ("capital_grants_contributions_derived", "capital_grants_derived"), ("tra2017_", "tra_"),
    ("_2014_17avg", "_1417avg"), ("domestic_overnight", "dom_overnight"), ("domestic_day", "dom_day"),
    ("international", "intl"), ("agriculture_forestry_fishing", "agri"), ("_fy_t_and_t_1", "_t_t1"),
    ("black_summer_recovery_grants_total", "black_summer_grants_total"),
    ("growth_pct_fy", "growth_pct"), ("_fy_pre", "_pre"), ("_fy_event", "_event"), ("_fy_plus1", "_plus1"),
    ("_june_pre", "_pre"), ("_june_event", "_event"), ("_june_plus1", "_plus1"),
]
TEMPLATE_NAMES = set()  # Bowen's template columns keep their names exactly (filled in main)


def neat(name):
    if name in TEMPLATE_NAMES:
        return name
    for old, new in NEAT:
        name = name.replace(old, new)
    return name


def relabel(d, panel=False):
    labels = [classify(c, panel) for c in d.columns]
    idx = order(labels)
    out = d.iloc[:, idx].copy()
    out.columns = [neat(labels[i][1]) for i in idx]
    table = pd.DataFrame({"column": out.columns, "original_column": [d.columns[i] for i in idx],
                          "group": [labels[i][0] for i in idx]})
    assert out.columns.is_unique, out.columns[out.columns.duplicated()].tolist()
    return out, table


SEVERITY_FILL = {1: "C6EFCE", 2: "FFEB9C", 3: "F8CBAD", 4: "FF7C80"}  # Light green, Moderate yellow, Severe orange,
# Extreme red
CLASS_COLS = ["Y_class", "Y_class_from_Y", "Y_class_excl_responder_deaths", "Y_class_label"]
SCALE_COLS = ["Y", "Y_norm", *PILLARS]  # green (low) -> yellow -> red (high)


def compact(ws, d, header_row=1, text_max=24, wide=None):
    """Compact layout: widths fitted to the values (not the long names), small one-line header, nothing wrapped,
    number formats as in combine.format_sheet. `wide` = {column: width} for text columns that deserve more room."""
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter
    wide = wide or {}
    head_font, head_align = Font(bold=True, size=8), Alignment(wrap_text=False, vertical="bottom")  # nothing wraps
    first, last = header_row + 1, header_row + len(d)
    for j, col in enumerate(d.columns, start=1):
        letter = get_column_letter(j)
        cell = ws.cell(row=header_row, column=j)
        cell.font, cell.alignment = head_font, head_align
        vals = d[col].dropna()
        fmt, width = None, 8
        if pd.api.types.is_datetime64_any_dtype(d[col]):
            fmt, width = "yyyy-mm-dd", 10
        elif pd.api.types.is_bool_dtype(d[col]):
            width = 6
        elif pd.api.types.is_numeric_dtype(d[col]) and len(vals):
            big = vals.abs().max()
            if pd.api.types.is_float_dtype(d[col]):
                med = vals.abs().median()
                whole = bool((vals == vals.round()).all())
                fmt = "#,##0" if (med >= 100 or whole) else "#,##0.00" if med >= 1 else "0.000"
                if any(k in str(col).lower() for k in ("lat", "lon")):
                    fmt = "0.0000"
            width = min(14, max(6, len(f"{big:,.0f}") + (4 if fmt and "." in fmt else 2)))
        elif len(vals):
            width = min(wide.get(col, text_max), max(6, int(vals.astype(str).str.len().quantile(0.9)) + 1))
        if fmt:
            for i in range(first, last + 1):
                ws.cell(row=i, column=j).number_format = fmt
        ws.column_dimensions[letter].width = width
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(d.columns))}{last}"


def write_sheet(w, name, d, table, na=None):
    """Band row (group, and topic on the master; one merged coloured cell per run of columns) above the column names.
    The master also gets a code row (Y1…, X1…) between the band and the names. Severity columns are colour coded."""
    from openpyxl.formatting.rule import ColorScaleRule
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    coded = "code" in table and table["code"].fillna("").astype(bool).any()
    hdr = 3 if coded else 2
    d.to_excel(w, sheet_name=name, index=False, startrow=hdr - 1)
    ws = w.sheets[name]
    compact(ws, d, header_row=hdr)
    groups = list(table["group"])
    labels = [GROUPS[g][1] + (f" · {tp}" if coded and isinstance(tp, str) and tp else "")
              for g, tp in zip(groups, table["topic"] if coded else [""] * len(groups))]
    if coded:
        code_font = Font(bold=True, size=9)
        for j, c in enumerate(table["code"], start=1):
            cell = ws.cell(row=2, column=j, value=c or None)
            cell.font, cell.alignment = code_font, Alignment(horizontal="center")
            cell.fill = PatternFill("solid", fgColor=GROUPS[groups[j - 1]][2])
    j = 1
    while j <= len(groups):  # merge each run of same-label columns into one band cell
        k = j
        while k < len(groups) and labels[k] == labels[j - 1]:
            k += 1
        g = groups[j - 1]
        fill = PatternFill("solid", fgColor=GROUPS[g][2])
        top = ws.cell(row=1, column=j, value=labels[j - 1])
        top.fill, top.font = fill, Font(bold=True, size=8)
        top.alignment = Alignment(horizontal="left", vertical="center")
        for c in range(j, k + 1):
            ws.cell(row=hdr, column=c).fill = fill
        if k > j:
            ws.merge_cells(start_row=1, start_column=j, end_row=1, end_column=k)
        j = k + 1
    ws.row_dimensions[1].height = 16
    ws.freeze_panes = f"D{hdr + 1}"
    if na is not None and na.values.any():  # cells that cannot exist: grey "N/A" (blank = not found)
        grey, centre = Font(italic=True, color="808080", size=9), Alignment(horizontal="center")
        for j, c in enumerate(d.columns, start=1):
            for i in np.flatnonzero(na[c].to_numpy()):
                cell = ws.cell(row=hdr + 1 + int(i), column=j, value="N/A")
                cell.font, cell.alignment = grey, centre
    if name == "master":
        cols = {c: i for i, c in enumerate(d.columns, start=1)}
        label_val = {v: k for k, v in CLASS_LABEL.items()}
        bold = Font(bold=True)
        for c in [c for c in CLASS_COLS if c in cols]:
            for i, v in enumerate(d[c], start=hdr + 1):
                v = label_val.get(v, v)
                if pd.notna(v) and int(v) in SEVERITY_FILL:
                    cell = ws.cell(row=i, column=cols[c])
                    cell.fill = PatternFill("solid", fgColor=SEVERITY_FILL[int(v)])
                    if c == "Y_class":
                        cell.font = bold
        for c in [c for c in SCALE_COLS if c in cols]:
            L = get_column_letter(cols[c])
            ws.conditional_formatting.add(f"{L}{hdr + 1}:{L}{len(d) + hdr}", ColorScaleRule(
                start_type="min", start_color="63BE7B", mid_type="percentile", mid_value=50, mid_color="FFEB84",
                end_type="max", end_color="F8696B"))


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


def option_role(col, role, opt, original=None):
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
        if col in Y_INPUTS or original in Y_INPUTS:
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
    mst, mmeta, na_mask, na_why = master.build(kec, book["lga_year"], decl)
    template = set(book["all_fires_dictionary"].query("in_template == 'yes'").column)
    TEMPLATE_NAMES.update(template)
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
    from src import codes
    out, t = sheets["master"]
    t = t.reset_index(drop=True)
    # Bowen's X1-X23 were examples: on the master they get plain names, so no name carries a number that differs from
    # its code (all_fires keeps his template names)
    plain = {c: re.sub(r"^X\d+_", f"X_{g}_", c) for c, g in zip(t.column, t.group) if re.match(r"^X\d+_", c)}
    plain = {c: n.replace("X_socio_grp_base_fy", "info_grp_base_fy") for c, n in plain.items()}
    assert not set(plain.values()) & set(t.column), "plain name collides with an existing column"
    t["column"] = t.column.replace(plain)
    t.loc[t.column == "info_grp_base_fy", ["group", "role"]] = ["info", "Info"]
    out = out.rename(columns=plain)
    # detail sheets: raw post-fire council levels (_src_ windows; raw material for new Y measures) and the business
    # counts by size / turnover band; the master keeps the impact measures and the per-industry business totals
    t["topic_"] = [codes.topic(c, g) for c, g in zip(t.column, t.group)]
    post = (t.role == "Y") & t.column.str.contains("_src_")
    band = (t.role == "X") & t.topic_.isin(["Business counts", "Business entries & exits"]) & t.column.str.contains(
        r"_(emp_|to_|nonemp|employing)")
    ids = t.role == "ID"
    detail = {}
    for dname, mask in [("post_fire_levels", post), ("business_detail", band)]:
        td = t[ids | mask].drop(columns="topic_").reset_index(drop=True)
        td["sheet"], td["code"], td["topic"], td["bowen_template"] = dname, "", [
            codes.topic(c, g) if r != "ID" else "" for c, g, r in zip(td.column, td.group, td.role)], ""
        detail[dname] = (out[td.column.tolist()], td)
    keep = ~(post | band)
    t, out = t[keep].drop(columns="topic_").reset_index(drop=True), out[t.column[keep].tolist()]
    t = codes.assign(t, lambda c: c in Y_HEAD or "_rank_" in c)

    def final_key(i):
        if t.role[i] == "ID":
            return (0, (i,))
        if t.code[i]:
            return (2, t.sort[i])
        if t.role[i] in ("X", "Y"):
            return (1, (i,))  # Y targets and hierarchy, named
        return (3, (i,))
    t = t.loc[sorted(t.index, key=final_key)].reset_index(drop=True).drop(columns="sort")
    out = out[t.column.tolist()]
    sheets["master"] = (out, t)
    tables[0] = t
    for dname, (dout, dt) in detail.items():
        sheets[dname] = (dout, dt)
        tables.insert(1, dt)

    def na_of(frame, table):
        """Cells that cannot exist (N/A), for a sheet's columns, from the master's N/A rules."""
        return pd.DataFrame({c: (na_mask[o].to_numpy() if o in na_mask else np.zeros(len(frame), bool))
                             for c, o in zip(table.column, table.original_column)}, index=frame.index)
    nas = {n: na_of(*sheets[n]) for n in DETAIL_SHEETS}
    for tb in tables:
        if tb.sheet.iloc[0] in DETAIL_SHEETS:
            tb["na_rule"] = [na_why.get(o, "") for o in tb.original_column]
            tb["na_cells"] = [int(nas[tb.sheet.iloc[0]][c].sum()) for c in tb.column]
    labelled = {n: sheets[n][0].astype(object).mask(nas[n], "N/A") for n in DETAIL_SHEETS}
    for dname in detail:
        labelled[dname].to_csv(OUT / f"master_{dname}.csv", index=False)
    labelled["master"].to_csv(MASTER_CSV, index=False)  # labelled names, as in the workbook; N/A = cannot exist
    labelled["master"].set_axis([c or n for c, n in zip(t.code, t.column)], axis=1).to_csv(MASTER_CODED_CSV,
                                                                                         index=False)
    variables = pd.concat(tables, ignore_index=True)[
        ["sheet", "code", "column", "role", "group_label", "topic", "bowen_template", "original_column", "meaning",
         "unit", "source", "source_url", "link_note", "note", "coverage_pct", "na_rule", "na_cells"]]

    for opt in Y_OPTIONS:
        variables[f"role_if_Y_{opt}"] = [option_role(c, r, opt, oc) if sh in DETAIL_SHEETS else ""
                                         for sh, c, r, oc in zip(variables.sheet, variables.column, variables.role,
                                                                 variables.original_column)]
    variables.to_csv(OUT / "master_variables.csv", index=False)
    removed = removed.assign(sheet="master")
    counts = kec.groupby(["Y_class", "Y_class_label"]).size().rename("rows").reset_index()
    ind_tab = pd.DataFrame([(p, n, "higher = worse" if s > 0 else "sign flipped (fall = worse)", ", ".join(c),
                             int(kec[f"{p}_rank_{slug(n)}"].notna().sum())) for p, n, s, c in INDICATORS],
                           columns=["pillar", "indicator", "direction", "source columns", "rows with data"])
    readme = pd.DataFrame({"item": [
        "What this file is", "Y: three measures", "", "", "", "", "Codes", "Labels", "", "", "", "", "Y levels", "", "", "", "", "Y_class", "", "", "",
        "Where Y is filled", "master sheet", "", "", "Blank vs zero", "Sheets"],
        "detail": [
        "The combined NSW bushfire workbook reformatted for Bowen: every column labelled X or Y. Same data, "
        "nothing dropped; only column names, column order and labels changed (see variables for old names).",
        "Recommended: sum the four pillars (DL+IL+FP+SL) -> normalise (Y, Y_norm 0-1) -> grade (Y_class 1-4).",
        "Option 1: Y_class, the 1-4 grade. Option 2: Y / Y_norm, the continuous pillar sum. Bowen's third option (FFDI "
        "itself as Y) is set aside for now: FFDI measures fire weather, not impact; it stays a predictor.",
        "Predictor roles for each option: role_if_Y_class / role_if_Y_sum on the codebook sheet.",
        "The band row on each data sheet shows the default roles (options 1 and 2).",
        "Codes on the master: row 1 = group and topic, row 2 = code, row 3 = name. Y1, Y2 … are impact variables by "
        "pillar (DL, then IL, FP, SL); X1-X23 are Bowen's template variables (or their event × council equivalents, "
        "see bowen_template on the codebook), X24 onwards our extra predictors by category (fire, terrain, people & "
        "economy, council). Codes are frozen in codes/master_codes.csv; master_event_council_coded.csv has codes as "
        "column names.",
        "Colours on the master sheet: Y_class 1 Light = green, 2 Moderate = yellow, 3 Severe = orange, 4 Extreme = red; "
        "Y, Y_norm and the pillars DL / IL / FP / SL are shaded green (low) to red (high).",
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
        "Every column's code, meaning, unit and source are on the codebook sheet; download links on download_links.",
        "Blank = not found (yet). N/A = cannot exist for that row (the source does not publish that year or quarter, the "
        "program only covered Black Summer, no ICA catastrophe was declared, TRA made no profile for the council); "
        "na_rule on the codebook says which. 0 = the source was checked and the value is zero.",
        "README, master, codebook, post_fire_levels (raw council figures in the fire year and the year after), business_detail (business counts by size and turnover band), removed_columns, insured_loss_reported (every published insured-loss figure, with quote; none is by council), indicators, key_events, all_fires, lga_year, key_facts, key_sources, "
        "download_links, data_sources"]})

    with pd.ExcelWriter(DEST, engine="openpyxl") as w:
        readme.to_excel(w, sheet_name="README", index=False)
        g = w.sheets["README"]
        combine.format_sheet(g, readme)
        from openpyxl.styles import Alignment
        for cell in g[1]:
            cell.alignment = Alignment(wrap_text=False, vertical="bottom")
        g.row_dimensions[1].height = None
        g.column_dimensions["A"].width, g.column_dimensions["B"].width = 20, 120
        g.auto_filter.ref = None
        write_sheet(w, "master", *sheets["master"], na=nas["master"])  # the main sheet, right after the README
        variables.to_excel(w, sheet_name="codebook", index=False)
        compact(w.sheets["codebook"], variables, wide={"column": 40, "bowen_template": 40, "topic": 24, "meaning": 70, "source": 45, "source_url": 40,
                                                        "note": 40, "original_column": 34, "group_label": 26,
                                                        "role_if_Y_class": 22, "role_if_Y_sum": 22})
        w.sheets["codebook"].freeze_panes = "D2"
        for name_, frame in [("insured_loss_reported", insured), ("removed_columns", removed)]:
            frame.to_excel(w, sheet_name=name_, index=False)
            compact(w.sheets[name_], frame, text_max=45)
            w.sheets[name_].freeze_panes = "A2"
        ind_tab.to_excel(w, sheet_name="indicators", index=False)
        counts.to_excel(w, sheet_name="indicators", index=False, startrow=len(ind_tab) + 3)
        compact(w.sheets["indicators"], ind_tab, text_max=45)
        w.sheets["indicators"].auto_filter.ref = None
        from openpyxl.styles import PatternFill
        ws_i = w.sheets["indicators"]
        for i, v in enumerate(counts["Y_class"], start=len(ind_tab) + 5):  # colour the class counts too
            ws_i.cell(row=i, column=1).fill = PatternFill("solid", fgColor=SEVERITY_FILL[int(v)])
            ws_i.cell(row=i, column=2).fill = PatternFill("solid", fgColor=SEVERITY_FILL[int(v)])
        for name in ["post_fire_levels", "business_detail", "key_events", "all_fires", "lga_year"]:
            out, t = sheets[name]
            write_sheet(w, name, out, t, na=nas.get(name))
        for name in ["key_facts", "key_sources", "download_links", "data_sources"]:
            book[name].to_excel(w, sheet_name=name, index=False)
            compact(w.sheets[name], book[name], text_max=45)
            w.sheets[name].freeze_panes = "A2"
    return DEST, kec


if __name__ == "__main__":
    dest, kec = main()
    print(dest)
    print(kec.groupby(["Y_class", "Y_class_label", "Y_class_reason"]).size())
