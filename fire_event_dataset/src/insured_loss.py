"""Insured losses below state level (mentor item (b)): every PUBLISHED figure, with its verbatim quote.

Findings (checked 2026-09-27):
- No public table gives insured losses of NSW bushfires by LGA, postcode, region or fire, from the Insurance Council of
  Australia (ICA), the NSW Government, the NSW Bushfire Inquiry (2020, no insured-loss figures), the Royal Commission
  into National Natural Disaster Arrangements (national figure only), the Senate inquiry (national only), ASIC
  (Black Summer claims review: outcome shares only; "The detailed findings have been shared with the insurers"),
  APRA (NCPD covers liability lines only) or Treasury.
- ICA Data Hub: catastrophe-level list only (already used by src/ica.py). ICA terms: data "cannot be commercially
  exploited and if an extract is copied for non-commercial use you must attribute it to the ICA".
- ICA Data Globe: a hazard-mapping platform for insurers (flood/bushfire/cyclone hazard at address level), access by
  ICA approval, no claims or loss data; the domain now redirects to the Data Hub.
- ICA Catastrophe 195 (2019-20) "eventually encompassed 183 postcodes across four states" (ICA Catastrophe Resilience
  Report 2020-21, p.18); the postcode list and per-postcode losses are not published.
- PERILS AG holds postcode-level industry losses for 2019-20 but sells them under licence ("The use of PERILS exposure
  and loss data other than in conjunction with a valid PERILS License ... is illegal and expressly forbidden"): NOT used,
  not even its headline shares.
- What IS public: a few ICA figures for a region or a single fire (2018-2019), mostly quoted in news, and the NSW
  share of the 2019-20 season total in an ICA media release. They are recorded below, one row per published figure,
  with the verbatim quote. The quote is checked against the saved copy of the page (quote_verified). Nothing is split
  or allocated: multi-state and multi-region figures keep their published geography (`geography_note`).

Writes: data/enrich/insured_loss.parquet / .csv (one row per figure; keyed by agrn and, where the figure is for one
council, region_id), data/enrich/insured_loss.doc.json. Sources saved under data/raw/econ/insurance/.
Run:  uv run --no-sync --with pypdf python -m src.insured_loss
"""
import html
import json
import re
import urllib.request

import pandas as pd

from src.common import DATA, record_source

RAW = DATA / "raw/econ/insurance"
ENRICH = DATA / "enrich"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
ICA_TERMS = "ICA: non-commercial use with attribution to the ICA (ICA Data Hub disclaimer)"

