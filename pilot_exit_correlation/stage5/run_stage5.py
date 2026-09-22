"""Stage 5 (descriptive): are the inferred 2019-20 cut-offs backed by official road-closure records?

    .venv/bin/python pilot_exit_correlation/stage5/run_stage5.py
"""
import datetime as dt
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import shapely
from shapely import wkt

HERE = Path(__file__).resolve().parent
STAGE1 = HERE.parent
sys.path.insert(0, str(STAGE1))
from src import inputs  # noqa: E402

POINT_M, LINE_M, PAD_AFTER_D = 1000, 100, 7
ARCHIVE_END = pd.Timestamp("2020-01-31")
OUT = HERE / "out"


def active_days(r):
    start = pd.Timestamp(r.start_time_upper).tz_convert("Australia/Sydney").normalize().tz_localize(None)
    end = r.end_time_upper if pd.notna(r.end_time_upper) else r.end_time_lower
    if pd.notna(end):
        end = pd.Timestamp(end).tz_convert("Australia/Sydney").normalize().tz_localize(None)
    elif r.duration_information_type == "right_censored_at_archive_end":
        end = ARCHIVE_END
    else:
        end = start
    return pd.date_range(start, max(start, end), freq="D")


def main():
    inputs.verify_inputs()
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)
    con = duckdb.connect(str(inputs.TRANSPORT_DB), read_only=True)
    cand = con.sql("select * from analysis.road_closure_candidates").df()
    members = con.sql("select disaster_family_id, min(family_start_date) s, max(family_end_date) e "
                      "from main.disaster_family_members group by 1").df().set_index("disaster_family_id")
    con.close()
    geo = shapely.from_wkt(cand.geometry_wkt.values)
    import pyproj
    tr = pyproj.Transformer.from_crs(4326, 3577, always_xy=True)
    cand["geom"] = [shapely.transform(g, lambda xy: np.c_[tr.transform(xy[:, 0], xy[:, 1])]) for g in geo]
    cand["is_point"] = [g.geom_type.endswith("Point") for g in geo]
    cand["days"] = [active_days(r) for r in cand.itertuples()]

    pairs = pd.read_parquet(STAGE1 / "stage4/out/timing_pairs_near_town.parquet")
    pairs = pairs[pairs.part == "A"]
    paths = pd.read_parquet(STAGE1 / "out/exit_paths.parquet")
    paths = paths[paths.ring_radius_km == 20]
    net = inputs.load_network()
    edge_geom = dict(zip(net["edges"].edge_id.values, net["geom"]))

    exit_rows, pair_rows = [], []
    for pr in pairs.itertuples():
        s, e = pd.Timestamp(members.loc[pr.event_id, "s"]), pd.Timestamp(members.loc[pr.event_id, "e"])
        window = pd.date_range(s, e + pd.Timedelta(days=PAD_AFTER_D), freq="D")
        per_exit_days, per_exit_days_located = [], []
        for ex in paths[paths.ucl_code == pr.ucl_code].sort_values("exit_index").itertuples():
            line = shapely.union_all([edge_geom[x] for x in ex.edge_ids])
            days, days_located, hits = set(), set(), []
            for c in cand.itertuples():
                lim = POINT_M if c.is_point else LINE_M
                if shapely.distance(c.geom, line) > lim:
                    continue
                overlap = set(c.days) & set(window)
                if not overlap:
                    continue
                days |= overlap
                if c.is_point:
                    days_located |= overlap
                hits.append(dict(ucl_code=pr.ucl_code, town=pr.town, event_id=pr.event_id, exit_index=ex.exit_index,
                                 candidate_id=c.candidate_id, road=c.road_identity, section=c.section_or_location,
                                 match_type="located (point)" if c.is_point else "named corridor, section approximate",
                                 record_first_seen=str(pd.Timestamp(c.start_time_upper).date()),
                                 record_active_days_in_window=len(overlap), closure_type=c.closure_type_or_severity,
                                 match_confidence=c.match_confidence, source=c.source_name))
            exit_rows += hits
            per_exit_days.append(days)
            per_exit_days_located.append(days_located)
        common = set.intersection(*per_exit_days) if per_exit_days else set()
        common_loc = set.intersection(*per_exit_days_located) if per_exit_days_located else set()
        pair_rows.append(dict(ucl_code=pr.ucl_code, town=pr.town, event_id=pr.event_id, exits=pr.exits,
                              exits_with_record=sum(1 for d in per_exit_days if d),
                              exits_with_located_record=len({h["exit_index"] for h in exit_rows
                                                             if h["ucl_code"] == pr.ucl_code and h["event_id"] == pr.event_id
                                                             and h["match_type"].startswith("located")}),
                              all_exits_recorded_same_day=bool(common),
                              first_common_day=str(min(common).date()) if common else "",
                              all_exits_located_same_day=bool(common_loc),
                              satellite_first_hit_near_town=str(pr.first_hit_K5km)[:10] if pd.notna(pr.first_hit_K5km) else "",
                              satellite_spread_hours_near_town=pr.spread_hours_K5km))
    ex = pd.DataFrame(exit_rows)
    pp = pd.DataFrame(pair_rows).sort_values(["exits_with_record", "town"], ascending=[False, True])
    ex.to_csv(OUT / "exit_record_matches.csv", index=False)
    pp.to_csv(OUT / "cutoff_record_summary.csv", index=False)
    assert aussef_before == inputs.sha256(inputs.AUSSEF_DB)
    meta = dict(run_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), cutoffs=len(pp),
                with_any_record=int((pp.exits_with_record > 0).sum()),
                all_exits_recorded=int((pp.exits_with_record == pp.exits).sum()),
                all_exits_same_day=int(pp.all_exits_recorded_same_day.sum()),
                all_exits_located_same_day=int(pp.all_exits_located_same_day.sum()),
                max_located_exits=int(pp.exits_with_located_record.max()),
                towns_matched_by_top_line_record=int(ex[~ex.match_type.str.startswith("located")].groupby("candidate_id").ucl_code.nunique().max())
                if len(ex) else 0,
                top_line_record=(ex[~ex.match_type.str.startswith("located")].groupby("candidate_id").ucl_code.nunique().idxmax())
                if len(ex) else "", records=len(cand),
                records_matched=int(ex.candidate_id.nunique()) if len(ex) else 0)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2))
    write_results(pp, ex, meta)
    print(json.dumps(meta, indent=2))
    print(pp.to_string(index=False))
    if len(ex):
        print(ex[["town", "exit_index", "road", "section", "match_type", "record_first_seen", "record_active_days_in_window"]].to_string(index=False))


