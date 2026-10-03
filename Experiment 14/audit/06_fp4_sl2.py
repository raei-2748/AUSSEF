import numpy as np, pandas as pd, common as C
m = C.master(); far = C.far_sets(m); b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
rows = []; out = m[["agrn", "region_id", "region_name", "F", "first_fire_start"]].copy()
def cmp(name, mine, variant):
    built = b[name].values; both = np.isfinite(mine) & np.isfinite(built); d = np.abs(mine - built)[both]
    rows.append(dict(indicator=name, variant=variant, n_mine=int(np.isfinite(mine).sum()), n_built=int(np.isfinite(built).sum()), n_both=int(both.sum()),
                     only_mine=int((np.isfinite(mine) & ~np.isfinite(built)).sum()), only_built=int((~np.isfinite(mine) & np.isfinite(built)).sum()),
                     max_abs_diff=d.max() if len(d) else np.nan, n_differ=int((d > 1e-9).sum())))
# FP4 cash cover
for variant, drop in [("namesakes_kept", False), ("namesakes_dropped", True)]:
    w = C.olg_wide(drop_pre2016_namesakes=drop)
    s = w.cash_expense_cover_ratio_months.dropna().to_dict()
    for name, post in [("FP4_main", [0, 1]), ("FP4_h0", [0]), ("FP4_h12", [1])]:
        own, exc, n = C.window_excess(s, m, far, post, [-2, -1])
        cmp(name, exc, variant)
        if variant == "namesakes_kept": out[name + "_mine"] = exc; out[name + "_built"] = b[name]; out[name + "_own"] = own
# SL2 DV
bv = C.bocsar_dv(); c = C.councils(); k2id = dict(zip(c.key, c.region_id))
bv["region_id"] = bv.lga.map(lambda s: k2id.get(C.norm(s))); bv = bv.dropna(subset=["region_id"])
dv = {(int(r), pd.Period(mo, "M")): v for r, mo, v in zip(bv.region_id, bv.month, bv.n)}
last = max(k[1] for k in dv)
def ch(rid, m0, min_post=12, need_full_pre=True):
    pre = [dv.get((rid, m0 + k)) for k in range(-24, 0)]; post = [dv.get((rid, m0 + k)) for k in range(6, 25) if m0 + k <= last]
    pre = [x for x in pre if x is not None]; post = [x for x in post if x is not None]
    if len(post) < min_post or (need_full_pre and len(pre) < 24) or not pre: return np.nan
    a, bb = np.mean(post), np.mean(pre)
    if a <= 0 or bb <= 0: return np.nan
    return np.log(a / bb)
for variant, minpost in [("min12post", 12)]:
    own, exc, cache = [], [], {}
    for _, row in m.iterrows():
        m0 = row.m0; k = (row.F, m0)
        if k not in cache:
            v = [ch(x, m0, minpost) for x in far[row.F]]; v = [x for x in v if np.isfinite(x)]
            cache[k] = np.median(v) if len(v) >= 5 else np.nan
        o = ch(row.region_id, m0, minpost); own.append(o); exc.append(o - cache[k])
    exc = np.array(exc); cmp("SL2", exc, variant); out["SL2_mine"] = exc; out["SL2_built"] = b["SL2"]; out["SL2_own"] = own
s = pd.DataFrame(rows); print(s.to_string()); s.to_csv("06_fp4_sl2_summary.csv", index=False); out.to_csv("06_fp4_sl2_rows.csv", index=False)
for nm in ["FP4_main", "SL2"]:
    d = out[(np.abs(out[nm + "_mine"] - out[nm + "_built"]) > 1e-9) | (out[nm + "_mine"].isna() != out[nm + "_built"].isna())]
    print(nm, "differing rows:", len(d)); print(d[["agrn", "region_name", "F", nm + "_mine", nm + "_built"]].head(15).to_string())
print("SL2 n by F:", out.groupby("F").SL2_built.apply(lambda x: x.notna().sum()).to_dict())
