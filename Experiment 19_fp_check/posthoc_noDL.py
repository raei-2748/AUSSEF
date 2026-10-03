"""POST-HOC (not in PRESPEC): what carries Y_noDL? Descriptive only."""
import sys; from pathlib import Path
import numpy as np, pandas as pd; from scipy.stats import spearmanr
HERE = Path(__file__).resolve().parent; PIPE = HERE.parent / "Experiment 18_hybrid/pipeline"
sys.path.insert(0, str(PIPE)); import data as D
T = pd.read_csv(PIPE / "results/ANALYSIS_TABLE_exp14_copy.csv", dtype={"agrn": str, "region_id": str})
P = D.pillars(T, "main"); Q = P.copy(); Q["DL"] = np.nan; y = D.composite(Q)
h = T.log_homes_in_fire_per_1000
print("n pillars present (IL,FP,SL) vs homes_in_fire:", round(spearmanr(Q[["IL","FP","SL"]].notna().sum(1), h, nan_policy="omit")[0],3))
for c in P.columns:
    ok = P[c].notna() & h.notna()
    print(f"{c[:45]:45s} n={ok.sum():3d} rho_homes={spearmanr(P.loc[ok,c], h[ok])[0]:+.3f}  rho_with_Y_noDL={spearmanr(P.loc[ok,c], y[ok])[0]:+.3f}")
