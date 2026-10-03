# Experiment 18 findings

## CORRECTION, 3 Oct 2026 (addendum B): the "model overstates" headline is withdrawn

**What was wrong.** v1 (below) checked the input-output (IO) model against five measured limits. Three of them measure
things the model does not predict:
- business **counts** (a café that loses months of sales is still counted);
- the **unemployment rate** (firms keep staff through short dips, and JobKeeper held them from March 2020).

The model predicts lost **sales** and lost **income**. On the two income checks, the default model was already inside
the measured range (slope -0.95% per 10 pp of homes inside). So "the default model overstates by 4-15x" and the
"A$41m-A$174m" range came mostly from the mismatched checks. The "1-3 month disruption" was forced by the unemployment
check and is also withdrawn. Ray spotted the problem; rules for the fix were locked first (PRESPEC_ADDENDUM_B.md,
LOCK_B.txt). This is a correction made after seeing v1 results (DEVIATIONS D23-D26).

**Corrected result (results/v2_IL_SUMMARY.json, figures/fig5_lost_trade_fair_check.png).**
- The model was checked against measured income only (ATO postcode and ABS small-area income, Black Summer, years 1-2).
- Industries with no jobs (ABS IO 6700 and 6701, dwelling ownership and housing rent) were removed from business
  interruption, which fixes the v1 audit's minor issue (a).
- **531 of 1,620 model settings agree with both income checks.** Over those settings, Black Summer **lost sales**
  in the first 24 months (36 council-fire rows, gross output, no rebuild offset, modelled) are:
  - **A$411m to A$2,707m** (middle 90%); full range A$271m to A$3,616m;
  - middle value **A$960m**; default settings A$640m.
- Labour income lost (middle value) A$295m; year-1 job-equivalents about 4,100.
- Disruption lengths of 1 to 30 months all fit, so there is no clash with the night-light data any more.
- Sensitivity, postcode income only (the check that passes its placebo): 1069 settings, A$56m to
  A$2,566m. That check has no floor, so it allows almost no loss.
- Out of sample: 57% of the income-consistent settings also agree with pre-COVID fires' income limit
  (wide CI, weak test).

**How to read it.**
- Lost sales are a real loss, carried mostly by local businesses and workers, but they are **not in Exp 17's payer
  accounts**. They are gross output, not value added, so they are shown next to the A$2.44bn loss account and never
  added to it.
- "Middle 90%" is the spread over model settings (assumptions), not a statistical confidence interval. Disruption of
  24 and 30 months gives identical 24-month totals. Dropping the 44 duplicates gives 487 settings, A$393m to A$2,766m,
  middle A$957m (audit B).
- Caveats (audit B):
  - Exp 13 says the Black Summer income fall cannot be separated from COVID, which weakens both income checks.
  - The low end rests only on the ABS small-area income check, which has no placebo. Without it the minimum is A$40m.
  - The checks constrain income net of rebuild wages, not gross lost sales directly.
  - The model and the measurements use different income measures and geographic scales. Some of the measured fall may
    be residents moving away.
  - The total covers 36 of 57 Black Summer rows.
  - Exp 13's wage-income result (-1.5% [-3.4, +0.4]) would be a closer like-for-like check (not used; not prespecified).
- The range is wide because measured income pins down only one slope.
- Modelled IL is built from fire-size inputs, so it stays out of the prediction target Y. The RF result is Y_measured.

**Also corrected: who pays.** v1 section 6 added government recovery money to the losses (A$3.39bn). Exp 17 keeps these
as two separate accounts: one shows who carried the loss, the other who spent money afterwards (part of it went to
the same households). The corrected figures (figures/fig6_black_summer_who_pays.png) are:
- losses A$2.44bn: insurers 77%, households 12%, governments' clean-up 11%;
- recovery money A$0.94bn, kept separate: Commonwealth 73%, NSW 27% (DEVIATIONS D27).

**Still true from v1:**
- Y_measured RF results and SHAP;
- the hybrid index did worse and is not used;
- the novelty wording in section 9, which becomes "we check an IO model's lost-sales estimate against fire-matched
  measured income".

