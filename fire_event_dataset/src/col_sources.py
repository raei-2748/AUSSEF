"""Source and link for every column of the X/Y workbook, by variable stem (the lga_year / fires / key-events name).

URLs are taken from out/download_links.csv (the links the pipeline actually downloaded) or from the source_url
recorded by the newer enrichment modules (fp_funding, grp_insurance, il_sector). Row-level sources (house losses,
reported facts) are pointed to the columns / sheet that hold them. `lookup` raises if a stem matches no rule.
"""
import re

import pandas as pd

from src.common import DATA, OUT

ENRICH = DATA / "enrich"


def _links():
    dl = pd.read_csv(OUT / "download_links.csv")

    def first(pattern, col="dataset", last=False):
        hit = dl[dl[col].astype(str).str.contains(pattern, regex=True)]
        assert len(hit), f"no download link matches {pattern}"
        return hit.download_url.iloc[-1 if last else 0]

    fp = pd.read_parquet(ENRICH / "fp_funding.parquet").groupby("program").source_url.first()
    g = pd.read_csv(ENRICH / "grp_insurance_long.csv", usecols=["measure", "source", "source_url"]).drop_duplicates(
        "measure").set_index("measure")
    il = pd.read_parquet(ENRICH / "il_sector.parquet", columns=["variable", "source", "release"])
    return first, fp, g, il


