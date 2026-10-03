# Experiment 11 findings: the impact clock

2 Oct 2026. Rules locked first (PRESPEC.md, LOCK.txt). Script `run_clock.py`, figure `figures/fig1_impact_clock.png`.
No new downloads. 218 council x fire rows; fire size = homes inside the fire per 1,000 dwellings; each outcome is the
change from the council's own pre-fire level minus the same change in unburned councils.

## Primary tests (one horizon per channel, fixed in advance from the mechanism table; Holm across five)
| Channel | Horizon | rho [95% CI] | Holm p | Verdict |
|---|---|---|---|---|
| Council grants per resident (FP) | FY after the fire | +0.21 [+0.08, +0.35] | 0.015 | **Detected** |
| Council fire-related grants, audited statements (FP) | FY after the fire | +0.45 [+0.17, +0.64] | 0.015 | **Detected** |
| Tourism traffic fall (IL) | months 0-3 | -0.25 [-0.42, -0.04] as run; about -0.04 after the audit correction | 0.74 | not detected* |
| Rents (SL) | months 13-24 | +0.18 [+0.01, +0.36] | 0.74 | not detected |
| Domestic violence (SL) | months 13-24 | +0.03 [-0.08, +0.15] | 0.74 | not detected |

\* The bootstrap CI excludes 0 but the within-season permutation test does not pass: the traffic signal is mostly
a difference between fire seasons (Black Summer vs others), not between councils within a season.

## The clock (descriptive)
- **Council money grows for years.** Grants per resident: +0.08 (fire year), +0.21, +0.29, **+0.43 three years
  after**. Fire-related grant lines peak two years after (+0.53). A one-year window shows only part of it.
  Fire-related grants hold without Black Summer (+0.53 the year after). Grants per resident without Black Summer: +0.16 at FY+1 (CI includes 0) and +0.28 at FY+3; by season the positive link comes from fire years 2016-2019 (2022-2023 about -0.10). Audit: both primary results re-derived exactly; one row per council-year gives +0.27 (C4) and +0.52 (C5).
- **Capital spending** turns positive only 2-3 years after (+0.22, +0.33), small samples, not significant.
- **Tourism traffic: withdrawn.** The independent audit (Experiment 12/audit/AUDIT.md) found station-days with only one
  direction recorded (14.9% at two-direction stations), more common after bigger fires; corrected, H0 rho is about -0.04
  (p about 0.85). The later-horizon "reversal" is built in, because the H2/H3 baseline overlaps the post-fire years.
- **Rents** drift up with fire size to year 2, but without Black Summer the sign flips: it is Black Summer-specific
  and overlaps the COVID regional rent boom. **Domestic violence:** flat at every horizon.
- **Rebuilding:** the per-home curve (REBUILD_CURVE.csv) is dominated by normal housing growth in councils whose losses
  are small relative to their size, so its median (about 1 approval per home destroyed by 48 months) is NOT a rebuild
  rate. In the two councils with the largest losses (Eurobodalla 510 homes, Bega Valley 467), new house approvals in the
  five financial years after Black Summer were 346 and 135 BELOW the 2018-19 level (figures/fig4_rebuild_paths.png):
  no rebuilding surge is visible. Either rebuilds displaced other building or many homes were not rebuilt.

## What it means
Timing matters for the fiscal channel: the council cost of a fire builds over 3+ years, so same-year or one-year
measures understate it. Timing does not rescue domestic violence or rents. The pattern supports the transfer story:
homes are lost at once, councils absorb rising recovery money over years, and rebuilding does not show up as a surge in new house approvals in the hardest-hit councils.

## Limits
Fire-related grants and capital spending from audited statements cover 50-64 rows (fewer at later horizons). COVID
and the 2022 floods overlap Black Summer's later horizons. Rebuild measures are descriptive and trend-unadjusted (deviation 1: the rebuild curve was replaced in the report by annual approvals for the six hardest-hit councils, after seeing that the per-home curve tracks council growth).
