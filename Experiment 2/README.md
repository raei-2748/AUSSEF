# Experiment 2

Start with [experiment.ipynb](experiment.ipynb) or its [browser preview](results/notebook_preview.html).

The longer history still does not consistently beat persistence for operating performance. Cash-cover gains are mixed; maintenance beats persistence more often, but the training mean has lower pooled MAE.

- `run_experiment.py` — complete original forecasting implementation; refitting is optional.
- `results/` — metrics, predictions, figures and detailed interpretation.
- `support/` — archived notebooks and organisation records.
- `data/` — V2 panels, source documents and construction audits.
- `requirements.txt` — dependencies for both experiments.

The short notebook is a results walkthrough: it reads saved CSVs and plots them. Execute the script to regenerate model outputs. The research design and saved model results have not changed during this cleanup.
