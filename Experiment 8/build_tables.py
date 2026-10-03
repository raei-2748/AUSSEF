"""Experiment 8: build mechanisms.csv, sources.csv, DATA_MAP.csv, the frequency chart and the bibliography part
from the multi-agent workflow output (raw/workflow_result.json) and the agents' web trace (raw/agent_web_trace.json).

Critic edits (pillar fixes, evidence downgrades, added mechanisms) are applied here, in code, so they are visible.
Run from this folder: python3 build_tables.py   (needs pandas + matplotlib)
"""
import csv
import json
from pathlib import Path
from urllib.parse import urlparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RES = json.loads((HERE / "raw/workflow_result.json").read_text())
TRACE = json.loads((HERE / "raw/agent_web_trace.json").read_text())
ACCESSED = "2026-10-02"
# Ray's rule: no Australian Community Media (ACM) mastheads (their terms bar AI use). Host list is shared project-wide.
ACM_HOSTS = [l.strip() for l in open(ROOT / "bibliography/acm_hosts.txt") if l.strip() and not l.startswith("#")]
ADD = json.loads((HERE / "raw/acm_replacement_records.json").read_text())  # replacement evidence found after exclusion


def is_acm(url):
    h = urlparse(str(url).strip()).netloc.lower().split(":")[0]
    return any(h == a or h.endswith("." + a) for a in ACM_HOSTS)


TYPE_SHORT = {
    "peer-reviewed literature": "lit",
    "government / inquiry / agency report": "gov",
    "news / first-person account": "news",
    "survey / interview study": "survey",
}
ORDER = ["lit", "gov", "news", "survey"]

# ---------- records and unique sources ----------
recs = pd.DataFrame(RES["records"] + [{k: v for k, v in r.items() if k != "mech_id"} for r in ADD["records"]])
recs["url"] = recs["url"].str.strip()
acm_recs = recs[recs.url.map(is_acm)].copy()
recs = recs[~recs.url.map(is_acm)].copy()
recs["stype"] = recs["source_type"].map(TYPE_SHORT)
recs["url"] = recs["url"].str.strip()
# one source = one URL; if several sweeps found the same URL it counts once, under the first sweep (lit, gov, news, survey)
recs["order"] = recs["stype"].map(ORDER.index)
first = recs.sort_values("order", kind="stable").drop_duplicates("url")
url_type = dict(zip(first["url"], first["stype"]))
url_sid = {u: f"E8S{i+1:03d}" for i, u in enumerate(first["url"])}
recs["source_id"] = recs["url"].map(url_sid)

mechs = pd.DataFrame(RES["normalise"]["mechanisms"])
rec2mech = {r: m["mech_id"] for m in RES["normalise"]["mechanisms"] for r in m["record_ids"]}
rec2mech.update({r["id"]: r["mech_id"] for r in ADD["records"]})
keep = set(recs["id"])
mechs["record_ids"] = mechs.mech_id.map(lambda m: [r for r, mm in rec2mech.items() if mm == m and r in keep])
acm_recs["mech_id"] = acm_recs["id"].map(rec2mech)
recs["mech_id"] = recs["id"].map(rec2mech).fillna("dropped")

# ---------- critic edits ----------
PILLAR_FIX = {
    "M27": ("IL", "Critic: volunteer days away from paid work are lost labour/earnings (IL); compensation payments sit in FP."),
    "M35": ("FP", "Critic: disaster payments are public spending (FP); cushioning SL is a secondary moderator role."),
    "M43": ("SL", "Critic: NSW rates are pegged (IPART), so value changes shift rates between ratepayers rather than cut council revenue; household wealth (SL), weak FP link."),
    "M44": ("X", "Critic: count of declared disasters before/after each fire per LGA is a covariate/moderator X, not a Y part."),
}
DOWNGRADE = {"M07": "moderate", "M19": "moderate", "M20": "moderate", "M29": "moderate"}
CAVEAT = {c["mech_id"]: c["problem"] for c in RES["critic"]["unsupported_claims"]}
mechs["pillar_original"] = mechs["pillar"]
mechs["critic_note"] = ""
for mid, (p, why) in PILLAR_FIX.items():
    mechs.loc[mechs.mech_id == mid, ["pillar", "critic_note"]] = [p, why]
