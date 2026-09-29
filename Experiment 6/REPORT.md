# Experiment 6: pre-fire council risk score, tested against the real fires

Bowen's change of angle: score every NSW council **before** any fire, using only pre-fire X plus the new
NSW Bush Fire Prone Land (BFPL) layer, then test the score against the DL/IL/FP/SL impact (Y) of the 96 real fires.
No Y is used to build the score. Y, the indicators and the master sheet are unchanged.

## Findings log (2026-09-29)

A pre-fire council score built from BFPL, forest, exposure, vulnerability and council-finance inputs finds which councils later get a big fire (AUC about 0.95); this is the well-studied part and works as a sanity check. On the under-studied impact side, council vulnerability (SEIFA, income, unemployment) is associated with heavier impact (Spearman +0.25 on all rows, +0.58 on fires burning 5% or more of a council; intervals exclude zero), while pre-fire council finances show no link to impact or to FP. The power check shows the fiscal null is informative on all 218 rows (94% power at rho 0.3) but not on the large fires alone (18%), so it cannot yet be read as "finances don't matter". None of this is proven: the large-fire evidence is mostly Black Summer, many tests were run, and the hazard + vulnerability structure was chosen after seeing the results, so it needs more real large fires (other years or states) as a fresh test.

## What was built

| Block | Inputs (all 129 NSW LGAs, 2014 snapshot; 2015/16 if 2014 missing) | Direction |
|---|---|---|
| **H** hazard | BFPL share Cat 1, BFPL share Cat 1+2, NVIS forest/woodland share | more = worse |
| **E** exposure | log population, log people inside BFPL Cat 1-2 (population x BFPL share; assumes even density) | more = worse |
| **V** vulnerability | SEIFA IRSD, median income, unemployment rate | poorer = worse |
| **F** fiscal | cash cover, own-source %, debt-service ratio, operating ratio, infrastructure backlog, unrestricted current ratio | weaker = worse |

Each item is a 0-1 percentile rank across NSW councils. A block is the mean of its items. The **pre-specified score**
`risk_add` is the equal-weight mean of H, E, V, F (`risk_mult` = H x E x mean(V, F), rank-scaled, is the multiplicative version).
Output: `results/COUNCIL_RISK_SCORE.csv` (all 129 councils), `results/risk_map.png`.

**BFPL data:** NSW RFS/DPHI *NSW Bush Fire Prone Land* (CC-BY), official ePlanning service layer 229, 235,537 polygons,
118 pages, 214 MB, generalised to about 30 m (`fetch_bfpl.py`; cached in `fire_event_dataset/data/bfpl/`).

**BFPL choice that matters:** Category 3 (grassland) covers 480,000 km2 of the west. "Any BFPL" is about 100% of most rural councils
and does not separate them, so the hazard block uses Cat 1 and Cat 1+2 only. "Any BFPL" alone scores AUC 0.72; Cat 1 alone scores 0.95
(table below).

## Result 1 (strong): the score finds the councils that get hit

AUC for "this council later had a fire burning at least X% of it" (129 councils, 34 positives at 5%):

| Score | >=2% (45) | >=5% (34) | >=10% (27) | >=20% (23) |
|---|---:|---:|---:|---:|
| **H hazard block** | 0.944 | 0.953 | 0.969 | 0.959 |
| BFPL Cat 1 share alone | 0.939 | 0.953 | 0.966 | 0.953 |
| NVIS forest share alone | 0.912 | 0.923 | 0.958 | 0.953 |
| BFPL "any" (incl. grassland) | 0.730 | 0.716 | 0.715 | 0.700 |
| Pre-specified `risk_add` | 0.903 | 0.910 | 0.911 | 0.920 |
| E / V / F alone | 0.65-0.70 | 0.63-0.72 | 0.64-0.70 | 0.67-0.71 |

The hazard block does the work. BFPL Cat 1 is a little better than forest share alone at 2% and 5% (0.939 vs 0.912; 0.953 vs 0.923),
but the two are highly correlated (Spearman 0.84), so **BFPL adds only a small increment** over vegetation data we already had. In the
full score BFPL makes no visible difference (0.910 vs 0.904 without it).

## Result 2 (mixed): does a higher score mean heavier damage once a fire hits?

