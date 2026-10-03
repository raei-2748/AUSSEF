# Experiment 18: hybrid IL pillar (run order and file index)
Rules: PRESPEC.md (locked, LOCK.txt). Deviations: DEVIATIONS.md. Sources: bibliography/parts/exp18_hybrid_2026-10-03.csv.
```
python3 src/run_pilot.py                 # pilot gate (Black Summer rows) -> pilot/
python3 full/build_il.py                 # modelled IL, 218 rows -> results/IL_MODELLED.csv, IL_CHECKS.csv, IL_GRID_*.csv, IL_SUMMARY.json (~30 s)
python3 full/run_models_hybrid.py main   # RF + baselines, Y_measured vs Y_hybrid -> results/MODEL_METRICS.csv, GUARD.csv, MATCH_EXP14.csv ... (~4 min)
python3 full/run_models_hybrid.py shuffle  # 100 shuffles x 3 targets -> results/SHUFFLE_CHECK.csv (~25 min)
uv run --no-project --with shap --with scikit-learn==1.7.2 --with pandas --with scipy --with statsmodels --with matplotlib python full/shap_measured.py
python3 full/bound_range.py              # descriptive: loss range over all settings passing the measured limits
uv run --no-project --with matplotlib --with pandas python full/figures.py   # -> figures/fig1..fig4
```
pipeline/ = byte-identical copy of the Experiment 14 pipeline (imported, never edited).
Y_measured = Y_v4 (primary). Y_hybrid and IL_model are "partly assumed" (secondary).