# file -> (url, title, publisher, source_type, licence/terms note)
SOURCES = {  # ACM papers (e.g. Bega District News) removed 2026-09-27: ACM prohibits AI use of its content
    "insurancebusiness_2018-04-19_tathra_ica.html": (
        "https://www.insurancebusinessmag.com/au/news/breaking-news/tathra-bushfire-cleanup-is-making-strong-progress--ica-98231.aspx",
        "Tathra bushfire cleanup is making strong progress - ICA", "Insurance Business Australia", "trade news quoting ICA",
        "© publisher; short quote for citation"),
    "reinsurancenews_2018-04-23_tathra_vic_45m.html": (
        "https://www.reinsurancene.ws/australias-tathra-and-victoria-bushfire-losses-reach-45mn-as-clean-up-begins/",
        "Australia's Tathra and Victoria bushfire losses reach $45mn as clean-up begins", "Reinsurance News",
        "trade news quoting ICA", "© publisher; short quote for citation"),
    "insurancejournal_2019-11-12_548129.html": (
        "https://www.insurancejournal.com/news/international/2019/11/12/548129.htm",
        "Insurance Journal, 12 Nov 2019 (Australia bushfire claims)", "Insurance Journal", "trade news quoting ICA",
        "© publisher; short quote for citation"),
    "abc_2019-11-13_bushfire_insurance.html": (
        "https://www.abc.net.au/news/2019-11-13/what-you-need-to-know-about-bushfire-insurance/11699382",
        "What you need to know about bushfire insurance", "ABC News", "news quoting ICA (Campbell Fuller)",
        "© ABC; short quote for citation"),
    "sbs_2019-11-12_ica_tweet.html": (
        "https://www.sbs.com.au/language/italian/en/article/bushfire-reach-sydneys-north-shore-as-crews-battle-78-fires-across-nsw/zuch48lfw",
        "Bushfire reach Sydney's north shore as crews battle 78 fires across NSW", "SBS", "news quoting ICA post",
        "© SBS; short quote for citation"),
    "insurancenews_2019-11-15_100m.html": (
        "https://www.insurancenews.com.au/daily/bushfires-insurers-face-100-million-losses-so-far",
        "Bushfires: insurers face $100 million losses so far", "insuranceNEWS.com.au", "trade news quoting ICA",
        "© publisher; short quote for citation"),
    "abc_2019-11-22_qld_nsw_145m.html": (
        "https://www.abc.net.au/news/2019-11-22/queensland-bushfire-crisis-nsw-fires-cost-insurance-damage-bill/11725920",
        "Queensland and NSW bushfires insurance damage bill", "ABC News", "news quoting ICA",
        "© ABC; short quote for citation"),
    "ica_2020-05-28_media_release_5.19b.pdf": (
        "https://insurancecouncil.com.au/wp-content/uploads/resources/Media%20releases/2020/2020_05/"
        "2020_05_Insurance%20bill%20for%20season%20of%20natural%20disasters%20climbs%20over%20$5.19b.pdf",
        "Insurance bill for season of natural disasters climbs over $5.19b (media release)",
        "Insurance Council of Australia", "primary (ICA)", ICA_TERMS),
    "aidr_black_summer_nsw.html": (
        "https://knowledge.aidr.org.au/resources/black-summer-bushfires-nsw-2019-20/",
        "Black Summer bushfires, NSW, 2019-20", "Australian Institute for Disaster Resilience Knowledge Hub",
        "secondary (government-funded knowledge hub citing ICA)", "© AIDR; short quote for citation"),
    "abc_2020-08-23_top_five.html": (
        "https://www.abc.net.au/news/2020-08-23/bushfire-season-in-top-five-for-insurance-payouts/12578860",
        "Bushfire season in top five for insurance payouts", "ABC News", "news quoting ICA",
        "© ABC; short quote for citation"),
    "ica_catastrophe_resilience_report_2020-21.pdf": (
        "https://insurancecouncil.com.au/wp-content/uploads/2021/09/ICA008_CatastropheReport_6.5_FA1_online.pdf",
        "Insurance Catastrophe Resilience Report 2020-21", "Insurance Council of Australia", "primary (ICA)", ICA_TERMS),
}