---

# v1 findings (2-3 Oct, kept as the record; sections 1, 3, 10 and 11 superseded by the correction above)

Written 3 Oct 2026 for Ray and Bowen. Plain English. Every number comes from a file in this folder. "Modelled" means it
comes from an assumed model. "Measured" means it comes from real data. Source ids (like E18P-05) are rows in
`bibliography/parts/exp18_hybrid_2026-10-03.csv`.

## 1. The question, and the short answer

Indirect loss (IL) is the harm to local business and jobs that follows a fire, beyond the homes and property burned.
We could not measure IL well (measured IL is not predictable from our X variables, RF rho +0.09). So we tried a standard
economist's tool, an input-output (IO) model, built from ABS national tables (E18-IO1 to IO4), and asked: does it agree
with what measured local data allow?

Short answer:
1. **No, not with its default settings.** The default IO model predicts more harm than the measured data allow
   (section 3). This is the strongest result.
2. **It agrees only if the disruption is very short** (3 months or less). That conflicts with night-light data
   (section 3), so the fit is real but uncomfortable.
3. **The hybrid did not improve prediction.** The overall impact index with modelled IL (Y_hybrid) scores lower than the
   measured one (Y_measured). The audit says this is mostly a side effect of how the model is built (section 5).
4. **The main scientific result is unchanged: Y_measured**, exactly reproduced from Experiment 14.

The gate in the prespec (PRESPEC F) was passed on the Black Summer pilot: 3 of 3 primary checks inside their CIs, all
settings inside plausible bounds, IL_model not trivial (0 tied values in the pilot). So the full 218-row run went ahead.
The pass was weak, and the pilot said so (sections 3 and 5).

## 2. What was done

- Locked a written plan (PRESPEC.md, hash in LOCK.txt) before any modelled number existed. The audit confirmed the lock
  came first.
- Built modelled IL for council x fire rows from: tourism spend lost, business interruption, and an offset for rebuilding
  work (homes destroyed x A$344,300 x 0.66). The ABS national model was scaled down to each council with a standard
  method (FLQ). Farm losses were left out (no farm data on disk).
- **Coverage is partial.** Only 88 of 218 rows have a modelled value (36 of the 57 Black Summer rows). 68 rows have no
  tourism spend and 62 more have no homes-destroyed count. Missing stays missing (DEVIATIONS D16).
- Searched 1,620 settings of the model's assumed knobs (disruption length, who is reached, rebuild share, scaling,
  model type) and compared each with five measured limits (Experiments 7, 12, 13, 15).
- Re-ran Experiment 14's random forest, leave-one-fire-season-out, on Y_measured and on Y_hybrid. Added SHAP.
- An independent audit re-derived the multipliers, five rows and both RF results (audit/AUDIT.md).

## 3. Result A: measured data limit the IO model (modelled vs measured)

Each check compares the model's slope with a measured 95% CI on the same scale (results/IL_CHECKS.csv).

| Check | Measured CI (real data) | Default model (modelled) | Data-constrained model (modelled) |
|---|---|---|---|
| M1 unemployment, points per 10% of residents in or within 1 km (primary) | -0.35 to +0.59 | +1.02, overstates | +0.03, inside |
| M2 income, % per 10 pp homes inside (primary) | -3.1 to +0.8 | -0.95, inside | +0.29, inside |
| M3 accommodation and food, % per 10 pp homes inside (primary) | -1.2 to +8.6 | -8.2, overstates | -0.37, inside |
| M1b SA2 unemployment (secondary; placebo test fails) | -0.29 to +0.12 | +3.81, overstates | +0.01, inside |
| M2b SA2 income (secondary) | -2.6 to -0.7 | -0.95, inside | +0.29, understates |

Sources: Exp 7 Day 6 and Exp 13 limits (E18P-05, E18P-06, E18P-07, E18P-14, E18P-16), checked by the audit.

- Default model: 2 of 3 primary checks and 1 secondary check show the model **overstating** harm.
- Constrained model (disruption 1 month, only people inside the outline, rebuild share 0.66, scaling 0.3, Type II): all 3
  primary checks inside. It does not reproduce the measured SA2 income fall (M2b), so no setting fits everything.
