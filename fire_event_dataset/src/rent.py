"""SL_rent_change: rise in median weekly rent for new bonds after a fire (NSW DCJ Rent and Sales Report, by LGA).

When homes burn, fewer are left to rent and rents rise; Akter & Grafton (2025, One Earth) find rents rose about A$20 a
week in Black Summer burnt areas. Measure: median weekly rent for new bonds (all dwellings, all bedroom counts) in the
quarter after the fire-start quarter vs the same quarter a year earlier, in %. Where the year-earlier quarterly file is
not on disk (before September 2017), the DCJ-published annual change of the later quarter is used (`rent_change_basis`).
An `_excess` version subtracts the median change in NSW councils with no fire >= 100 ha in that window (as in
src/vulnerable.py).

Raw files (unchanged) are in data/rent/, URLs in data/rent/urls.txt. One file per quarter, September 2017 to June 2026.
The June 2017 file has a different layout and no council totals by dwelling type; it is kept but not parsed. Earlier
issues were published only as PDF reports. DCJ blanks a council's median when 10 or fewer bonds were lodged ('-'); that
stays blank, never 0.
"""
import json
import re

import geopandas as gpd
import numpy as np
import pandas as pd

from src import socio
from src.common import DATA, record_source

RENT = DATA / "rent"
COMPARE_HA = 100
MONTHS = {"mar": 1, "jun": 2, "sep": 3, "dec": 4}
# DCJ council names that differ from the ABS LGA 2021 name after socio.norm()
ALIASES = {"gundagai": "cootamundragundagai", "nambucca": "nambuccavalley", "westernplains": "dubbo",
           "gleninnes": "gleninnessevern"}
COLS = {"local government area": "lga", "lga (local government": "lga", "dwelling types": "dwelling_type",
        "bedroom": "bedrooms", "median weekly rent": "median_rent", "new bonds lodged": "new_bonds",
        "total bonds held": "bonds_held", "annual change in median": "annual_change_published"}


def quarter_of(fname):
    m = re.search(r"(mar|jun|sep|dec)[a-z]*[_-](20\d\d)", fname.lower())
    return pd.Period(year=int(m.group(2)), quarter=MONTHS[m.group(1)], freq="Q") if m else None


def parse(path):
    d = pd.read_excel(path, sheet_name="LGA", header=None)
    h = int(d.index[d.apply(lambda r: r.astype(str).str.contains("Median Weekly Rent", case=False).any(), axis=1)][0])
    names = {}
    for i, v in enumerate(d.iloc[h]):
        lab = re.sub(r"\s+", " ", str(v)).strip().lower()
        for k, c in COLS.items():
            if k in lab and c not in names.values():  # first matching column wins
                names[i] = c
                break
    b = d.iloc[h + 1:, list(names)].set_axis(list(names.values()), axis=1)
    b = b[(b.dwelling_type == "Total") & (b.bedrooms == "Total") & (b.lga != "Total") & b.lga.notna()]
    b = b.drop_duplicates("lga")  # councils repeat under each region breakdown with identical values
    out = pd.DataFrame({"lga_name": b.lga.astype(str).str.strip()})
    for c in ("median_rent", "new_bonds", "bonds_held"):
        out[c] = pd.to_numeric(b[c].astype(str).str.replace(",", ""), errors="coerce") if c in b else np.nan
    if "annual_change_published" in b:
        s = b.annual_change_published.astype(str).str.strip()
        pct = s.str.endswith("%")
        v = pd.to_numeric(s.str.rstrip("%"), errors="coerce")
        out["annual_change_published_pct"] = np.where(pct, v, v * 100)  # older files store fractions
    else:
        out["annual_change_published_pct"] = np.nan
    return out


def council_quarter(lga):
    cached = RENT / "rent_lga_quarter.parquet"
    srcs = [RENT / line.split("\t")[0] for line in (RENT / "urls.txt").read_text().splitlines()]
    if cached.exists() and cached.stat().st_mtime > max(p.stat().st_mtime for p in srcs + [RENT / "urls.txt"]):
        return pd.read_parquet(cached)  # parsing 36 workbooks takes minutes; reuse unless a file changed
    names = {socio.norm(n): str(c) for c, n in zip(lga.LGA_CODE21, lga.LGA_NAME21)}
    parts = []
    for line in (RENT / "urls.txt").read_text().splitlines():
        f = line.split("\t")[0]
        q = quarter_of(f)
        if q is None or q < pd.Period("2017Q3", freq="Q"):
            continue
        t = parse(RENT / f)
        k = t.lga_name.map(socio.norm)
        t["region_id"] = k.map(lambda x: names.get(ALIASES.get(x, x)))
        bad = t.lga_name[t.region_id.isna()].tolist()
        if bad:
            print(f"[rent] {f}: unmatched councils {bad}")
        parts.append(t.dropna(subset=["region_id"]).assign(quarter=q, source_file=f))
    d = pd.concat(parts, ignore_index=True)
    assert not d.duplicated(["region_id", "quarter"]).any(), "two rows for one council-quarter"
    d.to_parquet(RENT / "rent_lga_quarter.parquet", index=False)
    return d


