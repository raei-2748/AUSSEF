# Pre-registration: stage 2, pooled exit-failure test

**Date registered:** 2026-09-21. Written before any stage-2 number (pooled ratio, observed or expected
isolations, historical overlay or relevant-fire count) was computed.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Why stage 2
Stage 1 (see `../PREREGISTRATION.md`, `../RESULTS.md`) tested each town separately and returned FAIL.
No town had more than one fire that cut all its exits, so the per-town test could not work. Stage 2
asks the same question with all towns pooled, then re-tests on an independent, older fire record.

## Question
When fires reach NSW towns, are all of a town's exit roads cut at once more often than they would be
if each exit failed independently? This is descriptive measurement: no machine learning, no prediction,
no causal claim.

## Data parts
- **Part A (discovery):** the stage-1 fire families (Geoscience Australia, July 2019 to July 2023) and
  the stage-1 overlay `analysis.fire_road_exposure_v2`.
- **Part B (confirmatory, independent):** NSW bushfire records from Geoscience Australia's historical
  bushfire boundaries (product 149017, `ga_original.zip`, agency NSW PWS).
  - Includes records with `fire_type = 'Bushfire'` and an ignition date from 1950-07-01 to 2019-06-30 inclusive.
  - **Excluded:** prescribed burns; records with no ignition date; and season composites, meaning names matching "Burnt YYYY", "WF YYYY-YY", "fire season" or "wildfire YYYY" (case-insensitive). A composite merges a whole season into one shape and would fake simultaneous closure.
  - Fire events are grouped into families with the part-A rule. Two fires are linked when their date intervals are within 3 days and their perimeters are within 5 km; families are the connected components. A fire's interval runs from ignition to the extinguish date, or is the ignition day alone when there is no extinguish date.
  - Part B closure is computed from the perimeters against the same 2019 road network: S0 = the road edge intersects the perimeter; S100 = the edge lies within 100 m of it.

## Communities, exits, relevant fires
- Communities are the stage-1 UCLs (NSW, population ≥ 200) with ≥ 2 exits and no `ring_inside_polygon`, at the given ring radius R.
- Exit counts and stored exit paths are taken unchanged from stage 1 (`../out/exit_paths.parquet`, hash-frozen).
- Relevant fires: families whose footprint lies within 30 km of the community polygon.
- Isolation: a fire isolates a community when no route from the community to the ring survives after every edge that fire closes is removed.

## Main measure: pooled ratio R
For each community c with n_c relevant fires, k_c isolating fires and c_cj fires closing exit j:
p̂_cj = c_cj / n_c (raw share, no smoothing).

- Observed O = Σ_c k_c.
- Expected under independence E = Σ_c n_c × Π_j p̂_cj.
- **R = O / E.** R is missing when E = 0.

If exits failed independently, E would be an unbiased estimate of O, so R ≈ 1.

**Companion (descriptive, no decision):** among community–fire pairs where at least one exit closed
(N1 pairs), the observed share where the fire isolated the community is O / N1. The expected share
under independence is E / E1, where E1 = Σ_c n_c × (1 − Π_j (1 − p̂_cj)).

**Uncertainty:**
- Bootstrap over fire events, 1,000 resamples, seed 20260921.
- Each resample draws whole fire events (families) with replacement from all events relevant to at least one included community, then recomputes every community.
- A resample with E = 0 has undefined R and ranks below every defined value.
- 95% percentile interval, with no interpolation.

## Decision rule (S0, R = 20 km), applied to part A and part B separately
- **NOT EVALUABLE** if O < 5 or N1 < 20.
- **PASS** if R ≥ 2 and the lower 95% bound > 1.
- **FAIL** otherwise.

Part B is the confirmatory result. Part A is discovery. Both are reported whatever they show.
No threshold will be changed after results are seen.

## Sensitivity analyses (no verdict)
- S100 instead of S0.
- Ring radius 10 km and 30 km.
- Part B with undated, non-composite bushfires added, each as a single event.

## Required caveats
- Perimeters are final extents, so closure timing is unknown and simultaneity is overstated. R is therefore an upper bound on how often exits fail together.
- Closure is inferred from mapped footprints, not observed closure records.
- Fires are not independent replications. The event bootstrap handles shared fires across towns but not shared weather or seasons.
- Part B applies the 2019 road network to fires from 1950 onwards. Roads that existed at the time may differ.
- Part B coverage depends on NSW PWS mapping, which may be incomplete away from the national-park estate, especially before the 1990s.