- 177 of 1,620 settings pass all 3 primary checks. **All 177 have disruption of 1 to 3 months.**
- **Effect on Black Summer** (36 rows, first 24 months, nominal mixed-year A$, modelled, partly assumed):
  default gross output loss A$649m; data-consistent range A$41m to A$174m across the 177 passing settings (a cut of
  73 to 94%); picked setting A$45m (results/IL_BOUND_RANGE.csv, IL_SUMMARY.json).
- Jobs lost in year 1 per home destroyed: 2.6 (default), 0.04 (constrained). Exp 12's measured upper limit for income-
  support recipients per home is 4.48 (descriptive only, not a calibration).

**The tension (stated by the audit as a major interpretation point).** Exp 15 night lights show the area inside the fire
dimmed for about 1.5 to 2.5 years. The model fits the other measured limits only with 1 to 3 months. A possible reading:
the lights dim because homes were lost, not because businesses closed. That is an interpretation, not tested.

**Out-of-sample check (weak).** Calibrating only on pre-2019 (pre-COVID) limits picks the same duration but a wider reach.
On Black Summer it passes M1 and M2 and overstates M3 (-1.35 vs limit -1.2) and M1b. The pre-2019 CIs are wide, so this
check has little power.

## 4. Result B: prediction (measured, leave-one-fire-season-out RF, 218 rows)

Y_measured = Y_v4, unchanged. Reproduced with the copied Experiment 14 code; the largest gap is about 1e-16
(results/MATCH_EXP14.csv).

| Target | X set | rho [95% CI] |
|---|---|---|
| Y_measured | PRE+FIRE | +0.43 [+0.28, +0.55]; shuffled-Y p = 0.01 (100 shuffles) |
| Y_measured | PRE alone | +0.18 [-0.07, +0.37], not detected |
| Y_measured, council-grouped CV check | PRE+FIRE | +0.25 [+0.07, +0.45] |
| DL | PRE+FIRE | +0.73 [+0.64, +0.79] (pillar numbers quoted from Exp 14) |
| IL (measured) | PRE+FIRE | +0.09 [-0.24, +0.40], not detected |
| FP | PRE+FIRE | -0.09 [-0.33, +0.11], not detected |
| SL | PRE+FIRE | +0.02 [-0.17, +0.19], not detected |

Only DL is predictable, and through it Y. What drives Y_measured (out-of-fold SHAP, share of mean |SHAP|): homes inside
the fire 29% (higher means higher impact), hazard H 11%, underinsurance proxy X23 11% (more underinsurance, higher
predicted impact), fiscal F 10%, vulnerability V 10%. Permutation importance agrees on the top two.
SHAP is read scientifically only for measured targets (results/SHAP_SUMMARY.csv, PERM_IMPORTANCE.csv).

## 5. Result C: the hybrid index did worse, and why (modelled, partly assumed)

| Target | X set | rho [95% CI] |
|---|---|---|
| Y_hybrid | PRE+FIRE | +0.19 [+0.02, +0.33]; shuffled-Y p = 0.02 |
| Y_hybrid minus Y_measured | PRE+FIRE | -0.24 [-0.40, -0.08] |
| IL_model alone (88 rows) | PRE+FIRE | +0.20 [-0.10, +0.47]; p = 0.08, not detected |
| Extra, not prespecified: Y_hybrid_gross (no rebuild offset) | PRE+FIRE | +0.43 [+0.31, +0.53], no better than Y_measured |

Why: with a 1-month disruption, the rebuild offset is bigger than the loss in 42 of 88 rows. Net IL_model then mostly
ranks councils by homes destroyed, reversed. Its Spearman with DL is -0.89 (88 rows), so it partly cancels DL inside Y.
**So "Y_hybrid is worse" mainly shows how the model was built. It is not evidence about real indirect loss.** The
leakage guard (removing the overlapping fire-size X columns) cannot catch overlap with a Y pillar.
The guard gives: Y_hybrid full-X minus guard +0.25 [+0.13, +0.39]; Y_measured +0.21 [+0.12, +0.34]. Most of that gain is
real fire-size signal shared with Y_measured. IL_model_gross RF rho 0.88 is circular (built from the X inputs) and is
not skill. Modelled IL vs measured IL: -0.22 (83 rows).

