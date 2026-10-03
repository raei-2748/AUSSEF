# Copied pipeline (Experiment 14, unchanged)
Files here are byte-identical copies of Experiment 14 (sha256 in COPY_SHA256.txt), copied 3 Oct 2026.
results/ANALYSIS_TABLE_exp14_copy.csv = Experiment 14/results/ANALYSIS_TABLE.csv (Y_measured = Y_v4 and its pillars).
They are not edited. Experiment 18 runs them through ../full/run_models_hybrid.py, which imports run_models.py and data.py
functions (cv_run, metrics, perm_importance, shuffle_check, pillars, composite) and adds the IL_model / Y_hybrid columns.
Because data.py sets OUT = pipeline/results, nothing is written into Experiment 14.