def md(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(str(fn(r)) for _, fn in cols) + " |" for _, r in df.iterrows())


def write_results(pp, ex, meta):
    pcols = [("Town", lambda r: r.town), ("Exits", lambda r: r.exits), ("Exits with a record", lambda r: r.exits_with_record),
             ("…of which located", lambda r: r.exits_with_located_record),
             ("All exits, located records, same day?", lambda r: "yes" if r.all_exits_located_same_day else "no"),
             ("All exits incl. corridor records, same day?", lambda r: f"yes ({r.first_common_day})" if r.all_exits_recorded_same_day else "no"),
             ("Satellite: fire near town first", lambda r: r.satellite_first_hit_near_town or "undated")]
    ecols = [("Town", lambda r: r.town), ("Exit", lambda r: r.exit_index), ("Road", lambda r: r.road),
             ("Section / location", lambda r: r.section), ("Match", lambda r: r.match_type),
             ("Record first seen", lambda r: r.record_first_seen), ("Days active in fire window", lambda r: r.record_active_days_in_window)]
    text = f"""# Stage 5 results: checking against real road-closure records (descriptive, no pass/fail)

## Summary

- 2019–20 full cut-offs checked: **{meta['cutoffs']}**.
- **Using only records with a real location (Live Traffic points):**
  - Every exit recorded closed on the same day: **{meta['all_exits_located_same_day']}** cut-offs.
  - The most exits of any one cut-off with a located record: **{meta['max_located_exits']}**.
- Including the approximate "named corridor" records (see the warning below):
  - {meta['with_any_record']} cut-offs have a record on at least one exit.
  - {meta['all_exits_recorded']} have a record on every exit.
  - {meta['all_exits_same_day']} have every exit covered on the same day.
- {meta['records_matched']} of the {meta['records']} curated closure records matched an exit of a cut-off town.

**Warning about the corridor records.** A single briefing record, `{meta['top_line_record']}`, matched
exits of **{meta['towns_matched_by_top_line_record']} different towns**. The earlier work mapped it as the whole named highway
near a very large fire complex, so it cannot say *which* stretch was shut. Every "same day" result
that relies on corridor records comes from such matches. **Treat them as unreliable.** The
located-only figures are the ones to use.

### In plain words

The official records we have are thin. They cover only a handful of roads, the Live Traffic snapshots
start on 12 January 2020, and the government briefing lists cover only some days in December 2019.
Most of the cut-offs we inferred happened on 30–31 December 2019, which is inside the gap. So the
records can **confirm some individual road closures** near cut-off towns, but they cannot confirm
or rule out that all of a town's roads were shut together. A missing record does not mean a road was open.

## Each cut-off

{md(pp, pcols)}

## Matched records

{md(ex, ecols) if len(ex) else 'No record matched any exit.'}

"Named corridor, section approximate" matches come from government briefing lists that give a road
name and a rough section. They were placed on the map using named roads near the fire, so a match
means "this named road was reported closed somewhere nearby", not "this exact stretch was closed".

## Caveats

- The records cover only selected days and roads. Absence is not evidence of an open road.
- A record's first-seen time is when a snapshot or briefing captured it, not the true start.
- Line matches are approximate (see above).
- This is descriptive only and plays no part in any verdict.
"""
    (HERE / "RESULTS.md").write_text(text)


if __name__ == "__main__":
    main()
