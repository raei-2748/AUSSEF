"""Key-events dataset: declared NSW bushfire disasters since 2015 (the mentor's "key information" view).

Workbook out/nsw_key_bushfire_events.xlsx:
- events         one row per declaration: name, dates, councils, summary, headline facts (from news/official reports)
- event_council  one row per declaration × council: fire features summed/maxed over the declared event's fires in that
                 council (from out/fires.csv), council context (X15–X22) and Y components for that council-year,
                 and council-level facts where reported
- facts          every reported fact with its source, quote and date (data/key_events/facts_*.csv)
- dictionary     column meanings
Headline facts: for each (event, council, fact) the preferred value is the latest-dated official source, else the
latest-dated news source; every value is also kept in `facts`. Nothing is summed across sources or estimated.
"""
import glob
import re

import numpy as np
import pandas as pd

from src.common import DATA, OUT

KE = DATA / "key_events"
FACTS = ["homes_destroyed", "homes_damaged", "deaths", "injuries", "people_evacuated", "livestock_lost",
         "agricultural_loss_aud", "fencing_km_lost", "businesses_affected", "power_customers_without_supply",
         "roads_closed", "area_burned_ha", "insured_loss_aud", "recovery_funding_aud", "emergency_warning_level",
         "fire_danger_rating", "cause"]
TEMPLATE_X = ["X15_pop_density", "X16_regional_GDP_proxy_total_income_aud", "X17_SEIFA", "X18_remoteness",
              "X19_cash_reserve", "X20_own_source_revenue_ratio", "X21_debt_burden", "X22_historical_disaster_count"]
Y_COLS = ["IL_job_loss_raw", "IL_unemployment_rate_change_excess_pp", "IL_business_count_change_pct",
          "IL_business_count_change_excess_pct", "SL_income_drop_raw", "SL_income_drop_excess_pct",
          "SL_vulnerable_loss_raw", "SL_vulnerable_loss_excess", "FP_budget_crowd_out_raw",
          "FP_service_share_change_plus1_excess", "FP_debt_ratio_change_raw", "FP_operating_ratio_change_plus1_excess",
          "FP_cash_cover_change_plus1_excess", "DL_insurance_loss_raw",
          # added 2026-09-26 for the Y composition (docs/y_composition/README.md)
          "IL_total_income_change_excess_pct", "FP_cash_cover_change_event_excess", "FP_roads_share_change_plus1_excess",
          "FP_renewals_ratio_change_plus1_excess", "FP_grants_per_capita_change_plus1_excess",
          "SL_rent_change_pct", "SL_rent_change_excess_pct", "dwellings_census"]


def load_facts():
    parts = [pd.read_csv(f, dtype=str) for f in sorted(glob.glob(str(KE / "facts_*.csv")))]
    if not parts:
        return pd.DataFrame(columns=["agrn", "council", "fact", "value"])
    f = pd.concat(parts, ignore_index=True)
    f["council"] = f.council.fillna("ALL").str.strip()
    f = apply_corrections(f)
    f = validate(f)
    f = link_status(f)
    f["as_of"] = pd.to_datetime(f.as_of_date, errors="coerce")
    f["official"] = f.source_type.str.lower().eq("official")
    return f


HEDGE = re.compile(r"(more than|over|at least|approximately|approx\.?|about|around|nearly|almost|up to|some|roughly|estimated)\s*\$?$",
                   re.I)
NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
       "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
       "eighteen": 18, "nineteen": 19, "twenty": 20, "twenty-five": 25, "no": 0}