for mid, s in DOWNGRADE.items():
    mechs.loc[mechs.mech_id == mid, "evidence_strength"] = s
mechs.loc[mechs.mech_id == "M32", "critic_note"] = (
    "Critic: smoke exposure itself should enter as an X variable (smoke days per council-fire), not a separate smoke study.")
mechs.loc[mechs.mech_id == "M16", "critic_note"] = (
    "Critic: movers vs stayers needs linked individual data (restricted); area data cannot test it.")
for mid, prob in CAVEAT.items():
    i = mechs.mech_id == mid
    mechs.loc[i, "critic_note"] = (mechs.loc[i, "critic_note"] + " Evidence caveat: " + prob).str.strip()

# key numbers that came from ACM articles are replaced with non-ACM evidence already in the sweep, or dropped
KQE = {
    "M03": "About 2 years before farm income resumes; 13,300 of 14,000 plants lost, 4-5 years to recover production (ABC Rural)",
    "M04": "50,000 of 168,000 ha of regional softwood plantation burnt; 42% salvaged; softwood employs 11,000+ in the region (ABC Rural 2023); about 5,000 jobs depend on the A$2bn Riverina industry (ABC 2020)",
    "M05": "Industry estimate about A$40m, NSW association up to A$100m incl. tourism (ABC/MDPI)",
    "M06": "South Coast NSW visitor spend -23% (A$251m) in Mar qtr 2020 (TRA); A$2.8b output and about 7,300 jobs lost nationally (Reiner et al.); about half of 120 Merimbula chamber members had takings down 60%+ (Region)",
    "M08": "Retail -0.3% in Jan 2020, department stores -2.2%, ACT -2.3% (ABS); two-thirds of 500 SMEs affected, mostly indirectly (NAB survey)",
    "M19": "Rent +A$20/week (~10%), +A$26 (13%) in disadvantaged areas after Black Summer (Akter & Grafton); Camp Fire: nearby prices +13% within six weeks (Hennighausen & James); Eurobodalla rents up almost 50% in five years to Dec 2022 (Region)",
    "M22": "Emergency Services Levy and taxes over 50% of NSW premiums (ICA via Insurance News, industry claim); monthly-payment surcharges up to 20% (ACCC)",
    "M30": "About 600 NSW schools closed in late 2019 (CESE media summary); about 64,600 new displacements recorded (IDMC)",
    "M36": "Only 7 of 90 Merimbula respondents had physical damage, so most were ineligible (Region); ~60% of SMEs wanted cash grants (NAB); 49% of support-line callers sought grant/loan help (ASBFEO)",
    "M41": "Commonwealth paid up to 75% of state recovery costs above thresholds (Productivity Commission)",
    "M43": "California 2018-21: homes farther from past fires ~2% higher value (FRBSF); Kinglake prices ~+150% in 10 years (analyst comment)",
    "M45": "202 interviews and 1,004 survey responses on Christmas-period displacement (BNHCRC Hazard Note 95)",
}
for mid, txt in KQE.items():
    mechs.loc[mechs.mech_id == mid, "key_quant_evidence"] = txt
mechs["critic_note"] = mechs.critic_note.str.replace(", and the Mallacoota listings are anecdotal", "", regex=False)  # ACM-sourced

