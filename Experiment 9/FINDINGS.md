# Experiment 9 findings: Bowen's pipeline on the composite Y

2 Oct 2026. Rules fixed in advance in PRESPEC.md (hash in LOCK.txt). All numbers: out-of-fold predictions, the
whole fire season held out (leave-one-fire-season-out), 95% CIs from resampling councils. 218 council x fire rows,
69 councils, 9 fire seasons.

## In one paragraph
The random forest predicts the main composite Y (DL + IL + FP + SL, equal weights) for an unseen fire season a little
better than a plain average: Spearman rho +0.28 [+0.12, +0.42], shuffled-Y p = 0.005. Typical error falls from 0.117 to
0.108 on the 0-1 scale (8% smaller; difference -0.010 [-0.016, -0.003]). That passes both pre-set rules. But the
skill is small, and the pillar-by-pillar results show where it comes from. **DL is predictable** (rho +0.73), almost
entirely from "homes inside the fire". **IL is partly predictable** (rho +0.26), but mostly from council vulnerability
V, a pre-fire trait. So it reflects which kind of council it is, not how big the fire was. **FP and SL show no
detectable skill** (rho -0.01 and -0.07; shuffled-Y p = 0.50 and 0.75). This is what Experiments 6 and 7 led us to
expect. The composite Y can only become more predictable when FP and SL get indicators that actually move with the
fire (the job of the Experiment 8 mechanism work and the Experiment 10 FP data).

## 1. Primary result (pre-registered)
Y_comp, X = pre-fire + fire, random forest vs training mean, leave-one-season-out.

| | Spearman rho [95% CI] | MAE |
|---|---|---|
| Random forest | **+0.28 [+0.12, +0.42]** | 0.108 |
| Ridge (linear) | +0.19 [+0.03, +0.35] | 0.107 |
| Fire-size line (share burned only) | -0.00 [-0.15, +0.13] | 0.115 |
| Training mean | (see note) | 0.117 |

- RF minus mean MAE: -0.010 [-0.016, -0.003], so **RF beats the mean**. Shuffled-Y: real rho +0.28 vs 95th
  percentile of shuffles +0.11, p = 0.005, so **there is a real ranking signal**.
- RF does **not** beat ridge (MAE difference +0.001 [-0.005, +0.006]). A simple linear model does as well.
- Share burned alone does not rank Y_comp at all. Part of the reason: 83 of the 218 rows have no DL value, so their Y
  comes only from IL, FP and SL.
- Council-grouped check (no council in both train and test): RF rho +0.33 [+0.19, +0.46]; it beats the mean again
  (-0.013 [-0.019, -0.007]).
- Note on the mean baseline: its rho is negative (-0.38). This is a known side effect of leaving one group out: when a
  high-Y season is held out, the training average drops. It is not a real result. Judge the mean by MAE only.

## 2. Pillar by pillar (figures/fig1_skill_by_pillar.png)
Random forest, leave-one-season-out:

| Target | n | pre-fire X only | pre-fire + fire X | shuffled-Y p (pre+fire) | beats mean on MAE? |
|---|---|---|---|---|---|
| Composite Y (main) | 218 | +0.19 [-0.03, +0.34] | **+0.28 [+0.12, +0.42]** | 0.005 | yes |
| Composite Y, workbook v1 | 218 | +0.21 [-0.03, +0.38] | +0.27 [+0.11, +0.41] | - | yes |
| DL (homes destroyed, v2) | 135 | +0.17 [-0.08, +0.36] | **+0.73 [+0.65, +0.80]** | 0.010* | yes (0.148 vs 0.266) |
| IL (income, businesses) | 218 | +0.26 [+0.04, +0.41] | +0.26 [+0.07, +0.40] | 0.010* | no (-0.007 [-0.021, +0.005]) |
| FP (council finances) | 199 | -0.04 [-0.28, +0.17] | -0.01 [-0.21, +0.19] | 0.50 | no |
| SL (income support) | 213 | -0.15 [-0.39, +0.07] | -0.07 [-0.25, +0.10] | 0.75 | no |

\* With 100 shuffles, 0.010 is the smallest p possible.

What this says:
- **DL:** fire information matters a lot: rho goes from +0.17 (pre-fire only) to +0.73. Ridge does slightly better
  than RF here (rho +0.76; RF MAE higher by +0.030 [+0.013, +0.050]). Both beat Experiment 7's Poisson model
  (rho +0.64).
