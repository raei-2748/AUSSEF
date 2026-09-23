# Stage 10 results: were the roads really closed, how long was the escape window, and what did isolation cost?

## A. Did traffic actually stop on roads the fire outline touched?

**RULE UNRELIABLE.** On 7 counter × fire cases where our rule says the road was
closed, traffic fell to 20% of normal or less on at least one day in 0% of cases
(95% interval 0%–35%). On 23 cases where a fire was within 500 m but did not touch
the road, it happened in 0% of cases.

| Closure rule | Traffic threshold | Rule says closed: traffic stopped | Road untouched: traffic stopped | Interpretation |
|---|---|---|---|---|
| outline touches road (S0) | ≤ 20% of normal | 0 / 7 = 0% [0%–35%] | 0 / 23 = 0% [0%–14%] | RULE UNRELIABLE |
| outline touches road (S0) | ≤ 50% of normal | 1 / 7 = 14% [3%–51%] | 1 / 23 = 4% [1%–21%] | (sensitivity) |
| ≥ 50% of segment inside outline | ≤ 20% of normal | 0 / 5 = 0% [0%–43%] | 0 / 25 = 0% [0%–13%] | (sensitivity) |
| ≥ 50% of segment inside outline | ≤ 50% of normal | 1 / 5 = 20% [4%–62%] | 1 / 25 = 4% [1%–20%] | (sensitivity) |
| within 100 m (S100) | ≤ 20% of normal | 0 / 17 = 0% [0%–18%] | 0 / 13 = 0% [0%–23%] | (sensitivity) |
| within 100 m (S100) | ≤ 50% of normal | 1 / 17 = 6% [1%–27%] | 1 / 13 = 8% [1%–33%] | (sensitivity) |

**In plain words.** We checked our "fire map touches road = road closed" rule against real traffic
counters. The table shows how often traffic really stopped when our rule said it would, and how often
it stopped anyway when the fire was nearby but didn't touch the road. With this few cases, the check
can only catch a badly wrong rule; it cannot measure accuracy precisely.

**What this means for the project.** On roads the fire outline touched, daily traffic usually kept
flowing: the lowest day was typically half or more of normal, and never close to zero. The
"outline touches road = road closed" rule therefore **overstates closure** at the level of whole days.
Every earlier stage built on that rule (stages 2–4 and 6–9) should be read as measuring **exposure of
roads to fire footprints**, not confirmed closures. Two limits remain: daily totals can hide closures
lasting only hours (an hourly check would be a new, separately pre-registered test), and there are
only 7 cases, mostly smaller historical fires.

Every case is listed below, so anyone can check it. Figure: `out/closure_validation.png`.

| Counter | Fire event | Fire start | Outline touches | Share inside | Lowest day vs normal | Lowest day | Valid days |
|---|---|---|---|---|---|---|---|
| 99990006 | DF_771fb41f1d1e3e74 | 2019-10-17 | yes | 100% | 25% | 2019-11-21 | 51 |
| 15334011 | HB_010210 | 2017-01-18 | yes | 37% | 53% | 2017-01-20 | 8 |
| 17126150 | HB_010210 | 2017-01-18 | yes | 3% | 57% | 2017-01-18 | 17 |
| 15334032 | DF_2e15e2238699ea88 | 2019-10-23 | yes | 100% | 61% | 2019-12-31 | 50 |
| 55860 | HB_010173 | 2016-12-13 | yes | 65% | 64% | 2016-12-25 | 13 |
| 15934014 | HB_010093 | 2016-11-04 | yes | 100% | 91% | 2016-11-05 | 15 |
| 56241 | HB_007759 | 2009-08-01 | yes | 100% | 95% | 2009-08-05 | 48 |
| 55856 | HB_009100 | 2013-10-13 | no | 0% | 40% | 2013-10-27 | 6 |
| 57101 | HB_008741 | 2012-12-05 | no | 0% | 57% | 2012-12-09 | 12 |
| 15252018 | DF_2e15e2238699ea88 | 2019-10-23 | no | 0% | 63% | 2019-12-25 | 102 |
| 57101 | HB_008457 | 2011-02-01 | no | 0% | 64% | 2011-02-13 | 6 |
| 56865 | HB_008457 | 2011-02-01 | no | 0% | 65% | 2011-02-13 | 7 |
| 56865 | HB_008741 | 2012-12-05 | no | 0% | 68% | 2012-12-09 | 14 |
| 57097 | HB_007538 | 2008-10-27 | no | 0% | 69% | 2008-11-02 | 13 |
| 57440 | HB_009320 | 2013-11-08 | no | 0% | 69% | 2013-11-17 | 11 |
| 15252019 | DF_2e15e2238699ea88 | 2019-10-23 | no | 0% | 70% | 2019-11-12 | 94 |
| 15934011 | DF_2e15e2238699ea88 | 2019-10-23 | no | 0% | 71% | 2019-12-25 | 109 |
| 15934010 | DF_2e15e2238699ea88 | 2019-10-23 | no | 0% | 72% | 2019-11-12 | 100 |
| 15252023 | DF_2e15e2238699ea88 | 2019-10-23 | no | 0% | 72% | 2019-11-12 | 93 |
| 57102 | HB_008457 | 2011-02-01 | no | 0% | 73% | 2011-02-13 | 6 |
| 57102 | HB_008741 | 2012-12-05 | no | 0% | 74% | 2012-12-09 | 14 |
| 15934015 | DF_2e15e2238699ea88 | 2019-10-23 | no | 0% | 76% | 2019-11-27 | 89 |
| 55724 | HB_007586 | 2009-01-04 | no | 0% | 77% | 2009-01-04 | 13 |
| 55883 | HB_008615 | 2012-09-24 | no | 0% | 82% | 2012-10-01 | 12 |
| 55863 | HB_010372 | 2017-09-03 | no | 0% | 84% | 2017-09-13 | 26 |
| 15828001 | HB_010390 | 2017-09-06 | no | 0% | 89% | 2017-09-10 | 14 |
| 58871 | HB_008689 | 2012-11-01 | no | 0% | 90% | 2012-11-06 | 9 |
| 56375 | HB_008556 | 2012-08-10 | no | 0% | 90% | 2012-08-09 | 8 |
| 58872 | HB_008573 | 2012-08-25 | no | 0% | 101% | 2012-08-28 | 9 |
| 56383 | HB_008556 | 2012-08-10 | no | 0% | 107% | 2012-08-12 | 12 |

