"""Gross regional product (X16 / IL_GRP_change_raw) and an insurance-coverage proxy (X23), council level.

What public data exist (checked 2026-09-27) and what is parsed here:

GRP
- BCARR "Experimental Gross Regional Product estimates" (Dept of Infrastructure, data file 26 Feb 2025):
  GRP for every SA4 in 2015-16 and 2020-21, average annual nominal/real change, GRP per capita 2020-21.
  SA4, not LGA. Each LGA gets (a) the values of the SA4 holding most of its residents, and (b) a
  population-share proxy: sum over SA4s of GRP_sa4 x (LGA residents in the SA4 / SA4 residents), 2021 Census
  mesh-block persons. (b) assumes equal GRP per resident inside an SA4, so it is a proxy, not an estimate.
- NSW Regional Economic Development Strategies (REDS) 2023 Updates, section 3 "About the region":
  "Size of the economy (2020)" per Functional Economic Region (FER), sourced there to REMPLAN 2020
  (NIEIR 2020 for Victorian/Queensland parts). One year only; regional NSW only (no Greater Sydney,
  Newcastle, Wollongong). For cross-border FERs the NSW-LGAs figure is used. A FER may hold several LGAs;
  the value is the FER's, flagged with the FER name and number of LGAs.
- Not used (terms): NIEIR GRP for every LGA (economy.id "State of the Regions Economic Indicators", REMPLAN
  community profiles). .id terms of use forbid scraping/harvesting and feeding content to AI; REMPLAN forbids
  reproduction without written approval. No yearly LGA GRP series is openly licensed.

Insurance (X23)
- No public source reports the share of households/dwellings insured by LGA or postcode (Census has no
  insurance question; ABS HES is state/capital-city only; Actuaries Institute affordability index and
  Climate Council "uninsurable" counts are risk/affordability measures published as maps/electorate tables).
- Proxy built here from the Census (2016 G33, 2021 G37, tenure x dwelling structure, occupied private
  dwellings): share of dwellings where building insurance is normally compulsory = owned with a mortgage
  (a standard lender condition) + flats/apartments not under a mortgage (strata buildings must be insured by
  the owners corporation). Components are also given. This is not measured coverage.

Writes
- data/enrich/grp_insurance.parquet / .csv   wide: region_id (ABS LGA 2021) x year (+ fy)
- data/enrich/grp_insurance_long.csv         one row per value with its source file and location
- data/enrich/grp_insurance.doc.json          column meanings
"""
import json
import re

import numpy as np
import pandas as pd

from src.common import DATA, record_source
from src.dwellings import RECODE_2016
from src.economy import GCP_URL

RAW = DATA / "raw/grp_insurance"
BCARR_XLSX = RAW / "bcarr_experimental_grp_sa4_data_2025-02-26.xlsx"
BCARR_PDF = RAW / "bcarr_experimental_grp.pdf"
BCARR_PAGE = "https://www.infrastructure.gov.au/department/media/publications/experimental-gross-regional-product-estimates"
BCARR_XLSX_URL = ("https://www.infrastructure.gov.au/sites/default/files/documents/"
                  "bcarr-experimental-gross-regional-product-estimates-data-26february2025.xlsx")
BCARR_PDF_URL = ("https://www.infrastructure.gov.au/sites/default/files/documents/"
                 "bcarr-experimental-gross-regional-product-estimates-final.pdf")
ASGS = RAW / "asgs"
ASGS_URL = ("https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/"
            "jul2021-jun2026/access-and-downloads/allocation-files/{f}")
