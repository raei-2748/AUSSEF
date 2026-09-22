# Pre-registration: stage 5, checking against real road-closure records

**Date registered:** 2026-09-22. Written before matching any closure record to any exit.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Purpose and status
Stages 2–4 infer road closure from fire maps and satellite detections. Stage 5 asks how many of the
inferred 2019–20 cut-offs are backed by **official closure records**. This is **descriptive only,
with no pass/fail**. The records are too few and too patchy for a test: 37 curated candidates,
Live Traffic snapshots only from 12 January 2020, and briefing lists only for selected days in
September and December 2019.

## Records used
`transport_criticality.duckdb` → `analysis.road_closure_candidates` (37 rows; hash-frozen database). The fields used are:
- the geometry (EPSG:4326 WKT)
- the first-seen time (`start_time_upper`)
- the last-seen or end bound (`end_time_upper`, else `end_time_lower`)
- the closure type and match confidence
- the source

Each record's **active days** run from the first-seen day to the end bound. When there is no end
bound, it runs to the first-seen day only for a single briefing observation, or to 2020-01-31 (the
archive end) when right-censored.

## Cut-offs checked
All part-A (2019–23) perimeter full cut-offs in the satellite-era sample, with the stage-4
near-town timing (`../stage4/out/timing_pairs_near_town.parquet`).

## Matching a record to an exit
A record matches exit j of a town if:
- **Place:**
  - For a point record (Live Traffic), the point lies within 1 km of exit j's stored path.
  - For a line record (Home Affairs named corridor), some part lies within 100 m of exit j's path.
- **Time:** its active days overlap the fire event's window (event start to end + 7 days).

Line records are labelled "named corridor, section approximate". The earlier work built them from
named OSM roads within 20 km of the fire, not from the exact closed section.

## What is reported (all descriptive)
- For each cut-off: how many exits have at least one matching record, split into located (point) and approximate (line) matches.
- For each cut-off: whether any single day has a matching record active on **every** exit, meaning records show all exits closed at once.
- For matched exits: the first-seen date of the record next to the satellite near-town hit date.
- Overall: the share of cut-offs with ≥ 1 matched exit, and with all exits matched.

## Caveats
- Absence of a record does not mean a road was open. The archive has gaps.
- Line matches are approximate.
- A record's first-seen time is when a snapshot or briefing captured it, not the true closure start.
