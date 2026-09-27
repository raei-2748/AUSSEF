"""Indirect-loss (IL) sector variables by NSW LGA and year: industry/size business counts, business entries and exits,
employee jobs by industry, business-related insolvencies, employee and own-business income, and (where published as
data) tourism visitation. Long format, no modelling.

Sources (raw files unchanged; URLs in data/raw/il/urls.txt, data/cabee/urls.txt):

1. ABS Counts of Australian Businesses (CABEE, 8165.0), LGA data cubes (already on disk for src/cabee.py):
   - DC10 "Businesses by industry division by LGA by employment size ranges": every division (A-S, X) x size cell
     (non-employing, 1-19 [releases to Jul2017-Jun2021] or 1-4 / 5-19 [from Jul2018-Jun2022], 20-199, 200+, total),
     plus the LGA total row. 30 June stocks, June 2015 - June 2025.
   - DC11 "... by turnover size ranges": LGA total row and selected divisions (KEY_TURNOVER_DIVS) x turnover band.
   Each June is taken from the most recent release that publishes it (as src/cabee.py). Parsing reuses
   src.cabee._tables / to_num. ABS perturbs LGA cells, so components need not add to totals.
   CABEE LGA cubes contain stocks only: no entries/exits by LGA (entries/exits by region come from Data by Region).
2. ABS Data by Region (14100DO0003 / 0004 / 0005), Table 2 = Local Government Areas (LGA 2020 in the 2015-20 release,
   LGA 2021 in 2011-22 .. 2011-25; NSW codes are identical to LGA 2021):
   - business entries and exits by employment size and by turnover band, year ended 30 June 2017-2024
     (CABEE-based; the 2011-25 release dropped them, so FY2024-25 is not published by LGA);
   - Jobs in Australia: jobs, employee jobs by ANZSIC division, year ended 30 June 2015-2023;
   - debtors entering business-related / all personal insolvencies (AFSA), FY2015-2021, and business-related
     insolvencies caused by economic conditions FY2015-2019 (2015-20 release only);
   - Personal Income in Australia: employee income and own unincorporated business income, FY2015-2023.
   Each (variable, year) is taken from the most recent release in which it has any NSW value.
3. Tourism Research Australia (TRA) Local Government Area Profiles 2017 (4-year average 2014-2017), one workbook per
   LGA, recovered from the Internet Archive (the TRA site no longer hosts them). Only LGAs with enough IVS/NVS sample
   have a profile. The 2019 (2016-19 average) and 2024 (2-year average) profiles are published only as Power BI
   dashboards, i.e. not as downloadable data, so they are not used.

Values: published numbers as float; '-', 'np', blanks -> NaN (never 0). DBR '-' means "not available, not available for
publication, nil or rounded to zero" - it is kept blank. Derived values are marked in `derived` and named *_sum.

Writes data/enrich/il_sector.parquet (+ .csv): region_id, period, period_start, period_end, variable, value, unit,
source (URL), source_file, sheet, release, derived, note. Also data/enrich/il_sector_all_releases.parquet (every
release, for within-release changes) and data/enrich/il_sector.doc.json.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from src import cabee
from src.cabee import to_num
from src.common import DATA, ROOT, record_source

RAW = DATA / "raw/il"
TRA_DIR = RAW / "tra_lga_2017"
ENRICH = DATA / "enrich"
STATE = "New South Wales"
ABS_LIC = "CC BY 4.0 (ABS)"
DBR_RELEASES = ["2011-25", "2011-24", "2011-23", "2011-22", "2015-20"]  # newest first
KEY_TURNOVER_DIVS = {"A", "E", "G", "H", "I", "R"}  # agriculture, construction, retail, accommodation & food,
# transport, arts & recreation
EMP_BANDS = {"Non employing": "non_employing", "1-19 Employees": "emp_1_19", "1-4 Employees": "emp_1_4",
             "5-19 Employees": "emp_5_19", "20-199 Employees": "emp_20_199", "200+ Employees": "emp_200_plus",
             "Total": "total"}
TO_BANDS = {"Zero to less than $50k": "to_0_50k", "$50k to less than $200k": "to_50k_200k",
            "$200k to less than $2m": "to_200k_2m", "$2m to less than $5m": "to_2m_5m",
            "$5m to less than $10m": "to_5m_10m", "$10m or more": "to_10m_plus", "Total": "total"}


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def urls(path: Path) -> dict:
    return dict(line.split("\t") for line in path.read_text().splitlines() if "\t" in line)


def june(y):
    return dict(period=f"{y}-06-30", period_start=f"{y}-06-30", period_end=f"{y}-06-30")


def fy(y):
    return dict(period=f"FY{y - 1}-{str(y)[2:]}", period_start=f"{y - 1}-07-01", period_end=f"{y}-06-30")


# ----------------------------------------------------------------------------------------------------------------- CABEE
def _tables(path: Path):
    """As src.cabee._tables, but also yields the sheet name: (year, sheet, title, body)."""
    x = pd.ExcelFile(path)
    for sh in x.sheet_names:
        if sh in cabee.SKIP_SHEETS:
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
        yield year, sh, title, body


def _cabee_blocks(fname):
    """Yield (year, sheet, NSW body with lga_code/lga_name/div/is_total) for each table of a CABEE LGA cube."""
    for year, sheet, title, b in _tables(cabee.CABEE / fname):
        b = b[b["state"] == STATE].copy()
        b["lga_code"] = b["lga_code"].map(lambda v: str(int(v)) if pd.notna(v) else None)
        lab = b["lga_label"].astype(str).str.strip()
        b["is_total"] = b["ind_code"].isna() & ((b["ind_label"].astype(str).str.strip() == "Total")
                                                | lab.str.startswith("Total "))
        b["lga_name"] = lab.str.replace(r"^Total ", "", regex=True)
        block = (b["lga_name"] != b["lga_name"].shift()).cumsum()  # same code repair as src/cabee.py
        b["lga_code"] = b.groupby(block)["lga_code"].transform("first")
        b["div"] = np.where(b["is_total"], "all",
                            b["ind_code"].astype(str).str.strip() + "_" + b["ind_label"].astype(str).map(cabee.snake))
        yield year, sheet, b


def cabee_long() -> pd.DataFrame:
    u = urls(cabee.CABEE / "urls.txt")
    rows = []
    for release, (f10, vintage) in cabee.RELEASES.items():
        for cube, fname, bands in (("DC10", f10, EMP_BANDS), ("DC11", cabee.TURNOVER_CUBES[release], TO_BANDS)):
            meta = dict(source=u[fname], source_file=rel(cabee.CABEE / fname), release=f"CABEE {release}")
            for year, sheet, b in _cabee_blocks(fname):
                if cube == "DC11":
                    b = b[b["is_total"] | b["div"].str[0].isin(KEY_TURNOVER_DIVS)]
                cols = [c for c in b.columns if c in bands]
                unknown = [c for c in b.columns[5:] if c not in bands and c not in
                           ("lga_code", "lga_name", "is_total", "div", "Total")]
                assert not unknown, (fname, year, unknown)
                for _, r in b.iterrows():
                    code = cabee.CODE_TO_LGA2021.get(r["lga_code"], r["lga_code"])
                    base = dict(region_id=code, lga_code_published=r["lga_code"], **june(year), unit="businesses",
                                sheet=sheet, note=f"{cube}; LGA boundaries: {vintage}", **meta)
                    pre = f"cabee_businesses_{r['div']}"
                    vals = {bands[c]: to_num(r[c]) for c in cols}
                    for k, v in vals.items():
                        if cube == "DC11" and k == "total":
                            continue  # same count as DC10 total (cross-check only)
                        rows.append({**base, "variable": f"{pre}_{k}", "value": v, "derived": False})
                    if cube == "DC10":
                        emp = [vals[k] for k in ("emp_1_19", "emp_1_4", "emp_5_19", "emp_20_199", "emp_200_plus")
                               if k in vals]
                        rows.append({**base, "variable": f"{pre}_employing_sum", "derived": True,
                                     "value": float(np.sum(emp)) if not np.isnan(emp).any() else np.nan,
                                     "note": base["note"] + "; derived: sum of published employing size cells"})
                        if "emp_1_4" in vals:
                            a, c = vals["emp_1_4"], vals["emp_5_19"]
                            rows.append({**base, "variable": f"{pre}_emp_1_19_sum", "derived": True,
                                         "value": a + c if not (np.isnan(a) or np.isnan(c)) else np.nan,
                                         "note": base["note"] + "; derived: 1-4 + 5-19 (for comparison with the "
                                                                "published 1-19 band of earlier releases)"})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------------- Data by Region
DIV_WORDS = {  # Jobs in Australia industry label -> ANZSIC division code (for variable names)
    "agriculture, forestry and fishing": "A", "mining": "B", "manufacturing": "C",
    "electricity, gas, water and waste services": "D", "construction": "E", "wholesale trade": "F",
    "retail trade": "G", "accommodation and food services": "H", "transport, postal and warehousing": "I",
    "information media and telecommunications": "J", "finance and insurance services": "K",
    "rental, hiring and real estate services": "L", "professional, scientific and technical services": "M",
    "administrative and support services": "N", "public administration and safety": "O",
    "education and training": "P", "health care and social assistance": "Q", "arts and recreation services": "R",
    "other services": "S",
}
EMP = {"non-employing": "non_employing", "1-4 employees": "emp_1_4", "5-19 employees": "emp_5_19",
       "20 or more employees": "emp_20_plus"}
TO = {"zero to less than $50k": "to_0_50k", "$50k to less than $200k": "to_50k_200k",
      "$200k to less than $2m": "to_200k_2m", "$2m to less than $5m": "to_2m_5m",
      "$5m to less than $10m": "to_5m_10m", "$10m or more": "to_10m_plus"}
PIA = {"employee income earners (no.)": ("pia_employee_income_earners", "persons"),
       "total employee income ($m)": ("pia_employee_income_total", "AUD million"),
       "median employee income ($)": ("pia_employee_income_median", "AUD"),
       "mean employee income ($)": ("pia_employee_income_mean", "AUD"),
       "own unincorporated business income earners (no.)": ("pia_own_business_income_earners", "persons"),
       "total own unincorporated business income ($m)": ("pia_own_business_income_total", "AUD million"),
       "median own unincorporated business income ($)": ("pia_own_business_income_median", "AUD"),
       "mean own unincorporated business income ($)": ("pia_own_business_income_mean", "AUD"),
       "own unincorporated business income as main source of income (%)":
           ("pia_own_business_income_main_source_pct", "%")}


def dbr_variable(group: str, header: str):
    """(variable, unit) for a Data by Region column, or None if not an IL item we keep."""
    g = re.sub(r"\s+", " ", group).strip().lower()
    h = re.sub(r"\s+", " ", header).strip().lower().replace("non employing", "non-employing")
    h = h.replace("gas water", "gas, water")
    for kind in ("entries", "exits"):
        if g.startswith(f"business {kind} by turnover"):
            if h.endswith("by turnover - total"):
                return f"business_{kind}_turnover_total", "businesses"
            m = re.search(rf"business {kind} with turnover of (.+)$", h)
            return (f"business_{kind}_{TO[m.group(1)]}", "businesses") if m else None
        if g.startswith(f"business {kind}"):
            if h.startswith("total number"):
                return f"business_{kind}_total", "businesses"
            for k, v in EMP.items():
                if h.endswith(k) or h.startswith(f"number of {k}"):
                    return f"business_{kind}_{v}", "businesses"
            return None
    if "insolvenc" in g and "occupation" not in g:
        if "caused by economic conditions" in h:
            return "insolvency_debtors_business_related_economic_conditions", "debtors"
        if "non-business related personal insolvencies" in h:
            return "insolvency_debtors_non_business_related", "debtors"
        if "business related personal insolvencies" in h:
            return "insolvency_debtors_business_related", "debtors"
        if h.startswith("total debtors entering personal insolvencies"):
            return "insolvency_debtors_total", "debtors"
        return None
    if g.startswith("jobs in australia"):
        if h == "number of jobs":
            return "jia_jobs_total", "jobs"
        if h == "number of jobs held by females":
            return "jia_jobs_female", "jobs"
        if h == "number of jobs held by males":
            return "jia_jobs_male", "jobs"
        m = re.match(r"number of employee jobs - (.+)$", h)
        if m:
            lab = m.group(1)
            return ("jia_employee_jobs_total", "jobs") if lab == "total" else \
                (f"jia_employee_jobs_{DIV_WORDS[lab]}_{cabee.snake(lab)}", "jobs")
        return None
    if g.startswith("personal income in australia") or g.startswith("estimates of personal income"):
        return PIA.get(h)
    return None


def dbr_long() -> pd.DataFrame:
    u = urls(RAW / "urls.txt")
    rows = []
    for release in DBR_RELEASES:
        for cube in ("14100DO0003", "14100DO0004", "14100DO0005"):
            fname = f"dbr{release}_{cube}.xlsx"
            r = pd.read_excel(RAW / fname, sheet_name="Table 2", header=None, dtype=object)
            title = str(r.iat[3, 0])
            assert "Local Government Area" in title, (fname, title)
            assert str(r.iat[6, 0]).strip() == "Code" and str(r.iat[6, 2]).strip() == "Year", fname
            grp = r.iloc[5].ffill()
            body = r.iloc[7:]
            body = body[body[0].astype(str).str.fullmatch(r"1\d{4}")]  # NSW LGA codes
            boundary = "LGA 2020 (ASGS 2016)" if release == "2015-20" else "LGA 2021 (ASGS Ed. 3)"
            for i in range(3, r.shape[1]):
                vu = dbr_variable(str(grp[i]), str(r.iat[6, i]))
                if vu is None:
                    continue
                var, unit = vu
                for code, label, year, v in zip(body[0], body[1], body[2], body[i]):
                    y = int(year)
                    if y < 2014:
                        continue
                    note = f"{str(grp[i]).strip()}: {str(r.iat[6, i]).strip()}; boundaries {boundary}"
                    if str(label).strip().endswith("*"):
                        note += "; ABS flags a 2019->2020 boundary change (some items on LGA 2019 boundaries)"
                    rows.append(dict(region_id=str(code), lga_code_published=str(code), **fy(y), variable=var,
                                     value=to_num(v), unit=unit, source=u[fname], source_file=rel(RAW / fname),
                                     sheet="Table 2", release=f"Data by Region {release}", derived=False, note=note))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------------------------- TRA
TRA_METRICS = {"visitors ('000)": ("visitors", "thousand visitors"), "nights ('000)": ("nights", "thousand nights"),
               "average stay (nights)": ("avg_stay", "nights"), "spend ($m)": ("spend", "AUD million")}
TRA_COLS = {2: "international", 4: "domestic_overnight", 6: "domestic_day", 8: "total"}
TRA_BUS = {"non-employing": "non_employing", "1 to 4 employees": "emp_1_4", "5 to 19 employees": "emp_5_19",
           "20 or more employees": "emp_20_plus", "total": "total"}


def lga_name_to_code() -> dict:
    """ABS LGA label (2016/2018 editions, as in the CABEE cubes) -> LGA 2021 code."""
    m = {}
    for release in ("jun2013-jun2017", "jun2014-jun2018", "jul2017-jun2021"):
        L = cabee.parse_release(release)
        for code, name in L[["lga_code", "lga_name"]].drop_duplicates().itertuples(index=False):
            m.setdefault(name.strip(), cabee.CODE_TO_LGA2021.get(code, code))
    return m


def tra_long() -> pd.DataFrame:
    if not TRA_DIR.exists():
        return pd.DataFrame()
    u = urls(TRA_DIR / "urls.txt")
    names = lga_name_to_code()
    rows = []
    for f in sorted(TRA_DIR.glob("*.xlsx")):
        r = pd.read_excel(f, header=None, dtype=object)
        sheet = pd.ExcelFile(f).sheet_names[0]
        col1 = r[1].astype(str).str.strip()
        head = col1[col1.str.contains(", NEW SOUTH WALES|, VICTORIA|, QUEENSLAND", regex=True)]
        if head.empty or not head.iloc[0].endswith("NEW SOUTH WALES"):
            continue
        assert "LOCAL GOVERNMENT AREA PROFILES, 2017" in " ".join(col1), f
        foot = " ".join(col1[col1.str.contains("four year average")])
        assert "2014 to 2017" in foot, f
        name = f.stem.strip()  # file name = TRA's LGA label (ABS 2016/2018 style, e.g. 'Bega Valley (A)')
        assert head.iloc[0].upper().startswith(name.upper().replace(" (NSW)", "")), (f, head.iloc[0])
        code = names.get(name) or {k.upper(): v for k, v in names.items()}.get(name.upper())
        assert code, f"no ABS code for TRA LGA {name!r}"
        base = dict(region_id=code, lga_code_published="", period="2014-2017 average", period_start="2014-01-01",
                    period_end="2017-12-31", source=u[f.name], source_file=rel(f), sheet=sheet,
                    release="TRA LGA Profiles 2017", derived=False)
        # key metrics block: rows between 'KEY TOURISM METRICS FOR <LGA>' and the next 'KEY TOURISM METRICS' block
        starts = col1.index[col1.str.startswith("KEY TOURISM METRICS FOR")].tolist()
        i0, i1 = starts[0], starts[1] if len(starts) > 1 else len(r)
        for i in range(i0 + 1, i1):
            lab = col1[i].lower()
            if lab in TRA_METRICS:
                met, unit = TRA_METRICS[lab]
                for c, seg in TRA_COLS.items():
                    rows.append({**base, "variable": f"tra2017_{met}_{seg}", "value": to_num(r.iat[i, c]),
                                 "unit": unit, "note": f"TRA LGA profile 2017 for {name}: {col1[i]} / {seg}; "
                                                       "4-year average 2014-2017; 'np'/'-' blank"})
            if lab.startswith("reason (") or lab.startswith("travel party"):
                break
        # tourism businesses (ABS CABEE, tourism-related industries) in columns 4 / 8
        c4 = r[4].astype(str).str.strip()
        t0 = c4.index[c4 == "TOURISM BUSINESSES^"]
        if len(t0):
            for i in range(t0[0] + 1, t0[0] + 7):
                lab = c4[i].lower()
                if lab in TRA_BUS:
                    v = to_num(r.iat[i, 8]) if pd.notna(r.iat[i, 8]) else to_num(r.iat[i, 9])
                    rows.append({**base, "period": "2017", "period_start": "2017-01-01", "period_end": "2017-12-31",
                                 "variable": f"tra2017_tourism_businesses_{TRA_BUS[lab]}", "value": v,
                                 "unit": "businesses", "note": f"TRA LGA profile 2017 for {name}: TOURISM BUSINESSES^ "
                                                               f"{c4[i]}; footnote '^ Data for 2017', source ABS "
                                                               "CABEE 8165.0 (tourism-related industries as defined "
                                                               "by TRA); perturbed by ABS"})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------------------------- build
def best_release(df: pd.DataFrame, order: list) -> pd.DataFrame:
    """Keep, per (variable, period), the newest release that has any value for it."""
    rank = {r: i for i, r in enumerate(order)}
    has = df[df.value.notna()].groupby(["variable", "period"]).release.agg(lambda s: min(s.unique(), key=rank.get))
    keep = df.set_index(["variable", "period"]).index.map(has.to_dict().get) == df.release.values
    return df[keep]


COLS = ["region_id", "period", "period_start", "period_end", "variable", "value", "unit", "source", "source_file",
        "sheet", "release", "derived", "note", "lga_code_published"]


def run():
    cab = cabee_long()
    dbr = dbr_long()
    tra = tra_long()
    allrel = pd.concat([cab, dbr, tra], ignore_index=True)[COLS]
    allrel.to_parquet(ENRICH / "il_sector_all_releases.parquet", index=False)
    order = [f"CABEE {r}" for r in cabee.RELEASES] + [f"Data by Region {r}" for r in DBR_RELEASES] + \
            ["TRA LGA Profiles 2017"]
    out = best_release(allrel, order)
    out = out[out.region_id.str.fullmatch(r"1\d{4}")]
    assert not out.duplicated(["region_id", "period", "variable"]).any()
    out = out.sort_values(["variable", "region_id", "period"]).reset_index(drop=True)
    out.to_parquet(ENRICH / "il_sector.parquet", index=False)
    out.to_csv(ENRICH / "il_sector.csv", index=False)

    doc = {
        "cabee_businesses_<div>_<band>": "ABS CABEE LGA cubes: businesses operating at 30 June; <div> = 'all' (LGA "
            "total) or ANZSIC division code_label; <band> = non_employing, emp_1_19 (to 2019), emp_1_4 / emp_5_19 "
            "(from 2020), emp_20_199, emp_200_plus, total (DC10) or to_* turnover bands (DC11, LGA total + divisions "
            + ",".join(sorted(KEY_TURNOVER_DIVS)) + ")",
        "cabee_*_employing_sum / *_emp_1_19_sum": "derived sums of published cells (perturbed; see derived/note)",
        "business_entries_* / business_exits_*": "ABS Data by Region (CABEE): businesses entering / exiting in the "
            "year ended 30 June, by employment size and turnover band; FY2016-17 to FY2023-24",
        "jia_*": "ABS Jobs in Australia via Data by Region: jobs (all) and employee jobs by ANZSIC division, year "
            "ended 30 June 2015-2023, LGA as assigned by ABS JIA (see JIA methodology for the geography basis)",
        "insolvency_debtors_*": "AFSA personal insolvency via ABS Data by Region, debtors entering in the year ended "
            "30 June, by debtor's LGA; 'business related' as classified by AFSA (see DBR explanatory notes)",
        "pia_*": "ABS Personal Income in Australia via Data by Region: employee and own unincorporated business "
            "income, year ended 30 June 2015-2023, by LGA of residence",
        "tra2017_*": "Tourism Research Australia LGA Profiles 2017 (4-year average 2014-2017): visitors, nights, "
            "average stay, spend by international / domestic overnight / domestic day / total; tourism businesses",
    }
    (ENRICH / "il_sector.doc.json").write_text(json.dumps(doc, indent=1))

    for f, url in urls(cabee.CABEE / "urls.txt").items():
        record_source(f"ABS CABEE by LGA (IL sector detail): {f}", url, cabee.CABEE / f, ABS_LIC,
                      "industry division x employment / turnover size, 30 June")
    for f, url in urls(RAW / "urls.txt").items():
        record_source(f"IL sector: {f}", url, RAW / f,
                      ABS_LIC if f.startswith("dbr") else "© Commonwealth (Tourism Research Australia)",
                      "ABS Data by Region, LGA table 2" if f.startswith("dbr") else "TRA LGA profiles list (2024)")
    if TRA_DIR.exists():
        for f, url in urls(TRA_DIR / "urls.txt").items():
            record_source(f"TRA LGA Profile 2017: {f}", url, TRA_DIR / f, "© Commonwealth (Tourism Research Australia)",
                          "Internet Archive copy; 4-year average 2014-2017")
    return out


if __name__ == "__main__":
    o = run()
    print(f"rows={len(o)}  variables={o.variable.nunique()}  LGAs={o.region_id.nunique()}")
    fam = o.variable.str.extract(r"^(cabee_businesses_all|cabee_businesses|business_entries|business_exits|jia|"
                                 r"insolvency|pia|tra2017)")[0]
    s = o.assign(fam=fam, has=o.value.notna()).groupby("fam").agg(
        n_var=("variable", "nunique"), n_lga=("region_id", "nunique"),
        periods=("period", lambda p: f"{p.min()} .. {p.max()} ({p.nunique()})"), filled=("has", "mean"))
    print(s.to_string())
