# Stage 9 results: does counting exits find the towns fire cuts off, and who pays?

## Headline

Published work rates a community's evacuation safety by **counting exit roads** (Fong et al., PNAS 2026:
fatality risk flattens at about six exits). We applied that counting method to NSW and checked it
against 70 years of fires.

**1. The count does track risk, in the right direction.** The share of towns ever fully cut off falls
steadily as the count rises, and no NSW town with 4 or more counted exits has ever been cut off. Our
network-based measure shows the same: towns with 6 or more independent routes were never cut off, while
a third of two-exit towns were.

**2. But the published threshold cannot be used here.** Only 5 NSW towns
in our sample reach 6 counted exits at all, so the six-exit standard does not separate Australian country
towns. The pre-registered comparison at that threshold is therefore **NOT EVALUABLE**.

**3. The blind spot is real but smaller than expected.** Using the same method without its
"divide by two" step, and a threshold of 3 roads out (nohalve_T3), **15 towns** look adequately
connected yet fire has cut every exit at once. **50,638 people live in them**, including
**15,954 aged 65+**, **4,405 who need help with everyday activities** and
**991 homes with no car**.

**4. The exits that fail are mostly the State's responsibility.** In those towns
**49.0%** of exit-route length is State-owned road (NSW Government), against
38.8% across all towns, and **52.9%** of the exit road that actually burned
was State-owned. Councils hold the local roads and the local budget; the State holds most of the
roads that fail.

**5. Indicative scale of the affected roads:** $6,893,951 a year in maintenance-equivalent
spending across 4 councils (per-council median $1,557,261). Exploratory only, see the caveat.

### In plain words

Counting roads out of town mostly works, and towns with several genuinely separate routes have not been
cut off. The problem is the towns in between: a handful have three or more roads out and were still
completely trapped, because one fire took the lot. About 50,638 people live there, and nearly a third
of them are over 65. Most of the roads they would escape on belong to the State, not their council.

This is descriptive measurement: no causal claim and no claim about lives.

## Does having more exits mean less risk?

| Measure | Exits | Towns | Ever cut off | Cut-off rate |
|---|---|---|---|---|
| counted exits (PNAS-style) | 0 | 59 | 12 | 20.3% |
| counted exits (PNAS-style) | 1 | 198 | 24 | 12.1% |
| counted exits (PNAS-style) | 2 | 137 | 6 | 4.4% |
| counted exits (PNAS-style) | 3 | 46 | 1 | 2.2% |
| counted exits (PNAS-style) | 4-5 | 16 | 0 | 0.0% |
| counted exits (PNAS-style) | 6+ | 5 | 0 | 0.0% |
| max-flow exits (this project) | 0 | 0 | 0 | missing% |
| max-flow exits (this project) | 1 | 0 | 0 | missing% |
| max-flow exits (this project) | 2 | 67 | 22 | 32.8% |
| max-flow exits (this project) | 3 | 91 | 11 | 12.1% |
| max-flow exits (this project) | 4-5 | 163 | 10 | 6.1% |
| max-flow exits (this project) | 6+ | 140 | 0 | 0.0% |

Figure: `out/cutoff_rate_by_exits.png`.

## Who lives in the blind spot?

The pre-registered primary comparison (≥ 6 counted exits) is **NOT EVALUABLE**: no NSW town is both
rated safe at that threshold and ever cut off. The rows below show every variant, including the
post-hoc unhalved count (DEVIATIONS U1). At the reported variant (nohalve_T3), towns in the blind spot
had a median 29.4% of residents aged 65+, against
23.1% in towns rated safe and never cut off.