def validate(f):
    """value_check: verified / number in words / hedged -> blanked / not in quote -> blanked / no quote -> blanked.
    A number is blanked only when the hedge word sits right before that number ('14 homes and more than 40 sheds'
    keeps 14)."""
    checks, vals = [], []
    for v, q in zip(f.value, f.quoted_text.fillna("")):
        if pd.isna(v) or str(v).strip() == "":
            checks.append("no value"); vals.append(v); continue
        try:
            x = float(str(v).replace(",", ""))
        except ValueError:
            checks.append("text value"); vals.append(v); continue
        if not q.strip():
            checks.append("no quote: blanked"); vals.append(np.nan); continue
        qn = q.replace(",", "")
        hit = None
        for m in re.finditer(r"\d+(?:\.\d+)?", qn):
            num = float(m.group())
            for mult in (1, 1e3, 1e6, 1e9):
                if abs(num * mult - x) < 1e-6 * max(1, x):
                    hit = m; break
            if hit:
                break
        if hit is None:
            words = [w for w, n in NUM.items() if n == x and re.search(rf"\b{w}\b", q, re.I)]
            if words:
                pre = q[:re.search(rf"\b{words[0]}\b", q, re.I).start()]
                checks.append("hedged: blanked" if HEDGE.search(pre.strip()) else "verified (number in words)")
                vals.append(np.nan if HEDGE.search(pre.strip()) else v)
            elif x == 1 and re.search(r"\b(died|killed|fatality|death of|lost (his|her) life)\b", q, re.I):
                checks.append("verified (one named death)"); vals.append(v)
            else:
                checks.append("not in quote: blanked"); vals.append(np.nan)
            continue
        pre = qn[:hit.start()].strip()
        if HEDGE.search(pre):
            checks.append("hedged: blanked"); vals.append(np.nan)
        else:
            checks.append("verified"); vals.append(v)
    f["value_as_submitted"] = f.value
    f["value"] = vals
    f["value_check"] = checks
    return f


def _links():
    from src import linkcheck
    lc = linkcheck.load()
    return linkcheck.clean, dict(zip(lc.url, zip(lc.verdict, lc.archive_url)))


# local copies cited by the agents, mapped to the official file (same SHA-256, checked 2026-09-25)
LOCAL_COPIES = {"nsw_bushfire_inquiry_final_report_2020.pdf":
                "https://www.nsw.gov.au/sites/default/files/noindex/2023-06/Final-Report-of-the-NSW-Bushfire-Inquiry.pdf"}


def link_status(f):
    """link_status per fact; a dead link with a Wayback copy is replaced by the copy (original kept)."""
    clean, lc = _links()
    st, url = [], []
    for u in f.source_url.fillna(""):
        for local, official in LOCAL_COPIES.items():  # local files cited by agents -> the identical official file
            if local in u:
                u = official
        v, a = lc.get(clean(u), ("unchecked", ""))
        st.append(v)
        # dead link, or a site that refuses automated checks: use the Wayback copy when one exists
        url.append(a if v in ("dead_archived", "blocked") and a else u)
    f["source_url_original"] = f.source_url
    f["source_url"] = url
    f["link_status"] = st
    return f


def clean_key_sources(text):
    """Keep checked links (ok / blocked / archived copy); list the rest in links_removed."""
    clean, lc = _links()
    keep, drop = [], []
    for part in re.split(r"\s*[;|]\s*|\s+(?=https?://)", str(text or "")):
        if not part.strip():
            continue
        u = clean(part)
        v, a = lc.get(u, ("unchecked", ""))
        if v in ("ok", "blocked", "unchecked") and u.startswith("http") and "wikipedia.org" not in u:
            keep.append(u)
        elif v == "dead_archived" and a:
            keep.append(a)
        else:
            drop.append(f"{part.strip()} [{v}]")
    return "; ".join(dict.fromkeys(keep)), "; ".join(drop)


