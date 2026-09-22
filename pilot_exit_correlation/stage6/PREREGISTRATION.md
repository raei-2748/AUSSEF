# Pre-registration: stage 6, cut-off risk versus council fiscal capacity

**Date registered:** 2026-09-22. Written before any council-level exposure or fiscal comparison was
computed. The inputs were profiled for coverage and join keys only.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Question (public finance)
Are the NSW towns whose exit roads have been cut all together by bushfire located in councils with
**weaker finances**, meaning less capacity to pay for safer roads? This is a descriptive
"risk versus capacity" comparison. It makes no causal claim: it does not say fires caused weak
finances, or the reverse.

## Data
- **Towns and cut-offs:** stage-2 results (`../stage2/out/community_level.parquet`), rule S0, ring 20 km. These cover the 447 towns with ≥ 2 exits in the stage-2 analysis.
- **A town is "cut off at least once"** if it had ≥ 1 observed full cut-off in part A (2019–23) or part B (1950–2019).
- **Town → council:** each UCL 2021 polygon is assigned to the ABS LGA 2021 polygon it overlaps most by area. The LGA 2021 shapefile (`W/dataset_phase1/raw/lga_2021/`) is hash-verified against `analysis.supplementary_input_hashes`.
- **Council finances:** `aussef.duckdb` → `master.fiscal_panel_extended`, a cleaned, canonical layer opened read-only. Councils are matched to LGAs by exact normalised name: lower case, "(NSW)" removed, words "city", "council", "shire", "regional" and "municipal" removed. Unmatched LGAs are listed, never guessed.
- **Baseline year:** financial year 2018-19 (`year_start = 2018`), the last full year before the 2019-20 fires.

## Groups
- **Exposed councils:** councils containing ≥ 1 town cut off at least once.
- **Comparison (primary):** all other matched councils that contain ≥ 1 stage-2 town.
- **Comparison (secondary):** "fire-touched but never cut off" councils. These contain ≥ 1 town where a fire closed at least one exit (parts A or B), but no town that was ever fully cut off.

## Primary measure and decision
**Own-source revenue share** (`own_source_pct`, 2018-19). This is the share of council revenue raised
from rates, fees and charges rather than grants, a standard NSW Office of Local Government
fiscal-capacity indicator.

- Estimate: median(exposed) − median(comparison).
- 95% CI: bootstrap over councils, 2,000 resamples, seed 20260921, resampling within each group.
- Also reported: two-sided Mann–Whitney U p-value.
- **SUPPORTED** (a risk–capacity mismatch) if the difference is < 0 and the 95% CI excludes 0.
- **NOT SUPPORTED** otherwise.
- **NOT EVALUABLE** if fewer than 8 exposed councils have 2018-19 own-source data.

## Secondary measures (descriptive; Holm-adjusted p-values reported, no verdict)
- Cash cover in months (`cash_cover_months`)
- Operating ratio (`operating_ratio_pct`)
- Grant dependence (`grants_pct`)
- Maintenance funding ratio (`maintenance_ratio_pct`, actual ÷ required maintenance)
- Road km per 1,000 residents (`road_km` / `population`)

All are 2018-19 values, each compared the same way as the primary measure.

## Sensitivity (no verdict)
- A 2016-17 to 2018-19 three-year average baseline instead of 2018-19 alone.
- The secondary comparison group.
- A population-weighted exposure (share of council residents living in cut-off towns), compared by Spearman rank correlation with own-source share across all matched councils.

## Required caveats
- This is descriptive: council finances and fire exposure share causes (geography, remoteness, forest cover). A gap shows a mismatch; it does not show why it exists.
- The number of exposed councils is small (expected in the tens), so the intervals will be wide.
- Cut-offs are inferred from fire maps (stage-2 caveats apply): an upper bound, with no timing.
- Councils are compared at a fixed 2021 boundary. Councils amalgamated in 2016 appear as current councils.
- Only councils present in the fiscal panel (103 councils) can be compared.