def run(ev, pieces, lga):
    d = council_quarter(lga)
    med = d.pivot(index="region_id", columns="quarter", values="median_rent")
    pub = d.pivot(index="region_id", columns="quarter", values="annual_change_published_pct")
    start = ev.set_index("event_id").start
    big = pieces[pieces.region_burn_area_ha >= COMPARE_HA]
    fire_q = set(zip(big.LGA_CODE21.astype(str), big.event_id.map(start).dt.to_period("Q")))

    def change(code, q0):
        a, b = q0 + 1, q0 - 3
        if code in med.index and a in med.columns and b in med.columns:
            if pd.notna(med.at[code, a]) and pd.notna(med.at[code, b]):
                return (med.at[code, a] - med.at[code, b]) / med.at[code, b] * 100, "levels"
            return np.nan, ""
        if code in pub.index and a in pub.columns and pd.notna(pub.at[code, a]):
            return pub.at[code, a], "DCJ published annual change"
        return np.nan, ""

    cache = {}

    def bench(q0):
        if q0 not in cache:
            window = {q0 - 3 + k for k in range(5)}
            comp = [c for c in med.index if not any((c, x) in fire_q for x in window)]
            vals = [change(c, q0)[0] for c in comp]
            cache[q0] = float(np.nanmedian(vals)) if np.isfinite(vals).any() else np.nan
        return cache[q0]

    rows = []
    for r in pieces[["event_id", "LGA_CODE21"]].itertuples(index=False):
        code, q0 = str(r.LGA_CODE21), pd.Timestamp(start[r.event_id]).to_period("Q")
        ch, basis = change(code, q0)
        pre = med.at[code, q0 - 1] if code in med.index and (q0 - 1) in med.columns else np.nan
        rows.append(dict(event_id=r.event_id, region_id=code, rent_median_weekly_pre=pre, SL_rent_change_pct=ch,
                         SL_rent_change_excess_pct=ch - bench(q0) if np.isfinite(ch) else np.nan,
                         rent_change_basis=basis or np.nan))
    out = pd.DataFrame(rows)
    out.to_parquet(DATA / "enrich/rent.parquet")
    src = "NSW DCJ Rent and Sales Report (new bonds, by LGA)"
    doc = {
        "rent_median_weekly_pre": ("Median weekly rent for new bonds, quarter before the fire", "AUD/week", src,
                                   "all dwellings; blank when 10 or fewer bonds lodged"),
        "SL_rent_change_pct": ("Median weekly rent change: quarter after the fire-start quarter vs the same quarter a "
                               "year earlier", "%", src, "fires from mid-2017; see rent_change_basis"),
        "SL_rent_change_excess_pct": ("As above minus the median change in NSW councils with no fire >= 100 ha in that "
                                      "window", "%", src, "positive = rents rose faster than in comparison councils"),
        "rent_change_basis": ("How the rent change was computed", "str", src,
                              "levels = from the two quarterly files; otherwise DCJ's published annual change"),
    }
    (DATA / "enrich/rent.doc.json").write_text(json.dumps(doc, indent=1))

    # annual values only when all four quarters are published: DCJ suppresses small counts ("s"), and the files start
    # in the September 2017 quarter, so a partial year (or a sum of blanks) would be mislabelled as a full year
    def full_year(f):
        return lambda s: f(s) if s.notna().sum() == 4 else np.nan
    ann = d.assign(year=d.quarter.dt.year).groupby(["region_id", "year"]).agg(
        rent_median_weekly_mean=("median_rent", full_year(pd.Series.mean)),
        rent_new_bonds_lodged=("new_bonds", full_year(pd.Series.sum))).reset_index()
    (DATA / "enrich_lga").mkdir(exist_ok=True)
    ann.to_parquet(DATA / "enrich_lga/rent.parquet", index=False)
    for line in (RENT / "urls.txt").read_text().splitlines():
        f, u = line.split("\t")
        record_source(f"NSW DCJ Rent and Sales Report: {f}", u, RENT / f, "CC BY 4.0 (NSW Department of Communities "
                      "and Justice)", "quarterly rents for new bonds by LGA" + ("" if quarter_of(f) and quarter_of(f) >=
                      pd.Period("2017Q3", freq="Q") else "; different layout, not parsed"))
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    pieces = gpd.read_parquet(DATA / "cache/fire_lga_pieces.parquet")
    lga = gpd.read_file(socio.PHASE1 / "raw/lga_2021/LGA_2021_AUST_GDA94.shp")
    lga = lga[lga.STE_NAME21 == "New South Wales"]
    out = run(ev, pieces, lga)
    print(out.notna().mean().round(3).to_string())
    print(out.rent_change_basis.value_counts(dropna=False))
    print(out[["SL_rent_change_pct", "SL_rent_change_excess_pct"]].describe().round(2))
