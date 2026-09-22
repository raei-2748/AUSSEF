# Pre-registration: stage 4, timing near the town

**Date registered:** 2026-09-22. Written before any stage-4 number was computed.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Honest status of this test
This is a **follow-up motivated by stage-3 results**, not an independent confirmatory test.

The stage-3 timing check (FAIL) dated each exit by the earliest hotspot anywhere along its stored
route. The route runs out to the 20 km ring, so fire far from town could date an exit weeks before
fire reached the stretch near town. The per-town timing table made this visible. Stage 4 asks the
evacuation-relevant version: **did fire reach every exit road near the town within the same window?**
The satellite data, sample, expected count and decision thresholds are all reused unchanged from stage 3.

## What is unchanged from stage 3 (see `../stage3/PREREGISTRATION.md`)
- The satellite-era sample: fire events from 2002-09-01, part A plus part B.
- The S0 closure rule; perimeter full cut-offs (O = 31) and the independence expectation E.
- The frozen DEA Hotspots cache (hash-verified, no new downloads).
- Hotspots must lie within D of the fire perimeter.
- The fire-event bootstrap (1,000 resamples, seed 20260921).
- Undated means "not simultaneous".

## The one change: date each exit near the town
For each exit j of an isolating town–fire pair:
- Let d_j be the distance from the town polygon to the nearest closed edge on exit j's path.
- The **near-town stretch** is the closed edges on exit j whose distance to the town polygon is ≤ max(K, d_j + 2 km).
  - Normally this is the closed edges within K km of the town.
  - If an exit's cut is entirely farther than K, it is the burned stretch closest to town.
- Exit j's hit time is the earliest hotspot within D of the fire perimeter and within D of that near-town stretch. If none qualifies, exit j is undated.
- A timed full cut-off requires every exit dated, with the spread of hit times ≤ W.

## Decision (primary: K = 5 km, W = 12 h, D = 1,000 m)
- **PASS** if R_timed ≥ 2 and its lower 95% bound > 1.
- **FAIL** otherwise.

The perimeter full cut-off count is already known to be 31 (≥ 5), so NOT EVALUABLE does not apply.

## Sensitivity (no verdict)
K = 2 km and 10 km (with W = 12 h); W = 24 h (with K = 5 km).

## Reading
If stage 4 passes, the stage-3 FAIL is attributed to dating exits far from town. That attribution is
a hypothesis supported by a post-hoc-motivated test, and it is reported as such. If stage 4 fails, the
"exits cut at different times" reading from stage 3 is strengthened.

## Caveats
All stage-3 caveats apply: hotspot location error, overpass gaps, smoke and cloud, closure inferred and
not observed, fires not independent, the 2019 network, and descriptive measurement only.
