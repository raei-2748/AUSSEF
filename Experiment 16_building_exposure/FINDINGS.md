# Experiment 16: exposure by building type

Date: 2 Oct 2026. Rules fixed first in `PRESPEC.md` and hash-locked in `LOCK.txt` before any damage count or
jobs/earnings outcome was compared with any exposure. Post-hoc checks are labelled. Source IDs (E16-xx) refer to
`bibliography/parts/exp16_building_exposure_2026-10-02.csv`; every number below is computed from those sources.

## Short answer
1. **We now have an exposure table by building function** for all 218 council x fire rows: homes, residents, farm
   homes, workplaces (shops/offices/factories), public facilities (schools, hospitals, halls, fire stations),
   farmland, roads, bridges, railways and power lines, inside each fire outline and within 1 km
   (`results/EXPOSURE_COUNCIL_FIRE.csv`).
2. **Fires seldom reach workplaces.** Shops, offices and factories sit in town centres; fire outlines mostly stop at
   the town edge. In Black Summer, all NSW fire outlines together held about 14,700 homes but the equivalent of only
   about 4 whole Commercial/Industrial mesh blocks (about 99 within 1 km).
3. **Damage check (pre-registered): none of the type-matched counts was clearly better than plain area burned at
   ranking councils' losses.** Farm homes ranked outbuilding losses worse than all homes inside the fire did. Post
   hoc: "homes inside the fire" had the highest correlation with every loss type, but beat area burned clearly only
   for outbuildings. Losses of different building types happen in the same places.
4. **Jobs and earnings test (pre-registered): cannot tell workplace exposure and home exposure apart** for any of the
   4 outcomes (the contrasts are wide: up to about +/-1.5% per 10 percentage points). Neither exposure on its own
   showed a "worse" effect near the fire. The single-exposure bounds are tight: per 10 percentage points of an
   SA2's workplaces within 1 km of a fire, unemployment rose by less than 0.02 points (not detected, CI
   [-0.07, +0.02]) and business numbers fell by less than 0.2% (not detected, CI [-0.18%, +0.53%]). This means
   "not visible at SA2 scale", not "no effect".

## 1. What was inside the fires, by function (descriptive, outcome-free)
All NSW fires starting in the financial year, counted once (union of outlines; `results/SEASON_TOTALS_BY_FUNCTION.csv`,
`season_totals.py`). Census mesh blocks (E16-07 to E16-11), fire outlines (E16-12), OpenStreetMap 1 Jan 2019 (E16-14).

| Black Summer 2019-20 (425 fires) | Inside outline | Within 1 km |
|---|---|---|
| Area (km2) | 54,241 | 68,873 |
| Residents | 28,718 | 178,746 |
| Homes (dwellings) | 14,676 | 87,636 |
| ...of which farm homes (Primary Production mesh blocks) | 3,837 | 8,150 |
| Workplace mesh blocks (Commercial + Industrial; 1 = one whole block) | 4.2 | 98.8 |
| Public-facility mesh blocks (Education + Hospital/Medical) | 7.2 | 80.2 |
| Farmland (Primary Production, km2) | 7,350 | 12,532 |
| OSM mapped workplace sites (shops, offices, pubs, motels, wineries...) | 97 | 1,068 |
| OSM mapped public sites (schools, clinics, fire stations, halls, churches) | 76 | 438 |
| ...of which emergency (fire, police, ambulance stations) | 20 | 76 |
| Major roads (km) | 2,773 | 5,220 |
| Local roads (km) | 5,971 | 10,453 |
| Tracks (km) | 14,671 | 17,687 |
| Road and rail bridges (OSM bridge segments) | 391 | 898 |
| Power lines (km) | 1,405 | 2,014 |

Every other season was far smaller (largest inside-outline home count: 1,839 in 2023-24). Across all 11 seasons the
inside-outline workplace count never exceeded 4.2 mesh blocks. Notes: OSM land-use areas (e.g. a retail or industrial
zone) count as one workplace "site", and every OSM shed counts as "farm". In this season table the Census vintage is
set per financial year (2021 Census from 2020-21), while the council table sets it by the event's first fire
(2016 Census for fires starting Jul-Dec 2020).

How it was measured (`build_exposure.py`): each mesh block's homes, people and land are spread evenly over its area
(the Experiment 7 method, E16-02); a mesh block's category (Residential, Commercial, Industrial, Education,
Hospital/Medical, Primary Production...) is its main land use. 2016 Census for fires up to 2020, 2021 after.
OpenStreetMap features got one class each (public > workplace > farm > home > other building).
Checks: the new "homes inside" count reproduces the project's existing column for all 218 rows (largest
difference 0.08 homes; E16-03) and the SA2 version reproduces Experiment 7's Day 9 dose exactly (E16-01).