Spearman(score, Y), council-cluster bootstrap 95% CI. All 218 council x fire rows, and only fires burning >=5% of the council (38 rows, 8 fires):

| Score | Y, all rows | Y, >=5% fires | DL (>=5%) | IL | FP | SL |
|---|---|---|---|---|---|---|
| Pre-specified `risk_add` | -0.07 [-0.25, +0.11] | +0.34 [+0.00, +0.62] | +0.22 | +0.27 | -0.20 | +0.32 |
| H (hazard) | -0.07 | +0.14 | +0.17 | +0.02 | +0.11 | -0.01 |
| E (exposure) | **-0.33** [-0.50, -0.16] | -0.33 | -0.31 | -0.20 | -0.07 | -0.31 |
| **V (vulnerability)** | +0.25 [+0.06, +0.43] | **+0.58** [+0.30, +0.76] | +0.39 | +0.44 | -0.27 | +0.60 |
| F (fiscal) | +0.03 | +0.00 | -0.14 | +0.29 | -0.07 | -0.02 |

- **Vulnerability (SEIFA, income, unemployment) is the block that tracks impact.** At council level (69 councils with a fire) V vs the council's
  worst fire: rho +0.52 [+0.31, +0.68].
- **Exposure points the wrong way**: bigger councils (more people in BFPL) get *lower* Y. Y is relative (homes destroyed per 1,000 dwellings,
  % income change, rank-based), so a large economy absorbs the same fire better. E is a count, not a rate.
- **Hazard predicts DL** (homes destroyed, all rows rho +0.37 [+0.14, +0.58]) but not IL/SL/FP.
- **Fiscal stress before the fire (F) does not predict FP, or Y overall.** Only a weak hint for IL at >=5% (+0.29, CI crosses 0). This is the
  gap Bowen wanted to fill, so it needs a plain statement: with these fiscal indicators the pre-fire signal is not there.
- The equal-weight `risk_add` is diluted by E's negative sign and F's nothing, so overall it is about zero (-0.07) and only moderate on large fires.

## Exploratory (not pre-specified): hazard + vulnerability

After seeing the block results, `risk_HV_mean` = mean(H, V), a likelihood + consequence structure, was tested. **This choice was made after looking at Y,
so treat the numbers as a hypothesis for Bowen, not a confirmed result.** Two H+V variants were tried (mean and product, both in `VALIDATION_ROW_LEVEL.csv`); they behave the same.

| `risk_HV_mean` | Y | DL | IL | FP | SL |
|---|---|---|---|---|---|
| all rows | +0.13 [-0.06, +0.32] | +0.48 [+0.26, +0.65] | +0.13 | -0.07 | +0.02 |
| >=2% burned (62 rows) | +0.42 [+0.19, +0.63] | +0.46 | +0.38 | -0.09 | +0.27 |
| >=5% burned (38 rows) | **+0.59** [+0.31, +0.77] | +0.46 | +0.41 | -0.21 | +0.55 |
| Black Summer only (50 rows) | +0.62 [+0.41, +0.77] | +0.60 | +0.15 | -0.18 | +0.41 |
| excluding Black Summer (168 rows) | +0.03 [-0.20, +0.28] | +0.56 [+0.23, +0.77] | +0.13 | -0.02 | -0.09 |

Council-level, `risk_HV_mean` vs the council's worst-fire Y: +0.40 [+0.17, +0.59].

## Bowen's question: can "large fire" be redefined?

Yes, and it helps. Only Black Summer has a council share >=20%. Definitions by physical size (not by Y, so no circularity):

| Definition | Rows | Fires | Councils | Years | Black Summer rows |
|---|---:|---:|---:|---|---:|
| share burned >= 20% (old) | 23 | 1 | 23 | 2019 | 23 |
| share burned >= 10% | 28 | 2 | 27 | 2019, 2023 | 27 |
| **share burned >= 5%** | 38 | 8 | 34 | 2016, 2018, 2019, 2023 | 30 |
| share burned >= 2% | 62 | 19 | 45 | 2016-2019, 2023 | 39 |
| burned >= 5,000 ha in council | 84 | 32 | 44 | 2015-19, 2023, 2025 | 39 |
| burned >= 1,000 ha in council | 151 | 71 | 58 | 2015-19, 2023-25 | 45 |
| Y class Severe/Extreme (circular) | 63 | 29 | 40 | 2016-19, 2023-25 | 27 |

