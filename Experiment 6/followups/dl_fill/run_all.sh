#!/bin/sh
# Reproduces everything in FINDINGS.md from the read-only workbook and Experiment 6 results (about 3 minutes).
# Needs: pandas, numpy, scipy, openpyxl. Writes only inside this folder. Never touches the workbook or data/aussef.duckdb.
set -e
cd "$(dirname "$0")"
mkdir -p out
python3 01_profile_missing.py > out/01_profile.log
python3 02_row_listing.py
python3 03_make_fill_table.py > out/03_fill_table.log
python3 04_build_filled.py > out/04_build_filled.log
python3 05_rerun_check.py > out/05_rerun.log
python3 06_sensitivity.py > out/06_sensitivity.log
python3 check_sources.py