def apply_corrections(f):
    path = KE / "corrections.csv"
    if not path.exists():
        return f
    f["correction_note"] = ""
    for c in pd.read_csv(path, dtype=str).fillna("").itertuples():
        m = (f.agrn.astype(str) == c.agrn) & (f.fact == c.fact) & f.quoted_text.fillna("").str.contains(c.match_quote,
                                                                                                         regex=False)
        if c.action == "set_council":
            f.loc[m, "council"] = c.new_value
        elif c.action == "set_agrn":
            f.loc[m, "agrn"] = c.new_value
        elif c.action == "set_fact":
            f.loc[m, "fact"] = c.new_value
        elif c.action == "set_source":
            f.loc[m, "source_url"] = c.new_value
            if getattr(c, "new_quote", ""):
                f.loc[m, "quoted_text"] = c.new_quote
            f.loc[m, "source_type"] = "news"
        elif c.action == "blank":
            f.loc[m, "value"] = np.nan
        elif c.action == "drop":
            f = f[~m]
            continue
        f.loc[m, "correction_note"] = c.note
    return f


def headline(f):
    """(agrn, council, fact) -> preferred value and its source."""
    if f.empty:
        return pd.DataFrame(columns=["agrn", "council", "fact", "value", "source_url"])
    g = f[f.value.notna() & (f.value.astype(str).str.strip() != "")]
    g = g.sort_values(["official", "as_of"], ascending=[False, False])
    return g.drop_duplicates(["agrn", "council", "fact"])[["agrn", "council", "fact", "value", "source_url"]]


def build_seed():
    """One row per declared bushfire event since 2015 (all declaration sources), with the linked fires."""
    from src import socio
    d = socio.disasters()
    b = d[d.hazard.astype(str).str.contains("fire", case=False) & (d.start >= "2015-01-01")].copy()
    fires = pd.read_csv(OUT / "fires.csv", low_memory=False, dtype={"region_id": str})
    fires["agrns"] = fires.official_declaration_agrn.fillna("").astype(str).str.split(";")
    fx = fires.explode("agrns")
    fx = fx[fx.agrns != ""]
    rows = []
    for a, g in b.groupby("agrn"):
        lf = fx[fx.agrns == str(a)]
        top = lf.drop_duplicates("event_id").sort_values("X1_burn_area", ascending=False).head(6)
        rows.append(dict(
            agrn=a, declaration_name=g.event_name.iloc[0], hazard=g.hazard.iloc[0], decl_start=g.start.min().date(),
            decl_end=g.end.max().date() if g.end.notna().any() else "", source=g.decl_source.iloc[0],
            declaration_source_url=g.decl_source_url.dropna().iloc[0] if g.decl_source_url.notna().any() else "",
            councils="; ".join(sorted(set(lf.region_name)) or sorted(set(g.council_name.astype(str)))),
            n_councils=g.key.nunique(), linked_fires=lf.event_id.nunique(),
            linked_burn_area_ha=round(lf.drop_duplicates("event_id").X1_burn_area.sum()),
            main_fires="; ".join(f"{n} ({str(s)[:10]}, {x:,.0f} ha)" for n, s, x in
                                 zip(top.event_name, top.date_start, top.X1_burn_area))))
    seed = pd.DataFrame(rows).sort_values("decl_start")
    seed.to_csv(KE / "seed_events.csv", index=False)
    return seed


def _summaries(seed):
    files = glob.glob(str(KE / "summaries_*.csv"))
    if not files:
        return pd.DataFrame(columns=["agrn"])
    s = pd.concat([pd.read_csv(p, dtype=str) for p in files], ignore_index=True)
    # rows written without an AGRN (declarations recovered by the agents) are matched to the seed by name
    name2id = dict(zip(seed.declaration_name.str.lower().str.strip(), seed.agrn.astype(str)))
    miss = s.agrn.isna() | (s.agrn.astype(str).str.strip() == "")
    s.loc[miss, "agrn"] = s.loc[miss, "declaration_name"].str.lower().str.strip().map(name2id)
    s = s[s.agrn.notna()]
    s["_len"] = s.summary.fillna("").str.len()  # two groups may summarise the same event: keep the fuller one
    s = s.sort_values("_len", ascending=False).drop_duplicates("agrn").drop(columns="_len")
    ks = s.key_sources.map(clean_key_sources)
    s["key_sources"], s["links_removed"] = ks.str[0], ks.str[1]
    return s


