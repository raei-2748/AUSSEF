import numpy as np, pandas as pd, common as C
m = C.master(); far = C.far_sets(m)
b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
r = C.rent(); r = r[r.median_rent > 0]
lr = {(a, q): np.log(v) for a, q, v in zip(r.region_id, r.quarter, r.median_rent)}
dupq = r.duplicated(["region_id", "quarter"]).sum()
print("rent duplicated (region_id, quarter):", dupq)
def change(rid, q0, post, min_pre=2, min_post=1):
    po = [lr[(rid, q0 + k)] for k in post if (rid, q0 + k) in lr]
    pr = [lr[(rid, q0 + k)] for k in range(-4, 0) if (rid, q0 + k) in lr]
    if len(pr) < min_pre or len(po) < min_post: return np.nan
    return np.mean(po) - np.mean(pr)
def build(post, min_post=1, pool_fn=None):
    own, exc, ncmp, cache = [], [], [], {}
    for _, row in m.iterrows():
        q0 = row.start.to_period("Q"); pool = far[row.F] if pool_fn is None else pool_fn(row)
        k = (row.F, q0, tuple(pool))
        if k not in cache:
            v = [change(x, q0, post, min_post=min_post) for x in pool]; v = [x for x in v if np.isfinite(x)]
            cache[k] = (np.median(v) if len(v) >= 5 else np.nan, len(v))
        o = change(row.region_id, q0, post, min_post=min_post); own.append(o); exc.append(o - cache[k][0]); ncmp.append(cache[k][1])
    return np.array(own), np.array(exc), np.array(ncmp)
out = m[["agrn", "region_id", "region_name", "F", "first_fire_start"]].copy(); rows = []
for name, post in [("SL1_main", range(5, 9)), ("SL1_h3", range(9, 17))]:
    for mp in [1, 2]:
        own, exc, n = build(post, min_post=mp); built = b[name].values
        both = np.isfinite(exc) & np.isfinite(built)
        d = np.abs(exc - built)[both]
        rows.append(dict(indicator=name, min_post_quarters=mp, n_mine=int(np.isfinite(exc).sum()), n_built=int(np.isfinite(built).sum()),
                         n_both=int(both.sum()), only_mine=int((np.isfinite(exc) & ~np.isfinite(built)).sum()),
                         only_built=int((~np.isfinite(exc) & np.isfinite(built)).sum()), max_abs_diff=d.max() if len(d) else np.nan,
                         n_differ=int((d > 1e-9).sum())))
        if mp == 1:
            out[name + "_mine"] = exc; out[name + "_built"] = built; out[name + "_own"] = own; out[name + "_nfar"] = n
s = pd.DataFrame(rows); print(s.to_string()); s.to_csv("04_sl1_summary.csv", index=False); out.to_csv("04_sl1_rows.csv", index=False)
d = out[(np.abs(out.SL1_main_mine - out.SL1_main_built) > 1e-9) | (out.SL1_main_mine.isna() != out.SL1_main_built.isna())]
print("differing SL1_main rows:\n", d.head(20).to_string())
print("SL1_main n by F:", out.groupby("F").SL1_main_built.apply(lambda x: x.notna().sum()).to_dict())
print("min FAR with value (rows with value):", out.loc[out.SL1_main_mine.notna(), "SL1_main_nfar"].min())
