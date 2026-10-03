# Experiment 16: exposure by building type. Rules fixed first

Written 2026-10-02, before any damage count or employment/earnings outcome was compared with any exposure measure.
Locked by SHA-256 in `LOCK.txt`. Anything added later is labelled "post hoc".

What was looked at before locking (all outcome-free):
- The exposure measures themselves (`build_exposure.py`): the SA2 homes measure reproduces Experiment 7's Day 9
  dose exactly (max difference 0.0); correlations between exposure measures; how many SA2-years are exposed.
- Coverage only (number of non-missing rows) of the damage columns in the master workbook.
- While checking what "facilities" means (fire_event_dataset/src/dl_council.py: "non-residential buildings"), the
  source rows for Armidale, Ballina and Bega Valley (2019-20) were seen on screen. No damage count was compared with
  any exposure measure.

## Why
Experiment 7 showed that "homes inside the fire outline" predicts homes destroyed far better than area burned.
Ray's point: different buildings drive different losses. Homes -> lost housing; shops, offices, factories, farm
buildings -> lost jobs and income; schools, halls, clinics -> lost services; roads, bridges, power -> repair costs.
So we measure what was inside (and within 1 km of) each fire outline BY FUNCTION and test two things.

## Exposure measures (outcome-free; already built)
Council x fire (218 rows, `results/EXPOSURE_COUNCIL_FIRE.csv`), inside the outline (`_in`) and within 1 km (`_1km`):
- Census mesh blocks (MB; 2016 Census for events starting up to 2020, 2021 after). Counts spread evenly over each MB:
  `homes`, `residents`, `farm_homes` (dwellings in Primary Production MBs), `workplace_mb` (Commercial + Industrial
  MBs, area-share weighted), `public_mb` (Education + Hospital/Medical MBs), `farm_km2` (Primary Production land).
- OpenStreetMap snapshot 1 Jan 2019: mapped sites by class (`osm_home`, `osm_workplace`, `osm_public` with school /
  health / emergency / hall_library / worship, `osm_farm`, `osm_other_building`), road km (major, local, track),
  `bridges`, `rail_km`, `power_line_km`.
SA2 x financial year (all NSW fires starting in the FY, inside the outline, Census 2021 MBs):
- H = share of the SA2's dwellings inside; W = share of its Commercial+Industrial MBs inside;
  W_osm = share of its OSM workplace sites inside; F = share of its Primary Production land inside;
  P = share of its Education+Hospital MBs inside; A = share of its land inside.
- The same within 1 km of the outline (outline included): H_1km, W_1km, W_osm_1km, F_1km, P_1km, A_1km.

Known before the test (outcome-free): fires seldom reach workplaces INSIDE the outline. SA2-years with >= 10%
exposed inside: H 20 (19 in 2019-20), W 4 (3 in 2019-20), W_osm 10 (all 2019-20), F 22. Within 1 km there is much
more variation: H_1km 404, W_1km 213, W_osm_1km 340. Council x fire: only 1 of 218 rows has >= 1 whole
Commercial/Industrial MB inside the outline, while the 1 km zone reaches up to 28. Therefore the workplace
comparisons below use the 1 km zone as primary (as Experiment 7 Day 7 did for residents); inside is secondary.
Among SA2-years touched within 1 km, Spearman correlations: H_1km-W_1km +0.44, H_1km-W_osm_1km +0.61. A "cannot
tell apart" result would mean "not visible at this scale", not "no effect".

