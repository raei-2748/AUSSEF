"""ABS Counts of Australian Businesses, including Entries and Exits (CABEE, cat. 8165.0)
-> tidy NSW LGA x June-year table of business counts.

Source: the LGA data cubes of each CABEE release ("Businesses by industry division by Local Government
Area (LGA) by employment size ranges" = data cube 10; the turnover-size cube 11 is kept raw and only used
as a cross-check). Raw files (unchanged) are in data/cabee/, URLs in data/cabee/urls.txt.

Each release publishes 3 June stocks by LGA ("operating at 30 June"), e.g. the Jul2021-Jun2025 release
has June 2023, 2024, 2025. For each year the MOST RECENT release that publishes it is used (later releases
revise; see RELEASES). Result: June 2015 - June 2025. LGA cubes were first published in the Jun2013-Jun2017
release (so no June 2013/2014 by LGA), and the June 2026 LGA cube is scheduled for December 2026 (the
Jul2022-Jun2026 release only has data cube 1 at the time of writing).

Sheet layout (all releases): title rows 0-4 (row 3 = table title incl. "June YYYY"), header rows 5-6
(State | LGA Code | LGA Label | Industry Code | Industry Label | <size ranges> | Total), data from row 7,
footnotes below. One block of rows per LGA: 19 ANZSIC divisions (A-S) + X "Currently Unknown" + an LGA
total row (industry code blank; older releases put "Total <LGA>" in the LGA label, newer ones "Total" in the
industry label). Releases from Jul2016-Jun2020 contain both "Annualised" and "(Experimental) Point in Time"
employment-size tables; only the Annualised (= historical-consistent) tables are used; the business totals
are identical in both.

Measures (all from the LGA total row unless stated):
  businesses_total            'Total' column
  businesses_non_employing    'Non employing' column
  businesses_employing        DERIVED: sum of the published employing size-range cells (1-19 / 1-4 + 5-19,
                              20-199, 200+). Cells are perturbed, so this need not equal total - non-employing.
  businesses_emp_1_19, businesses_emp_1_4, businesses_emp_5_19, businesses_emp_20_199, businesses_emp_200_plus
                              published size-range columns (1-19 split into 1-4 / 5-19 from the Jul2018-Jun2022
                              release on; the combined 1-19 is not derived).
  businesses_<division>       'Total' column of each industry-division row (snake_case of published label).
Values: published numbers as float; blanks / 'np' / '-' / 's' etc. -> NaN (never 0). Published zeros stay 0.
Note ABS perturbation: all LGA cells, including LGA totals, may be perturbed (only national/state/division
totals are not), so components need not add up.

load(all_releases=False) returns long: lga_code, lga_name, lga_boundary_vintage, year, measure, value, release.
Run as main -> data/cabee/cabee_lga_year.parquet (wide: one column per measure).
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CABEE = ROOT / "data/cabee"
STATE = "New South Wales"

# release -> (LGA employment-size cube file, boundary vintage note). Order: newest first.
# Vintages from the CABEE methodology "History of changes" (all years in a release are allocated to that
# release's boundaries) and the LGA code/label style in the cube.
RELEASES = {
    "jul2021-jun2025": ("jul2021-jun2025_8165DC10.xlsx", "LGA 2025 (ASGS Ed. 3 annual LGA update)"),
    "jul2020-jun2024": ("jul2020-jun2024_8165DC10.xlsx", "LGA 2024 (ASGS Ed. 3 annual LGA update)"),
    "jul2019-jun2023": ("jul2019-jun2023_8165DC10_revised.xlsx", "LGA 2023 (ASGS Ed. 3 annual LGA update)"),
    "jul2018-jun2022": ("jul2018-jun2022_816510.xlsx", "LGA 2022 (ASGS Ed. 3 annual LGA update)"),
    "jul2017-jun2021": ("jul2017-jun2021_8165010.xlsx", "LGA 2021 (ASGS Ed. 3)"),
    "jul2016-jun2020": ("jul2016-jun2020_816510.xls", "LGA 2020 (ASGS 2016 LGA update)"),
    "jul2015-jun2019": ("jul2015-jun2019_816510.xls", "LGA 2018/2019 (ASGS 2016; not stated, NSW codes = LGA 2018)"),
    "jun2014-jun2018": ("jun2014-jun2018_8165010.xls", "LGA 2018 (ASGS 2016 LGA update)"),
    "jun2013-jun2017": ("jun2013-jun2017_8165010.xls", "LGA 2016 (ASGS 2016)"),
}
TURNOVER_CUBES = {
    "jul2021-jun2025": "jul2021-jun2025_8165DC11.xlsx", "jul2020-jun2024": "jul2020-jun2024_8165DC11.xlsx",
    "jul2019-jun2023": "jul2019-jun2023_8165DC11_revised.xlsx", "jul2018-jun2022": "jul2018-jun2022_816511.xlsx",
    "jul2017-jun2021": "jul2017-jun2021_8165011.xlsx", "jul2016-jun2020": "jul2016-jun2020_816511.xls",
    "jul2015-jun2019": "jul2015-jun2019_816511.xls", "jun2014-jun2018": "jun2014-jun2018_8165011.xls",
    "jun2013-jun2017": "jun2013-jun2017_8165011.xls",
}
# Published NSW LGA codes that differ from ASGS LGA 2021 codes (same council; code changed only).
# 10130/14200 appear in releases up to Jul2015-Jun2019 (June 2015-2017 of the spliced series), 13510/18230
# (pre-2017 names Gundagai / Western Plains Regional) only in Jun2013-Jun2017 (June 2015). Not applied in load().
CODE_TO_LGA2021 = {"10130": "10180", "14200": "14220", "13510": "12160", "18230": "12390"}
# Non-council NSW rows kept in the output: 19399 Unincorporated NSW, 19499 No usual address (NSW).
NON_COUNCIL_CODES = {"19399", "19499"}
SKIP_SHEETS = {"About", "Contents", "Disclaimer", "Further information", "Explanatory Notes"}
SIZE_COLS = {  # published header -> measure
    "Non employing": "businesses_non_employing",
    "1-19 Employees": "businesses_emp_1_19",
    "1-4 Employees": "businesses_emp_1_4",
    "5-19 Employees": "businesses_emp_5_19",
    "20-199 Employees": "businesses_emp_20_199",
    "200+ Employees": "businesses_emp_200_plus",
}


def snake(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def to_num(v) -> float:
    """Published cell -> float; anything non-numeric (blank, 'np', '-', 's', ...) -> NaN, never 0."""
    if isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool):
        return float(v)
    if isinstance(v, str):
        t = v.strip().replace(",", "")
        if re.fullmatch(r"-?\d+(\.\d+)?", t):
            return float(t)
    return np.nan


def _tables(path: Path):
    """Yield (year, DataFrame-with-header) for every Annualised / plain employment-size LGA table."""
    x = pd.ExcelFile(path)
    for sh in x.sheet_names:
        if sh in SKIP_SHEETS:
            continue
        raw = x.parse(sh, header=None, dtype=object)
        title = next(str(v) for v in raw.iloc[:6, 0] if isinstance(v, str) and "Local Government Area" in v)
        if "Point in Time" in title:
            continue
        year = int(re.search(r"June (\d{4})", title).group(1))
        hdr = next(i for i in range(12) if str(raw.iat[i, 0]).strip() == "State")
        cols = [str(c).strip() for c in raw.iloc[hdr]]
        body = raw.iloc[hdr + 2:].copy()
        body.columns = ["state", "lga_code", "lga_label", "ind_code", "ind_label"] + cols[5:]
        yield year, title, body


def parse_release(release: str) -> pd.DataFrame:
    fname, vintage = RELEASES[release]
    out = []
    for year, _title, b in _tables(CABEE / fname):
        b = b[b["state"] == STATE].copy()
        b["lga_code"] = b["lga_code"].map(lambda v: str(int(v)) if pd.notna(v) else None)
        lab = b["lga_label"].astype(str).str.strip()
        is_total = b["ind_code"].isna() & ((b["ind_label"].astype(str).str.strip() == "Total")
                                           | lab.str.startswith("Total "))
        b["lga_name"] = lab.str.replace(r"^Total ", "", regex=True)
        # Raw-file defect: in jun2013-jun2017 'June 2015' the Balranald (A) block has LGA codes 10300..10320
        # (auto-filled). Within a contiguous block of one LGA name, the code of the block's first row is used.
        block = (b["lga_name"] != b["lga_name"].shift()).cumsum()
        first = b.groupby(block)["lga_code"].transform("first")
        if (first != b["lga_code"]).any():
            bad = sorted(b.loc[first != b["lga_code"], "lga_name"].unique())
            print(f"[cabee] {release} June {year}: repaired LGA codes within block(s) {bad}")
            b["lga_code"] = first
        size_cols = [c for c in b.columns if c in SIZE_COLS]
        emp_cols = [c for c in size_cols if c != "Non employing"]
        unknown = [c for c in b.columns[5:] if c not in SIZE_COLS and c not in ("Total", "lga_name")]
        assert not unknown, (release, year, unknown)
        tot = b[is_total]
        for _, r in tot.iterrows():
            base = dict(lga_code=r["lga_code"], lga_name=r["lga_name"], year=year)
            out.append({**base, "measure": "businesses_total", "value": to_num(r["Total"])})
            for c in size_cols:
                out.append({**base, "measure": SIZE_COLS[c], "value": to_num(r[c])})
            vals = [to_num(r[c]) for c in emp_cols]
            out.append({**base, "measure": "businesses_employing",
                        "value": float(np.sum(vals)) if not any(np.isnan(vals)) else np.nan})
        div = b[b["ind_code"].notna()]
        for _, r in div.iterrows():
            out.append(dict(lga_code=r["lga_code"], lga_name=r["lga_name"], year=year,
                            measure="businesses_" + snake(str(r["ind_label"])), value=to_num(r["Total"])))
        # sanity: one total row per LGA, 20 division rows per LGA
        assert tot["lga_code"].is_unique, (release, year)
        assert (div.groupby("lga_code").size() == 20).all(), (release, year)
    df = pd.DataFrame(out)
    df["lga_boundary_vintage"] = vintage
    df["release"] = release
    return df


def load(all_releases: bool = False) -> pd.DataFrame:
    """Long NSW table. Default: each June year taken from the most recent release publishing it."""
    df = pd.concat([parse_release(r) for r in RELEASES], ignore_index=True)
    if not all_releases:
        order = {r: i for i, r in enumerate(RELEASES)}  # 0 = newest
        best = df.groupby("year")["release"].agg(lambda s: min(s.unique(), key=order.get))
        df = df[df["release"] == df["year"].map(best)]
    cols = ["lga_code", "lga_name", "lga_boundary_vintage", "year", "measure", "value", "release"]
    return df[cols].sort_values(["year", "lga_code", "measure"]).reset_index(drop=True)


def turnover_totals(release: str) -> pd.DataFrame:
    """LGA 'Total' column from the turnover-size cube (cross-check only)."""
    rows = []
    for year, _t, b in _tables(CABEE / TURNOVER_CUBES[release]):
        b = b[b["state"] == STATE]
        lab = b["lga_label"].astype(str).str.strip()
        tot = b[b["ind_code"].isna() & ((b["ind_label"].astype(str).str.strip() == "Total")
                                        | lab.str.startswith("Total "))]
        for _, r in tot.iterrows():
            rows.append(dict(lga_code=str(int(r["lga_code"])), year=year, total_turnover_cube=to_num(r["Total"])))
    return pd.DataFrame(rows)


def wide(long: pd.DataFrame) -> pd.DataFrame:
    idx = ["lga_code", "lga_name", "lga_boundary_vintage", "year", "release"]
    w = long.set_index(idx + ["measure"])["value"].unstack("measure").reset_index()
    w.columns.name = None
    lead = idx + ["businesses_total", "businesses_employing", "businesses_non_employing"]
    return w[lead + [c for c in w.columns if c not in lead]].sort_values(["lga_code", "year"]).reset_index(drop=True)


if __name__ == "__main__":
    long = load()
    w = wide(long)
    out = CABEE / "cabee_lga_year.parquet"
    w.to_parquet(out, index=False)
    print(f"long rows={len(long)}  wide rows={len(w)} cols={w.shape[1]} -> {out}")
    print(w.groupby(["year", "release", "lga_boundary_vintage"]).agg(
        n_lga=("lga_code", "nunique"), n_total=("businesses_total", "count"),
        nsw_sum=("businesses_total", "sum")).to_string())
