"""Experiment 18: out-of-fold SHAP for Y_measured (= Y_v4) and its measured pillars, plus Y_hybrid (labelled
"what the assumed model encodes"). Same RF as the copied Experiment 14 pipeline, leave-one-fire-season-out: each
row's SHAP values come from the model that did NOT see its fire season.
Run: uv run --no-project --with shap --with scikit-learn==1.7.2 --with pandas --with scipy --with statsmodels
     --with matplotlib python full/shap_measured.py   -> results/SHAP_SUMMARY.csv, results/SHAP_OOF_Y_measured.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr

EXP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXP / "pipeline"))
import run_models as R  # noqa: E402

RES = EXP / "results"
T = pd.read_csv(RES / "HYBRID_TABLE.csv", dtype={"agrn": str, "region_id": str})
TARGETS = [("Y_v4", "measured"), ("DL", "measured"), ("IL", "measured"), ("FP", "measured"), ("SL", "measured"),
           ("Y_hybrid", "partly assumed: what the assumed model encodes")]
rows, keep = [], {}
for target, status in TARGETS:
    for xs in ("PRE", "PRE+FIRE"):
        d = T.dropna(subset=[target]).reset_index(drop=True)
        xcols = R.XSETS[xs]
        S = np.full((len(d), len(xcols)), np.nan)
        Xi = np.full((len(d), len(xcols)), np.nan)
        for tr, te in R.folds(d, "season"):
            m = R.rf().fit(d[xcols].iloc[tr], d[target].to_numpy()[tr])
            imp, forest = m.steps[0][1], m.steps[-1][1]
            xt = imp.transform(d[xcols].iloc[te])
            S[te] = shap.TreeExplainer(forest).shap_values(xt)
            Xi[te] = xt
        mabs = np.abs(S).mean(axis=0)
        gs = R.clusters(d)
        rng = np.random.default_rng(R.SEED)
        boot = []
        for _ in range(1000):
            idx = np.concatenate([gs[i] for i in rng.integers(0, len(gs), len(gs))])
            boot.append(np.abs(S[idx]).mean(axis=0))
        lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
        for j, c in enumerate(xcols):
            dirn = spearmanr(Xi[:, j], S[:, j])[0] if np.nanstd(Xi[:, j]) > 0 else np.nan
            rows.append(dict(target=target, status=status, xset=xs, feature=c, mean_abs_shap=mabs[j], lo=lo[j],
                             hi=hi[j], share_of_total=mabs[j] / mabs.sum(), direction_rho=dirn, rows=len(d)))
        if xs == "PRE+FIRE" and target == "Y_v4":
            out = d[["agrn", "region_id", "region_name", "season"]].copy()
            for j, c in enumerate(xcols):
                out[f"x_{c}"] = Xi[:, j]
                out[f"shap_{c}"] = S[:, j]
            out.to_csv(RES / "SHAP_OOF_Y_measured.csv", index=False, float_format="%.5g")
        print(target, xs, "done", flush=True)
pd.DataFrame(rows).to_csv(RES / "SHAP_SUMMARY.csv", index=False, float_format="%.5g")