## 2. Does each exposure type predict what was actually destroyed? (pre-registered)
Spearman rank correlation with the destroyed count across council x fire rows; 95% CI from 2,000 bootstraps over
councils (`damage_check.py`, `results/DAMAGE_CHECK.csv`). Damage counts: homes from the panel (E16-04); facilities
(non-residential buildings) and outbuildings from the master workbook (E16-05, E16-30; mostly the Commonwealth
National Bushfire Recovery Agency LGA profiles, E16-31).

| Damage (rows) | Matched exposure | rho | Area burned rho | Matched minus area | Homes (same zone) rho | Verdict |
|---|---|---|---|---|---|---|
| Homes destroyed (135) | homes inside | 0.76 [0.66, 0.83] | 0.70 | +0.07 [-0.02, +0.14] | - | Not better than area burned |
| Facilities destroyed (54) | workplace + public mesh blocks within 1 km | 0.62 [0.41, 0.80] | 0.71 | -0.10 [-0.30, +0.13] | 0.66 | Not better than area burned |
| Outbuildings destroyed (65) | farm homes inside | 0.76 [0.61, 0.85] | 0.75 | +0.01 [-0.11, +0.13] | 0.86 | Not better than area burned |

- Facilities and outbuildings counts are almost all Black Summer (50 of 54 and 52 of 65 rows), so this is mostly a
  comparison between councils within one season. Black-Summer-only results are the same (in the CSV).
- The two Black Summer declarations overlap (AGRN 871 and 880 share 9 fires; 7 councils have rows under both), so
  some council-total damage counts may appear twice. Post hoc (after the audit), dropping the 880 rows changes
  nothing: homes 0.76 [0.67, 0.83], +0.07 [-0.01, +0.14] vs area; facilities unchanged (no 880 rows);
  outbuildings 0.76 [0.62, 0.86], +0.01 [-0.10, +0.13]; all still "not better than area burned"
  (`results/posthoc/DAMAGE_CHECK_WITHOUT_880.json`).
- Why this differs from Experiment 7 Day 8 ("homes inside" clearly beat area): Day 8 compared predictions made with
  the season left out, against area as a share of the council, in a rate model. Here the comparison is a plain rank
  correlation with area burned in km2, which already ranks councils well. The two are not in conflict.

- Pre-registered type-specificity check: farm homes ranked outbuildings WORSE than all homes inside the fire
  (farm homes minus homes -0.11 [-0.23, -0.02]); for facilities, matched minus homes within 1 km was
  -0.04 [-0.16, +0.07].

**Post hoc (not pre-registered, chosen after seeing Part 1; `posthoc.py`, `results/posthoc/POSTHOC_DAMAGE.json`):**
- Homes inside the fire ranked outbuildings destroyed better than area burned: +0.12 [+0.04, +0.21].
- For facilities, homes inside had the highest correlation (0.79), but not clearly above area burned:
  +0.08 [-0.03, +0.21]. OSM workplace + public sites inside: 0.76, +0.04 [-0.09, +0.20] over area.
- For homes destroyed the pre-registered verdict stands: +0.07 [-0.02, +0.14], not clearly better than area.
- Reading: losses of all building types happen in the same places, so the homes count is a reasonable all-purpose
  guide, though not clearly better than area burned except for outbuildings.
  The Census categories are too coarse for non-residential buildings: a whole Commercial mesh block counts as one,
  and shops inside Residential blocks are missed.

## 3. Do workplaces near the fire link to jobs and earnings better than homes near the fire? (pre-registered)
SA2 x financial-year panel, the Experiment 7 Day 9 design (`employment_test.py`; SA2 and region-by-year fixed
effects, SEs clustered by SA3). Exposure = share of the SA2's homes (H) or workplaces (W = Commercial/Industrial mesh
blocks; W_osm = OpenStreetMap workplace sites) within 1 km of fires starting that year. Effect = average over the
fire year and the next two years, per 10 percentage points. Outcomes: unemployment rate (DEWR, E16-18), number of
income earners and total income (ABS, E16-20), number of businesses (ABS CABEE, E16-19); via E16-17.

Sign conventions: the "alone" columns are raw changes (unemployment in points, others in %); the "minus" column is
signed so that positive = workplace exposure is the more harmful one.

| Outcome (worse =) | Homes alone | Workplaces alone (W) | Workplace minus home, joint model (W / W_osm) | Verdict |
|---|---|---|---|---|
| Unemployment rate, pts (up) | -0.01 [-0.07, +0.05] | -0.03 [-0.07, +0.02] | -0.06 [-0.20, +0.08] / -0.05 [-0.28, +0.19] | Cannot tell apart |
| Income earners, % (down) | +0.16 [-0.21, +0.54] | +0.04 [-0.18, +0.26] | +0.25 [-0.67, +1.16] / +0.00 [-1.25, +1.26] | Cannot tell apart |
| Total income, % (down) | +0.05 [-0.42, +0.52] | -0.01 [-0.32, +0.30] | +0.12 [-0.90, +1.14] / -0.05 [-1.57, +1.48] | Cannot tell apart |
| Businesses, % (down) | +0.29 [-0.27, +0.86] | +0.18 [-0.18, +0.53] | +0.20 [-0.91, +1.31] / +0.37 [-1.16, +1.89] | Cannot tell apart |

