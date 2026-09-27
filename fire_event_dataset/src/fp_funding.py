"""FP (fiscal pressure) inputs: disaster recovery money reaching NSW councils, council-reported damage costs, and the
capital-side council finance items the OLG Time Series lets us compute.

What public data exist (searched 2026-09-27; see the module README section in the report / data/raw/fp/urls.txt):

  A. Grants and allocations to councils, by council (2019-20 Black Summer bushfires only; no other fire season has a
     published council-level list):
     1. NBRA "Local Government Area Grants Package" (Commonwealth): initial $1m (announced 9 Jan 2020) + share of the
        $17m (13 Feb 2020) per council. Published figures are rounded ("$1.416 million").
     2. BCRRF Stream 1 (Commonwealth-NSW, DRFA): $250,000 or $100,000 per council (joint release, 29 Sep 2020).
     3. NSW EPA Bushfire-generated green waste, Stream B (DRFA): 15 councils, $31.5m.
     4. NSW EPA Bushfire Recovery Program for Council Landfills, Phase 2: 15 councils, $22.1m.
  B. Project funding located in an LGA (recipient may be a council, NGO, business ...):
     5. BLER (Bushfire Local Economic Recovery) by LGA: Audit Office of NSW, "Bushfire recovery grants" (2022),
        Appendix two - Fast-Tracked, SDG and Open-round projects and total $ per LGA. All three rounds were announced
        Sep 2020 - Jun 2021 (report p.7 and p.10), i.e. FY 2020-21.
     6. Black Summer Bushfire Recovery (BSBR) Grants, Commonwealth: project list with LGA(s) and approved amount
        (NRRA, archived 15 Aug 2022). Multi-LGA projects are NOT split across LGAs (amount kept whole, flagged).
  C. Council-reported damage-cost estimates vs funding received (the reconstruction-gap ingredients):
     7. Audit Office of NSW, "Report on Local Government 2020", pp.32-33 (PDF pages): six bushfire councils, 2019-20.
        Transcribed by hand to data/raw/fp/audit_lg2020_council_impacts.csv; every number is checked against the
        quote, and every quote against the PDF page text, at build time.
  D. Council capital side (all councils x FY), from the NSW OLG Time Series files already in data/olg/:
     8. capital_grants_contributions_aud_derived = total revenue from continuing operations - total expenses from
        continuing operations - net operating result before capital grants & contributions. An accounting identity on
        three OLG-published $ figures, not a published number; OLG publishes the NOR-before-capital line only from
        2019-20. Rows failing a sanity check (negative, or larger than grants & contributions % x revenue) are flagged.
     9. asset_maintenance_actual_aud / asset_maintenance_required_aud: OLG-published $ (not parsed by src/olg.py).

What does NOT exist publicly (so FP_reconstruction_gap_raw cannot be filled for all councils):
  - DRFA (or NDRRA) claims or payments by council and year. NSW Public Works / Resilience NSW / NSW Reconstruction
    Authority publish only state totals (e.g. $81.7m eligible EPAR expenditure in 2019-20, LG 2020 report p.36).
  - Council capital expenditure in dollars in any consolidated dataset (OLG Time Series has only the renewals ratio;
    ABS GFS has no council detail). It sits only in each council's audited financial statements (PDF).
  - Council damage estimates for all councils: only the Audit Office examples above (2019-20) and a region-level
    table for 2021-22 floods ("Natural disasters", 2023).

Output: data/enrich/fp_funding.parquet (+ .csv), long format, one row per region_id x fy x program x measure
(project detail for BSBR / multi-LGA in data/enrich/fp_funding_projects.parquet + .csv). Blank = unknown, never 0.
A 0 appears only where the source prints '--' for an eligible LGA with no funded BLER project.

Run from fire_event_dataset/:  uv run --no-sync --with pdfplumber --with openpyxl --with xlrd --with pyogrio python -m src.fp_funding
"""
import html as htmlmod
import json
import re
from unittest import mock

