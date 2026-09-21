# Stage 3 results: stricter checks

## Verdicts (pre-registered)

- **3a · A · S0 outside town · none (perimeter): FAIL.** R = 6.65 (95% CI 0.67 to 8.74); 22 full cut-offs observed vs 3.31 expected.
- **3a · B · S0 outside town · none (perimeter): PASS.** R = 13.79 (95% CI 3.07 to 29.27); 20 full cut-offs observed vs 1.45 expected.
- **3b · satellite era (2002-09 to 2023) · S0 · all exits hit within 12 h (hotspot ≤ 1000 m): FAIL.** R = 6.91 (95% CI 0.00 to 12.38); 9 full cut-offs observed vs 1.30 expected.

### In plain words

- **3a (outside-the-town check):** a road only counts as cut if it burns *outside* the town. This removes cases where the fire map simply surrounds the town.
- **3b (timing check):** a cut-off only counts if satellites show fire reaching *every* road out within 12 hours. Cut-offs that satellites could not date count as "not at the same time", so this check is deliberately strict.

The true effect likely lies between the stage-2 figure (upper bound, no timing) and the 3b timed
figure (conservative).

This is a descriptive measurement. It is not a causal estimate and says nothing about lives saved.

## All results

| Check | Sample | Closure | Timing | Observed | Expected | R [95% CI] | Verdict |
|---|---|---|---|---|---|---|---|
| 3a | A | S0 (stage-2 rule) | none (perimeter) | 22 | 3.31 | 6.65 [0.85, 9.07] | (comparison / sensitivity) |
| 3a | A | S0 outside town | none (perimeter) | 22 | 3.31 | 6.65 [0.67, 8.74] | FAIL |
| 3a | B | S0 (stage-2 rule) | none (perimeter) | 24 | 1.61 | 14.91 [4.41, 30.14] | (comparison / sensitivity) |
| 3a | B | S0 outside town | none (perimeter) | 20 | 1.45 | 13.79 [3.07, 29.27] | PASS |
| 3b | satellite era (2002-09 to 2023) | S0 | none (perimeter) | 31 | 1.30 | 23.80 [7.61, 37.86] | (comparison / sensitivity) |
| 3b | satellite era (2002-09 to 2023) | S0 | all exits hit within 12 h (hotspot ≤ 1000 m) | 9 | 1.30 | 6.91 [0.00, 12.38] | FAIL |
| 3b | satellite era (2002-09 to 2023) | S0 | all exits hit within 6 h (hotspot ≤ 1000 m) | 8 | 1.30 | 6.14 [0.00, 11.88] | (comparison / sensitivity) |
| 3b | satellite era (2002-09 to 2023) | S0 | all exits hit within 24 h (hotspot ≤ 1000 m) | 11 | 1.30 | 8.44 [2.17, 14.81] | (comparison / sensitivity) |
| 3b | satellite era (2002-09 to 2023) | S0 | all exits hit within 12 h (hotspot ≤ 500 m) | 8 | 1.30 | 6.14 [0.86, 10.41] | (comparison / sensitivity) |
| 3b | satellite era (2002-09 to 2023) | S0 | all exits hit within 6 h (hotspot ≤ 500 m) | 8 | 1.30 | 6.14 [0.00, 10.59] | (comparison / sensitivity) |
| 3b | satellite era (2002-09 to 2023) | S0 | all exits hit within 24 h (hotspot ≤ 500 m) | 10 | 1.30 | 7.68 [1.58, 12.50] | (comparison / sensitivity) |
| 3b | satellite era (2002-09 to 2023) | S0 outside town | all exits hit within 12 h (hotspot ≤ 1000 m) | 7 | 1.24 | 5.65 [0.00, 10.97] | (comparison / sensitivity) |

Rows marked "(comparison / sensitivity)" carry no verdict. The 3a rows with the stage-2 rule reproduce
stage 2 exactly (a built-in check).

## Timing of each full cut-off (satellite era, S0)

Of 31 perimeter full cut-offs in the satellite era, 29 could be dated on every exit (hotspot within 1 km). Among those, the median time between the first and last exit being reached was 54.9 h; 9 were within 12 h, 11 within 24 h.

