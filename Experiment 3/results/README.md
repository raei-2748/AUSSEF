# Experiment 3 — disaster-induced routine maintenance crowd-out

**Measurement pilot complete; NO-GO for causal estimation from the recovered evidence.** This is not evidence of no effect.

Start with [the short notebook](../experiment.ipynb), [its browser preview](notebook_preview.html), or [the A–F measurement verdict](measurement_quality.md).

- 3 disaster-affected councils, 3 provisional comparison councils, 36 unique council-years.
- 103-council backbone; 306 candidate comparisons screened using pre-event characteristics.
- 37 curated documentary observations; **0 certified same-year routine budget/actual outcomes**.
- Capital disruption is documented, but routine-maintenance crowd-out and fiscal-capacity effects remain unidentified.
- No models were fitted. `statistical_results.csv` is intentionally absent because the modelling gate failed.

## Files

| File | Purpose |
|---|---|
| `experiment3_panel.csv` | Candidate annual panel, including explicit missing outcome/status fields and secondary aggregate maintenance |
| `routine_maintenance_evidence.csv` | Routine candidates, components and definition evidence |
| `reconstruction_expenditure_evidence.csv` | Reconstruction, funding, damage and capital evidence with separate classifications |
| `documentary_evidence.csv` | Complete curated ledger with source, raw values, units, page and eligibility reasons |
| `comparison_candidates.csv` | All 306 screened pairs, feature values, ranking and exclusions |
| `pretrend_audit.csv` | Three pre-years per selected pair; aggregate diagnostic only |
| `advance_funding_audit.csv` | Agreement/payment clocks and unresolved fields |
| `source_provenance.csv` | Official URLs, access status and hashes |
| `backbone_value_provenance.csv` | Value-level lineage to frozen V2 inputs |
| `measurement_missingness.csv` | Every unavailable primary/reconstruction field and its reason |
| `figures/` | Recovered plans versus missing actuals, aggregate pre-trends, and the unavailable post-disaster outcome |

## Reproduce

Open the notebook from within AUSSEF and run all cells. It calls `build_workflow.py`, which rebuilds only Experiment 3 tables/figures from cached evidence. It does not download new files or fit models. The pre-event screen is in `screen_comparisons.py`; curated observations are in `curated_evidence.json`. `acquire_sources.py` is the optional acquisition helper; its URL-list input is `source_provenance.json`. Dependencies: pandas, numpy, matplotlib, nbformat, nbclient, IPython, requests, beautifulsoup4 and pypdf.

Experiments 1 and 2, the original CSV and all 623 files present before this task are hash-protected. The repository index is deliberately not refreshed, because that would overwrite an existing output contrary to this request. The new workflow has no dependency on changing older files.
