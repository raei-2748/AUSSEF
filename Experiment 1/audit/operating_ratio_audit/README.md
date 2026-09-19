# Operating-ratio movement audit


## Purpose and frozen inputs

Explains existing forecast failures without fitting models. Source CSV, notebooks 01/02 and all previous outputs remain hash-verified unchanged. Run notebook 03 from the repository root with pandas, numpy, matplotlib, openpyxl, xlrd, nbformat and a Jupyter kernel. Cached official sources make reruns offline. No imputation, outcome correction or data append is performed.


## Selection and coverage

```csv
selection,n
all held-out,370
priority union,97
top20 change,20
top20 persistence,20
top20 ridge,20
>10 pp,94
>20 pp,12
```


All 97 priority cases receive original OLG aggregate screening and an explicit case explanation. 9 have documentary contributors; the remaining 88 are unresolved. Documentary review is selective, not a census of every council report. See source manifests for failed downloads; Wollongong was read through browser PDF extraction after direct download returned 403.


## Temporal structure and errors

Prior year t−1 plus exposure t predicts target t+1. Selection concerns two-year changes; adjacent annual changes are included. Financial year is labelled by start year. Errors are prediction minus actual; absolute errors are in percentage points. No new MAE/RMSE/R² or model selection is needed for this explanation audit. Existing negative results remain frozen.


## Files

large_fiscal_movements.csv is the full selected union, including large ridge errors without >10pp change. all_frozen_forecast_cases.csv preserves all rows. forecast_error_case_audit.csv adds explanations. accounting_component_audit.csv retains units, original cells and audited pages. documentary_evidence.csv records contributor-level provenance. disaster_fiscal_links.csv separates declarations, scope-limited mapped burn, unknown damage and documented transactions. Candidate counts overlap and are not failures solved. Historical inventory is a feasibility screen. Figures are descriptive and accounting bridges are not causal decompositions.


## A–F verdict

**A.** Documented contributors include operating-grant levels and advance timing, depreciation, expense reversals and maintenance/capital classification. Carrathool’s before-capital result improves $10.487m, including $7.586m more operating grants. This is not an exact OP causal decomposition.

**B.** 9 of 97 selected cases have documented contributors; 88 remain unexplained after aggregate screening. Evidence is mixed fiscal/accounting. We cannot establish that either dominates the full case set.

**C.** Yes, for a subset. Carrathool reports storm/flood operating grants; Liverpool Plains describes disaster road funding; Murray River reports flood operating/capital support and $3.992m counter-disaster/reactive maintenance. General FAG advances must not be relabelled disaster grants. No quantified disaster causal share or maintenance crowd-out has been established.

**D.** Potentially: published lagged revenue/expense composition, adopted rates and budgets, and dated approved grant schedules. Availability before each forecast has not yet been certified. Target-year realised receipts, costs and late restatements would leak the outcome; improvement remains unproven.

**E.** Candidate common coverage starts in 2012–13: potentially five additional distinct years before 2017–18 for comparable continuing councils. Mergers, partial periods, units and changing definitions prevent a certified all-council append. More years are not independent shocks by default.

**F.** CONDITIONAL GO for a bounded data-feasibility stage: certify a small dated predictor panel and an older continuing-council subset first. Only then consider rerunning the same simple forward tests. Retain NO-GO for claims of useful fiscal prediction now. A disaster-finance mechanism study is promising, but this audit alone does not establish crowd-out; do not pivot to a causal claim.


## Limitations

Case selection on errors prevents representative mechanism-frequency estimates. Most cases lack a full adjusted-ratio bridge. OLG totals include capital and may differ from adjusted performance measures. Comparative revisions are retained, not silently substituted. No prospective publication-date archive or verified damage series was assembled. Asset revaluation through equity is distinct from depreciation or charges through income. Target-year explanation is not target-year predictability. The source manifests contain duplicate downloads and later reports; download count must not be presented as independent evidence.