DL_METRICS = {"homes_destroyed": "DL", "homes_damaged": "DL", "facilities_destroyed": "DL", "facilities_damaged": "DL",
              "outbuildings_destroyed": "DL", "outbuildings_damaged": "DL", "properties_destroyed": "DL",
              "properties_damaged": "DL", "fencing_km": "DL", "livestock_lost": "DL", "deaths": "SL",
              "injuries": "SL"}


def dl_council_wide():
    """Preferred value per (agrn, council, metric) from data/enrich/dl_council.parquet (src/dl_council.py), with its
    scope and a one-cell source: title | URL | page | quote."""
    p = DATA / "enrich/dl_council.parquet"
    cols = ["agrn", "region_id"]
    if not p.exists():
        return pd.DataFrame(columns=cols)
    d = pd.read_parquet(p)
    d = d[d.preferred].copy()
    assert not d.duplicated(["agrn", "region_id", "metric"]).any(), "dl_council: more than one preferred value"
    d["src"] = (d.source_title.fillna("") + " | " + d.url.fillna("") + " | " + d.page_or_section.fillna("").astype(str)
                + " | \"" + d.quote.fillna("") + "\"")
    out = None
    for metric, pillar in DL_METRICS.items():
        s = d[d.metric == metric].set_index(cols)
        if s.empty:
            continue
        name = f"{pillar}_{metric}_sourced"
        w = pd.DataFrame({name: s.value, f"{name}_scope": s.scope, f"{name}_source_type": s.source_type,
                          f"{name}_source": s.src})
        out = w if out is None else out.join(w, how="outer")
    out = out.reset_index()
    out["agrn"], out["region_id"] = out.agrn.astype(str), out.region_id.astype(str)
    return out


