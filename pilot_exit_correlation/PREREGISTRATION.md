# Pre-registration: correlated-exit-failure pilot

**Date registered:** 2026-09-21, before any community-level exit, closure or rho value was computed.
**Status:** frozen. Do not edit after results exist. Record any deviation in `DEVIATIONS.md`.

## Question
Do all of a community's exit roads fail together in mapped fires more often than they would if
exits failed independently? This is a measurement pilot. No prediction, no machine learning, no
causal claim.

## Inputs
As frozen in `RUN_LOG.md`: the 2019-01-01 OSM road network (EPSG:3577), the fire-family × road-edge
overlay `analysis.fire_road_exposure_v2`, fire-family membership `main.disaster_family_members`,
Geoscience Australia event perimeters, and ABS UCL 2021 boundaries with 2021 Census population (G01 `Tot_P_P`).
Any input hash mismatch stops the run.

## Definitions

**Communities.** NSW UCL 2021 polygons with 2021 Census usual-resident population ≥ 200,
reprojected to EPSG:3577.

**Road graph.** An undirected graph built from 2019 network edges, excluding `highway = service`.
Egress is treated as undirected because the stored network carries no legal one-way routing.
Parallel edges between the same node pair are kept as separate unit-capacity links.

**Exits (radius R).**
- Primary R = 20 km; sensitivity runs at R = 10 km and R = 30 km.
- Sources: network nodes inside the community polygon. If there are none, use the endpoints of edges intersecting the polygon.
- Ring (sink): the outside endpoints of edges that cross the circle of radius R centred on the polygon centroid.
- Exits = the maximum number of edge-disjoint source-to-ring paths, computed by unit-capacity max-flow.
- One path decomposition is stored per community: the minimum-total-length set of that many edge-disjoint paths (min-cost max-flow). Decompositions are not unique.
- A community whose polygon extends to or beyond the R circle is flagged `ring_inside_polygon`. Its exits are missing and it is ineligible at that R.

**Relevant fires.** Fire families (all 1,034; seasons 2019-20 to 2022-23) whose unioned footprint
lies within 30 km of the community polygon.

**Closure.**
- Primary rule S0: an edge is closed by a family if the overlay's `direct_burned_m > 0`.
- Sensitivity rule S100: an edge is closed if `nearest_burn_distance_m <= 100`.
- A family closes exit j if any edge on exit j's stored path is closed.

**Observed isolation.** For each community and relevant fire, remove every edge that fire closes
and test for any remaining source-to-ring path. Isolated means none remains.

**Metrics** (n relevant fires, k isolating fires, c_j fires closing exit j):
- P_obs = (k + 0.5) / (n + 1), with Jeffreys smoothing.
- p_j = (c_j + 0.5) / (n + 1), with Jeffreys smoothing; P_ind = the product of p_j over all exits.
- rho = P_obs / P_ind. **rho is missing (not zero) when k = 0** (user decision; this prevents smoothing alone from producing a large rho). rho is also missing when exits are missing or n = 0.
- Bootstrap: 1,000 resamples of relevant fires with replacement, fixed seed 20260921, giving 95% percentile intervals.
  - A resample with k = 0 has undefined rho. It is ranked below every defined value, so it cannot support a lower bound > 1.
  - If the 2.5th-percentile position falls among undefined resamples, the lower bound is reported as missing and counts as "not > 1".
- N_eff (secondary):
  - Build the phi (Pearson) correlation matrix of exit-closure indicators across relevant fires, using exits that close in at least one fire and not in every fire (constant columns are excluded and counted).
  - Eigenvalues λ; N_eff = (Σλ)² / Σλ².
  - N_eff = 1 if exactly one exit remains; missing if none remain.

**Eligibility** (at each R and rule): exits ≥ 2 and relevant fires ≥ 10, and not `ring_inside_polygon`.
The number of communities failing each criterion is reported.

## Decision rule (primary: S0, R = 20 km)
**PASS** if at least 20% of eligible communities have rho > 5 **and** a bootstrap lower 95% bound > 1.
Otherwise **FAIL**. The denominator is all eligible communities, including those with missing rho.
A FAIL is reported plainly and no threshold is tuned afterwards.

**Stop rule.** If fewer than 10 communities are eligible under S0 at R = 20 km, the result is
reported as NOT EVALUABLE with the count, and no verdict is issued.

S100 and R = 10/30 km are sensitivity analyses only and do not change the verdict.

## Required caveats
- Final fire perimeters assume every road inside closed at the same moment. This overstates simultaneous failure, so rho is an upper bound. A later stage will test timing with daily satellite fire progression.
- Closure is inferred from mapped footprints, not from observed closure records.
- Fire events affecting the same community are not independent replications.