import numpy as np
import pandas as pd
import pdfplumber
import pyogrio

from src import olg
from src.common import DATA, PHASE1, record_source

FP = DATA / "raw/fp"
ENRICH = DATA / "enrich"
LGA_SHP = PHASE1 / "raw/lga_2021/LGA_2021_AUST_GDA94.shp"
WB = "http://web.archive.org/web/"
AUDIT = "https://www.audit.nsw.gov.au/sites/default/files/documents/"
NBRA = "https://www.bushfirerecovery.gov.au/"
EVENT_BS = "2019-20 Black Summer bushfires"

SOURCES = {  # local file -> (name, URL actually downloaded, original URL if archived, licence, note)
    "audit_Appendix_two_-_Bushfire_recovery_grants.pdf": (
        "Audit Office of NSW, Bushfire recovery grants (2022), Appendix two - BLER program distribution",
        AUDIT + "Appendix%20two%20-%20Bushfire%20recovery%20grants.pdf", "", "CC BY 4.0 (Audit Office of NSW)",
        "BLER projects and total funding per LGA, PDF pp.1-2 (report pp.40-41)"),
    "audit_Bushfire_recovery_grants.pdf": (
        "Audit Office of NSW, Bushfire recovery grants (2022), full report",
        AUDIT + "Bushfire%20recovery%20grants.pdf", "", "CC BY 4.0 (Audit Office of NSW)",
        "round announcement dates: PDF p.7 (SDG Sep 2020, Fast-Tracked Oct 2020), p.10 (195 open-round Jun 2021)"),
    "audit_lg2020_report.pdf": (
        "Audit Office of NSW, Report on Local Government 2020",
        AUDIT + "Report%20on%20Local%20Government%202020.pdf", "", "CC BY 4.0 (Audit Office of NSW)",
        "council bushfire impacts PDF pp.32-33; state DRFA EPAR total p.36; BCRRF counts p.37"),
    "audit_lg2020_council_impacts.csv": (
        "Hand transcription of Audit Office LG 2020 pp.32-33 (verbatim quotes, checked against the PDF at build)",
        "data/raw/fp/audit_lg2020_council_impacts.csv", AUDIT + "Report%20on%20Local%20Government%202020.pdf",
        "derived", "one row per figure; quote + PDF page"),
    "nbra_local_council_list_20210309.pdf": (
        "National Bushfire Recovery Agency, Local Government Area Grants Package - local council list",
        WB + "20210309162441id_/" + NBRA + "sites/default/files/files/Local%20council%20list_%20PDF%20download.pdf",
        NBRA + "sites/default/files/files/Local%20council%20list_%20PDF%20download.pdf",
        "CC BY 4.0 (Commonwealth)", "Wayback copy (site retired); 'Total support received' per council, all states"),
    "nbra_more_funding_lg.html": (
        "NBRA media release 13 Feb 2020: More funding for Local Governments recovering from bushfires",
        WB + "20210928190011/" + NBRA + "news/more-funding-local-governments-recovering-bushfires",
        NBRA + "news/more-funding-local-governments-recovering-bushfires", "CC BY 4.0 (Commonwealth)",
        "explains package = initial $1m (PM, 9 Jan 2020) + $17m to 60 LGAs ($200,000-$416,667)"),
    "homeaffairs_bcrrf_stream1_release.html": (
        "Joint media release Littleproud/Toole 29 Sep 2020: NSW Bushfire Community and Resilience Fund grants",
        WB + "20201101051538id_/https://minister.homeaffairs.gov.au/davidlittleproud/Pages/"
             "nsw-bushfire-community-resilience-fund-grants.aspx",
        "https://minister.homeaffairs.gov.au/davidlittleproud/Pages/nsw-bushfire-community-resilience-fund-grants.aspx",
        "CC BY 4.0 (Commonwealth)", "BCRRF Stream 1 council table ($250,000 / $100,000)"),
    "bsbr_approved_projects_20220815.pdf": (
        "NRRA, Black Summer Bushfire Recovery Grants - Approved Projects",
        WB + "20220815212716id_/https://recovery.gov.au/sites/default/files/BSBR%20-%20Approved%20Projects..pdf",
        "https://recovery.gov.au/sites/default/files/BSBR%20-%20Approved%20Projects..pdf", "CC BY 4.0 (Commonwealth)",
        "project x LGA(s) x state x approved amount; first archived 2 Mar 2022"),
    "epa_green_waste.html": (
        "NSW EPA, Bushfire-generated green waste clean-up and processing program (Stream B recipients)",
        "https://epa.nsw.gov.au/Working-together/Grants/Bushfire-recovery-programs/"
        "Bushfire-generated-green-waste-clean-up-and-processing-program", "", "CC BY 4.0 (NSW EPA)",
        "funded under DRFA; page 'Updated 26 October 2021'"),
    "epa_council_landfills.html": (
        "NSW EPA, Bushfire Recovery Program for Council Landfills (Phase 2 recipients)",
        "https://epa.nsw.gov.au/Working-together/Grants/Bushfire-recovery-programs/Council-landfills", "",
        "CC BY 4.0 (NSW EPA)", "page 'Updated 24 November 2021'; table absent from the 22 Oct 2021 Wayback copy"),
}

