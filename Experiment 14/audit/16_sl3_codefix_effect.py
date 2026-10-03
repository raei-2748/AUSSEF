"""Effect on Y_v4 and the primary metric of adding the 2 SL3 rows lost to ABS code changes (Inverell 2018, Armidale 2019)."""
import numpy as np, pandas as pd, common as C
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
A = pd.read_csv(C.ROOT + "Experiment 14/results/ANALYSIS_TABLE.csv"); comp = pd.read_csv("07_composite_rows.csv")
fx = pd.read_csv("14c_sl3_fixcodes_rows.csv")
def y(sl3):
    R = comp[[c for c in comp.columns if c.startswith("rank_")]].copy(); R["rank_SL3"] = pd.Series(sl3).rank(pct=True)
    P = pd.DataFrame({p: R[[c for c in R.columns if c[5:7] == p]].mean(axis=1) for p in ["DL", "IL", "FP", "SL"]}); return P.mean(axis=1)
y0 = y(A.SL3.values); y1 = y(fx.SL3_mine.values)
print("y0 equals built Y_v4:", np.abs(y0 - A.Y_v4).max() < 1e-12, "| rows changed:", int((np.abs(y1 - y0) > 1e-12).sum()), "| Spearman:", round(spearmanr(y0, y1).correlation, 4), "| max change:", round(np.abs(y1 - y0).max(), 4))
X = ["H", "E2", "V", "F", "X23", "log_share", "peak_ffdi", "severity_high_extreme", "log_homes_in_fire_per_1000", "log_homes_within_1km_per_1000"]
def metric(yv):
    Xm = A[X].values; pred = np.zeros(len(yv)); base = np.zeros(len(yv)); g = A.season.values
    for s in np.unique(g):
        te = g == s; tr = ~te; med = np.nanmedian(Xm[tr], 0)
        rf = RandomForestRegressor(n_estimators=500, max_features=0.3333, min_samples_leaf=5, random_state=20261002, n_jobs=-1)
        rf.fit(np.where(np.isnan(Xm[tr]), med, Xm[tr]), yv[tr]); pred[te] = rf.predict(np.where(np.isnan(Xm[te]), med, Xm[te])); base[te] = yv[tr].mean()
    return round(spearmanr(yv, pred).correlation, 3), round(np.mean(np.abs(yv - pred)), 4), round(np.mean(np.abs(yv - base)), 4)
print("primary (rho, MAE RF, MAE mean): built", metric(y0.values), "| with 2 SL3 rows added", metric(y1.values))
