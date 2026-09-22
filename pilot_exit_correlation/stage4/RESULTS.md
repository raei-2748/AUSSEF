# Stage 4 results: timing near the town

## Verdict (pre-registered; a follow-up motivated by stage 3, not an independent test)

**PASS.** When each exit is dated by when fire reached it within about 5 km of the town,
11 of 31 satellite-era full cut-offs had fire reach every exit within 12 hours.
R_timed = 8.44 (95% CI 1.92 to 14.36) against 1.30 expected under independence.
PASS needed R_timed ≥ 2 and a lower bound > 1.

### In plain words

Stage 3 timed each road by the first fire detected anywhere along it, up to 20 km out, which could be
weeks before fire reached the town. Stage 4 times each road near the town, where people get trapped.
Measured this way, the typical gap between fire reaching the first and the last road out was
22.2 hours (29 of 31 cut-offs could be dated on every road). For comparison,
the whole-route gap in stage 3 was 54.9 hours.

This is a descriptive measurement. It is not a causal estimate and says nothing about lives saved.

## All results

| Timing rule | Timed cut-offs | Expected | R [95% CI] | Verdict |
|---|---|---|---|---|
| none (perimeter; stage-3 sample) | 31 | 1.30 | 23.80 [8.86, 38.01] | (comparison / sensitivity) |
| all exits reached within 12 h near town (K = 5 km) | 11 | 1.30 | 8.44 [1.92, 14.36] | PASS |
| all exits reached within 12 h near town (K = 2 km) | 12 | 1.30 | 9.21 [1.58, 15.46] | (comparison / sensitivity) |
| all exits reached within 12 h near town (K = 10 km) | 11 | 1.30 | 8.44 [1.64, 13.66] | (comparison / sensitivity) |
| all exits reached within 24 h near town (K = 5 km) | 17 | 1.30 | 13.05 [2.33, 21.25] | (comparison / sensitivity) |

The first row is the stage-3 perimeter sample, reproduced exactly as a built-in check.

## Each full cut-off

| Town | Event | Exits | Dated near town | First exit reached (UTC) | Hours first→last, near town | Hours, whole route (stage 3) |
|---|---|---|---|---|---|---|
| Medlow Bath (L) | HB_004614 | 2 | 2 | 2002-12-05 23:33 | 24.7 | 24.7 |
| Evans Head | HB_004523 | 2 | 2 | 2003-01-30 14:52 | 9.5 | 9.5 |
| Lake Tabourie (L) | HB_007759 | 2 | 2 | 2009-08-27 04:44 | 54.9 | 54.9 |
| Yerrinbool (L) | HB_009111 | 2 | 2 | 2013-10-17 03:50 | 431.8 | 431.8 |
| Nords Wharf (L) | HB_009122 | 3 | 3 | 2013-10-17 14:52 | 0.0 | 0.0 |
| Catherine Hill Bay (L) | HB_009122 | 2 | 2 | 2013-10-17 14:52 | 0.0 | 0.0 |
| Tingha (L) | HB_011036 | 4 | 4 | 2019-02-12 04:15 | 23.5 | 23.5 |
| Tallwoods Village (L) | DF_771fb41f1d1e3e74 | 2 | 2 | 2019-10-26 06:30 | 2.8 | 2.8 |
| Red Head (L) | DF_771fb41f1d1e3e74 | 2 | 2 | 2019-10-26 06:30 | 3.3 | 3.3 |
| Diamond Beach (L) | DF_771fb41f1d1e3e74 | 2 | 2 | 2019-10-26 06:30 | 3.3 | 3.3 |
| Hallidays Point - West (L) | DF_771fb41f1d1e3e74 | 2 | 2 | 2019-10-26 06:30 | 3.3 | 3.3 |
| Hallidays Point - Black Head | DF_771fb41f1d1e3e74 | 2 | 2 | 2019-10-26 06:30 | 3.3 | 3.3 |
| Nelligen (L) | DF_c65d27d344ed2b65 | 4 | 4 | 2019-11-26 03:10 | 828.9 | 828.9 |
| Batemans Bay | DF_c65d27d344ed2b65 | 5 | 5 | 2019-11-26 03:58 | 832.0 | 832.8 |
| Cobargo (L) | DF_c65d27d344ed2b65 | 4 | 4 | 2019-11-30 23:30 | 735.4 | 735.4 |
| Kioloa (L) | DF_c65d27d344ed2b65 | 2 | 2 | 2019-12-02 03:21 | 9.4 | 12.6 |
| Bawley Point (L) | DF_c65d27d344ed2b65 | 2 | 2 | 2019-12-02 08:40 | 22.2 | 27.5 |
| Lake Tabourie (L) | DF_c65d27d344ed2b65 | 2 | 2 | 2019-12-03 07:50 | 53.4 | 81.9 |
| Ulladulla | DF_c65d27d344ed2b65 | 3 | 3 | 2019-12-03 16:20 | 655.8 | 497.3 |
| Moruya | DF_c65d27d344ed2b65 | 4 | 4 | 2019-12-04 02:20 | 1,202.4 | 641.7 |
| Buxton (NSW) | DF_0e5c7670677aa724 | 3 | 3 | 2019-12-12 03:59 | 44.2 | 44.2 |
| Balmoral (L) | DF_0e5c7670677aa724 | 2 | 2 | 2019-12-14 00:10 | 120.8 | 165.0 |
| Milton | DF_c65d27d344ed2b65 | 3 | 3 | 2019-12-19 09:20 | 278.8 | 490.6 |
| Mogo (L) | DF_c65d27d344ed2b65 | 4 | 4 | 2019-12-30 15:56 | 1.9 | 830.7 |
| Malua Bay | DF_c65d27d344ed2b65 | 3 | 3 | 2019-12-30 16:04 | 22.8 | 851.7 |
| Batlow | DF_eb998975bfde99b9 | 3 | 3 | 2019-12-30 16:04 | 0.0 | 5.2 |
| Rosedale - Guerilla Bay (L) | DF_c65d27d344ed2b65 | 3 | 3 | 2019-12-30 17:30 | 21.4 | 850.9 |
| Sussex Inlet | DF_c65d27d344ed2b65 | 2 | 2 | 2019-12-31 02:10 | 12.7 | 70.0 |
| Berrara - Cudmirrah (L) | DF_c65d27d344ed2b65 | 2 | 2 | 2019-12-31 02:10 | 12.7 | 285.2 |
| Abernethy (L) | HB_004625 | 2 | 0 | undated | missing | missing |
| Thredbo Village (L) | HB_004979 | 2 | 0 | undated | missing | missing |

Figure: `out/timing_near_town_vs_route.png`.

## Caveats

- This test was designed after seeing the stage-3 per-town timing table, so treat it as supporting evidence, not independent confirmation.
- Hotspots have ±375 m to ±1 km location error and a few overpasses a day, and smoke or cloud can hide fire. A hotspot near a road does not prove the road was closed.
- Timing within about 5 km of town still measures when fire *arrived*, not how long roads stayed shut.
- Fires are not independent; the bootstrap resamples whole fire events. The 2019 road network is used throughout.

## Run

Seed 20260921, 1000 bootstrap resamples, runtime 157.8 s, run at 2026-09-22T02:10:06+00:00.
The stage-3 hotspot cache was hash-verified; no network requests were made.
`aussef.duckdb` SHA-256 was unchanged before and after: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.
