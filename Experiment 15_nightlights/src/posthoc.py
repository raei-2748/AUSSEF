"""Experiment 15 POST-HOC checks (NOT pre-registered; added after seeing results and after the independent audit).

Writes:
  results/posthoc_v2_pool200.txt         V2 without fires whose control pool has < 200 pixels
  results/control_pool_lga.csv           which councils the comparison pixels sit in (South Coast, Tathra)
  results/posthoc_recovery_checks.txt    Q3 recovery rule with Feb 2025 left out; Later-window gap by brightness
  results/windows.csv, pooled_fires.csv  + column ci_valid (pseudo-town interval judged unusable when the group is
                                         > 25% of the control pool, the pool has < 200 pixels, or the interval
                                         does not contain its own estimate; council rows use the block bootstrap)
Run from src/: uv run --no-project --with geopandas --with pyarrow --with rasterio --with scipy --with pyogrio python posthoc.py
"""
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

import analysis as A

RES = A.RES
out = ["POST-HOC (not in prespec). Added after the independent audit, 2 Oct 2026.", ""]

# 1. V2 restricted to fires with >= 200 control pixels
d = pd.read_csv(RES / "pooled_fires.csv")
k = d[d.n_ctrl_px >= 200]
big, none = k[k.DL_house_loss_raw >= 30].D_early.dropna(), k[k.DL_house_loss_raw.isna()].D_early.dropna()
rng = np.random.default_rng(20261002)
db = [rng.choice(big, len(big)).mean() - rng.choice(none, len(none)).mean() for _ in range(1000)]
(RES / "posthoc_v2_pool200.txt").write_text(
    "POST-HOC (not in prespec): V2 restricted to fires with >= 200 control pixels\n"
    f"n_big={len(big)} n_none={len(none)} diff={big.mean() - none.mean():.3f} "
    f"95% CI [{np.percentile(db, 2.5):.3f}, {np.percentile(db, 97.5):.3f}]\n"
    "dropped: " + ", ".join(d[d.n_ctrl_px < 200].event_name) + "\n")

# 2. where the comparison pixels are
lga = gpd.read_parquet(A.DS / "data/cache/lga2021_nsw_geom.parquet").to_crs(3577)
rows = []
groups = {}
for name, ids in [("south_coast", A.SOUTH_COAST), ("tathra", A.TATHRA)]:
    g = A.Group(ids)
    groups[name] = g
    pts = gpd.GeoDataFrame(geometry=shapely.points(A.px.x.values[g.ctrl_pix], A.px.y.values[g.ctrl_pix]), crs=3577)
    j = gpd.sjoin(pts, lga, how="left")
    rows.append(j.region_name.fillna("(outside NSW LGAs)").value_counts().rename("control_pixels").reset_index()
                .assign(group=name))
pd.concat(rows)[["group", "region_name", "control_pixels"]].to_csv(RES / "control_pool_lga.csv", index=False)

# 3. recovery rule without Feb 2025, and Later-window gap split by pixel brightness
for ring in ["inside", "ring_0_1km", "ring_1_5km"]:
    m = pd.read_csv(RES / f"monthly_south_coast_{ring}.csv")
    feb = m.loc[m.month == "2025-02", "D"].values[0]
    jan = m.loc[m.month == "2025-01", "D"].values[0]
    out.append(f"South Coast {ring}: D 2025-01 = {jan:+.3f}, 2025-02 = {feb:+.3f} (jump {feb - jan:+.3f})")
c = pd.read_csv(RES / "monthly_south_coast_councils.csv")
out.append(f"Council group: D 2025-01 = {c.loc[c.month == '2025-01', 'D'].values[0]:+.3f}, "
           f"2025-02 = {c.loc[c.month == '2025-02', 'D'].values[0]:+.3f}")
m = pd.read_csv(RES / "monthly_south_coast_inside.csv")
E = groups["south_coast"].E
out.append(f"Q3 rule with all months: {A.recovery_month(m, E)}")
out.append(f"Q3 rule with 2025-02 left out: {A.recovery_month(m[m.month != '2025-02'], E)}")
s = m.set_index("ord").D
sm = {o: np.nanmean([s.get(o - 1, np.nan), s.get(o, np.nan), s.get(o + 1, np.nan)]) for o in s.index if o > E}
ok = [o for o in sorted(sm) if sm[o] >= -0.05]
out.append(f"Months after E with 3-month mean >= -0.05: {len(ok)} of {len(sm)}")
p = pd.read_csv(RES / "pixels_south_coast.csv")
for ring in ["inside", "ring_0_1km"]:
    for w in ["early", "later"]:
        q = p[(p.ring == ring) & (p.window == w)]
        for lab, sel in [("baseline >= 1 nW", q.base_mean >= 1), ("baseline < 1 nW", q.base_mean < 1)]:
            qq = q[sel]
            out.append(f"South Coast {ring} {w} {lab}: {len(qq)} px, gap "
                       f"{100 * (qq.sum_r.sum() / qq.sum_E.sum() - 1):+.1f}% (ratio of sums, no interval)")
(RES / "posthoc_recovery_checks.txt").write_text("\n".join(out) + "\n")

# 4. interval validity flags
summ = json.loads((RES / "summary.json").read_text())
w = pd.read_csv(RES / "windows.csv")
pool = {"south_coast": summ["south_coast"]["n_ctrl_px"], "tathra": summ["tathra"]["n_ctrl_px"],
        "south_coast_councils": summ["south_coast_councils"]["n_ctrl_px"]}
share = w.pixels / w.group.map(pool)
inside = (w.lo <= w.D) & (w.D <= w.hi)
w["ci_valid"] = (share <= 0.25) & (w.group.map(pool) >= 200) & inside & (w.group != "south_coast_councils")
w["ci_note"] = np.where(w.group == "south_coast_councils", "use boot_lo/boot_hi (group larger than control pool)",
                        np.where(share > 0.25, "ring > 25% of control pool: pseudo-town interval mixes in regional "
                                 "differences", np.where(w.D.isna(), "no usable pixel-months (all masked)",
                                          np.where(~inside, "interval does not contain its estimate", ""))))
w.to_csv(RES / "windows.csv", index=False)
d["ci_valid"] = (d.n_ctrl_px >= 200) & (d.lo <= d.D_early) & (d.D_early <= d.hi)
d.to_csv(RES / "pooled_fires.csv", index=False)
print("\n".join(out))
print((RES / "posthoc_v2_pool200.txt").read_text())
print(w[~w.ci_valid][["group", "ring", "window", "ci_note"]].to_string())
