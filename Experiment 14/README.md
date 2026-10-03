# Experiment 14: Y v4 (composite impact score, version 4 — chosen after seeing v3)

Read FINDINGS.md first, then PRESPEC.md (rules, locked before computing: LOCK_PRESPEC.txt) and DATA_CHECK.md (payment
and insurance data search). The audit is in audit/AUDIT.md.

## Run order
```
python3 build_v4_indicators.py   # -> inputs/v4_indicators.csv, inputs/FAR_SETS.csv, results/V4_BUILD_LOG.json (~3 min)
python3 data.py                  # -> results/ANALYSIS_TABLE.csv, results/COVERAGE.csv
python3 lock.py                  # -> LOCK.txt (before fitting)
python3 run_models.py            # -> results/METRICS.csv, PERM_IMPORTANCE.csv, OOF_PREDICTIONS.csv, SHUFFLE_CHECK.csv (~35 min)
python3 descriptive.py           # -> results/DESC_*.csv (not pre-registered)
python3 make_table.py            # -> results/V1_V3_V4_TABLE.csv
```
Read-only inputs come from Experiments 6, 7, 9, 10 and 12, plus fire_event_dataset/ and the master workbook.
raw/ holds the two NEMA files (downloaded with Ray's OK; bibliography E14-24, E14-25). results_prefix/ holds the
stopped pre-fix run (deviation 4).
