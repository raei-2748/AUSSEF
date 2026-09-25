"""SL_vulnerable_loss_raw: rise in working-age income-support recipients after a fire (DSS payments by LGA).

Measure: income_support_total (JobSeeker/Newstart, Youth Allowance other, Parenting Payments, DSP, Carer Payment,
Special Benefit; defined in src/dss.py) in the quarter after the fire-start quarter, minus the same quarter a year
earlier, per 1,000 residents (ABS ERP, year before the fire). An `_excess` version subtracts the median change in NSW
councils with no fire >= 100 ha in that window, which removes statewide shocks such as the COVID JobSeeker surge in 2020.

Councils are joined by LGA code; the 2016–2018 file uses pre-merger councils, whose counts are summed into their 2016
successor (counts are additive). Auburn and Holroyd were split between two successors, so those are left blank.
"""
import json

import geopandas as gpd
import numpy as np
import pandas as pd

from src import socio
from src.common import DATA, record_source
from src.olg import PREDECESSORS

DSS = DATA / "dss/dss_lga_quarter.parquet"
COMPARE_HA = 100
SPLIT = {"auburn", "holroyd"}


def council_quarter(lga):
    d = pd.read_parquet(DSS)
    d["name"] = d.lga_name.astype(str).str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()
    names = {socio.norm(n): str(c) for c, n in zip(lga.LGA_CODE21, lga.LGA_NAME21)}
    succ = {socio.norm(k): socio.norm(v) for k, v in PREDECESSORS.items()}
    codes21 = set(names.values())

    def to21(row):
        c = str(row.lga_code)
        if c in codes21 and row.lga_vintage != 2014:
            return c
        k = socio.norm(row["name"])
        if k in SPLIT:
            return None
        return names.get(succ.get(k, k)) or names.get(k)
    d["code21"] = d.apply(to21, axis=1)
    d = d[d.code21.notna()]
    agg = d.groupby(["code21", "quarter"])[["income_support_total", "jobseeker_newstart"]].sum(min_count=1)
    return agg


def run(ev, pieces, lga):
    q = council_quarter(lga)
    pop = socio.population()
    start = ev.set_index("event_id").start
    big = pieces[pieces.region_burn_area_ha >= COMPARE_HA]
    fire_q = set(zip(big.LGA_CODE21.astype(str), big.event_id.map(start).dt.to_period("Q")))
    wide = q.income_support_total.unstack("quarter")
    cache = {}

    def change(code, q0):
        a, b = q0 + 1, q0 - 3
        if code not in wide.index or a not in wide.columns or b not in wide.columns:
            return np.nan
        return wide.at[code, a] - wide.at[code, b]

    def bench(q0):
        if q0 not in cache:
            a, b = q0 + 1, q0 - 3
            if a in wide.columns and b in wide.columns:
                window = {q0 - 3 + k for k in range(5)}
                comp = [c for c in wide.index if not any((c, x) in fire_q for x in window)]
                yr = (q0 - 4).year
                per = (wide.loc[comp, a] - wide.loc[comp, b]) / [pop.get((c, yr), np.nan) / 1000 for c in comp]
                cache[q0] = float(per.median())
            else:
                cache[q0] = np.nan
        return cache[q0]

    rows = []
    for r in pieces[["event_id", "LGA_CODE21"]].itertuples(index=False):
        code, q0 = str(r.LGA_CODE21), pd.Timestamp(start[r.event_id]).to_period("Q")
        p = pop.get((code, q0.year - 1), np.nan)
        ch = change(code, q0)
        per = ch / (p / 1000) if p and not np.isnan(p) else np.nan
        pre = wide.at[code, q0 - 1] if code in wide.index and (q0 - 1) in wide.columns else np.nan
        rows.append(dict(event_id=r.event_id, region_id=code, SL_vulnerable_loss_raw=per,
                         SL_vulnerable_loss_excess=per - bench(q0), income_support_recipients_pre=pre,
                         income_support_per_1000_pre=pre / (p / 1000) if p and not np.isnan(p) else np.nan))
    out = pd.DataFrame(rows)
    out.to_parquet(DATA / "enrich/vulnerable.parquet")
    doc = {
        "SL_vulnerable_loss_excess": ("Rise in income-support recipients per 1,000 residents minus the median rise in NSW "
                                      "councils with no fire >= 100 ha in that window", "per 1,000", "DSS payments by LGA",
                                      "removes statewide shocks such as the 2020 COVID JobSeeker surge"),
        "income_support_recipients_pre": ("Working-age income-support recipients, quarter before the fire", "persons",
                                          "DSS payments by LGA", "definition in src/dss.py"),
        "income_support_per_1000_pre": ("Working-age income-support recipients per 1,000 residents, quarter before",
                                        "per 1,000", "DSS, ABS ERP", "a vulnerability indicator"),
    }
    (DATA / "enrich/vulnerable.doc.json").write_text(json.dumps(doc, indent=1))
    # council × year for the lga_year sheet (mean of the four quarters)
    ann = q.reset_index()
    ann["year"] = ann.quarter.dt.year
    ann = ann.groupby(["code21", "year"])[["income_support_total", "jobseeker_newstart"]].mean().reset_index()
    ann = ann.rename(columns={"code21": "region_id", "income_support_total": "income_support_recipients_mean",
                              "jobseeker_newstart": "jobseeker_newstart_recipients_mean"})
    (DATA / "enrich_lga").mkdir(exist_ok=True)
    ann.to_parquet(DATA / "enrich_lga/dss.parquet")
    for line in (DATA / "dss/urls.txt").read_text().splitlines():
        f, u = line.split("\t")
        record_source(f"DSS Payments by LGA: {f}", u, DATA / "dss" / f, "CC BY 4.0 (Department of Social Services)",
                      "quarterly recipients by payment type; values 1–4 randomised to 0/5 before Dec 2022, rounded to 5 after")
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    pieces = gpd.read_parquet(DATA / "cache/fire_lga_pieces.parquet")
    lga = socio_lga = gpd.read_file(socio.PHASE1 / "raw/lga_2021/LGA_2021_AUST_GDA94.shp")
    lga = lga[lga.STE_NAME21 == "New South Wales"]
    out = run(ev, pieces, lga)
    print(out.describe().T.round(2).to_string())
