"""Write the fires / lga_year / dictionary / sources workbook in Bowen's template column order."""
import pandas as pd

from src.common import MANIFEST, OUT
from src.links import rows as download_links

# (column, meaning, unit, source, note) — template columns first, in template order
TEMPLATE = [
    ("event_id", "Fire event ID (GA inventory)", "str", "Geoscience Australia bushfire boundaries", ""),
    ("event_name", "Fire name as recorded by the agency", "str", "GA", ""),
    ("region_id", "LGA 2021 code", "str", "ABS ASGS 2021", "one row per fire × LGA it burned in"),
    ("region_name", "LGA name", "str", "ABS ASGS 2021", ""),
    ("year", "Calendar year of fire start", "int", "GA", ""),
    ("date_start", "Fire start (ignition) date", "date", "GA", ""),
    ("date_end", "Fire end date (extinguish, else capture)", "date", "GA", "missing when not recorded"),
    ("Y", "Composite impact index 0–1", "float", "", "blank: to be designed in class"),
    ("Y_class", "Light / medium / heavy / extreme", "category", "", "blank: to be designed in class"),
    ("DL", "Direct loss, standardised", "float", "", "blank: to be designed in class"),
    ("IL", "Indirect impact, standardised", "float", "", "blank: to be designed in class"),
    ("FP", "Fiscal pressure, standardised", "float", "", "blank: to be designed in class"),
    ("SL", "Social impact, standardised", "float", "", "blank: to be designed in class"),
    ("DL_insurance_loss_raw", "Insured loss of the linked ICA catastrophe (AUD, original)", "float",
     "ICA Historical Catastrophe List (June 2024)",
     "CATASTROPHE-LEVEL, same value on every linked fire, may include other states; see ica_* and area-share proxy"),
    ("DL_house_loss_raw", "Homes destroyed by the whole fire", "count",
     "NSW coronial inquiry, NSW RFS, AIDR (see house_loss_source)",
     "official per-fire figures, mainly 2019-20 and major fires; blank = no official figure; same value on each council row"),
    ("IL_GRP_change_raw", "Gross regional product change", "float", "",
     "no official LGA GRP is published (economy.id/REMPLAN estimates are proprietary); proxies: "
     "IL_business_count_change_pct (ABS business counts) and IL_total_income_change_pct_proxy (ABS income)"),
    ("IL_job_loss_raw", "Change in unemployed persons: quarter after the fire vs same quarter a year before",
     "float", "DEWR Small Area Labour Markets (smoothed)", "positive = more unemployed"),
    ("FP_reconstruction_gap_raw", "Reconstruction funding gap", "float", "", "not publicly measurable at council level"),
    ("FP_budget_crowd_out_raw", "Crowd-out: fall in the everyday-services share of council spending (community services, "
     "recreation & culture, environment), FY before the fire to FY after", "pp", "NSW OLG Time Series Data",
     "positive = services squeezed; see FP_service_share_change_plus1_excess for the comparison-adjusted version"),
    ("SL_income_drop_raw", "Median income change, event FY vs previous FY (%)", "float",
     "ABS Personal Income in Australia", "negative = drop; income data end FY 2021-22"),
    ("SL_vulnerable_loss_raw", "Rise in working-age income-support recipients per 1,000 residents: quarter after the "
     "fire vs same quarter a year before", "per 1,000", "DSS Payments by LGA; ABS ERP",
     "proxy for loss to vulnerable groups; 2016 onward; SL_vulnerable_loss_excess removes statewide shocks (e.g. COVID)"),
    ("X1_burn_area", "Fire burned area (ha, whole fire)", "float", "GA outline", "area inside this LGA: region_burn_area_ha"),
    ("X2_FFDI", "Max McArthur Mark 5 FFDI during the fire", "float",
     "computed: Open-Meteo ERA5 daily Tmax, RH min, wind max + drought factor from NASA POWER rain (KBDI)",
     "reanalysis wind is a 25 km daily value, so peaks are lower than station FFDI"),
    ("X3_SPEI", "SPEI-3 at the ignition month (negative = drier than normal)", "float",
     "computed from NASA POWER rain and Hargreaves PET, 1991–2020 reference", "normal fit per calendar month"),
    ("X4_fire_duration", "Fire duration (days)", "float", "GA dates", ""),
    ("X5_hotspot_density", "Satellite hotspots per km² of the outline + 500 m buffer, during the fire", "float", "DEA Hotspots (all products)",
     "0 = queried, none found"),
    ("X6_severity", "Share of burnt pixels in high or extreme severity", "float", "NSW FESM (season of the fire)",
     "fires inside FESM mapping"),
    ("X7_temp_max", "Max 2 m temperature during the fire (°C)", "float", "Open-Meteo ERA5", ""),
    ("X8_humidity_min", "Min relative humidity during the fire (%)", "float", "Open-Meteo ERA5", ""),
    ("X9_wind_max", "Max 10 m wind speed during the fire (km/h)", "float", "Open-Meteo ERA5", ""),
    ("X10_elevation", "Mean elevation inside the fire (m)", "float", "AWS Terrain Tiles (SRTM-based), ~65 m", ""),
    ("X11_slope", "Mean slope inside the fire (degrees)", "float", "computed from AWS Terrain Tiles", ""),
    ("X12_vegetation", "Dominant NVIS Major Vegetation Group inside the fire", "category", "NVIS 6.0 (100 m)", ""),
    ("X13_canopy_cover", "Mean tree canopy cover inside the fire (%)", "float", "Hansen GFC v1.11 treecover2000", ""),
    ("X14_road_exposure", "Road km inside the fire within this LGA", "float", "2019 OSM network (excl. service)", ""),
    ("X15_pop_density", "LGA population ÷ area, year before the fire (per km²)", "float", "ABS ERP", ""),
    ("X16_regional_GDP", "Regional GDP", "float", "", "no official LGA GDP; see X16_regional_GDP_proxy_total_income_aud"),
    ("X17_SEIFA", "IRSD score (2016 for fires ≤2020, 2021 after)", "float", "ABS SEIFA", ""),
    ("X18_remoteness", "Remoteness class at fire centroid (0 major city … 4 very remote)", "float", "ABS RA 2021", ""),
    ("X19_cash_reserve", "Council cash cover (months), FY before the fire", "float", "AUSSEF fiscal panel (NSW OLG)", ""),
    ("X20_own_source_revenue_ratio", "Council own-source revenue (%), FY before", "float", "AUSSEF fiscal panel", ""),
    ("X21_debt_burden", "Council debt service ratio (%), FY before", "float", "AUSSEF fiscal panel", ""),
    ("X22_historical_disaster_count", "Declared disasters for the LGA in the previous 10 years", "int",
     "AUSSEF disaster declarations (NSW Reconstruction Authority)",
     "declaration dates parsed from names; the table has few declarations before 2018, so early fires are undercounted"),
    ("X23_insurance_coverage", "Insurance coverage", "float", "", "not publicly available by LGA"),
    ("split", "train / val / test", "str", "", "blank: to be designed in class"),
]


