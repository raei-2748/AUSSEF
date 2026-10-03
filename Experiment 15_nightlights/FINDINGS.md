# Experiment 15: night lights inside and near fire outlines - FINDINGS

2 Oct 2026. Pre-registered in PRESPEC.md (LOCK.txt) and PRESPEC_AMENDMENT_1.md (LOCK_AMENDMENT_1.txt).
Source ids in brackets refer to rows in `bibliography/parts/exp15_nightlights_2026-10-02.csv`.
All results are computed from:
- the night-light files [E15-D01];
- Census 2016 homes [E15-D03];
- fire outlines [E15-D04];
- hotspots [E15-D02];
- official homes-destroyed figures [E15-D05];
- council boundaries [E15-D06].

Numbers come from `results/`. An independent audit was done before reporting: AUDIT.md [E15-P07]. Its fixes are
included here.

## 1. First, Ray's question: can the satellite tell fire light from house light?

**Not in our files.** Full answer with sources: FIRE_LIGHT_CHECK.md.
- Our monthly files are not filtered for fires. The provider says version 1 "has NOT been filtered to screen out
  lights from aurora, fires, boats, and other temporal lights" [E15-002].
- Only EOG's annual VNL V2 removes "most fires", using a 12-month median [E15-001].
- Smoke dims city light as seen by VIIRS [E15-003].

So the design:
- removes pixel-months near cached fire detections (2 km) [E15-D02] or near a burning outline (2 km);
- compares the same calendar months;
- compares with similar unburned places;
- reads results only after the fire was out.

Smoke that spread hundreds of kilometres is not removed by the mask. It only partly cancels through the comparison.

## 2. What was measured (plain version)

1. **Settled pixels.** These are night-light pixels (about 500 m) with at least 5 homes in the 2016 Census
   [E15-D03]. NSW has 31,662 of them, holding 2,846,474 homes.
2. **Expected light.** For each burned settled pixel, lights after the fire were compared with that pixel's own
   lights in the same calendar month during the 2 years before. This was then adjusted by how much similar unburned
   settled pixels changed: same brightness band, 15-150 km away, and no fire within 10 km.
3. **Result.** Light gap = actual / expected. −10% means 10% darker than expected.
4. **Uncertainty.** 95% intervals come from 1,000 "pseudo-towns": compact groups of real unburned pixels treated as
   if they had burned (Amendment 1). A gap is "detected" only if its interval excludes 0.

## 3. Black Summer South Coast (Currowan 2, Clyde Mountain, Badja Forest Rd, Border Fire)

The fire group burned from 2019-11 to 2020-03. Inside the outlines there are **105 settled pixels with 2,449 homes**
[E15-D03, E15-D04]. These four fires destroyed 312, 490, 399 and 111 homes [E15-D05]. The 1,429 comparison pixels
sit mostly in:
- Queanbeyan-Palerang (223);
- Shellharbour (214);
- Yass Valley (173);
- Snowy Monaro (160);
- Goulburn Mulwaree (153);
- Kiama (108).

That is inland towns plus the Illawarra fringe (`results/control_pool_lga.csv`, post-hoc count) [E15-D06].

| Lights vs expected | Inside the outline (105 px) | 0-1 km outside (286 px) | 1-5 km outside (602 px) * |
|---|---|---|---|
| Before the fire (placebo, 12 months) | −2.6% [−11.9%, +4.8%] | −1.4% [−5.4%, +7.3%] | +1.1% [−1.0%, +9.5%] |
| During (Nov 2019: 8 of 105 inside px usable; Mar 2020: 97) ** | −14.2% [−25.5%, −2.4%] | −9.7% [−17.6%, −4.6%] | −8.5% [−12.0%, −5.9%] |
| **First 6 months after (Apr-Sep 2020)** | **−9.0% [−20.4%, −1.7%]** | **−12.2% [−23.5%, −5.2%]** | −3.6% [−9.9%, +1.7%] |
| Months 7-18 (Oct 2020-Sep 2021) | −9.7% [−17.2%, −2.4%] | −9.7% [−15.7%, −1.4%] | +1.1% [−5.7%, +8.5%] |
| Months 19-30 | −9.6% [−20.7%, +0.3%] | −12.4% [−18.0%, +2.3%] | −3.5% [−11.7%, +7.7%] |
| Month 31 to Jun 2025 | −6.6% [−19.9%, +5.9%] | −10.9% [−26.3%, +1.2%] | +0.4% [−12.9%, +7.4%] |

