"""As 14_sl3.py but the pre window needs only >= 6 months from July 2018 (no full-window gate). Arg fixcodes: map ABS codes 10130->10180 (Armidale Regional), 14200->14220 (Inverell) used in the 2018/2019 vintages."""
"""SL3 rebuild gap (trend-adjusted, FAR growth), auditor's own code."""
import glob, numpy as np, pandas as pd, common as C
m = C.master(); far = C.far_sets(m); A = pd.read_csv(C.ROOT + "Experiment 14/results/ANALYSIS_TABLE.csv"); b = pd.read_csv(C.ROOT + "Experiment 14/inputs/v4_indicators.csv")
parts = []
for f in sorted(glob.glob(C.ROOT + "fire_event_dataset/data/raw/abs_building_approvals/BA_LGA20*.csv")):
    try: d = pd.read_csv(f, usecols=["MEASURE", "SECTOR", "WORK_TYPE", "BUILDING_TYPE", "REGION", "TIME_PERIOD", "OBS_VALUE"], dtype=str)
    except ValueError: print("unreadable (no data):", f.split("/")[-1]); continue
    d = d[(d.MEASURE == "1") & (d.SECTOR == "9") & (d.WORK_TYPE == "1") & (d.BUILDING_TYPE == "110") & d.REGION.str.match(r"^1\d{4}$")]
    d["vintage"] = f[-8:-4]; parts.append(d)
import sys
FIX = len(sys.argv) > 1 and sys.argv[1] == "fixcodes"
ba = pd.concat(parts); ba["region_id"] = ba.REGION.astype(int)
ba["region_id"] = ba.region_id.replace({10130: 10180, 14200: 14220}) if FIX else ba.region_id; ba["month"] = pd.PeriodIndex(ba.TIME_PERIOD, freq="M"); ba["n"] = pd.to_numeric(ba.OBS_VALUE, errors="coerce")
ids = set(C.councils().region_id)
print("approval region codes not in the 129 councils:", sorted(set(ba.region_id) - ids)); print("councils with no approvals:", sorted(ids - set(ba.region_id)))
print("duplicate council-months:", ba.duplicated(["region_id", "month"]).sum(), "| months:", ba.month.min(), "-", ba.month.max())
S = {(r, mo): v for r, mo, v in zip(ba.region_id, ba.month, ba.n) if np.isfinite(v)}; last = ba.month.max()
cnt = ba.groupby("region_id").month.nunique(); print("council month counts (min/max):", cnt.min(), cnt.max())
def prepost(r, m0, need_full_post):
    pre = [S[(r, m0 - k)] for k in range(1, 13) if (r, m0 - k) in S]  # >= 6 needed; data start 2018-07
    post = [S[(r, m0 + k)] for k in range(1, 25) if (r, m0 + k) in S]
    if len(pre) < 6: return None
    if need_full_post and len(post) < 24: return None
    if not post: return None
    return np.mean(pre), np.sum(post), np.mean(post), len(post)
rows = []; out = m[["agrn", "region_id", "region_name", "F", "first_fire_start"]].copy(); out["homes_v2"] = A.homes_v2
for full in (True, False):
    for use_g in (True, False):
        vals, gs, ns = [], [], []
        for _, row in m.iterrows():
            h = A.homes_v2[_]
            if not (h >= 5): vals.append(np.nan); gs.append(np.nan); ns.append(np.nan); continue
            own = prepost(row.region_id, row.m0, full)
            ratios = []
            for x in far[row.F]:
                p = prepost(x, row.m0, full)
                if p and p[0] > 0: ratios.append(p[2] / p[0])
            g = np.median(ratios) - 1 if len(ratios) >= 5 else np.nan
            if own is None or not np.isfinite(g): vals.append(np.nan); gs.append(g); ns.append(len(ratios)); continue
            pre_mean, post_sum, _, npost = own
            extra = post_sum - 24 * pre_mean * (1 + (g if use_g else 0))
            vals.append(1 - np.clip(extra / h, 0, 1)); gs.append(g); ns.append(len(ratios))
        mine = np.array(vals); built = b.SL3.values; both = np.isfinite(mine) & np.isfinite(built); d = np.abs(mine - built)[both]
        rows.append(dict(full_24_post_months=full, far_growth_adjust=use_g, n_mine=int(np.isfinite(mine).sum()), n_built=int(np.isfinite(built).sum()),
                         only_mine=int((np.isfinite(mine) & ~np.isfinite(built)).sum()), only_built=int((~np.isfinite(mine) & np.isfinite(built)).sum()),
                         max_abs_diff=d.max() if len(d) else np.nan, n_differ=int((d > 1e-9).sum())))
        if full and use_g: out["SL3_mine"] = mine; out["SL3_built"] = built; out["g_far"] = gs; out["n_far"] = ns
        if full and not use_g: out["SL3_mine_no_growth_adj"] = mine
s = pd.DataFrame(rows); print(s.to_string()); s.to_csv(("14c_sl3_fixcodes_summary.csv" if FIX else "14c_sl3_summary.csv"), index=False); out.to_csv(("14c_sl3_fixcodes_rows.csv" if FIX else "14c_sl3_rows.csv"), index=False)
v = out[out.SL3_built.notna() | out.SL3_mine.notna()]
print(v[["agrn", "region_name", "F", "homes_v2", "g_far", "n_far", "SL3_mine", "SL3_built", "SL3_mine_no_growth_adj"]].round(4).to_string())
print("rows with >=5 homes:", int((A.homes_v2 >= 5).sum()), "| of which pre-window starts before 2018-07:", int(((A.homes_v2 >= 5) & (m.m0 - 12 < pd.Period('2018-07', 'M'))).sum()))
print("SL3 = 1 (no extra rebuilding):", int((out.SL3_mine == 1).sum()), "| SL3 = 0:", int((out.SL3_mine == 0).sum()))
