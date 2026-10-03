# Experiment 16 audit (independent, skeptical)

Date: 2 Oct 2026. The auditor modified no existing file. All re-derivations are separate scripts in the session
scratchpad (`audit/spot_exposure.py`, `audit/damage_audit.py`, `audit/employment_audit.py`). They read the original
inputs and compare against `results/`.

**Bottom line:** the numbers are right. Every value I re-derived independently matches the results files: exposure
geometry, the three primary Spearman rho values and their bootstrap CIs, and the joint-model contrasts. All 9 lock
hashes match, and the scripts do what PRESPEC says. What needs fixing is wording in FINDINGS.md (one post-hoc
headline is overclaimed) plus several undisclosed caveats. None of them changes a pre-registered verdict.

---

## 1. Lock integrity and adherence to PRESPEC: PASS (two low-severity notes)

- **Hashes.** I recomputed sha256 for all 9 files in LOCK.txt and all 9 match, including
  `results/EXPOSURE_COUNCIL_FIRE.csv` (`cd0d0db2…`). The background rerun regenerated that file byte-identical:
  `data/rerun_hash_check.txt` and `data/_council_before_rerun.csv` both give `cd0d0db2…`. A note about this was
  appended to LOCK.txt at 22:55 (the file's mtime changed), but the hash lines are unchanged.
- **Timeline.** File mtimes are consistent with the claim. PRESPEC was saved 22:47:20 and damage_check.py
  22:47:53; the first outcome output (damage_check.log) is 22:48:18; employment_test.log is 22:49:36; posthoc.py
  22:52.
- **PRESPEC vs code.** I checked each point:
  - Zones: facilities use 1 km (`workplace_mb_1km + public_mb_1km`); homes and outbuildings use inside
    (`homes_in`, `farm_homes_in`); workplace tests use 1 km as primary.
  - Outcomes and lags: U and B use lags 0-4; E and I use lags 0-2.
  - FY windows: 2015-2024 for U and B, 2015-2021 for E and I.
  - Effect is mean β0..2 × 0.1 (per 10 pp). Placebo is the mean of the two leads × 0.1.
  - D is signed as worse(workplace) − worse(home).
  - Holm is applied over exactly the 8 primary (1 km) contrasts.
  - Verdict rules follow PRESPEC for both parts.
  - Bootstrap: resamples `region_id`, B = 2,000, seed 20261002, percentile CI.

  I found no unlabelled deviation. Post-hoc items use seed+1 and are labelled.
- **Low: the lock does not cover the analysis code.** LOCK.txt hashes the plan, the exposure code and the exposure
  data, but not `damage_check.py` or `employment_test.py`. Nothing is committed to git, so nothing outside the
  folder anchors the timestamps. This is mitigated: I checked that the code implements PRESPEC exactly. Next time,
  commit or hash the analysis scripts before running them.
- **Low: a stale comment in a locked file.** In `build_exposure.py` `sa2_fy()`, the comments say "inside the outline
  (primary)" and "within 1 km (secondary)". That is the reverse of PRESPEC. It is cosmetic only, because
  `employment_test.py` correctly treats 1 km as primary. It cannot be edited without breaking the hash, so mention
  it in FINDINGS or the next lock.
- **Low: a pre-specified item is missing from FINDINGS.** PRESPEC says the "within-SA2 fit gain of W-only vs H-only"
  is "Reported, no verdict". It is in `EMPLOYMENT_SINGLE.csv` (`r2_within`) but not in FINDINGS.md. Values for
  H vs W: U 0.004 vs 0.006; E 0.003 vs 0.000; I 0.002 vs 0.000; B 0.012 vs 0.004.

## 2. Exposure construction: PASS

**Spot check with independent code.** I used geopandas `overlay` for MB area shares and `sindex` queries for OSM,
with my own reads of the fires, LGA, mesh-block shapefiles and count files.

| Row | homes_in | workplace_mb_in | workplace_mb_1km | osm_workplace_in | bridges_in | burned_km2 |
|---|---|---|---|---|---|---|
| 871 × Bega Valley (Black Summer, 2016 MBs) | 907.365 = | 0 = | 0 = | 13 = | 55 = | 3493.22 = |
| 871 × Lithgow (Black Summer) | 510.613 = | 0.0141 = | 28.0001 vs 27.9997 | 10 = | 10 = | = |
| RAA-2016-r22 × Cessnock (2016) | 15.599 = | 0.7331 = | 26.998 vs 26.995 | 2 = | 6 = | = |
| 1075 × Tenterfield (2021 MBs) | 147.910 = | 0 = | 0 = | 1 = | 0 = | = |

"=" means identical to at least 3 decimals. The `osm_workplace_1km` and `bridges_1km` values match exactly.
`homes_1km` differs by +0.03% to +0.18%. That is fully explained by buffer resolution: my audit used shapely's
default `quad_segs=16`, the script uses 8. Not an error.

Other checks:
- **Census vintage.** The rule is 2016 MBs if the earliest linked fire started in or before 2020, otherwise 2021. It
  is applied as in `affected_pop.py`, and my rows reproduced the `census_year`. `homes_in` reproduces ANALYSIS_TABLE
  `dwellings_in_fire` for all 218 rows (maximum difference 0.081, as FINDINGS says).
- **SA2 measures.** `H` reproduces Experiment 7 `sa2_fy_dose_homes_in.parquet` exactly (maximum difference
  2.8e-17, 1,933 rows, no one-sided non-zeros).
- **PRESPEC counts.** All reproduce:
  - SA2-years with share ≥ 10%: H 20 (19 Black Summer), W 4 (3), W_osm 10, F 22, H_1km 404, W_1km 213,
    W_osm_1km 340.
  - Spearman correlations: +0.44 and +0.61 on SA2-years with any non-zero 1 km measure (n = 1,760). On all 1,933
    rows they are 0.45 and 0.61. Trivial.
- **Union of fires, clipping, units.**
  - Fires are unioned per AGRN through the `official_declaration_agrn` split.
  - Zones are cut with the same LGA 2021 shapefile as `src/regions.py`.
  - Units are EPSG:3577 metres: area / 1e6 gives km², length / 1000 gives km, the buffer is 1,000 m.
  - No double counting within a row. Each MB is weighted by its area share, clipped to [0, 1].
- **OSM classification.** The priority (`np.select`: public > workplace > farm > home > other) works on real cases:
  - building=yes + amenity=school → public (53/53)
  - house + shop → workplace
  - shed + shop → workplace
  - building=shed → farm

  Two counting quirks are not disclosed (low):
  - 12% of the 40,935 OSM "workplace sites" are `landuse=retail/commercial/industrial` polygons, counted as one
    site each alongside the shop points inside them. This is the same double-count type FINDINGS mentions for
    schools.
  - 8,063 `building=shed` features, including suburban sheds, count as "farm".
- **Bridges.** These are OSM bridge ways that intersect the zone (FINDINGS correctly says "segments"). A way that
  crosses a council line counts in both councils.

## 3. Damage check (damage_check.py): PASS

- **Merges.** Exposure → ANALYSIS_TABLE → master workbook are all 1:1 (218/218, no duplicate keys).
- **Homes destroyed.** `homes_per_1000_v2_inferred × dwellings / 1000` is integer to 6e-14 and equals the
  ANALYSIS_TABLE `homes_v2` column (135 rows).
- **Columns.** `DL_facilities_destroyed_sourced` (54 rows) and `DL_outbuildings_destroyed_sourced` (65 rows) are the
  right columns.
- **Independent re-derivation.** My own rank-correlation code and bootstrap (different RNG):

| Damage | rho file / audit | rho CI file / audit | minus area file / audit (CI) | minus homes file / audit (CI) |
|---|---|---|---|---|
| Homes (135) | 0.7614 / 0.7614 | [0.664, 0.832] / [0.664, 0.831] | +0.066 [-0.022, 0.139] / [-0.012, 0.142] | — |
| Facilities (54) | 0.6159 / 0.6159 | [0.414, 0.796] / [0.402, 0.799] | -0.095 [-0.297, 0.127] / [-0.296, 0.134] | -0.042 [-0.164, 0.072] / [-0.171, 0.086] |
| Outbuildings (65) | 0.7561 / 0.7561 | [0.606, 0.852] / [0.613, 0.852] | +0.008 [-0.108, 0.131] / [-0.110, 0.133] | -0.108 [-0.227, -0.018] / [-0.224, -0.018] |

  The point estimates are identical. The CIs differ only by Monte Carlo noise. All three verdicts ("Not better than
  area burned") follow from the rules. For homes, the minus-area CI lower bound is close to 0 (-0.02 and -0.01 in
  two independent bootstraps), so the homes verdict is near the line.
- **Medium: the AGRN 871 / 880 overlap is not disclosed.**
  - 9 fires are linked to both declarations.
  - 1,284 of AGRN 880's 1,597 km² (80%) lies inside the 871 union.
  - 7 councils have both an 871 row and an 880 row: Kempsey, Richmond Valley, Clarence Valley, Kyogle, Mid-Coast,
    Nambucca Valley, Port Macquarie-Hastings.

  So the 880 rows' exposures largely repeat part of the 871 rows' exposures. For outbuildings, the 871 rows for
  Kempsey and Richmond Valley are council totals (173, 178). Those totals presumably include losses that are also
  counted fire-specifically in the 880 rows (5, 2). Facilities have no duplicate council-season rows. The council
  bootstrap handles the dependence between rows, so verdicts are unlikely to change. FINDINGS should still state the
  overlap and ideally add a "drop 880 rows" sensitivity (labelled post hoc). `season_totals.py` takes the union of
  outlines, so the season-totals table is not affected.

## 4. Employment test: PASS

- **Independent re-derivation.** I used statsmodels OLS with explicit SA2 dummies and GCCSA×FY dummies and
  SA3-clustered SEs. I built my own lags and leads by shifted merges (dose 0 where missing) and my own SALM
  quarter→FY mapping.

| Joint model (1 km) | D file | D audit | work effect file | work effect audit |
|---|---|---|---|---|
| Businesses, H + W | +0.1975 [-0.9134, 1.3084] | +0.1975 [-0.9133, 1.3083] | +0.0501 [-0.420, 0.5203] | +0.0501 [-0.420, 0.5202] |
| Businesses, H + W_osm | +0.3678 [-1.1558, 1.8914] | +0.3678 [-1.1556, 1.8912] | -0.0298 | -0.0298 |
| Unemployment, H + W | -0.0559 [-0.1957, 0.0840] | -0.0559 [-0.1957, 0.0839] | -0.0355 | -0.0355 |
| Unemployment, H + W_osm | -0.0454 [-0.2789, 0.1881] | -0.0454 [-0.2789, 0.1880] | -0.0285 | -0.0285 |

  Rows match: 5,844 and 5,062. The last-digit CI differences come from a one-degree-of-freedom difference in the
  small-sample factor.
- **Signs and FY mapping.**
  - D uses `sgn = +1` (U) or `-1` (log outcomes) on workplace minus home, so positive = workplace more "worse".
  - PIA `fy` is the first year of "2017-18".
  - CABEE June y maps to FY y-1.
  - SALM Q3/Q4 map to that year's FY; Q1/Q2 map to the previous FY.
  - Fire FY is the start year if the month is 7 or later.

  All are consistent with each other.
- **Panel filters.** These match PRESPEC and Experiment 7 Day 9 / Day 5: SA2s in sa2_info; income needs
  pop ≥ 100, sum > 0 and earners > 0; businesses need value > 0. The PIA linking code is identical to Day 5 for
  earners and sum.
- **Low: missing fire years are coded as 0.** The fire outlines start 2015-01-01, so FY2014-15 is a half year. Any
  lag reaching FY ≤ 2013 is set to 0, which treats unobserved fires (e.g. the Oct 2013 Blue Mountains fires) as
  "no fire". This affects β2 for FY2015 rows and β1-β4 in the early years. Experiment 7 did the same. It is not
  disclosed in FINDINGS.

## 5. FINDINGS.md: numbers PASS, some wording ISSUES

- **Numbers.** Every number I checked traces to a results file, a log, or the bibliography:
  - The season-totals table: all 15 rows plus "1,839 in 2023-24" and "never exceeded 4.2".
  - The Part 1 table, the type-specificity CIs and all post-hoc values.
  - The Part 2 table: 12 single-model cells and 8 D cells.
  - The single-model bounds: 0.020 / -0.178 / -0.316 / -0.176.
  - SA2 counts (623 / 639) and exposed SA2-years (198 / 78 / 209).
  - Holm p = 1.0, and that all primary placebos include 0.
  - Row counts 50/54 and 52/65; 0.08 homes; the Day 8 explanation (checked against PRESPEC_DAY8: R0 = log share
    burned, Poisson rate, season left out).
- **Medium: an overclaim in a post-hoc headline.** Short answer 3 says "homes inside the fire was the best single
  guide to every kind of loss". "What this means" repeats it as "best single predictor of every kind of building
  loss". In fact:
  - homes_in has the highest point estimate among the exposures tried.
  - It beats area burned with a CI above 0 only for outbuildings (+0.12 [+0.04, +0.21]).
  - For homes (+0.07 [-0.02, +0.14], which is the pre-registered verdict "Not better than area burned") and for
    facilities (+0.08 [-0.03, +0.21]), it is not distinguishable from area burned.
  - It was picked post hoc from many candidates.

  Suggested wording: "had the highest rank correlation for every loss type, but was clearly better than area burned
  only for outbuildings".
- **Low: phrasing that reads like "no effect".** Short answer 3 says "none … ranked councils' losses better than
  plain area burned". This should read "none was clearly better than area burned (CIs in table)". The point
  estimates for homes and outbuildings are higher.
- **Low to medium: mixed sign conventions and "tight" bounds.**
  - In the Part 2 table, the "Homes alone" and "Workplaces alone" columns are raw changes (+ = increase), while
    "Workplace minus home" is "worse"-signed. For example, earners +0.16 means earners rose. Label the columns.
  - "The bounds are tight" applies only to the single-W models. The joint contrasts D that drive the verdict are
    wide (up to ±1.5% per 10 pp, i.e. ±15% for a whole SA2). Say so.
- **Low: "all CIs include 0" is not true of every inside model.** That sentence in the inside (secondary) bullet
  fails for the single P models:
  - E +0.97 [+0.33, +1.61]
  - I +1.02 [+0.30, +1.74]
  - B +0.64 [+0.05, +1.23]

  The B result has a passing placebo and goes in the "better" direction (more businesses), and it is not mentioned.
  Reword to "all workplace and home CIs include 0", and mention the B result as unexplained and reported only.
- **Low: overstated causal explanation.** "At SA2 scale that is too small to show up" gives a reason as if it were
  fact. Use "may be too small".
- **Low: the OSM counts are not NSW-only.** "274,224 mapped NSW areas … 63,169 tagged as houses" (FINDINGS Limits
  and PRESPEC) counts the NSW bounding box, which includes the ACT and border areas of Vic and Qld. Inside NSW the
  counts are 210,247 areas and 47,746 houses (2021 NSW MB dwellings: 3.36 M, so "about 3.4 million" is fine).
- **Low: Census vintage rule in `season_totals.py`.** It uses 2021 MBs for FY2020-21, but the council rule uses 2016
  for fires starting Jul-Dec 2020. Its docstring calls this the "affected_pop.py rule". This affects only the
  descriptive 2020-21 row.
- **Bibliography CSV: PASS.**
  - It parses (32 rows), the columns exactly match the README, there are no duplicate IDs, and every quote is
    25 words or fewer.
  - No news sources, so no ACM.
  - Every ABS, DEWR, PIA and LGA URL appears in project files (backfill / BIBLIOGRAPHY.csv / affected_pop.py /
    dl_council.py).
  - The Geofabrik URL is confirmed by the file's macOS `kMDItemWhereFroms` record (a `utm_source` tag was stripped,
    which is fine).

  Two low notes:
  - E16-14 and E16-31 are listed as FAILED in `bibliography/BROKEN_LINKS.csv` / `link_status.csv`. E16-31 already
    says it was read via Wayback; E16-14 should say "link check timed out 2026-10-02".
  - E16-24 to E16-27 (the NEXIS / data.gov.au / researchdata URLs) appear in no other project file. They come from
    this session's web search, so I cannot verify them from disk. Ray should click-check them.

