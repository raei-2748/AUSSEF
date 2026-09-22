# Pre-registration: stage 9, illusory redundancy — who is wrongly counted as safe, and who pays

**Date registered:** 2026-09-23. Written before any stage-9 number was computed. Only file lists,
column names and field names were inspected.
**Status:** frozen. Record any change in `DEVIATIONS.md`.

## Why
Published work rates a community's evacuation safety by **counting its exit roads**. Fong et al.
(PNAS 2026, "Egress thresholds and wildfire fatalities") count higher-order roads crossing a 0.5 km
buffer around a community, divide by two, and find wildfire fatality risk flattening at about six
exits. That method treats exits as **independent**, which stages 2–4 of this project show is wrong:
in NSW, fires cut every exit of a town together far more often than independence predicts.

Stage 9 asks the social and fiscal consequence: **which towns does a count-based standard rate as
safe although fire has cut them off entirely, who lives in those towns, and who owns and funds
their exit roads?**

## Part 1: classification (measurement failure)
- **Counted exits** (PNAS-style), from the frozen 2019 road network: the number of distinct higher-order roads (`motorway`, `trunk`, `primary`, `secondary`, `tertiary` and their `_link` variants) whose edges cross the boundary of a 0.5 km buffer around the town polygon, divided by 2 and rounded down. Roads are distinguished by `ref` where present, otherwise by `name`; unnamed crossing edges count individually.
- **Ever cut off:** ≥ 1 observed full cut-off in stage 2 (rule S0, 20 km ring, parts A 2019–23 or B 1950–2019).
- Groups at threshold T (**primary T = 6** as published; **secondary T = 3**):
  - **Illusory redundancy:** counted exits ≥ T and ever cut off.
  - **Correctly rated safe:** counted exits ≥ T and never cut off.
  - **Rated at risk:** counted exits < T.
- Reported: the cut-off rate by counted-exit bucket, and by the stage-1 max-flow exit count, so the two measures can be compared against what fires did.

## Part 2: who lives there (social)
Frozen ABS 2021 Census UCL pack. Measures per town:
- % aged 65+ (G01), % needing assistance with core activities (G18), % of dwellings with no motor vehicle (G34),
- % one-person households (G35 `Num_Psns_UR_1_Total` ÷ `Total_Total`), % rented (G37 `R_Tot_Total` ÷ total households), median weekly household income (G02).

**Primary decision measure:** % aged 65+, illusory vs correctly-rated-safe towns, at T = 6.
- Median difference, bootstrap over towns (2,000 resamples, seed 20260921), Mann–Whitney p.
- **SUPPORTED** if the whole 95% CI is above 0; **OPPOSITE** if entirely below; **NOT SUPPORTED** otherwise.
- **NOT EVALUABLE** if either group has fewer than 10 towns; person-weighted totals are still reported.

Secondary (descriptive, Holm-adjusted): the other five measures, and the same comparisons at T = 3.

Person-weighted totals for illusory-redundancy towns: residents, aged 65+, needing assistance,
dwellings with no car.

## Part 3: who owns and funds the exits (finance)
- **Ownership:** TfNSW "NSW Road Network Categorisation" (CC-BY; `admin_clas`: S = State, R = Regional). Each stage-1 exit-path edge is labelled by the nearest categorised line within **25 m**; unmatched edges are labelled **local** (council). Reported per town: the share of exit-route length that is State, Regional and local, and the same for edges that fires actually closed.
- **Council capacity** (reusing the stage-6/7 town → council join and `master.fiscal_panel_extended`, 2018-19): own-source revenue per resident, own-source revenue per resident aged 65+ in the council's illusory-redundancy towns, and grant dependence. Councils missing from the panel are listed, never imputed.
- Headline comparison: the level of government that owns the failing exits against the level that holds the fiscal capacity.

## Part 4: indicative cost (exploratory, labelled)
Kilometres of closed exit route in illusory-redundancy towns × council road spending per km
(`olg_road_expenditure_panel.csv` 2018-19 roads/bridges/footpaths expenditure ÷ `road_km`).
Reported as a quartile range across councils, never a single number. It is an **annual
maintenance-equivalent** figure, not a construction cost, and carries no decision.

## Caveats
- Counted exits are our implementation of a published method on Australian data, not the authors' own figures; no US result is re-estimated here.
- Cut-offs are inferred from fire maps (stage-2 caveats: upper bound, no timing).
- Road categories are current, and are applied to a 2019 network.
- The Census was taken in August 2021, after the 2019–20 fires.
- Descriptive throughout: no causal claim, no claim about lives, no machine learning.