# One row per published figure. `quote` must appear in the saved source (checked); "…" separates checked fragments.
FACTS = [
    dict(fid="tathra_vic_2018_ib", file="insurancebusiness_2018-04-19_tathra_ica.html", statement_date="2018-04-19",
         agrn="NSW1718-20", region_id="", geography="Tathra (NSW) and south-west Victoria fires, 17-18 March 2018 combined",
         geography_type="multi-state event", multi_state=True, insured_loss_aud=45e6, claims=1050,
         loss_basis="claims lodged to date",
         quote="claims lodged due to both the Tathra and Victorian bushfires number 1,050, amounting to $45m",
         note="NSW and Victoria combined; no NSW-only split published"),
    dict(fid="nnsw_seq_sep2019_ij", file="insurancejournal_2019-11-12_548129.html", statement_date="2019-11-12",
         agrn="", region_id="", geography="northern NSW and south-east Queensland fires, September 2019",
         geography_type="multi-state region", multi_state=True, insured_loss_aud=20e6, claims=300,
         loss_basis="insured losses",
         quote="insurers received 300 claims from fires in northern NSW and south-east Queensland, with A$20 million",
         note="NSW and QLD combined; NSW declarations covering September 2019: AGRN 871 and 880 (not assigned)"),
    dict(fid="rappville_oct2019_ij", file="insurancejournal_2019-11-12_548129.html", statement_date="2019-11-12",
         agrn="871", region_id="16610", geography="Rappville bushfire, October 2019 (Richmond Valley)",
         geography_type="fire", multi_state=False, insured_loss_aud=25e6, claims=200, loss_basis="insured losses (estimate)",
         quote="the Rappville bushfire resulted in 200 claims",
         note="Rappville lies in Richmond Valley LGA; council is also under AGRN 880 (from Jul 2019)"),
    dict(fid="rappville_oct2019_abc", file="abc_2019-11-13_bushfire_insurance.html", statement_date="2019-11-13",
         agrn="871", region_id="16610", geography="Rappville bushfire, October 2019 (Richmond Valley)",
         geography_type="fire", multi_state=False, insured_loss_aud=25e6, claims=200, loss_basis="insured losses (estimate)",
         quote="Rappville … 200 claims … $25 million", note="ABC attributes to ICA; same figure as the Insurance Journal row"),
    dict(fid="mnc_nov2019_ica_post", file="sbs_2019-11-12_ica_tweet.html", statement_date="2019-11-12",
         agrn="871", region_id="", geography="catastrophe areas of the NSW mid-north coast (ICA CAT195, early)",
         geography_type="region", multi_state=False, insured_loss_aud=40e6, claims=360, loss_basis="initial estimate",
         quote="insurers have received 360 claims from the catastrophe areas of NSW mid-north coast including 80 suspected "
               "total losses. Initial losses estimated at $40m",
         note="80 suspected total losses; councils not listed by ICA"),
    dict(fid="nsw_qld_nov2019_in", file="insurancenews_2019-11-15_100m.html", statement_date="2019-11-15",
         agrn="871", region_id="", geography="bushfire catastrophe in NSW and Queensland, November 2019",
         geography_type="multi-state event", multi_state=True, insured_loss_aud=100e6, claims=900,
         loss_basis="insured losses to date",
         quote="bushfire catastrophe in NSW and Queensland have climbed to $100 million from 900 claims",
         note="NSW and QLD combined"),
    dict(fid="qld_nnsw_nov2019_abc", file="abc_2019-11-22_qld_nsw_145m.html", statement_date="2019-11-22",
         agrn="871", region_id="", geography="Queensland and northern NSW, November 2019 fires", geography_type="multi-state event",
         multi_state=True, insured_loss_aud=145e6, claims=1340, loss_basis="damage bill to date",
         quote="1,340 … $145 million", note="QLD and NSW combined"),
    dict(fid="cat195_nsw_share_ica", file="ica_2020-05-28_media_release_5.19b.pdf", statement_date="2020-05-28",
         agrn="871", region_id="", geography="NSW share of ICA CAT195 (2019-20 bushfires, four states $2.32 billion)",
         geography_type="state share", multi_state=False, insured_loss_aud=None, claims=None,
         loss_basis="share of estimated insurance losses", nsw_share_pct=81,
         quote="NSW (81 per cent)",
         note="ICA gives $2.32 billion across four states and NSW's 81 per cent; the dollar product is not in this release"),
    dict(fid="cat195_nsw_aud_aidr", file="aidr_black_summer_nsw.html", statement_date="",
         agrn="871", region_id="", geography="NSW part of ICA CAT195 (2019-20)", geography_type="state share",
         multi_state=False, insured_loss_aud=1.88e9, claims=None, loss_basis="NSW share of insured losses",
         quote="NSW accounted for 81 per cent of these losses, or $1.88 billion", note="AIDR states the dollar value"),
    dict(fid="cat195_nsw_claims_abc", file="abc_2020-08-23_top_five.html", statement_date="2020-08-23",
         agrn="871", region_id="", geography="NSW share of 2019-20 bushfire claims", geography_type="state share",
         multi_state=False, insured_loss_aud=None, claims=None, loss_basis="share of claims (about 30,000 claims)",
         quote="30,000 claims, with NSW accounting for three-quarters", note="claims count share only, no dollars"),
    dict(fid="cat195_postcodes_ica", file="ica_catastrophe_resilience_report_2020-21.pdf", statement_date="2021-09",
         agrn="871", region_id="", geography="ICA CAT195 declared area", geography_type="postcode count",
         multi_state=True, insured_loss_aud=None, claims=None, loss_basis="not a loss: number of postcodes declared",
         quote="encompassed 183 postcodes across four states",
         note="postcode list and per-postcode losses not published"),
]


def fetch(fn, url):
    p = RAW / fn
    if p.exists():
        return p, False
    RAW.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90) as r:
        p.write_bytes(r.read())
    return p, True


def norm(s):
    s = html.unescape(s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace(" ", " ").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).lower()


def text_of(p):
    if p.suffix == ".pdf":
        from pypdf import PdfReader
        return {i + 1: norm(pg.extract_text() or "") for i, pg in enumerate(PdfReader(p).pages)}
    raw = p.read_text(errors="ignore")
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    t = norm(re.sub(r"<[^>]+>", " ", raw))
    # many news pages also carry the text in JSON (escaped); include the raw text as a fallback
    return {None: t + " " + norm(raw.replace("\\u002F", "/").replace('\\"', '"'))}