MBC_URL = "https://www.abs.gov.au/census/guide-census-data/mesh-block-counts/2021/Mesh%20Block%20Counts%2C%202021.xlsx"
REDS_DIR = RAW / "reds2023"
REDS_PAGE = "https://www.nsw.gov.au/regional-nsw/regional-economic-development-strategies"
CACHE = DATA / "cache/lga2021_sa4_2021_persons.parquet"
TENURE = {2016: (DATA / "abs/gcp2016/2016 Census GCP Local Government Areas for NSW/2016Census_G33_NSW_LGA.csv",
                 "LGA_CODE_2016"),
          2021: (DATA / "abs/gcp2021/2021 Census GCP Local Government Areas for NSW/2021Census_G37_NSW_LGA.csv",
                 "LGA_CODE_2021")}

# FER -> (file, page, NSW LGA names as in ABS LGA 2021, value AUD m, verbatim text that must be on the page, note)
# Values are the NSW part for cross-border FERs; pairing of label and number checked on the PDF text layer.
REDS = {
    "Albury-Wodonga": ("Albury-Wodonga-REDS-2023-Update.pdf", 9, ["Albury", "Federation", "Greater Hume Shire"],
                       5040, "NSW LGAs $5.04 billion", "NSW LGAs only; whole FER incl. Wodonga, Indigo $7.76 billion"),
    "Bathurst and Oberon": ("Bathurst-and-Oberon-REDS-2023-Update.pdf", 9, ["Bathurst Regional", "Oberon"], 3104,
                            "Size of the economy (2020) $3.104 billion", ""),
    "Castlereagh": ("Castlereagh-REDS-2023-Update.pdf", 9, ["Gilgandra", "Warrumbungle Shire"], 678,
                    "Size of the economy (2020) $678 million", ""),
    "Central Coast and Lake Macquarie": ("Central-Coast-and-Lake-Macquarie-REDS-2023-Update.pdf", 9,
                                         ["Central Coast (NSW)", "Lake Macquarie"], 26900,
                                         "Size of the economy (2020) $26.9 billion", ""),
    "Central Orana": ("Central-Orana-REDS-2023-Update.pdf", 9, ["Dubbo Regional", "Narromine"], 3758,
                      "Size of the economy (2020) $3.758 billion", ""),
    "Clarence Valley": ("Clarence-Valley-REDS-2023-Update.pdf", 9, ["Clarence Valley"], 2659,
                        "Size of the economy (2020) $2.659 billion", ""),
    "Coffs Coast": ("Coffs-Coast-REDS-2023-Update.pdf", 9, ["Bellingen", "Coffs Harbour"], 5053,
                    "Size of the economy (2020) $5.053 billion", ""),
    "Cowra": ("Cowra-REDS-2023-Update.pdf", 9, ["Cowra"], 685, "Size of the economy (2020) $685 million", ""),
    "Eastern Riverina": ("Eastern-Riverina-REDS-2023-Update.pdf", 9, ["Coolamon", "Junee", "Lockhart", "Wagga Wagga"],
                         5752, "Size of the economy (2020) $5.752 billion", ""),
    "Far South Coast": ("Far-South-Coast-REDS-2023-Update.pdf", 10, ["Bega Valley", "Eurobodalla"], 3684,
                        "Size of the economy (2020) $3.684 billion", ""),
    "Far West": ("Far-West-REDS-2023-Update.pdf", 9, ["Broken Hill", "Central Darling", "Unincorporated NSW"], 1406,
                 "Size of the economy (2020) $1.406 billion", ""),
    "Hastings Macleay": ("Hastings-Macleay-REDS-2023-Update.pdf", 9, ["Kempsey", "Port Macquarie-Hastings"], 6110,
                         "Size of the economy (2020) $6.11 billion", ""),
    "Hunter": ("Hunter-REDS-2023-Update.pdf", 9, ["Cessnock", "Dungog", "Maitland", "Muswellbrook", "Port Stephens",
                                                  "Singleton", "Upper Hunter Shire"], 24997,
               "Size of the economy (2020) $24.997 billion", "excludes Newcastle"),
    "Kiama": ("Kiama-REDS-2023-Update.pdf", 9, ["Kiama"], 796, "Size of the economy (2020) $796 million", ""),
    "Lithgow": ("Lithgow-REDS-2023-Update.pdf", 9, ["Lithgow"], 1900, "Size of the economy (2020) $1.9 billion", ""),
    "Lower North West": ("Lower-North-West-REDS-2023-Update_1.pdf", 9, ["Gunnedah", "Liverpool Plains",
                                                                         "Tamworth Regional"], 5395,
                         "Size of the economy (2020) $5.395 billion", ""),
    "Mid-Lachlan": ("Mid-Lachlan-REDS-2023-Update.pdf", 9, ["Forbes", "Lachlan", "Parkes"], 1892,
                    "Size of the economy (2020) $1.892 billion", ""),
    "Mid-Western": ("Mid-Western-REDS-2023-Update.pdf", 9, ["Mid-Western Regional"], 2795,
                    "Size of the economy (2020) $2.795 billion", ""),
    "MidCoast": ("MidCoast-REDS-2023-Update.pdf", 9, ["Mid-Coast"], 4317, "Size of the economy (2020) $4.317 billion", ""),
    "Murray": ("Murray-REDS-2023-Update.pdf", 9, ["Berrigan", "Edward River", "Murray River"], 1649, "$1.649 billion",
               "NSW LGAs only (label and value paired by page position); whole FER incl. Campaspe, Gannawarra, "
               "Moira $5.052 billion, Victorian LGAs $3.403 billion"),
    "Nambucca": ("Nambucca-REDS-2023-Update.pdf", 9, ["Nambucca Valley"], 920,
                 "Size of the economy (2020) $920 million", ""),
    "Northern New England High Country": ("Northern-New-England-High-Country-REDS-2023-Update.pdf", 9,
                                          ["Glen Innes Severn", "Tenterfield"], 779, "$0.779 billion",
                                          "NSW LGAs only (label and value paired by page position); whole FER incl. "
                                          "Southern Downs (Qld) $2.428 billion"),
    "Northern Rivers": ("Northern-Rivers-REDS-2023-Update.pdf", 9, ["Ballina", "Byron", "Kyogle", "Lismore",
                                                                    "Richmond Valley"], 8844,
                        "Size of the economy (2020) $8.844 billion", ""),
    "Orange, Blayney and Cabonne": ("Orange-Blayney-and-Cabonne-REDS-2023-Update.pdf", 9,
                                    ["Blayney", "Cabonne", "Orange"], 4339, "Size of the economy (2020) $4.339 billion", ""),
    "Queanbeyan-Palerang": ("Queanbeyan-Palerang-REDS-2023-Update.pdf", 9, ["Queanbeyan-Palerang Regional"], 2554,
                            "Size of the economy (2020) $2.554 billion", ""),
    "Shellharbour": ("Shellharbour-REDS-2023-Update.pdf", 9, ["Shellharbour"], 2635,
                     "Size of the economy (2020) $2.635 billion", ""),
    "Shoalhaven": ("Shoalhaven-REDS-2023-Update.pdf", 9, ["Shoalhaven"], 5645,
                   "Size of the economy (2020) $5.645 billion", ""),
    "Snowy Monaro": ("Snowy-Monaro-REDS-2023-Update.pdf", 9, ["Snowy Monaro Regional"], 1444,
                     "Size of the economy (2020) $1.444 billion", ""),
    "Snowy Valleys": ("Snowy-Valleys-REDS-2023-Update.pdf", 9, ["Snowy Valleys"], 1011,
                      "Size of the economy (2020) $1.011 billion", ""),
    "South West Slopes": ("South-West-Slopes-REDS-2023-Update.pdf", 9, ["Bland", "Cootamundra-Gundagai Regional",
                                                                        "Hilltops", "Temora", "Weddin"], 2755,
                          "Size of the economy (2020) $2.755 billion", ""),
    "Southern New England High Country": ("Southern-New-England-High-Country-REDS-2023-Update.pdf", 9,
                                          ["Armidale Regional", "Uralla", "Walcha"], 2509,
                                          "Size of the economy (2020) $2.509 billion", ""),
    "Southern Tablelands": ("Southern-Tablelands-REDS-2023-Update.pdf", 9, ["Goulburn Mulwaree", "Upper Lachlan Shire",
                                                                            "Yass Valley"], 2727,
                            "Size of the economy (2020) $2.727 billion", ""),
    "Tweed": ("Tweed-REDS-2023-Update.pdf", 9, ["Tweed"], 4307, "Size of the economy (2020) $4.307 billion", ""),
    "Upper North West": ("Upper-North-West-REDS-2023-Update.pdf", 9, ["Gwydir", "Inverell", "Moree Plains", "Narrabri"],
                         4042, "Size of the economy (2020) $4.042 billion", ""),
    "Western Murray": ("Western-Murray-REDS-2023-Update.pdf", 9, ["Balranald", "Hay", "Wentworth"], 795,
                       "NSW LGAs $0.795 billion", "NSW LGAs only; whole FER incl. Mildura, Swan Hill $4.043 billion"),
    "Western Plains": ("Western-Plains-REDS-2023-Update.pdf", 9, ["Bogan", "Bourke", "Brewarrina", "Cobar", "Coonamble",
                                                                  "Walgett", "Warren"], 1698,
                       "Size of the economy (2020) $1.698 billion", ""),
    "Western Riverina": ("Western-Riverina-REDS-2023-Update.pdf", 9, ["Carrathool", "Griffith", "Leeton", "Murrumbidgee",
                                                                      "Narrandera"], 3511,
                         "Size of the economy (2020) $3.511 billion", ""),
    "Wingecarribee": ("Wingecarribee-REDS-2023-Update.pdf", 9, ["Wingecarribee"], 2883,
                      "Size of the economy (2020) $2.883 billion", ""),
}