\* The 1-5 km ring is 42% of the size of the comparison pool, so its pseudo-towns also pick up region-to-region
differences. Its intervals are flagged `ci_valid = False` in results/windows.csv.
\** The "During" interval understates uncertainty: pseudo-towns keep all their months while the burned pixels lose
most. It is not used for any verdict.

Figures: `figures/curves_south_coast.png` (month by month; the shaded 24 months before the fire are the baseline and
sit near 0 by construction) and `figures/map_south_coast.png` (pixel maps).

**What this says:**
- **A drop was detected inside the burned outlines and within 1 km of them.**
  - Inside: −9.0% in the first 6 months and −9.7% in months 7-18.
  - Within 1 km: −12.2% and −9.7%.
  - So it was **detected through month 18 (to Sep 2021)**.
  - In months 19-30 the estimates stay around −10% to −12%, but the intervals include 0, so a gap was not detected
    there.
- **Before the fire, a gap was not detected** (−2.6% [−11.9%, +4.8%]). This passes the pre-set placebo rule. But the
  interval is wide enough that a pre-fire decline as big as the effect (−9%) cannot be ruled out.
- **1-5 km away, a drop was not detected** (−3.6% [−9.9%, +1.7%]).
- **The pre-set gradient test was not detected either.** It asks whether the drop is bigger inside than 1-5 km away:
  −0.057 in log units [−0.204, +0.054]. So it is **not shown** that the drop belongs to the burned area rather than to
  a wider change. This matters for two reasons:
  - The first 6 months (Apr-Sep 2020) were also the first COVID months.
  - The burned area is coastal holiday country, while most comparison places are inland.
- **Recovery (pre-set rule: back within 5% of expected and staying there for 6 months).**
  - The rule is met only at **January 2025, the last month the rule can be checked** (the data end in 2025-06).
  - This depends on a single month. In Feb 2025 the gap jumped by +0.40 to +0.46 in log units in every ring, including
    the unburned 1-5 km ring, and by +0.39 in the council group (post-hoc, `results/posthoc_recovery_checks.txt`).
  - That looks like a shift on the comparison side or across the region, not rebuilding.
  - With Feb 2025 left out, no recovery month is found.
  - **So the timing of recovery is not shown.**
  - *Post-hoc:* the 19 brighter inside pixels (baseline ≥ 1 nW/cm²/sr) were still 14.8% below expected in the last
    window. The 86 dim ones were +1.0% (point estimates, no intervals).
- **Whole councils dilute the signal.** Over all settled pixels in Shoalhaven, Eurobodalla and Bega Valley (1,628 px),
  the first-6-months gap is −4.2% [−8.5%, +0.1%] (block bootstrap; this group is too big for pseudo-towns), not
  detected (`figures/dilution_south_coast.png`). That is about half the inside size. This fits the view that council
  averages are a weak measure. (Experiment 7 had a different problem: its council lights rose after heavy fires.)

## 4. Pre-COVID fire: Tathra / Reedy Swamp, March 2018

This fire destroyed 65 homes [E15-D05]. Inside the outline there are only **9 settled pixels with 452 homes**
[E15-D03, E15-D04]. The comparison pool is 397 pixels, mostly Snowy Monaro (235) and other parts of Bega Valley
(146) [E15-D06].

