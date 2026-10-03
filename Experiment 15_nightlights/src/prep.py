"""Experiment 15, step 1 (OUTCOME-FREE): pixel grid, homes per pixel, fire distances, fire masks, cloud-free counts.

Reads NO radiance (avg_rade9) values. Only the n_cf (cloud-free count) files, Census 2016 mesh blocks, fire outlines
and the cached DEA hotspots.

Writes work/:
  pixels.parquet     settled pixels (>= MIN_DWELL dwellings, Census 2016): pix, row, col, lon, lat, x, y (EPSG:3577),
                     dwell, gsyd (majority of the pixel's dwellings in Greater Sydney GCCSA)
  fire_pix.parquet   event_id, pix, dist_m (0 = pixel centre inside the outline), for every pixel within 15 km
  months.csv         the 132 available months (yyyymm) and product version
  ncf.npy            uint16 [n_pix, n_months] cloud-free counts
  flag_hot.npy       bool [n_pix, n_months] a cached hotspot within FLAG_M of the pixel centre that month
  flag_fire.npy      bool [n_pix, n_months] a mapped outline within FLAG_M was burning that month
  near_fire_months.npz  per pixel, months when a mapped outline within CTRL_M was burning (for control exclusion)
Run: uv run --no-project --with geopandas --with pyarrow --with rasterio --with scipy --with pyogrio python src/prep.py
"""
import glob
import json
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import rasterio
import shapely
from pyproj import Transformer
from rasterio import features
from scipy.spatial import cKDTree

ROOT = Path("/Users/ray/Research/AUSSEF - Local")
HERE = Path(__file__).resolve().parents[1]
WORK = HERE / "work"
DS = ROOT / "fire_event_dataset"
OD = Path.home() / ("Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/"
                    "Fire Dataset Build Inputs (only needed to rebuild the fire dataset)")
VIIRS = OD / "Economic raw data - ABS - insurance - VIIRS night lights/viirs_nsw"
HOT = OD / "Satellite hotspot downloads cache (per fire)"
MIN_DWELL = 5        # settled pixel: >= 5 Census-2016 dwellings
SUB = 5              # supersampling factor for allocating mesh blocks to pixels
FLAG_M = 2000        # fire mask radius
CTRL_M = 10000       # controls must be >= 10 km from any burning mapped fire in the window
FAR_M = 15000        # store fire-pixel distances up to this
END_MISSING_DAYS = 60


def months():
    ms = sorted({Path(p).name[:6] for p in glob.glob(str(VIIRS / "*_n_cf.tif"))})
    man = pd.read_csv(DS / "data/manifest.csv", encoding="utf-8", encoding_errors="replace")
    prod = {}
    for n in man.name:
        m = re.search(r"composite (\d{6}) avg_rade9 \(([^,]+),", str(n))
        if m:
            prod[m.group(1)] = m.group(2)
    return pd.DataFrame({"yyyymm": ms, "product": [prod.get(m, "") for m in ms]})