Going from 20% to 5% takes large fires from 1 to 8 (and to 19 at 2%). The catch: **Black Summer is still 30 of the 38 rows at 5%**,
so the >=5% tests remain mostly a Black Summer result. The 2% and 5,000 ha cuts spread it more (39 of 62 and 39 of 84). Full grid
of every score x definition x pillar: `results/VALIDATION_ROW_LEVEL.csv`.

## Power check: could our data have found an effect if it existed?

`power_check.py` -> `results/POWER_CHECK.csv`. X is the real X (the same 218 council x fire rows and real block scores). Y is fake: real Y
shuffled within Black Summer and within each year (keeps its spread and clustering, breaks any link to X), then a known effect
(correlation rho) is planted on the fiscal block F or the vulnerability block V. The same test as the real analysis is applied
(Spearman, council-cluster bootstrap, "detected" = interval above 0). 300 simulations per cell, 200 bootstrap draws each.

Percent of simulations in which the planted effect was detected:

| Planted on | Rows tested | rho 0 (false alarm) | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
|---|---|---:|---:|---:|---:|---:|---:|
| F fiscal | all rows (218) | 0 | 11 | 52 | 94 | 100 | 100 |
| F fiscal | fires >= 5% burned (38) | 1 | 5 | 10 | 18 | 33 | 60 |
| V vulnerability | all rows (218) | 0 | 15 | 72 | 99 | 100 | 100 |
| V vulnerability | fires >= 5% burned (38) | 7 | 15 | 46 | 78 | 93 | 100 |

What this says:
- **On all 218 rows the fiscal null is informative.** The real F-vs-Y correlation was +0.03 [-0.17, +0.21]. With about 94% power at rho 0.3, an effect that large would have been caught. Effects of about 0.1-0.2 could still hide (11-52% power).
- **On the >=5% fires the fiscal null is not informative.** Power is only 18% at rho 0.3 and 60% at 0.5, so "no fiscal signal" among large fires cannot separate "no effect" from "too few fires".
- **The vulnerability result on >=5% fires is testable:** 78% power at rho 0.3, 93% at 0.4. A real effect of that size would usually be seen, which supports taking the +0.58 seriously. It does not remove the Black Summer and forking-path caveats.
- **Excluding Black Summer cannot be tested.** Only 8 rows. Even with nothing planted, V is "detected" 13% of the time (mean estimated rho +0.36), because the Y shuffle keeps year-level differences that line up with V. Power for that subset is not reported as meaningful.
- The planted rho is a correlation across all rows, so the subset numbers show what a fixed underlying effect looks like when tested on fewer rows. False alarms at rho 0 are 0-1% (F) and 0-7% (V), close to the expected 2.5% for a one-sided rule, except the 7% at V and >=5%.

Limits: the fake Y keeps real Y's spread and clustering but not council persistence over time; the bootstrap clusters by council, not by fire (same as the real analysis).

## Limits to keep in view

1. **Black Summer drives the severity signal.** Excluding it, `risk_add` on Y is -0.19 [-0.39, +0.02] and the exploratory H+V is +0.03; only DL (+0.56) survives.
2. The H+V structure was chosen after looking at results (see above). The forking-path risk is real with 96 fires.
3. BFPL is the current mapping (post-2019 updates), not a 2014 snapshot. It is a vegetation and slope hazard map, not a fire outcome, but councils remap over time.
4. "People inside BFPL" assumes uniform density inside each council, which overstates it for councils with bush and town separated.
5. No fire-weather (FFDI climatology) and no council-wide slope in the score yet: BFPL already builds vegetation and slope in, but the weather leg Bowen listed is missing. Source would be a pre-2015 ERA5 climatology per council.
6. Rows within one fire share the same weather and burn, and Y is a within-sample rank composite. CIs cluster by council but not by fire.
7. Y has DL for only 90 of 218 rows.

## Files

`fetch_bfpl.py` (download) -> `build_council_hazard.py` (BFPL, forest shares per council; `results/COUNCIL_HAZARD.csv`) ->
`build_and_validate_score.py` (score and every table in `results/`) -> `make_figures.py` (`risk_map.png`, `score_vs_Y.png`).
Seeds fixed (`SEED = 20260929`, 2,000 bootstrap draws).
