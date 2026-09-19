# Experiment 4 — funding-access feasibility audit

**NO-GO for pooled LGA × disaster Category C modelling with the supplied records.** No predictive or causal models were fitted.

Start with [the short executed notebook](../experiment.ipynb), [HTML preview](notebook_preview.html), or [the A–K report](feasibility_report.md).

The primary input is a byte-identical copy of the user's 11 August 2026 CSV in `inputs/`; its SHA-256 also matches the publisher's current download. Experiments 1–3 and 737 existing files are unchanged.

## Key outputs

- `activation_backbone_audit.csv`: fields, actual types/missingness, definitions and semantic gaps.
- `event_category_summary.csv`, `category_variation_audit.csv`: all 378 AGRNs, all/no/mixed C/D patterns.
- `candidate_risk_set.csv`: all 2,305 LGA records, raw flags and conservative statuses; marks the 739 rows in C-positive events.
- `risk_set_validation.csv`: one review for each of 30 C-positive events.
- `category_c_measure_audit.csv`: 63 program/review records, verified categories separate from unresolved mappings.
- `positive_negative_case_audit.csv`: named geographic availability and outside-scope cases; **no eligible negatives**.
- `mixed_event_case_review.csv`: raw category and individual-assistance flags for all eight mixed events.
- `need_data_availability.csv`: 16 separate need-variable audits × 30 events; no fabricated need values.
- `capacity_linkage_audit.csv`: per-value pre-onset fiscal linkage, source year, lag and quality exclusions.
- `temporal_leakage_audit.csv`, `policy_era_audit.csv`, `source_provenance.csv`: timing, rules and evidence.
- `figures/`: six descriptive figures. Zero certified coverage means evidence is unresolved, not that the underlying quantity is zero.

## Reproduce

Run the notebook from AUSSEF. It runs `build_audit.py` against the immutable copied input, read-only V2 panel and curated JSON evidence/catalogues. No network access, model fitting, imputation or previous-experiment regeneration occurs. The script checks original hashes before and after running. Cached official documents and extraction files are in `sources/`; blocked documents are identified in provenance and the report. Dependencies: Python, pandas, numpy, matplotlib, nbformat, nbclient and IPython. There is intentionally no `statistical_results.csv`.

## Interpretation

`VERIFIED_POSITIVE` means a named Category C geographic program scope was verified, **not money received**. `OUTSIDE_MEASURE_SCOPE` is not an eligible rejection. `UNKNOWN_ELIGIBILITY` and `AMBIGUOUS_RECORD` are not zero outcomes. `NOT_LGA_DECISION` and `NOT_COMPARABLE` mark unit/hazard exclusions. The reserved `VERIFIED_ELIGIBLE_NEGATIVE` status has no observations.

A full consideration/eligibility register, measure-specific decision IDs and dates, independent damage assessments and broader pre-onset capacity data are needed before revisiting modelling. Public program sources were reviewed for every C-positive event, but complete measure inventories were not certified. This audit preserves that limitation.