def lga_sa4_persons():
    """Census 2021 persons in each LGA 2021 x SA4 2021 intersection (NSW), from mesh blocks."""
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    lga = pd.read_excel(ASGS / "LGA_2021_AUST.xlsx", dtype=str,
                        usecols=["MB_CODE_2021", "LGA_CODE_2021", "LGA_NAME_2021", "STATE_CODE_2021"])
    mb = pd.read_excel(ASGS / "MB_2021_AUST.xlsx", dtype=str,
                       usecols=["MB_CODE_2021", "SA4_CODE_2021", "SA4_NAME_2021", "STATE_CODE_2021"])
    cnt = pd.concat([pd.read_excel(ASGS / "Mesh_Block_Counts_2021.xlsx", sheet_name=s, header=6, dtype={"MB_CODE_2021": str})
                     for s in ["Table 1", "Table 1.1"]])  # NSW parts 1 and 2
    cnt = cnt[cnt.MB_CODE_2021.str.fullmatch(r"\d{11}", na=False)]
    lga, mb = lga[lga.STATE_CODE_2021 == "1"], mb[mb.STATE_CODE_2021 == "1"]
    j = lga.merge(mb.drop(columns="STATE_CODE_2021"), on="MB_CODE_2021").merge(
        cnt[["MB_CODE_2021", "Person"]], on="MB_CODE_2021", how="left")
    j["Person"] = pd.to_numeric(j.Person, errors="coerce").fillna(0)
    out = j.groupby(["LGA_CODE_2021", "LGA_NAME_2021", "SA4_CODE_2021", "SA4_NAME_2021"], as_index=False).Person.sum()
    CACHE.parent.mkdir(exist_ok=True)
    out.to_parquet(CACHE)
    return out