All-vehicle volumes use the counter's published total where it exists, otherwise light + heavy
vehicles added together (many counters never publish a total; see DEVIATIONS.md V1).

Coverage: 742 counters with data, 531 matched to a road; 104 counter × fire pairs
within 500 m (2006–2020), of which 30 had enough valid days and a baseline.

## B. The escape window (from stage 4, restated)

Of 31 satellite-era full cut-offs, 29 could be dated on every exit near town.
The time between fire reaching the **first** and the **last** road out was:
median **22.2 hours** (middle half 3.3–120.8 h); within 6 h in 9, within 12 h in
11, within 24 h in 17. 2 could not be dated.

**In plain words.** Once fire reaches one road out of town, residents typically have about a day
before the others go too, and sometimes only a few hours. This is the evacuation window. People who
can't leave quickly (older residents, people needing help, people without cars, visitors) are the ones
this window matters most for. Figure: `out/escape_window.png`; list: `out/escape_window.csv`.

## C. Short-run disruption to movement of people and freight (Black Summer, pre-COVID)

Counters within 5 km of a Black Summer fire, weekly totals from 4 November 2019 to 23 February 2020,
compared with the same weeks in the three previous summers.

| Vehicles | Counters | Counters with ≥ 1 week below 80% | Counter-weeks below 80% | Median deepest week | Net missing trips |
|---|---|---|---|---|---|
| all vehicles | 42 | 12 | 24 of 322 | 83% | 1,486,340 (2.9% of normal) |
| heavy (freight) | 40 | 9 | 21 of 286 | 93% | -134,686 (-2.7% of normal) |

**In plain words.** This shows how much movement of people and goods on roads near the fires fell
below normal over the summer. It measures disrupted trips, not dollars, and not every drop is due to
closures (evacuation orders, tourists told to leave, and smoke all cut traffic). Per-counter detail:
`out/corridor_disruption.csv`.

## D. Is a council-finance model worth building? (pre-set go / no-go rule)

**NO-GO.**

- **road spending:** largest post-fire gap (cut off − burned only) -1.8 index points vs largest pre-fire gap 15.2; councils {'burned only': 23, 'cut off': 7, 'untouched': 73}; **NO-GO**.
- **total grants:** largest post-fire gap (cut off − burned only) missing index points vs largest pre-fire gap missing; councils {'burned only': 19, 'cut off': 5, 'untouched': 60}; **NOT EVALUABLE (data missing)**.

Figure: `out/fiscal_index.png`; data: `out/fiscal_index.csv`. The rule: GO only if councils with
cut-off towns jump more than burned-only councils after the fire, by more than the gap between the same
groups in the years before it.

## Caveats

- **Few validation cases.** Counters rarely sit exactly on the roads fires touched, so the intervals are wide.
- **Traffic stopping is not the same as an official closure.** Evacuation orders, tourist leave zones and smoke reduce traffic too, and a road can be closed without a counter on it.
- **Counters are fixed points.** A closure elsewhere on a road may not show at the counter.
- **Raw data.** Traffic counts come from the raw database layer (approved). Days with missing hours or directions are excluded, never treated as zero.
- **Pre-COVID only.** Parts A and C stop before March 2020 effects where relevant.
- Descriptive throughout: no causal claims, and no claims that anyone was trapped.

## Run

Run at 2026-09-23T12:49:35+00:00. Traffic raw layer: 4,193,981 rows, fingerprint `241b6cf4f2b406a393426bd09df674f14894f3b8b3748df49f79dfaacb7e0631`.
`aussef.duckdb` SHA-256 unchanged: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.
