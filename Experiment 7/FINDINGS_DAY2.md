# Experiment 7, Day 2: predicting housing loss from pre-fire data, and the map

Date: 30 Sep 2026. Rules locked before any result: `PRESPEC_DAY2.md` (LOCK_DAY2.txt) and, for the
prospective check, `PRESPEC_DAY2B.md` (LOCK_DAY2B.txt). Scripts: `day2_consequence.py`, `day2b_prospective.py`,
`make_maps.py`. Target: homes destroyed per 1,000 dwellings (DL_FILLED v2: reported plus inferred zeros, 135 rows,
54 with losses, 68 councils, 9 fire seasons).

## Short answer
- **Which councils lose homes: yes.** A map built only from data available before Black Summer ranks the councils
  that went on to lose at least 1 home per 1,000 dwellings in 2019-20 with AUC 0.91 [0.86, 0.96]. Half of its top 20
  lost homes, about 3 times the base rate (20 of 129).
- **How many homes a given fire destroys: only partly.** Pre-registered test: adding exposure (share of a council's
  homes inside bush-prone land) to fire size did not improve out-of-season ranking (not confirmed). It did cut
  out-of-season prediction error by 40%. The big unknown is the season itself: Black Summer destroyed 5 to 15 times
  more homes than the same fire sizes had destroyed in other seasons.

## Primary test (pre-registered): not confirmed
Leave-one-fire-season-out, Spearman of predicted vs observed homes destroyed per 1,000 dwellings:

| Model | Out-of-season Spearman | Out-of-season error (Poisson deviance) |
|---|---|---|
| M0 fire size only | 0.563 | 16,465 |
| M1 + exposure (pre-registered) | 0.569 | 9,955 (-40%) |
| M2 + disadvantage | 0.562 | 10,594 |
| M3 + hazard + council finances | 0.515 | 10,842 |

M1 minus M0 = +0.006 [-0.093, +0.099], so the pre-set verdict is **not confirmed**. Exposure changes how big the
predicted loss is, not the order: among the 54 rows with losses, fire size alone ranks them better (0.61 vs 0.48;
post hoc). The 40% error cut has a post-hoc interval of [11%, 61%] (26% outside the Black Summer fold).

Black Summer held out (models trained on the other 8 seasons): 2,483 homes destroyed; predicted 165 (M0) and
451 (M1). Other seasons: 164 destroyed; predicted 189 and 212. Outside Black Summer the models are about right; in
it, fire-day conditions that no council statistic contains multiplied the losses.

Sensitivity: reported figures only (93 rows): M1 beats M0 by +0.43 [0.18, 0.70] (confirmed); with flagged
estimates (208 rows): -0.04 [-0.11, +0.03]. The answer depends on how missing figures are treated, which is
another reason to call it not confirmed.

## What the in-sample model says (associations, not out-of-sample claims)
Given the same share burned:
- Homes destroyed rise almost in proportion to the share burned (elasticity 0.93).
- Each extra 6.7 points of a council's homes inside bush-prone land (1 SD) roughly doubles homes destroyed: rate ratio
  1.96 [1.11, 3.11]. Partial rank correlation +0.28 [0.06, 0.47].
- More disadvantaged councils lose more homes: rate ratio 1.87 [1.10, 3.14] per SD of the vulnerability block
  (with exposure in the model); partial rank correlation +0.28 [0.12, 0.42]. Not an out-of-sample gain (M2 does
  not beat M1).
- Hazard and council finances add nothing once fire size is known.

## Independent 2013 fires (descriptive, 9 NSW rows)
Trained on 2015-25, M1 predicts 177 homes for the October 2013 fires vs 211 observed (M0: 120); rank correlation 0.73
(M0 0.69). Blue Mountains: 86 predicted, 205 observed. Hawkesbury: 50 predicted, 2 observed.

## The disadvantage claim from Experiment 6
Experiment 6 reported that poorer councils "suffer more" on Y. On the socioeconomic part of Y that link is +0.21 on
all rows, but it disappears with Day 1's placebo-passing counterfactual (+0.09 [-0.14, +0.30]; placebo +0.03).
Day 1 showed that part of Y does not respond to fires, so this link should not be reported as a fire effect. The
housing-loss link above is the defensible version: for the same fire size, poorer councils lose more homes
(in-sample).

## The map (Figure 3) and the prospective check (Figure 4)
- Likelihood: logistic on the hazard block; leave-one-council-out AUC 0.95 for a fire burning >= 5% of the council.
- Consequence: M1 at a 20% burned scenario (so, in effect, the exposure layer on a homes-destroyed scale).
- Priority: 3 × 3 bivariate. In-sample, the combined index ranks the 23 councils that lost >= 1 home per 1,000
  dwellings in 2015-25 with AUC 0.93 (hazard alone 0.90, exposure alone 0.91); Spearman with realised losses 0.70.
- Prospective (built from 2015-18 fires only, BFPL caveat: today's map): AUC 0.91 for Black Summer housing loss.
  Among councils burned >= 5% in Black Summer, exposure alone ranks their losses only weakly (+0.17 [-0.25, +0.57]),
  and share burned does better (+0.36 [0.02, 0.64]). The map works mainly because the places where fires go and the
  places where homes sit in bush-prone land are the same places.

## Honest bottom line
1. Pre-fire data can say which councils are likely to lose homes (prospective AUC 0.91).
2. It cannot say how bad a given season will be: Black Summer was 5-15 times worse per hectare burned.
3. The socioeconomic aftermath (income, business, budgets, welfare) is not visible per fire in council statistics
   (Day 1), so it cannot be predicted per fire at this scale. Seeing it needs smaller areas (SA2/SA1), where the
   literature finds effects.