ADDED = [
    ("M46", "Deaths and injuries", "Fire kills and injures people (lost lives, burns, long recovery).", "DL",
     "DL: deaths and injuries per 100,000 (severity tiers)", "added by critic"),
    ("M47", "Public infrastructure and council assets damaged", "Roads, bridges, water/sewer, halls destroyed; the repair bill then flows to FP.", "DL",
     "DL: infrastructure damage; cost side in FP (DRFA restoration claims)", "added by critic"),
    ("M48", "Destroyed homes owned by non-residents (holiday homes)", "Where many lost homes were holiday homes, the loss falls on owners living elsewhere, so local resident income and jobs move less.", "X",
     "X / moderator of DL -> IL/SL: pre-fire unoccupied-dwelling share (Census 2016)", "added by critic"),
    ("M49", "Insurance payouts as a local money inflow", "Claims paid replace lost wealth and pay local builders, cushioning local income.", "Moderator",
     "Moderator of DL -> SL/IL (insured share of loss)", "added by critic"),
    ("M50", "Concurrent drought amplifies and confounds farm loss", "The 2017-20 drought made farm fire losses worse and blurs any fire-only farm effect.", "X",
     "X: pre-fire rainfall deciles / drought status per council", "added by critic"),
    ("M51", "Government-funded clean-up and debris removal", "State and Commonwealth paid to clear destroyed properties (a large cost per destroyed home).", "FP",
     "FP: clean-up spending per destroyed home", "added by critic"),
    ("M52", "Park, forest and road closures extend tourism loss", "National parks and state forests stayed closed for months, so visitor loss outlasts the fire.", "IL",
     "IL: park-closure days per council (tourism loss duration)", "added by critic"),
    ("M53", "Aboriginal cultural and Country loss", "Loss of cultural sites and Country is a separate social loss for Aboriginal communities (Royal Commission).", "SL",
     "SL: note only (hard to measure)", "added by critic"),
    ("M54", "Bank hardship deferrals hide financial stress", "Mortgage deferrals after the fires (then COVID) delay arrears for 6-12 months.", "Moderator",
     "Moderator of SL hardship timing", "added by critic"),
    ("M55", "Capital recovery spending and disaster grants / DRFA reimbursement", "Councils spend on rebuilding roads, bridges and buildings; part is reimbursed later through disaster grants (DRFA), with timing gaps and unfunded parts.", "FP",
     "FP: council capital purchases (cash-flow statement) and natural-disaster grant lines in audited financial statements and Quarterly Budget Review Statements; being collected in Experiment 10 (not duplicated here)", "added by Ray (2 Oct)"),
]
add = pd.DataFrame([dict(mech_id=a, name=b, description=c, pillar=d, pillar_original=d, pillar_note=e,
                         affected_group="", direction="worse", time_scale="", evidence_strength="not swept",
                         key_quant_evidence="", record_ids=[], critic_note=f) for a, b, c, d, e, f in ADDED])
mechs = pd.concat([mechs, add], ignore_index=True)

# ---------- frequency by source type (unique URLs) ----------
used = recs[recs.mech_id != "dropped"]
for t in ORDER:
    mechs[f"n_{t}"] = mechs.mech_id.map(
        lambda m: int(used[used.mech_id == m]["url"].drop_duplicates().map(url_type).eq(t).sum()))
mechs["n_sources"] = mechs[[f"n_{t}" for t in ORDER]].sum(axis=1)
mechs["n_records"] = mechs.record_ids.map(len)

# ---------- data map ----------
maps = {m["mech_id"]: m for m in RES["mappings"]}
mechs["exp7_status"] = mechs.mech_id.map(lambda m: maps[m]["exp7_status"] if m in maps else "not tested")
mechs["exp7_result"] = mechs.mech_id.map(lambda m: maps[m]["exp7_result"] if m in maps else "")
mechs["fine_grain_feasible"] = mechs.mech_id.map(lambda m: maps[m]["fine_grain_feasible"] if m in maps else "")
mechs["best_data"] = mechs.mech_id.map(
    lambda m: "; ".join(f"{d['dataset']} ({d['geography']}, {d['time_step']}, {d['access']})" for d in maps[m]["datasets"][:3])
    if m in maps else "")
mechs.loc[mechs.mech_id == "M48", ["best_data", "fine_grain_feasible"]] = [
    "ABS Census 2016 GCP DataPack: unoccupied private dwellings by SA1/SA2 (open)", "yes"]
mechs.loc[mechs.mech_id == "M55", ["best_data", "fine_grain_feasible"]] = [
    "NSW council audited financial statements + Quarterly Budget Review Statements (being collected in Experiment 10)", "partly"]

rank = {"strong": 0, "moderate": 1, "weak": 2, "not swept": 3}
mechs["_r"] = mechs.evidence_strength.map(rank)
mechs = mechs.sort_values(["n_sources", "_r"], ascending=[False, True]).reset_index(drop=True)
mechs.insert(0, "rank", range(1, len(mechs) + 1))
cols = ["rank", "mech_id", "name", "pillar", "pillar_original", "pillar_note", "description", "affected_group",
        "direction", "time_scale", "n_sources", "n_lit", "n_gov", "n_news", "n_survey", "n_records",
        "evidence_strength", "key_quant_evidence", "exp7_status", "exp7_result", "fine_grain_feasible", "best_data",
        "critic_note"]
