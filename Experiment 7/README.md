# Experiment 7: what fires measurably do to NSW councils, and what pre-fire data can predict

Read `FINDINGS_DAY1.md`, `FINDINGS_DAY2.md`, then `FINDINGS_DAY3.md` (the new Y and X) `FINDINGS_DAY4.md` (blurry data: pooled bounds) `FINDINGS_DAY5.md` (SA2 income) `FINDINGS_DAY6.md` (unemployment) `FINDINGS_DAY7.md` (SA2 unemployment, welfare, businesses) `FINDINGS_DAY8.md` (rapid post-fire damage estimate) `FINDINGS_DAY9.md` (longer timeline) `FINDINGS_DAY10.md` (where the loss went) and `FINDINGS_DAY11.md` (council net cost). Every test was fixed in a PRESPEC file and hash-locked before it
ran (`LOCK_DAY1.txt`, `LOCK_DAY2.txt`, `LOCK_DAY2B.txt`); anything added afterwards is labelled a deviation.

| Step | Script | Output |
|---|---|---|
| 0 | `prep_panels.py` (project `.venv`) | `panels/dss_quarter.parquet` |
| 1 | `build_y2.py` (locked Day 1) | `results/CRITERION*.csv`, `ROWS_Y2.csv`, `INDICATOR_DOSE_RESPONSE.csv`, `EVENT_PROFILE*.csv` |
| 1b | `deviations_day1.py` | `results/DEV_*` (trend-robust counterfactual, average effects, noise budget) |
| 2 | `day2_consequence.py` (locked Day 2) | `results/DAY2_*`, `COUNCIL_MAP_LAYERS.csv` |
| 2b | `day2b_prospective.py` (locked Day 2B) | `results/DAY2B_*` |
| 3 | `day3_new_y_x.py` (locked Day 3) | `results/NEW_Y_X_TABLE.csv`, `DAY3_*` |
| 4 | `day4_blurry.py` (locked Day 4) | `results/DAY4_*` |
| 5 | `prep_sa2_dose.py` (uv env), `day5_sa2_income.py` (locked Day 5) | `panels/sa2_*`, `results/DAY5_*` |
| 6 | `day6_unemployment.py` (locked Day 6) | `results/DAY6_UNEMPLOYMENT.json` |
| 7 | `day7_U_unemployment.py`, `day7_W_welfare.py`, `day7_B_businesses.py` (locked Day 7, workflow) | `results/DAY7_*` |
| 8 | `day8_rapid_estimate.py` (locked Day 8), `make_fig5_rapid.py` | `results/DAY8_*`, `fig5_rapid_estimate.png` |
| 9 | `prep_sa2_dose.py fy homes_in`, `day9_long_run.py` (locked Day 9) | `results/DAY9_*`, `results/posthoc_day9/` |
| 10 | `day10_where_loss_went.py` (locked Day 10) | `results/DAY10_WHERE_LOSS_WENT.json` |
| 11 | `day11_council_net_cost.py` (locked Day 11) | `results/DAY11_NET_COST.json` |
| figs | `make_figures_day1.py`, `make_maps.py` (uv env with geopandas) | `results/fig1..fig4*.png` |

Run order: `../.venv/bin/python prep_panels.py`, then `python3` for steps 1-2b and `make_figures_day1.py`, then
`uv run --no-project --with geopandas --with shapely --with pyarrow --with matplotlib --with pandas python make_maps.py`.

Inputs are read-only: the master workbook (sha256 123423ea...ec3), `fire_event_dataset/out/fires.csv`, the dataset's
OLG, DSS and night-light panels, and Experiment 6's council layers and `DL_FILLED.csv`.
