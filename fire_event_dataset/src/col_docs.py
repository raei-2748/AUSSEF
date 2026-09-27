"""Meaning and unit of every lga_year (council × year) variable, for the variables sheet of the X/Y workbook.

The original lga_year columns are documented here by hand; the 2026-09-27 enrichments take their units from their own
tables (il_sector.unit, grp_insurance.doc.json, fp_funding amounts in AUD).
"""
import json

import pandas as pd

from src.common import DATA

ENRICH = DATA / "enrich"

LGA_YEAR = {  # column -> (meaning, unit)
    "area_km2": ("Council area", "km²"),
    "population": ("Estimated resident population at 30 June", "persons"),
    "population_density": ("Estimated resident population ÷ council area, 30 June", "persons per km²"),
    "seifa_irsd": ("SEIFA Index of Relative Socio-economic Disadvantage score (2016 Census to 2020, 2021 after)",
                   "index score"),
    "median_income_aud_fy": ("Median total personal income of income earners, financial year", "AUD"),
    "total_income_aud_fy": ("Total personal income of all income earners, financial year", "AUD"),
    "income_earners_fy": ("Number of personal income earners, financial year", "persons"),
    "fiscal_building_infrastructure_renewals_ratio_pct_fy": ("Building & infrastructure renewals ratio: asset "
                                                             "renewal spending ÷ depreciation", "%"),
    "fiscal_cash_cover_months_fy": ("Cash expense cover ratio: unrestricted cash and investments ÷ monthly "
                                    "operating and financing costs", "months"),
    "fiscal_council_population_fy": ("Council population as reported by NSW OLG", "persons"),
    "fiscal_debt_service_cover_fy": ("Debt service cover (AUSSEF fiscal panels, older years)", "ratio (times)"),
    "fiscal_debt_service_cover_ratio_fy": ("Debt service cover ratio: operating result before interest and "
                                           "depreciation ÷ principal and interest repayments; blank = no debt",
                                           "ratio (times)"),
    "fiscal_debt_service_ratio_pct_fy": ("Debt service ratio: loan repayments ÷ operating revenue", "%"),
    "fiscal_exp_community_services_housing_aud_fy": ("Spending on community services, education, housing & "
                                                     "community amenities", "AUD"),
    "fiscal_exp_environment_aud_fy": ("Spending on environment", "AUD"),
    "fiscal_exp_governance_admin_aud_fy": ("Spending on governance & administration", "AUD"),
    "fiscal_exp_other_services_aud_fy": ("Spending on other services", "AUD"),
    "fiscal_exp_public_order_health_water_sewer_aud_fy": ("Spending on public order, safety, health, water & sewer",
                                                          "AUD"),
    "fiscal_exp_recreation_culture_aud_fy": ("Spending on recreation & culture", "AUD"),
    "fiscal_exp_roads_bridges_footpaths_aud_fy": ("Spending on roads, bridges & footpaths (a published 0 is treated "
                                                  "as not reported)", "AUD"),
    "fiscal_grants_pct_fy": ("Grants & contributions share of revenue", "%"),
    "fiscal_infrastructure_backlog_ratio_pct_fy": ("Infrastructure backlog ratio: cost to bring assets to a "
                                                   "satisfactory standard ÷ asset value", "%"),
    "fiscal_maintenance_gap_aud_fy": ("Required minus actual asset maintenance spending", "AUD"),
    "fiscal_maintenance_ratio_pct_fy": ("Asset maintenance ratio: actual ÷ required maintenance", "%"),
    "fiscal_net_operating_result_before_capital_aud_fy": ("Net operating result before capital grants & "
                                                          "contributions", "AUD"),
    "fiscal_operating_ratio_pct_fy": ("Operating performance ratio: (operating revenue excl. capital grants − "
                                      "operating expenses) ÷ operating revenue", "%"),
    "fiscal_own_source_pct_fy": ("Own-source operating revenue share of total revenue", "%"),
    "fiscal_road_km_fy": ("Road length maintained by the council (local and regional roads)", "km"),
    "fiscal_roads_share_pct_fy": ("Roads, bridges & footpaths share of spending (÷ sum of the spending-by-function "
                                  "lines, OLG's definition)", "%"),
    "fiscal_service_share_pct_fy": ("Everyday services (community services & housing, recreation & culture, "
                                    "environment) share of spending (÷ sum of the spending-by-function lines)", "%"),
    "fiscal_total_expenses_aud_fy": ("Total expenses (AUSSEF fiscal panels)", "AUD"),
    "fiscal_total_expenses_continuing_ops_aud_fy": ("Total expenses from continuing operations", "AUD"),
    "fiscal_total_revenue_including_capital_aud_fy": ("Total revenue from continuing operations, including capital "
                                                      "grants", "AUD"),
    "fiscal_unrestricted_current_ratio_fy": ("Unrestricted current ratio: current assets ÷ current liabilities, "
                                             "unrestricted", "ratio (times)"),
    "fiscal_grants_per_capita_aud_fy": ("Grants & contributions revenue per resident (grants % × total revenue ÷ "
                                        "population)", "AUD per person"),
    "businesses_total_june": ("Businesses operating at 30 June", "businesses"),
    "businesses_non_employing_june": ("Non-employing businesses operating at 30 June", "businesses"),
    "income_support_recipients_mean": ("Working-age income-support recipients, mean of the calendar year's quarters",
                                       "persons"),
    "jobseeker_newstart_recipients_mean": ("JobSeeker / Newstart recipients, mean of the calendar year's quarters",
                                           "persons"),
    "dwellings_census": ("Private dwellings, occupied + unoccupied (Census 2016 to 2020, 2021 after)", "dwellings"),
    "dwellings_occupied_census": ("Occupied private dwellings (Census 2016 to 2020, 2021 after)", "dwellings"),
    "unemployment_rate_annual_mean": ("Smoothed unemployment rate, mean of the calendar year's quarters", "%"),
    "labour_force_annual_mean": ("Labour force, mean of the calendar year's quarters", "persons"),
    "unemployed_annual_mean": ("Unemployed persons, mean of the calendar year's quarters", "persons"),
    "employed_persons_census": ("Employed residents (Census 2016 to 2020, 2021 after)", "persons"),
    "rent_median_weekly_mean": ("Median weekly rent of new bonds, mean of the year's four quarters (blank unless all "
                                "four are published)", "AUD per week"),
    "rent_new_bonds_lodged": ("New rental bonds lodged in the calendar year (blank unless all four quarters are "
                              "published)", "bonds"),
}


