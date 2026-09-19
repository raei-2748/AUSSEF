# Experiment 4 — NSW budget-reallocation pilot
Start with [the experiment notebook](../experiment.ipynb) or [the pilot report](PILOT_REPORT.md).
Separate from the older funding-access Experiment4 and Queensland4B.

**NO-GO for causal modelling/scaling with this reconstruction. No models fitted.**
Lismore/Richmond Valley/Wagga: FY2021–22. Eurobodalla/Griffith: FY2019–20.

- budget_chains.csv: curated B0→Q1→Q2→Q3→ACTUAL category histories. Missing actuals stay blank.
- budget_stages_clean.csv / quarterly_summary.csv: reproducible long table and changes.
- annual_cash_pairs.csv: audited all-IPPE cash comparisons, separate from ordinary outcomes.
- project_revision_register.csv / year_end_followup.csv: selected projects, IDs, deferrals, scope.
- decision_dates.csv / event_timeline.csv: reporting, adoption and event dates.
- comparison_screen.csv / capacity_availability.csv: comparison and fiscal-vintage limits.
- cleaning_log.csv / reconciliation_checks.csv / coverage_and_exclusions.csv / feasibility_gates.csv: checks.
- minimum_additional_data.csv: exact request checklist; nothing sent.
- model_ready_ordinary_panel.csv: intentionally empty.
- source_index.csv / source_provenance.json / source_hashes.csv / sources/: URLs, attempts, hashes, records and image checks.
- eurobodalla_source_transcription.csv: curated public-PDF numbers; direct downloads blocked.
- measurement_contract.json / variable_dictionary.csv: definitions.

Nominal AUD unless explicitly labelled millions. Annual accounts' AUD thousands converted ×1000.
Lismore unit/year conflicts remain quarantined. Griffith “Ordinary Services” is a fund name.
Quarter end is not approval/publication date. Rows share council/event dependence.
Run [`../code/reproduce.py`](../code/reproduce.py) with Python, pandas, numpy and matplotlib, or run the short notebook.
The helper rebuilds checks and descriptive outputs offline; it does not download or fit models.
Existing experiments and NSW Data Panel.csv are read-only and hash-verified.
