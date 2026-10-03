#!/usr/bin/env python3
"""Merge per-council extraction CSVs + verifier CSVs + bibliography fragments into the deliverables:
extraction_raw.csv, statements_tidy.csv, verification.csv, coverage_report.csv/.md,
and ../../bibliography/parts/exp10_A_comparison_councils.csv.  (No statistics.)
Optional: work/batches/finder_status.json (finder per-year status) for coverage notes."""
import csv, glob, json, os
import pandas as pd

ROOT = "/Users/ray/Research/AUSSEF - Local"
D = os.path.join(ROOT, "Experiment 10", "A_comparison_councils")
FYS = ["2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
CORE = ["capex_ippe", "grants_contrib_operating", "grants_contrib_capital", "total_expenses", "depreciation"]
TIDY_ITEMS = CORE + ["disaster_grant_operating", "disaster_grant_capital", "disaster_expense",
                     "bushfire_emergency_services_grant", "other_disaster_line"]

allc = pd.read_csv(os.path.join(D, "comparison_councils.csv"), dtype={"region_id": str})
names = dict(zip(allc.region_id, allc.region_name))
sel = pd.read_csv(os.path.join(D, "selected_25.csv"), dtype={"region_id": str})
coun = allc[allc.region_id.isin(sel.region_id)]
SUPP = ["17200", "15950", "15350", "12380", "10500", "11570", "11520"]  # metro, extracted before scope change

# raw
parts = []
for f in sorted(glob.glob(os.path.join(D, "work", "extract", "*.csv"))):
    x = pd.read_csv(f, dtype=str, keep_default_na=False)
    x["extract_file"] = os.path.basename(f)
    parts.append(x)
raw_all = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
raw_all["region_id"] = raw_all["region_id"].str.strip()
raw_all[raw_all.region_id.isin(SUPP)].to_csv(os.path.join(D, "supplementary_metro_extraction_raw.csv"), index=False)
raw = raw_all[raw_all.region_id.isin(coun.region_id)].copy()
raw.to_csv(os.path.join(D, "extraction_raw.csv"), index=False)

# tidy: current-year values; prior-year column (from next year's GPFS) only where no current-year value exists
r = raw.copy()
r["value_num"] = pd.to_numeric(r["value_aud"].str.replace(",", ""), errors="coerce")
r = r[r["item"].isin(TIDY_ITEMS) & r["fy"].isin(FYS)]
cur = r[r["column"] == "current_year"]
pri = r[r["column"] == "prior_year"]
have = set(zip(cur.region_id, cur.fy, cur["item"]))
fill = pri[[(a, b, c) not in have for a, b, c in zip(pri.region_id, pri.fy, pri["item"])]]
fill = fill.drop_duplicates(["region_id", "fy", "item", "label"])
tidy = pd.concat([cur, fill])
tidy = tidy.assign(council=tidy.region_id.map(names).fillna(tidy.council))
tidy = tidy.rename(columns={"value_num": "value_aud_n"})
out = tidy[["region_id", "council", "fy", "item", "value_aud_n", "page", "label", "file"]].rename(
    columns={"value_aud_n": "value_aud"}).sort_values(["region_id", "fy", "item"])
out.to_csv(os.path.join(D, "statements_tidy.csv"), index=False)
n_fill = len(fill)

# verification
vparts = [pd.read_csv(f, dtype=str, keep_default_na=False) for f in sorted(glob.glob(os.path.join(D, "work", "verify", "*.csv")))]
ver = pd.concat(vparts, ignore_index=True) if vparts else pd.DataFrame(columns=["verdict", "region_id"])
ver = ver[ver.region_id.astype(str).str.strip().isin(coun.region_id)]
ver.to_csv(os.path.join(D, "verification.csv"), index=False)

# coverage
fstat = {}
fp = os.path.join(D, "work", "batches", "finder_status.json")
if os.path.exists(fp):
    for c in json.load(open(fp)):
        for y in c["years"]:
            fstat[(c["region_id"], y["fy"])] = (y["status"], y.get("notes", ""))
rows = []
for rid in coun.region_id:
    for fy in FYS:
        sub = out[(out.region_id == rid) & (out.fy == fy)]
        core = [i for i in CORE if i in set(sub["item"])]
        dis = sub[sub["item"].str.startswith("disaster_")]
        st, note = fstat.get((rid, fy), ("", ""))
        src = "current-year GPFS" if len(cur[(cur.region_id == rid) & (cur.fy == fy)]) else (
            "prior-year column of next GPFS" if len(sub) else "none")
        rows.append(dict(region_id=rid, council=names[rid], fy=fy, finder_status=st, value_source=src,
                         core_items_found=len(core), core_missing=";".join(i for i in CORE if i not in core),
                         disaster_lines=len(dis), disaster_aud=dis["value_aud"].sum() if len(dis) else 0,
                         finder_note=note))
cov = pd.DataFrame(rows)
cov.to_csv(os.path.join(D, "coverage_report.csv"), index=False)

# bibliography part
cols = ["source_id", "title", "author_or_publisher", "year", "source_type", "url", "doi", "accessed_date", "local_path",
        "bytes", "sha256", "used_in", "what_it_was_used_for", "pages_or_table", "quote_or_value", "notes"]
bib = []
for f in ["downloads_bib.csv", "searched_bib.csv"]:
    p = os.path.join(D, "work", "bib", f)
    if os.path.exists(p):
        bib.append(pd.read_csv(p, dtype=str, keep_default_na=False))
bib = pd.concat(bib, ignore_index=True) if bib else pd.DataFrame(columns=cols)
bib = bib.drop_duplicates(subset=["url", "local_path", "used_in"]).reset_index(drop=True)
pages = out.groupby("file").apply(lambda g: "; ".join(
    f"p{p} {i}" for p, i in sorted(set(zip(g.page.astype(str), g["item"])), key=lambda t: (len(t[0]), t[0]))))
ex = out[out["item"] == "capex_ippe"].sort_values("fy").groupby("file").last()
for i, row in bib.iterrows():
    lp = row["local_path"]
    if lp and lp in pages.index:
        bib.at[i, "pages_or_table"] = pages[lp][:900]
        if lp in ex.index:
            e = ex.loc[lp]
            bib.at[i, "quote_or_value"] = f"\"{e['label']}\" FY{e['fy']} = {e['value_aud']:,.0f} AUD"[:200]
    elif lp:
        rid = lp.split("/")[5] if lp.count("/") >= 5 else ""
        why = ("supplementary metropolitan set (values in supplementary_metro_extraction_raw.csv)" if rid in SUPP else
               "downloaded before the 2 Oct scope change; council outside the final 25, not extracted"
               if rid not in set(coun.region_id) else "downloaded, no values extracted")
        bib.at[i, "notes"] = (row["notes"] + "; " if row["notes"] else "") + why
        if rid in SUPP:
            bib.at[i, "used_in"] = "Experiment 10/A_comparison_councils (supplementary metropolitan set)"
        elif rid not in set(coun.region_id):
            bib.at[i, "used_in"] = "downloaded, not used (council outside final 25)"
for i in range(len(bib)):
    if not bib.at[i, "source_id"]:
        bib.at[i, "source_id"] = f"exp10Acmp_web_{i:04d}"
bp = os.path.join(ROOT, "bibliography", "parts", "exp10_A_comparison_councils.csv")
bib[cols].to_csv(bp, index=False)

# downloads
dl = pd.read_csv(os.path.join(D, "downloads_log.csv"), dtype=str, keep_default_na=False)
tot = pd.to_numeric(dl[dl.status == "downloaded"]["bytes"]).sum()

vc = ver["verdict"].value_counts().to_dict() if len(ver) else {}
md = [f"# Coverage report: Source A (audited GPFS), 25 comparison councils x 9 FYs = {len(cov)} council-years", "",
      f"- downloads: {(dl.status=='downloaded').sum()} PDFs kept, {tot/1e6:,.0f} MB; statuses: {dl.status.value_counts().to_dict()}",
      f"- extraction_raw rows: {len(raw)}; statements_tidy rows: {len(out)} ({n_fill} filled from prior-year column)",
      f"- council-years with all 5 core items: {(cov.core_items_found==5).sum()}; with none: {(cov.core_items_found==0).sum()}",
      f"- council-years with >=1 disaster line: {(cov.disaster_lines>0).sum()}",
      f"- verification: {len(ver)} rows checked = {len(ver)/max(len(raw),1):.1%} of raw rows; verdicts {vc}", "",
      "## Core items found, by FY (council count with all 5)", "",
      cov.assign(full=cov.core_items_found == 5).groupby("fy").full.sum().to_frame().T.to_markdown(), "",
      "## Council-years with no values", "",
      cov[cov.core_items_found == 0][["region_id", "council", "fy", "finder_status", "finder_note"]].to_markdown(index=False)]
open(os.path.join(D, "coverage_report.md"), "w").write("\n".join(md))
print("\n".join(md[:8]))
