"""NSW Office of Local Government (OLG) "Time Series Data" -> tidy council x financial-year table.

Source page: https://www.olg.nsw.gov.au/public/your-council-data-and-reports
Raw files (unchanged) live in data/olg/; their URLs are in URLS below and data/olg/urls.txt.

Layout of every yearly workbook used here: one sheet per year ("Councils" / "2016-17 DATA" ...),
one row per council, one column per indicator; the indicator label is the last non-blank header
cell above the first council row (Albury), footnotes sit below the council rows. County-council
sheets and the helper "Sheet1" tabs are skipped.

load() returns a long table: council_name, council_name_norm, fy_start, metric, value, source_file.
Rules: blanks / '-' / 'n/a' / 'Not collected' -> NaN (never 0); published numbers are kept as
published except (a) percentages published as fractions in some files are put back on the 0-100
scale (FRACTION_TO_PCT) and (b) revenue published in $'000 is converted to $ (read from the header).
Debt measures are kept separate (debt_service_cover_ratio, debt_service_ratio_pct); neither is
derived from the other. Grants & contributions % is kept as published, own-source is NOT derived from it.

Run as main to write data/olg/olg_long.parquet, olg_wide.parquet and urls.txt.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OLG = ROOT / "data/olg"
BASE = "https://www.olg.nsw.gov.au/sites/default/files/"
URLS = {f.rsplit("/", 1)[1]: BASE + f for f in [
    "2026-02/comparative-information-on-nsw-local-government-1994-2011-time-series-data.xls",
    "2026-02/time-series-data-1994-2015.xls",
    "2026-02/time-series-data-2011-12-2013-14.xlsx",
    "2026-02/time-series-data-2014-15_1.xls",
    "2026-02/time-series-data-2015-16.xls",
    "2026-02/time-series-data-2016-17.xls",
    "2026-02/time-series-data-2017-2018.xls",
    "2026-02/time-series-data-2018-2019.xlsx",
    "2026-02/time-series-data-2019-2020.xlsx",
    "2026-02/time-series-data-2020-2021.xlsx",
    "2026-02/time-series-data-2021-22.xlsx",
    "2026-02/time-series-data-2022-23.xlsx",
    "2026-02/time-series-data-2023-24.xlsx",
    "2026-05/time-series-data-2024-2025.xlsx",
]}

# (file, sheet) per fy_start. Primary = the stand-alone yearly file; the 1994-2015 compendium is a
# secondary copy of 2013-14 and 2014-15 (kept only when load(all_sources=True), used as a cross-check).
SHEETS = [
    (2013, "time-series-data-2011-12-2013-14.xlsx", "2013-14 Time Series Data ", True),
    (2013, "time-series-data-1994-2015.xls", "2013-14 DATA", False),
    (2014, "time-series-data-2014-15_1.xls", "2014-15 Time Series Data", True),
    (2014, "time-series-data-1994-2015.xls", "2014-15 DATA", False),
    (2015, "time-series-data-2015-16.xls", "2015-16 DATA", True),
    (2016, "time-series-data-2016-17.xls", "2016-17 DATA", True),
    (2017, "time-series-data-2017-2018.xls", "2017-18 DATA (Final)", True),
    (2018, "time-series-data-2018-2019.xlsx", "2018_19_Councils", True),
    (2019, "time-series-data-2019-2020.xlsx", "Councils", True),
    (2020, "time-series-data-2020-2021.xlsx", "Councils", True),
    (2021, "time-series-data-2021-22.xlsx", "Councils", True),
    (2022, "time-series-data-2022-23.xlsx", "Councils", True),
    (2023, "time-series-data-2023-24.xlsx", "Councils ", True),
    (2024, "time-series-data-2024-2025.xlsx", "Councils ", True),
]

# metric -> regex on the (lower-cased, whitespace-collapsed) indicator label
METRICS = {
    "cash_expense_cover_ratio_months": r"^cash expense cover ratio",
    "own_source_revenue_pct": r"^%? ?own source (operating )?revenue",
    "debt_service_cover_ratio": r"^debt service cover ratio",
    "debt_service_ratio_pct": r"^debt service ratio",
    "operating_performance_ratio_pct": r"^operating performance ratio",
    "unrestricted_current_ratio": r"^unrestricted current ratio",
    "building_infrastructure_renewals_ratio_pct": r"^building (&|and) infrastructure renewals? ratio",
    "infrastructure_backlog_ratio_pct": r"^infrastructure backlog ratio",
    "asset_maintenance_ratio_pct": r"^asset maintenance ratio",
    "grants_contributions_revenue_pct": r"^%? ?grants (& contributions )?revenue",
    "population": r"^population( \d{4})?$",
    "total_revenue_continuing_ops_aud": r"^(\d{4}/\d{2} )?total revenue from continuing operations",
    # spending by function ($, not the % or per-capita versions) -> budget crowd-out after a disaster
    "total_expenses_continuing_ops_aud": r"^total expenses from continuing operations",
    "net_operating_result_before_capital_aud": r"^net operating result before capital",
    "exp_governance_admin_aud": r"^total governance (&|and) administration expenditure",
    "exp_public_order_safety_health_aud": r"^total public order,? safety,? (&|and )?health,? expenditure(?!.*water)",
    "exp_environment_aud": r"^total environmental expenditure",
    "exp_community_services_housing_aud": r"^total community services,? education",
    "exp_recreation_culture_aud": r"^total recreational (&|and) cultural expenditure",
    "exp_roads_bridges_footpaths_aud": r"^total roads,? bridges (&|and) footpaths expenditure",
    "exp_other_services_aud": r"^total other services expenditure",
    "exp_water_aud": r"^total water expenditure(?! per capita)",
    "exp_sewer_aud": r"^total sewer expenditure(?! per capita)",
    # to 2017-18 OLG publishes public order, safety, health, water & sewer as one line; from 2018-19 as three
    # (wide() adds the combined line for later years as the sum of exp_public_order_safety_health, water, sewer)
    "exp_public_order_health_water_sewer_aud": r"^total public order,? safety,? health,? water (&|and) sewer expenditure",
}
# Percent metrics published as fractions (0.81 instead of 81). Decided from the column medians and
# checked against the prior year's file; see __main__ check. {fy_start: [metrics]}
FRACTION_TO_PCT = {
    2023: ["own_source_revenue_pct", "operating_performance_ratio_pct", "asset_maintenance_ratio_pct",
           "building_infrastructure_renewals_ratio_pct", "grants_contributions_revenue_pct"],
    2024: ["grants_contributions_revenue_pct"],
}
MISSING = {"", "-", "--", "n/a", "na", "n.a.", "nan", "not collected", "not available", "#n/a", "*"}
# words dropped only in council_name_norm (the published name is kept in council_name). 'the', 'of',
# 'city', 'municipality' are needed for the older long-form names ("The Council of the City of Botany Bay").
DROP_WORDS = r"\b(council|city|of|the|shire|municipal|municipality|regional)\b"


# Names that differ from the ABS LGA 2021 name after normalisation.
ALIASES = {"nambucca": "nambucca valley"}  # renamed Nambucca Valley Council (OLG file uses "Nambucca" to 2017-18)
# Pre-May-2016 councils (fy_start 2013-2014 only) -> the 2016 merged council / LGA 2021 name (normalised).
# Crosswalk only: values are NOT aggregated or imputed for the successor. Auburn and Holroyd were split
# (Cumberland + Parramatta); Parramatta, Hornsby, The Hills, Dubbo and Murrumbidgee keep their names
# across 2016 but their boundaries/entities changed, so their pre-2016 rows describe the old council.
PREDECESSORS = {
    "armidale dumaresq": "armidale", "guyra": "armidale",
    "ashfield": "inner west", "leichhardt": "inner west", "marrickville": "inner west",
    "auburn": "cumberland", "holroyd": "cumberland",
    "bankstown": "canterbury bankstown", "canterbury": "canterbury bankstown",
    "bombala": "snowy monaro", "cooma monaro": "snowy monaro", "snowy river": "snowy monaro",
    "boorowa": "hilltops", "harden": "hilltops", "young": "hilltops",
    "botany bay": "bayside", "rockdale": "bayside",
    "conargo": "edward river", "deniliquin": "edward river",
    "cootamundra": "cootamundra gundagai", "gundagai": "cootamundra gundagai",
    "corowa": "federation", "urana": "federation",
    "gloucester": "mid coast", "great lakes": "mid coast", "greater taree": "mid coast",
    "gosford": "central coast", "wyong": "central coast",
    "hurstville": "georges river", "kogarah": "georges river",
    "jerilderie": "murrumbidgee",
    "manly": "northern beaches", "pittwater": "northern beaches", "warringah": "northern beaches",
    "murray": "murray river", "wakool": "murray river",
    "palerang": "queanbeyan palerang", "queanbeyan": "queanbeyan palerang",
    "tumbarumba": "snowy valleys", "tumut": "snowy valleys",
    "wellington": "dubbo",
}


def _clean(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def norm_name(name):
    """Lower-case, drop 'council/city of/shire/municipal/regional/city', punctuation -> space."""
    s = _clean(name).lower().replace("&", " and ")
    s = re.sub(r"[#*]+", "", s)
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(DROP_WORDS, " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return ALIASES.get(s, s)


def to_float(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, (int, float, np.number)) and not isinstance(v, bool):
        return float(v)
    s = _clean(v).lower().replace(",", "").replace("$", "").replace("%", "")
    if s in MISSING or s.startswith("not collected"):
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def parse_sheet(fn, sheet, fy):
    raw = pd.read_excel(OLG / fn, sheet_name=sheet, header=None)
    first = raw[0].astype(str).str.contains("albury", case=False)
    r0 = int(first.idxmax())
    # council rows: from Albury down, col 1 (OLG group) populated -> excludes footnotes / blank rows
    body = raw.iloc[r0:]
    body = body[body[0].notna() & body[1].notna()]
    rows = []
    for c in range(2, raw.shape[1]):
        hdr = [_clean(v) for v in raw.iloc[:r0, c] if pd.notna(v) and _clean(v)]
        if not hdr:
            continue
        label = hdr[-1]
        lab = label.lower()
        yr = re.search(r"(\d{4})/(\d{2})", label)  # multi-year files: keep only this file's own year
        if yr and int(yr.group(1)) != fy and not lab.startswith("typical"):
            continue
        for m, rx in METRICS.items():
            if re.search(rx, lab):
                break
        else:
            continue
        vals = body[c].map(to_float)
        bad = body[c][vals.isna() & body[c].notna()].map(_clean)
        bad = bad[~bad.str.lower().isin(MISSING) & ~bad.str.lower().str.startswith("not collected")]
        if len(bad):
            print(f"[olg] {fn}:{m}: {len(bad)} unparsed text cells -> NaN, e.g. {bad.unique()[:3].tolist()}")
        if m.endswith("_aud") and re.search(r"\$\s*['’,]?\s*'?000", label):
            vals = vals * 1000.0
        if m in FRACTION_TO_PCT.get(fy, []):
            vals = vals * 100.0
        rows.append(pd.DataFrame({"council_name": body[0].map(_clean).values, "fy_start": fy, "metric": m,
                                  "value": vals.values, "label": label, "source_file": fn,
                                  "source_sheet": _clean(sheet)}))
    df = pd.concat(rows, ignore_index=True)
    if df.duplicated(["council_name", "metric"]).any():
        raise ValueError(f"duplicate council/metric in {fn}:{sheet}")
    return df


def load(all_sources=False, keep_label=False):
    """Long tidy table for fy_start 2013..2024 (one row per council x fy x metric).

    all_sources=True also returns the secondary 1994-2015 compendium copies of 2013-14/2014-15.
    """
    parts = [parse_sheet(fn, sh, fy).assign(primary=prim) for fy, fn, sh, prim in SHEETS
             if all_sources or prim]
    df = pd.concat(parts, ignore_index=True)
    df.insert(1, "council_name_norm", df["council_name"].map(norm_name))
    cols = ["council_name", "council_name_norm", "fy_start", "metric", "value", "source_file"]
    if keep_label:
        cols += ["label", "source_sheet"]
    if all_sources:
        cols += ["primary"]
    return df[cols].sort_values(["council_name_norm", "fy_start", "metric"]).reset_index(drop=True)


def wide(long):
    """council x fy_start, one column per metric (primary sources only; only council-years that exist)."""
    if "primary" in long:
        long = long[long["primary"]]
    w = long.pivot(index=["council_name_norm", "fy_start"], columns="metric", values="value")
    names = long.groupby(["council_name_norm", "fy_start"])["council_name"].first()
    w = w.join(names).reset_index()
    parts = ["exp_public_order_safety_health_aud", "exp_water_aud", "exp_sewer_aud"]
    if all(p in w for p in parts):
        comb = w[parts].sum(axis=1, min_count=1)  # water/sewer blank for councils without those services
        w["exp_public_order_health_water_sewer_aud"] = w.get("exp_public_order_health_water_sewer_aud",
                                                             pd.Series(np.nan, index=w.index)).fillna(
            comb.where(w.exp_public_order_safety_health_aud.notna()))
    # normalised LGA-2021 name this row belongs to (predecessors -> successor; for joining, not aggregating)
    w["successor_lga21_norm"] = w["council_name_norm"].map(lambda n: PREDECESSORS.get(n, n))
    return w[["council_name", "council_name_norm", "successor_lga21_norm", "fy_start"]
             + [m for m in METRICS if m in w]]


if __name__ == "__main__":
    long = load()
    long.to_parquet(OLG / "olg_long.parquet", index=False)
    w = wide(long)
    w.to_parquet(OLG / "olg_wide.parquet", index=False)
    with open(OLG / "urls.txt", "w") as f:
        for k, u in URLS.items():
            f.write(f"{k}\t{u}\n")
    print("long", long.shape, "wide", w.shape)
    key = ["cash_expense_cover_ratio_months", "own_source_revenue_pct", "debt_service_cover_ratio",
           "debt_service_ratio_pct"]
    print(w.groupby("fy_start")[key].count().assign(councils=w.groupby("fy_start").size()))
