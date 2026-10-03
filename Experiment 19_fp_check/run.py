"""Experiment 19 (PRESPEC.md, LOCK.txt). python3 run.py -> results/METRICS.csv, results/BRIDGE.csv"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent / "Experiment 18_hybrid/pipeline"
sys.path.insert(0, str(PIPE))
import data as D, run_models as R  # noqa: E402

T = pd.read_csv(PIPE / "results/ANALYSIS_TABLE_exp14_copy.csv", dtype={"agrn": str, "region_id": str})
P = D.pillars(T, "main")
assert np.nanmax(np.abs(D.composite(P) - T.Y_v4)) < 1e-12
h3 = D.pillars(T, "h3")
T["FP1_main_r"] = P["FP1_grants_per_resident_rise_excess_far"].to_numpy()
T["FP1_h3_r"] = h3["FP1_grants_per_resident_rise_excess_far"].to_numpy()
T["FP4_main_r"] = P["FP4_cash_cover_drawdown_excess_far"].to_numpy()
T["FP_grants"] = P[["FP1_grants_per_resident_rise_excess_far", "FP2_fire_grant_share_jump_excess_far"]].mean(axis=1).to_numpy()
Q = P.copy(); Q["DL"] = np.nan
T["Y_noDL"] = D.composite(Q).to_numpy()

targets = ["Y_v4", "FP", "FP1_main_r", "FP1_h3_r", "FP4_main_r", "FP_grants", "Y_noDL"]
rng = np.random.default_rng(R.SEED)
xcols = R.XSETS["PRE+FIRE"]
rows, bridge = [], []
for t in targets:
    d = T.dropna(subset=[t]).reset_index(drop=True)
    Pr, _ = R.cv_run(d, t, xcols, "season", models=("mean", "ridge", "size_line", "rf"))
    for r in R.metrics(d, t, Pr, rng):
        rows.append(dict(target=t, **r))
    ok = T[t].notna() & T.log_homes_in_fire_per_1000.notna()
    bridge.append(dict(target=t, n=int(ok.sum()), rho_homes_in_fire=spearmanr(T.loc[ok, t], T.loc[ok, "log_homes_in_fire_per_1000"])[0]))
    print(t, "done", flush=True)
M = pd.DataFrame(rows); M.to_csv(HERE / "results/METRICS.csv", index=False)
B = pd.DataFrame(bridge); B.to_csv(HERE / "results/BRIDGE.csv", index=False)
e18 = pd.read_csv(HERE.parent / "Experiment 18_hybrid/results/MODEL_METRICS.csv")
for t in ["Y_v4", "FP"]:
    a = M[(M.target == t) & (M.model == "rf")].rho.iloc[0]
    b = e18[(e18.target == t) & (e18.xset == "PRE+FIRE") & (e18.cv == "season") & (e18.model == "rf")].rho.iloc[0]
    print(f"repro {t}: {a:.6f} vs E18 {b:.6f}")
print(M[M.model.isin(["rf", "size_line"])][["target", "model", "n", "seasons", "rho", "rho_lo", "rho_hi"]].round(3).to_string(index=False))
print(B.round(3).to_string(index=False))