out = mechs[cols].copy()
out["record_ids"] = mechs.record_ids.map(" ".join)
out.to_csv(HERE / "mechanisms.csv", index=False)

# ---------- sources.csv ----------
src = (recs.groupby("source_id").agg(
    url=("url", "first"), title=("source_title", "first"), author_or_outlet=("author_or_outlet", "first"),
    year=("year", "first"), place=("place", "first"), disaster=("disaster", "first"),
    found_by=("stype", lambda s: " ".join(sorted(set(s), key=ORDER.index))),
    mech_ids=("mech_id", lambda s: " ".join(sorted(set(s)))),
    record_ids=("id", " ".join)).reset_index())
src.insert(3, "source_type", src.url.map(url_type))
fetch = TRACE["fetch"]
src["opened_by_agent"] = src.url.map(lambda u: "yes" if u in fetch else "no (search-result summary)")
src["fetch_possibly_failed"] = src.url.map(lambda u: "yes" if fetch.get(u, {}).get("fail") else "")
src.to_csv(HERE / "sources.csv", index=False)

acm_recs[["id", "mech_id", "author_or_outlet", "source_title", "url"]].to_csv(HERE / "sources_excluded_acm.csv", index=False)

# ---------- DATA_MAP.csv ----------
rows = [dict(mech_id=m["mech_id"], **d, exp7_status=m["exp7_status"]) for m in RES["mappings"] for d in m["datasets"]]
dm = pd.DataFrame(rows)
dm["pillar"] = dm.mech_id.map(dict(zip(mechs.mech_id, mechs.pillar)))
dm = dm[["mech_id", "pillar", "dataset", "publisher", "url", "geography", "time_step", "years", "approx_size",
         "access", "notes", "exp7_status"]].sort_values(["pillar", "mech_id"])
dm.to_csv(HERE / "DATA_MAP.csv", index=False)

# ---------- chart ----------
COL = {"DL": "#2a78d6", "IL": "#eb6834", "FP": "#1baf7a", "SL": "#eda100", "X": "#e87ba4", "Moderator": "#008300"}
ch = mechs[mechs.n_sources > 0].sort_values("rank", ascending=False)
fig, ax = plt.subplots(figsize=(9, 0.25 * len(ch) + 1.7), dpi=150)
ax.barh(range(len(ch)), ch.n_sources, color=ch.pillar.map(COL), height=0.72, edgecolor="white", linewidth=1)
ax.set_yticks(range(len(ch)))
ax.set_yticklabels([f"{r.name}  ({r.mech_id})" for r in ch.itertuples()], fontsize=7.3)
for i, v in enumerate(ch.n_sources):
    ax.text(v + 0.15, i, str(v), va="center", fontsize=7, color="#444")
ax.set_xlabel("Distinct sources (unique web pages) reporting the mechanism", fontsize=9)
fig.suptitle(f"How often each fire -> socioeconomic mechanism is reported, coloured by Bowen's pillar\n"
             f"({len(recs)} records, {len(src)} unique sources: papers, government/inquiry, news, surveys)\n"
             f"Experiment 8, 2 Oct 2026", fontsize=9.5, x=0.01, ha="left")
ax.set_ylim(-0.7, len(ch) - 0.3)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
ax.grid(axis="x", color="#ddd", linewidth=0.6)
ax.set_axisbelow(True)
present = [p for p in COL if p in set(ch.pillar)]
names = {"DL": "DL direct loss", "IL": "IL indirect loss", "FP": "FP fiscal pressure", "SL": "SL social loss",
         "X": "X variable", "Moderator": "Moderator"}
