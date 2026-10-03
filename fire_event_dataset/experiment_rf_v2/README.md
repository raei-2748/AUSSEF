# Bowen RF amended benchmark V2

V2 repairs the three issues documented in the V1 audit. Read `REPORT.md` for results and limits, `PROTOCOL.md` for the fixed amendment, and `SOURCE_ELIGIBILITY_REGISTRY.csv` for every predictor's timing rule.

The original continuous Y, classes derived from continuous predictions, rows, groups and outer splits are preserved. V1 remains beside this folder. V2 follows inspection of V1 and reuses its holdout; it is not fresh independent confirmation.

Use the versions in `requirements.txt`. In a fresh reproduction copy, run `check_repairs.py`, `run_experiment.py`, `validate_and_report.py`, keeping the preserved V1 sibling folder for comparison and hash verification. The runner refuses to overwrite completed results. No source workbook or canonical database is edited.
