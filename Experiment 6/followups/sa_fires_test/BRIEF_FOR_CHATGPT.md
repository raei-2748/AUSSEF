# Briefing: pre-fire council risk score for bushfires, and where we are stuck

Purpose: I want help finding a workable way forward. Please read all of this, then answer the questions in section 9. Where you are unsure, say so; do not invent sources or numbers.

## 1. The project in one paragraph
A student research project (AUSSEF) on Australian bushfires. Unit of analysis = council x fire (one row per local government area affected by a fire). We built a **pre-fire risk score** for each council from information known before any fire, and test whether high-score councils really suffered more in real fires. The mentor (Bowen) approved this angle and asked whether the definition of a "large fire" could be changed to include more large fires. The intended end product includes a NSW risk map.

## 2. The score (built before looking at outcomes)
Four blocks, each item turned into a 0-1 percentile across 129 NSW councils (1 = worse), block = mean of items, score = equal-weight mean of available blocks:
- **H hazard:** share of council area in NSW Bush Fire Prone Land (Category 1; Category 1+2) and forest share (NVIS). Grassland (Cat 3) excluded.
- **E exposure:** share of dwellings and residents inside Bush Fire Prone Land Cat 1-2 (2016 Census mesh blocks).
- **V vulnerability:** SEIFA disadvantage index (low), median income (low), unemployment rate (high).
- **F fiscal:** council finance ratios (cash cover, own-source revenue, debt service, operating ratio, infrastructure backlog, unrestricted current ratio).

## 3. The outcome measure Y (four pillars, each a percentile in a master distribution)
- **DL** direct loss: homes destroyed per 1,000 dwellings (sourced counts; known for under half the rows).
- **IL** indirect loss: fall in total income and in business counts, relative to same-state councils with no big fire that year.
- **FP** council fiscal pressure: cash-cover drawdown, services crowd-out, renewals-ratio rise (excess over no-fire councils).
- **SL** social loss: rise in working-age income-support recipients per 1,000 residents (excess over no-fire councils).
Y = mean of the pillars available. All excess-change measures subtract the median change of same-state councils with no fire of 100 ha or more in the window.

## 4. What we found, in order
1. **Master data (NSW 2015-2025, 96 fires, 218 council x fire rows).** The hazard block picks councils that later get a big fire (AUC about 0.95). Given a big fire, the vulnerability block tracked Y (rank correlation about +0.58 on councils with at least 5% burned). Equal-weight score about 0 on all rows. Fiscal block about 0 and does not predict fiscal pressure. But: **30 of the 38 rows at >=5% burned are from Black Summer (2019-20)**, and all councils with >=20% burned are Black Summer. Random forests on the same inputs did not clearly beat the fixed score.
2. **Round 1 fresh test (frozen rules):** NSW Oct 2013 and Victoria Black Saturday 2009, 26 council rows. Pooled Spearman +0.00, 95% CI [-0.40, +0.40]. Verdict "cannot tell".
3. **Round 2 fresh test (frozen rules):** five South Australian fires (Sampson Flat 2015, Pinery 2015, Cudlee Creek, Kangaroo Island, Keilira 2019-20). Only 11 councils had >=1% of area burned. Pooled with round 1 (37 rows, 7 fires, 5 separate weather periods): **Spearman -0.09, 95% CI [-0.42, +0.26]**. Pre-set rule (replicated if lower bound >0; not replicated if upper bound <+0.30; else cannot tell) gives **"not replicated"**.

