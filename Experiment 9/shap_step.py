"""SHAP (TreeSHAP, mean |SHAP|) for an RF fitted on all rows, PRE+FIRE; descriptive only (PRESPEC.md).

Run (throwaway env, same scikit-learn as the main run):
  uv run --no-project --python 3.13 --with shap --with scikit-learn==1.7.2 --with pandas --with statsmodels \
      --with openpyxl python shap_step.py
"""
import numpy as np
import pandas as pd
import shap

from data import OUT
from run_models import XSETS, rf

TARGETS = ['Y_comp', 'DL', 'IL', 'FP', 'SL']

T = pd.read_csv(OUT / 'ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str})
xcols = XSETS['PRE+FIRE']
rows, vals = [], []
for t in TARGETS:
    d = T.dropna(subset=[t]).reset_index(drop=True)
    pipe = rf().fit(d[xcols], d[t])
    imp, model = pipe[0], pipe[-1]
    X = pd.DataFrame(imp.transform(d[xcols]), columns=xcols)
    sv = shap.TreeExplainer(model).shap_values(X)
    for j, c in enumerate(xcols):
        rows.append(dict(target=t, feature=c, mean_abs_shap=float(np.abs(sv[:, j]).mean()),
                         corr_value_shap=float(np.corrcoef(X[c], sv[:, j])[0, 1]) if X[c].std() > 0 else np.nan))
    if t == 'Y_comp':
        vals = pd.concat([X.add_prefix('x_'), pd.DataFrame(sv, columns=xcols).add_prefix('shap_')], axis=1)
pd.DataFrame(rows).to_csv(OUT / 'SHAP_IMPORTANCE.csv', index=False)
vals.to_csv(OUT / 'SHAP_VALUES_Y_comp.csv', index=False)
print(pd.DataFrame(rows).pivot(index='feature', columns='target', values='mean_abs_shap').round(4))