def dwellings_grid(tf, shape):
    counts = pd.read_csv(DS / "data/raw/pop/2016_census_mesh_block_counts.csv", dtype={"MB_CODE_2016": str}, encoding="latin-1")
    counts = counts[pd.to_numeric(counts.State, errors="coerce") == 1]
    counts["dwelling"] = pd.to_numeric(counts.Dwelling, errors="coerce").fillna(0.0)
    mb = pyogrio.read_dataframe(f"/vsizip/{DS}/data/raw/pop/MB_2016_NSW_shape.zip/MB_2016_NSW.shp",
                                columns=["MB_CODE16", "GCC_CODE16"])
    mb = mb.merge(counts[["MB_CODE_2016", "dwelling"]], left_on="MB_CODE16", right_on="MB_CODE_2016")
    mb = mb[(mb.dwelling > 0) & mb.geometry.notna() & ~mb.geometry.is_empty].reset_index(drop=True)
    mb["geometry"] = shapely.make_valid(mb.geometry.values)  # GDA94 lon/lat, treated as the WGS84 grid (< 2 m apart)
    print("mesh blocks with dwellings:", len(mb), "dwellings:", mb.dwelling.sum())
    H, W = shape
    sub_tf = rasterio.Affine(tf.a / SUB, 0, tf.c, 0, tf.e / SUB, tf.f)
    tree = shapely.STRtree(mb.geometry.values)
    pairs = []
    step = 40  # pixel rows per strip
    for r0 in range(0, H, step):
        r1 = min(H, r0 + step)
        top, bot = tf.f + tf.e * r0, tf.f + tf.e * r1
        idx = tree.query(shapely.box(tf.c, bot, tf.c + tf.a * W, top))
        if len(idx) == 0:
            continue
        stf = rasterio.Affine(sub_tf.a, 0, sub_tf.c, 0, sub_tf.e, top)
        arr = features.rasterize(((mb.geometry.values[i], int(i) + 1) for i in idx), out_shape=((r1 - r0) * SUB, W * SUB),
                                 transform=stf, fill=0, dtype="int32")
        rr, cc = np.nonzero(arr)
        if len(rr) == 0:
            continue
        pix = (r0 + rr // SUB) * W + cc // SUB
        key = (arr[rr, cc].astype(np.int64) - 1) * (H * W) + pix
        u, n = np.unique(key, return_counts=True)
        pairs.append(np.stack([u // (H * W), u % (H * W), n], 1))
    pairs = np.concatenate(pairs)
    hits = np.bincount(pairs[:, 0], weights=pairs[:, 2], minlength=len(mb))
    dw = np.zeros(H * W)
    syd = np.zeros(H * W)
    share = mb.dwelling.values[pairs[:, 0]] * pairs[:, 2] / hits[pairs[:, 0]]
    np.add.at(dw, pairs[:, 1], share)
    np.add.at(syd, pairs[:, 1], share * (mb.GCC_CODE16.values[pairs[:, 0]] == "1GSYD"))
    miss = np.nonzero(hits == 0)[0]  # tiny mesh blocks no sub-cell centre fell in: put at a point inside them
    rp = shapely.point_on_surface(mb.geometry.values[miss])
    inv = ~tf
    for i, p in zip(miss, rp):
        c, r = inv * (p.x, p.y)
        r, c = int(r), int(c)
        if 0 <= r < H and 0 <= c < W:
            dw[r * W + c] += mb.dwelling.values[i]
            syd[r * W + c] += mb.dwelling.values[i] * (mb.GCC_CODE16.values[i] == "1GSYD")
    print("dwellings allocated:", round(dw.sum()), "| tiny MBs placed by point:", len(miss))
    return dw.reshape(H, W), syd.reshape(H, W)


def main():
    WORK.mkdir(exist_ok=True)
    if __import__("os").environ.get("HOT_ONLY"):
        return hot_only()
    mo = months()
    mo.to_csv(WORK / "months.csv", index=False)
    ym = list(mo.yyyymm)
    mstart = pd.to_datetime(mo.yyyymm, format="%Y%m")
    print(len(ym), "months", ym[0], ym[-1])
    with rasterio.open(VIIRS / f"{ym[0]}_n_cf.tif") as s:
        tf, shape = s.transform, s.shape
    dw, syd = dwellings_grid(tf, shape)
    np.save(WORK / "dwell_grid.npy", dw.astype(np.float32))
    rows, cols = np.nonzero(dw >= MIN_DWELL)
    lon = tf.c + (cols + 0.5) * tf.a
    lat = tf.f + (rows + 0.5) * tf.e
    x, y = Transformer.from_crs(4326, 3577, always_xy=True).transform(lon, lat)
    px = pd.DataFrame(dict(pix=np.arange(len(rows)), row=rows, col=cols, lon=lon, lat=lat, x=x, y=y,
                           dwell=dw[rows, cols], gsyd=syd[rows, cols] > 0.5 * dw[rows, cols]))
    px.to_parquet(WORK / "pixels.parquet", index=False)
    print("settled pixels:", len(px), "| dwellings in them:", round(px.dwell.sum()), "| Greater Sydney:", px.gsyd.sum())

    # cloud-free counts (quality only, no radiance)
    ncf = np.zeros((len(px), len(ym)), dtype=np.uint16)
    for j, m in enumerate(ym):
        with rasterio.open(VIIRS / f"{m}_n_cf.tif") as s:
            ncf[:, j] = s.read(1)[rows, cols]
    np.save(WORK / "ncf.npy", ncf)

    # fire outlines: distance of every settled pixel within FAR_M
    f = gpd.read_parquet(DS / "data/cache/fires.parquet")
    f = f[f.geometry.notna() & ~f.geometry.is_empty].copy()
    f["end_use"] = f.end.fillna(f.start + pd.Timedelta(days=END_MISSING_DAYS))
    pts = shapely.points(px.x.values, px.y.values)
    ptree = shapely.STRtree(pts)
    out = []
    for r in f.itertuples():
        g = shapely.make_valid(r.geometry)
        idx = ptree.query(g.buffer(FAR_M), predicate="intersects")
        if len(idx):
            out.append(pd.DataFrame(dict(event_id=r.event_id, pix=idx, dist_m=shapely.distance(g, pts[idx]))))
    fp = pd.concat(out, ignore_index=True)
    fp.to_parquet(WORK / "fire_pix.parquet", index=False)
    # all Census-2016 dwellings with pixel centre inside each outline (settled or not), fires touching a settled pixel
    f4 = f[f.event_id.isin(fp.event_id.unique())].to_crs(4326)
    dwin = []
    for r in f4.itertuples():
        x0, y0, x1, y1 = r.geometry.bounds
        c0, r0 = (int(np.floor(v)) for v in ~tf * (x0, y1))
        c1, r1 = (int(np.ceil(v)) for v in ~tf * (x1, y0))
        c0, r0, c1, r1 = max(c0, 0), max(r0, 0), min(c1, shape[1]), min(r1, shape[0])
        m = features.rasterize([(r.geometry, 1)], out_shape=(r1 - r0, c1 - c0),
                               transform=rasterio.Affine(tf.a, 0, tf.c + c0 * tf.a, 0, tf.e, tf.f + r0 * tf.e),
                               fill=0, dtype="uint8")
        sub = dw[r0:r1, c0:c1]
        dwin.append((r.event_id, float(sub[m == 1].sum())))
    pd.DataFrame(dwin, columns=["event_id", "dwell_in_all"]).to_parquet(WORK / "fire_dwell_in.parquet", index=False)
    print("fire-pixel pairs within 15 km:", len(fp))

    # month masks from outlines
    mend = mstart + pd.offsets.MonthEnd(0)
    fd = f.set_index("event_id")[["start", "end_use"]]
    flag_fire = np.zeros_like(ncf, dtype=bool)
    near = np.zeros_like(ncf, dtype=bool)
    fpm = fp.join(fd, on="event_id")
    for j in range(len(ym)):
        act = fpm[(fpm.start <= mend[j]) & (fpm.end_use >= mstart[j])]
        flag_fire[act.pix[act.dist_m <= FLAG_M].values, j] = True
        near[act.pix[act.dist_m <= CTRL_M].values, j] = True
    np.save(WORK / "flag_fire.npy", flag_fire)
    np.savez_compressed(WORK / "near_fire_months.npz", near=near)

    if not __import__("os").environ.get("SKIP_HOT"):
        hot_only()


def hot_only():
    """Hotspot mask (separate step: the OneDrive hotspot cache downloads slowly)."""
    px = pd.read_parquet(WORK / "pixels.parquet")
    ym = list(pd.read_csv(WORK / "months.csv", dtype=str).yyyymm)
    ncf = np.load(WORK / "ncf.npy")
    flag_fire = np.load(WORK / "flag_fire.npy")
    # hotspots: every cached detection (all sensors), any month, within FLAG_M of a settled pixel
    hs = []
    for p in sorted(HOT.glob("*.parquet")):
        d = pd.read_parquet(p)
        if len(d):
            hs.append(d[["latitude", "longitude", "datetime"]])
    hs = pd.concat(hs, ignore_index=True)
    hs["datetime"] = pd.to_datetime(hs.datetime, utc=True, format="mixed").dt.tz_convert("Australia/Sydney")
    hs = hs.drop_duplicates()
    hx, hy = Transformer.from_crs(4326, 3577, always_xy=True).transform(hs.longitude.values, hs.latitude.values)
    hs_ym = hs.datetime.dt.strftime("%Y%m").values
    col = {m: j for j, m in enumerate(ym)}
    tree = cKDTree(np.c_[px.x.values, px.y.values])
    for rad, name in [(FLAG_M, "flag_hot.npy"), (5000, "flag_hot5.npy")]:  # 5 km version: sensitivity S1
        fh = np.zeros_like(ncf, dtype=bool)
        nb = tree.query_ball_point(np.c_[hx, hy], r=rad)
        for k, lst in enumerate(nb):
            j = col.get(hs_ym[k])
            if lst and j is not None:
                fh[lst, j] = True
        np.save(WORK / name, fh)
        if rad == FLAG_M:
            flag_hot = fh
    # 5 km outline mask (sensitivity S1)
    f = gpd.read_parquet(DS / "data/cache/fires.parquet")
    f["end_use"] = f.end.fillna(f.start + pd.Timedelta(days=END_MISSING_DAYS))
    fpm = pd.read_parquet(WORK / "fire_pix.parquet").join(f.set_index("event_id")[["start", "end_use"]], on="event_id")
    mstart = pd.to_datetime(pd.Series(ym), format="%Y%m")
    mend = mstart + pd.offsets.MonthEnd(0)
    ff5 = np.zeros_like(ncf, dtype=bool)
    for j in range(len(ym)):
        act = fpm[(fpm.start <= mend[j]) & (fpm.end_use >= mstart[j]) & (fpm.dist_m <= 5000)]
        ff5[act.pix.values, j] = True
    np.save(WORK / "flag_fire5.npy", ff5)
    info = dict(hotspot_files=len(list(HOT.glob('*.parquet'))), hotspots=len(hs), settled_pixels=len(px),
                pixel_months_flag_hot=int(flag_hot.sum()), pixel_months_flag_fire=int(flag_fire.sum()),
                share_ncf_lt2=float((ncf < 2).mean()))
    (WORK / "prep_info.json").write_text(json.dumps(info, indent=1))
    print(info)


if __name__ == "__main__":
    main()
