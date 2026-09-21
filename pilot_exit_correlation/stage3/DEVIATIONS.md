# Deviations from stage3/PREREGISTRATION.md

| # | Date | Change | Reason | Effect on verdict |
|---|---|---|---|---|
| Z1 | 2026-09-22 | The first full run was stopped during the timing step, after all 12 hotspot downloads had completed and been cached. `s3/timing.py` now filters hotspots near the exit roads (spatial index) before the fire-perimeter distance test, instead of testing every hotspot against the perimeter. | The original order took over 30 minutes per large fire. The qualifying hotspots are identical by construction (both conditions are still required), and the toy tests pass unchanged. No results had been produced. | None. Implementation speed only. |
| Z2 | 2026-09-22 | Added a results section explaining that the timing rule measures first arrival at each exit route, not overlapping closure. | This limit only became visible from the per-town timing table (e.g. Batemans Bay about 35 days). It is needed to interpret the FAIL correctly. | None. The pre-registered verdict is unchanged. |