| Lights vs expected | Inside (9 px) | 0-1 km (18 px) | 1-5 km (40 px) |
|---|---|---|---|
| Before (placebo) | −2.3% [−11.1%, +12.6%] | +2.6% [−4.5%, +15.4%] | +1.2% [−6.3%, +9.4%] |
| First 6 months (May-Oct 2018) | −1.6% [−20.3%, +26.5%] | −0.6% [−18.0%, +19.1%] | −14.4% [−27.4%, +1.6%] |
| Months 7-18 (Nov 2018-Oct 2019, pre-COVID) | −9.0% [−24.2%, +11.5%] | −8.6% [−21.8%, +4.9%] | −13.7% [−25.8%, −1.3%] |
| Months 19-30 (Nov 2019-Oct 2020: Black Summer, COVID) | −6.8% [−28.6%, +18.1%] | +1.4% [−17.6%, +18.4%] | −14.7% [−29.8%, −3.2%] |
| Month 31 to Jun 2025 | +1.7% [−23.3%, +37.1%] | +28.0% [−1.8%, +60.5%] | −0.3% [−24.0%, +22.2%] |

- **Inside: too few pixels to tell** (pre-set rule: interval wider than 0.30 in log units). The first-6-months gap
  is −1.6%, interval [−20.3%, +26.5%]. A real 10-20% drop could hide in that.
- The 1-5 km ring shows detected drops in months 7-18 (−13.7%) and 19-30 (−14.7%). That ring was not a main question,
  and many ring × window cells were looked at, so treat it as a lead, not a finding. Months 19-30 also include Black
  Summer and COVID.
- Figures: `figures/curves_tathra.png`, `figures/map_tathra.png`.

**2013 Blue Mountains: not possible.** The imagery starts in January 2014, three months after that fire, so there is
no "before". The project's outlines also start in 2015 [E15-D01, E15-D04].

## 5. Does the drop grow with homes destroyed? (dose test, pooled)

There are 22 fires with at least 5 settled pixels inside. 10 of them have an official homes-destroyed figure
[E15-D05] (`figures/dose_pooled.png`).
- **V1:** Spearman between the first-6-months gap and homes destroyed per 1,000 homes inside the outline:
  **ρ = +0.36, 95% CI [−0.54, +0.85], 10 fires.** A link with home loss was not detected. The point estimate has the
  unexpected sign. Badja Forest Rd has the highest loss rate but only 6 settled pixels, and its lights look brighter.
- **V2:** fires with ≥ 30 homes destroyed (8) minus fires with no reported figure (12): **−0.040 in log units (about
  −4 percentage points), 95% CI [−0.103, +0.027].** Not detected.
  - Note: the pre-set V2 includes 4 "no figure" fires whose comparison pools are tiny (3 to 178 pixels). In those, the
    pseudo-town interval is unreliable (`ci_valid = False` in results/pooled_fires.csv).
- *Post-hoc, not pre-registered:* without those 4 fires, V2 = −0.068 [−0.131, −0.003]
  (`results/posthoc_v2_pool200.txt`). This is a hint only, because the cut was chosen after seeing the data.

## 6. Verdict against the pre-set rules

| Rule | Result |
|---|---|
| (a) Measures the shock: South Coast drop detected, placebo passes, Tathra detected or too small | **Met, but fragile.** −9.0% [−20.4%, −1.7%] under the Amendment-1 interval, fixed before any real data was read. Under the block bootstrap first locked in PRESPEC, the interval is [−16.0%, +0.7%] and covers 0. The 12-month baseline check touches 0, and the per-pixel average halves the drop. Placebo passes but is wide. Tathra: too few pixels. |
| Q4 gradient (inside minus 1-5 km) | **Not detected:** −0.057 [−0.204, +0.054]. It is not shown that the drop is specific to the burned area rather than a regional (e.g. COVID-season) change. |
| (b) Tracks home loss (V1 or V2) | **Not detected:** V1 ρ +0.36 [−0.54, +0.85]; V2 −0.040 [−0.103, +0.027]. |
| (c) Shows rebuilding (recovery month found) | **Met by the letter only:** January 2025, the last possible month, and it depends on one region-wide jump (Feb 2025). Not robust, so rebuilding timing is not shown. |

