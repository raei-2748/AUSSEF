# Experiment 4 — Infrastructure Budget Deviation Audit

Development of Experiment 3 for the revised NSW quarterly/annual budget question. **CONDITIONAL GO for targeted data collection; NO-GO for modelling now.** The older funding-access Experiment 4 and Queensland 4B are preserved as separate studies.

Start with [AUDIT_REPORT.md](AUDIT_REPORT.md) or [the audit notebook](../experiment.ipynb).

- `readiness_matrix.csv`: usable evidence, cleaning and remaining gaps.
- `minimum_additional_data.csv`: prioritised collection fields.
- `annual_deviation_examples.csv`: four broad capital cash-flow examples, not ordinary-infrastructure outcomes.
- `quarterly_revision_examples.csv`: six Lismore lines from one snapshot; no complete quarterly series.
- `project_deferral_audit.csv`: narratives, with missing timing/identity fields preserved.
- `nsw_disaster_timing_audit.csv` and `candidate_pre_event_capacity_links.csv`: conservative joins; event-wide dates, not certified local exposure/public availability.
- `capacity_coverage_by_year.csv`, `pilot_capacity_contrast.csv`: measurement coverage and lack of interaction support.
- `repository_inventory.csv`, `csv_schema_inventory.csv`, `dataset_profile.csv`, `field_quality_profile.csv`, `cached_document_search.csv`: inspectable audit evidence.
- `validation_checks.json` and `frozen_existing_sha256.json`: preservation and checks.
- `audit.py`: one reproducible audit helper; no modelling, network calls or changes to old files.

Run the notebook with pandas, numpy, nbformat and IPython available. It reads local cached files, checks all pre-existing file hashes, and regenerates only this folder’s audit CSVs. Blank values remain missing. Fiscal and event joins are candidates, not an estimation-ready panel. Source URLs/pages remain in the example tables and the preserved E3 source/evidence registers.
