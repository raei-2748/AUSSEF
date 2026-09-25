"""IL business-activity proxy: change in the number of businesses in the council (ABS CABEE, src/cabee.py).

For a fire in the financial year ending June Y: % change in businesses operating at 30 June, June Y−1 → June Y
(`IL_business_count_change_pct`) and June Y−1 → June Y+1 (`..._plus1_pct`). ABS revises earlier years between
releases (sometimes heavily for small councils), so both years always come from the SAME release: the latest one
that contains both. `_excess` subtracts the median change, in that release, of NSW councils with no fire >= 100 ha
in the same window. Council counts carry ABS confidentiality noise; small councils are noisy.
"""
import json

import geopandas as gpd
import numpy as np
import pandas as pd

from src import cabee
from src.common import DATA, record_source

COMPARE_HA = 100


def _fy_end(ts):
    ts = pd.Timestamp(ts)
    return ts.year + 1 if ts.month >= 7 else ts.year


def run(ev, pieces):
    L = cabee.load(all_releases=True)
    L = L[L.measure == "businesses_total"].copy()
    L["code"] = L.lga_code.astype(str).replace(cabee.CODE_TO_LGA2021)
    tab = L.groupby(["release", "year", "code"]).value.first()
    rel_years = L.groupby("release").year.agg(["min", "max"])
    start = ev.set_index("event_id").start
    big = pieces[pieces.region_burn_area_ha >= COMPARE_HA]
    fire_fy = set(zip(big.LGA_CODE21.astype(str), big.event_id.map(start).map(_fy_end)))

    def release_for(y0, y1):
        ok = rel_years[(rel_years["min"] <= y0) & (rel_years["max"] >= y1)]
        return ok.index[-1] if len(ok) else None  # releases sort chronologically by name within each era

    order = sorted(rel_years.index, key=lambda r: rel_years.loc[r, "max"])
    rel_years = rel_years.loc[order]
    bench_cache = {}

    def change(rel, y0, y1, code):
        try:
            a, b = tab[(rel, y1, code)], tab[(rel, y0, code)]
        except KeyError:
            return np.nan
        return (a - b) / b * 100 if b else np.nan

    def bench(rel, y0, y1, fy):
        k = (rel, y0, y1)
        if k not in bench_cache:
            codes = tab.loc[rel].index.get_level_values("code").unique()
            comp = [c for c in codes if c.startswith("1") and not any((c, fy + j) in fire_fy for j in range(0, y1 - fy + 1))]
            bench_cache[k] = float(np.nanmedian([change(rel, y0, y1, c) for c in comp])) if comp else np.nan
        return bench_cache[k]

    rows = []
    for r in pieces[["event_id", "LGA_CODE21"]].itertuples(index=False):
        code, fy = str(r.LGA_CODE21), _fy_end(start[r.event_id])
        row = dict(event_id=r.event_id, region_id=code)
        for lag, lab in ((0, ""), (1, "_plus1")):
            y0, y1 = fy - 1, fy + lag
            rel = release_for(y0, y1)
            if rel is None:
                continue
            ch = change(rel, y0, y1, code)
            row[f"IL_business_count_change{lab}_pct"] = ch
            row[f"IL_business_count_change{lab}_excess_pct"] = ch - bench(rel, y0, y1, fy)
            if lag == 0:
                row["businesses_total_pre"] = tab.get((rel, y0, code), np.nan)
                row["business_count_release"] = rel
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_parquet(DATA / "enrich/business.parquet")
    doc = {
        "IL_business_count_change_pct": ("% change in businesses operating, June before the fire FY → June at its end",
                                         "%", "ABS CABEE (8165.0)", "both years from the same ABS release"),
        "IL_business_count_change_excess_pct": ("As above minus the median change in NSW councils with no fire >= 100 ha",
                                                "%", "ABS CABEE", "comparison within the same release"),
        "IL_business_count_change_plus1_pct": ("% change in businesses, June before the fire FY → June a year later", "%",
                                               "ABS CABEE", "lagged"),
        "IL_business_count_change_plus1_excess_pct": ("As above minus comparison-council median", "%", "ABS CABEE", "lagged"),
        "businesses_total_pre": ("Businesses operating in the council, June before the fire FY", "count", "ABS CABEE",
                                 "size of the local business economy (regional GDP proxy)"),
        "business_count_release": ("ABS CABEE release used", "str", "ABS", ""),
    }
    (DATA / "enrich/business.doc.json").write_text(json.dumps(doc, indent=1))
    w = pd.read_parquet(DATA / "cabee/cabee_lga_year.parquet")
    w["region_id"] = w.lga_code.astype(str).replace(cabee.CODE_TO_LGA2021)
    keep = ["region_id", "year", "businesses_total", "businesses_non_employing"]
    (DATA / "enrich_lga").mkdir(exist_ok=True)
    w[[c for c in keep if c in w]].rename(columns={"businesses_total": "businesses_total_june",
                                                   "businesses_non_employing": "businesses_non_employing_june"}
                                          ).to_parquet(DATA / "enrich_lga/business.parquet")
    for line in (DATA / "cabee/urls.txt").read_text().splitlines():
        f, u = line.split("\t")
        record_source(f"ABS CABEE by LGA: {f}", u, DATA / "cabee" / f, "CC BY 4.0 (ABS)", "businesses at 30 June by LGA")
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    pieces = gpd.read_parquet(DATA / "cache/fire_lga_pieces.parquet")
    out = run(ev, pieces)
    print(out.describe().T.round(2).to_string())
