"""Independent auditor recompute of Experiment 15 point estimates from work/ arrays (no import of analysis.py)."""
import numpy as np, pandas as pd, geopandas as gpd, shapely
from pathlib import Path

EXP = Path("/Users/ray/Research/AUSSEF - Local/.claude/worktrees/quirky-lamport-88ae45/Experiment 15_nightlights")
W = EXP / "work"
DS = Path("/Users/ray/Research/AUSSEF - Local/fire_event_dataset")
px = pd.read_parquet(W / "pixels.parquet")
mo = pd.read_csv(W / "months.csv", dtype=str)
MO = np.array([int(m[:4]) * 12 + int(m[4:]) - 1 for m in mo.yyyymm])
CAL = MO % 12
rad = np.clip(np.load(W / "rad.npy").astype(float), 0, None)
ncf = np.load(W / "ncf.npy")
fh = np.load(W / "flag_hot.npy"); ff = np.load(W / "flag_fire.npy")
near = np.load(W / "near_fire_months.npz")["near"]
fp = pd.read_parquet(W / "fire_pix.parquet")
fires = gpd.read_parquet(DS / "data/cache/fires.parquet")
fires["end_use"] = fires.end.fillna(fires.start + pd.Timedelta(days=60))
valid = (ncf >= 2) & ~fh & ~ff
o = lambda y, m: y * 12 + m - 1
lab = lambda x: f"{x//12}-{x%12+1:02d}"
print("months", len(MO), lab(MO.min()), lab(MO.max()))
missing = [lab(x) for x in range(MO.min(), MO.max() + 1) if x not in set(MO)]
print("missing months:", missing)


def run(ids, label, win_list):
    f = fires[fires.event_id.isin(ids)]
    S = int(f.start.min().year * 12 + f.start.min().month - 1)
    E = int(f.end_use.max().year * 12 + f.end_use.max().month - 1)
    d = fp[fp.event_id.isin(ids)].groupby("pix").dist_m.min()
    dist = np.full(len(px), np.inf); dist[d.index] = d.values
    bc = np.nonzero((MO >= S - 24) & (MO <= S - 1))[0]
    b = np.full((len(px), 12), np.nan)
    for c in range(12):
        cc = bc[CAL[bc] == c]
        if len(cc):
            v = np.where(valid[:, cc], rad[:, cc], np.nan)
            with np.errstate(all="ignore"):
                b[:, c] = np.nanmean(v, 1)
    with np.errstate(all="ignore"):
        bmean = np.nanmean(b, 1)
    band = np.digitize(np.nan_to_num(bmean, nan=-1), [1, 3, 10, 30])
    g = f.geometry.union_all()
    cdist = shapely.distance(g, shapely.points(px.x.values, px.y.values))
    win = (MO >= S - 24) & (MO <= E + 12)
    ctrl = (cdist > 15000) & (cdist <= 150000) & ~px.gsyd.values & ~near[:, win].any(1) & ~np.isnan(bmean)
    late = near & (MO[None] > E + 12)
    ccens = np.where(late.any(1), MO[np.argmax(late, 1)], 10**9)
    cval = valid & (MO[None] < ccens[:, None])
    reb = ff & (MO[None] > E)
    tcens = np.where(reb.any(1), MO[np.argmax(reb, 1)], 10**9)
    tval = valid & (MO[None] < tcens[:, None])
    bm = b[:, CAL]
    cp = np.nonzero(ctrl)[0]
    cok = cval[cp] & ~np.isnan(bm[cp])
    R = np.full((5, len(MO)), np.nan)
    Rall = np.where(cok, rad[cp], 0).sum(0) / np.where(cok, bm[cp], 0).sum(0)
    for s in range(5):
        sel = band[cp] == s
        n = cok[sel].sum(0)
        rs = np.where(cok[sel], rad[cp][sel], 0).sum(0) / np.where(cok[sel], bm[cp][sel], 0).sum(0)
        R[s] = np.where(n >= 20, rs, Rall)
    out = {"S": lab(S), "E": lab(E), "n_ctrl": len(cp)}
    rings = {"inside": dist == 0, "ring_0_1km": (dist > 0) & (dist <= 1000), "ring_1_5km": (dist > 1000) & (dist <= 5000)}
    for rn, rmask in rings.items():
        tp = np.nonzero(rmask & ~np.isnan(bmean))[0]
        ok = tval[tp] & ~np.isnan(bm[tp]) & np.isfinite(R[band[tp]])
        A = np.where(ok, rad[tp], 0).sum(0)
        Ex = np.where(ok, bm[tp] * np.nan_to_num(R[band[tp]]), 0).sum(0)
        res = {"n": len(tp), "bands": np.bincount(band[tp], minlength=5).tolist()}
        for wn, (m0, m1) in win_list(S, E).items():
            cols = (MO >= m0) & (MO <= m1)
            with np.errstate(all="ignore"):
                res[wn] = np.log(A[cols].sum() / Ex[cols].sum())
        out[rn] = res
        if rn == "inside":
            out["inside_monthly"] = pd.Series(np.log(A / Ex), index=MO)
            out["inside_npx"] = pd.Series(ok.sum(0), index=MO)
    out["ctrl_bands"] = np.bincount(band[cp], minlength=5).tolist()
    out["ctrl_pix"] = cp
    return out


