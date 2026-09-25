"""DL_house_loss_raw: homes destroyed per fire, from official reports (data/house_loss/, compiled with quotes).

Only matches rated high or medium confidence are used. Where official sources disagree, the preferred source is:
NSW coronial inquiry > NSW RFS (Bush Fire Bulletin, annual report, media releases) > AIDR Knowledge Hub > secondary.
All values found for a fire are listed in `house_loss_all_sources`, so conflicts stay visible. The value is for the
whole fire, so it repeats on every council row of that fire. Blank = no official per-fire figure (not zero).
"""
import json

import pandas as pd

from src.common import DATA, record_source

HL = DATA / "house_loss"


def _rank(title, stype):
    t = str(title).lower()
    if stype != "official":
        return 9
    if "coron" in t:
        return 0
    if "rfs" in t or "rural fire" in t:
        return 1
    if "aidr" in t:
        return 2
    return 3


def run():
    h = pd.read_csv(HL / "house_loss.csv")
    m = pd.read_csv(HL / "house_loss_matches.csv")
    m = m[m.match_confidence.isin(["high", "medium"]) & m.suggested_event_id.notna()]
    x = h.merge(m[["fire_name", "source_url", "suggested_event_id", "match_confidence"]], on=["fire_name", "source_url"])
    x = x[x.homes_destroyed.notna()].copy()
    # one reported figure belongs to one fire: if the same quote was matched to several events (e.g. Border/Rockton,
    # which merged), keep only the best-confidence match
    x["_conf"] = x.match_confidence.map({"high": 0, "medium": 1})
    x = x.sort_values("_conf").drop_duplicates(["source_url", "quoted_text"]).drop(columns="_conf")
    x["rank"] = [_rank(t, s) for t, s in zip(x.source_title, x.source_type)]
    rows = []
    for eid, g in x.groupby("suggested_event_id"):
        g = g.sort_values("rank")
        best = g.iloc[0]
        rows.append(dict(
            event_id=eid, DL_house_loss_raw=float(best.homes_destroyed),
            homes_damaged=float(best.homes_damaged) if pd.notna(best.homes_damaged) else float("nan"),
            house_loss_source=f"{best.source_title} ({best.source_page_or_section})", house_loss_url=best.source_url,
            house_loss_match_confidence=best.match_confidence,
            house_loss_all_sources=" | ".join(f"{int(v)} ({t})" for v, t in zip(g.homes_destroyed, g.source_title))))
    out = pd.DataFrame(rows)
    out.to_parquet(DATA / "enrich/house_loss.parquet")
    doc = {
        "homes_damaged": ("Homes damaged (preferred source)", "count", "official reports", "blank if not stated"),
        "house_loss_source": ("Source of DL_house_loss_raw and page/section", "str", "", ""),
        "house_loss_url": ("URL of that source", "str", "", ""),
        "house_loss_match_confidence": ("How confidently the report's fire was matched to this fire", "str", "", ""),
        "house_loss_all_sources": ("Every homes-destroyed figure found for this fire, with source", "str", "",
                                   "shows disagreements between official sources"),
    }
    (DATA / "enrich/house_loss.doc.json").write_text(json.dumps(doc, indent=1))
    for u, t in h.drop_duplicates("source_url")[["source_url", "source_title"]].itertuples(index=False):
        record_source(f"House loss: {t}", u, None, "public report", "per-fire homes destroyed")
    return out


if __name__ == "__main__":
    out = run()
    print(len(out), out.DL_house_loss_raw.sum())
    print(out.sort_values("DL_house_loss_raw", ascending=False)[["event_id", "DL_house_loss_raw", "house_loss_all_sources"]]
          .head(12).to_string())