def bcarr():
    t = pd.read_excel(BCARR_XLSX, sheet_name="SA4")
    t = t[t.state == "New South Wales"].iloc[:, :8]
    t.columns = ["state", "sa4", "sa4_name", "grp_2016", "grp_2021", "nom_chg", "real_chg", "grp_pc_2021"]
    t["sa4"] = t.sa4.astype(int).astype(str)
    return t.set_index("sa4")


def grp_rows(names):
    x = lga_sa4_persons()
    b = bcarr()
    sa4_pop = x.groupby("SA4_CODE_2021").Person.sum()
    x["lga_share"] = x.Person / x.groupby("LGA_CODE_2021").Person.transform("sum")
    x["sa4_share"] = x.Person / x.SA4_CODE_2021.map(sa4_pop)
    missing = set(x.SA4_CODE_2021) - set(b.index)
    assert not missing - {"197", "199"}, missing  # 197/199 = migratory/no usual address pseudo-SA4s
    src = dict(source="BCARR Experimental Gross Regional Product estimates (26 Feb 2025)", source_url=BCARR_XLSX_URL,
               source_file=str(BCARR_XLSX.relative_to(DATA)))
    rows = []
    for code, g in x.groupby("LGA_CODE_2021"):
        g = g[g.SA4_CODE_2021.isin(b.index)]
        if g.empty or g.Person.sum() == 0:
            continue
        top = g.sort_values("Person", ascending=False).iloc[0]
        s = b.loc[top.SA4_CODE_2021]
        geo = dict(region_id=code, region_name=names.get(code, top.LGA_NAME_2021), geo_level="SA4",
                   geo_code=top.SA4_CODE_2021, geo_name=top.SA4_NAME_2021, lga_pop_share_in_geo=round(top.lga_share, 4),
                   n_geo_units=len(g), **src)
        loc = f"sheet SA4, row SA4_code {top.SA4_CODE_2021}"
        for fy, yr, m, v, u, col in [
                ("2015-16", 2016, "grp_sa4_aud_m", s.grp_2016, "AUD m, current prices", "GRP 2015-16 ($m)"),
                ("2020-21", 2021, "grp_sa4_aud_m", s.grp_2021, "AUD m, current prices", "GRP 2020-21 ($m)"),
                ("2020-21", 2021, "grp_per_capita_sa4_aud", s.grp_pc_2021, "AUD per resident", "GRP per capita 2020-21 ($)"),
                ("2015-16 to 2020-21", 2021, "grp_sa4_nominal_avg_annual_change_pct", s.nom_chg, "% per year",
                 "Nominal GRP, Average annual change 2015-16 to 2020-21 (%)"),
                ("2015-16 to 2020-21", 2021, "grp_sa4_real_avg_annual_change_pct", s.real_chg, "% per year",
                 "Real GRP, Average annual change 2015-16 to 2020-21 (%) (real 21-22)")]:
            rows.append(dict(geo, fy=fy, year=yr, measure=m, value=float(v), unit=u, source_loc=f"{loc}, column '{col}'",
                             note="value of the SA4 holding most of the LGA's residents (2021 Census mesh blocks)"))
        for fy, yr, col in [("2015-16", 2016, "grp_2016"), ("2020-21", 2021, "grp_2021")]:
            v = float((g.sa4_share * g.SA4_CODE_2021.map(b[col])).sum())
            rows.append(dict(geo, geo_level="LGA (from SA4)", geo_code=code, geo_name=geo["region_name"],
                             lga_pop_share_in_geo=1.0, fy=fy, year=yr, measure="grp_lga_popshare_proxy_aud_m", value=round(v, 1),
                             unit="AUD m, current prices",
                             source_loc="sheet SA4, GRP columns; weights: ABS MB allocation files + Mesh Block Counts 2021",
                             note="PROXY: sum over SA4s of SA4 GRP x (LGA residents in SA4 / SA4 residents), 2021 Census "
                                  "persons; assumes equal GRP per resident within an SA4 (2021 weights also for 2015-16)"))
    return rows


