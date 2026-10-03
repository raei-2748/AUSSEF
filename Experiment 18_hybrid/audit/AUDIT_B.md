# Audit B: Experiment 18 addendum B (income-only check, gross lost trade)

**Verdict: MINOR ISSUES.** Every number recomputes exactly; the lock and the v1 record are intact. The issues are
wording, plus weaknesses of the income check that should be stated. Independent agent, 3 Oct 2026. Helper:
`audit/audit_b_recompute.py` (prints only, writes nothing).

## Findings
1. **Lock: PASS.** sha256 of PRESPEC_ADDENDUM_B.md = `7b859b20...7761` = LOCK_B.txt. Lock 10:05:19. Later: v2_IL_GRID.csv
   and v2_IL_SUMMARY.json 10:07:10; fig5/fig6 born 10:07:56, redrawn 10:10:13. src/io_model.py changed 10:05:54 (after the
   lock, as expected: it holds the fix). File times cannot prove no v2 number was seen earlier; the addendum honestly
   says it was written after v1.
2. **v1 record: PASS.** All 30 files listed in LOCK_B.txt re-hash identically (21 results, 5 pilot, 4 figures).
3. **v1 reproduction and the fix: PASS.** `exclude_zero_jobs=False` gives Black Summer gross 649.46266267405, exactly
   IL_SUMMARY.json, and all 1,620 v1 M2 slopes in IL_GRID_B.csv (max relative gap 5e-5 = the file's 5-digit rounding).
   The summary's own check compares with a rounded 649.5, so it is weaker than it looks. ABS table 20: 6700 and 6701 have
   0 full-time and 0 part-time jobs, and they are the only such industries. The flag changes only `xk`, which feeds the
   business-interruption (BI) vector and division output-per-job (Division L: A$1.49m -> A$0.50m per job). Tourism and
   rebuild responses, baseline jobs, baseline labour income and baseline accommodation/food output are unchanged
   (labour-per-job cannot move: 6700/6701 have zero labour income). Default: direct BI 160.2 -> 151.0, gross 649.5 ->
   640.0, slope -0.9525 -> -0.9520; tourism 425.9 and offset 312.5 identical.
   **ISSUE (wording):** 6701 is "Actual rent for housing" (tenants' rent). Only 6700 is owner-occupiers' imputed rent.
4. **Independent recompute: PASS.** My own code for the BI vector, FLQ, Type I/II Leontief, time windows and slope
   (reusing only the data loaders), 36 rows each: default (6 mo, 1 km, b 0.66, delta 0.3, II) gross 639.99, slope
   -0.9520; lowest (6 mo, inside, b 0, delta 0.2, I) 271.18, -0.7152; median (9 mo, 1 km, b 1, delta 0.3, II) 959.98,
   -1.4218. All match the grid to every digit, as do labour income, direct tourism and direct BI. Hand check, Eurobodalla
   (default): tourism 356.16 x 0.5143 x 6/12 = 91.58; BI 0.0782 x 3,339.8 x 6/12 = 130.63; both match the project.
   Type II spending still reaches rent industries, but only 0.3% of gross, so it does not matter.
5. **Count and range: PASS.** From the CSV: 531 settings (slope rule = column); min 271.18, p05 411.06, median 959.98,
   p95 2,707.3, max 3,616.2; M2 only 1,069, min 39.9. Unrounded Exp 13 CIs: 533, min 258, median 960 (robust).
   **ISSUE (minor):** d=30 equals d=24 inside a 24-month window, so 44 settings count twice (without them: 487, p05 393,
   median 957, p95 2,766). "Middle 90%" is a spread over the chosen grid, not a confidence interval.
6. **Is the income-only check fair? Mostly yes, with weaknesses to state.**
   - Fair: business counts are a stock, not sales. Unemployment is blurred by firms keeping staff and by JobKeeper;
     M1b fails its placebo. Total income is the closest thing the model predicts.
   - COVID cuts both ways: Exp 13 says the Black Summer income fall "cannot be separated from COVID" (pre-COVID sign
     differs), and JobKeeper is in taxable income. The reason used to drop unemployment also weakens M2/M2b.
   - The low end rests on M2b's upper limit (-0.7) alone; M2b has no placebo and no pre-COVID estimate. Without it the
     minimum is A$40m.
   - The checks constrain *net* income (loss minus rebuild wages), not gross. Every rebuild share passes (83-93 settings
     each), so the offset is not pinned down: a big gross loss passes if a big offset cancels it.
   - Measured falls are mostly "fewer earners" (Exp 13); some may be people whose homes burned moving away, which the
     IO model does not include.
   - Unit mismatch: the model gives employees' pay lost as a % of employees' pay; the measured figure is % of *total*
     income. Exp 13's wage income (Y4, B: -1.5% [-3.4, +0.4], passes the COVID checks) is a closer match.
   - Scale: the model is council-wide, with spill-over; the measured slopes compare postcodes/SA2s within one SA4, which
     nets out spill-over to neighbours.
   - Coverage: 36 of 57 Black Summer rows (17 no visitor spend, 4 no home count), so the total is partial.
   - Gross output is not value added (supply-chain sales are counted more than once); never add it to Exp 17. Labour
     income (median A$295m, default A$203m) is the better "income lost" number.
   - **ISSUE (wording):** "lost sales, modelled, not a cost to a payer" is half right. Lost sales are a real loss, mostly
     carried by local businesses and their workers; some is made up elsewhere in NSW, and some may overlap with recovery
     money (Disaster Recovery Allowance, business grants). Say "not in Exp 17's payer accounts".
   - **ISSUE:** FINDINGS.md "How to read it" still says "shown next to the counted A$3.39bn bill" (should be A$2.44bn).
7. **fig5: PASS.** It matches v2_IL_SUMMARY.json: slopes M2/M2b -0.95, M1 +1.02, M3 -8.2; CIs as in CHECKS_B; n=531;
   411 / 960 / 2,707; default 640; grey line ends at about 270 and 3,610 (read off the pixels). Cosmetic: the "measured
   95% CI" label is clipped at the left.
8. **fig6 (redrawn): PASS; keeping the accounts separate is right.** Against Exp 17 BLACK_SUMMER_ACCOUNT.csv (mid):
   insurers 1,886.8 (77%), households 292.9 (12%), clean-up 265.0 (11%), total 2,444.6; Commonwealth 692.5 (73%), NSW
   250.3 (27%), total 942.8; 2,444.6 + 942.8 = 3,387 (the old A$3.39bn). Trivial: fig6 prints A$692m, Exp 17 prints 693.
   The two accounts answer different questions (who carried the loss; who spent money afterwards), and adding them mixes
   losses with outlays, A$266m of which went to households.
   **ISSUE (wording, D27):** "counts transfers to households twice" overstates it. Exp 17 says those payments went to
   many more people than lost homes, so they do not cancel the A$293m gap. Exp 17 still prints A$3.39bn as "gross, not a
   net cost to society"; that label is fine if anyone quotes the sum.

## Recommended wording
- Headline: "Checked against measured income in the burned areas, a standard input-output model puts sales lost in 36
  of 57 Black Summer council areas in the first two years at A$0.41bn-A$2.7bn (middle 90% of the 531 model settings
  that fit; all A$0.27bn-A$3.6bn; default A$0.64bn). Modelled gross output, carried mainly by local businesses and their
  workers (about A$0.3bn of wages), partly made up elsewhere, not in the payer accounts and never added to the A$2.44bn
  loss account. The income check cannot fully separate the fire from COVID."
- fig5 x-label: "...lost sales, 36 of 57 council areas, first 24 months, A$m (modelled gross output; not in the payer
  accounts)".
- FINDINGS: "the counted A$3.39bn bill" -> "the A$2.44bn loss account". "1 to 30 months all fit" -> add "(30 = 24 here)".
- D24: "6700 imputed rent for owner-occupiers and 6701 actual rent for housing (both 0 jobs in ABS table 20)".
- D27: "...summed them (A$3.39bn), mixing losses with later government outlays (A$266m of them paid to households)."
