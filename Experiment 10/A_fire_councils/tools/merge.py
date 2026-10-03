#!/usr/bin/env python3
"""Merge per-batch work files into the final Experiment 10 / A outputs."""
import csv, glob, json, os, collections
ROOT = "/Users/ray/Research/AUSSEF - Local"
EXP = f"{ROOT}/Experiment 10/A_fire_councils"
YEARS = ["2015-16","2016-17","2017-18","2018-19","2019-20","2020-21","2021-22","2022-23","2023-24"]
BIB = "source_id,title,author_or_publisher,year,source_type,url,doi,accessed_date,local_path,bytes,sha256,used_in,what_it_was_used_for,pages_or_table,quote_or_value,notes".split(",")
CORE = ["capex_ippe","grants_contrib_operating","grants_contrib_capital","total_expenses","depreciation"]
batches = json.load(open(f"{EXP}/batches.json"))
councils = [(c["region_id"], c["council"], b["batch"]) for b in batches for c in b["councils"]]

def read(p):
    with open(p, newline="", encoding="utf-8-sig") as fh: return list(csv.DictReader(fh))
def write(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

# downloads log
dl = []
for p in sorted(glob.glob(f"{EXP}/work/batch_*/downloads_log.csv")):
    b = p.split("batch_")[1][:2]
    for r in read(p): r["batch"] = b; dl.append(r)
dcols = ["batch"] + list(read(sorted(glob.glob(f"{EXP}/work/batch_*/downloads_log.csv"))[0])[0].keys()) if dl else ["batch"]
write(f"{EXP}/downloads_log.csv", dl, [c for c in dcols if c != "batch"] + ["batch"])
# drop rows for files that no longer exist (deleted wrong files) only from the bytes total
ok = [r for r in dl if r.get("result") == "OK" and os.path.exists(f"{ROOT}/{r['local_path']}")]
total_bytes = sum(int(r["bytes"]) for r in ok)

# raw extraction
raw = []
for p in sorted(glob.glob(f"{EXP}/work/batch_*/extract_*.csv")):
    rows = read(p)
    raw += rows
rcols = "region_id,council,fy,statement_fy,column,item,label,value_as_printed,unit_multiplier,value_aud,page,printed_page,statement_section,file,notes".split(",")
write(f"{EXP}/extraction_raw.csv", raw, rcols)

# tidy: current-year column values; prior-year comparatives only fill council-years with no current-year statement
cur_years = {(r["region_id"], r["fy"]) for r in raw if r["column"].strip().lower() == "current"}
tidy, seen = [], set()
for r in raw:
    col = r["column"].strip().lower()
    if col == "current": basis = "own-year statement"
    elif col == "prior" and (r["region_id"], r["fy"]) not in cur_years: basis = f"prior-year comparative in FY{r['statement_fy']} statement"
    else: continue
    if r["fy"] not in YEARS: continue
    key = (r["region_id"], r["fy"], r["item"], r["label"].strip().lower(), r["value_aud"], basis)
    if key in seen: continue
    seen.add(key)
    tidy.append(dict(region_id=r["region_id"], council=r["council"], fy=r["fy"], item=r["item"], value_aud=r["value_aud"],
                     page=r["page"], label=r["label"], file=r["file"], source_basis=basis))
tidy.sort(key=lambda r: (r["region_id"], r["fy"], r["item"], r["label"]))
write(f"{EXP}/statements_tidy.csv", tidy, ["region_id","council","fy","item","value_aud","page","label","file","source_basis"])

# coverage
status = {}
for p in glob.glob(f"{EXP}/work/batch_*/found_status.csv"):
    for r in read(p): status[(r["region_id"], r["fy"])] = r
items_by = collections.defaultdict(set); basis_by = {}
for t in tidy:
    items_by[(t["region_id"], t["fy"])].add(t["item"]); basis_by[(t["region_id"], t["fy"])] = t["source_basis"]
cov = []
for rid, name, b in councils:
    for fy in YEARS:
        s = status.get((rid, fy), {})
        its = items_by.get((rid, fy), set())
        core_found = [i for i in CORE if i in its]
        dis = sorted(i for i in its if i.startswith("disaster"))
        if len(core_found) == len(CORE): cell = "found" if basis_by[(rid, fy)] == "own-year statement" else "prior-year comparative only"
        elif core_found: cell = "partial"
        else: cell = "missing"
        cov.append(dict(region_id=rid, council=name, fy=fy, coverage=cell, download_status=s.get("status",""),
                        core_items_found=";".join(core_found), core_items_missing=";".join(i for i in CORE if i not in its),
                        disaster_items=";".join(dis), source_basis=basis_by.get((rid, fy), ""),
                        reason=s.get("reason",""), file=s.get("local_path","")))
write(f"{EXP}/coverage_council_year.csv", cov, list(cov[0].keys()))
wide = collections.OrderedDict()
for c in cov:
    wide.setdefault((c["region_id"], c["council"]), {})[c["fy"]] = c["coverage"]
with open(f"{EXP}/coverage_matrix.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["region_id","council"] + YEARS)
    for (rid, n), d in wide.items(): w.writerow([rid, n] + [d[y] for y in YEARS])

# verification
vl = []
for tag, pat in [("pass1_text", "verify_log.csv"), ("pass2_visual", "verify2_log.csv")]:
    for p in sorted(glob.glob(f"{EXP}/work/batch_*/{pat}")):
        for r in read(p): r["pass"] = tag; vl.append(r)
vcols = "pass,region_id,fy,statement_fy,column,item,label,file,page,extracted_value_aud,checked_value_aud,status,note".split(",")
if vl: write(f"{EXP}/verification_log.csv", vl, vcols)

# bibliography part
pages = collections.defaultdict(set)
for t in tidy: pages[t["file"]].add(int(t["page"]) if str(t["page"]).isdigit() else t["page"])
bib = []
for p in sorted(glob.glob(f"{EXP}/work/batch_*/biblio.csv")):
    for r in read(p):
        lp = (r.get("local_path") or "").strip()
        if lp and lp in pages and not r.get("pages_or_table"):
            pg = sorted(pages[lp], key=lambda x: (isinstance(x, str), x))
            r["pages_or_table"] = "PDF pages " + ", ".join(map(str, pg)) + " (see statements_tidy.csv)"
            r["what_it_was_used_for"] = r.get("what_it_was_used_for") or "audited GPFS values: capex, grants, expenses, depreciation, disaster lines"
        if lp and not os.path.exists(f"{ROOT}/{lp}"):
            r["notes"] = (r.get("notes","") + "; local file not present (deleted as wrong file or never saved)").strip("; ")
        bib.append({k: r.get(k, "") for k in BIB})
write(f"{ROOT}/bibliography/parts/exp10_A_fire_councils.csv", bib, BIB)

cnt = collections.Counter(c["coverage"] for c in cov)
print(json.dumps(dict(files_ok=len(ok), total_mb=round(total_bytes/1e6,1), raw_rows=len(raw), tidy_rows=len(tidy),
      coverage=cnt, verify_rows=len(vl), verify_status=collections.Counter(v["pass"]+":"+v.get("status","") for v in vl), bib_rows=len(bib)), indent=1))