## 6. Other reviewer concerns

- **Was 1 km as primary chosen without looking at outcomes? Yes, and it is disclosed.** PRESPEC gives an
  outcome-free reason: exposure distributions only (1 of 218 rows has ≥ 1 whole C/I MB inside; 4 SA2-years with
  W ≥ 10% inside). It cites the Experiment 7 Day 7 precedent, and it was saved before any outcome output. PRESPEC
  also discloses one small leak: damage values for Armidale, Ballina and Bega Valley were seen on screen before
  locking. That cannot plausibly have driven the zone choice.
- **Black Summer dominates every test.** 50 of 54 facility rows and 52 of 65 outbuilding rows are Black Summer, so
  Part 1 is in effect a comparison of councils within one season. This is disclosed.
- **"Fires seldom reach workplaces" depends on the measure.** It rests on MB land-use categories (shops in
  Residential MBs are missed) and incomplete OSM. Meanwhile the NBRA counts show 284 non-residential buildings
  destroyed in Black Summer rows. Phrase it as "fire outlines seldom overlap Commercial/Industrial mesh blocks"
  rather than about workplaces in general.

---

## Summary

| # | Check | Result | Severity |
|---|---|---|---|
| 1a | Lock hashes (9 files) + rerun identical | PASS | — |
| 1b | Scripts follow PRESPEC (zones, outcomes, lags, effect, placebo, Holm, verdicts, bootstrap) | PASS | — |
| 1c | Analysis scripts not hashed / no git anchor | ISSUE | low |
| 1d | Stale "inside (primary)" comment in locked build_exposure.py | ISSUE | low |
| 1e | Pre-specified r2_within comparison not reported | ISSUE | low |
| 2 | Exposure re-derivation (4 rows incl. Black Summer; 2016 + 2021 vintages), units, union, clipping, OSM priority | PASS | — |
| 2b | OSM landuse polygons and sheds counted as sites / "farm" | ISSUE | low |
| 3a | Damage check merges, columns, rho and bootstrap re-derived | PASS | — |
| 3b | AGRN 871/880 overlap (80% of 880 inside 871; 7 councils) not disclosed | ISSUE | medium |
| 4a | Joint contrasts re-derived with statsmodels dummies (4 models) | PASS | — |
| 4b | Lags into unobserved pre-2015 years set to 0, undisclosed | ISSUE | low |
| 5a | FINDINGS numbers trace to results | PASS | — |
| 5b | Post-hoc "homes inside best guide to every kind of loss" overclaims | ISSUE | medium |
| 5c | Mixed sign conventions; "bounds are tight" vs wide D | ISSUE | low-medium |
| 5d | "all CIs include 0" (inside) incorrect for P; B result omitted | ISSUE | low |
| 5e | "none ranked better" / "too small to show up" phrasing | ISSUE | low |
| 5f | OSM "NSW" counts are bounding-box counts | ISSUE | low |
| 5g | season_totals vintage for FY2020-21 differs from council rule | ISSUE | low |
| 5h | Bibliography format, no ACM, URLs traceable (except NEXIS web-search URLs) | PASS (2 low notes) | low |
| 6 | 1 km primary choice outcome-free and disclosed | PASS | — |

