"""DSS payment recipients by NSW council x quarter (proxy for impacts on vulnerable groups).

Source: data.gov.au "DSS Payments by Local Government Area"
(https://data.gov.au/data/api/3/action/package_show?id=dss-payments-by-local-government-area).
Five CSVs, one per ASGS LGA boundary vintage, stored unchanged in data/dss/ (see data/dss/urls.txt):

    vintage  quarters             file
    2014     2016Q1 - 2018Q4      dss-payments-mar-2016-to-dec-2018-by-2014-lga.csv
    2018     2019Q1 - 2020Q4      dss-payments-mar-2019-to-dec-2020-by-2018-lga.csv
    2020     2021Q1 - 2023Q1      dss-payments-mar-2021-to-mar-2023-by-2020-lga.csv
    2022     2023Q2 - 2024Q3      dss-demographics-2022-lga-september-2024.csv
    2024     2024Q4 - 2026Q2      dss-benefit-and-payment-recipient-demographics-2024-lga-june-2026.csv

Values are point-in-time recipient counts at the end of the quarter-month (e.g. "2019-12" -> 2019Q4).

load() -> long table, NSW only (LGA codes 1xxxx, includes 19399 "Unincorporated NSW"):
    lga_code, lga_name (both as published), lga_vintage (int), quarter (Period[Q-DEC]),
    payment (payment name as published), recipients (float)

Missing rules (missing is never zero):
    * blank, ".", "-", "<5", "np", "n.p." and any other non-numeric cell -> NaN.
      (Only "." occurs, 49 cells in the 2014 file, all non-NSW at build time.)
    * published 0 stays 0. Thousands separators ("1,096" in the 2018 file) are parsed as numbers.
    * A payment not published in a vintage (e.g. Commonwealth Rent Assistance in the 2014 file) has no
      rows in the long table and is NaN in the wide table.

Confidentiality (from the dataset notes) -- affects small counts:
    * before Dec 2022: values of 1-4 were randomly published as 0 or 5, so a published 0 or 5 before
      2022Q4 means "0-5"; zeros before 2022Q4 are NOT guaranteed true zeros.
    * from Dec 2022 (2022Q4): all cells rounded to the nearest 5, values 1-7 shown as 5; zeros are true zeros.
      Totals re-computed from rounded cells can differ from true totals.

Wide summary (data/dss/dss_lga_quarter.parquet, one row per lga_code x lga_vintage x quarter):
    jobseeker_newstart          "Newstart Allowance" (2014 file), "Newstart Allowance / Jobseeker Payment"
                                (2018 file), "JobSeeker Payment" (2020+ files). JobSeeker replaced Newstart
                                on 20 March 2020, so this is treated as one series. It also absorbed Sickness
                                Allowance (closed Mar 2020) and later Partner/Widow Allowance (closed 2021-22),
                                which are small; they are NOT added here.
    youth_allowance_other       "Youth Allowance (other)"  (job-seeker youth allowance, 16-21)
    disability_support_pension  "Disability Support Pension"
    parenting_payment_single    "Parenting Payment Single"
    age_pension                 "Age Pension"
    carer_payment               "Carer Payment"
    commonwealth_rent_assistance "Commonwealth Rent Assistance" (not published in the 2014 file -> NaN 2016-2018)
    income_support_total        working-age income support, defined here as the sum of:
                                jobseeker_newstart + Youth Allowance (other) + Parenting Payment Single
                                + Parenting Payment Partnered + Disability Support Pension + Carer Payment
                                + Special Benefit + legacy allowances while published (Sickness Allowance,
                                Partner Allowance, Widow Allowance, Widow B Pension, Wife Pension (both types)).
                                Excludes Age Pension, student payments (Youth Allowance (student and apprentice),
                                Austudy, ABSTUDY), family payments, concession cards, CRA and Carer Allowance
                                (supplements, not income support). NaN if any component published in that
                                vintage is NaN. Summing rounded cells compounds rounding error (see above).
    DSS does not publish a total, so this is a constructed sum.

Run as main to write the parquet.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DSS = ROOT / "data" / "dss"
OUT = DSS / "dss_lga_quarter.parquet"

FILES = {
    2014: "dss-payments-mar-2016-to-dec-2018-by-2014-lga.csv",
    2018: "dss-payments-mar-2019-to-dec-2020-by-2018-lga.csv",
    2020: "dss-payments-mar-2021-to-mar-2023-by-2020-lga.csv",
    2022: "dss-demographics-2022-lga-september-2024.csv",
    2024: "dss-benefit-and-payment-recipient-demographics-2024-lga-june-2026.csv",
}

# published payment name -> wide column
GROUPS = {
    "Newstart Allowance": "jobseeker_newstart",
    "Newstart Allowance / Jobseeker Payment": "jobseeker_newstart",
    "JobSeeker Payment": "jobseeker_newstart",
    "Youth Allowance (other)": "youth_allowance_other",
    "Disability Support Pension": "disability_support_pension",
    "Parenting Payment Single": "parenting_payment_single",
    "Age Pension": "age_pension",
    "Carer Payment": "carer_payment",
    "Commonwealth Rent Assistance": "commonwealth_rent_assistance",
}
WIDE_COLS = list(dict.fromkeys(GROUPS.values()))

INCOME_SUPPORT = {
    "Newstart Allowance", "Newstart Allowance / Jobseeker Payment", "JobSeeker Payment",
    "Youth Allowance (other)", "Parenting Payment Single", "Parenting Payment Partnered",
    "Disability Support Pension", "Carer Payment", "Special Benefit",
    "Sickness Allowance", "Partner Allowance", "Widow Allowance", "Widow B Pension",
    "Wife Pension (Partner on Age Pension)", "Wife Pension (Partner on Disability Support Pension)",
}


def _to_num(s: pd.Series) -> pd.Series:
    """Numeric parse; anything non-numeric (blank, '.', '-', '<5', 'np') -> NaN, never 0."""
    s = s.astype("string").str.strip().str.replace(",", "", regex=False)
    return pd.to_numeric(s.where(s.str.fullmatch(r"\d+(\.\d+)?", na=False)), errors="coerce").astype(float)


def read_vintage(vintage: int) -> pd.DataFrame:
    raw = pd.read_csv(DSS / FILES[vintage], dtype=str, keep_default_na=False)
    date_col, code_col, name_col = raw.columns[:3]
    raw = raw[raw[code_col].str.strip().str.startswith("1")]  # NSW LGA codes start with 1
    long = raw.melt(id_vars=[date_col, code_col, name_col], var_name="payment", value_name="value")
    return pd.DataFrame({
        "lga_code": long[code_col].str.strip(),
        "lga_name": long[name_col].str.strip(),
        "lga_vintage": vintage,
        "quarter": pd.PeriodIndex(pd.to_datetime(long[date_col].str.strip(), format="%Y-%m"), freq="Q"),
        "payment": long["payment"],
        "recipients": _to_num(long["value"]),
    })


def load() -> pd.DataFrame:
    """Long NSW table across all five vintages (see module docstring)."""
    df = pd.concat([read_vintage(v) for v in FILES], ignore_index=True)
    assert not df.duplicated(["lga_code", "lga_vintage", "quarter", "payment"]).any()
    return df.sort_values(["lga_vintage", "quarter", "lga_code", "payment"], ignore_index=True)


def wide(long: pd.DataFrame | None = None) -> pd.DataFrame:
    long = load() if long is None else long
    keys = ["lga_code", "lga_name", "lga_vintage", "quarter"]
    g = long[long.payment.isin(GROUPS)].assign(col=lambda d: d.payment.map(GROUPS))
    # each group has exactly one published name per vintage, so 'first' does not merge anything
    assert not g.duplicated(keys + ["col"]).any()
    w = g.pivot_table(index=keys, columns="col", values="recipients", aggfunc="first", dropna=False)
    w = w.reindex(columns=WIDE_COLS)
    inc = long[long.payment.isin(INCOME_SUPPORT)]
    w["income_support_total"] = inc.groupby(keys)["recipients"].sum(min_count=1).where(
        inc.groupby(keys)["recipients"].apply(lambda s: s.notna().all()))
    w = w.reset_index()
    w.columns.name = None
    # pivot_table drops all-NaN rows/cols in some pandas versions; rebuild from the full key set
    base = long[keys].drop_duplicates()
    return base.merge(w, on=keys, how="left").sort_values(["lga_vintage", "quarter", "lga_code"], ignore_index=True)


if __name__ == "__main__":
    long = load()
    w = wide(long)
    w.to_parquet(OUT, index=False)  # quarter round-trips as period[Q-DEC] via pandas' pyarrow extension type
    print(f"wrote {OUT} {w.shape}")
    print(w.groupby("lga_vintage").quarter.agg(["min", "max", "nunique"]))
