# Pre-registration: stage 7, who lives in towns that get fully cut off, and what can their councils spend?

**Date registered:** 2026-09-22. Written before any town-level vulnerability figure was computed. Only
the Census table names and column names were inspected.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Question
Are the NSW towns whose exit roads have all been cut by fire at once home to more people who find it
hard to evacuate? And what own-source money do their councils have per such resident? This is
descriptive: no causal claim and no claim about lives.

## Towns and groups (from stage 2: S0, 20 km ring, towns with ≥ 2 exits)
- **Cut-off towns:** ≥ 1 observed full cut-off in part A (2019–23) or part B (1950–2019).
- **Comparison (primary):** all other stage-2 towns (never cut off).
- **Comparison (secondary):** towns touched by fire (a fire closed ≥ 1 exit) but never fully cut off.

Single-exit towns are outside the stage-2 sample and are not included.

## Vulnerability measures (ABS 2021 Census, General Community Profile, by UCL; the data pack is hash-frozen)
1. **Primary:** share of residents aged 65 and over, from G01: (Age 65–74 + 75–84 + 85+) ÷ total persons.
2. Share of occupied dwellings with **no motor vehicle**, from G34: 0 vehicles ÷ dwellings with the number of vehicles stated.
3. Share of people who **need assistance with core activities**, from G18: need assistance ÷ (total − not stated).
4. **Median weekly household income**, from G02 (lower means more vulnerable).

Measures are missing (never zero) when a denominator is 0 or not published.

## Decision (primary measure only)
- Estimate: median(cut-off towns) − median(never-cut-off towns) in the % aged 65+.
- 95% CI: bootstrap over towns, 2,000 resamples, seed 20260921, resampling within each group.
- Also reported: two-sided Mann–Whitney p.
- **SUPPORTED** (cut-off towns are older) if the difference is > 0 and the whole 95% CI is > 0.
- **OPPOSITE** if the whole CI is < 0.
- **NOT SUPPORTED** otherwise.
- NOT EVALUABLE if fewer than 15 cut-off towns have the measure.

## Secondary (descriptive, no verdict)
- Measures 2–4, compared the same way, with Holm-adjusted Mann–Whitney p-values.
- All four measures against the secondary comparison group.

## Totals and public-finance link (descriptive)
- Totals across cut-off towns: residents, residents aged 65+, people needing assistance, and dwellings with no car.
- For each council containing cut-off towns (town → council by largest overlap, as in stage 6):
  - its vulnerable residents in cut-off towns (aged 65+, and needing assistance)
  - its own-source revenue per resident in 2018-19 = `total_revenue_including_capital_aud` × `own_source_pct` / 100 ÷ `population`, from `master.fiscal_panel_extended`
  - **own-source dollars per vulnerable resident in cut-off towns** (the council's own-source revenue ÷ its residents aged 65+ living in cut-off towns)

  Councils missing from the extended panel are listed as missing, never filled in.

## Caveats
- Town comparisons ignore that one fire can cut off several neighbouring towns; the CI is optimistic.
- Census 2021 was taken in August 2021, after the 2019–20 fires. Population may already have changed.
- Council revenue is not money set aside for evacuation roads, and many exit roads are state roads.
- Cut-offs are inferred from fire maps (stage 2): an upper bound.
