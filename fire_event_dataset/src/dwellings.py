"""Private dwellings per LGA (ABS Census 2016 G32, 2021 G36): the denominator for homes destroyed per 1,000 dwellings.

`dwellings_census` = all private dwellings, occupied + unoccupied (Census `Total_PDs_Dwellings`); holiday houses count,
because they burn too. Vintage rule as for SEIFA and industry shares: the 2016 Census for years to 2020, 2021 after.
2016 LGA codes are recoded to 2021 codes where ABS changed them (RECODE_2016: interim names of merged councils, a
renamed council, a small boundary change); Botany Bay and Rockdale are summed into Bayside (counts are additive).

Writes
- data/enrich/dwellings.parquet (event_id + region_id): dwellings in the council when the fire started
- data/enrich_lga/dwellings.parquet (region_id + year)
"""
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.common import DATA, record_source
from src.economy import GCP_URL

GCP = {2016: (DATA / "abs/gcp2016/2016 Census GCP Local Government Areas for NSW/2016Census_G32_NSW_LGA.csv",
              "LGA_CODE_2016"),
       2021: (DATA / "abs/gcp2021/2021 Census GCP Local Government Areas for NSW/2021Census_G36_NSW_LGA.csv",
              "LGA_CODE_2021")}
# 2016 code -> 2021 code (names from the 2016 Census geography file); areas match the 2021 councils
RECODE_2016 = {"10130": "10180",  # Armidale Regional (code changed with the Armidale Dumaresq/Guyra merger name)
               "13510": "12160",  # "Gundagai" (A), 3,981 km2 = Cootamundra-Gundagai Regional
               "18230": "12390",  # "Western Plains Regional" = Dubbo Regional
               "14200": "14220",  # Inverell, minor boundary change
               "11100": "10500", "16650": "10500"}  # Botany Bay + Rockdale = Bayside


def vintage(year):
    return 2016 if year <= 2020 else 2021


def census_dwellings():
    """{vintage: DataFrame indexed by LGA code (no 'LGA' prefix) with total and occupied private dwellings}."""
    out = {}
    for y, (path, code) in GCP.items():
        t = pd.read_csv(Path(path), dtype={code: str}).set_index(code)
        t.index = t.index.str.replace("LGA", "", regex=False)
        d = pd.DataFrame({"dwellings_census": pd.to_numeric(t.Total_PDs_Dwellings, errors="coerce"),
                          "dwellings_occupied_census": pd.to_numeric(t.OPDs_Tot_OPDs_Dwellings, errors="coerce")})
        if y == 2016:
            d = d.groupby(lambda c: RECODE_2016.get(c, c)).sum(min_count=1)
        out[y] = d
    return out


def run(ev, pieces):
    dw = census_dwellings()
    start = ev.set_index("event_id").start
    rows = []
    for r in pieces[["event_id", "LGA_CODE21"]].itertuples(index=False):
        code, v = str(r.LGA_CODE21), vintage(pd.Timestamp(start[r.event_id]).year)
        row = dict(event_id=r.event_id, region_id=code, dwellings_census_vintage=v)
        if code in dw[v].index:
            row.update(dw[v].loc[code].to_dict())
        rows.append(row)
    fire = pd.DataFrame(rows)
    (DATA / "enrich").mkdir(exist_ok=True)
    fire.to_parquet(DATA / "enrich/dwellings.parquet")

    codes = sorted(set(pieces.LGA_CODE21.astype(str)) | set(dw[2021].index))
    lga = pd.DataFrame([dict(region_id=c, year=y, **dw[vintage(y)].loc[c].to_dict())
                        for c in codes for y in range(2014, 2026) if c in dw[vintage(y)].index])
    (DATA / "enrich_lga").mkdir(exist_ok=True)
    lga.to_parquet(DATA / "enrich_lga/dwellings.parquet")

    doc = {
        "dwellings_census": ["Private dwellings in the council, occupied + unoccupied", "dwellings",
                             "ABS Census GCP (2016 G32 / 2021 G36)", "2016 Census for fires to 2020, 2021 after; "
                             "denominator for homes destroyed per 1,000 dwellings"],
        "dwellings_occupied_census": ["Occupied private dwellings in the council", "dwellings",
                                      "ABS Census GCP (2016 G32 / 2021 G36)", ""],
        "dwellings_census_vintage": ["Census year used for dwelling counts", "year", "ABS Census", ""],
    }
    (DATA / "enrich/dwellings.doc.json").write_text(json.dumps(doc, indent=1))
    for y in GCP:
        record_source(f"ABS {y} Census General Community Profile, LGA, NSW", GCP_URL.format(y=y),
                      DATA / f"abs/gcp_{y}.zip", "CC BY 4.0", "industry of employment and dwelling tables")
    return fire, lga


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    pieces = gpd.read_parquet(DATA / "cache/fire_lga_pieces.parquet")
    f, l = run(ev, pieces)
    print(f.notna().mean().round(3).to_string())
    print(l.groupby("year").dwellings_census.agg(["count", "sum"]))