**Plain answer: does it work as a measure of displacement and rebuilding?**
- **Not yet.**
  - At the finest scale, lights in settled areas inside and within 1 km of the biggest fire cluster (South Coast) were
    about 9-12% below expected. That gap was detected through month 18.
  - That is a real lead, and it is clearer than the council averages, which halve it.
  - But the pre-set tests that would tie it to the fire itself were not detected:
    - the gradient against 1-5 km;
    - the link with homes destroyed.
  - The recovery date rests on one odd month.
- **Other causes of the dimming** cannot be separated from people leaving:
  - fewer holiday visitors;
  - broken or switched-off street lights;
  - dark burnt ground;
  - COVID-era changes that hit the coast differently from the inland comparison towns.

  Burnt trees could push lights the other way (FIRE_LIGHT_CHECK.md, item 5).
- **Honest wording for the report:** "Night lights from settled areas inside and right next to the Black Summer South
  Coast burns were about 9-12% below expected for 18 months. A link with the number of homes destroyed was not
  detected, and the method could not time the recovery." Not "X% of people left".

## 7. How solid is the South Coast drop? (pre-set checks)

| Check (inside, first 6 months) | South Coast | Tathra |
|---|---|---|
| Main | −9.0% [−20.4%, −1.7%] | −1.6% [−20.3%, +26.5%] |
| S1: 5 km fire mask | −9.0% [−20.2%, −2.4%] | −1.6% [−19.5%, +26.5%] |
| S2: ≥ 4 cloud-free looks | −9.0% [−20.1%, −1.8%] | −1.6% [−19.2%, +26.5%] |
| S3: controls 30-150 km | −10.3% [−20.9%, −3.7%] | −3.4% [−19.8%, +9.5%] |
| S5: 12-month baseline | −6.9% [−15.5%, +0.1%] | −1.6% [−21.5%, +15.3%] |
| S4: average of per-pixel log ratios (no interval pre-set) | −4.2% | −5.9% |
| Block bootstrap (first locked interval; Amendment 1 found it too narrow for small groups) | [−16.0%, +0.7%] | [−4.8%, +1.7%] |
| Random block groups (PRESPEC robustness): share of random groups below the real value | 2.0% | 72.3% |

- **S1 and S2 are weak checks here.** They change very few first-6-months pixel-months (the fires were out and skies
  clear). The estimates hardly move, but that says little.
- **S3** (farther controls) keeps the drop.
- **S5** (12-month baseline) touches 0. S5 also shrinks the window used to exclude controls to S−12..E+12, so it
  changes the control pool too.
- **S4:** the per-pixel average is smaller (−4.2%). *Post-hoc:* brighter pixels carry most of the drop. The 19 inside
  pixels with baseline ≥ 1 nW/cm²/sr were −11.6% in the first 6 months; the 86 dim ones were −6.8%.

## 8. Deviations, fixes and known quirks (all labelled)

1. **Amendment 1**, made before any real radiance was read: main intervals come from pseudo-towns, because a
   synthetic test showed the block bootstrap was far too narrow for Tathra. The synthetic evidence was re-run and
   saved in `results_synth/`:
   - `coverage_test_12_null_seeds.txt`: estimate spread 0.0164 vs pseudo-town spread 0.0167 (South Coast); 0.0450 vs
     0.0421 (Tathra); mean bias +0.002 / +0.014.
   - `planted_minus30pct_run.log`: planted −0.357 recovered as −0.357 [−0.402, −0.328].
2. **Bug fix:** a calendar month with no baseline (2017-11 is missing in the source [E15-D01]) turned the South Coast
   placebo into "not a number". Those months are now dropped on both sides. No main number changed.
3. **Bug fix:** S3 (30-150 km controls) did nothing at first, because distances beyond 15 km were not stored. It now
   uses the full distance. Main results are identical before and after; only the S3 row changed.
4. **Deviation (Q6):** the council group (1,628 px) is bigger than the control pool (1,305 px), so pseudo-towns cannot
   be made. Its interval is the block bootstrap.
5. **Interval validity:** `ci_valid` columns were added post-hoc to results/windows.csv and pooled_fires.csv. An
   interval is flagged when:
   - the group is more than 25% of the pool;
   - the pool is under 200 pixels;
   - the interval does not contain its own estimate; or
   - the window has no usable pixel-months.