def write(fires, lga_year, extras_doc):
    OUT.mkdir(exist_ok=True)
    tcols = [c for c, *_ in TEMPLATE]
    for c in tcols:
        if c not in fires:
            fires[c] = pd.NA
    extra = [c for c in fires.columns if c not in tcols]
    fires = fires[tcols + extra]
    rows = []
    for c, meaning, unit, src, note in TEMPLATE:
        rows.append(dict(column=c, meaning=meaning, unit=unit, source=src, note=note, in_template="yes"))
    for c in extra:
        m, u, s, n = extras_doc.get(c, ("", "", "", ""))
        rows.append(dict(column=c, meaning=m, unit=u, source=s, note=n, in_template="no"))
    dic = pd.DataFrame(rows)
    cov = fires.replace("", pd.NA).notna().mean() * 100
    dic["coverage_pct"] = dic.column.map(cov).round(1)
    sources = pd.read_csv(MANIFEST).drop_duplicates("name", keep="last") if MANIFEST.exists() else pd.DataFrame()
    xlsx = OUT / "nsw_fire_events_2015_2025.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        fires.to_excel(w, sheet_name="fires", index=False)
        lga_year.to_excel(w, sheet_name="lga_year", index=False)
        dic.to_excel(w, sheet_name="dictionary", index=False)
        sources.to_excel(w, sheet_name="sources", index=False)
        links = download_links()
        links.to_excel(w, sheet_name="download_links", index=False)
        ws = w.sheets["download_links"]
        for i, u in enumerate(links.download_url, start=2):
            if u.startswith("http") and "{" not in u:
                ws.cell(row=i, column=3).hyperlink = u
                ws.cell(row=i, column=3).style = "Hyperlink"
    fires.to_csv(OUT / "fires.csv", index=False)
    lga_year.to_csv(OUT / "lga_year.csv", index=False)
    dic.to_csv(OUT / "dictionary.csv", index=False)
    download_links().to_csv(OUT / "download_links.csv", index=False)
    return xlsx, dic