## 6. Who pays (Black Summer; Experiment 17 counted costs, mid values)

Of A$3.39bn: insurers 56%, Commonwealth 24%, NSW 11%, households 9% (E18F-09; the shares in the run instructions did
not match the file, so the file values are used, D21). The data-consistent modelled loss to local business output
(A$41m to A$174m) is small next to this. It is output, not a cost to a payer, so it is shown separately.

## 7. What did NOT work

- The default IO model does not match measured limits (overstates).
- No setting fits all five checks (M2b understated).
- Modelled IL does not predict better than measured Y. IL_model alone is not detected.
- Coverage: 88 of 218 rows. Farm output is missing.
- Out-of-sample calibration failed M3 and M1b.

## 8. Audit (audit/AUDIT.md): verdict "minor issues"

Arithmetic is correct: multipliers, five rows, all limits, both RF results re-derived exactly; prespec hash intact;
Experiment 14 code copy is byte-identical. Two major interpretation points, both stated above (sections 3 and 5).
Minor: (a) the IO "Rental and real estate" division includes owner-occupied housing with output but no jobs, so output
per job is A$1.49m vs A$0.32m on average, which inflates baseline and business-interruption loss (not in DEVIATIONS);
(b) Exp 13 flags its income limit "pre-COVID sign differs" and the prespec does not mention it; (c) a code comment says
pre-period 2009-2018 while the code uses 2014-2018 (same result); (d) one file the audit opened (Exp 13 pia.json) lacked a
bibliography row, now added (E18F-12). Deviations D1 to D22 are in DEVIATIONS.md (for example 100 shuffles instead of
200, D17; SHAP added, D18).

## 9. Safe wording for novelty (from the literature check, about 15 sources)

"Published Black Summer input-output estimates, as far as we could see, do not check their indirect-loss figures against
measured local outcomes. We check a standard input-output model's indirect-loss estimates against fire-matched measured
local data and bound them, validated leave-one-fire-season-out. Related measured-versus-modelled comparisons exist for
other disasters (a Texas wildfire with IMPLAN, an earthquake with nightlights). We are not aware of one for Australian
bushfires." Do not say "first" without the caveat that the search was limited. Closest works:
- Dudensing, Richardson and Lu 2013, Hurricane Ike and a Texas wildfire (E18L03; abstract only read).
- Wang et al. 2018, Wenchuan earthquake and nightlights (E18L01).
- Reiner, Malik, Lenzen et al. 2024, Black Summer tourism: A$2.8bn output, about 7,300 jobs (E18L04, E18L05; figures
  from the University of Sydney page because the journal page was paywalled).
- Walls and Wibbenmeyer 2023, US wildfires, measured, no IO model (E18L09).
- Koks et al. 2016, IO vs CGE on floods (E18L02).
- ABS warns national multipliers can overstate and are not for small regions (E18L08).

IO sources read only as search snippets (Hallegatte ARIO E18L06/L07, Haimes and Santos E18L11, Flegg FLQ E18L10,
Quiggin E18L12): do not cite from memory, read them first.

## 10. How to describe this honestly

Strongest honest claim: measured local data put tight limits on indirect loss, and a standard IO model must be cut by
roughly 73 to 94% to respect them, but only if disruption is very short. That is a bounded estimate, partly assumed.
It is not a predictive win. Report Y_measured as the result; use the hybrid only for a dollar estimate of indirect loss,
not as a pillar.

## 11. Decisions for Ray

1. Drop the hybrid as a Y pillar and keep it as a dollar-bound only? (Recommended.)
2. Accept 1 to 3 months disruption with the homes-not-businesses reading, or test it?
3. Frame this in the write-up as "bounding IO with measured data", not "better prediction".
4. Use the safe novelty wording in section 9 (with the limited-search caveat), never "first".

Figures: figures/fig1 to fig4. Nothing was committed. No other experiment folder was changed.