def check(quote, pages):
    parts = [norm(x).strip(" .") for x in quote.split("…") if x.strip()]
    for pg, t in pages.items():
        if all(x in t for x in parts):
            return True, pg
    return False, None


def run():
    new = {}
    for fn, (url, *_rest) in SOURCES.items():
        p, fresh = fetch(fn, url)
        new[fn] = fresh
    for fn, (url, title, pub, stype, lic) in SOURCES.items():
        if new[fn]:
            record_source(f"{pub}: {title}", url, RAW / fn, lic, "insured-loss figure source (src/insured_loss.py)")
    texts = {fn: text_of(RAW / fn) for fn in SOURCES}
    rows = []
    for f in FACTS:
        url, title, pub, stype, lic = SOURCES[f["file"]]
        ok, pg = check(f["quote"], texts[f["file"]])
        r = dict(f)
        r.update(source_title=title, publisher=pub, source_type=stype, source_url=url, local_file=str(RAW / f["file"]),
                 pdf_page=pg, quote_verified=ok)
        if not ok:  # never keep an unverified number
            r["insured_loss_aud"] = r["claims"] = r["nsw_share_pct"] = None
        rows.append(r)
    out = pd.DataFrame(rows)
    out["nsw_share_pct"] = pd.to_numeric(out.get("nsw_share_pct"), errors="coerce")
    for c in ["insured_loss_aud", "claims"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    cols = ["fid", "agrn", "region_id", "geography", "geography_type", "multi_state", "statement_date",
            "insured_loss_aud", "claims", "nsw_share_pct", "loss_basis", "quote", "quote_verified", "source_title",
            "publisher", "source_type", "source_url", "pdf_page", "local_file", "note"]
    out = out[cols]
    ENRICH.mkdir(parents=True, exist_ok=True)
    out.to_parquet(ENRICH / "insured_loss.parquet", index=False)
    out.to_csv(ENRICH / "insured_loss.csv", index=False)
    doc = {
        "fid": ["Figure id", "str", "", ""],
        "agrn": ["Declared event the figure belongs to, when unambiguous by date and place", "id",
                 "out/key_events.csv", "blank = not assignable (e.g. spans two declarations)"],
        "region_id": ["ABS LGA 2021 code, only when the figure is for one fire inside one council", "code", "", ""],
        "geography": ["Geography exactly as published", "str", "source", "no allocation or split is applied"],
        "geography_type": ["fire / region / multi-state event / state share / postcode count", "str", "", ""],
        "multi_state": ["True if the published figure includes another state", "bool", "", ""],
        "statement_date": ["Date of the statement (figures are 'to date' and later revised)", "date", "source", ""],
        "insured_loss_aud": ["Insured loss as published", "AUD", "source", "blank if not published or quote unverified"],
        "claims": ["Claims count as published", "count", "source", ""],
        "nsw_share_pct": ["NSW share of a multi-state catastrophe loss, as published", "%", "ICA", ""],
        "loss_basis": ["What the number is (to-date bill, estimate, share)", "str", "source", ""],
        "quote": ["Verbatim text containing the figure ('…' joins separately checked fragments)", "str", "source", ""],
        "quote_verified": ["Quote found in the saved copy of the source", "bool", "computed", "numbers blanked if False"],
        "source_type": ["primary (ICA) / news quoting ICA / secondary", "str", "", ""],
        "pdf_page": ["Page of the PDF holding the quote", "int", "", ""],
        "_not_public": ["No LGA/postcode/fire table of insured losses exists publicly (ICA, NSW Government, NSW Bushfire "
                        "Inquiry, Royal Commission, Senate, ASIC, APRA, Treasury). ICA CAT195 per-postcode data and ASIC "
                        "detailed findings are unpublished; PERILS postcode losses are licensed only (not used).",
                        "", "", ""],
    }
    (ENRICH / "insured_loss.doc.json").write_text(json.dumps(doc, indent=1))
    return out


if __name__ == "__main__":
    o = run()
    print(o[["fid", "agrn", "region_id", "insured_loss_aud", "claims", "nsw_share_pct", "quote_verified", "pdf_page"]].to_string())
