"""Quarterly economic activity around each fire (mentor item (a): "GDP change before and after the fire, by quarter").

No public quarterly GDP/GRP exists below the state. What IS public, downloadable and licensed for reuse (checked 2026-09-27):

1. ABS Australian National Accounts (5206.0), Table 25 "State Final Demand, Summary Components by State: Chain volume
   measures" (June 2026 release). NSW State Final Demand (SFD), quarterly, 1985 onward. STATE LEVEL ONLY (context:
   every NSW council gets the same value). ABS publishes no quarterly Gross State Product; GSP (5220.0) is annual.
   Licence CC BY 4.0.
2. Monthly VIIRS Day/Night Band night-time lights (EOG "VNL v1" monthly cloud-free composites, 15 arc-second grid,
   avg_rade9 in nW/cm2/sr, and n_cf = cloud-free observations), as mirrored in the World Bank "Light Every Night"
   public S3 bucket (s3://globalnightlight/composites/, anonymous access, Registry of Open Data on AWS, licence
   "World Bank Open Database License" linked to CC BY 4.0). The EOG site itself now requires a login and NASA Black
   Marble (VNP46A3) needs an Earthdata login: neither was used. Only the NSW window of each global COG is read
   (HTTP range requests) and stored under data/raw/econ/viirs_nsw/. Stray-light-EXCLUDED ("slexcl") version, the
   higher-quality one; NSW cloud-free coverage is near-complete in every month checked. Suomi-NPP only.
   Months 2014-01 .. 2025-06 (the bucket's last npp month); months absent from the bucket stay blank.
   Per ABS LGA 2021 (NSW) and month: mean radiance over covered pixels, sum of lights, and the same mean after
   removing pixels inside any mapped fire outline burning in that month (flames are bright in the DNB and would
   otherwise inflate the fire month). Quarterly = mean of the available monthly values.
   CAVEATS: (i) product changes: reprocessed "rp2/vcm" to operational "ops/vcm" at 2017-04, cloud mask vcm -> ecm
   at 2018-01, and 2024-10 exists only as "ecmcfg" (level shifts possible;
   `ntl_product` records it, event windows crossing it are flagged); (ii) monthly composites do not remove fires,
   gas flares or aurora; (iii) rural LGAs are mostly dark, so means are small and noisy; (iv) lights measure
   settlement/electricity use, not output. A proxy, not GRP.
3. ABS Weekly Payroll Jobs (6160.0.55.001), Table 5 "Sub-state - Payroll jobs indexes" by SA4 and SA3, weekly,
   week ending 4 Jan 2020 .. 13 May 2023 (index 14 March 2020 = 100). The ABS withdrew sub-state estimates from the
   15 July 2023 release ("Sub-state geography indexes (Table 5) have been withdrawn in this release") and ended the
   whole series with the week ending 15 March 2025 release. The last file with Table 5 (released 8 June 2023) is
   parsed. Quarterly = mean of weekly index values dated in the quarter. LGA value = LGA-resident-weighted mean of
   the SA3 indexes (2021 Census mesh-block persons), a proxy; the majority SA4 is also given.
4. NSW Government / RBA: no public quarterly regional (sub-state) activity series was found. NSW Treasury's economic
   dashboard reports state aggregates sourced from the ABS; the RBA publishes no regional quarterly output.

Writes (all under data/enrich/):
- econ_state_quarterly.parquet/.csv   region_id "1" (NSW, ABS STE 2021) x period: NSW SFD
- ntl_lga_month.parquet               region_id (ABS LGA 2021) x month: night-lights statistics
- ntl_lga_quarter.parquet/.csv        region_id x period
- payroll_sub_state_quarter.parquet   SA4 / SA3 x period (ABS codes as published)
- payroll_lga_quarter.parquet         region_id x period: resident-weighted SA3 proxy + majority SA4
- econ_quarterly_events.parquet/.csv  agrn x region_id (declared events): windows q-4 .. q+4 around the fire-start
                                      quarter, changes and excess changes
- econ_quarterly_fires.parquet        event_id x region_id (every mapped fire x council piece): same windows
- econ_quarterly.doc.json             column meanings
Run:  uv run --no-sync --with rasterio --with openpyxl python -m src.econ_quarterly
"""
import calendar
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from src.common import DATA, OUT, PHASE1, record_source

RAW = DATA / "raw/econ"
ENRICH = DATA / "enrich"
CACHE = DATA / "cache"
STE_NSW = "1"