| Measure | Threshold | n (illusory / safe) | Median illusory | Median correctly safe | Difference [95% CI] | p | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| Residents aged 65+ (%) | ≥ 6 exits | 0 / 5 | missing | missing | missing [missing, missing] | missing | missing | NOT EVALUABLE |
| Need assistance (%) | ≥ 6 exits | 0 / 5 | missing | missing | missing [missing, missing] | missing | missing |  |
| Dwellings with no car (%) | ≥ 6 exits | 0 / 5 | missing | missing | missing [missing, missing] | missing | missing |  |
| One-person households (%) | ≥ 6 exits | 0 / 5 | missing | missing | missing [missing, missing] | missing | missing |  |
| Rented dwellings (%) | ≥ 6 exits | 0 / 5 | missing | missing | missing [missing, missing] | missing | missing |  |
| Median household income ($/wk) | ≥ 6 exits | 0 / 5 | missing | missing | missing [missing, missing] | missing | missing |  |
| Residents aged 65+ (%) | ≥ 3 exits | 1 / 66 | 33.0 | 22.7 | 10.2 [8.4, 12.5] | 0.205 | missing |  |
| Need assistance (%) | ≥ 3 exits | 1 / 66 | 10.2 | 8.0 | 2.2 [1.7, 3.1] | 0.313 | missing |  |
| Dwellings with no car (%) | ≥ 3 exits | 1 / 66 | 6.8 | 6.6 | 0.2 [-0.1, 1.7] | 0.816 | missing |  |
| One-person households (%) | ≥ 3 exits | 1 / 66 | 35.0 | 30.7 | 4.3 [2.5, 6.4] | 0.289 | missing |  |
| Rented dwellings (%) | ≥ 3 exits | 1 / 66 | 32.0 | 29.3 | 2.8 [-0.4, 5.8] | 0.737 | missing |  |
| Median household income ($/wk) | ≥ 3 exits | 1 / 66 | 1,090.0 | 1,346.5 | -256.5 [-323.0, -160.0] | 0.394 | missing |  |
| Residents aged 65+ (%) | ≥ 6 exits | 1 / 66 | 33.0 | 22.7 | 10.2 [8.4, 12.5] | 0.205 | missing |  |
| Need assistance (%) | ≥ 6 exits | 1 / 66 | 10.2 | 8.0 | 2.2 [1.7, 3.1] | 0.313 | missing |  |
| Dwellings with no car (%) | ≥ 6 exits | 1 / 66 | 6.8 | 6.6 | 0.2 [-0.1, 1.7] | 0.816 | missing |  |
| One-person households (%) | ≥ 6 exits | 1 / 66 | 35.0 | 30.7 | 4.3 [2.5, 6.4] | 0.289 | missing |  |
| Rented dwellings (%) | ≥ 6 exits | 1 / 66 | 32.0 | 29.3 | 2.8 [-0.6, 5.6] | 0.737 | missing |  |
| Median household income ($/wk) | ≥ 6 exits | 1 / 66 | 1,090.0 | 1,346.5 | -256.5 [-321.0, -156.5] | 0.394 | missing |  |
| Residents aged 65+ (%) | ≥ 3 exits | 15 / 289 | 29.4 | 23.1 | 6.3 [0.9, 10.8] | 0.052 | missing |  |
| Need assistance (%) | ≥ 3 exits | 15 / 289 | 8.8 | 7.7 | 1.0 [-1.6, 3.3] | 0.475 | missing |  |
| Dwellings with no car (%) | ≥ 3 exits | 15 / 289 | 4.4 | 5.0 | -0.6 [-2.6, 1.0] | 0.416 | missing |  |
| One-person households (%) | ≥ 3 exits | 15 / 289 | 28.6 | 30.7 | -2.1 [-14.9, 2.9] | 0.172 | missing |  |
| Rented dwellings (%) | ≥ 3 exits | 15 / 289 | 17.7 | 24.0 | -6.3 [-9.9, 2.8] | 0.129 | missing |  |
| Median household income ($/wk) | ≥ 3 exits | 15 / 289 | 1,228.0 | 1,269.0 | -41.0 [-229.0, 219.0] | 0.999 | missing |  |

Figure: `out/who_lives_in_blind_spot.png`. Illusory-redundancy towns by variant: {'T6': 0, 'T3': 1, 'nohalve_T6': 1, 'nohalve_T3': 15}.
Groups at ≥ 6 counted exits: {'rated at risk': 456, 'correctly rated safe': 5}; at ≥ 3: {'rated at risk': 394, 'correctly rated safe': 66, 'illusory redundancy': 1}; unhalved at ≥ 3: {'correctly rated safe': 289, 'rated at risk': 157, 'illusory redundancy': 15}.