EXTRA_ALIASES = {"glen innes": "glen innes severn", "mid coast": "midcoast"}
# LGA names shared with councils in other states; only matters for multi-state BSBR projects
AMBIGUOUS = {"centralcoast", "campbelltown", "bayside"}


def key(name):
    k = olg.norm_name(str(name).replace("\n", " "))
    k = EXTRA_ALIASES.get(k, k)
    return k.replace(" ", "")


def lga_names():
    l = pyogrio.read_dataframe(LGA_SHP, read_geometry=False)
    l = l[l.STE_NAME21 == "New South Wales"]
    return {key(n): (str(c), n) for c, n in zip(l.LGA_CODE21, l.LGA_NAME21)}


def aud(s):
    """'$1.416 million' -> 1416000.0 ; '$200,000' -> 200000.0 ; '--' -> None."""
    s = str(s).strip().replace("\xa0", " ")
    m = re.fullmatch(r"\$?\s*([\d.,]+)\s*(million|m)?", s, re.I)
    if not m:
        return None
    v = float(m.group(1).replace(",", ""))
    return v * 1e6 if m.group(2) else v


def page_text(pdf, page):
    with pdfplumber.open(FP / pdf) as p:
        return p.pages[page - 1].extract_text() or ""


def html_text(fn):
    h = (FP / fn).read_text(errors="ignore")
    h = re.sub(r"<(script|style).*?</\1>", "", h, flags=re.S)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", "\n", h))
    return re.sub(r"\n\s*\n+", "\n", t)


def row(**kw):
    base = dict(region_id=None, region_name=None, source_council_name=None, successor_region_id=None, fy=None,
                fy_basis=None, event=None, hazard=None, program=None, funder=None, recipient_type=None, measure=None,
                amount_aud=np.nan, amount_as_published=None, n_projects=np.nan, check_flag=None, source_file=None,
                source_url=None, source_locator=None, quote=None, note=None)
    base.update(kw)
    return base


def put_region(r, names, name):
    k = key(name)
    if k in names:
        r["region_id"], r["region_name"] = names[k]
    return r


