"""Local economy enrichment: SALM unemployment (IL_job_loss_raw), ABS remoteness (X18), Census industry shares.

Writes
- data/enrich/economy.parquet  (event_id + region_id): fire-row columns
- data/enrich_lga/economy.parquet (region_id + year): council × year columns for the lga_year sheet
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from src.common import DATA, record_source

SALM_CSV = DATA / "salm/salm_lga.csv"
SALM_URL = ("https://www.dewr.gov.au/download/17069/salm-smoothed-lga-datafiles-asgs-2025-march-quarter-2026/43119/"
            "salm-smoothed-lga-datafiles-asgs-2025-march-quarter-2026/csv")
RA_SHP = DATA / "abs/RA_2021/RA_2021_AUST_GDA94.shp"
RA_URL = ("https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/"
          "edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/RA_2021_AUST_GDA94.zip")
GCP = {2016: (DATA / "abs/gcp2016/2016 Census GCP Local Government Areas for NSW", "2016Census_G51", "LGA_CODE_2016"),
       2021: (DATA / "abs/gcp2021/2021 Census GCP Local Government Areas for NSW", "2021Census_G54", "LGA_CODE_2021")}
GCP_URL = "https://www.abs.gov.au/census/find-census-data/datapacks/download/{y}_GCP_LGA_for_NSW_short-header.zip"
INDUSTRIES = {  # Census short-header prefix -> output name (ANZSIC divisions)
    "Ag_For_Fshg": "agriculture_forestry_fishing", "Mining": "mining", "Manufact": "manufacturing",
    "El_Gas_Wt_Waste": "utilities", "Constru": "construction", "WhlesaleTde": "wholesale", "RetTde": "retail",
    "Accom_food": "accommodation_food", "Trans_post_wrehsg": "transport", "Info_media_teleco": "information_media",
    "Fin_Insur": "finance_insurance", "RtnHir_REst": "rental_real_estate",
    "Pro_scien_tec": "professional_services", "Admin_supp": "admin_support",
    "Public_admin_sfty": "public_administration", "Educ_trng": "education", "HlthCare_SocAs": "health_social",
    "Art_recn": "arts_recreation", "Oth_scs": "other_services",
}
Q = {"Mar": 1, "Jun": 2, "Sep": 3, "Dec": 4}


def salm():
    d = pd.read_csv(SALM_CSV, skiprows=2, dtype=str).dropna(subset=["LGA Code (2025 ASGS)"])
    d = d.rename(columns={"Data Item": "item", "LGA Code (2025 ASGS)": "region_id"}).drop(columns=d.columns[1])
    long = d.melt(id_vars=["item", "region_id"], var_name="q", value_name="v")
    long["v"] = pd.to_numeric(long.v.str.replace(",", ""), errors="coerce")  # "-" = unavailable -> missing
    mon, yy = long.q.str[:3], long.q.str[-2:]
    long["period"] = pd.PeriodIndex(year=2000 + yy.astype(int), quarter=mon.map(Q), freq="Q")
    w = long.pivot_table(index=["region_id", "period"], columns="item", values="v", aggfunc="first")
    return w.rename(columns={"Smoothed unemployment (persons)": "unemployed", "Smoothed labour force (persons)": "labour_force",
                             "Smoothed unemployment rate (%)": "unemployment_rate"})


def census_industry():
    out = {}
    for y, (folder, stem, code) in GCP.items():
        parts = [pd.read_csv(f).set_index(code) for f in sorted(Path(folder).glob(f"{stem}*_NSW_LGA.csv"))]
        t = pd.concat(parts, axis=1)
        t = t.loc[:, ~t.columns.duplicated()]
        t.index = t.index.astype(str).str.replace("LGA", "", regex=False)
        stated = t.P_Tot_Tot - t.P_ID_NS_Tot
        s = pd.DataFrame({f"industry_share_{v}": t[f"P_{k}_Tot"] / stated for k, v in INDUSTRIES.items()})
        s["employed_persons_census"] = t.P_Tot_Tot
        out[y] = s
    return out


def remoteness(ev):
    ra = gpd.read_file(RA_SHP)
    ra = ra[ra.RA_CODE21.astype(str).str[-1].isin(list("01234"))].to_crs(3577)
    pts = gpd.GeoDataFrame(ev[["event_id"]], geometry=gpd.points_from_xy(ev.centroid_lon, ev.centroid_lat), crs=4283).to_crs(3577)
    j = gpd.sjoin(pts, ra[["RA_CODE21", "RA_NAME21", "geometry"]], how="left", predicate="within").drop_duplicates("event_id")
    j["X18_remoteness"] = j.RA_CODE21.astype(str).str[-1].where(j.RA_CODE21.notna()).astype(float)
    return j.set_index("event_id")[["X18_remoteness", "RA_NAME21"]].rename(columns={"RA_NAME21": "remoteness_name"})


def run(ev, pieces):
    sa, ind, ra = salm(), census_industry(), remoteness(ev)
    start = ev.set_index("event_id").start
    rows = []
    for r in pieces[["event_id", "LGA_CODE21"]].itertuples(index=False):
        code, s = str(r.LGA_CODE21), pd.Timestamp(start[r.event_id])
        q0 = pd.Period(s, freq="Q")
        g = lambda q, c: sa[c].get((code, q), np.nan)
        row = dict(event_id=r.event_id, region_id=code,
                   unemployment_rate_pre=g(q0 - 1, "unemployment_rate"), labour_force_pre=g(q0 - 1, "labour_force"),
                   unemployed_pre=g(q0 - 1, "unemployed"),
                   unemployment_rate_after=g(q0 + 1, "unemployment_rate"), unemployed_after=g(q0 + 1, "unemployed"))
        # job loss: unemployed persons in the quarter after the fire minus the same quarter one year earlier
        row["IL_job_loss_raw"] = row["unemployed_after"] - g(q0 - 3, "unemployed")
        row["unemployment_rate_change_pp"] = row["unemployment_rate_after"] - g(q0 - 3, "unemployment_rate")
        v = 2016 if s.year <= 2020 else 2021
        if code in ind[v].index:
            row.update(ind[v].loc[code].to_dict())
        row["census_vintage"] = v
        rows.append(row)
    fire = pd.DataFrame(rows)
    fire["X18_remoteness"] = fire.event_id.map(ra.X18_remoteness)
    fire["remoteness_name"] = fire.event_id.map(ra.remoteness_name)
    (DATA / "enrich").mkdir(exist_ok=True)
    fire.to_parquet(DATA / "enrich/economy.parquet")

    # council × year
    ann = sa.reset_index().assign(year=lambda x: x.period.dt.year).groupby(["region_id", "year"])[
        ["unemployment_rate", "labour_force", "unemployed"]].mean().add_suffix("_annual_mean").reset_index()
    lga_rows = []
    for (code, y), grp in ann.groupby(["region_id", "year"]):
        rr = grp.iloc[0].to_dict()
        v = 2016 if y <= 2020 else 2021
        if code in ind[v].index:
            rr.update(ind[v].loc[code].to_dict())
        lga_rows.append(rr)
    lga = pd.DataFrame(lga_rows)
    (DATA / "enrich_lga").mkdir(exist_ok=True)
    lga.to_parquet(DATA / "enrich_lga/economy.parquet")

    doc = {
        "unemployment_rate_pre": ["LGA smoothed unemployment rate, quarter before the fire", "%", "JSA/DEWR SALM", ""],
        "labour_force_pre": ["LGA labour force, quarter before the fire", "persons", "SALM", ""],
        "unemployed_pre": ["LGA unemployed persons, quarter before the fire", "persons", "SALM", ""],
        "unemployment_rate_after": ["Unemployment rate, quarter after the fire-start quarter", "%", "SALM", ""],
        "unemployed_after": ["Unemployed persons, quarter after the fire-start quarter", "persons", "SALM", ""],
        "unemployment_rate_change_pp": ["Unemployment rate, quarter after vs same quarter a year before", "pp", "SALM",
                                        "seasonally comparable; smoothed series"],
        "remoteness_name": ["ABS remoteness area at the fire centroid", "category", "ABS RA 2021", ""],
        "census_vintage": ["Census used for industry shares", "year", "ABS Census", "2016 for fires to 2020, 2021 after"],
        "employed_persons_census": ["Employed residents (Census)", "persons", "ABS Census GCP", ""],
    }
    doc.update({f"industry_share_{v}": [f"Share of employed residents in {v.replace('_', ' ')}", "fraction",
                                        "ABS Census GCP (2016 G51 / 2021 G54)", "place of usual residence; excludes not stated"]
                for v in INDUSTRIES.values()})
    (DATA / "enrich/economy.doc.json").write_text(json.dumps(doc, indent=1))
    record_source("JSA/DEWR Small Area Labour Markets, LGA (ASGS 2025), March quarter 2026", SALM_URL, SALM_CSV, "CC BY 4.0",
                  "smoothed unemployment, labour force, rate, Dec 2010 – Mar 2026")
    record_source("ABS Remoteness Areas 2021 (GDA94)", RA_URL, DATA / "abs/RA_2021.zip", "CC BY 4.0", "")
    for y in GCP:
        record_source(f"ABS {y} Census General Community Profile, LGA, NSW", GCP_URL.format(y=y),
                      DATA / f"abs/gcp_{y}.zip", "CC BY 4.0", "industry of employment table")
    return fire, lga


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    pieces = gpd.read_parquet(DATA / "cache/fire_lga_pieces.parquet")
    f, l = run(ev, pieces)
    print(f.notna().mean().round(3).to_string())
    print(l.shape, l.year.min(), l.year.max())
