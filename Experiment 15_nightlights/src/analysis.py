"""Experiment 15, step 2: light gap D inside / near fire outlines vs matched unburned settled pixels (PRESPEC.md).

Run AFTER LOCK.txt. Reads radiance (avg_rade9) for the settled pixels only (cached in work/rad.npy).
Writes results/*.csv and results/*.json; figures come from src/figures.py.
Run: uv run --no-project --with geopandas --with pyarrow --with rasterio --with scipy python src/analysis.py
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

from prep import DS, VIIRS, WORK

HERE = Path(__file__).resolve().parents[1]
import os
SYNTH = bool(os.environ.get("SYNTH"))  # code test on synthetic lights with a planted drop (no real radiance read)
RES = HERE / ("results_synth" if SYNTH else "results")
NBOOT = 1000
BLOCK_M = 3000
BANDS = [0, 1, 3, 10, 30, np.inf]
MIN_CTRL = 20
RNG = np.random.default_rng(20261002)

SOUTH_COAST = ["F_1e185c690e800a5cfe", "F_592a4d0267971025b2", "F_a543db8a50cf524023", "F_948a8dcc8a9b94a266"]
TATHRA = ["F_e69a83842cba888fd5"]
COUNCILS = ["Shoalhaven", "Eurobodalla", "Bega Valley"]


def ordm(ts):
    ts = pd.Timestamp(ts)
    return ts.year * 12 + ts.month - 1


def ord_label(o):
    return f"{o // 12}-{o % 12 + 1:02d}"


# ---------------------------------------------------------------- load
px = pd.read_parquet(WORK / "pixels.parquet")
mo = pd.read_csv(WORK / "months.csv", dtype=str)
MO = np.array([int(m[:4]) * 12 + int(m[4:]) - 1 for m in mo.yyyymm])   # month ordinals of the 132 columns
CAL = MO % 12
ncf = np.load(WORK / "ncf.npy")
fp = pd.read_parquet(WORK / "fire_pix.parquet")
fires = gpd.read_parquet(DS / "data/cache/fires.parquet")
fires["end_use"] = fires.end.fillna(fires.start + pd.Timedelta(days=60))
hl = pd.read_parquet(DS / "data/enrich/house_loss.parquet")
dwin = pd.read_parquet(WORK / "fire_dwell_in.parquet")
near = np.load(WORK / "near_fire_months.npz")["near"]


def radiance():
    p = WORK / "rad.npy"
    if p.exists():
        return np.load(p)
    rad = np.zeros(ncf.shape, dtype=np.float32)
    for j, m in enumerate(mo.yyyymm):
        with rasterio.open(VIIRS / f"{m}_avg_rade9.tif") as s:
            rad[:, j] = s.read(1)[px.row.values, px.col.values]
    np.save(p, rad)
    return rad


def synthetic():
    """Lognormal pixel levels x season x noise; South Coast inside pixels lose 30% in 2020-04..2020-09."""
    rng = np.random.default_rng(int(os.environ.get("SYNTH_SEED", 1)))
    lvl = np.exp(rng.normal(1.0, 1.2, len(px)))[:, None]
    season = 1 + 0.1 * np.cos(2 * np.pi * CAL / 12)[None, :]
    _, binv = np.unique(np.floor(px.x.values / 3000) * 1e6 + np.floor(px.y.values / 3000), return_inverse=True)
    shock = rng.normal(0, 0.05, (binv.max() + 1, len(MO)))[binv]  # spatially shared block-month shocks
    r = lvl * season * np.exp(rng.normal(0, 0.15, (len(px), len(MO))) + shock)
    ins = fp[fp.event_id.isin(SOUTH_COAST) & (fp.dist_m == 0)].pix.unique()
    cols = (MO >= ordm("2020-04-01")) & (MO <= ordm("2020-09-01"))
    r[np.ix_(ins, np.nonzero(cols)[0])] *= float(os.environ.get("SYNTH_EFFECT", 0.7))
    return r.astype(np.float32)


RAD = synthetic() if SYNTH else np.clip(radiance(), 0, None)
BLOCK = (np.floor(px.x.values / BLOCK_M).astype(np.int64) * 100000 + np.floor(px.y.values / BLOCK_M).astype(np.int64))


def masks(flag_km=2, ncf_min=2):
    if SYNTH and not (WORK / "flag_hot.npy").exists():
        fh, ff = np.zeros(ncf.shape, bool), np.load(WORK / "flag_fire.npy")
    elif flag_km == 2:
        fh, ff = np.load(WORK / "flag_hot.npy"), np.load(WORK / "flag_fire.npy")
    elif SYNTH:
        fh, ff = np.zeros(ncf.shape, bool), np.load(WORK / "flag_fire.npy")
    else:
        fh, ff = np.load(WORK / "flag_hot5.npy"), np.load(WORK / "flag_fire5.npy")
    return (ncf >= ncf_min) & ~fh & ~ff, ff


# ---------------------------------------------------------------- one group
class Group:
    """Treated rings + control pool for one fire group, aggregated by 3 km block for fast bootstrap."""

    def __init__(self, ids, S=None, E=None, flag_km=2, ncf_min=2, ctrl_min_km=15, base_months=24,
                 base_override=None, extra_treated=None):
        f = fires[fires.event_id.isin(ids)]
        self.S = ordm(f.start.min()) if S is None else S
        self.E = ordm(f.end_use.max()) if E is None else E
        valid, ff = masks(flag_km, ncf_min)
        d = fp[fp.event_id.isin(ids)].groupby("pix").dist_m.min()
        dist = np.full(len(px), np.inf)
        dist[d.index.values] = d.values
        # baseline months
        b0, b1 = (self.S - base_months, self.S - 1) if base_override is None else base_override
        bcols = np.nonzero((MO >= max(b0, MO.min())) & (MO <= b1))[0]
        self.base_ok = len(bcols) >= 12
        # baseline by calendar month (valid months only)
        b = np.full((len(px), 12), np.nan)
        for c in range(12):
            cols = bcols[CAL[bcols] == c]
            if len(cols):
                v = np.where(valid[:, cols], RAD[:, cols], np.nan)
                with np.errstate(all="ignore"):
                    b[:, c] = np.nanmean(v, axis=1)
        self.b = b
        with np.errstate(all="ignore"):
            bmean = np.nanmean(b, axis=1)
        self.band = np.digitize(np.nan_to_num(bmean, nan=-1), BANDS[1:-1])
        self.bmean = bmean
        # treated rings, re-burn censoring after E
        rings = {"inside": dist == 0, "ring_0_1km": (dist > 0) & (dist <= 1000), "ring_1_5km": (dist > 1000) & (dist <= 5000)}
        if extra_treated is not None:
            rings = {"council": extra_treated & ~px.gsyd.values}
        after = (MO[None, :] > self.E) & ff
        cens = np.where(after.any(1), MO[np.argmax(after, 1)], 10 ** 9)
        tvalid = valid & (MO[None, :] < cens[:, None])
        # controls
        # distance to G for every pixel (fire_pix only stores <= 15 km; bug fix after lock: S3 needs > 15 km)
        import shapely
        g = f.to_crs(3577).geometry.union_all()
        cdist = shapely.distance(g, shapely.points(px.x.values, px.y.values))
        ctrl = (cdist > ctrl_min_km * 1000) & (cdist <= 150000) & ~px.gsyd.values
        win = (MO >= self.S - base_months) & (MO <= self.E + 12)
        ctrl &= ~near[:, win].any(1)
        if extra_treated is not None:
            ctrl &= ~extra_treated
        latenear = near & (MO[None, :] > self.E + 12)
        ccens = np.where(latenear.any(1), MO[np.argmax(latenear, 1)], 10 ** 9)
        cvalid = valid & (MO[None, :] < ccens[:, None])
        self.ctrl_pix = np.nonzero(ctrl)[0]
        self.rings = {k: np.nonzero(v & ~np.isnan(bmean))[0] for k, v in rings.items()}
        self.ctrl_pix = self.ctrl_pix[~np.isnan(bmean[self.ctrl_pix])]
        bm = b[:, CAL]  # baseline for each pixel-month
        self.bm = bm
        self.tvalid, self.cvalid = tvalid, cvalid
        # control aggregates by block x band x month
        self.cb_ids, cinv = np.unique(BLOCK[self.ctrl_pix], return_inverse=True)
        self.C = self._agg(self.ctrl_pix, cinv, len(self.cb_ids), cvalid)
        ok = cvalid[self.ctrl_pix] & ~np.isnan(bm[self.ctrl_pix])
        self.cr = np.where(ok, RAD[self.ctrl_pix], 0.0)
        self.cbm = np.where(ok, bm[self.ctrl_pix], 0.0)
        self.cn = ok.astype(float)
        self.cblock = cinv
        self.cband = self.band[self.ctrl_pix]
        # treated aggregates: all rings share one block index (joint resampling)
        allt = np.unique(np.concatenate(list(self.rings.values()))) if self.rings else np.array([], int)
        self.tb_ids, _ = np.unique(BLOCK[allt], return_inverse=True)
        self.T = {}
        for k, pix in self.rings.items():
            inv = np.searchsorted(self.tb_ids, BLOCK[pix])
            self.T[k] = self._agg(pix, inv, len(self.tb_ids), tvalid)

    def _agg(self, pix, inv, nb, valid):
        ok = valid[pix] & ~np.isnan(self.bm[pix])
        r = np.where(ok, RAD[pix], 0.0)
        bb = np.where(ok, self.bm[pix], 0.0)
        out = np.zeros((3, nb, len(BANDS) - 1, len(MO)))
        for s in range(len(BANDS) - 1):
            sel = self.band[pix] == s
            for a, arr in enumerate([r, bb, ok.astype(float)]):
                np.add.at(out[a, :, s, :], inv[sel], arr[sel])
        return out  # [sum r, sum b, n valid] x block x band x month

    def ratio(self, wc):
        """Control change R[band, month] for control block weights wc."""
        Cr, Cb, Cn = (np.tensordot(wc, self.C[a], axes=(0, 0)) for a in range(3))
        with np.errstate(all="ignore"):
            R = Cr / Cb
            Rall = Cr.sum(0) / Cb.sum(0)
        return np.where((Cn >= MIN_CTRL) & np.isfinite(R), R, Rall[None, :])  # NaN where no control baseline

    def sums(self, ring, wt, R):
        """Bug fix after lock: band-months with no usable control ratio (NaN) are dropped for the treated side too."""
        ok = np.isfinite(R)
        A = np.tensordot(wt, self.T[ring][0], axes=(0, 0))
        B = np.tensordot(wt, self.T[ring][1], axes=(0, 0))
        N = np.tensordot(wt, self.T[ring][2], axes=(0, 0))
        return (np.where(ok, A, 0).sum(0), np.where(ok, B * np.nan_to_num(R), 0).sum(0),
                np.where(ok, N, 0).sum(0))

    def null_draws(self, ring, n=NBOOT):
        """Amendment 1: random placebo "pseudo-towns". Each draw starts at a random control pixel and takes the nearest
        control pixels until the treated ring's count in every brightness band is matched; this compact pseudo-group
        is compared with the remaining controls by exactly the same formula. Returns per-draw monthly sums (A, E)."""
        quota = np.bincount(self.band[self.rings[ring]], minlength=len(BANDS) - 1)
        cxy = np.c_[px.x.values[self.ctrl_pix], px.y.values[self.ctrl_pix]]
        tree = cKDTree(cxy)
        kmax = min(len(self.ctrl_pix), max(50 * int(quota.sum()), 2000))
        Ctot = [np.zeros((len(BANDS) - 1, len(MO))) for _ in range(3)]
        for s in range(len(BANDS) - 1):
            sel = self.cband == s
            for a, arr in enumerate([self.cr, self.cbm, self.cn]):
                Ctot[a][s] = arr[sel].sum(0)
        As, Es = np.zeros((n, len(MO))), np.zeros((n, len(MO)))
        for i in range(n):
            need = quota.copy()
            pick = []
            _, order = tree.query(cxy[RNG.integers(len(cxy))], k=kmax)  # pseudo-town: nearest pixels to a random seed
            for q in np.atleast_1d(order):
                sb = self.cband[q]
                if need[sb] > 0:
                    pick.append(q)
                    need[sb] -= 1
                    if need.sum() == 0:
                        break
            pick = np.array(pick, int)
            pb = self.cband[pick]
            sub = [np.zeros((len(BANDS) - 1, len(MO))) for _ in range(3)]
            for a, arr in enumerate([self.cr, self.cbm, self.cn]):
                np.add.at(sub[a], pb, arr[pick])
            Cr, Cb, Cn = (Ctot[a] - sub[a] for a in range(3))
            with np.errstate(all="ignore"):
                R = Cr / Cb
                Rall = Cr.sum(0) / Cb.sum(0)
            R = np.where((Cn >= MIN_CTRL) & np.isfinite(R), R, Rall[None, :])
            ok = np.isfinite(R)
            As[i] = np.where(ok, sub[0], 0).sum(0)
            Es[i] = np.where(ok, sub[1] * np.nan_to_num(R), 0).sum(0)
        return As, Es

    def windows(self):
        S, E = self.S, self.E
        return {"placebo_pre": (S - 12, S - 1), "during": (S, E), "early": (E + 1, E + 6), "y1_2": (E + 7, E + 18),
                "y2_3": (E + 19, E + 30), "later": (E + 31, MO.max())}

    def run(self, nboot=NBOOT):
        ones_c, ones_t = np.ones(len(self.cb_ids)), np.ones(len(self.tb_ids))
        R0 = self.ratio(ones_c)
        out = {"monthly": {}, "window": {}}
        draws_t = RNG.multinomial(len(self.tb_ids), np.ones(len(self.tb_ids)) / len(self.tb_ids), nboot) if len(self.tb_ids) else None
        draws_c = RNG.multinomial(len(self.cb_ids), np.ones(len(self.cb_ids)) / len(self.cb_ids), nboot)
        Rb = [self.ratio(w) for w in draws_c]
        for ring in self.T:
            a0, e0, n0 = self.sums(ring, ones_t, R0)
            boots = [self.sums(ring, draws_t[i], Rb[i])[:2] for i in range(nboot)]
            with np.errstate(all="ignore"):
                Dm = np.log(a0 / e0)
                Db = np.array([np.log(a / e) for a, e in boots])
            NA, NE = self.null_draws(ring, nboot)
            self.pool_share = getattr(self, "pool_share", {})
            self.pool_share[ring] = len(self.rings[ring]) / max(len(self.ctrl_pix), 1)
            with np.errstate(all="ignore"):
                Nm = np.log(NA / NE)
            out["monthly"][ring] = pd.DataFrame({"ord": MO, "month": [ord_label(o) for o in MO], "D": Dm,
                                                 "lo": Dm - np.nanpercentile(Nm, 97.5, 0),
                                                 "hi": Dm - np.nanpercentile(Nm, 2.5, 0),
                                                 "boot_lo": np.nanpercentile(Db, 2.5, 0),
                                                 "boot_hi": np.nanpercentile(Db, 97.5, 0),
                                                 "n_valid_px": n0, "sum_r": a0, "sum_E": e0})
            for w, (m0, m1) in self.windows().items():
                cols = (MO >= m0) & (MO <= m1)
                if w == "placebo_pre" or not cols.any():
                    continue
                with np.errstate(all="ignore"):
                    d = np.log(a0[cols].sum() / e0[cols].sum())
                    db = np.array([np.log(a[cols].sum() / e[cols].sum()) for a, e in boots])
                    nd = np.log(NA[:, cols].sum(1) / NE[:, cols].sum(1))
                out["window"][(ring, w)] = dict(D=d, lo=d - np.nanpercentile(nd, 97.5), hi=d - np.nanpercentile(nd, 2.5),
                                                boot_lo=np.nanpercentile(db, 2.5), boot_hi=np.nanpercentile(db, 97.5),
                                                months=int(cols.sum()), px_months=float(n0[cols].sum()),
                                                pixels=len(self.rings[ring]), _draws=db, _null=nd)
        return out


def placebo_pre(ids, **kw):
    """C1: months S-12..S-1 against a baseline built from S-24..S-13 only (interval from random placebo groups)."""
    f = fires[fires.event_id.isin(ids)]
    S = ordm(f.start.min())
    g = Group(ids, S=S, E=ordm(f.end_use.max()), base_override=(S - 24, S - 13), **kw)
    res = {}
    R0 = g.ratio(np.ones(len(g.cb_ids)))
    cols = (MO >= S - 12) & (MO <= S - 1)
    for ring in g.T:
        a, e, _ = g.sums(ring, np.ones(len(g.tb_ids)), R0)
        d = np.log(a[cols].sum() / e[cols].sum())
        NA, NE = g.null_draws(ring)
        with np.errstate(all="ignore"):
            nd = np.log(NA[:, cols].sum(1) / NE[:, cols].sum(1))
        res[ring] = dict(D=d, lo=d - np.nanpercentile(nd, 97.5), hi=d - np.nanpercentile(nd, 2.5))
    return res


def random_placebo(g, ring="inside", n=1000):
    """Draw control blocks holding ~as many pixels as the ring; their Early D against the remaining controls."""
    npx = len(g.rings[ring])
    cpx_per_block = np.bincount(np.searchsorted(g.cb_ids, BLOCK[g.ctrl_pix]), minlength=len(g.cb_ids))
    m0, m1 = g.windows()["early"]
    cols = (MO >= m0) & (MO <= m1)
    out = []
    for _ in range(n):
        order = RNG.permutation(len(g.cb_ids))
        k = np.searchsorted(np.cumsum(cpx_per_block[order]), npx) + 1
        pick = np.zeros(len(g.cb_ids))
        pick[order[:k]] = 1
        R = g.ratio(1 - pick)
        A = np.tensordot(pick, g.C[0], axes=(0, 0))
        B = np.tensordot(pick, g.C[1], axes=(0, 0))
        ok = np.isfinite(R)
        out.append(np.log(np.where(ok, A, 0)[:, cols].sum() / np.where(ok, B * np.nan_to_num(R), 0)[:, cols].sum()))
    return np.array(out)


def recovery_month(mdf, E):
    """Q3: first month k >= E+1 whose 3-month centred mean of D is >= -0.05 and stays so for 6 months in a row."""
    s = mdf.set_index("ord").D
    s = s[s.index >= E]
    sm = {o: np.nanmean([s.get(o - 1, np.nan), s.get(o, np.nan), s.get(o + 1, np.nan)]) for o in s.index}
    keys = [o for o in sorted(sm) if o >= E + 1]
    for i, o in enumerate(keys):
        run = [sm[k] for k in keys[i:i + 6]]
        if len(run) == 6 and all(v >= -0.05 for v in run):
            return ord_label(o)
    return None


def tidy(name, res):
    rows = []
    for (ring, w), v in res["window"].items():
        rows.append(dict(group=name, ring=ring, window=w, **{k: v[k] for k in v if not k.startswith("_")}))
    return rows


def main():
    RES.mkdir(exist_ok=True)
    summary, windows = {}, []
    for name, ids in [("south_coast", SOUTH_COAST), ("tathra", TATHRA)]:
        g = Group(ids)
        res = g.run()
        windows += tidy(name, res)
        for ring, mdf in res["monthly"].items():
            mdf.to_csv(RES / f"monthly_{name}_{ring}.csv", index=False)
        e = res["window"]
        grad = e[("inside", "early")]["_null"] - e[("ring_1_5km", "early")]["_null"]  # independent pseudo-groups
        pre = placebo_pre(ids)
        rp = random_placebo(g)
        summary[name] = dict(
            S=ord_label(g.S), E=ord_label(g.E), n_ctrl_px=len(g.ctrl_pix), n_ctrl_blocks=len(g.cb_ids),
            n_treated_blocks=len(g.tb_ids), rings={k: len(v) for k, v in g.rings.items()},
            ring_size_as_share_of_control_pool=g.pool_share,
            dwell_inside=float(px.dwell.values[g.rings["inside"]].sum()),
            recovery_inside=recovery_month(res["monthly"]["inside"], g.E),
            gradient_early=dict(D=(gd := e[("inside", "early")]["D"] - e[("ring_1_5km", "early")]["D"]),
                                lo=float(gd - np.nanpercentile(grad, 97.5)), hi=float(gd - np.nanpercentile(grad, 2.5))),
            placebo_pre=pre, random_placebo_early_inside=dict(
                share_of_random_groups_below_real=float(np.mean(rp < e[("inside", "early")]["D"])),
                p2_5=float(np.percentile(rp, 2.5)), p97_5=float(np.percentile(rp, 97.5))))
        # per-pixel maps: Early and Later window ratio with full controls
        R0 = g.ratio(np.ones(len(g.cb_ids)))
        rows = []
        for ring, pix in g.rings.items():
            for w in ["early", "y1_2", "later"]:
                m0, m1 = g.windows()[w]
                cols = (MO >= m0) & (MO <= m1)
                Ep = g.bm[pix][:, cols] * R0[g.band[pix]][:, cols]
                ok = g.tvalid[pix][:, cols] & np.isfinite(Ep)
                a = np.where(ok, RAD[pix][:, cols], 0).sum(1)
                ee = np.where(ok, Ep, 0).sum(1)
                with np.errstate(all="ignore"):
                    rows.append(pd.DataFrame(dict(pix=pix, ring=ring, window=w, sum_r=a, sum_E=ee, D=np.log(a / ee),
                                                  lon=px.lon.values[pix], lat=px.lat.values[pix],
                                                  dwell=px.dwell.values[pix], base_mean=g.bmean[pix])))
        pd.concat(rows).to_csv(RES / f"pixels_{name}.csv", index=False)

    # Q6: council-wide (dilution demo) with South Coast timing and controls
    lga = gpd.read_parquet(DS / "data/cache/lga2021_nsw_geom.parquet").to_crs(3577)
    import shapely
    pts = shapely.points(px.x.values, px.y.values)
    inl = np.zeros(len(px), bool)
    for geom in lga[lga.region_name.isin(COUNCILS)].geometry:
        inl |= shapely.contains(geom, pts)
    gc = Group(SOUTH_COAST, extra_treated=inl)
    rc = gc.run()
    windows += tidy("south_coast_councils", rc)
    rc["monthly"]["council"].to_csv(RES / "monthly_south_coast_councils.csv", index=False)
    summary["south_coast_councils"] = dict(pixels=int(len(gc.rings["council"])), n_ctrl_px=len(gc.ctrl_pix),
                                           note="group larger than the control pool: pseudo-town interval invalid, "
                                                "use boot_lo/boot_hi (deviation, see FINDINGS)",
                                           dwell=float(px.dwell.values[gc.rings["council"]].sum()))

    # Q5: pooled dose across fires
    ins = fp[fp.dist_m == 0].groupby("event_id").size()
    pool = fires[fires.event_id.isin(ins[ins >= 5].index) & (fires.start <= "2024-06-30")]
    prow = []
    for r in pool.itertuples():
        g = Group([r.event_id])
        if not g.base_ok or len(g.rings["inside"]) == 0:
            prow.append(dict(event_id=r.event_id, event_name=r.event_name, note="baseline < 12 months or no pixels"))
            continue
        res = g.run(nboot=300)
        e = res["window"].get(("inside", "early"))
        prow.append(dict(event_id=r.event_id, event_name=r.event_name, start=str(r.start.date()),
                         end=ord_label(g.E), pixels_inside=len(g.rings["inside"]), n_ctrl_px=len(g.ctrl_pix),
                         D_early=e["D"] if e else np.nan, lo=e["lo"] if e else np.nan, hi=e["hi"] if e else np.nan))
    pdf = pd.DataFrame(prow).merge(hl[["event_id", "DL_house_loss_raw"]], on="event_id", how="left").merge(
        dwin, on="event_id", how="left")
    pdf["homes_per_1000_dwell_in"] = 1000 * pdf.DL_house_loss_raw / pdf.dwell_in_all
    pdf.to_csv(RES / "pooled_fires.csv", index=False)
    v = pdf.dropna(subset=["D_early", "homes_per_1000_dwell_in"])
    rho = spearmanr(v.D_early, v.homes_per_1000_dwell_in).statistic if len(v) >= 3 else np.nan
    rb = []
    for _ in range(NBOOT):
        s = v.sample(len(v), replace=True, random_state=int(RNG.integers(1e9)))
        if s.D_early.nunique() > 1 and s.homes_per_1000_dwell_in.nunique() > 1:
            rb.append(spearmanr(s.D_early, s.homes_per_1000_dwell_in).statistic)
    big = pdf[(pdf.DL_house_loss_raw >= 30)].D_early.dropna()
    none = pdf[pdf.DL_house_loss_raw.isna()].D_early.dropna()
    db = [RNG.choice(big, len(big)).mean() - RNG.choice(none, len(none)).mean() for _ in range(NBOOT)]
    summary["pooled"] = dict(
        fires=int(pdf.D_early.notna().sum()), V1=dict(n=len(v), rho=rho, lo=float(np.nanpercentile(rb, 2.5)),
                                                    hi=float(np.nanpercentile(rb, 97.5))),
        V2=dict(n_big=len(big), n_none=len(none), diff=float(big.mean() - none.mean()),
                lo=float(np.percentile(db, 2.5)), hi=float(np.percentile(db, 97.5))))

    # sensitivity S1-S5 (South Coast and Tathra, inside, Early)
    sens = []
    for name, ids in [("south_coast", SOUTH_COAST), ("tathra", TATHRA)]:
        for lab, kw in [("S1_mask_5km", dict(flag_km=5)), ("S2_ncf_ge4", dict(ncf_min=4)),
                        ("S3_controls_30_150km", dict(ctrl_min_km=30)), ("S5_baseline_12m", dict(base_months=12))]:
            g = Group(ids, **kw)
            e = g.run(nboot=300)["window"][("inside", "early")]
            sens.append(dict(group=name, check=lab, D=e["D"], lo=e["lo"], hi=e["hi"]))
        g = Group(ids)
        R0 = g.ratio(np.ones(len(g.cb_ids)))
        pix = g.rings["inside"]
        m0, m1 = g.windows()["early"]
        cols = (MO >= m0) & (MO <= m1)
        Ep = g.bm[pix][:, cols] * R0[g.band[pix]][:, cols]
        ok = g.tvalid[pix][:, cols] & np.isfinite(Ep)
        a = np.where(ok, RAD[pix][:, cols], 0).sum(1)
        ee = np.where(ok, Ep, 0).sum(1)
        good = (a > 0) & (ee > 0)
        sens.append(dict(group=name, check="S4_mean_pixel_log_ratio", D=float(np.mean(np.log(a[good] / ee[good]))),
                         lo=np.nan, hi=np.nan, note=f"{good.sum()} of {len(pix)} pixels with light > 0"))
    pd.DataFrame(sens).to_csv(RES / "sensitivity.csv", index=False)
    pd.DataFrame(windows).to_csv(RES / "windows.csv", index=False)
    (RES / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float))
    print(pd.DataFrame(windows).round(3).to_string())


if __name__ == "__main__":
    main()
