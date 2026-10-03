import numpy as np, pandas as pd, common as C
m = C.master(); A = pd.read_csv(C.ROOT + "Experiment 14/results/ANALYSIS_TABLE.csv"); b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
assert (A.agrn.astype(str).values == m.agrn.astype(str).values).all() and (A.region_id.values == m.region_id.values).all()
fp1 = pd.read_csv("03_fp1_rows.csv"); sl1 = pd.read_csv("04_sl1_rows.csv"); fs = pd.read_csv("06_fp4_sl2_rows.csv")
dl = pd.read_csv(C.ROOT + "Experiment 6/followups/dl_fill/DL_FILLED.csv")
dl = m[["agrn", "region_id"]].astype({"agrn": str}).merge(dl.astype({"agrn": str})[["agrn", "region_id", "homes_per_1000_v2_inferred"]], how="left", on=["agrn", "region_id"])
print("DL_FILLED join: rows", len(dl), "missing", dl.homes_per_1000_v2_inferred.isna().sum(),
      "| max diff vs ANALYSIS_TABLE:", (dl.homes_per_1000_v2_inferred - A.homes_per_1000_v2_inferred).abs().max(),
      "| NaN mismatch:", (dl.homes_per_1000_v2_inferred.isna() != A.homes_per_1000_v2_inferred.isna()).sum())
pop = pd.to_numeric(m.X_council_council_population_pre, errors="coerce"); d = pd.to_numeric(m.SL_deaths_sourced, errors="coerce")
ind = pd.DataFrame({
    "DL1": (dl.homes_per_1000_v2_inferred.values, +1, "DL", "built (DL_FILLED)"),
    "IL2": (b.IL2.values, -1, "IL", "built (not re-derived)"), "IL3": (b.IL3.values, -1, "IL", "built (not re-derived)"),
    "FP1": (fp1.FP1_main_namesakes_kept_mine.values, +1, "FP", "auditor"), "FP2": (b.FP2_main.values, +1, "FP", "built (not re-derived)"),
    "FP3": (b.FP3_main.values, +1, "FP", "built (not re-derived)"), "FP4": (fs.FP4_main_mine.values, -1, "FP", "auditor"),
    "SL1": (sl1.SL1_main_mine.values, +1, "SL", "auditor"), "SL2": (fs.SL2_mine.values, +1, "SL", "auditor"),
    "SL3": (b.SL3.values, +1, "SL", "built (not re-derived)"), "SL4": ((d / pop * 1e5).values, +1, "SL", "auditor")}.items(), columns=["k", "v"]) if False else None
spec = {"DL1": (dl.homes_per_1000_v2_inferred.values, +1, "DL", "ind_DL1_homes_destroyed_per_1000_dwellings"),
        "IL2": (b.IL2.values, -1, "IL", "ind_IL2_income_affected_sa2_excess_far"), "IL3": (b.IL3.values, -1, "IL", "ind_IL3_business_affected_sa2_excess_far"),
        "FP1": (fp1.FP1_main_namesakes_kept_mine.values, +1, "FP", "ind_FP1_grants_per_resident_rise_excess_far"),
        "FP2": (b.FP2_main.values, +1, "FP", "ind_FP2_fire_grant_share_jump_excess_far"), "FP3": (b.FP3_main.values, +1, "FP", "ind_FP3_capex_share_jump_excess_far"),
        "FP4": (fs.FP4_main_mine.values, -1, "FP", "ind_FP4_cash_cover_drawdown_excess_far"),
        "SL1": (sl1.SL1_main_mine.values, +1, "SL", "ind_SL1_rent_rise_year2_excess_far"), "SL2": (fs.SL2_mine.values, +1, "SL", "ind_SL2_domestic_violence_rise_excess_far"),
        "SL3": (b.SL3.values, +1, "SL", "ind_SL3_rebuild_gap_trend_adjusted"), "SL4": ((d / pop * 1e5).values, +1, "SL", "ind_SL4_deaths_per_100k_residents")}
R = pd.DataFrame(index=A.index); res = []
for k, (v, sgn, p, col) in spec.items():
    R[k] = pd.Series(sgn * v.astype(float)).rank(pct=True)
    diff = (R[k] - A[col]).abs(); nm = (R[k].isna() != A[col].isna()).sum()
    res.append(dict(item=k, n=int(R[k].notna().sum()), n_built=int(A[col].notna().sum()), nan_mismatch=int(nm), max_abs_diff=diff.max()))
P = pd.DataFrame({p: R[[k for k in spec if spec[k][2] == p]].mean(axis=1) for p in ["DL", "IL", "FP", "SL"]})
Y = P.mean(axis=1)
for p in ["DL", "IL", "FP", "SL"]:
    res.append(dict(item="pillar " + p, n=int(P[p].notna().sum()), n_built=int(A[p].notna().sum()), nan_mismatch=int((P[p].isna() != A[p].isna()).sum()), max_abs_diff=(P[p] - A[p]).abs().max()))
res.append(dict(item="Y_v4", n=int(Y.notna().sum()), n_built=int(A.Y_v4.notna().sum()), nan_mismatch=int((Y.isna() != A.Y_v4.isna()).sum()), max_abs_diff=(Y - A.Y_v4).abs().max()))
s = pd.DataFrame(res); print(s.to_string()); s.to_csv("07_composite_summary.csv", index=False)
out = A[["agrn", "region_name", "season"]].copy(); out = pd.concat([out, R.add_prefix("rank_"), P.add_prefix("mine_"), A[["DL", "IL", "FP", "SL", "Y_v4"]].add_prefix("built_")], axis=1); out["mine_Y_v4"] = Y
out.to_csv("07_composite_rows.csv", index=False)
print("pillars present per row:", P.notna().sum(axis=1).value_counts().sort_index().to_dict())
print("Y_v4 describe:", Y.describe().round(3).to_dict())
print("10 example rows:\n", out[["agrn", "region_name", "mine_Y_v4", "built_Y_v4"]].iloc[::22].to_string())
# Spearman of Y_v4 with log homes in fire per 1000 (descriptive)
print("Spearman Y_v4 vs log_homes_in_fire_per_1000:", round(Y.corr(A.log_homes_in_fire_per_1000, method="spearman"), 3))
