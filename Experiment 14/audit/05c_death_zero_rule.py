"""Check the inferred-zero death rule (Experiment 6 dl_fill FINDINGS: zeros allowed when the official season total
left over after allocated rows is 1 or less) and test how much SL4 zeros matter for Y_v4 and the primary metric."""
import numpy as np, pandas as pd, common as C
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
m = C.master(); A = pd.read_csv(C.ROOT + "Experiment 14/results/ANALYSIS_TABLE.csv")
d = pd.to_numeric(m.SL_deaths_sourced, errors="coerce")
official = {2015: 1, 2016: 2, 2017: 0, 2018: 0, 2019: 25}   # numbers quoted in info_SL_deaths_sourced_ref (see 05b output)
rows = []
for F, tot in official.items():
    g = m[m.F == F]; alloc = d[g.index].sum()
    rows.append(dict(F=F, official_season_total=tot, deaths_allocated_to_panel_rows=alloc, leftover=tot - alloc,
                     zero_rows=int(m.loc[g.index, "info_SL_deaths_sourced_scope"].isin(["season_zero", "statewide_zero"]).sum()),
                     rule_ok=(tot - alloc) <= 1))
t = pd.DataFrame(rows); print(t.to_string()); t.to_csv("05c_death_zero_rule.csv", index=False)
# sensitivity: zero rows in seasons that fail the rule (leftover > 1) -> missing
bad_F = t[~t.rule_ok].F.tolist(); print("seasons failing the stated rule:", bad_F)
pop = pd.to_numeric(m.X_council_council_population_pre, errors="coerce")
sl4 = d / pop * 1e5
sl4_alt = sl4.copy(); sl4_alt[m.F.isin(bad_F) & m.info_SL_deaths_sourced_scope.isin(["season_zero", "statewide_zero"])] = np.nan
comp = pd.read_csv("07_composite_rows.csv")
def y_with(sl4v):
    R = comp[[c for c in comp.columns if c.startswith("rank_")]].copy(); R["rank_SL4"] = sl4v.rank(pct=True)
    P = pd.DataFrame({p: R[[c for c in R.columns if c[5:7] == p]].mean(axis=1) for p in ["DL", "IL", "FP", "SL"]}); return P.mean(axis=1)
y0 = y_with(sl4); y1 = y_with(sl4_alt)
print("check y0 == built Y_v4:", np.abs(y0 - A.Y_v4).max())
print("rows changed:", int((np.abs(y1 - y0) > 1e-12).sum()), "| Spearman(Y_v4, Y_v4 with bad-season zeros missing):", round(spearmanr(y0, y1).correlation, 4))
X = ["H", "E2", "V", "F", "X23", "log_share", "peak_ffdi", "severity_high_extreme", "log_homes_in_fire_per_1000", "log_homes_within_1km_per_1000"]
def metric(y):
    Xm = A[X].values; pred = np.zeros(len(y)); base = np.zeros(len(y)); g = A.season.values
    for s in np.unique(g):
        te = g == s; tr = ~te; med = np.nanmedian(Xm[tr], 0)
        rf = RandomForestRegressor(n_estimators=500, max_features=0.3333, min_samples_leaf=5, random_state=20261002, n_jobs=-1)
        rf.fit(np.where(np.isnan(Xm[tr]), med, Xm[tr]), y[tr]); pred[te] = rf.predict(np.where(np.isnan(Xm[te]), med, Xm[te])); base[te] = y[tr].mean()
    return round(spearmanr(y, pred).correlation, 3), round(np.mean(np.abs(y - pred)), 4), round(np.mean(np.abs(y - base)), 4)
print("primary metric (rho, MAE RF, MAE mean) as built:", metric(y0.values), "| with bad-season zeros missing:", metric(y1.values))