All 8 Holm-adjusted p-values are 1.0. Placebos (the two years before the fire) include 0 in all primary single
models. Pre-specified fit comparison (share of within-SA2 variation explained, single models): workplace (W) vs
homes (H): unemployment 0.59% vs 0.35%, earners 0.03% vs 0.33%, total income 0.04% vs 0.15%, businesses 0.42% vs
1.15%. All are tiny; neither exposure explains much.
- Not detected, with bounds per 10 pp of an SA2's workplaces within 1 km of a fire: unemployment up by less than
  0.02 points, earners down by less than 0.18%, total income down by less than 0.32%, businesses down by less than
  0.18%. For a whole SA2 (100%), multiply by 10.
- 623 SA2s for unemployment and income, 639 for businesses. SA2-years with at least 10% of their workplaces within
  1 km of a fire: 198 (unemployment), 78 (income panels, which end in 2021-22), 209 (businesses).
- Inside the outline (secondary, no verdict): too few SA2-years (4 with W >= 10%) to say anything; the home and
  workplace CIs all include 0. Public facilities inside (6 SA2-years >= 10%) showed higher earners and income
  afterwards, but the years before the fire were already higher (placebo fails), so no claim; their business count
  was higher too, +0.64% [+0.05, +1.23] (the "better" direction, placebo passes), which on 6 SA2-years is not
  something to build on.

## What this means
- For the report: the useful new product is the exposure table (what was inside each fire, by function).
  Splitting by building type did not add predictive power with the data we have; "homes inside the fire" and area
  burned remain the simplest guides to building losses of every type.
- Workplace losses are rare in NSW fires, and when they happen they are a few businesses in a few towns (Black
  Summer: about 97 mapped workplace sites inside outlines). At SA2 scale that may be too small to show up in
  unemployment, earners or business counts. A finer test would need jobs counted where people work.

## Limits
- Black Summer dominates every test; COVID and the 2022 floods follow it.
- OpenStreetMap 2019 is incomplete, especially in the bush (inside NSW: 210,247 mapped areas, of which 47,746
  tagged as houses, against about 3.4 million dwellings in the 2021 mesh-block counts); OSM numbers are "mapped
  sites", and a school mapped as both a site and a building can count twice.
- Fires before 2015 are not in the outline file, so their exposure is coded 0 in the lagged terms (e.g. the
  2013-14 fires fall in the comparison group).
- The 1 km zone includes unburned land ("near the fire", not "burned").
- Census 2021 mesh blocks (after Black Summer) are used for the SA2 panel, as in Experiment 7.
- Outcomes are by where people live (unemployment, income) or where businesses are registered, not by workplace.

## Decisions for Ray (nothing downloaded)
1. **NEXIS building exposure (Geoscience Australia)**: open (CC BY 4.0) commercial, industrial and residential
   building counts by SA1 for 2015, 2016, 2017 and 2020, via AURIN public download links listed on data.gov.au
   (E16-26, E16-27). File size not yet known; I would check it is under 40 MB before downloading. It would replace
   whole-mesh-block counts with building counts. OK to download?
2. **Jobs by place of work (ABS Census 2021, TableBuilder)**: needs your free TableBuilder account (E16-28, E16-29:
   the 2021 DataPacks page lists no Working Population Profile). A table of jobs by Destination Zone (and industry)
   for NSW would let us measure "jobs inside / near the fire" directly.
3. Possible next test (not run): roads, bridges and power lines inside the fire vs council repair grants
   (Experiment 11 grants data).

## Audit (independent fresh reviewer, `audit/AUDIT.md`)
All locked hashes match; the council table re-runs byte-identical; the reviewer's own code re-derived the exposure
values for 4 rows, the three primary damage correlations and 4 joint jobs models (match to 4 decimals). Fixes made
after the audit: softer wording on "homes inside" (it beat area burned clearly only for outbuildings), the 871/880
overlap disclosed and checked (post hoc), sign conventions stated, the pre-specified fit comparison added, OSM
counts restricted to NSW. Not changed: a comment in the locked `build_exposure.py` calls "inside" primary for the
SA2 file; PRESPEC (1 km primary for the jobs test) is what the analysis followed. The analysis scripts were written
after the lock, so the lock fixes the plan and the exposure data, not the analysis code.

## Files
`PRESPEC.md`, `LOCK.txt` (hashes), `extract_osm.py` (OSM pull), `build_exposure.py` (exposure tables),
`damage_check.py` (Part 1), `employment_test.py` (Part 2), `posthoc.py` (post hoc), `season_totals.py`
(season totals), `run.sh` (runs any script in a throwaway uv environment). Results in `results/`; derived data in
`data/` (OSM NSW extract 2019, SA2 x year exposure; logs). Audit: `audit/AUDIT.md`.
