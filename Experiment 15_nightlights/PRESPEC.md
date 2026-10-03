# Experiment 15 PRESPEC: night lights at the pixels inside and near fire outlines

Written 2 Oct 2026, before any radiance (`avg_rade9`) value was read. Up to now only these were opened: cloud-free
counts (`n_cf`), Census 2016 mesh blocks, fire outlines and the hotspot cache (`src/prep.py`, outcome-free). The
hash of this file is in LOCK.txt. Any later change or added check is labelled **post-hoc** in FINDINGS.md.
Fire light and smoke: see FIRE_LIGHT_CHECK.md (the monthly files are not fire-filtered; design below handles it).

## Question
After a fire, did lights from homes and businesses inside and near the outline drop, compared with similar unburned
places? When did they come back? This would be a proxy for people leaving (displacement) and rebuilding. It does
not rely on surveys taken in the COVID years.

## Data (all already in the project)
- 132 monthly VIIRS DNB composites, 2014-01 to 2025-06: `avg_rade9` (radiance, nW/cm²/sr) and `n_cf` (cloud-free
  looks). EOG VNL v1, stray light excluded, NSW window. Six months are missing from the source: 2014-03, 2017-10,
  2017-11, 2021-08, 2022-06, 2022-08. They are skipped, not filled. Read from OneDrive in place.
- Census 2016 mesh-block dwellings. Each mesh block is spread over the 15-arc-second pixels it covers (5×5
  sub-cells per pixel). Total kept: 3,062,931 of 3,063,152 dwellings.
- Fire outlines: `fire_event_dataset/data/cache/fires.parquet` (GA, 2015-01 onward). A missing end date is set to
  start + 60 days, for masking only.
- DEA hotspots: per-fire cache on OneDrive, all sensors.
- Homes destroyed per fire: `fire_event_dataset/data/enrich/house_loss.parquet` (29 fires with an official figure).

## Definitions
- **Settled pixel**: at least 5 Census-2016 dwellings. 31,662 pixels in NSW, holding 2,846,474 dwellings.
- **r(p,m)**: radiance of pixel p in month m. Values below 0 are set to 0.
- **Valid pixel-month**: the month exists, `n_cf` ≥ 2, no cached hotspot within 2 km that month, and no mapped
  outline within 2 km burning that month. Invalid pixel-months are dropped.
- **Fire group G**: one or more fires. Start month S is the earliest start. End month E is the latest end.
- **Treated rings** (distance from the pixel centre to the nearest outline in G): *inside* (0), *ring 0-1 km*
  (0 < d ≤ 1 km), *ring 1-5 km* (1 < d ≤ 5 km).
- **Re-burn censoring**: after E, a treated pixel is dropped from the first month in which a mapped fire not in G
  burns within 2 km.
- **Control pool**: settled pixels 15-150 km from G and not in Greater Sydney (by majority of dwellings). A pixel
  can be a control only if no mapped fire burns within 10 km of it from S−24 to E+12. If a fire later comes within
  10 km, it is dropped from that month on.
- **Baseline b(p,c)**: mean of valid r(p,m) over the months S−24..S−1 that fall in calendar month c. Fires that
  start before 2016-01 use what exists from 2014-01, with at least 12 months required. A pixel-month whose calendar
  month has no baseline value is dropped.
- **Brightness band**: the pixel's mean baseline, in bins [0,1), [1,3), [3,10), [10,30), ≥30 nW/cm²/sr.
- **Control change R(s,m)**: Σ r(q,m) / Σ b(q,c(m)) over the valid control pixels q in band s. If band s has fewer
  than 20 valid control pixels that month, the all-band ratio is used instead.
- **Expected light**: E(p,m) = b(p,c(m)) × R(s(p),m).
- **Light gap D**: ln(Σ r / Σ E), summed over valid treated pixels for one month, or over all months of a window.
  It is shown as a percent, 100(e^D − 1). Example: −20% means lights were 20% below what similar unburned places
  suggest.

## Windows (relative to the end month E)
- *During the fire*: S..E. Shown, but labelled "flames and smoke possible". Not used for any verdict.
- **Early**: E+1..E+6. **Year 1-2**: E+7..E+18. **Year 2-3**: E+19..E+30. **Later**: E+31..2025-06.
- **Placebo before the fire**: S−12..S−1, compared with a baseline from S−24..S−13 only.