def page_text(path, page):
    from pypdf import PdfReader
    return re.sub(r"\s+", " ", PdfReader(path).pages[page - 1].extract_text() or "")


def reds_rows(names):
    code_of = {v: k for k, v in names.items()}
    rows, missing = [], []
    for fer, (f, page, lgas, v, quote, note) in REDS.items():
        path = REDS_DIR / f
        txt = page_text(path, page)
        if quote not in txt:
            raise ValueError(f"REDS {fer}: quoted text not found on page {page}: {quote!r}")
        for n in lgas:
            code = code_of.get(n)
            if code is None:
                missing.append(n)
                continue
            rows.append(dict(region_id=code, region_name=n, fy="", year=2020, measure="grp_fer_reds_aud_m", value=float(v),
                             unit="AUD m", geo_level="LGA" if len(lgas) == 1 else "FER", geo_code=fer, geo_name=fer,
                             lga_pop_share_in_geo=np.nan, n_geo_units=len(lgas),
                             source="NSW Regional Economic Development Strategy 2023 Update, section 3 (REMPLAN 2020)",
                             source_url=f"{REDS_PAGE} -> {f}", source_file=str(path.relative_to(DATA)),
                             source_loc=f"page {page}: '{quote}'",
                             note=("'Size of the economy (2020)', the report cites REMPLAN 2020; not defined further. "
                                   + ("Value is for the whole FER of " + str(len(lgas)) + " NSW LGAs, not this LGA. "
                                      if len(lgas) > 1 else "") + note).strip()))
    if missing:
        raise ValueError(f"LGA names not in ABS LGA 2021: {missing}")
    return rows


