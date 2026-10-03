import numpy as np, pandas as pd, common as C
from scipy.stats import spearmanr
m = C.master(); far = C.far_sets(m); A = pd.read_csv(C.ROOT + "Experiment 14/results/ANALYSIS_TABLE.csv")
comp = pd.read_csv("07_composite_rows.csv"); fp1 = pd.read_csv("03_fp1_rows.csv"); sl1 = pd.read_csv("04_sl1_rows.csv")
out = []
# i1 coverage of FP pillar parts by F
cov = pd.DataFrame({"F": m.F, "FP1": A.FP1_main.notna(), "FP2": A.FP2_main.notna(), "FP3": A.FP3_main.notna(), "FP4": A.FP4_main.notna(),
                    "SL1": A.SL1_main.notna(), "SL2": A.SL2.notna(), "SL3": A.SL3.notna(), "SL4": A.SL4.notna(), "DL1": A.homes_per_1000_v2_inferred.notna(),
                    "IL2": A.IL2.notna(), "IL3": A.IL3.notna()}).groupby("F").sum()
print("indicator coverage by fire year:\n", cov.to_string()); cov.to_csv("09_coverage_by_F.csv")
print("FP1_main post years by F:", fp1.groupby("F").FP1_main_n_post_years.agg(lambda x: x.value_counts().to_dict()).to_dict())
# SL1 rows with an incomplete post window (quarters 5-8)
r = C.rent(); last = r.quarter.max()
q0 = m.start.dt.to_period("Q"); npost = [(sum(1 for k in range(5, 9) if q + k <= last)) for q in q0]
x = pd.Series(npost)[A.SL1_main.notna().values]; print("SL1_main rows by number of post quarters observable (5-8):", x.value_counts().sort_index().to_dict(), "| rent last quarter", last)
# pillars present
print("rows by number of pillars:", comp[["mine_DL", "mine_IL", "mine_FP", "mine_SL"]].notna().sum(axis=1).value_counts().sort_index().to_dict())
one = comp[comp[["mine_DL", "mine_IL", "mine_FP", "mine_SL"]].notna().sum(axis=1) == 1]
print("one-pillar rows by season:", one.season.value_counts().to_dict())
# SL4 ties
print("SL4 values: zeros", (A.SL4 == 0).sum(), "positive", (A.SL4 > 0).sum(), "| rank given to zeros:", A.loc[A.SL4 == 0, "ind_SL4_deaths_per_100k_residents"].unique())
# duplicated council-FY rows
dup = m.duplicated(["region_id", "F"], keep=False); print("rows sharing a council-FY:", dup.sum(), "| distinct council-FY among them:", m[dup].groupby(["region_id", "F"]).ngroups,
      "| FP1 identical within council-FY:", A[dup].groupby([m.region_id[dup], m.F[dup]]).FP1_main.nunique(dropna=True).max() <= 1)
# season-wise mean of Y_v4 and of FP1 (time-horizon confounding)
print("mean Y_v4 / FP1_main / FP pillar by season:\n", A.groupby("season")[["Y_v4", "FP1_main", "FP", "DL", "SL"]].mean().round(3).to_string())
# within-season ranking skill of the RF OOF predictions (auditor's OOF)
o = pd.read_csv("08_oof_auditor.csv")
o["y_r"] = o.groupby("season").y.rank(pct=True); o["p_r"] = o.groupby("season").rf_oof.rank(pct=True)
big = o[o.season.map(o.season.value_counts()) >= 10]
print("pooled OOF rho:", round(spearmanr(o.y, o.rf_oof).correlation, 3), "| within-season rho (ranks within season, seasons n>=10):", round(spearmanr(big.y_r, big.p_r).correlation, 3))
print("per-season OOF rho:", {s: round(spearmanr(g.y, g.rf_oof).correlation, 2) for s, g in o.groupby("season") if len(g) >= 10})
print("rho between season-mean y and season-mean prediction:", round(spearmanr(o.groupby('season').y.mean(), o.groupby('season').rf_oof.mean()).correlation, 2))
# FAR councils that have master rows in F+1..F+3 (fire later inside the post window) or F-2..F-1 (pre window)
mast_by_F = m.groupby("F").region_id.apply(set).to_dict(); bs = C.burned_share_fy()
rows = []
for F, s in far.items():
    later = {x for x in s if any(x in mast_by_F.get(F + k, set()) or bs.get((x, F + k), 0) >= 0.005 for k in (1, 2, 3))}
    earlier = {x for x in s if any(x in mast_by_F.get(F + k, set()) or bs.get((x, F + k), 0) >= 0.005 for k in (-2, -1))}
    rows.append(dict(F=F, far=len(s), burned_or_row_in_F1_F3=len(later), burned_or_row_in_Fm2_Fm1=len(earlier), clean_both=len(set(s) - later - earlier)))
t = pd.DataFrame(rows); print(t.to_string()); t.to_csv("09_far_contamination.csv", index=False)
# sensitivity: FP1_main with FAR restricted to councils not burned / not master in F+1..F+3 (post window)
w = C.olg_wide(drop_pre2016_namesakes=False)
g = (w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population); g = g[np.isfinite(g) & (g > 0)].to_dict()
clean = {F: [x for x in s if not any(x in mast_by_F.get(F + k, set()) or bs.get((x, F + k), 0) >= 0.005 for k in (1, 2, 3))] for F, s in far.items()}
_, exc_clean, n_clean = C.window_excess(g, m, clean, [1, 2, 3], [-2, -1], transform=np.log)
base = A.FP1_main.values; ok = np.isfinite(exc_clean) & np.isfinite(base)
print("FP1_main, FAR also clean in F+1..F+3: n", ok.sum(), "(was", np.isfinite(base).sum(), ") | Spearman with built", round(spearmanr(exc_clean[ok], base[ok]).correlation, 3),
      "| mean shift", round(np.nanmean(exc_clean[ok] - base[ok]), 3), "| shift by F:", pd.Series(exc_clean - base).groupby(m.F).mean().round(3).to_dict(),
      "| min comparison n:", int(np.min(n_clean[np.isfinite(exc_clean)])) if ok.any() else None)
pd.DataFrame(dict(agrn=m.agrn, region_name=m.region_name, F=m.F, FP1_main_built=base, FP1_main_far_clean_post=exc_clean, n_far_clean=n_clean)).to_csv("09_fp1_far_clean_post.csv", index=False)
# sign checks: correlation of each signed rank with fire size, to see the direction convention is as declared
for col in [c for c in A.columns if c.startswith("ind_")]:
    v = A[[col, "log_homes_in_fire_per_1000"]].dropna()
    out.append(dict(indicator=col, n=len(v), spearman_with_log_homes_in_fire=round(spearmanr(v[col], v.log_homes_in_fire_per_1000).correlation, 3)))
s = pd.DataFrame(out); print(s.to_string()); s.to_csv("09_rank_vs_fire_size.csv", index=False)
