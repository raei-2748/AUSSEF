# Experiment 9: Bowen's modelling pipeline on the composite Y

Random forest + baselines + variable importance on the main Y = DL + IL + FP + SL (equal weights),
council x fire panel (218 rows), validated by leaving out one whole fire season at a time.
Built so better IL / FP / SL indicators (from the Experiment 8 mechanism work) can be added later by editing
**one file: `config.toml`**.

Read in this order: `FINDINGS.md` (results, plain English) -> `PRESPEC.md` (rules fixed before fitting) -> `LOCK.txt`.

## Run order
```
python3 data.py          # builds results/ANALYSIS_TABLE.csv (all Y versions + X) from config.toml; checks it reproduces the workbook
python3 lock.py          # ONLY when starting a new pre-registered version: hashes PRESPEC.md, config.toml, inputs
python3 run_models.py    # CV, metrics, permutation importance, shuffled-Y check (~35 min; --skip-shuffle for ~4 min)
uv run --no-project --python 3.13 --with shap --with scikit-learn==1.7.2 --with pandas --with statsmodels \
    --with openpyxl --with pyarrow python shap_step.py     # SHAP in a throwaway env
python3 make_figures.py  # figures/*.png
```

## Files
| File | What it is |
|---|---|
| `config.toml` | pillar indicators (source, columns, sign), weights, X sets, model settings |
| `data.py` | builds Y versions and X from the config; reproduction check vs workbook |
| `run_models.py` | RF, ridge, training mean, fire-size line, Poisson (DL); season + council CV; bootstrap CIs; permutation importance; shuffled-Y |
| `shap_step.py` | TreeSHAP importance (descriptive) |
| `make_figures.py` | figures |
| `results/METRICS.csv` | every target x X set x CV scheme x model: Spearman, MAE, CIs, RF-minus-baseline MAE |
| `results/PERM_IMPORTANCE.csv`, `SHAP_IMPORTANCE.csv` | importance tables |
| `results/OOF_PREDICTIONS.csv` | held-out predictions per row |
| `results/SHUFFLE_CHECK.csv` | shuffled-Y p-values |
| `results/WEIGHTS.json` | weights used (incl. entropy) and the reproduction check |

## Adding a new indicator later
1. Make a CSV with columns `agrn`, `region_id` and the new value(s), one row per master row.
2. Add an `[[indicator]]` block to `config.toml` (`source = "csv"`, `path`, `columns`, `sign`, `pillar`).
   A template is in the file. To replace an old indicator, delete or comment out its block.
3. Bump `[meta].version`, add a short dated addendum to `PRESPEC.md` saying what changed and why, run `lock.py`,
   then the run order above. Keep the old results folder (copy `results/` to `results_v1/`) so versions can be compared.

Inputs (read-only): master workbook (path in `../Experiment 7/build_y2.py`), `../Experiment 6/followups/dl_fill/DL_FILLED.csv`,
`../Experiment 6/results/COUNCIL_ITEMS_v2.csv`, `../fire_event_dataset/data/enrich/affected_pop_event_council.parquet`.