# ---------------------------------------------------------------- A1 NBRA council package
def nbra(names):
    fn = "nbra_local_council_list_20210309.pdf"
    out = []
    with pdfplumber.open(FP / fn) as p:
        for tb in p.pages[0].extract_tables():
            for cells in tb:
                cells = [c for c in cells if c]
                amt = [c for c in cells if str(c).startswith("$")]
                nm = [c for c in cells if not str(c).startswith("$")]
                if len(amt) != 1 or len(nm) != 1:
                    continue
                r = put_region(row(source_council_name=nm[0], fy="2019-20",
                                   fy_basis="announced 9 Jan 2020 ($1m) and 13 Feb 2020 ($17m share)",
                                   event=EVENT_BS, hazard="bushfire",
                                   program="NBRA Local Government Area Grants Package (initial $1m + $17m distribution)",
                                   funder="Australian Government (National Bushfire Recovery Fund)",
                                   recipient_type="council", measure="grant_allocated_aud", amount_aud=aud(amt[0]),
                                   amount_as_published=amt[0], source_file=fn, source_locator="PDF p.1 table",
                                   note="'Total support received'; published figure is rounded (e.g. $1.416 million)"),
                               names, nm[0])
                out.append(r)
    d = pd.DataFrame(out)
    other = d[d.region_id.isna()].source_council_name.tolist()
    print(f"[nbra] {len(d)} councils listed, {d.region_id.notna().sum()} NSW; not NSW (dropped): {other}")
    return d[d.region_id.notna()]