# ---------------------------------------------------------------- ABS State Final Demand
SFD_BASE = ("https://www.abs.gov.au/statistics/economy/national-accounts/"
            "australian-national-accounts-national-income-expenditure-and-product/jun-2026/")
SFD_FILES = {"5206025_SFD_Summary.xlsx": "ABS 5206.0 Jun 2026, Table 25 State Final Demand summary components by state (CVM)",
             "5206026_SFD_NSW.xlsx": "ABS 5206.0 Jun 2026, Table 26 State Final Demand detailed components: NSW"}
SFD_SERIES = {  # series ID -> column (NSW, chain volume measures, $m / %)
    "A2303111F": "nsw_sfd_sa_aud_m",
    "A2303118W": "nsw_sfd_sa_qoq_pct",
    "A2299980W": "nsw_sfd_orig_aud_m",
    "A2303108T": "nsw_hh_consumption_sa_aud_m",
    "A2303109V": "nsw_private_gfcf_sa_aud_m",
}
SFD_PAGE = ("https://www.abs.gov.au/statistics/economy/national-accounts/"
            "australian-national-accounts-national-income-expenditure-and-product/latest-release")

# ---------------------------------------------------------------- night-time lights
NTL_BUCKET = "https://globalnightlight.s3.amazonaws.com"
NTL_DIR = RAW / "viirs_nsw"
NTL_BBOX = (140.9, -37.6, 153.7, -28.1)  # lon/lat window covering NSW (+ margin)
NTL_FIRST, NTL_LAST = "201401", "202512"
NTL_LICENCE = ("World Bank Open Database License / CC BY 4.0 (Registry of Open Data on AWS: wb-light-every-night); "
               "data: Earth Observation Group, Payne Institute, Colorado School of Mines / NOAA NCEI")
NTL_PAGE = "https://registry.opendata.aws/wb-light-every-night/"
LGA_SHP = PHASE1 / "raw/lga_2021/LGA_2021_AUST_GDA94.shp"
LGA_CACHE = CACHE / "lga2021_nsw_geom.parquet"

# ---------------------------------------------------------------- payroll jobs
PAY_URL = ("https://www.abs.gov.au/statistics/labour/jobs/payroll-jobs/week-ending-13-may-2023/6160055001_DO005.xlsx")
PAY_PAGE = "https://www.abs.gov.au/statistics/labour/jobs/payroll-jobs/week-ending-13-may-2023"
PAY_WITHDRAWN = "https://www.abs.gov.au/statistics/labour/jobs/payroll-jobs/week-ending-15-july-2023"
PAY_XLSX = RAW / "abs_6160055001_DO005_we20230513.xlsx"
ASGS = DATA / "raw/grp_insurance/asgs"
SA3_CACHE = CACHE / "lga2021_sa3_2021_persons.parquet"

WIN = [-4, -1, 0, 1, 2, 4]  # quarters relative to the fire-start quarter
FORCE_RECORD = False  # the Jun-2026 SFD and payroll files were downloaded (and recorded) while writing this module
MIN_FIRE_HA = 100           # comparison councils: no fire >= this size started in q-4 .. q+1


def fetch(url, path):
    """Download once; returns True if downloaded now (sources are recorded on first download only)."""
    if path.exists():
        return False
    if True:
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research data download)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return True


def qstr(ts):
    ts = pd.Timestamp(ts)
    return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"


def qshift(period, k):
    y, q = int(period[:4]), int(period[-1])
    n = y * 4 + (q - 1) + k
    return f"{n // 4}Q{n % 4 + 1}"


# ================================================================ 1. State Final Demand
def sfd():
    for f, name in SFD_FILES.items():
        p = RAW / f"abs_{f}"
        if fetch(SFD_BASE + f, p) or FORCE_RECORD:
            record_source(name, SFD_BASE + f, p, "CC BY 4.0 (ABS)",
                      "parsed: Table 25 NSW series " + ", ".join(SFD_SERIES) if "025" in f else "downloaded for reference, not parsed")
    d = pd.read_excel(RAW / "abs_5206025_SFD_Summary.xlsx", "Data1", header=None)
    ids = d.iloc[9].tolist()
    body = d.iloc[10:].copy()
    body = body[pd.to_datetime(body[0], errors="coerce").notna()]
    out = pd.DataFrame({"period": [qstr(t) for t in pd.to_datetime(body[0])]})
    for sid, col in SFD_SERIES.items():
        out[col] = pd.to_numeric(body[ids.index(sid)], errors="coerce").values
    out.insert(0, "region_id", STE_NSW)
    out["nsw_sfd_sa_yoy_pct"] = (out.nsw_sfd_sa_aud_m / out.nsw_sfd_sa_aud_m.shift(4) - 1) * 100
    out.to_parquet(ENRICH / "econ_state_quarterly.parquet", index=False)
    out.to_csv(ENRICH / "econ_state_quarterly.csv", index=False)
    return out


