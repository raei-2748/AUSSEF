import numpy as np, pandas as pd, common as C, os
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import spearmanr
A = pd.read_csv(C.ROOT + "Experiment 14/results/ANALYSIS_TABLE.csv")
mine_y = pd.read_csv("07_composite_rows.csv").mine_Y_v4.values
X = ["H", "E2", "V", "F", "X23", "log_share", "peak_ffdi", "severity_high_extreme", "log_homes_in_fire_per_1000", "log_homes_within_1km_per_1000"]
def run(y, xcols, groups):
    ok = np.isfinite(y); Xm = A.loc[ok, xcols].values; yv = y[ok]; g = groups[ok]
    pred = np.full(len(yv), np.nan); base = np.full(len(yv), np.nan)
    for s in np.unique(g):
        te = g == s; tr = ~te
        med = np.nanmedian(Xm[tr], axis=0); Xtr = np.where(np.isnan(Xm[tr]), med, Xm[tr]); Xte = np.where(np.isnan(Xm[te]), med, Xm[te])
        rf = RandomForestRegressor(n_estimators=500, max_features=0.3333, min_samples_leaf=5, random_state=20261002, n_jobs=-1).fit(Xtr, yv[tr])
        pred[te] = rf.predict(Xte); base[te] = yv[tr].mean()
    return dict(n=int(ok.sum()), rho=spearmanr(yv, pred).correlation, mae_rf=np.mean(np.abs(yv - pred)), mae_mean=np.mean(np.abs(yv - base))), yv, pred, base, g
rows = []
for lab, y in [("Y_v4 (auditor re-derived)", mine_y), ("Y_v4 (built column)", A.Y_v4.values)]:
    r, yv, pred, base, g = run(y, X, A.season.values); r["target"] = lab; r["xset"] = "PRE+FIRE"; rows.append(r)
    if lab.startswith("Y_v4 (aud"):
        # season-level and council-cluster bootstrap of MAE difference and rho (auditor's own, 2000 draws)
        rng = np.random.default_rng(1); cl = A.region_id.values[np.isfinite(y)]; uc = np.unique(cl); dd, rr = [], []
        for _ in range(2000):
            pick = rng.choice(uc, len(uc)); idx = np.concatenate([np.where(cl == u)[0] for u in pick])
            dd.append(np.mean(np.abs(yv[idx] - pred[idx])) - np.mean(np.abs(yv[idx] - base[idx]))); rr.append(spearmanr(yv[idx], pred[idx]).correlation)
        r["mae_diff_ci"] = f"[{np.percentile(dd, 2.5):+.4f}, {np.percentile(dd, 97.5):+.4f}]"; r["rho_ci"] = f"[{np.percentile(rr, 2.5):+.3f}, {np.percentile(rr, 97.5):+.3f}]"
        pd.DataFrame(dict(agrn=A.agrn, region_id=A.region_id, season=A.season, y=yv, rf_oof=pred, base_oof=base)).to_csv("08_oof_auditor.csv", index=False)
r, *_ = run(mine_y, X[:5], A.season.values); r["target"] = "Y_v4 (auditor re-derived)"; r["xset"] = "PRE"; rows.append(r)
s = pd.DataFrame(rows); print(s.to_string()); s.to_csv("08_primary_metric.csv", index=False)
p = C.ROOT + "Experiment 14/results/METRICS.csv"
if os.path.exists(p):
    M = pd.read_csv(p); print(M.columns.tolist())
    sel = M[(M.target == "Y_v4") & (M.cv == "season")]
    print(sel.to_string())
