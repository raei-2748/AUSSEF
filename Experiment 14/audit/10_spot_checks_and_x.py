import numpy as np, pandas as pd, common as C
m = C.master(); far = C.far_sets(m); A = pd.read_csv(C.ROOT + "Experiment 14/results/ANALYSIS_TABLE.csv")
E9 = pd.read_csv(C.ROOT + "Experiment 9/results/ANALYSIS_TABLE.csv")
X = ["H", "E2", "V", "F", "X23", "log_share", "peak_ffdi", "severity_high_extreme", "log_homes_in_fire_per_1000", "log_homes_within_1km_per_1000", "season"]
same_keys = (E9.agrn.astype(str).values == A.agrn.astype(str).values).all() and (E9.region_id.values == A.region_id.values).all()
print("Exp 9 vs Exp 14 ANALYSIS_TABLE same row order:", same_keys)
for c in X + ["Y_v3", "Y_comp"]:
    if c in E9 and c in A: print(f"  {c}: max abs diff {np.nanmax(np.abs(E9[c].values - A[c].values)):.2e}, NaN mismatch {(E9[c].isna() != A[c].isna()).sum()}")
    elif c in E9: 
        alt = "Y_v3" if c == "Y_comp" else None
        if alt: print(f"  Exp9 {c} vs Exp14 {alt}: max abs diff {np.nanmax(np.abs(E9[c].values - A[alt].values)):.2e}")
w = C.olg_wide(drop_pre2016_namesakes=False); r = C.rent()
g = (w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population)
cc = w.cash_expense_cover_ratio_months
lr = r.set_index(["region_id", "quarter"]).median_rent
lines = []
pick = A.index[::22][:10]
for i in pick:
    row = m.loc[i]; F = row.F; rid = row.region_id
    lines.append(f"\n## {row.region_name} (agrn {row.agrn}), first_fire_start {row.start.date()}, F = {F} (FY {F}-{(F+1)%100:02d}), m0 {row.m0}")
    gp = {fy: g.get((rid, fy), np.nan) for fy in range(F - 2, F + 4)}
    lines.append("grants per resident A$ by fy_start: " + ", ".join(f"{k}: {v:,.0f}" for k, v in gp.items()))
    pre = [np.log(gp[k]) for k in (F - 2, F - 1) if np.isfinite(gp[k])]; post = [np.log(gp[k]) for k in (F + 1, F + 2, F + 3) if np.isfinite(gp[k])]
    own = np.mean(post) - np.mean(pre) if pre and post else np.nan
    lines.append(f"FP1 own = mean log post {np.mean(post) if post else np.nan:.4f} - mean log pre {np.mean(pre) if pre else np.nan:.4f} = {own:+.4f}; built FP1_main {A.FP1_main[i]:+.4f} -> implied FAR median {own - A.FP1_main[i]:+.4f}")
    cp = {fy: cc.get((rid, fy), np.nan) for fy in range(F - 2, F + 2)}
    lines.append("cash cover months: " + ", ".join(f"{k}: {v:.2f}" for k, v in cp.items()) + f"; built FP4_main {A.FP4_main[i]:+.3f}")
    q0 = row.start.to_period("Q")
    rq = {str(q0 + k): lr.get((rid, q0 + k), np.nan) for k in list(range(-4, 0)) + list(range(5, 9))}
    lines.append(f"rent (fire quarter {q0}) pre q-4..q-1 and post q+5..q+8: " + ", ".join(f"{k}: {v:.0f}" for k, v in rq.items()) + f"; built SL1_main {A.SL1_main[i]:+.4f}")
    lines.append(f"deaths {row.SL_deaths_sourced} / pop {row.X_council_council_population_pre} -> SL4 built {A.SL4[i]}; Y_v4 {A.Y_v4[i]:.4f} (DL {A.DL[i]:.3f}, IL {A.IL[i]:.3f}, FP {A.FP[i]:.3f}, SL {A.SL[i]:.3f})")
open("10_spot_checks.md", "w").write("# Spot checks (raw inputs printed by 10_spot_checks_and_x.py)\n" + "\n".join(lines) + "\n")
print("\n".join(lines))
