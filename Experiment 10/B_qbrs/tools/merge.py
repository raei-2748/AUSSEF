"""Merge per-council work files into final outputs. Re-runnable."""
import glob, os, sys, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from common import *
W = os.path.join(B, "work")
plan = pd.read_csv(os.path.join(B, "councils_plan.csv"))
def cat(pattern):
    fs = sorted(glob.glob(os.path.join(W, pattern)))
    ds = [pd.read_csv(f, dtype=str, keep_default_na=False) for f in fs if os.path.getsize(f) > 0]
    return pd.concat(ds, ignore_index=True) if ds else pd.DataFrame()
dl = cat("*/downloads_log.csv")
if len(dl):
    dl["on_disk"] = [("yes" if os.path.exists(os.path.join(ROOT, p)) else "no") if p else "" for p in dl.local_path]
    shas = {}
    for p in glob.glob(os.path.join(PDF_ROOT, "*", "*")):
        import hashlib; shas.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.relpath(p, ROOT))
    m = (dl.status == "downloaded") & (dl.on_disk == "no")
    dl.loc[m, "notes"] = [n + (f" | file not on disk; identical content kept at {shas[h]}" if h in shas else " | file removed by agent after download (not a QBRS / wrong meeting)") for n, h in zip(dl.loc[m, "notes"], dl.loc[m, "sha256"])]
dl.to_csv(os.path.join(B, "downloads_log.csv"), index=False)
raw = cat("*/extraction_raw.csv"); raw.to_csv(os.path.join(B, "extraction_raw.csv"), index=False)
ver = cat("batch_*_verification.csv"); ver.to_csv(os.path.join(B, "verification.csv"), index=False)
bib = cat("*/bib.csv")
if len(bib):
    bib = bib.drop_duplicates(subset=["url", "local_path", "used_in"])
    bib.to_csv(os.path.join(ROOT, "bibliography", "parts", "exp10_B_qbrs.csv"), index=False, columns=BIB_COLS)
STD = {f"{p}_{c}" for p in ["capex", "opex", "opinc"] for c in
       ["original_budget", "revised_budget_prior", "variation_this_quarter", "projected_year_end", "ytd_actual"]}
STD |= {"opres_original_budget", "opres_projected_year_end"}
if len(raw):
    base = raw["item"].str.replace(r"_(general|water|sewer)$", "", regex=True)
    tidy = raw[base.isin(STD) | raw["item"].str.startswith("disaster")].copy()
    tidy["value_aud"] = pd.to_numeric(tidy["value_aud"].str.replace(",", ""), errors="coerce")
    lab = tidy["label"].str.lower()
    routine = lab.str.contains(r"emergency services? levy|fire service levy|esl\b|rfs maint|rural fire service maint|fire (?:fighting|service) (?:levy|contribution)", regex=True)
    recovery = lab.str.contains(r"bushfire|bush fire|drfa|ndrra|disaster recovery|natural disaster|recovery|blazeaid|black summer|storm|flood", regex=True)
    tidy["disaster_class"] = ""
    d = tidy["item"].str.startswith("disaster")
    tidy.loc[d, "disaster_class"] = "other_check"
    tidy.loc[d & recovery, "disaster_class"] = "disaster_recovery"
    tidy.loc[d & routine & ~recovery, "disaster_class"] = "routine_emergency_services"
    tidy = tidy.rename(columns={"council": "council_pdf"})
    tidy["region_id"] = tidy["region_id"].astype(int)
    tidy = tidy.merge(plan[["region_id", "region_name", "group"]].rename(columns={"region_name": "council"}), on="region_id", how="left")
    cols = ["region_id", "council", "group", "fy", "quarter", "item", "disaster_class", "value_aud", "page", "label", "file", "notes"]
    tidy[cols].sort_values(["region_id", "fy", "quarter", "item"]).to_csv(os.path.join(B, "qbrs_tidy.csv"), index=False)
# coverage
fys = ["2018-19", "2019-20", "2020-21", "2021-22"]; qs = ["Q1", "Q2", "Q3"]
rows = []
for r in plan.itertuples():
    d = dl[(dl.region_id == str(r.region_id)) & (dl.status == "downloaded")] if len(dl) else pd.DataFrame()
    x = raw[raw.region_id == str(r.region_id)] if len(raw) else pd.DataFrame()
    for fy in fys:
        for q in qs:
            xx = x[(x.fy == fy) & (x.quarter == q)] if len(x) else pd.DataFrame()
            it = set(xx["item"]) if len(xx) else set()
            rows.append(dict(region_id=r.region_id, council=r.region_name, group=r.group, tier=r.tier, fy=fy, quarter=q,
                doc_downloaded=int(len(d[(d.fy == fy) & (d.quarter == q)]) > 0) if len(d) else 0,
                capex_orig=int(any(i.startswith("capex_original") for i in it)),
                capex_revised=int(any(i.startswith("capex_projected") or i.startswith("capex_revised") for i in it)),
                opex_orig=int(any(i.startswith("opex_original") for i in it)),
                opex_revised=int(any(i.startswith("opex_projected") or i.startswith("opex_revised") for i in it)),
                disaster_rows=sum(i.startswith("disaster") for i in it if True) if len(xx) == 0 else int(xx["item"].str.startswith("disaster").sum())))
cov = pd.DataFrame(rows); cov.to_csv(os.path.join(B, "coverage_by_quarter.csv"), index=False)
byc = cov.groupby(["region_id", "council", "group", "tier"]).agg(quarters_with_doc=("doc_downloaded", "sum"),
    quarters_capex_orig_and_rev=("capex_revised", lambda s: int(((cov.loc[s.index, "capex_orig"] == 1) & (s == 1)).sum())),
    quarters_opex_orig_and_rev=("opex_revised", lambda s: int(((cov.loc[s.index, "opex_orig"] == 1) & (s == 1)).sum())),
    disaster_rows=("disaster_rows", "sum")).reset_index().sort_values(["tier", "region_id"])
byc.to_csv(os.path.join(B, "coverage_by_council.csv"), index=False)
print("downloads", len(dl), "ok", int((dl.status == "downloaded").sum()) if len(dl) else 0,
      "bytes", pd.to_numeric(dl.get("bytes", pd.Series(dtype=str)), errors="coerce")[dl.status == "downloaded"].sum() if len(dl) else 0)
print("raw rows", len(raw), "bib rows", len(bib), "verification rows", len(ver))
if len(ver): print(ver.verdict.value_counts().to_string())
print(byc.to_string())