# ================================================================ 2. night-time lights
def ntl_months():
    """Suomi-NPP monthly composites in the bucket: {yyyymm: (key_avg, key_ncf, product)} (stray-light excluded)."""
    xml = urllib.request.urlopen(f"{NTL_BUCKET}/?delimiter=/&prefix=composites/", timeout=60).read().decode()
    prefixes = re.findall(r"<Prefix>composites/(npp_(\d{6})_(\w+))/</Prefix>", xml)
    out = {}
    for pre, ym, prod in prefixes:
        if not (NTL_FIRST <= ym <= NTL_LAST):
            continue
        keys = re.findall(r"<Key>([^<]+)</Key>",
                          urllib.request.urlopen(f"{NTL_BUCKET}/?prefix=composites/{pre}/", timeout=60).read().decode())
        # stray-light excluded version: "<mask>-slexcl" (2012-2024); in 2024-10 the only equivalent is "ecmcfg"
        # (the stray-light corrected one there is "ecmslcfg"). A month without an n_cf file stays blank.
        for tag in ["slexcl", "_ecmcfg_"]:
            avg = [k for k in keys if tag in k and k.endswith(".avg_rade9.tif")]
            ncf = [k for k in keys if tag in k and k.endswith(".n_cf.tif")]
            if avg and ncf:
                out[ym] = (avg[0], ncf[0], prod + "/" + re.search(r"global_(\w+?)(?:-slexcl)?_v10", avg[0]).group(1))
                break
    return out


def ntl_clip(key, path):
    """Read the NSW window of a global COG over HTTP and save it (deflate)."""
    import rasterio
    from rasterio.windows import from_bounds
    if path.exists():
        return path
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MAX_RETRY="5", GDAL_HTTP_RETRY_DELAY="3"):
        with rasterio.open(f"/vsicurl/{NTL_BUCKET}/{key}") as s:
            w = from_bounds(*NTL_BBOX, s.transform).round_offsets().round_lengths()
            a = s.read(1, window=w)
            prof = dict(driver="GTiff", dtype=a.dtype, width=a.shape[1], height=a.shape[0], count=1, crs=s.crs,
                        transform=s.window_transform(w), compress="deflate", tiled=True, blockxsize=256, blockysize=256,
                        predictor=3 if a.dtype.kind == "f" else 2)
    tmp = path.with_suffix(".part.tif")
    with rasterio.open(tmp, "w", **prof) as o:
        o.write(a, 1)
    tmp.rename(path)
    return path


def lga_geoms():
    if LGA_CACHE.exists():
        return gpd.read_parquet(LGA_CACHE)
    g = gpd.read_file(LGA_SHP)
    g = g[(g.STE_NAME21 == "New South Wales") & g.geometry.notna()]
    g = g[["LGA_CODE21", "LGA_NAME21", "geometry"]].rename(columns={"LGA_CODE21": "region_id", "LGA_NAME21": "region_name"})
    g.to_parquet(LGA_CACHE)
    record_source("ABS LGA 2021 boundaries (NSW subset, GDA94), cached", LGA_SHP, LGA_CACHE, "CC BY 4.0 (ABS)",
                  "copy of the phase-1 ABS ASGS 2021 LGA shapefile, NSW only")
    return g


def ntl_grids(template):
    """LGA label grid and, per month, a mask of pixels inside fires burning that month."""
    import rasterio
    from rasterio.features import rasterize
    with rasterio.open(template) as s:
        shape, tr = (s.height, s.width), s.transform
    g = lga_geoms().to_crs(4326)
    codes = g.region_id.astype(str).tolist()
    lab = rasterize(((geom, i + 1) for i, geom in enumerate(g.geometry)), out_shape=shape, transform=tr, fill=0,
                    dtype="int32")
    return lab, codes, shape, tr


def fire_mask(fires, ym, shape, tr):
    from rasterio.features import rasterize
    m0 = pd.Timestamp(f"{ym[:4]}-{ym[4:]}-01")
    m1 = m0 + pd.offsets.MonthEnd(0)
    end = fires["end"].fillna(fires["start"])
    sel = fires[(fires.start <= m1) & (end >= m0)]
    if sel.empty:
        return np.zeros(shape, bool), 0
    return rasterize(((geom, 1) for geom in sel.geometry), out_shape=shape, transform=tr, fill=0, dtype="uint8",
                     all_touched=True).astype(bool), len(sel)


