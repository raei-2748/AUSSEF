# Bowen RF V1

Start with [REPORT.md](REPORT.md). This completed experiment preserves Ray's selected Drive workbook and uses its `master` sheet to predict continuous Y and then the class from Y.

- `snapshot/`: the unchanged workbook, its extracted master and codebook, grouping and feature audit.
- `PROTOCOL.md`: decisions fixed before model fitting.
- `results/`: held-out predictions, model comparisons, classes, sensitivities, tuning, checks and charts.
- `results/RF_MODEL.joblib`: portable sklearn model fitted only on the older training cohort.
- `prepare.py`, `run_experiment.py`, `validate_and_report.py`: extraction, fitting and independent verification/reporting.
- `requirements.txt`: package versions used in the isolated experiment runtime.

The completed V1 runner refuses to overwrite its results. Reproduce in a fresh folder, remove copied `results/` in that fresh reproduction only, install `requirements.txt` in an isolated environment, then run the three scripts in order. The source path can be supplied to `prepare.py --source /absolute/path/to/workbook.xlsx`.

The verdict is predictive gain not established. No canonical database or original workbook was modified. The exported model is an experimental benchmark, not a deployed forecast.