# ---------------------------------------------------------------- A2 BCRRF Stream 1
def bcrrf(names):
    fn = "homeaffairs_bcrrf_stream1_release.html"
    h = (FP / fn).read_text(errors="ignore")
    tb = re.search(r"<table>.*?</table>", h[h.find("Stream 1 funding"):], re.S).group(0)
    heads = [htmlmod.unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<th[^>]*>(.*?)</th>", tb, re.S)]
    cols = re.findall(r"<td>(.*?)</td>", tb, re.S)
    out = []
    for head, col in zip(heads, cols):
        amt = re.search(r"\$[\d,]+", head).group(0)
        for li in re.findall(r"<li>(.*?)</li>", col, re.S):
            nm = htmlmod.unescape(re.sub(r"<[^>]+>", "", li)).strip()
            r = put_region(row(source_council_name=nm, fy="2020-21", fy_basis="joint media release 29 Sep 2020",
                               event=EVENT_BS, hazard="bushfire", program="BCRRF Stream 1 (Bushfire Community Recovery "
                               "and Resilience Fund)", funder="Australian and NSW Governments (DRFA Category C/D)",
                               recipient_type="council", measure="grant_allocated_aud", amount_aud=aud(amt),
                               amount_as_published=amt + " will be made available", source_file=fn,
                               source_locator="table 'BCRRF Stream 1 funding'",
                               note="min. 25% to be passed on as council-run small community grants"), names, nm)
            out.append(r)
    d = pd.DataFrame(out)
    assert d.region_id.notna().all(), d[d.region_id.isna()]
    assert (d.amount_aud == 250000).sum() == 27 and (d.amount_aud == 100000).sum() == 5  # Audit Office LG2020 p.37
    return d


# ---------------------------------------------------------------- A3/A4 EPA tables
def epa(names, fn, program, fy, fy_basis, note, total):
    t = html_text(fn)
    seg = t[t.find("Recipient"):t.find("Total =")]
    lines = [x.strip() for x in seg.split("\n") if x.strip()][2:]
    out = []
    for nm, amt in zip(lines[0::2], lines[1::2]):
        nm = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", nm)  # 'Richmond ValleyCouncil' (markup artefact)
        r = put_region(row(source_council_name=nm, fy=fy, fy_basis=fy_basis, event=EVENT_BS, hazard="bushfire",
                           program=program, funder="NSW Environment Protection Authority", recipient_type="council",
                           measure="grant_awarded_aud", amount_aud=aud(amt), amount_as_published=amt, source_file=fn,
                           source_locator="table 'Successful ... applicants'", note=note), names, nm)
        out.append(r)
    d = pd.DataFrame(out)
    assert d.region_id.notna().all(), d[d.region_id.isna()]
    stated = aud(re.search(r"Total = (\$[\d,]+)", t).group(1))
    assert abs(d.amount_aud.sum() - stated) < 1 and abs(stated - total) < 1, (d.amount_aud.sum(), stated)
    return d


# ---------------------------------------------------------------- B5 BLER by LGA (Audit Office)
def bler(names):
    fn = "audit_Appendix_two_-_Bushfire_recovery_grants.pdf"
    out = []
    with pdfplumber.open(FP / fn) as p:
        for pg in p.pages:
            for ln in (pg.extract_text() or "").split("\n"):
                m = re.match(r"^(.*?)\s+(\d+|--)\s+(\d+|--)\s+(\d+|--)\s+([\d,]+|--)$", ln.strip())
                if not m:
                    continue
                nm, ft, sdg, opn, tot = m.groups()
                n = sum(int(x) for x in (ft, sdg, opn) if x != "--")
                r = row(source_council_name=nm, fy="2020-21",
                        fy_basis="SDG announced Sep 2020, Fast-Tracked Oct 2020, open round Jun 2021 (report pp.7, 10)",
                        event=EVENT_BS, hazard="bushfire",
                        program="BLER Fund (Fast-Tracked + SDG + Open round), projects located in LGA",
                        funder="Australian and NSW Governments (Department of Regional NSW)",
                        recipient_type="any (councils, JOs, NGOs, businesses)", measure="project_funding_in_lga_aud",
                        amount_aud=0.0 if tot == "--" else aud(tot), amount_as_published=tot, n_projects=n,
                        source_file=fn, source_locator=f"PDF p.{pg.page_number} (Appendix two table)",
                        note=f"projects: Fast-Tracked {ft}, SDG {sdg}, Open round {opn}"
                             + ("; '--' = no funded project (eligible LGA)" if tot == "--" else ""))
                if nm.lower() == "total":
                    total = r
                    continue
                if nm == "Multiple LGAs":
                    r["region_name"] = "Multiple LGAs (not attributable)"
                else:
                    r = put_region(r, names, nm)
                out.append(r)
    d = pd.DataFrame(out)
    assert d.region_id.notna().sum() == len(d) - 1, d[d.region_id.isna()]
    assert abs(d.amount_aud.sum() - total["amount_aud"]) < 1 and d.n_projects.sum() == total["n_projects"]
    return d


# ---------------------------------------------------------------- B6 BSBR project list
def bsbr(names):
    fn = "bsbr_approved_projects_20220815.pdf"
    recs = []
    with pdfplumber.open(FP / fn) as p:
        for pg in p.pages:
            for tb in pg.extract_tables():
                for cells in tb:
                    if len(cells) < 5:
                        continue
                    if cells[0] and re.fullmatch(r"BSBR\d+", str(cells[0]).strip()):
                        recs.append(dict(project_id=cells[0].strip(), title=cells[1], lga_text=cells[2] or "",
                                         state=cells[3], amount=cells[4], page=pg.page_number))
                    elif recs and not cells[0] and cells[2]:  # row continued on the next page
                        recs[-1]["lga_text"] += "\n" + cells[2]
    proj = pd.DataFrame(recs)
    proj["state"] = proj.state.str.replace("\n", " ")
    proj["amount_aud"] = proj.amount.map(aud)
    assert proj.amount_aud.notna().all() and not proj.project_id.duplicated().any()
    txt = proj.lga_text.str.replace(r"-\s*\n\s*", "-", regex=True).str.replace("\n", " ")
    txt = txt.str.replace(r"\s*-\s+", "-", regex=True).str.replace(r"\s+", " ", regex=True)
    txt = txt.str.replace(r"\((including|incl)[^)]*\)", "", regex=True)  # Alpine Resorts note contains commas
    proj["lgas"] = txt.map(lambda s: [x.strip() for x in s.split(",") if x.strip()])
    proj["n_lgas"] = proj.lgas.str.len()
    rows = []
    for r in proj.itertuples():
        for nm in r.lgas:
            k = key(nm)
            if k not in names:
                continue
            if r.state not in ("NSW", "Multiple LGA"):
                continue  # a single-state non-NSW project whose LGA shares a name with an NSW one
            code, lname = names[k]
            rows.append(dict(project_id=r.project_id, project_title=r.title, region_id=code, region_name=lname,
                             source_lga_name=nm, state_column=r.state, n_lgas=r.n_lgas,
                             multi_state_ambiguous_name=(k in AMBIGUOUS and r.state != "NSW"),
                             approved_amount_aud=r.amount_aud, amount_as_published=r.amount,
                             source_file=fn, source_locator=f"PDF p.{r.page}"))
    pj = pd.DataFrame(rows)
    out = []
    for (code, single), g in pj.groupby(["region_id", pj.n_lgas == 1]):
        amt = g.approved_amount_aud.sum() if single else np.nan
        out.append(row(region_id=code, region_name=g.region_name.iloc[0], fy=None,
                       fy_basis="approval date not published; list first archived 2 Mar 2022",
                       event=EVENT_BS, hazard="bushfire", program="Black Summer Bushfire Recovery (BSBR) Grants",
                       funder="Australian Government (NRRA)", recipient_type="any (not named in list)",
                       measure="project_funding_in_lga_aud" if single else "multi_lga_project_funding_not_split_aud",
                       amount_aud=amt, n_projects=len(g),
                       check_flag=None if single else "multi-LGA projects: whole-project total in note, not split",
                       source_file=fn, source_locator="project list (see fp_funding_projects)",
                       note=None if single else f"sum of whole-project amounts of {len(g)} multi-LGA projects "
                                                f"touching this LGA = {g.approved_amount_aud.sum():,.0f} AUD"))
    print(f"[bsbr] {len(proj)} projects (all states, ${proj.amount_aud.sum():,.0f}); NSW-LGA links: {len(pj)}")
    return pd.DataFrame(out), pj


# ---------------------------------------------------------------- C7 Audit Office LG 2020 council impacts
def _quote_in(quote, text, max_gap=2):
    """Quote words appear in order in the page text, allowing up to max_gap stray tokens (two-column table layout)."""
    tok = lambda x: [w.rstrip(".,;:") for w in re.findall(r"[\w$.,%'-]+", x.lower())]
    q, t = tok(quote), tok(text)
    for i in range(len(t)):
        j, k, gap = 0, i, 0
        while j < len(q) and k < len(t) and gap <= max_gap:
            if t[k] == q[j]:
                j, gap = j + 1, 0
            else:
                gap += 1
            k += 1
        if j == len(q):
            return True
    return False


def audit_lg2020(names):
    fn = "audit_lg2020_council_impacts.csv"
    c = pd.read_csv(FP / fn)
    out = []
    for r in c.itertuples():
        txt = page_text("audit_lg2020_report.pdf", int(r.pdf_page))
        m = re.search(r"\$([\d,.]+)( million)?", r.quote)
        in_quote = m is not None and abs(aud(m.group(1) + (m.group(2) or "")) - r.amount_aud) < 1
        ok = in_quote and _quote_in(r.quote, txt)
        out.append(put_region(row(source_council_name=r.council_name, fy=r.fy, fy_basis="council financial year "
                                  "audited", event=EVENT_BS if "bushfire" in r.hazard else None, hazard=r.hazard,
                                  program="Audit Office of NSW, Report on Local Government 2020 (council examples)",
                                  funder=None, recipient_type="council", measure=r.measure,
                                  amount_aud=r.amount_aud if ok else np.nan, amount_as_published=m.group(0) if m else None,
                                  check_flag=None if ok else "quote/number check failed -> blanked",
                                  source_file="audit_lg2020_report.pdf", source_locator=f"PDF p.{r.pdf_page}",
                                  quote=r.quote, note=None if pd.isna(r.note) else r.note), names, r.council_name))
    d = pd.DataFrame(out)
    assert d.region_id.notna().all()
    bad = d.check_flag.notna().sum()
    print(f"[audit_lg2020] {len(d)} figures, {bad} failed the quote check")
    return d


# ---------------------------------------------------------------- D8/D9 OLG capital side
OLG_EXTRA = {"asset_maintenance_actual_aud": r"^actual asset maintenance expenditure",
             "asset_maintenance_required_aud": r"^required asset maintenance expenditure"}


def olg_rows(names):
    with mock.patch.object(olg, "METRICS", OLG_EXTRA):
        am = pd.concat([olg.parse_sheet(fn, sh, fy) for fy, fn, sh, prim in olg.SHEETS if prim and fy >= 2014],
                       ignore_index=True)
    am = am.pivot_table(index=["council_name", "fy_start"], columns="metric", values="value", aggfunc="first")
    w = pd.read_parquet(DATA / "olg/olg_wide.parquet")
    w = w[w.fy_start >= 2014].set_index(["council_name", "fy_start"])
    w = w.join(am, how="outer")
    w["cap"] = (w.total_revenue_continuing_ops_aud - w.total_expenses_continuing_ops_aud
                - w.net_operating_result_before_capital_aud)
    grants = w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud
    ratio = 100 * w.asset_maintenance_actual_aud / w.asset_maintenance_required_aud
    w["am_check"] = (ratio - w.asset_maintenance_ratio_pct).abs()
    files = {fy: fn for fy, fn, sh, prim in olg.SHEETS if prim}
    out = []
    for (nm, fy), r in w.iterrows():
        base = dict(source_council_name=nm, fy=f"{fy}-{str(fy + 1)[2:]}", fy_basis="council financial year",
                    program="NSW OLG Time Series Data", funder=None, recipient_type="council",
                    source_file="data/olg/" + files[fy], source_url=olg.URLS[files[fy]], source_locator="council sheet")
        k = key(nm)
        if k in names:
            base["region_id"], base["region_name"] = names[k]
        else:
            succ = olg.PREDECESSORS.get(olg.norm_name(nm))
            if succ is None:
                succ = olg.norm_name(re.sub(r"\(new\)", "", nm))
                if key(succ) in names:  # 'Parramatta (new)' etc. = the LGA-2021 council
                    base["region_id"], base["region_name"] = names[key(succ)]
            else:
                base["successor_region_id"] = names[key(succ)][0]
                base["note"] = "pre-May-2016 council; boundary differs from LGA 2021 (successor given)"
        if pd.notna(r.cap):
            flag = None
            if r.cap < 0:
                flag = "negative: identity inconsistent in OLG data"
            elif pd.notna(grants[(nm, fy)]) and r.cap > grants[(nm, fy)] * 1.01:
                flag = "exceeds grants & contributions % x revenue"
            b = dict(base, note=((base.get("note") or "") + "; derived = total revenue - total expenses - net "
                                 "operating result before capital (OLG $ lines)").lstrip("; "))
            out.append(row(**b, measure="capital_grants_contributions_aud_derived", amount_aud=r.cap,
                           check_flag=flag))
        for m in OLG_EXTRA:
            if pd.notna(r.get(m)):
                chk = r.am_check
                out.append(row(**base, measure=m, amount_aud=r[m],
                               check_flag="actual/required differs from published asset maintenance ratio by >2 pp"
                               if pd.notna(chk) and chk > 2 else None))
    d = pd.DataFrame(out)
    un = d[d.region_id.isna() & d.successor_region_id.isna()].source_council_name.unique()
    assert len(un) == 0, un
    print(f"[olg] {len(d)} rows; capital grants derived for FY {sorted(d[d.measure.str.startswith('capital')].fy.unique())}")
    return d


def main():
    names = lga_names()
    (FP / "urls.txt").write_text("".join(f"{fn}\t{v[1]}\t{v[2]}\n" for fn, v in SOURCES.items()))
    for fn, (name, url, orig, lic, note) in SOURCES.items():
        record_source("fp_funding: " + name, url, FP / fn, lic, (note + ("; original " + orig if orig else "")).strip())
    parts = [nbra(names), bcrrf(names),
             epa(names, "epa_green_waste.html", "NSW EPA Bushfire-generated green waste clean-up (Stream B)", None,
                 "award date not published; page updated 26 Oct 2021", "funded under DRFA", 31_500_057),
             epa(names, "epa_council_landfills.html", "NSW EPA Bushfire Recovery Program for Council Landfills "
                 "(Phase 2)", "2021-22", "published Oct-Nov 2021 (absent from 22 Oct 2021 archive; page updated "
                 "24 Nov 2021)", "26 landfill infrastructure projects in 15 councils", 22_074_935),
             bler(names)]
    bs, proj = bsbr(names)
    parts += [bs, audit_lg2020(names)]
    grants = pd.concat(parts, ignore_index=True)
    grants["source_url"] = grants.source_file.map(lambda f: SOURCES[f][1] if f in SOURCES else None)
    o = olg_rows(names)
    for fn in sorted(o.source_file.unique()):
        record_source("fp_funding: NSW OLG Time Series (asset maintenance $, capital-grants identity)",
                      olg.URLS[fn.split("/")[-1]], DATA / fn, "CC BY 4.0 (NSW OLG)", "re-read by src/fp_funding.py")
    d = pd.concat([grants, o], ignore_index=True)
    ENRICH.mkdir(parents=True, exist_ok=True)
    d.to_parquet(ENRICH / "fp_funding.parquet", index=False)
    d.to_csv(ENRICH / "fp_funding.csv", index=False)
    proj["source_url"] = SOURCES["bsbr_approved_projects_20220815.pdf"][1]
    proj.to_parquet(ENRICH / "fp_funding_projects.parquet", index=False)
    proj.to_csv(ENRICH / "fp_funding_projects.csv", index=False)
    doc = {
        "region_id": ["ABS LGA 2021 code (blank for pre-2016 councils and 'Multiple LGAs')", "str", "ABS ASGS 2021", ""],
        "successor_region_id": ["LGA 2021 code of the merged successor, for pre-May-2016 councils", "str", "", ""],
        "fy": ["Financial year the money was announced/published (grants) or the council FY (OLG, audit)", "str",
               "", "blank where the source gives no date; see fy_basis"],
        "program": ["Program or dataset", "str", "", ""],
        "measure": ["What amount_aud is", "str", "",
                    "grant_allocated_aud / grant_awarded_aud: to the council; project_funding_in_lga_aud: projects "
                    "located in the LGA, any recipient; council_reported_damage_cost_estimate_aud, "
                    "disaster_funding_received_aud, infrastructure_impairment_aud: Audit Office LG 2020; "
                    "capital_grants_contributions_aud_derived, asset_maintenance_*_aud: OLG"],
        "amount_aud": ["Amount", "AUD (nominal)", "see source_file / source_url", "blank = unknown, never 0"],
        "check_flag": ["Why a value is doubtful or blanked", "str", "", ""],
    }
    (ENRICH / "fp_funding.doc.json").write_text(json.dumps(doc, indent=1))
    s = d[d.amount_aud.notna()].groupby(["program", "measure"]).agg(
        rows=("amount_aud", "size"), councils=("region_id", "nunique"), fys=("fy", lambda x: ",".join(sorted(set(x.dropna())))),
        total_aud=("amount_aud", "sum"))
    pd.set_option("display.width", 250)
    print(s.to_string())


if __name__ == "__main__":
    main()