- **IL:** the ranking is just as good **without** any fire information (+0.26 either way), so it comes from council
  traits (mainly V), not from fire size. And it is too weak to beat the average on error size.
- **FP, SL:** no detectable predictive skill. CIs rule out rho above about +0.2.

## 3. Which X variables matter (figures/fig2, fig3)
Permutation importance on held-out seasons (how much error grows when one X is shuffled; pre-fire + fire X):
- **Composite Y:** homes inside the fire (+0.005 MAE [+0.003, +0.007]), then vulnerability V (+0.003), exposure E2,
  fiscal F (small but above 0). Peak FFDI is borderline. Share burned, severity, hazard H and homes within 1 km: about 0.
- **DL:** homes inside the fire dominates (+0.029 [+0.023, +0.036]); then V, E2, homes within 1 km.
- **IL:** V (+0.007) and share burned (+0.005); nothing else.
- **FP, SL:** nothing clearly above 0 (SL: E2 small, +0.003 [+0.001, +0.005]).

SHAP (RF fitted on all rows; in-sample, descriptive) gives the same top variables: homes inside the fire for DL and
the composite, V and share burned for IL, and a flat, noisy profile for FP and SL.

## 4. Sensitivity
- **Weights.** More weight on DL means more predictable: class note 35/25/30/10, rho +0.45 [+0.29, +0.58]; deck
  30/25/25/20, +0.34 [+0.18, +0.48]. Entropy weights put 41% on SL and 11% on FP; rho drops to +0.15
  [-0.01, +0.29] and no longer beats the mean. Weight choice therefore changes the answer. This is a reason to fix the
  weights for conceptual reasons, not by which ones predict best.
- **Leave one pillar out (equal weights on the rest):** without DL, rho +0.22 [+0.05, +0.37]; without IL, +0.06
  [-0.09, +0.21]; without FP, +0.23; without SL, +0.44 [+0.27, +0.58]. The composite's skill comes from DL and IL.
  FP and SL add noise.
- **Complete rows only** (all four pillars, n = 128): RF +0.37 [+0.19, +0.51], ridge +0.49 [+0.34, +0.61].
- **Workbook Y_v1** (original DL, 90 rows) behaves almost the same as Y_comp.

## 5. Honest limits
- Small data: 218 rows but only 9 fire seasons; one season (2014) has a single row. 2019-20 (Black Summer) is 57 rows.
- All Y pillars are percentile ranks across the 218 rows. They are computed once on all rows (they use no X).
- The improvement over the average for the composite Y is real but small (0.009 on a 0-1 scale). It is mostly the
  DL pillar coming through.
- "Homes inside the fire" is measured after the fire starts. So the pre-fire + fire model is a rapid post-fire
  estimate, not a forecast. The pre-fire-only model is the forecast, and for the composite Y its skill is not
  clearly above 0 (+0.19 [-0.03, +0.34]; shuffled p = 0.02, but the CI includes 0, so it fails the pre-set rule).
- FP and SL: "no detectable predictive skill above about rho +0.2", not "no effect".

## 6. What to do next (inside Bowen's framework)
1. Keep this pipeline as the fixed test bench. When Experiment 8/10 produce fire-matched IL, FP or SL indicators,
   add them in `config.toml` (README explains how; council x financial-year FP tables are already supported) and
   re-run. The test is simple: does that pillar's row in the table in section 2 move away from 0?
2. Report the composite and the pillars together, always. The composite alone hides that only DL is driving it.
3. Weights: pick and justify them before seeing results (equal is the default), and show the weight sensitivity.

## Deviations from PRESPEC.md
1. After locking, a commented-out template for council x financial-year indicators (for the Experiment 10 FP data) was
   added to `config.toml`, and `data.py` gained a matching `council_fy` source type. Comments and unused code only. The
   rebuilt analysis table is byte-identical, but the config.toml hash no longer matches LOCK.txt (new hash 6078852106...).
2. Permutation importance was rewritten to make one prediction call per fold (all 30 repeats stacked) instead of one
   per repeat. The method is the same; it is only faster.
3. Added `SOURCES.csv` (project bibliography format); a coordinator session copied it to
   `bibliography/parts/exp9_rf_pipeline.csv`.
