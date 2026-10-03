# Experiment 18 deviations and interpretation choices (pilot, 3 Oct 2026)

PRESPEC.md is locked (sha256 ae7ef9b9..., checked unchanged before the pilot). Nothing here changes the checks, CIs,
grid, selection rule or gate. Code: `src/io_model.py`, `src/run_pilot.py`.

- **D1** Deviations are recorded here, not in FINDINGS.md, as the run instructions asked.
- **D2** The 2023-24 ABS IO tables have 115 industries (header columns 0101 to 9502), not 114. All 115 used.
- **D3** TRA names matched after removing "(A)"/"(C)". "Nambucca" matched to "Nambucca Valley" (renamed council,
  same area). Cootamundra-Gundagai is not matched to the TRA "Gundagai" file (a different, smaller area), so it is
  missing. Glen Innes Severn, Muswellbrook and Tenterfield have 'np' total spend, so missing. Missing stays missing.
- **D4** Three council codes are not in the 2016 Census file (Armidale Regional, Cootamundra-Gundagai, Inverell).
  For these the 2021 Census G54 is used instead of leaving the council out.
- **D5** Census G51/G54 count employed residents (place of usual residence). These are used as "council jobs". For M1
  the labour force is approximated by employed persons (unemployed not added). This makes the modelled rate change
  slightly larger, so it stays an upper bound.
- **D6** Pilot only: every model slope is computed over Black Summer rows, including M1, whose measured CI covers all
  seasons.
- **D7** FLQ details. Diagonal cells use the industry's own LQ (usual FLQ form). Type II: the household spending column
  is scaled by min(1, LQ_i x lambda) (households as buyer, LQ = 1); the labour income row by min(1, lambda / LQ_j)
  (households as seller). Household spending share = household use of each domestic product / total household uses
  (Table 2 row T3), so imports and taxes leak out.
- **D8** Business interruption: council jobs by division x national output per job of that division; each division's
  output is spread over its IO industries by national output shares.
- **D9** Timing: tourism and business losses are spread evenly over months 1..d (only the first 24 months are counted,
  so d = 30 counts 24). The rebuild offset is spread evenly over months 7-36: 6/30 of it falls in year 1 and 18/30 in
  years 1-2. "Output loss" and "job-years" are for the first 24 months. M1 uses year-1 jobs; M2 and M3 use the
  years 1-2 average per year.
- **D10** Rows with no homes destroyed count (homes_v2 missing, 5 rows) have no rebuild offset, so modelled IL is
  missing for them.
- **D11** Out-of-sample (P) calibration: M2b has no pre-COVID CI (PIA has no pre-COVID data) and is dropped. M1 uses
  the same all-seasons CI. P CIs: M1b [-0.83, +1.05], M2 [-2.7, +4.4], M3 [-6.4, +26.0] (Exp 13 ALL_RESULTS).
- **D12** Pilot reports Y_measured from Experiment 14 METRICS.csv unchanged. The re-run with the same code is left
  for the full stage.
- **D13** Dollars are nominal and mixed-year (IO 2023-24, TRA 2014-17 average, rebuild cost 2019-20). Only shares are
  used for checks and ranks; A$ totals are rough.

## Full build (3 Oct 2026)
PRESPEC.md re-checked unchanged (sha256 ae7ef9b9...). Code: `full/build_il.py`, `full/run_models_hybrid.py`,
`full/shap_measured.py`, `full/figures.py`. The Experiment 14 pipeline is copied byte-for-byte into `pipeline/`
(COPY_SHA256.txt) and imported, not edited.
- **D14** D6 ends: in the full build M1's model slope uses ALL rows with a model (its CI covers all seasons). M1b, M2,
  M2b, M3 slopes use Black Summer rows (their CIs are Black Summer). The grid pick did not change (d 1, inside, b 0.66,
  delta 0.3, Type II), (results/IL_SUMMARY.json `same_pick_as_pilot` = true).
- **D15** Out-of-sample (P) calibration in the full build uses pre-COVID rows (seasons 2014-2018 in the panel) for the
  M1b/M2/M3 slopes, matching Exp 13 sample P (the pilot had only Black Summer rows). Pick unchanged from pilot.
- **D16** Modelled IL exists for 88 of 218 rows only: 68 rows have no TRA visitor spend and 62 more have no
  homes-destroyed count (homes_v2), so no rebuild offset (D10). Missing stays missing; in Y_hybrid those rows have no
  IL pillar and the other pillars are re-weighted (PRESPEC C rule).
- **D17** Shuffled-Y checks use 100 permutations (PRESPEC E says 200) for Y_hybrid PRE+FIRE and IL_model PRE+FIRE, as
  the run instructions asked; Y_measured PRE+FIRE is also re-checked with 100. Pillar shuffle results are quoted from
  Experiment 14 (same code, same rows), not re-run. Seed for shuffles = 20261002 + 18.
- **D18** SHAP was not in the prespec (it names permutation importance). Added as asked by the run instructions:
  out-of-fold TreeSHAP from the same leave-one-season-out RFs (shap package, scikit-learn 1.7.2 via uv), measured
  targets interpreted, Y_hybrid shown only as "what the assumed model encodes". Permutation importance is also kept.
- **D19** Extra, not prespecified, labelled as such: RF runs for IL_model_gross (no rebuild offset) and Y_hybrid_gross,
  and a guard run for Y_measured and measured IL with the overlap X removed (to give the guard a measured baseline).
- **D20** Guard "overlap X" = log share burned, log homes inside fire, log homes within 1 km. V items (COUNCIL_ITEMS_v2)
  hold no industry-mix item, so V is not removed.
- **D21** Who-pays figure uses Experiment 17 results/BLACK_SUMMER_ACCOUNT.csv mid values, both accounts added by payer:
  insurers 56%, Commonwealth 24%, NSW 11%, households 9% of A$3.39bn. The shares quoted in the run instructions
  (57.5 / 25 / 12 / 6%) were not found in that file; the file values are used.
- **D22** Extra, descriptive: full/bound_range.py reports Black Summer modelled loss over every grid setting with all three primary checks inside (177 of 1,620), not only the picked one (results/IL_BOUND_RANGE.csv).

## Addendum B (3 Oct 2026, after seeing v1 results; PRESPEC_ADDENDUM_B.md, LOCK_B.txt)
- **D23** Checks restricted to measured total income (M2, M2b). Unemployment (M1, M1b) and business counts (M3) are reported as descriptive only: the IO model predicts sales and income, not firm exits or lay-offs. Made after seeing v1, prompted by Ray's question.
- **D24** Zero-employment IO industries (6700 ownership of dwellings, 6701 actual rent for housing; the addendum's "owner-occupied" label is loose, per audit B) removed from business interruption and per-job ratios (v1 audit minor issue a). `exclude_zero_jobs=False` reproduces v1 exactly.
- **D25** Headline quantity changed to gross lost sales (no rebuild offset), because rebuild spending is paid by insurers and governments already counted in Exp 17.
- **D26** Exp 16 exposure file now read from the main-checkout copy (`Experiment 16_building_exposure/`, byte-identical to the worktree file).
- **D27** Who-pays figure redrawn as Exp 17's two separate accounts (losses A$2.44bn; recovery money A$0.94bn). v1 fig2 and section 6 summed them (A$3.39bn). One account shows who carried the loss, the other who spent money afterwards, so they are not added (audit B: part of the A$266m household payments went to people who did not lose homes).