def ntl():
    import rasterio
    months = ntl_months()
    NTL_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []
    for ym, (ka, kn, prod) in months.items():
        jobs += [(ka, NTL_DIR / f"{ym}_avg_rade9.tif"), (kn, NTL_DIR / f"{ym}_n_cf.tif")]
    new = {p for k, p in jobs if not p.exists()}
    with ThreadPoolExecutor(6) as ex:
        for p in ex.map(lambda j: ntl_clip(*j), jobs):
            print("ok", p.name, flush=True)
    for ym, (ka, kn, prod) in months.items():
        for k, kind in [(ka, "avg_rade9"), (kn, "n_cf")]:
            if NTL_DIR / f"{ym}_{kind}.tif" not in new:
                continue  # recorded when first downloaded
            record_source(f"VIIRS DNB monthly composite {ym} {kind} ({prod}, stray-light excluded), NSW window",
                          f"{NTL_BUCKET}/{k}", NTL_DIR / f"{ym}_{kind}.tif", NTL_LICENCE,
                          f"window {NTL_BBOX} (lon/lat) of the global COG read by HTTP range requests; values unchanged")
    first = NTL_DIR / f"{sorted(months)[0]}_avg_rade9.tif"
    lab, codes, shape, tr = ntl_grids(first)
    n_lab = len(codes) + 1
    npix = np.bincount(lab.ravel(), minlength=n_lab)
    fires = gpd.read_parquet(CACHE / "fires.parquet", columns=["event_id", "start", "end", "geometry"]).to_crs(4326)
    rows = []
    for ym in sorted(months):
        with rasterio.open(NTL_DIR / f"{ym}_avg_rade9.tif") as s:
            a = s.read(1).astype("float64")
        with rasterio.open(NTL_DIR / f"{ym}_n_cf.tif") as s:
            n = s.read(1)
        cov = (n > 0) & np.isfinite(a)
        fm, nf = fire_mask(fires, ym, shape, tr)
        l = lab.ravel()
        c1 = np.bincount(l, weights=cov.ravel(), minlength=n_lab)
        s1 = np.bincount(l, weights=np.where(cov, a, 0).ravel(), minlength=n_lab)
        ex = cov & ~fm
        c2 = np.bincount(l, weights=ex.ravel(), minlength=n_lab)
        s2 = np.bincount(l, weights=np.where(ex, a, 0).ravel(), minlength=n_lab)
        ncf = np.bincount(l, weights=np.where(cov, n, 0).ravel(), minlength=n_lab)
        fpx = np.bincount(l, weights=fm.ravel(), minlength=n_lab)
        for i, code in enumerate(codes, start=1):
            if npix[i] == 0:
                continue
            rows.append(dict(region_id=code, month=f"{ym[:4]}-{ym[4:]}", ntl_product=months[ym][2],
                             ntl_pixels=int(npix[i]), ntl_covered_share=c1[i] / npix[i],
                             ntl_mean_cf_obs=ncf[i] / c1[i] if c1[i] else np.nan,
                             ntl_mean_rad=s1[i] / c1[i] if c1[i] else np.nan,
                             ntl_sum_rad=s1[i] if c1[i] == npix[i] else np.nan,
                             ntl_fire_pixel_share=fpx[i] / npix[i],
                             ntl_mean_rad_excl_fire=s2[i] / c2[i] if c2[i] else np.nan))
        print(ym, "fires burning", nf, flush=True)
    m = pd.DataFrame(rows)
    m.to_parquet(ENRICH / "ntl_lga_month.parquet", index=False)
    m["period"] = [qstr(pd.Timestamp(x + "-01")) for x in m.month]
    agg = {c: "mean" for c in ["ntl_mean_rad", "ntl_mean_rad_excl_fire", "ntl_sum_rad", "ntl_covered_share",
                               "ntl_fire_pixel_share"]}
    q = m.groupby(["region_id", "period"]).agg(**{k: (k, v) for k, v in agg.items()},
                                               ntl_months=("month", "nunique"),
                                               ntl_product=("ntl_product", lambda s: "|".join(sorted(set(s))))).reset_index()
    # sum of lights is only comparable when every month of the quarter was fully covered
    full = m.groupby(["region_id", "period"]).ntl_sum_rad.apply(lambda s: s.notna().all()).values
    q.loc[~full, "ntl_sum_rad"] = np.nan
    q.to_parquet(ENRICH / "ntl_lga_quarter.parquet", index=False)
    q.to_csv(ENRICH / "ntl_lga_quarter.csv", index=False)
    missing = [f"{y}{mm:02d}" for y in range(int(NTL_FIRST[:4]), 2026) for mm in range(1, 13)
               if NTL_FIRST <= f"{y}{mm:02d}" <= max(months) and f"{y}{mm:02d}" not in months]
    return q, missing