wl = lambda S, E: {"during": (S, E), "early": (E + 1, E + 6), "y1_2": (E + 7, E + 18), "y2_3": (E + 19, E + 30), "later": (E + 31, MO.max())}
SC = ["F_1e185c690e800a5cfe", "F_592a4d0267971025b2", "F_a543db8a50cf524023", "F_948a8dcc8a9b94a266"]
TA = ["F_e69a83842cba888fd5"]
win_csv = pd.read_csv(EXP / "results/windows.csv")
for name, ids in [("south_coast", SC), ("tathra", TA)]:
    r = run(ids, name, wl)
    print(f"\n== {name}: S={r['S']} E={r['E']} n_ctrl={r['n_ctrl']} ctrl bands={r['ctrl_bands']}")
    for rn in ["inside", "ring_0_1km", "ring_1_5km"]:
        print(f"  {rn} n={r[rn]['n']} bands={r[rn]['bands']}")
        for wn in ["during", "early", "y1_2", "y2_3", "later"]:
            mine = r[rn][wn]
            theirs = win_csv[(win_csv.group == name) & (win_csv.ring == rn) & (win_csv.window == wn)].D.values
            print(f"    {wn:7s} mine={mine:+.5f}  code={theirs[0] if len(theirs) else np.nan:+.5f}  pct={100*(np.exp(mine)-1):+.2f}%")
    ms = r["inside_monthly"]; npx = r["inside_npx"]
    S_o = int(r["S"][:4]) * 12 + int(r["S"][5:]) - 1; E_o = int(r["E"][:4]) * 12 + int(r["E"][5:]) - 1
    print("  during months valid px:", {lab(k): int(npx[k]) for k in range(S_o, E_o + 1) if k in npx.index})
    # recovery: 3-mo centred mean from E+1
    s = ms[ms.index >= E_o]
    sm = {k: np.nanmean([s.get(k - 1, np.nan), s.get(k, np.nan), s.get(k + 1, np.nan)]) for k in s.index}
    keys = [k for k in sorted(sm) if k >= E_o + 1]
    print("  last 14 smoothed months:", {lab(k): round(sm[k], 3) for k in keys[-14:]})
    runs = [lab(k) for i, k in enumerate(keys) if len(keys[i:i+6]) == 6 and all(sm[x] >= -0.05 for x in keys[i:i+6])]
    print("  recovery candidates:", runs[:5], "| months >= -0.05 after E:", sum(sm[k] >= -0.05 for k in keys), "of", len(keys))
    # longest run
    best = 0; cur = 0
    for k in keys:
        cur = cur + 1 if sm[k] >= -0.05 else 0; best = max(best, cur)
    print("  longest run of smoothed >= -0.05:", best)
    if name in ("south_coast", "tathra"):
        cp = r["ctrl_pix"]
        lga = gpd.read_parquet(DS / "data/cache/lga2021_nsw_geom.parquet").to_crs(3577)
        pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(px.x.values[cp], px.y.values[cp]), crs=3577)
        j = gpd.sjoin(pts, lga[["region_name", "geometry"]], how="left", predicate="within")
        print("  control pool by LGA:", j.region_name.value_counts().head(8).to_dict())