def lookup():
    """column -> (meaning, unit) for every lga_year column, original and 2026-09-27 additions."""
    docs = dict(LGA_YEAR)
    il = pd.read_parquet(ENRICH / "il_sector.parquet", columns=["variable", "unit", "source"])
    il_units = il.drop_duplicates("variable").set_index("variable").unit
    il_doc = json.load(open(ENRICH / "il_sector.doc.json"))
    g = json.load(open(ENRICH / "grp_insurance.doc.json"))
    return docs, il_units, il_doc, g


def describe(v, docs, il_units, il_doc, g):
    """(meaning, unit) for lga_year column v; None parts when unknown."""
    if v in docs:
        return docs[v]
    if v.startswith("industry_share_"):
        return (f"Share of employed residents in {v[15:].replace('_', ' ')} (Census 2016 to 2020, 2021 after)",
                "share 0-1")
    for suf in ("_june", "_fy", "_2014_17avg", "_2017", "_census", "_2020"):
        if v.endswith(suf):
            stem = v[: -len(suf)]
            break
    else:
        stem = v
    if stem in il_units.index:
        fam = next((k for k in il_doc if stem.startswith(k.split("<")[0].split(" ")[0].rstrip("*_"))), None)
        when = {"_june": "at 30 June", "_fy": "in the financial year"}.get(v[len(stem):], "")
        return (f"{stem} {when}. {il_doc.get(fam, '') if fam else ''}".strip(), il_units[stem])
    key = stem.replace("insurance_proxy_", "X23_insurance_proxy_")
    if key in g:
        m, unit = g[key][0], g[key][1]
        return (m, unit)
    if v.startswith("fp_"):
        return (f"{v[3:-3].replace('_', ' ')} (bushfire recovery / council finance program money, financial year)",
                "AUD")
    return (None, None)