# ================================================================ 3. payroll jobs (sub-state, 2020-2023)
def lga_sa3_persons():
    if SA3_CACHE.exists():
        return pd.read_parquet(SA3_CACHE)
    lga = pd.read_excel(ASGS / "LGA_2021_AUST.xlsx", dtype=str, usecols=["MB_CODE_2021", "LGA_CODE_2021", "STATE_CODE_2021"])
    mb = pd.read_excel(ASGS / "MB_2021_AUST.xlsx", dtype=str, usecols=["MB_CODE_2021", "SA3_CODE_2021", "STATE_CODE_2021"])
    cnt = pd.concat([pd.read_excel(ASGS / "Mesh_Block_Counts_2021.xlsx", sheet_name=s, header=6, dtype={"MB_CODE_2021": str})
                     for s in ["Table 1", "Table 1.1"]])
    cnt = cnt[cnt.MB_CODE_2021.str.fullmatch(r"\d{11}", na=False)]
    lga, mb = lga[lga.STATE_CODE_2021 == "1"], mb[mb.STATE_CODE_2021 == "1"]
    j = lga.merge(mb.drop(columns="STATE_CODE_2021"), on="MB_CODE_2021").merge(cnt[["MB_CODE_2021", "Person"]],
                                                                               on="MB_CODE_2021", how="left")
    j["Person"] = pd.to_numeric(j.Person, errors="coerce").fillna(0)
    out = j.groupby(["LGA_CODE_2021", "SA3_CODE_2021"], as_index=False).Person.sum()
    out.to_parquet(SA3_CACHE)
    return out


def payroll():
    if fetch(PAY_URL, PAY_XLSX) or FORCE_RECORD:
        record_source("ABS Weekly Payroll Jobs and Wages, Table 5 sub-state payroll jobs indexes (SA4, SA3), week ending "
                  "13 May 2023 (last release with sub-state data)", PAY_URL, PAY_XLSX, "CC BY 4.0 (ABS)",
                  "weekly index, 14 Mar 2020 = 100, weeks 2020-01-04..2023-05-13; sub-state withdrawn from the "
                  "15 Jul 2023 release; series ended with week ending 15 Mar 2025")
    rows = []
    for sheet, lvl, codecol in [("SA4", "SA4", 1), ("SA3", "SA3", 2)]:
        d = pd.read_excel(PAY_XLSX, sheet, header=None)
        hdr = d.iloc[5].tolist()
        dates = {i: pd.Timestamp(v) for i, v in enumerate(hdr) if isinstance(v, (pd.Timestamp,)) or hasattr(v, "year")}
        body = d.iloc[6:]
        body = body[body[0].astype(str).str.startswith("1. NSW")]
        for _, r in body.iterrows():
            code, name = str(r[codecol]).split(". ", 1)
            for i, t in dates.items():
                v = pd.to_numeric(r[i], errors="coerce")
                rows.append(dict(geo_level=lvl, geo_code=code, geo_name=name, week_ending=t, index=v))
    w = pd.DataFrame(rows)
    w["period"] = [qstr(t) for t in w.week_ending]
    q = w.groupby(["geo_level", "geo_code", "geo_name", "period"]).agg(
        payroll_index_mean=("index", "mean"), payroll_weeks=("index", "count")).reset_index()
    q.to_parquet(ENRICH / "payroll_sub_state_quarter.parquet", index=False)
    # LGA proxy: resident-weighted mean of SA3 indexes; plus majority SA4
    x = lga_sa3_persons().rename(columns={"LGA_CODE_2021": "region_id", "SA3_CODE_2021": "geo_code"})
    x = x[x.Person > 0]
    sa3 = q[q.geo_level == "SA3"]
    j = x.merge(sa3, on="geo_code", how="inner")
    j["wv"] = j.Person * j.payroll_index_mean
    lg = j.groupby(["region_id", "period"]).agg(wv=("wv", "sum"), w=("Person", "sum")).reset_index()
    tot = x.groupby("region_id").Person.sum()
    lg["payroll_index_lga_sa3_proxy"] = lg.wv / lg.w
    lg["payroll_sa3_weight_matched"] = lg.w / lg.region_id.map(tot)
    sa4p = pd.read_parquet(CACHE / "lga2021_sa4_2021_persons.parquet")
    maj = sa4p.sort_values("Person").groupby("LGA_CODE_2021").tail(1)[["LGA_CODE_2021", "SA4_CODE_2021"]]
    maj.columns = ["region_id", "sa4_code"]
    s4 = q[q.geo_level == "SA4"][["geo_code", "period", "payroll_index_mean"]].rename(
        columns={"geo_code": "sa4_code", "payroll_index_mean": "payroll_index_sa4_majority"})
    lg = lg.drop(columns=["wv", "w"]).merge(maj, on="region_id", how="left").merge(s4, on=["sa4_code", "period"], how="left")
    lg.to_parquet(ENRICH / "payroll_lga_quarter.parquet", index=False)
    return q, lg