ax.legend([plt.Rectangle((0, 0), 1, 1, color=COL[p]) for p in present], [names[p] for p in present],
          loc="lower right", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(HERE / "fig_mechanism_frequency.png")

# ---------- bibliography part (project rule: log every source read, searched or used) ----------
BIB_COLS = ["source_id", "title", "author_or_publisher", "year", "source_type", "url", "doi", "accessed_date",
            "local_path", "bytes", "sha256", "used_in", "what_it_was_used_for", "pages_or_table", "quote_or_value", "notes"]


def btype(t, url):
    if t in ("lit",):
        return "journal_article"
    if t == "news":
        return "news"
    if t == "survey":
        return "survey"
    return "pdf_report" if url.lower().endswith(".pdf") else "government_page" if ".gov.au" in url else "web_page"


bib, seen = [], set()
for r in src.itertuples():
    q = recs[recs.source_id == r.source_id]["quant_evidence"].replace("", pd.NA).dropna()
    f = fetch.get(r.url, {})
    note = ("link possibly failed for agent 2026-10-02 (403/timeout); record based on search summary" if f.get("fail")
            else "" if f else "not opened in full by agent; record based on search-result summary")
    bib.append(dict(source_id=r.source_id, title=r.title, author_or_publisher=r.author_or_outlet, year=r.year,
                    source_type=btype(r.source_type, r.url), url=r.url, accessed_date=ACCESSED,
                    used_in="Experiment 8/mechanisms.csv; MECHANISMS.md",
                    what_it_was_used_for=f"mechanism evidence ({r.mech_ids})",
                    quote_or_value=(" ".join(q.iloc[0].split()[:25]) if len(q) else ""), notes=note))
    seen.add(r.url)
n = 0
for d in RES["mappings"]:
    for x in d["datasets"]:
        u = x["url"].strip()
        if u in seen:
            continue
        seen.add(u)
        n += 1
        f = fetch.get(u, {})
        bib.append(dict(source_id=f"E8D{n:03d}", title=x["dataset"], author_or_publisher=x["publisher"], year=x["years"],
                        source_type="dataset", url=u, accessed_date=ACCESSED, used_in="Experiment 8/DATA_MAP.csv",
                        what_it_was_used_for=f"candidate data for {d['mech_id']} (NOT downloaded)",
                        notes=("link possibly failed for agent 2026-10-02" if f.get("fail")
                               else "" if f else "page described from search results; not opened in full")))
n = 0
for u, f in fetch.items():
    if not u or u in seen:
        continue
    seen.add(u)
    n += 1
    bib.append(dict(source_id=f"E8F{n:03d}", title="(page opened by agent; title not recorded)", source_type="web_page",
                    url=u, accessed_date=ACCESSED, used_in="opened, not used",
                    notes=f"agent {f['label']}" + ("; link possibly failed 2026-10-02" if f.get("fail") else "")))
n = 0
for u, (title, lab, query) in TRACE["hits"].items():
    if u in seen:
        continue
    seen.add(u)
    n += 1
    bib.append(dict(source_id=f"E8H{n:04d}", title=title, source_type="other", url=u, accessed_date=ACCESSED,
                    used_in="searched, not used", notes=f"web-search result for query: {query}"))
for u, t in ADD["search"]["hits"]:
    if u not in seen:
        seen.add(u)
        n += 1
        bib.append(dict(source_id=f"E8H{n:04d}", title=t, source_type="other", url=u, accessed_date=ACCESSED,
                        used_in="searched, not used", notes=f"web-search result for query: {ADD['search']['query']}"))
for r in acm_recs.drop_duplicates("url").itertuples():
    if r.url not in seen:
        seen.add(r.url)
        n += 1
        bib.append(dict(source_id=f"E8A{n:04d}", title=r.source_title, author_or_publisher=r.author_or_outlet,
                        year=r.year, source_type="news", url=r.url, accessed_date=ACCESSED))
for b in bib:
    if is_acm(b["url"]):
        b["used_in"] = "excluded: ACM (AI-use ban)"
        b["what_it_was_used_for"] = ""
        b["quote_or_value"] = ""
with open(ROOT / "bibliography/parts/exp8_mechanisms.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=BIB_COLS)
    w.writeheader()
    for b in bib:
        w.writerow({k: b.get(k, "") for k in BIB_COLS})

print(f"ACM excluded: {len(acm_recs)} records, {acm_recs.url.nunique()} sources")
print(f"mechanisms {len(out)}  sources {len(src)}  data rows {len(dm)}  bibliography rows {len(bib)}")
print(out.groupby("pillar").agg(n=("mech_id", "count"), sources=("n_sources", "sum")))
print(out[["rank", "mech_id", "name", "pillar", "n_sources", "n_lit", "n_gov", "n_news", "n_survey",
           "evidence_strength", "exp7_status"]].to_string())
