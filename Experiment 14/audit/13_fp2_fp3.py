"""FP2 fire-related grant share and FP3 capex share, all windows, auditor's own code."""
import re, numpy as np, pandas as pd, common as C
m = C.master(); far = C.far_sets(m); b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
FIRE = re.compile(r"bushfire|bush fire|rural fire|fire protection|fire service|emergency services|disaster recovery|natural disaster", re.I)
BAD = re.compile(r"storm|flood", re.I)
def load(path, items_pred, label_rule=True):
    s = pd.read_csv(path); s["fy"] = s.fy.str[:4].astype(int); s["value_aud"] = pd.to_numeric(s.value_aud, errors="coerce")
    te = s[s.item == "total_expenses"].groupby(["region_id", "fy"]).value_aud.sum()
    cap = s[s.item == "capex_ippe"].groupby(["region_id", "fy"]).value_aud.sum()
    lines = s[s.item.map(items_pred)]
    if label_rule:
        lab = lines.label.fillna("")
        lines = lines[lab.str.contains(FIRE) & ~lab.str.contains(BAD)]
    fire = lines.groupby(["region_id", "fy"]).value_aud.sum().reindex(te.index).fillna(0.0)
    has = set(lines.region_id.unique())
    return (fire / te).dropna().to_dict(), (cap / te).dropna().to_dict(), has, set(s.region_id)
dg = lambda it: it.startswith("disaster_grant_")
fire_share, fire_cap, has_lines, fire_councils = load(C.ROOT + "Experiment 10/A_fire_councils/statements_tidy.csv", dg)
variants = {}
for nm, rule in [("cmp_label_rule", True), ("cmp_no_label_rule", False)]:
    variants[nm] = load(C.ROOT + "Experiment 10/A_comparison_councils/statements_tidy.csv", lambda it: it == "bushfire_emergency_services_grant" or dg(it), rule)
print("fire councils in statements:", len(fire_councils), "| fire councils without any fire-related line:", sorted(fire_councils - has_lines))
def change(series, r, F, post):
    po = [series[(r, F + k)] for k in post if (r, F + k) in series]; pr = [series[(r, F + k)] for k in (-2, -1) if (r, F + k) in series]
    return np.mean(po) - np.mean(pr) if po and pr else np.nan
WIN = {"main": [1, 2, 3], "h0": [0], "h12": [1, 2], "h3": [3]}
rows = []; out = m[["agrn", "region_id", "region_name", "F"]].copy()
for vname, (cmp_share, cmp_cap, _, cmp_councils) in variants.items():
    for has_rule in (True, False):
        for ind, own_s, cmp_s in [("FP2", fire_share, cmp_share), ("FP3", fire_cap, cmp_cap)]:
            for w, post in WIN.items():
                vals, ncmp = [], []
                for _, row in m.iterrows():
                    r, F = row.region_id, row.F
                    if ind == "FP2" and has_rule and r in fire_councils and r not in has_lines: vals.append(np.nan); ncmp.append(np.nan); continue
                    o = change(own_s, r, F, post)
                    pool = [x for x in cmp_councils if x in set(far[F])]
                    cv = [change(cmp_s, x, F, post) for x in pool]; cv = [v for v in cv if np.isfinite(v)]
                    vals.append(o - np.median(cv) if len(cv) >= 5 and np.isfinite(o) else np.nan); ncmp.append(len(cv))
                mine = np.array(vals); col = f"{ind}_{w}"; built = b[col].values
                both = np.isfinite(mine) & np.isfinite(built); d = np.abs(mine - built)[both]
                rows.append(dict(cmp_variant=vname, has_lines_rule=has_rule, indicator=col, n_mine=int(np.isfinite(mine).sum()), n_built=int(np.isfinite(built).sum()),
                                 only_mine=int((np.isfinite(mine) & ~np.isfinite(built)).sum()), only_built=int((~np.isfinite(mine) & np.isfinite(built)).sum()),
                                 max_abs_diff=d.max() if len(d) else np.nan, n_differ=int((d > 1e-9).sum()), min_cmp=np.nanmin(ncmp) if np.isfinite(mine).any() else np.nan))
                if vname == "cmp_label_rule" and has_rule:
                    out[col + "_mine"] = mine; out[col + "_built"] = built; out[col + "_ncmp"] = ncmp
s = pd.DataFrame(rows); s.to_csv("13_fp2_fp3_summary.csv", index=False); out.to_csv("13_fp2_fp3_rows.csv", index=False)
print(s.to_string())
print("comparison councils with statements that are FAR, by F:", {F: len(variants['cmp_label_rule'][3] & set(far[F])) for F in far})
print("FP2_main rows by F:", out.groupby("F").FP2_main_built.apply(lambda x: x.notna().sum()).to_dict())