6. **The analysis.py version hashed in LOCK_AMENDMENT_1.txt was not kept as a separate copy.** The current file
   includes the fixes in items 2-3, summary bookkeeping, and a NaN guard in the pixel maps. The definitions, windows
   and interval method were not changed. The independent audit re-derived all 30 main window estimates with its own
   code and matched them to 5 decimals (AUDIT.md).
7. **Recovery-rule quirks:**
   - "6 months in a row" counts available months, so missing months (2021-08, 2022-06, 2022-08) are skipped.
   - The smoothed value at E+1 averages in month E, a fire month.
8. **Post-hoc outputs** (not pre-registered) come from `src/posthoc.py`:
   - `results/posthoc_v2_pool200.txt`;
   - `results/control_pool_lga.csv`;
   - `results/posthoc_recovery_checks.txt`;
   - the `ci_valid` columns.

## 9. Limits

- **Hotspot gaps.** The hotspot cache only covers mapped fires' own boxes and dates [E15-P03]. Unmapped burns, and
  fires in 2014 (outlines start 2015), are not masked.
- **Missing months.** Six months are absent from the source [E15-D01].
- **Product changes.** The product changed in 2017-04, 2018-01 and 2024-10 (2024-10 is a different configuration,
  `ecmcfg`) [E15-P01, E15-P02]. Tathra's baseline crosses the first two, and the South Coast "later" window crosses
  the third. Comparing with controls cancels shifts common to both groups, not shifts that differ by place.
- **Homes data.** Census 2016 homes are used for every fire, including those years later.
- **Pixel size.** About 500 m pixels mean "inside" and "0-1 km" blur together.
- **COVID.** The South Coast's first post-fire months were also the first COVID months. Its comparison places are a
  different mix (inland towns and the Illawarra fringe), so COVID can only partly cancel.
- **Tathra's comparison pool** is narrow: Snowy Monaro and other parts of Bega Valley.

## 10. Decisions for Ray (nothing downloaded)

1. **Annual VNL V2 cross-check (fire-filtered)** [E15-001]. EOG's annual "average-masked" files, 2017-2022.
   - Source: https://eogdata.mines.edu/products/vnl/ (EOG login needed), or Google Earth Engine.
   - Size: not shown without logging in; I would report it before downloading.
   - Use: check the yearly South Coast dimming after EOG's own fire removal.
2. **Full-NSW DEA hotspots, 2014-2025** (https://hotspots.dea.ga.gov.au/geoserver/wfs).
   - Use: close the masking gap for unmapped burns.
   - Size: unknown. A count-only query timed out [E15-010].
3. **A finer dose test inside the South Coast** using NSW fire severity maps (FESM 2019-20, already on OneDrive
   [E15-D07]): high/extreme vs low severity settled pixels. No new download, but it needs a new pre-spec. This is the
   most direct way to test whether the drop follows the damage.

## Files

- `FIRE_LIGHT_CHECK.md`: the fire-light question, with sources.
- `PRESPEC.md`, `LOCK.txt`, `PRESPEC_AMENDMENT_1.md`, `LOCK_AMENDMENT_1.txt`: the pre-registration and locks.
- `AUDIT.md`: the independent audit and responses.
- `src/prep.py`: outcome-free setup.
- `src/analysis.py`: main analysis (`SYNTH=1` runs the synthetic test).
- `src/synth_coverage_test.py`: the Amendment-1 evidence.
- `src/posthoc.py`: post-hoc checks.
- `src/figures.py`: the figures.
- `src/bib.py`: bibliography logging.
- `results/`: windows.csv, monthly_*.csv, pixels_*.csv, pooled_fires.csv, sensitivity.csv, summary.json, plus the
  post-hoc files.
- `results_synth/`: synthetic test outputs.
- `figures/`: 6 PNG figures.
- `work/`: cached intermediates (rad.npy holds the radiance at settled pixels only).
- `sources/`: saved documentation pages and PDFs.