# ================================================================ 4. windows around fires
def windows(keys, start_col, panels, fire_quarters):
    """keys: rows with region_id and a start date. panels: {prefix: (df keyed region_id/period, value col)}."""
    k = keys.copy()
    k["q0"] = [qstr(t) if pd.notna(t) else None for t in pd.to_datetime(k[start_col])]
    for pre, (df, col) in panels.items():
        lut = df.set_index(["region_id", "period"])[col].to_dict()
        for o in WIN + [-3]:
            k[f"{pre}_q{o:+d}"] = [lut.get((r, qshift(q, o))) if q else None for r, q in zip(k.region_id, k.q0)]
            k[f"{pre}_q{o:+d}"] = pd.to_numeric(k[f"{pre}_q{o:+d}"], errors="coerce")
        k[f"{pre}_chg_pct_q+1_vs_q-1"] = (k[f"{pre}_q+1"] / k[f"{pre}_q-1"] - 1) * 100
        k[f"{pre}_yoy_pct_q+1"] = (k[f"{pre}_q+1"] / k[f"{pre}_q-3"] - 1) * 100
        k[f"{pre}_yoy_pct_q+4_vs_q0"] = (k[f"{pre}_q+4"] / k[f"{pre}_q+0"] - 1) * 100
        if fire_quarters is not None:
            # excess: minus the median same-period change in NSW councils with no fire >= MIN_FIRE_HA started q-4..q+1
            allr = df.region_id.unique()
            ex = []
            for q in k.q0:
                if not q:
                    ex.append(np.nan)
                    continue
                span = {qshift(q, o) for o in range(-4, 2)}
                burnt = set(fire_quarters[fire_quarters.period.isin(span)].region_id)
                ctrl = [r for r in allr if r not in burnt]
                a = np.array([lut.get((r, qshift(q, 1)), np.nan) for r in ctrl], float)
                b = np.array([lut.get((r, qshift(q, -3)), np.nan) for r in ctrl], float)
                ex.append(np.nanmedian((a / b - 1) * 100) if np.isfinite(a / b).any() else np.nan)
            k[f"{pre}_yoy_pct_q+1_ctrl_median"] = ex
            k[f"{pre}_yoy_pct_q+1_excess"] = k[f"{pre}_yoy_pct_q+1"] - k[f"{pre}_yoy_pct_q+1_ctrl_median"]
        k = k.drop(columns=[f"{pre}_q-3"])
    return k