## The towns

| Town | Roads out (unhalved) | Counted exits (halved) | Max-flow exits | Residents | Aged 65+ % | State-owned share of exits | Council |
|---|---|---|---|---|---|---|---|
| Ulladulla | 3 | 1 | 3 | 14,396 | 31.9 | 57.3% | Shoalhaven |
| Batemans Bay | 6 | 3 | 5 | 12,263 | 33.0 | 47.5% | Eurobodalla |
| St Georges Basin - Sanctuary Point | 5 | 2 | 4 | 11,000 | 29.4 | 55.0% | Shoalhaven |
| Moruya | 5 | 2 | 4 | 2,762 | 27.9 | 45.0% | Eurobodalla |
| Old Erowal Bay | 4 | 2 | 2 | 1,719 | 47.6 | 48.6% | Shoalhaven |
| Basin View | 3 | 1 | 4 | 1,583 | 25.7 | 54.9% | Shoalhaven |
| Milton | 3 | 1 | 3 | 1,538 | 36.3 | 64.5% | Shoalhaven |
| Hallidays Point - Black Head | 3 | 1 | 2 | 1,106 | 49.3 | 40.5% | Mid-Coast |
| Huskisson (L) | 3 | 1 | 3 | 825 | 31.3 | 35.2% | Shoalhaven |
| Catherine Hill Bay (L) | 4 | 2 | 2 | 820 | 10.6 | 80.5% | Lake Macquarie |
| Red Head (L) | 3 | 1 | 2 | 798 | 34.3 | 40.2% | Mid-Coast |
| Cowan (L) | 3 | 1 | 2 | 599 | 17.4 | 92.8% | Hornsby |
| Hallidays Point - West (L) | 4 | 2 | 2 | 500 | 25.4 | 53.1% | Mid-Coast |
| Tingha (L) | 4 | 2 | 4 | 445 | 23.6 | 0.0% | Inverell |
| Sutton (L) | 3 | 1 | 3 | 284 | 12.7 | 20.7% | Yass Valley |

## Who owns and funds the exits

| Council | Towns | Residents | Aged 65+ | Burned exit km | Own-source $ per resident | Road spend per km | Indicative annual cost |
|---|---|---|---|---|---|---|---|
| Eurobodalla | 2 | 15,025 | 4,812 | 173.3 | $2,799 | $17,969 | $3,114,522 |
| Hornsby | 1 | 599 | 104 | 0.0 | $missing | $missing | $missing |
| Inverell | 1 | 445 | 105 | 8.1 | $missing | $missing | $missing |
| Lake Macquarie | 1 | 820 | 87 | 0.0 | $1,021 | $29,232 | $0 |
| Mid-Coast | 3 | 2,404 | 946 | 57.1 | $missing | $missing | $missing |
| Shoalhaven | 6 | 31,061 | 9,864 | 224.8 | $2,183 | $16,811 | $3,779,429 |
| Yass Valley | 1 | 284 | 36 | 0.0 | $1,422 | $5,627 | $0 |

Councils missing from the fiscal panel (not costed): Hornsby, Inverell, Mid-Coast.

## Caveats

- **The cost figure is exploratory.** It multiplies burned exit kilometres by what each council currently spends per kilometre of road. It is an annual maintenance-equivalent scale, **not** the cost of building a new road, and it carries no decision.
- Counted exits are our implementation of a published US method on Australian data. No US result is re-estimated here, and the paper's own figures are not reproduced.
- The "divide by two" step in that method is ambiguous for Australian roads; both the halved (pre-registered) and unhalved (post-hoc) counts are reported.
- The blind-spot group is small, so its social comparison is indicative, not conclusive.
- Cut-offs are inferred from fire maps (stage-2 caveats: upper bound, no timing).
- Road ownership is current and applied to a 2019 network. Edges more than 25 m from a categorised road are treated as local.
- The Census was taken in August 2021, after the 2019–20 fires.

## Run

Seed 20260921, 2000 bootstrap resamples, run at 2026-09-22T21:40:58+00:00.
All inputs hash-verified. `aussef.duckdb` SHA-256 unchanged: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.