## Part 1. Does each exposure type predict what was actually destroyed? (council x fire rows)
Damage counts (master workbook; per council x event; council total unless the scope column says one fire):
| Damage | Rows | Matched exposure (primary, inside) | Other exposures reported |
|---|---|---|---|
| Homes destroyed (homes_per_1000_v2_inferred x dwellings / 1,000) | 135 | `homes_in` | OSM homes |
| Facilities destroyed (non-residential buildings; DL_facilities_destroyed_sourced) | 54 | `workplace_mb_1km + public_mb_1km` (within 1 km) | inside version; OSM workplace+public sites (inside and 1 km) |
| Outbuildings destroyed (DL_outbuildings_destroyed_sourced) | 65 | `farm_homes_in` | `farm_km2_in`; OSM farm+other buildings |
Comparison exposures for every damage type: area burned in the council (`burned_km2`) and homes in the same zone as
the matched exposure (`homes_in`, or `homes_1km` for facilities).
Statistic: Spearman rank correlation with the destroyed count. Uncertainty: bootstrap over councils (resample
region_id with replacement, all its rows kept together), 2,000 draws, seed 20261002, percentile 95% CI.
Verdict per damage type:
- "Matched exposure works" if its rho CI is above 0 AND rho(matched) - rho(area burned) has a CI above 0.
- "Type-specific" if in addition rho(matched) - rho(homes, same zone) has a CI above 0 (facilities and
  outbuildings only).
  If not, the honest reading is "homes inside the fire does as well".
- Otherwise "not better than area burned", with the CI.
Also reported: the 1 km versions, and the same rows restricted to 2019-20 (Black Summer).

## Part 2. Do workplaces inside the fire link to local jobs and earnings better than homes inside the fire?
SA2 x financial-year panel (the Experiment 7 Day 9 set-up). Outcomes (worse direction):
- U unemployment rate, DEWR SALM unsmoothed, FY mean of quarters (up), FY 2015-2024, lags 0-4.
- E log number of income earners, ABS Personal Income Table 1.4 (down), FY 2015-2021, lags 0-2.
- I log total income, same source (down), FY 2015-2021, lags 0-2.
- B log business count, ABS CABEE, June y assigned to FY y-1 (down), FY 2015-2024, lags 0-4.
Sample filters as Experiment 7 Day 9 (SA2s in sa2_info; income: population >= 100 and positive values;
businesses: positive counts).
Primary exposures: the 1 km versions (H_1km vs W_1km, H_1km vs W_osm_1km). The inside versions are run the same
way and reported without a verdict.
Model: y[s,t] = a[s] + b[GCCSA,t] + sum_k beta_k X[s,t-k] + lambda_1 X[s,t+1] + lambda_2 X[s,t+2] + e, for each
exposure X in the model. Fixed effects swept out (alternating projections, as Day 9); SEs clustered by SA3.
Effect = mean of beta_0..beta_2 (fire year and two years after), per 10 percentage points. Placebo = mean of the
two leads.
- Single models: H only; W only; W_osm only (also F and P only, reported, no verdict).
- Joint models (the test): H + W, and H + W_osm (all 1 km versions). Contrast D = effect(workplace) - effect(home), signed so that
  positive = the workplace effect is the more "worse" one.
- Holm correction over the 8 contrasts (2 workplace measures x 4 outcomes).
Verdict per outcome x workplace measure:
- "Workplace exposure links better" if D's Holm-adjusted p < 0.05 with D > 0, AND the workplace effect in the
  joint model has a CI excluding 0 in the worse direction, AND its placebo CI includes 0.
- "Home exposure links better" if D < 0 with Holm p < 0.05, AND the home effect has a CI excluding 0 in the worse
  direction, AND its placebo CI includes 0.
- Otherwise "cannot tell apart", reported with D's CI (and each effect's CI as a bound).
Reported, no verdict: within-SA2 fit gain (R-squared after fixed effects) of W-only vs H-only models.

## Caveats stated in advance
- Black Summer dominates every test; COVID (2020-21) and the 2022 floods follow it.
- Census 2021 MBs (after Black Summer) are used for the SA2 panel, as in Experiment 7.
- OSM 2019 is incomplete, especially in the bush (274,224 mapped NSW areas, of which 63,169 tagged as houses,
  against about 3.4 million dwellings in the 2021 mesh block counts); OSM numbers are "mapped sites", not all
  buildings.
- The 1 km zone includes unburned land, so it measures "near the fire", not "burned".
- MB categories describe the main land use of each MB; a shop inside a Residential MB is not counted as a workplace.
- No jobs-by-workplace data are on disk (ABS place-of-work needs TableBuilder; NEXIS commercial/industrial SA1
  counts are open (CC BY 4.0) but not downloaded). Both are listed for Ray to approve.