| Town | Fire event | Part | Exits | Exits dated | First exit hit (UTC) | Hours first→last exit |
|---|---|---|---|---|---|---|
| Medlow Bath (L) | HB_004614 | B | 2 | 2 | 2002-12-05 23:33 | 24.7 |
| Evans Head | HB_004523 | B | 2 | 2 | 2003-01-30 14:52 | 9.5 |
| Thredbo Village (L) | HB_004979 | B | 2 | 1 | 2003-02-04 04:11 | missing |
| Lake Tabourie (L) | HB_007759 | B | 2 | 2 | 2009-08-27 04:44 | 54.9 |
| Yerrinbool (L) | HB_009111 | B | 2 | 2 | 2013-10-17 03:50 | 431.8 |
| Nords Wharf (L) | HB_009122 | B | 3 | 3 | 2013-10-17 14:52 | 0.0 |
| Catherine Hill Bay (L) | HB_009122 | B | 2 | 2 | 2013-10-17 14:52 | 0.0 |
| Tingha (L) | HB_011036 | B | 4 | 4 | 2019-02-12 04:15 | 23.5 |
| Tallwoods Village (L) | DF_771fb41f1d1e3e74 | A | 2 | 2 | 2019-10-26 06:30 | 2.8 |
| Red Head (L) | DF_771fb41f1d1e3e74 | A | 2 | 2 | 2019-10-26 06:30 | 3.3 |
| Diamond Beach (L) | DF_771fb41f1d1e3e74 | A | 2 | 2 | 2019-10-26 06:30 | 3.3 |
| Hallidays Point - West (L) | DF_771fb41f1d1e3e74 | A | 2 | 2 | 2019-10-26 06:30 | 3.3 |
| Hallidays Point - Black Head | DF_771fb41f1d1e3e74 | A | 2 | 2 | 2019-10-26 06:30 | 3.3 |
| Batemans Bay | DF_c65d27d344ed2b65 | A | 5 | 5 | 2019-11-26 03:10 | 832.8 |
| Nelligen (L) | DF_c65d27d344ed2b65 | A | 4 | 4 | 2019-11-26 03:10 | 828.9 |
| Mogo (L) | DF_c65d27d344ed2b65 | A | 4 | 4 | 2019-11-26 03:10 | 830.7 |
| Malua Bay | DF_c65d27d344ed2b65 | A | 3 | 3 | 2019-11-26 03:10 | 851.7 |
| Rosedale - Guerilla Bay (L) | DF_c65d27d344ed2b65 | A | 3 | 3 | 2019-11-26 03:58 | 850.9 |
| Cobargo (L) | DF_c65d27d344ed2b65 | A | 4 | 4 | 2019-11-30 23:30 | 735.4 |
| Kioloa (L) | DF_c65d27d344ed2b65 | A | 2 | 2 | 2019-12-02 00:10 | 12.6 |
| Bawley Point (L) | DF_c65d27d344ed2b65 | A | 2 | 2 | 2019-12-02 03:21 | 27.5 |
| Lake Tabourie (L) | DF_c65d27d344ed2b65 | A | 2 | 2 | 2019-12-02 03:21 | 81.9 |
| Ulladulla | DF_c65d27d344ed2b65 | A | 3 | 3 | 2019-12-02 09:10 | 497.3 |
| Milton | DF_c65d27d344ed2b65 | A | 3 | 3 | 2019-12-02 15:52 | 490.6 |
| Moruya | DF_c65d27d344ed2b65 | A | 4 | 4 | 2019-12-04 02:20 | 641.7 |
| Balmoral (L) | DF_0e5c7670677aa724 | A | 2 | 2 | 2019-12-12 03:59 | 165.0 |
| Buxton (NSW) | DF_0e5c7670677aa724 | A | 3 | 3 | 2019-12-12 03:59 | 44.2 |
| Berrara - Cudmirrah (L) | DF_c65d27d344ed2b65 | A | 2 | 2 | 2019-12-19 04:50 | 285.2 |
| Sussex Inlet | DF_c65d27d344ed2b65 | A | 2 | 2 | 2019-12-28 03:58 | 70.0 |
| Batlow | DF_eb998975bfde99b9 | A | 3 | 3 | 2019-12-30 10:50 | 5.2 |
| Abernethy (L) | HB_004625 | B | 2 | 0 | undated | missing |

## Figures

- `out/stage3_ratio_forest.png`: every ratio with its 95% interval.
- `out/cutoff_timing_hist.png`: hours between the first and last exit being reached.

## Important limit of the timing check

The timing rule compares when fire **first reached** each exit route. Each route is stored all the
way out to the 20 km ring, so its "hit time" is the earliest hotspot anywhere along it, which can be
far from the town. A road first reached on day 1 may still be closed, or may have reopened, weeks
later. The check therefore tests "fire first arrived at every exit within W hours". That is stricter
than "every exit was closed at the same moment", which would need closure durations (how long each
road stayed shut). No such data exist in this project. Some long gaps in the table, such as about 35
days for Batemans Bay in the 2019–20 Currowan fire, reflect this: fire reached one exit route early,
far from town, and another much later.

## Required caveats

- Hotspots are satellite detections: ±375 m to ±1 km location error, a few overpasses a day, and gaps under smoke and cloud. A hotspot near a road does not prove the road was impassable, and a missing hotspot does not prove it was open.
- Closure is inferred from fire maps and satellite detections, not from recorded road closures.
- Fires are not independent replications. The bootstrap resamples whole fire events.
- The 2019 road network is used for all fires.
- Satellite timing is only possible for fires from September 2002 onwards.

## Run

Seed 20260921, 1000 bootstrap resamples, runtime 164.9 s, run at 2026-09-21T22:35:09+00:00.
Hotspots: 12 fire events, 590,786 detections (DEA Hotspots; manifest in `out/hotspot_manifest.csv`).
`aussef.duckdb` SHA-256 was unchanged before and after: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.
