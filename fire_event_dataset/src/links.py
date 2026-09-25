"""The `download_links` sheet: every download URL behind the dataset, one row per file or API.

Types: file = direct file download; api = web service queried per fire / grid cell (an example request is given);
page = landing page only (no direct file URL recorded for that input).
"""
import pandas as pd

from src.common import DATA

ABS_ASGS = ("https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/"
            "edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/")
PIA = "https://www.abs.gov.au/statistics/labour/earnings-and-working-conditions/personal-income-australia/"
SEED_2019 = ("https://datasets.seed.nsw.gov.au/dataset/f7eb3f73-5831-4cc9-8259-8d1f210214ac/resource/"
             "51106786-6f4c-4383-a3c5-5ae59b397e0e/download/fireseverityfesm.zip")
SEED_2020B = ("https://datasets.seed.nsw.gov.au/dataset/71e2d6bb-136a-4046-aba4-2bbe77086392/resource/"
              "18d9fad3-b421-4183-879f-ab902af1ffc6/download/fireseverityfesm.zip")


def rows():
    r = []
    add = lambda used, name, url, kind, note="": r.append(dict(used_for=used, dataset=name, download_url=url, type=kind, note=note))

    # fires and boundaries
    add("fire list, outlines, dates (GA_V2)", "Geoscience Australia bushfire boundaries, historical (zip, file geodatabase)",
        "https://d28rz98at9flks.cloudfront.net/149017/149017_00_0.zip", "file", "SHA-256 checked on every build")
    add("fire list, outlines, dates (2020–25)", "GA Historical Bushfire Extents 2020–25, FeatureServer layer 3 (NSW, not prescribed)",
        "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/arcgis/rest/services/Historical_Bushfire_Extents_2020%E2%80%9325_View/"
        "FeatureServer/3/query?where=state+LIKE+%27NSW%25%27&outFields=*&outSR=4283&f=geojson", "api", "paged, 200 records per request")
    add("region_id, region_name, area", "ABS LGA 2021 boundaries (GDA94 shapefile)", ABS_ASGS + "LGA_2021_AUST_GDA94_SHP.zip", "file")
    add("X18_remoteness", "ABS Remoteness Areas 2021 (GDA94)",
        "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/"
        "edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/RA_2021_AUST_GDA94.zip", "file")
    add("X14_road_exposure", "OpenStreetMap Australia extract, 1 Jan 2019 (Geofabrik)",
        "https://download.geofabrik.de/australia-oceania/australia-190101.osm.pbf", "file",
        "from the earlier road-closure pilot; service roads excluded")

    # weather
    add("X2_FFDI, X7–X9, rain during fire", "Open-Meteo historical weather API (ERA5)",
        "https://archive-api.open-meteo.com/v1/archive?latitude=-33.4&longitude=150.4&start_date=2019-10-24&end_date=2019-12-23"
        "&daily=temperature_2m_max,relative_humidity_2m_min,wind_speed_10m_max,precipitation_sum&timezone=Australia/Sydney",
        "api", "one request per fire; example shown")
    add("X2 drought factor, X3_SPEI", "NASA POWER daily point API",
        "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR,T2M_MAX,T2M_MIN&community=AG"
        "&latitude=-33.5&longitude=150.5&start=19910101&end=20251231&format=JSON", "api", "one request per 0.5° cell; example shown")

    # fire behaviour and landscape
    add("X5_hotspot_density", "DEA Hotspots WFS (Geoscience Australia)",
        "https://hotspots.dea.ga.gov.au/geoserver/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=public:hotspots"
        "&outputFormat=application/json&count=10&CQL_FILTER=datetime%20BETWEEN%20%272019-12-01T00:00:00Z%27%20AND%20"
        "%272019-12-02T00:00:00Z%27%20AND%20BBOX(geometry,-33.9000,150.0000,-32.9000,150.9000)", "api", "one query per fire; example shown")
    for line in (DATA / "fesm/urls.txt").read_text().splitlines():
        s, u = line.split()
        if s == "202021":
            continue
        add("X6_severity", f"NSW FESM severity raster, season {s[:4]}-{s[4:]}", u, "file")
    add("X6_severity", "NSW FESM severity raster, season 2019-20", SEED_2019, "file", "copy already on disk in data/Manual")
    add("X6_severity", "NSW FESM severity raster, season 2020-21", SEED_2020B, "file")
    add("X10_elevation, X11_slope", "AWS Open Data Terrain Tiles (terrarium PNG, zoom 11)",
        "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/11/1879/1227.png", "api",
        "1,926 tiles, pattern .../terrarium/11/{x}/{y}.png; example shown is the Blue Mountains tile")
    add("X12_vegetation", "NVIS 6.0 Present Major Vegetation Groups, MDBA ImageServer (exportImage)",
        "https://gis.mdba.gov.au/arcgis/rest/services/Vegetation/NVIS_Version_6_0_Australia_Present_Major_Vegetation_Groups/"
        "ImageServer/exportImage?bbox=835300,-4213400,2082700,-3206900&bboxSR=3577&imageSR=3577&format=tiff&pixelType=S8&f=image",
        "api", "requested in 2000 × 2000 px tiles covering this box")
    add("(not used: format unreadable)", "NVIS 7.0 Present MVG rasters (File Geodatabase)",
        "https://www.arcgis.com/sharing/rest/content/items/5e70b5afc36a4c458a2cceb313eb3889/data", "file",
        "downloaded, but the raster format needs a GDAL build this project does not have")
    for t in ("20S_140E", "20S_150E", "30S_140E", "30S_150E"):
        add("X13_canopy_cover", f"Hansen Global Forest Change v1.11 tree cover 2000, tile {t}",
            f"https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_treecover2000_{t}.tif", "file")

    # people and economy
    add("X15_pop_density, population", "ABS Regional population 2024-25, LGA ERP 2001–2025",
        "https://www.abs.gov.au/statistics/people/population/regional-population/2024-25/32180DS0004_2001-25.xlsx", "file")
    add("X15 (fallback)", "ABS Regional population 2022-23, LGA ERP 2001–2023",
        "https://www.abs.gov.au/statistics/people/population/regional-population/2022-23/32180DS0004_2001-23.xlsx", "file")
    add("SL_income_drop_raw, X16 proxy", "ABS Personal Income in Australia 2011-12 to 2017-18 (Table 1)",
        PIA + "2011-12-2017-18/6524055002_DO001.xls", "file")
    add("SL_income_drop_raw, X16 proxy", "ABS Personal Income in Australia 2015-16 to 2019-20 (Table 1)",
        PIA + "2015-16-2019-20/6524055002_DO001.xlsx", "file")
    add("SL_income_drop_raw, X16 proxy", "ABS Personal Income in Australia 2021-22, Table 1 (2017-18 to 2021-22)",
        PIA + "2021-22/Table%201%20-%20Total%20income%2C%20earners%20and%20summary%20statistics%20by%20geography%2C"
        "%202017-18%20to%202021-22.xlsx", "file")
    add("SL_income_drop_raw, X16 proxy", "ABS Personal Income in Australia 2022-23, Table 1 (2018-19 to 2022-23)",
        PIA + "2022-23/Table%201%20-%20Total%20income%2C%20earners%20and%20summary%20statistics%20by%20geography%2C"
        "%202018-19%20to%202022-23.xlsx", "file", "latest release")
    add("X17_SEIFA (2016)", "ABS SEIFA 2016, LGA indexes",
        "https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&2033055001%20-%20lga%20indexes.xls&2033.0.55.001"
        "&Data%20Cubes&5604C75C214CD3D0CA25825D000F91AE&0&2016&27.03.2018&Latest", "file")
    add("X17_SEIFA (2021)", "ABS SEIFA 2021, LGA indexes",
        "https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/2021/"
        "Local%20Government%20Area%2C%20Indexes%2C%20SEIFA%202021.xlsx", "file")
    add("IL_job_loss_raw, unemployment", "DEWR Small Area Labour Markets, LGA (ASGS 2025), March quarter 2026",
        "https://www.dewr.gov.au/download/17069/salm-smoothed-lga-datafiles-asgs-2025-march-quarter-2026/43119/"
        "salm-smoothed-lga-datafiles-asgs-2025-march-quarter-2026/csv", "file")
    for y in (2016, 2021):
        add("industry shares", f"ABS {y} Census General Community Profile, LGA, NSW",
            f"https://www.abs.gov.au/census/find-census-data/datapacks/download/{y}_GCP_LGA_for_NSW_short-header.zip", "file")
    for line in (DATA / "dss/urls.txt").read_text().splitlines():
        fname, url = line.split("\t")
        add("SL_vulnerable_loss_raw", f"DSS Payments by LGA: {fname}", url, "file", "data.gov.au, quarterly 2016–2026")
    for yr, url in [("2012-13", "https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/14743"),
                    ("2013-14", "https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/14785"),
                    ("2014-15", "https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/15213"),
                    ("2015-16", "https://wayback.archive-it.org/22771/20240423201346/https://www.opengov.nsw.gov.au/download/15718"),
                    ("2016-17", "https://files.parliament.nsw.gov.au/fileapi/ParlFiles/GetArtifact?serverRelativeUrl=/tp/files/72400/NSW+Rural+Assistance+Authority+Annual+Report.PDF")]:
        add("X22, official declaration (2012–2017)", f"NSW Rural Assistance Authority annual report {yr} (declarations table)",
            url, "file", "declarations transcribed in AUSSEF Experiment 2 ledger (record_id gives the PDF page)")
    gap = pd.read_csv(DATA / "key_events/gap_declarations_2017_18.csv", dtype=str) \
        if (DATA / "key_events/gap_declarations_2017_18.csv").exists() else pd.DataFrame(columns=["source_url"])
    for u in gap.source_url.dropna().unique():
        name = ("NSW natural disaster declarations FY2017-18 (archived emergency.nsw.gov.au page)" if "archive.org" in u
                else "DisasterAssist declaration page: " + u.rsplit("/", 1)[-1].replace(".aspx", "").replace("-", " "))
        add("X22, official declaration (FY2017-18)", name, u, "page", "")
    hl = DATA / "house_loss/house_loss.csv"
    if hl.exists():
        for t, u in pd.read_csv(hl).drop_duplicates("source_url")[["source_title", "source_url"]].itertuples(index=False):
            add("DL_house_loss_raw", t, u, "file" if str(u).lower().endswith(".pdf") else "page", "quoted per fire in house_loss_all_sources")
    for line in (DATA / "cabee/urls.txt").read_text().splitlines():
        fname, url = line.split("\t")
        add("IL business proxy, X16 proxy", f"ABS Counts of Australian Businesses by LGA: {fname}", url, "file",
            "annual, June 2015–June 2025")
    add("DL_insurance_loss_raw", "ICA Historical Normalised Catastrophe List, June 2024",
        "https://insurancecouncil.com.au/wp-content/uploads/2024/07/ICA-Historical-Normalised-Catastrophe-June-2024.xlsx", "file")

    # council finance and disasters (from the AUSSEF database)
    for line in (DATA / "olg/urls.txt").read_text().splitlines():
        fname, url = line.split("\t")
        add("X19–X21, FP_* columns, lga_year finance", f"NSW OLG Time Series Data: {fname}", url, "file",
            "OLG values take priority; AUSSEF fiscal panels fill council-years OLG does not publish")
    for fy in ("2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26", "2026-27"):
        add("X22, official_declaration_*", f"NSW Reconstruction Authority natural disaster declarations, FY {fy}",
            "https://www.nsw.gov.au/departments-and-agencies/nsw-reconstruction-authority/about-us/recovery/"
            f"natural-disaster-declarations/fy-{fy}", "page", "via AUSSEF disasters table (source_url per declaration)")
    return pd.DataFrame(r)