## Required fixes (FINDINGS.md only; no re-analysis needed)

1. **(medium)** Rewrite the post-hoc headline in Short answer 3 and "What this means". homes_in had the highest
   rank correlation for each loss type, but was clearly above area burned only for outbuildings
   (+0.12 [+0.04, +0.21]). For homes it was +0.07 [-0.02, +0.14] and for facilities +0.08 [-0.03, +0.21]. It was
   chosen post hoc.
2. **(medium)** Disclose the AGRN 871/880 overlap:
   - 9 shared fires; 80% of 880's outline lies inside 871's; 7 councils appear twice in 2019-20.
   - The outbuilding council totals for Kempsey and Richmond Valley overlap the 880 rows.
   - Optionally add a labelled post-hoc sensitivity that drops the 880 rows.
3. **(low-medium)** Fix the Part 2 table and the "tight bounds" sentence:
   - In the Part 2 table, label the single-model columns as raw change (+ = increase).
   - Say that "tight bounds" refers to the single-W models, and that the D CIs behind the verdict are wide.
4. **(low)** Correct "all CIs include 0" for the inside models, and mention the P-inside business result
   (+0.64 [+0.05, +1.23]) as reported only.
5. **(low)** Report the pre-specified R² (within) comparison of W-only vs H-only.
6. **(low)** Add to Limits:
   - Fires before 2015 are unobserved and coded as 0 in lags.
   - OSM counts are for the NSW bounding box (210,247 areas and 47,746 houses inside NSW).
   - OSM landuse polygons count as workplace "sites".
   - season_totals uses the 2021 Census for FY2020-21.
   - The stale comment in build_exposure.py.
7. **(low)** Change "none … ranked better than area burned" to "none was clearly better (CIs above)". Change "too
   small to show up" to "may be too small".
8. **(low)** Bibliography:
   - Add "link check timed out 2026-10-02" to E16-14.
   - Ray to click-check the NEXIS URLs (E16-24 to E16-27).
9. **(process, low)** For future experiments, hash or commit the analysis scripts with the lock.