def build():
    seed = build_seed()
    fires = pd.read_csv(OUT / "fires.csv", low_memory=False, dtype={"region_id": str})
    fires["agrn"] = fires.official_declaration_agrn.fillna("").astype(str).str.split(";")
    fx = fires.explode("agrn")
    fx = fx[fx.agrn != ""]
    facts = load_facts()
    head = headline(facts)
    summ = _summaries(seed)

    # ---- event × council
    rows = []
    for a, g in fx.groupby(["agrn", "region_id"]):
        agrn, code = a
        g = g.copy()
        w = g.region_burn_area_ha.fillna(0)
        big = g.loc[w.idxmax()]
        one = g.drop_duplicates("event_id")
        r = dict(agrn=agrn, region_id=code, region_name=big.region_name, fires_n=g.event_id.nunique(),
                 fire_names="; ".join(one.sort_values("region_burn_area_ha", ascending=False).event_name.head(8)),
                 first_fire_start=g.date_start.dropna().astype(str).min(), last_fire_end=g.date_end.dropna().astype(str).max() if g.date_end.notna().any() else np.nan,
                 burn_area_in_council_ha=w.sum(), share_of_council_burned=g.share_of_region_burned.sum(),
                 largest_fire_total_area_ha=g.X1_burn_area.max(), max_fire_duration_days=g.X4_fire_duration.max(),
                 max_ffdi=g.X2_FFDI.max(), min_spei3=g.X3_SPEI.min(), max_temp_c=g.X7_temp_max.max(),
                 min_rh_pct=g.X8_humidity_min.min(), max_wind_kmh=g.X9_wind_max.max(),
                 # hotspot_count is per whole fire: take each fire's share inside this council (2026-09-27 fix)
                 hotspots_n=(g.hotspot_count * g.region_share_of_fire).sum(min_count=1) if "hotspot_count" in g
                 else np.nan,
                 severity_high_extreme_share=(np.average(g.X6_severity.dropna(),
                                                         weights=w[g.X6_severity.notna()].clip(lower=1e-9))
                                              if g.X6_severity.notna().any() else np.nan),
                 mean_slope_deg=np.average(g.X11_slope.fillna(0), weights=w.clip(lower=1e-9)),
                 dominant_vegetation=big.X12_vegetation, mean_canopy_pct=big.X13_canopy_cover,
                 road_km_burned=g.X14_road_exposure.sum(),
                 homes_destroyed_by_these_fires=one.DL_house_loss_raw.sum(min_count=1) if "DL_house_loss_raw" in one else np.nan,
                 # whole-fire figure × share of that fire inside this council (an assumption, like the ICA area share)
                 homes_destroyed_area_share=((one.DL_house_loss_raw * one.region_share_of_fire).sum(min_count=1)
                                             if "DL_house_loss_raw" in one else np.nan))
        for c in TEMPLATE_X + Y_COLS:  # council-year context: from the largest fire's row (same council & FY)
            r[c] = big.get(c, np.nan)
        rows.append(r)
    ec = pd.DataFrame(rows)
    # the same fires can sit under two overlapping declarations (e.g. AGRN 880 North Coast from July 2019 and AGRN 871
    # statewide from August 2019): list the other declarations so sums across events are not double counted
    multi = fx.groupby(["event_id", "region_id"]).agrn.apply(lambda s: set(s))
    other = {}
    for (eid, code), ags in multi.items():
        for a in ags:
            other.setdefault((a, code), set()).update(ags - {a})
    ec["also_under_declarations"] = ["; ".join(sorted(other.get((a, c), set()))) for a, c in zip(ec.agrn, ec.region_id)]
    if not head.empty:
        hc = head[head.council != "ALL"].copy()
        hc["key"] = hc.council.str.lower().str.replace(r"[^a-z]", "", regex=True)
        ec["key"] = ec.region_name.str.lower().str.replace(r"\(nsw\)", "", regex=True).str.replace(r"[^a-z]", "", regex=True)
        piv = hc.pivot_table(index=["agrn", "key"], columns="fact", values="value", aggfunc="first")
        piv.columns = [f"reported_{c}" for c in piv.columns]
        ec = ec.merge(piv.reset_index(), on=["agrn", "key"], how="left").drop(columns="key")

    # DL for Y: homes destroyed in this council per 1,000 private dwellings. A council-specific reported figure is used
    # when one exists; otherwise the area-share split of whole-fire figures
    # Sourced figures only (2026-09-27): first the per-council table of src/dl_council.py (one preferred, quote-checked
    # value per row and metric), then council facts from facts_*.csv. The area-share split of whole-fire figures stays
    # in homes_destroyed_area_share as a labelled proxy: it double counts when a source already assigns a fire's
    # losses to one council (e.g. Sir Ivan 2017: RFS puts all 35 homes in Warrumbungle)
    rep = ec["reported_homes_destroyed"] if "reported_homes_destroyed" in ec else pd.Series(np.nan, index=ec.index)
    rep = pd.to_numeric(rep, errors="coerce")
    ec = ec.merge(dl_council_wide(), on=["agrn", "region_id"], how="left")
    dl = ec["DL_homes_destroyed_sourced"]
    ec["DL_homes_destroyed_in_council"] = dl.fillna(rep)
    ec["DL_homes_destroyed_basis"] = np.select(
        [dl.notna() & (ec.DL_homes_destroyed_sourced_scope == "fire_in_council"), dl.notna(), rep.notna()],
        ["one fire in the council (lower bound), see DL_homes_destroyed_sourced_source",
         "council figure, see DL_homes_destroyed_sourced_source", "council report (key_facts)"], "")
    ec["DL_homes_destroyed_per_1000_dwellings"] = ec.DL_homes_destroyed_in_council / ec.dwellings_census * 1000

    # ---- events
    ev = seed.copy()
    agg = ec.groupby("agrn").agg(councils_with_fires=("region_id", "nunique"), fires_n=("fires_n", "sum"),
                                 burn_area_ha=("burn_area_in_council_ha", "sum"), max_ffdi=("max_ffdi", "max"))
    ev = ev.merge(agg, left_on="agrn", right_index=True, how="left")
    if not head.empty:
        # event headline: the whole-event figure; if none, the figure when only one council reports that fact
        one = head[head.council != "ALL"].groupby(["agrn", "fact"]).filter(lambda g: len(g) == 1)
        allrows = head[head.council == "ALL"]
        one = one[~one.set_index(["agrn", "fact"]).index.isin(allrows.set_index(["agrn", "fact"]).index)]
        ha = pd.concat([allrows, one]).pivot_table(index="agrn", columns="fact", values="value", aggfunc="first")
        ha.columns = [f"reported_{c}" for c in ha.columns]
        ev = ev.merge(ha, left_on="agrn", right_index=True, how="left")
    ok = facts[facts.value_check.astype(str).str.startswith(("verified", "text"))] if "value_check" in facts else facts
    if not ok.empty:
        def line(r):
            where = "" if r.council == "ALL" else f"{r.council}: "
            what = f"{r.value} {str(r.fact).replace('_', ' ')}" if str(r.fact) != "other" else f"{r.value} ({r.notes})"
            return f"{where}{what} [{r.publisher or r.source_title}, {str(r.as_of_date)[:10]}]"
        ok = ok.fillna({"publisher": "", "notes": ""})
        kf = ok.groupby("agrn").apply(lambda g: "; ".join(line(r) for r in g.itertuples()))
        ev["key_facts"] = ev.agrn.astype(str).map(kf)
    keep = [c for c in ["agrn", "real_agrn_if_found", "official_name_if_found", "towns_affected", "summary", "key_sources",
                        "links_removed"]
            if c in summ.columns]
    if keep:
        ev = ev.merge(summ[keep].drop_duplicates("agrn"), on="agrn", how="left")

    dic = pd.DataFrame([
        ("agrn", "Declaration ID (AGRN); 'RAA-' = from NSW Rural Assistance Authority annual reports without AGRN"),
        ("burn_area_in_council_ha", "Area burned inside this council by the declared event's fires (GA outlines)"),
        ("share_of_council_burned", "Share of the council area burned by these fires"),
        ("max_ffdi", "Highest daily FFDI during any of these fires (reanalysis; ranks fires, not official FFDI)"),
        ("severity_high_extreme_share", "Area-weighted share of burnt area in high/extreme severity (NSW FESM)"),
        ("homes_destroyed_by_these_fires", "Sum of official homes-destroyed figures of the fires touching this council "
                                           "(whole-fire figures; a fire spanning councils counts fully in each)"),
        ("also_under_declarations", "Other declarations covering some of the same fires in this council (avoid double counting)"),
        ("homes_destroyed_area_share", "Whole-fire homes-destroyed figures × each fire's share inside this council "
                                       "(assumes losses spread like burned area)"),
        ("DL_homes_destroyed_in_council", "Homes destroyed in this council: council-specific reported figure if any, "
                                          "else homes_destroyed_area_share (see DL_homes_destroyed_basis)"),
        ("DL_homes_destroyed_basis", "Which figure DL_homes_destroyed_in_council uses"),
        ("DL_homes_destroyed_per_1000_dwellings", "DL_homes_destroyed_in_council per 1,000 private dwellings "
                                                  "(ABS Census, dwellings_census)"),
        ("reported_*", "Headline fact from news/official reports: the whole-event figure (latest official source preferred), "
                       "or the one council's figure when only one council reports it; every value is in `facts`"),
        ("key_facts", "Every verified fact for the event in words: council, value, source, date"),
        ("X15…X22, IL_*, SL_*, FP_*, DL_*", "Council context and Y components for this council and financial year "
                                            "(see the main dataset's dictionary); _excess = vs councils without a large fire"),
    ], columns=["column", "meaning"])
    src_of = {"agrn": "declaration (declaration_source_url)", "reported_*": "facts sheet: source_url per fact",
              "homes_destroyed_area_share": "house-loss sources (main dataset house_loss_source) × GA outlines",
              "DL_homes_destroyed_in_council": "facts sheet, or house-loss sources × GA outlines",
              "DL_homes_destroyed_basis": "computed",
              "DL_homes_destroyed_per_1000_dwellings": "as above ÷ ABS Census private dwellings (2016 G32 / 2021 G36)",
              "key_facts": "facts sheet: source_url per fact",
              "X15…X22, IL_*, SL_*, FP_*, DL_*": "main dataset nsw_fire_events_2015_2025.xlsx (dictionary + download_links)"}
    dic["source"] = dic.column.map(src_of).fillna("GA fire outlines and enrichments in the main dataset (see sources sheet)")
    dic = pd.concat([dic, pd.DataFrame([
        ("declaration_source_url", "Official document listing the declaration (page number where it is a PDF)",
         "declaration source"),
        ("summary / key_sources", "Summary written from the listed sources; events with no coverage say so", "summary sources"),
        ("links_removed", "Links the research agents gave that failed the link check (dead, guessed, bare homepage, "
                          "Wikipedia); not used", "out/link_check.csv"),
        ("facts.link_status", "ok / blocked (site refuses automated checks) / dead_archived (Wayback copy used) / dead",
         "out/link_check.csv"),
    ], columns=["column", "meaning", "source"])], ignore_index=True)
    # every document behind the workbook: declarations, facts, summaries, and the data behind event_council
    src = [dict(kind="declaration", title=n, url=u, used_for="declaration name, dates, councils")
           for n, u in zip(ev.declaration_name, ev.declaration_source_url) if isinstance(u, str) and u]
    if not facts.empty:
        for r in facts.drop_duplicates("source_url").itertuples():
            src.append(dict(kind=f"fact ({r.source_type})", title=f"{r.source_title} — {r.publisher}", url=r.source_url,
                            used_for="facts sheet / reported_* columns"))
    if "key_sources" in ev:
        for u in ev.key_sources.dropna().str.split(r"\s*[;|\s]\s*(?=https?://)", regex=True).explode().str.strip():
            if u.startswith("http"):
                src.append(dict(kind="summary", title="", url=u, used_for="events.summary"))
    from src.links import rows as data_links
    for r in data_links().itertuples():
        src.append(dict(kind=f"data ({r.type})", title=r.dataset, url=r.download_url,
                        used_for=f"event_council: {r.used_for}"))
    sources = pd.DataFrame(src).drop_duplicates(["url", "used_for"])
    path = OUT / "nsw_key_bushfire_events.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        ev.to_excel(w, sheet_name="events", index=False)
        ec.to_excel(w, sheet_name="event_council", index=False)
        facts.drop(columns=[c for c in ["as_of", "official"] if c in facts]).to_excel(w, sheet_name="facts", index=False)
        dic.to_excel(w, sheet_name="dictionary", index=False)
        sources.to_excel(w, sheet_name="sources", index=False)
        ws = w.sheets["sources"]
        for i, u in enumerate(sources.url, start=2):
            if isinstance(u, str) and u.startswith("http") and "{" not in u:
                ws.cell(row=i, column=3).hyperlink = u.split(" (PDF")[0]
                ws.cell(row=i, column=3).style = "Hyperlink"
    ev.to_csv(OUT / "key_events.csv", index=False)
    ec.to_csv(OUT / "key_event_council.csv", index=False)
    return ev, ec, facts


if __name__ == "__main__":
    ev, ec, facts = build()
    print(len(ev), "events;", len(ec), "event×council rows;", len(facts), "facts")