def events(sfd_q, ntl_q, pay_lga):
    pieces = pd.read_parquet(CACHE / "fire_lga_pieces.parquet", columns=["event_id", "LGA_CODE21", "region_burn_area_ha"])
    fires = pd.read_parquet(CACHE / "fires.parquet", columns=["event_id", "start", "burn_area_ha"])
    pf = pieces.merge(fires, on="event_id").rename(columns={"LGA_CODE21": "region_id"})
    pf["region_id"] = pf.region_id.astype(str)
    big = pf[pf.region_burn_area_ha >= MIN_FIRE_HA].copy()
    big["period"] = [qstr(t) for t in big.start]
    fire_q = big[["region_id", "period"]].drop_duplicates()

    ntl_q = ntl_q.copy()
    sfd_lga = None
    panels = {"ntl_mean": (ntl_q, "ntl_mean_rad"), "ntl_mean_exfire": (ntl_q, "ntl_mean_rad_excl_fire"),
              "payroll": (pay_lga, "payroll_index_lga_sa3_proxy")}
    prod = ntl_q.set_index(["region_id", "period"]).ntl_product.to_dict()

    def add_state(k):
        s = sfd_q.set_index("period")
        for o in [-1, 0, 1, 4]:
            k[f"nsw_sfd_sa_aud_m_q{o:+d}"] = [s.nsw_sfd_sa_aud_m.get(qshift(q, o)) if q else None for q in k.q0]
        k["nsw_sfd_chg_pct_q+1_vs_q-1"] = (k["nsw_sfd_sa_aud_m_q+1"] / k["nsw_sfd_sa_aud_m_q-1"] - 1) * 100
        k["nsw_sfd_yoy_pct_q0"] = [s.nsw_sfd_sa_yoy_pct.get(q) if q else None for q in k.q0]
        k["ntl_window_product_change"] = [
            len({p for o in range(-4, 5) for p in str(prod.get((r, qshift(q, o)), "")).split("|") if p}) > 1 if q else None
            for r, q in zip(k.region_id, k.q0)]
        return k

    kec = pd.read_csv(OUT / "key_event_council.csv", dtype={"region_id": str},
                      usecols=["agrn", "region_id", "region_name", "first_fire_start"])
    ev = add_state(windows(kec, "first_fire_start", panels, fire_q))
    ev = ev.rename(columns={"q0": "fire_start_quarter"})
    ev.to_parquet(ENRICH / "econ_quarterly_events.parquet", index=False)
    ev.to_csv(ENRICH / "econ_quarterly_events.csv", index=False)
    fr = pf[["event_id", "region_id", "start", "region_burn_area_ha"]]
    frw = add_state(windows(fr, "start", panels, fire_q)).rename(columns={"q0": "fire_start_quarter"})
    frw.to_parquet(ENRICH / "econ_quarterly_fires.parquet", index=False)
    return ev, frw


