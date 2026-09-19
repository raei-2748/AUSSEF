# Experiment 4B — Queensland 2022 Betterment Fund Access

**CONDITIONAL GO for data acquisition; NO-GO for modelling now.** No verified eligible unsuccessful council applications or comparable two-outcome project-need block were reconstructed. No model was fitted.

Start with [the feasibility report](FEASIBILITY_REPORT.md), then [the notebook](../experiment.ipynb). The [QRA request](QRA_DATA_REQUEST.md) is a draft and has not been sent.

| File | Purpose |
|---|---|
| published_approved_projects.csv | 221 original public asset/works rows; 194 council rows; not a certified application dataset |
| decision_evidence.csv | 13 source observations, including repeated statuses and excluded leads; not 13 applications |
| decision_universe_reconciliation.csv; repeated_project_labels.csv | Submission/project mismatch and retained repeated names |
| council_cluster_audit.csv | Award-list rows within 38 councils; application dependence remains |
| queensland_capacity_values.csv | 130 values: core QAO ratios for 39 councils plus an Ipswich pilot |
| capacity_data_availability.csv; capacity_council_coverage.csv | Coverage and comparability limits |
| temporal_availability_audit.csv | Pre-event measurement versus publication and application timing |
| project_need_quality_audit.csv; policy_and_unit_audit.csv | Need criteria, missing evidence and changing rules |
| feasibility_gates.csv | Six explicit modelling gates |
| search_and_negative_findings.csv | Search scope and unresolved/negative findings |
| source_provenance.csv/json; sources/ | Official URLs, access dates, cached files and hashes; unsuccessful access retained |
| DATA_DICTIONARY.md | Units, missingness and identifiers |
| figures/ | Descriptive audit figures, not model results |
| build_audit.py; qao_capacity_transcription.csv; case_evidence.json | One rebuild helper and source-checked manual inputs |
| validation_checks.json; frozen_existing_sha256.json | Counts and preservation of all 962 pre-existing files |

Reproduce: run the notebook from the repository root with Python containing pandas, numpy, matplotlib, beautifulsoup4, nbformat and nbclient. The notebook rebuilds only this experiment’s derived tables/figures from the cached official sources and manually checked transcriptions; it makes no network requests. The helper first checks frozen-file hashes. Original source downloads are not refreshed on rerun. The manual inputs remain auditable against the cited PDF pages.

All monetary values carry their own units/basis. Missing numeric CSV cells mean unknown/not recovered, never zero. Zero recovered eligible unsuccessful cases means search yield, not the population count. Public audit row IDs are not official IDs. The intended observation is a project application with its submission/revisions linked, not a council or disaster.

If data gates pass later, compare need-only M0 against need-plus-capacity M1 using logistic regression and a shallow tree, with whole-council holdouts and training-only preprocessing. Paired held-out log loss/Brier score, calibration and defined discrimination metrics—not training fit—would inform progress. No performance metrics exist yet. Retrospective status evidence must not become a post-decision predictor.