def tenure_rows(names):
    rows = []
    for y, (path, col) in TENURE.items():
        t = pd.read_csv(path, dtype={col: str}).set_index(col)
        t.index = t.index.str.replace("LGA", "", regex=False)
        k = pd.DataFrame({
            "total": t.Total_Total, "mortgage": t.O_MTG_Total, "outright": t.O_OR_Total, "rented": t.R_Tot_Total,
            "flats": t.Total_DS_Flat_apart, "flats_not_mortgage": t.Total_DS_Flat_apart - t.O_MTG_DS_Flat_apart})
        if y == 2016:
            k = k.groupby(lambda c: RECODE_2016.get(c, c)).sum(min_count=1)
        tab = "G33" if y == 2016 else "G37"
        src = dict(source=f"ABS {y} Census GCP, NSW LGA, {tab} Tenure and landlord type by dwelling structure",
                   source_url=GCP_URL.format(y=y), source_file=str(path.relative_to(DATA)))
        for code, r in k.iterrows():
            if r.total <= 0:
                continue
            base = dict(region_id=code, region_name=names.get(code, ""), fy="", year=y, unit="share of occupied private dwellings",
                        geo_level="LGA", geo_code=code, geo_name=names.get(code, ""), lga_pop_share_in_geo=1.0, n_geo_units=1,
                        **src)
            for m, num, cols, note in [
                    ("dw_owned_mortgage_share", r.mortgage, "O_MTG_Total / Total_Total", ""),
                    ("dw_owned_outright_share", r.outright, "O_OR_Total / Total_Total", ""),
                    ("dw_rented_share", r.rented, "R_Tot_Total / Total_Total", ""),
                    ("dw_flat_apartment_share", r.flats, "Total_DS_Flat_apart / Total_Total", ""),
                    ("X23_insurance_proxy_building_cover_required_share", r.mortgage + r.flats_not_mortgage,
                     "(O_MTG_Total + Total_DS_Flat_apart - O_MTG_DS_Flat_apart) / Total_Total",
                     "PROXY, not measured coverage: dwellings where building insurance is normally compulsory - "
                     "mortgaged (lender condition) or flat/apartment (strata owners corporation must insure; "
                     "Strata Schemes Management Act 2015 (NSW) s 160). Excludes contents cover; not every flat is "
                     "strata-titled; denominator includes tenure 'not stated'")]:
                rows.append(dict(base, measure=m, value=round(float(num / r.total), 4),
                                 source_loc=f"{path.name}: {cols}", note=note))
    return rows


