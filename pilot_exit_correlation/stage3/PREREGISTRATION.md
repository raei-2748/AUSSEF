# Pre-registration: stage 3, stricter checks on the pooled result

**Date registered:** 2026-09-22. Written before any stage-3 number (filtered or timed cut-offs,
hotspot downloads, satellite-era ratios) was computed.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Why stage 3
Stage 2 found that all exits were cut together far more often than chance would predict in the
1950–2019 record (R = 14.9, PASS). The 2019–23 test narrowly failed (R = 6.6). Two features of the
data could inflate R:
1. **The town lies inside the fire map.** An isolation can happen because streets *inside* the town fall inside the perimeter, not because the exits were cut.
2. **Final perimeters carry no timing.** Roads burned days apart look cut at the same moment.

Stage 3 tests whether the finding survives each correction.

Everything not stated here is unchanged from `../stage2/PREREGISTRATION.md`: the communities
(≥ 2 exits, no `ring_inside_polygon`), the stored exit paths, relevant fires within 30 km, the S0
closure rule, the ring at R = 20 km, the pooled ratio R = O / E, and the fire-event bootstrap
(1,000 resamples, seed 20260921).

## Stage 3a: outside-the-town closure
- A road edge counts as closed by a fire only if it lies **outside** the town polygon. Every edge intersecting the town polygon is removed from that fire's closed set before exit closure and the isolation test are evaluated.
- Run on part A (2019–23) and part B (1950–2019, confirmatory) separately.
- **Decision** for each part:
  - NOT EVALUABLE if O < 5 or fewer than 20 town–fire pairs have ≥ 1 exit cut.
  - PASS if R ≥ 2 and the lower 95% bound > 1.
  - FAIL otherwise.

## Stage 3b: satellite timing
**Sample (satellite era).** Fire events that start on or after 2002-09-01: all part-A families plus
part-B events with earliest ignition from 2002-09-01 to 2019-06-30. Each town's relevant fires are
the satellite-era events within 30 km. Both the untimed R and the timed R are computed on this same
sample.

**Hotspots.**
- Source: DEA Hotspots (Geoscience Australia) WFS layer `public:hotspots`, all sensors, with no confidence filter.
- A query is made only for fire events that isolate at least one town in the satellite-era sample. These are the only events that can yield a timed full cut-off.
- Query area: the event's bounding box padded by 0.02°.
- Query time: from the event's start minus 1 day to its end plus 7 days.
  - Event end is the latest extinguish date or the family end date.
  - When there is no end date, end = start + 30 days.

**Exit hit time.** For an isolating town–fire pair, exit j's hit time is the earliest hotspot that
lies within D metres of that fire's perimeter **and** within D metres of any edge on exit j's stored
path that the fire closes. If no hotspot qualifies, exit j is undated.

**Timed full cut-off.** The fire isolates the town (perimeter rule), every exit is dated, and the
latest hit time minus the earliest is ≤ W hours.

**R_timed** = (number of timed full cut-offs) / E, where E is the satellite-era expectation under
independence from the perimeter closures, unchanged. Undated or non-simultaneous cut-offs are counted
as not simultaneous. R_timed is therefore conservative, while the untimed R is an upper bound.

**Primary:** S0, W = 12 h, D = 1,000 m.
- NOT EVALUABLE if the satellite-era sample has fewer than 5 perimeter full cut-offs.
- Otherwise PASS if R_timed ≥ 2 and its lower 95% bound > 1 (fire-event bootstrap as in stage 2).
- Otherwise FAIL.

**Sensitivity (no verdict):** W = 6 h and 24 h; D = 500 m; timing combined with the stage-3a
outside-town rule.

**Also reported (descriptive):**
- The share of perimeter cut-offs whose exits could all be dated.
- For dated cut-offs, the hours between the first and last exit being hit.

## Reading the three results together
- Stage 2 R is the upper bound.
- 3a removes the "town inside the fire" route to isolation.
- 3b is conservative about timing.

If 3a and 3b both pass for their confirmatory samples, the finding is robust to both concerns. If
either fails, that is reported plainly as the finding.

## Required caveats
- Hotspots are satellite detections with ±375 m (VIIRS) to ±1 km (MODIS) location error, a few overpasses a day, and gaps under smoke or cloud. A hotspot near a road is not proof that the road was impassable.
- Closure is still inferred from maps and detections, not from recorded road closures.
- Fires are not independent replications.
- The 2019 road network is used throughout.
- This is descriptive measurement only: no ML, no causal or lives-saved claims.
