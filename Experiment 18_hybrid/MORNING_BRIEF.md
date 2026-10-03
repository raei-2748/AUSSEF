> **Superseded 3 Oct (addendum B).** The headline "the model overstates; Black Summer A$41m-A$174m" is withdrawn.
> Those numbers came from checks the model cannot be tested on (unemployment, business counts). Checked fairly against
> measured income, Black Summer lost sales are A$411m-A$2,707m (middle A$960m, modelled). The A$3.39bn who-pays total also added two
> accounts that Exp 17 keeps separate: losses A$2.44bn (insurers 77%, households 12%) plus recovery money A$0.94bn.
> See the top of FINDINGS.md.

# Experiment 18 morning brief (3 Oct 2026)
DONE: Locked prespec, built an IO model of indirect loss (88 of 218 rows, 36 of 57 Black Summer), held it to measured limits, re-ran RF on Y_measured and Y_hybrid, SHAP, independent audit (verdict: minor issues, arithmetic exact).
1. IO model overstates with default settings: unemployment +1.02 pts per 10% (measured CI upper +0.59); accommodation/food -8.2% per 10 pp (CI lower -1.2%). Modelled vs measured.
2. Cut to fit measured limits, Black Summer gross output loss falls from A$649m to A$41m-A$174m (73-94% cut; 177 of 1,620 settings pass). Modelled, partly assumed, 36 rows.
3. Y_measured reproduced exactly: RF season-out +0.43 [+0.28, +0.55], shuffle p=0.01. Only DL (+0.73) predictable; IL +0.09, FP -0.09, SL +0.02 not detected.
4. Hybrid is worse: Y_hybrid +0.19 [+0.02, +0.33]; difference -0.24 [-0.40, -0.08]. Audit: mostly built-in, rebuild offset mirrors DL (rho -0.89). Not evidence about real loss.
5. Who pays (A$3.39bn): insurers 56%, Cwlth 24%, NSW 11%, households 9%.
DID NOT WORK: no setting fits all 5 checks; fit needs only 1-3 months disruption but night lights show 1.5-2.5 years; out-of-sample calibration fails M3; IL_model alone not detected (p=0.08); no farm losses; 130 of 218 rows have no model.
NOT a prediction win. The honest result is the bound. Pilot gate passed, but weakly.
SAFE NOVELTY: we are not aware of a measured-vs-IO check for Australian bushfires; never say "first" (about 15 sources searched).
DECIDE: (a) hybrid as dollar-bound only, not a pillar (recommended); (b) test "homes lost, not businesses closed" reading of night lights; (c) frame as "bounding IO with measured data".
Files: Experiment 18_hybrid/FINDINGS.md, MORNING_BRIEF.md, audit/AUDIT.md, figures/. Nothing committed.