def rules():
    first, fp, g, il = _links()

    def dbr(prefix):
        """Data cube of the newest Data by Region release used for this family (older releases: see
        data/raw/il/urls.txt)."""
        s = il[il.variable.str.startswith(prefix)]
        s = s.assign(end=s.release.str.extract(r"(\d{2})$")[0].astype(int)).sort_values("end").source  # 2011-25 newest
        return s.iloc[-1]
    olg = first("OLG Time Series Data: time-series-data-2024", last=True)
    census = f"{first('2016 Census General Community Profile')} ; {first('2021 Census General Community Profile')}"
    R = [  # (regex on stem, source, url) — first match wins
        (r"^(X16_regional_GDP|X23_insurance_coverage|IL_GRP_change_raw|FP_reconstruction_gap_raw)$",
         "Bowen template column: no public source found, left blank (see the proxy columns)", ""),
        (r"^(Y|DL|IL|FP|SL|Y_.*|.*_rank_.*)$", "computed in src/xy_format.py (Y hierarchy)", ""),
        (r"^(info_|fire_names|also_under|summary|key_facts|key_sources|links_removed|towns_affected|"
         r"real_agrn|official_name_if|main_fires|linked_fires|councils$|source$|declaration_source_url)",
         "provenance / notes (see key_sources, data_sources)", ""),
        (r"_sourced", "per-council facts collected 2026-09-27 (src/dl_council.py): each value's title, URL, page and "
                      "verbatim quote are in the matching _source column", ""),
        (r"(pop_in_fire|pop_within|dwellings_in_fire|dwellings_within|pop_census_year|^census_year$)",
         "ABS Census Mesh Block Counts 2016 / 2021 × ABS Mesh Block boundaries × GA fire outlines (src/affected_pop.py; "
         "2016 boundaries and counts also listed in data/manifest.csv)",
         "https://www.abs.gov.au/census/guide-census-data/mesh-block-counts/2021/Mesh%20Block%20Counts%2C%202021.xlsx"),
        *[(pat, *__import__("src.panel_extra", fromlist=["ECON_SRC"]).ECON_SRC[k])
          for pat, k in [(r"(ntl_|fire_start_quarter)", "ntl"), (r"payroll_", "payroll"), (r"nsw_sfd", "nsw_sfd")]],
        (r"^reported_", "declaration, inquiry and agency reports: one source per value on the key_facts sheet "
                        "(links on key_sources)", ""),
        (r"(house_loss|homes_destroyed|homes_damaged|DL_house_loss_raw)",
         "per-fire official reports (RFS, Coroner, AIDR, council reports): links per value in the house_loss_url "
         "column (all_fires) and on key_sources", ""),
        (r"^(ica_|DL_insurance)", "ICA Historical Normalised Catastrophe List, June 2024", first("ICA Historical")),
        (r"^(agrn|declaration_name|hazard|decl_|official_declaration|X22|historical_bushfire|n_councils)",
         "NSW Reconstruction Authority / RAA / DisasterAssist declarations",
         first("Reconstruction Authority natural disaster declarations, FY 2019-20")),
        (r"(^cabee_|^businesses_|IL_business_count|business_count_release|IL_(accommodation_food|retail|arts_recreation|"
         r"agriculture)_business|accommodation_food_business_share)",
         "ABS Counts of Australian Businesses (8165.0), LGA data cube 10 (employment size) / 11 (turnover); newest "
         "release linked, one file per release in download_links", first("jul2021-jun2025_8165DC10")),
        (r"(business_entries|business_exits)", "ABS Data by Region, CABEE entries and exits (14100DO0003)",
         dbr("business_")),
        (r"(^jia_|IL_jobs_change|IL_accommodation_food_jobs)", "ABS Jobs in Australia, via Data by Region (14100DO0005)",
         dbr("jia_")),
        (r"(^pia_|own_business_income)", "ABS Personal Income in Australia, via Data by Region (14100DO0004)",
         dbr("pia_")),
        (r"insolvency", "AFSA personal insolvencies, via ABS Data by Region (14100DO0003)", dbr("insolvency")),
        (r"^tra2017_", "Tourism Research Australia LGA profiles 2017: one workbook per council (Internet Archive "
                       "copies; each council's URL is in data/raw/il/urls.txt)", ""),
        (r"(grp_fer_reds|grp_reds)", "NSW Regional Economic Development Strategies 2023 updates, section 3 (REMPLAN "
                                     "2020): one PDF per region, value for the whole region",
         "https://www.nsw.gov.au/regional-nsw/regional-economic-development-strategies"),
        (r"(grp_|X16_regional_GDP_sa4|X16_grp)", "BCARR Experimental Gross Regional Product estimates (2025)",
         "https://www.infrastructure.gov.au/department/media/publications/experimental-gross-regional-product-estimates"),
        (r"(insurance_proxy|^dw_)", "ABS Census 2016 G33 / 2021 G37 tenure by dwelling type", census),
        *[(rf"^fp_{short}_|FP_reported_{short}_", prog, str(fp.get(prog, "")))
          for prog, short in __import__("src.panel_extra", fromlist=["FP_SHORT"]).FP_SHORT.items() if short != "olg"],
        (r"FP_reported_black_summer", "sum of the FP_reported_* grant columns (see each)", ""),
        (r"^(fiscal_|X19|X20|X21|FP_|X_council_|fp_olg)", "NSW OLG Time Series Data (+ AUSSEF fiscal panels): one file "
                                                          "per year (all listed in download_links); newest linked", olg),
        (r"(median_income|total_income|income_earners|X16_regional_GDP|IL_total_income|SL_income)",
         "ABS Personal Income in Australia (LGA tables)", first("Personal Income in Australia 2022-23")),
        (r"(^population|X15|population_density)", "ABS Estimated Resident Population", first("Regional population 2024")),
        (r"(seifa|X17)", "ABS SEIFA 2016 / 2021 (IRSD)", f"{first('SEIFA 2016')} ; {first('SEIFA 2021')}"),
        (r"(unemploy|labour_force|IL_job_loss)", "DEWR Small Area Labour Markets", first("Small Area Labour Markets")),
        (r"(industry_share|dwellings|employed_persons|census_vintage)", "ABS Census General Community Profile", census),
        (r"(rent_|SL_rent)", "NSW DCJ Rent and Sales Report, quarterly rent tables (one file per quarter, all in download_links); newest linked", first("Rent and Sales", last=True)),
        (r"(income_support|jobseeker|SL_vulnerable)", "DSS Payments by LGA (data.gov.au; several files, all in download_links); newest linked", first("DSS Payments", last=True)),
        (r"(^area_km2|^region_id|^region_name)", "ABS LGA 2021 boundaries", first("LGA 2021 boundaries")),
        (r"(X18|remoteness)", "ABS Remoteness Areas 2021", first("Remoteness Areas")),
        (r"(X14|road_km)", "OpenStreetMap (Geofabrik extract)", first("OpenStreetMap")),
        (r"(X6|severity)", "NSW FESM fire extent and severity rasters, one per season (all in download_links); one season linked", first("FESM severity raster")),
        (r"(X5|hotspot)", "DEA Hotspots (Geoscience Australia) WFS; link is an example request", first("DEA Hotspots")),
        (r"(kbdi|drought_factor|X3|spei|power_cell)", "NASA POWER daily point API; link is an example request", first("NASA POWER")),
        (r"(X2|ffdi|X7|X8|X9|temp|humid|wind|rh_pct|rain_|weather_days)",
         "Open-Meteo historical weather API (ERA5), FFDI computed; link is an example request", first("Open-Meteo")),
        (r"(X10|X11|elevation|slope|terrain)", "AWS Terrain Tiles (terrarium); link is one example tile", first("Terrain Tiles")),
        (r"(X13|canopy)", "Hansen Global Forest Change v1.11 tree cover 2000 (four tiles, all in download_links); one linked", first("Hansen")),
        (r"(X12|vegetation)", "NVIS 6.0 Major Vegetation Groups", first("NVIS 6.0")),
        (r"(^X1_|burn_area|burned|share_of|largest_fire|region_share|event_id|event_name|date_|first_fire|last_fire|"
         r"fires_n|councils_with_fires|merged|ga_|agency|capture_method|fire_type|ignition|centroid|X4|duration|"
         r"^year$|^split$)",
         "Geoscience Australia bushfire boundaries (historical + 2020-25 extents)", first("bushfire boundaries")),
    ]
    return [(re.compile(p), s, u) for p, s, u in R]


_RULES = None


def lookup(stem):
    global _RULES
    if _RULES is None:
        _RULES = rules()
    for pat, s, u in _RULES:
        if pat.search(stem):
            return s, u
    raise KeyError(f"no source rule for {stem}")
