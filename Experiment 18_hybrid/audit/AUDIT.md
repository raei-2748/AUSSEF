# Experiment 18 (hybrid IL pillar): independent audit

Date: 3 Oct 2026. Auditor did not write the Experiment 18 code. Re-derivation script: `audit/audit_recompute.py`
(own parsing of the ABS tables, Census and TRA files; own FLQ, Leontief, row model, composite and RF loop). Numbers:
`audit/audit_numbers.json`. No other file was edited.

Sources: every input the audit read already has a row in `bibliography/parts/exp18_hybrid_2026-10-03.csv` (E18-IO1..IO5,
E18-D1b, E18-D3/D4, E18P-02/05/06/13/14/15/16, E18F-01/02/04). One exception: `Experiment 13/results/pia.json` was opened
to confirm the M2b limit. It has no row. The limit itself is already sourced through E18P-16 (Exp 13 FINDINGS line 30).
The orchestrator should add a row for it, because this audit was told not to edit other files.

## Check table

| # | Check | Result | Severity |
|---|---|---|---|
| 1a | ABS IO inputs | Table 6 direct requirements equal Table 5 flows / output (max diff 1e-6). My own inverse of national A equals ABS Table 7 (max diff 2e-8; Type I accommodation multiplier 1.850 both ways). The code reads A, labour-income row and household column identically to my parse (diff 0). 115 industries (D2 logged). | none |
| 1b | Regionalised multipliers, 3 councils (FLQ delta 0.3) | Re-derived from Census industry counts. Bega Valley (South Coast, Black Summer; 12,681 jobs, accommodation and food LQ 1.50, lambda 0.212): Type I / II accommodation 1.068 / 1.077, tourism bundle Type II 1.085, construction Type II 1.171. Blue Mountains: 1.115 / 1.140, 1.154, 1.239. Armidale Regional (2021 Census fallback, D4): 1.079 / 1.088, 1.086, 1.151. Regional multipliers are much smaller than the national 1.85, as FLQ intends. My row results (1c) match the code exactly, so the code's multipliers match mine. | none |
| 1c | Division L (rental and real estate) output per job | Division L includes ownership of dwellings, which has output but no jobs (IO 6700/6701). So output per job in L is A$1.49m, against A$0.32m on average. This inflates council baseline output and business-interruption loss in L. It is not in DEVIATIONS (D8 describes the division method but not this effect). It changes only the scale of shares, mostly the same way across councils. | minor |
| 2 | Modelled IL, 5 rows, unconstrained and constrained | Bega Valley 2019, Eurobodalla 2019, Blue Mountains 2019, Armidale Regional 2019, Cowra 2022. Net output loss, loss share and year-1 unemployment change all match `IL_MODELLED.csv` to every printed digit. Examples: Eurobodalla unconstrained +A$172.6m (share +2.43%, +10.0 unemployment points); constrained -A$51.0m (share -0.72%). Bega Valley constrained -A$72.9m. | none |
| 3a | Limits quoted from Exp 13 | M1b B [-0.29, +0.12], M2 B [-3.10, +0.78] (quoted [-3.1, +0.8]), M3 B [-1.23, +8.56], M2b B [-2.60, -0.68] (quoted [-2.6, -0.7]), P CIs M1b [-0.83, +1.05], M2 [-2.69, +4.40], M3 [-6.44, +26.0]. All correct (ALL_RESULTS.csv, pia.json, FINDINGS line 30). | none |
| 3b | Limit quoted from Exp 7 | Day 6: -0.01 points [-0.35, +0.59] per 10% of residents in or within 1 km. Correct. | none |
| 3c | Limit quoted from Exp 12 | BOUNDS.csv income_support_recipients_per_home: slope 1.35, CI upper 4.479. Quoted 4.48 correctly. Used as descriptive only. | none |
| 3d | Context of the Exp 13 limits | Exp 13 flags income B "fails: pre-COVID sign differs" and unemployment B "fails: placebo". PRESPEC marks M1b secondary for this reason but does not mention the M2 COVID flag. M2 is a primary check. | minor |
| 4a | Y_measured (Y_v4) RF, leave-one-season-out, PRE+FIRE | My own loop (500 trees, max_features 0.3333, leaf 5, seed 20261002, median impute, 9 seasons, 218 rows): rho 0.432, the same as MODEL_METRICS and Exp 14. MATCH_EXP14 max difference is about 1e-16. Pipeline copy is byte-identical to Exp 14 (COPY_SHA256 all OK). | none |
| 4b | Y_hybrid RF, same setup | Y_hybrid rebuilt as an equal-weight mean of the pillars present (IL replaced by IL_model). Max diff from the original is 6e-17. RF rho 0.193, the same as the original. | none |
| 5a | Leakage guard logic | Overlap X are correct (log share, log homes inside, log homes within 1 km; D20: no industry item in V). The paired council-cluster bootstrap compares the same rows. The difference rho(full) - rho(overlap removed) is +0.25 [0.13, 0.39] for Y_hybrid and +0.21 [0.12, 0.34] for Y_measured, so these X add no extra skill to the modelled part. The logic is correct. | none |
| 5b | Circularity the guard cannot see | IL_model vs DL Spearman -0.89 (88 rows; re-derived). In the constrained setting (d = 1 month) the rebuild offset is larger than the loss in 42 of 88 rows. IL_model therefore mostly ranks councils by homes destroyed, in reverse. So Y_hybrid partly cancels DL, and this alone can explain why Y_hybrid scores lower (rho 0.19 vs 0.43; difference -0.24 [-0.40, -0.08]). The number is reported (IL_SUMMARY, MODEL_SUMMARY) but must be stated next to any Y_hybrid result. The guard removes X columns. It cannot catch overlap with a Y pillar (homes destroyed is DL1). | major (interpretation) |
| 5c | Calibration pushes duration to the edge | All 177 grid settings with M1, M2 and M3 all inside have d of 1-3 months. None have d of 12 or more. Exp 15 night lights show the area inside the fire dimmed for about 1.5-2.5 years. The pick (d = 1) is inside the prespecified bounds (1-30), so it is not a rule breach. But "the model fits the measured limits" holds only with a very short disruption that conflicts with another measured source. This should be said. The P-only calibration fails M1b and M3 on Black Summer. This is reported (IL_SUMMARY). | major (interpretation) |
| 5d | IL_model own skill | Shuffled-Y p = 0.079 (100 shuffles). IL_model RF rho 0.20 [-0.10, 0.47]: not detected. IL_model_gross RF rho 0.88 is built from X inputs (share, homes), so it is circular and must not be read as skill. It is labelled extra (D19). | minor |
| 6a | Prespec lock | PRESPEC.md sha256 = ae7ef9b9...a758a1c, the same as LOCK.txt. Lock time 23:30:31. The first code was saved at 23:35 and the first outputs at 23:36. No modelled value predates the lock. | none |
| 6b | Deviations logged | D1-D22 cover: 115 industries, Census fallback, TRA matching, 100 not 200 shuffles, SHAP added, extra gross runs, who-pays shares. Not logged: (i) the Division L dwellings effect (1c); (ii) build_il.py docstring says P = seasons 2009-2018 while D15 says 2014-2018 (the code uses season <= 2018; rows with a model start in 2014, so the result is the same). | minor |
| 7 | Every number in a write-up has a bibliography row | There is no FINDINGS or REPORT write-up yet. The only write-ups are README, PRESPEC, DEVIATIONS, LITERATURE_NOTE and INVENTORY. Numbers in DEVIATIONS and PRESPEC trace to rows: A$344,300 and 34% (E18P-09/17); all CIs (E18P-05/06/07/14/16); 56/24/11/9% of A$3.39bn (E18F-09, re-added: 1886.8 + 825.0 + 382.8 + 292.9 = 3387.5); 57 rows (E18P-02); rho +0.09 (E18F-04/E18P-18). No ACM hosts and no duplicate IDs in the part file. Rows E18L14-L17 are "searched, not used" and empty, which is acceptable. | none |

## Bottom line

**Minor issues. The computations are correct, but the Y_hybrid interpretation needs two caveats.**

- The arithmetic is correct. Multipliers, all 5 audited rows, the measured limits, and the RF results for
  Y_measured (rho 0.432) and Y_hybrid (rho 0.193) all re-derive exactly. The prespec lock is intact, and the Exp 14
  pipeline copy is untouched.
- Caveat 1. Y_hybrid scores lower than Y_measured mainly because of how the model was built. The constrained IL_model
  is driven by the rebuild offset, so it runs against DL (Spearman -0.89). Do not read "Y_hybrid is worse" as evidence
  about real indirect loss.
- Caveat 2. The model meets the measured limits only when disruption lasts 3 months or less. Night lights (Exp 15)
  show the inside of the fire dimmed for about 1.5-2.5 years. Plain wording: "a standard input-output model only fits
  the measured local limits if disruption is very short".
- Y_measured remains the primary result and is unchanged.