## 5. Details that matter for interpretation
- The "not replicated" label is fragile: without the three 2019-20 SA fires (same season as Black Summer) pooled is +0.05 [-0.30, +0.37] = "cannot tell". Dropping Cudlee Creek or Kangaroo Island alone puts the upper bound at 0.30.
- The rule is a weak bar: in a planted-effect simulation on these rows, a true zero would be labelled "not replicated" only about 40% of the time, and a true correlation of 0.3 would be detected (lower bound >0) only about 40% of the time. About 47 comparable rows would be needed for 80% power at a true 0.4, about 85 for 0.3.
- Pieces (descriptive, not decisive): vulnerability block alone +0.26 [-0.09, +0.55] pooled (+0.65 on the 11 SA rows); homes destroyed per 1,000 dwellings -0.58 [-0.86, -0.14] on 16 rows (wrong direction: higher-score councils lost fewer homes per dwelling); income/business loss pillar +0.24 [-0.12, +0.56].
- SA specifics: hazard/exposure come from the SA Bushfire Protection Areas layer (modelled risk classes, not NSW vegetation categories) placed in the NSW scale; fiscal block could not be built (SA finance ratios failed a 30% comparability rule); business-count indicator missing for Sampson Flat; homes destroyed sourced for 5 of 11 SA rows.
- The bootstrap treats councils as independent although councils in one fire share weather and burn, so true uncertainty is larger than shown.
- Each fire contributes only 1-4 councils under the 1%-burned rule, so extra fires add rows slowly (Tasmania 2013 about 2 rows, WA Waroona 2, Wooroloo 1).
- Rules we follow: pre-specify and hash-lock the score, outcome recipe and test before computing outcomes; new-fire rows are kept separate from the master data; no Australian Community Media sources; no Wikipedia; ABC, government, inquiry and audit-office sources are fine.

## 6. The bottleneck as I frame it (a measurement bottleneck)
1. **Too few big fires and too few councils per fire.** Large burns are rare and each covers 1-4 councils, so sample size grows slowly and one season (Black Summer) dominates the master data.
2. **The outcome is noisy and incomplete.** Homes destroyed is the only direct measure and is known for under half the rows. Income, business counts, council finances and income support move for many reasons besides fire, and we can only remove a same-state median trend.
3. **The score mixes two different questions:** "where will a large fire occur" (hazard: works, AUC about 0.95) and "how badly will a council be hurt given a fire" (consequence: not shown to work outside Black Summer). Fire behaviour on the day (weather, wind change, fire path) is not in a pre-fire score at all.
4. **Adding more data files has not helped** because the limits are in (1)-(3), not in missing inputs.

## 7. What still looks solid
- Hazard block identifies where large fires happen, independent of Black Summer.
- Gap in the literature as we read it: the NSW Reconstruction Authority State Disaster Mitigation Plan (2024) scores council risk using building loss only and has not tested against real fires (it lists social and economic impact indicators as not yet established); other work covers only resilience indices or only fire occurrence.

## 8. Options we have discussed (not yet decided)
A. Present the NSW output as two labelled layers: hazard ("where large fires are likely", validated) and vulnerability ("who is more exposed to harm", descriptive), without claiming it predicts damage.
B. Concentrate on one clean outcome (homes destroyed) rather than a four-pillar composite.
C. Report the finding itself: a pre-fire score identifies hazard but does not predict multi-dimensional damage outside Black Summer, because outcome data are thin.
D. Keep adding independent fires (slow, and unlikely to settle it on its own).

## 9. Questions for you
1. Is my framing of the bottleneck right? What have I missed (statistical design, unit of analysis, outcome definition)?
2. Is there a better unit or design than council x fire with a 1%-burned threshold, for example fire-level or grid-cell (mesh-block) outcomes, or a different comparison design, that would give far more usable data from what we have?
3. Which outcome(s) could be measured much more cleanly, and from what public Australian sources (not ACM, not Wikipedia)? For example insurance claims by postcode/LGA, building-impact assessments, DRFA payments, house-loss datasets.
4. Should the score be split into a hazard (occurrence) model and a separate consequence model, and how would you validate each so that the result does not depend on Black Summer?
5. How would you handle the small, clustered sample honestly (for example hierarchical or fire-level clustering, exact tests, or a Bayesian summary)?
6. If you were a supervisor, which of options A-D would you choose, or what would you propose instead? Give a concrete 2-week plan with what to build and what result would count as success or failure, decided before looking at outcomes.
