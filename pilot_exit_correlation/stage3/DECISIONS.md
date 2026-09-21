# Judgment calls: stage 3

| # | Date | Decision | Reason |
|---|---|---|---|
| F1 | 2026-09-22 | Timing data from DEA Hotspots WFS (public, no account); download approved by the user. | The user chose this source; it covers Aug 2002 to the present. |
| F2 | 2026-09-22 | The "same time" window is 12 h, with 6 h and 24 h as sensitivity. | User decision. |
| F3 | 2026-09-22 | The satellite era starts on 2002-09-01. | The DEA archive starts on 2002-08-27; starting a few days later avoids partial coverage. |
| F4 | 2026-09-22 | Hotspots are downloaded only for events that isolate ≥ 1 town. | Only those events can produce a timed full cut-off, so this is smaller than the plan's "events cutting ≥ 1 exit" and gives the same answer. |
| F5 | 2026-09-22 | An event with no end date ends at start + 30 days; the query window is start − 1 d to end + 7 d. | Many historical records have only an ignition date. Too short a window would leave late exits undated. |
| F6 | 2026-09-22 | Hotspots must lie within D of the fire perimeter as well as within D of the exit's closed edges. | Excludes detections from unrelated fires and industrial heat sources nearby. |
| F7 | 2026-09-22 | No confidence filter on hotspots. | A filter would add another tunable threshold, and the location distance already restricts matches. |
| F8 | 2026-09-22 | Hotspot queries use a lat/lon BBOX (WFS 2.0 axis order lat, lon), paged with `count=10000` and `sortBy=id`. | Verified read-only on 2026-09-22: 5,499 hits for Batemans Bay on 30–31 Dec 2019. |
| F9 | 2026-09-22 | The downloaded cache is frozen: later runs use the cache and verify its SHA-256, and never re-query. | The live database can be reprocessed, so freezing keeps the result reproducible. |