def run():
    x = lga_sa4_persons()
    names = x.drop_duplicates("LGA_CODE_2021").set_index("LGA_CODE_2021").LGA_NAME_2021.to_dict()
    long = pd.DataFrame(grp_rows(names) + reds_rows(names) + tenure_rows(names))
    long = long[long.region_id.isin(names)]  # NSW LGA 2021 codes only
    cols = ["region_id", "region_name", "year", "fy", "measure", "value", "unit", "geo_level", "geo_code", "geo_name",
            "lga_pop_share_in_geo", "n_geo_units", "source", "source_url", "source_file", "source_loc", "note"]
    long = long[cols].sort_values(["region_id", "year", "measure"]).reset_index(drop=True)

    wide = long.pivot_table(index=["region_id", "year"], columns="measure", values="value", aggfunc="first").reset_index()
    wide.columns.name = None
    wide.insert(1, "region_name", wide.region_id.map(names))
    fy = {2016: "2015-16", 2021: "2020-21", 2020: ""}
    wide.insert(3, "fy_grp", wide.year.map(fy))
    sa4 = long[long.measure == "grp_sa4_aud_m"].drop_duplicates("region_id").set_index("region_id")
    wide["sa4_code"] = wide.region_id.map(sa4.geo_code)
    wide["sa4_name"] = wide.region_id.map(sa4.geo_name)
    wide["sa4_lga_pop_share"] = wide.region_id.map(sa4.lga_pop_share_in_geo)
    wide["lga_n_sa4"] = wide.region_id.map(sa4.n_geo_units)
    fer = long[long.measure == "grp_fer_reds_aud_m"].set_index("region_id")
    wide["reds_fer_name"] = wide.region_id.map(fer.geo_name).where(wide.year == 2020)
    wide["reds_fer_n_nsw_lgas"] = wide.region_id.map(fer.n_geo_units).where(wide.year == 2020)

    out = DATA / "enrich"
    out.mkdir(exist_ok=True)
    wide.to_parquet(out / "grp_insurance.parquet", index=False)
    wide.to_csv(out / "grp_insurance.csv", index=False)
    long.to_csv(out / "grp_insurance_long.csv", index=False)
    doc = {
        "fy_grp": ["Financial year of the GRP values in the row (2016 = 2015-16, 2021 = 2020-21; 2020 = REDS 'size of "
                   "the economy (2020)')", "str", "", "Census rows use the Census year"],
        "grp_sa4_aud_m": ["GRP of the SA4 holding most of the LGA's residents", "AUD m, current prices",
                          "BCARR Experimental GRP estimates (2025), sheet SA4", "SA4-level value, not LGA; see sa4_lga_pop_share"],
        "grp_lga_popshare_proxy_aud_m": ["LGA GRP proxy: sum over SA4s of SA4 GRP x LGA share of SA4 residents",
                                         "AUD m, current prices", "BCARR + ABS mesh blocks 2021",
                                         "assumes equal GRP per resident inside an SA4"],
        "grp_per_capita_sa4_aud": ["GRP per resident of the SA4, 2020-21", "AUD", "BCARR", "SA4-level"],
        "grp_sa4_nominal_avg_annual_change_pct": ["SA4 nominal GRP, average annual change 2015-16 to 2020-21", "%/yr",
                                                  "BCARR", "only change published; not around a fire date"],
        "grp_sa4_real_avg_annual_change_pct": ["SA4 real GRP (2021-22 prices), average annual change 2015-16 to 2020-21",
                                               "%/yr", "BCARR", "state-by-industry deflators"],
        "grp_fer_reds_aud_m": ["'Size of the economy (2020)' of the REDS Functional Economic Region containing the LGA",
                               "AUD m", "NSW REDS 2023 Updates (REMPLAN 2020)",
                               "FER-level unless reds_fer_n_nsw_lgas = 1; NSW part for cross-border FERs; regional NSW only"],
        "dw_owned_mortgage_share": ["Occupied private dwellings owned with a mortgage", "share", "ABS Census G33/G37", ""],
        "dw_owned_outright_share": ["Occupied private dwellings owned outright", "share", "ABS Census G33/G37", ""],
        "dw_rented_share": ["Occupied private dwellings rented", "share", "ABS Census G33/G37", ""],
        "dw_flat_apartment_share": ["Occupied private dwellings that are flats or apartments", "share", "ABS Census G33/G37", ""],
        "X23_insurance_proxy_building_cover_required_share": [
            "Share of occupied private dwellings where building insurance is normally compulsory (mortgaged, or flat/"
            "apartment under strata)", "share", "ABS Census G33 (2016) / G37 (2021)",
            "PROXY, not measured insurance coverage; no public LGA coverage data exist"],
        "sa4_code": ["SA4 (2021) holding most of the LGA's residents", "code", "ABS ASGS 2021", ""],
        "sa4_lga_pop_share": ["Share of the LGA's 2021 Census residents living in sa4_code", "share", "ABS mesh blocks", ""],
        "lga_n_sa4": ["Number of SA4s the LGA's mesh blocks fall in", "count", "ABS ASGS 2021", ""],
        "reds_fer_name": ["REDS Functional Economic Region", "str", "NSW REDS 2023", ""],
        "reds_fer_n_nsw_lgas": ["NSW LGAs in the FER", "count", "NSW REDS 2023", ""],
    }
    (out / "grp_insurance.doc.json").write_text(json.dumps(doc, indent=1))

    record_source("BCARR Experimental Gross Regional Product estimates, data (SA4, 2015-16 and 2020-21)", BCARR_XLSX_URL,
                  BCARR_XLSX, "Commonwealth of Australia (Dept of Infrastructure website terms; CC BY 4.0 where marked)",
                  f"publication page {BCARR_PAGE}; published 26 Feb 2025")
    record_source("BCARR Experimental Gross Regional Product estimates, fact sheet (method, caveats)", BCARR_PDF_URL,
                  BCARR_PDF, "Commonwealth of Australia", "method: income approach, Census employment + ABS State Accounts")
    for f in ["MB_2021_AUST.xlsx", "LGA_2021_AUST.xlsx"]:
        record_source(f"ABS ASGS Edition 3 allocation file {f}", ASGS_URL.format(f=f), ASGS / f, "CC BY 4.0",
                      "mesh block -> SA4 / LGA 2021")
    record_source("ABS Mesh Block Counts, 2021 (NSW tables 1 and 1.1)", MBC_URL, ASGS / "Mesh_Block_Counts_2021.xlsx",
                  "CC BY 4.0", "Census persons per mesh block; LGA x SA4 weights")
    for fer, (f, page, *_rest) in REDS.items():
        url = [u for u in (REDS_DIR / "urls.txt").read_text().split() if u.endswith(f)][0]
        record_source(f"NSW REDS 2023 Update: {fer}", url, REDS_DIR / f, "NSW Government (nsw.gov.au copyright terms)",
                      f"page {page}, 'Size of the economy (2020)', cited to REMPLAN 2020")
    for y, (path, _c) in TENURE.items():
        record_source(f"ABS {y} Census GCP NSW LGA tenure x dwelling structure ({path.name})", GCP_URL.format(y=y), path,
                      "CC BY 4.0", "X23 insurance proxy")
    return wide, long


if __name__ == "__main__":
    w, l = run()
    print(w.shape, l.shape)
    print(w.groupby("year").apply(lambda g: g.notna().sum()).T.to_string())