## Fires
- **Main 1, Black Summer South Coast**: Currowan 2 (F_1e185c690e800a5cfe), Clyde Mountain (F_592a4d0267971025b2),
  Badja Forest Rd (F_a543db8a50cf524023) and Border Fire (F_948a8dcc8a9b94a266), the four South Coast fires with
  official home-loss figures. S = 2019-11, E = 2020-03.
- **Main 2, pre-COVID: Tathra / Reedy Swamp** (F_e69a83842cba888fd5), 18 Mar to 24 Apr 2018. S = 2018-03,
  E = 2018-04. The pre-COVID read runs to 2019-10. Later months are shown but labelled (Black Summer, COVID).
- **2013 Blue Mountains: not possible.** Imagery starts 2014-01, three months after that fire, so there is no
  "before". The fire is also not in the project's outlines, which start 2015-01. Stated as a limit, not attempted.
- **Pooled set (for the dose test)**: every mapped fire with at least 5 settled pixels inside, starting by 2024-06
  (22 fires). Each fire is its own group.
- **Council-wide comparison (dilution demo)**: all settled pixels in Shoalhaven, Eurobodalla and Bega Valley LGAs
  (2021 boundaries), with the Main 1 timing and controls. This shows what averaging over councils does.

## Inference
- Cluster bootstrap with 3 km × 3 km blocks (EPSG:3577). Treated blocks (all rings together) and control blocks
  are resampled separately, 1,000 draws. Percentile 95% CI.
- Robustness: random placebo groups. 1,000 times, draw control blocks with the same number of pixels as the
  inside group and treat them as "burned"; compute their Early D against the remaining controls. Report where the
  real D falls.

## Questions and pre-set reading rules
- **Q1** South Coast, inside, Early D. "Drop detected" if the 95% CI is entirely below 0.
- **Q2** Tathra, inside, Early D. Same rule. If the CI is wider than 0.30 in log units: "too few pixels to tell".
- **Q3** Recovery (only if Q1 or Q2 finds a drop): the first month k ≥ E+1 at which the 3-month centred mean of D
  is ≥ −0.05 and stays ≥ −0.05 for 6 months in a row. Also report D for each later window.
- **Q4** Gradient: Early D(inside) − Early D(ring 1-5 km), with bootstrap CI. Expected below 0 if the drop is caused
  by the fire.
- **Q5** Dose across fires (pooled set, inside, Early D for each fire):
  - V1: Spearman ρ between Early D and homes destroyed per 1,000 dwellings inside the outline, over fires with an
    official figure. 95% CI by bootstrapping fires. Expected ρ < 0.
  - V2: mean Early D in fires with an official figure ≥ 30 homes minus mean Early D in fires with no figure. 95% CI
    by bootstrapping fires. Expected < 0.
- **Q6** Dilution: council-wide Early D vs inside Early D.
- **C1 placebo** for each main group: D before the fire. The group's result counts as "reliable" only if
  |D_pre| ≤ 0.05 or its CI covers 0.

**Verdict on "lights as a measure":**
- (a) *Measures the shock* if Q1 detects a drop, C1 passes, and Q2 either detects a drop or is "too few pixels".
- (b) *Tracks home loss* if V1 or V2 has a CI entirely on the expected side.
- (c) *Shows rebuilding* if Q3 finds a recovery month.
Results are worded "not detected, CI [..]", never "no effect".

## Pre-set sensitivity checks
- S1: 5 km fire mask instead of 2 km.
- S2: `n_cf` ≥ 4.
- S3: controls 30-150 km away.
- S4: mean of per-pixel log ratios instead of ratio of sums.
- S5: 12-month baseline.

## Outputs
FINDINGS.md, plus figures in `figures/`:
- Curves of D by month (inside, 0-1 km, 1-5 km) with 95% bands, for both main fires.
- Pixel maps of the Early and Later light gap, with outlines.
- Pooled dose plot.

Independent audit by a fresh reviewer agent before reporting. Not done here because it would need a new download
(Ray decides): annual VNL v2 fire-filtered cross-check, full-NSW DEA hotspot download.
