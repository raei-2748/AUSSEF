import numpy as np, pandas as pd, common as C
m = C.master(); far = C.far_sets(m)
b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
assert (b.agrn.values == m.agrn.values).all() and (b.region_id.values == m.region_id.values).all()
res = {}
for variant, drop in [("namesakes_dropped", True), ("namesakes_kept", False)]:
    w = C.olg_wide(drop_pre2016_namesakes=drop)
    g = (w.grants_contributions_revenue_pct / 100 * w.total_revenue_continuing_ops_aud / w.population)
    g = g[np.isfinite(g) & (g > 0)]; s = g.to_dict()
    for name, post in [("FP1_main", [1, 2, 3]), ("FP1_h0", [0]), ("FP1_h12", [1, 2]), ("FP1_h3", [3])]:
        own, exc, n = C.window_excess(s, m, far, post, [-2, -1], transform=np.log)
        res[(variant, name)] = exc
        if name == "FP1_main" and variant == "namesakes_dropped":
            res["own"] = own; res["ncmp"] = n
            npost = [sum((r, F + k) in s for k in [1, 2, 3]) for r, F in zip(m.region_id, m.F)]
            res["npost"] = npost
rows = []; out = m[["agrn", "region_id", "region_name", "F"]].copy()
for variant in ["namesakes_dropped", "namesakes_kept"]:
    for name in ["FP1_main", "FP1_h0", "FP1_h12", "FP1_h3"]:
        mine = res[(variant, name)]; built = b[name].values
        both = np.isfinite(mine) & np.isfinite(built); onlym = np.isfinite(mine) & ~np.isfinite(built); onlyb = ~np.isfinite(mine) & np.isfinite(built)
        d = np.abs(mine - built)[both]; nd = int((d > 1e-9).sum())
        rows.append(dict(variant=variant, indicator=name, n_mine=int(np.isfinite(mine).sum()), n_built=int(np.isfinite(built).sum()),
                         n_both=int(both.sum()), only_mine=int(onlym.sum()), only_built=int(onlyb.sum()),
                         max_abs_diff=float(d.max()) if len(d) else np.nan, n_rows_differ_gt_1e9=nd))
        out[f"{name}_{variant}_mine"] = mine
        if variant == "namesakes_dropped": out[f"{name}_built"] = built
out["FP1_main_own"] = res["own"]; out["FP1_main_n_far_with_value"] = res["ncmp"]; out["FP1_main_n_post_years"] = res["npost"]
s = pd.DataFrame(rows); s.to_csv("03_fp1_summary.csv", index=False); out.to_csv("03_fp1_rows.csv", index=False)
print(s.to_string())
for variant in ["namesakes_dropped", "namesakes_kept"]:
    d = out[np.abs(out[f"FP1_main_{variant}_mine"] - out["FP1_main_built"]) > 1e-9]
    print(variant, "differing FP1_main rows:\n", d[["agrn", "region_name", "F", f"FP1_main_{variant}_mine", "FP1_main_built"]].to_string())
print("post-years used (FP1_main):", pd.Series(res["npost"]).value_counts().to_dict())
print("min FAR councils with a value:", np.nanmin(res["ncmp"]))
print("FP1_main by F: n with value", out.groupby("F")["FP1_main_built"].apply(lambda x: x.notna().sum()).to_dict())
