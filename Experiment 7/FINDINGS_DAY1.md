# Experiment 7, Day 1: can a better "normal" rescue the socioeconomic part of Y?

Date: 30 Sep 2026. Rules locked before any result: `PRESPEC_DAY1.md` (hash in `LOCK_DAY1.txt`).
Scripts: `prep_panels.py`, `build_y2.py` (locked analysis), `deviations_day1.py` (follow-ups written after the
locked result, listed below), `make_figures_day1.py`. Master workbook read-only (sha256 123423ea...ec3).

## Short answer
No. Across the 218 NSW council × fire rows, the socioeconomic pillars of Y (income, businesses, council budgets,
welfare) show no relationship with fire size, whichever way "normal" is estimated. Direct loss (homes
destroyed) rises steeply with fire size. So the reason every scoring experiment failed on "how bad" is the target:
outside direct loss, per-fire Y at council level is mostly ordinary year-to-year variation, not fire impact.

## What was done
Y v1 measures each indicator as "change in this council minus the median change in NSW councils with no fire of
100 ha". Day 1 replaced that with the standard imputation estimator (Borusyak, Jaravel & Spiess 2024): each
council's expected path from its own level plus year effects of comparable unburned councils (Metro / Regional /
Rural, OLG 2018-19 classes), fitted only on council-years without a fire. Same 7 indicators, same windows, same
aggregation. Check: does the socioeconomic part (IL, FP, SL; DL left out because it is identical) rise with the share
of the council burned? Guard: a placebo (pretend every fire happened 3 years earlier) must show nothing.

## Results
| Version of the socioeconomic part | Rank correlation with share burned (95% CI) | Placebo |
|---|---|---|
| V1 (current workbook) | -0.00 [-0.14, +0.13] | not run |
| V2a (imputation, NSW year effects) | -0.08 [-0.25, +0.08] | fails (+0.38) |
| V2b (imputation, Metro/Regional/Rural year effects) | -0.09 [-0.23, +0.05] | fails (+0.25) |
| V2 + night lights (a / b) | -0.06 / -0.08 | fails |
| Deviation D1: V2b + each council's own trend, no night lights | -0.00 [-0.18, +0.18] | passes (+0.19 [-0.02, +0.38]) |

Locked rule outcome: no V2 variant passed its placebo, so V1 stays. But V1 itself does not track fire size.
For comparison, direct loss (DL rank) vs share burned: **+0.65** (90 rows with a reported figure).

Homes destroyed per 1,000 dwellings by share of the council burned (Figure 1, left):
<1%: 0.2 · 1-5%: 0.8 · 5-20%: 0.7 · >=20%: **8.0** [4.7, 12.1] (about 45 times the smallest group).

Socioeconomic indicators by the same groups (change after the fire vs the council's own pre-fire years, in SD of
normal noise; Figure 1, right): all within ±0.3 SD in every group except council cash reserves after the most
severe fires (+0.66 [0.37, 0.96] SD, about 2.4 months of expenses), against +0.21 in the smallest-fire group.
Within the Black Summer season alone the drawdown grows with fire size (1.1, 2.0, 2.4 months), which fits the
literature (councils pay up front, reimbursement lags), but it is one season, so it is suggestive, not established.

Event profile for the 23 councils with >= 20% burned (Figure 2): no jump in income, businesses, services or asset
renewals; income-support recipients drift down steadily from 3 years before the fire (a pre-existing trend, not a
fire effect: this is why the placebo failed); cash reserves dip in the fire year and the year after.

## Why the socioeconomic signal cannot be seen per fire (noise budget)
How far one council-year normally moves for no reason (1 SD), and what a fire would need to do to stand out (2 SD):

| Indicator | Normal noise (1 SD) | Needed to stand out |
|---|---|---|
| Total personal income | 8% | 16% |
| Number of businesses | 6.5% | 13% |
| Council cash reserves | 3.7 months | 7.4 months |
| Services share of spending | 4.8 points | 9.7 points |
| Asset renewals ratio | 111 points | 222 points |
| Income-support recipients | 7 per 1,000 residents | 14 per 1,000 |

Black Saturday's documented income effect was about -8% for employed people in affected areas (up to -31% for
agriculture workers), and they are a minority of a council's residents. Diluted to the whole council it is well
under the 16% needed. This matches the literature: council or
county aggregates are usually null; effects appear in small areas, for individuals, or only for the worst fires.

## Deviations from the prespec (all free of pre-fire predictors)
1. D1: council-specific trends added and night lights dropped, after the locked result showed pre-trends.
2. Night lights dropped: after the fire, lights in heavily burned councils rose (z -1.8 in the >= 20% group; the
   workbook's own night-light indicator correlates -0.52 with share burned). Fire light or recovery lighting, not
   lost activity, so it cannot serve as an economic indicator here.
3. D2 (average effects by fire size with the smallest-fire group as a negative control) and D3 (noise budget)
   were added to explain the result. The trend model's D2 version is not used: its negative control fails
   (+2 to +3 SD in the smallest-fire group), because extrapolating each council's trend is unstable.

## What this means
1. Per-fire severity at council level should be anchored on direct loss (homes destroyed per 1,000 dwellings,
   deaths). That is the only pillar that clearly responds to the fire.
2. The socioeconomic pillars should be reported as average effects by severity tier (e.g. council cash drawdown
   after the most severe fires), not as per-fire scores. As per-fire scores they rank noise.
3. Experiment 6's "poorer councils suffer more" result needs a second look: if Y's socioeconomic part does not respond
   to fires, a link between disadvantage and Y cannot simply be read as a fire effect. Day 2 checks it directly
   (it disappears with the placebo-passing counterfactual).
4. The consequence part of the risk score should therefore predict homes destroyed per 1,000 dwellings
   (given a fire), which is Day 2.