def doc(missing):
    D = {}
    D["region_id"] = ["ABS LGA 2021 code (\"1\" = NSW state in econ_state_quarterly)", "code", "ABS ASGS 2021", ""]
    D["period"] = ["Calendar quarter, e.g. 2019Q4 = Oct-Dec 2019", "str", "", ""]
    D["nsw_sfd_sa_aud_m"] = ["NSW State Final Demand, chain volume, seasonally adjusted (ABS series A2303111F)",
                             "AUD m", "ABS 5206.0 Table 25", "STATE level: identical for every council"]
    D["nsw_sfd_sa_qoq_pct"] = ["NSW SFD quarter-on-quarter % change, SA (A2303118W)", "%", "ABS 5206.0 Table 25", "state"]
    D["nsw_sfd_orig_aud_m"] = ["NSW SFD, chain volume, original (A2299980W)", "AUD m", "ABS 5206.0 Table 25", "state"]
    D["nsw_hh_consumption_sa_aud_m"] = ["NSW household final consumption, CVM, SA (A2303108T)", "AUD m", "ABS 5206.0 Table 25", "state"]
    D["nsw_private_gfcf_sa_aud_m"] = ["NSW private gross fixed capital formation, CVM, SA (A2303109V)", "AUD m", "ABS 5206.0 Table 25", "state"]
    D["nsw_sfd_sa_yoy_pct"] = ["NSW SFD SA, % change on the same quarter a year earlier", "%", "computed from A2303111F", "state"]
    D["month"] = ["Calendar month (ntl_lga_month)", "YYYY-MM", "", ""]
    D["ntl_product"] = ["Composite product: npp_<rp2|ops>/<vcm|ecm> (reprocessed to 2017-03, operational from 2017-04)",
                        "str", "EOG VIIRS DNB monthly v1.0 via World Bank Light Every Night", "level breaks possible at 2017-04 (rp2->ops), 2018-01 (vcm->ecm cloud mask) and 2024-10 (ecmcfg naming)"]
    D["ntl_pixels"] = ["15 arc-second pixels whose centre lies in the LGA", "count", "computed", ""]
    D["ntl_covered_share"] = ["Share of LGA pixels with >= 1 cloud-free observation (n_cf > 0)", "share", "EOG n_cf", ""]
    D["ntl_mean_cf_obs"] = ["Mean number of cloud-free observations per covered pixel", "count", "EOG n_cf", ""]
    D["ntl_mean_rad"] = ["Mean avg_rade9 radiance over covered LGA pixels (quarter: mean of monthly values)", "nW/cm2/sr",
                         "EOG VIIRS DNB monthly, stray-light excluded", "PROXY for activity; includes fire light, noise (negatives kept)"]
    D["ntl_sum_rad"] = ["Sum of radiance over the LGA (only when every pixel covered, every month of the quarter)",
                        "nW/cm2/sr x pixels", "same", "equal-angle pixels; not area-corrected"]
    D["ntl_fire_pixel_share"] = ["Share of LGA pixels inside a mapped fire outline burning in the month", "share",
                                 "GA fire outlines (data/cache/fires.parquet)", ""]
    D["ntl_mean_rad_excl_fire"] = ["As ntl_mean_rad after removing pixels inside fires burning in that month", "nW/cm2/sr",
                                   "computed", "removes flame light; burnt settlements outside the burning month remain"]
    D["ntl_months"] = ["Months with a composite in the quarter (quarter value = their mean)", "count", "",
                       "months missing from the bucket: " + ", ".join(missing)]
    D["geo_level / geo_code / geo_name"] = ["ABS SA4 or SA3 as published in the payroll table", "code", "ABS 6160.0.55.001 Table 5", ""]
    D["payroll_index_mean"] = ["Mean weekly payroll jobs index over weeks ending in the quarter (14 Mar 2020 = 100)", "index",
                               "ABS Weekly Payroll Jobs Table 5, release of 8 Jun 2023", "2020Q1..2023Q2 only; Q2 2023 partial"]
    D["payroll_weeks"] = ["Weekly values in the quarter", "count", "", ""]
    D["payroll_index_lga_sa3_proxy"] = ["LGA-resident-weighted mean of SA3 payroll indexes (2021 mesh-block persons)", "index",
                                        "ABS payroll + ASGS 2021 + Mesh Block Counts 2021", "PROXY: assumes the SA3 index applies to each part"]
    D["payroll_sa3_weight_matched"] = ["Share of the LGA's residents whose SA3 has a payroll index", "share", "", ""]
    D["sa4_code / payroll_index_sa4_majority"] = ["Payroll index of the SA4 holding most LGA residents", "index", "ABS", "SA4 level"]
    D["agrn / event_id"] = ["Declared event (AGRN) or mapped fire", "id", "out/key_event_council.csv; data/cache/fires.parquet", ""]
    D["fire_start_quarter"] = ["Quarter of first_fire_start (events) or fire start (fires) = q0", "str", "", ""]
    D["<x>_q{-4,-1,+0,+1,+2,+4}"] = ["Quarterly value k quarters from q0 for x = ntl_mean, ntl_mean_exfire, payroll", "as panel",
                                     "panels above", "blank = not published / outside coverage"]
    D["<x>_chg_pct_q+1_vs_q-1"] = ["% change, quarter after vs quarter before the fire-start quarter", "%", "computed",
                                   "not seasonally adjusted: seasonal swings in lights/jobs are included"]
    D["<x>_yoy_pct_q+1"] = ["% change, quarter after the fire vs the same quarter a year earlier (q-3)", "%", "computed", "removes seasonality"]
    D["<x>_yoy_pct_q+4_vs_q0"] = ["% change, q+4 vs q0 (same quarter one year after)", "%", "computed", ""]
    D["<x>_yoy_pct_q+1_ctrl_median"] = [f"Median of the same yoy change across NSW LGAs with no fire >= {MIN_FIRE_HA} ha "
                                        "starting in q-4..q+1", "%", "computed", "comparison group, descriptive"]
    D["<x>_yoy_pct_q+1_excess"] = ["yoy change minus the comparison median", "pp", "computed", "descriptive, not causal"]
    D["nsw_sfd_sa_aud_m_q{-1,+0,+1,+4}"] = ["NSW SFD (SA, CVM) around the fire-start quarter", "AUD m", "ABS", "state context"]
    D["nsw_sfd_chg_pct_q+1_vs_q-1"] = ["NSW SFD % change q+1 vs q-1", "%", "ABS", "state context"]
    D["nsw_sfd_yoy_pct_q0"] = ["NSW SFD yoy % change in the fire-start quarter", "%", "ABS", "state context"]
    D["ntl_window_product_change"] = ["True if the q-4..q+4 window spans two night-lights product versions", "bool", "", ""]
    (ENRICH / "econ_quarterly.doc.json").write_text(json.dumps(D, indent=1))


def main():
    ENRICH.mkdir(parents=True, exist_ok=True)
    s = sfd()
    print("SFD", s.period.min(), s.period.max())
    p, lg = payroll()
    print("payroll", p.period.min(), p.period.max(), lg.region_id.nunique(), "LGAs")
    q, missing = ntl()
    print("ntl", q.period.min(), q.period.max(), q.region_id.nunique(), "LGAs; missing months", missing)
    ev, fr = events(s, q, lg)
    doc(missing)
    print(ev.notna().mean().round(2).to_string())


if __name__ == "__main__":
    main()
