"""Stage 8 (exploratory): 2016->2021 change in towns cut off by Black Summer vs towns burned but not cut off.

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage8/run_stage8.py
"""
import datetime as dt
import io
import json
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio

HERE = Path(__file__).resolve().parent
STAGE1, STAGE2, STAGE3, STAGE6 = (HERE.parent, HERE.parent / "stage2", HERE.parent / "stage3", HERE.parent / "stage6")
for p in (STAGE1, STAGE2, STAGE3, STAGE6):
    sys.path.insert(0, str(p))
import run_stage3 as s3run  # noqa: E402
from src import inputs  # noqa: E402
from src.closure import closed_sets as overlay_closed_sets  # noqa: E402
from src.exits import CommunityGraph  # noqa: E402
from stats6 import holm, mann_whitney_p, median_diff_ci  # noqa: E402

SEED, B, MIN_CUT = 20260921, 2000, 10
IOU_PRIMARY, IOU_SENS = 0.7, (0.5, 0.85)
BS_START, BS_END = pd.Timestamp("2019-07-01"), pd.Timestamp("2020-06-30")
DATA = STAGE1 / "data"
ZIPS = {"gcp2016": (DATA / "2016_GCP_UCL_for_NSW_short-header.zip", "2455e718330840eeb83a1b0cca53174366b31d5a2a451e9efa0691298db76b16"),
        "ucl2016": (DATA / "1270055004_ucl_2016_aust_shape.zip", "692668cee6e0d0a5db7b46970118b5c775ee283893d9d2f50c99535e0335ffd1"),
        "gcp2021": (DATA / "2021_GCP_UCL_for_NSW_short-header.zip", "19eca38d9d92c612d4083551535a53c730f30683205a16b26098235d17fc7aaf")}
OUTCOMES = {"pop_growth_pct": "Population growth 2016→2021 (%)",
            "hh_income_change_pct": "Median household income change (%, nominal)",
            "emp_ratio_change_pp": "Employment-to-population ratio change (pp)",
            "unemp_rate_change_pp": "Unemployment rate change (pp)"}
PRIMARY = "pop_growth_pct"
OUT = HERE / "out"


def verify_zips():
    for key, (p, h) in ZIPS.items():
        if inputs.sha256(p) != h:
            raise SystemExit(f"HASH MISMATCH for {p}")


def census(year):
    z = zipfile.ZipFile(ZIPS[f"gcp{year}"][0])
    lf = "G43B" if year == 2016 else "G46B"

    def table(t):
        name = next(n for n in z.namelist() if n.endswith(f"{year}Census_{t}_NSW_UCL.csv"))
        return pd.read_csv(io.BytesIO(z.read(name))).set_index(f"UCL_CODE_{year}")

    g01, g02, glf = table("G01"), table("G02"), table(lf)
    d = pd.DataFrame(index=g01.index)
    d["persons"] = g01.Tot_P_P
    d["hh_income"] = g02.Median_tot_hhd_inc_weekly.where(g02.Median_tot_hhd_inc_weekly > 0)
    pop15 = glf.P_Tot_LF_Tot + glf.P_Not_in_LF_Tot
    d["emp_ratio"] = np.where(pop15 > 0, 100 * glf.P_Tot_Emp_Tot / pop15, np.nan)
    d["unemp_rate"] = np.where(glf.P_Tot_LF_Tot > 0, 100 * glf.P_Tot_Unemp_Tot / glf.P_Tot_LF_Tot, np.nan)
    d.index = d.index.str.removeprefix("UCL")
    return d


def black_summer_status():
    """Per town: cut off / burned not cut off / not touched by a 2019-20 fire (stage-3 machinery, part A only)."""
    net = inputs.load_network()
    overlay, members = inputs.load_overlay()
    famA = inputs.load_family_geometries(members)
    closed = overlay_closed_sets(overlay)["S0"]
    start = members.groupby("disaster_family_id").family_start_date.min()
    bs = set(start[(pd.to_datetime(start) >= BS_START) & (pd.to_datetime(start) <= BS_END)].index)
    ucl = inputs.load_communities().set_index("UCL_CODE21", drop=False)
    s1 = pd.read_parquet(STAGE1 / "out/community_results.parquet")
    inc = s1[(s1.rule == "S0") & (s1.ring_radius_km == 20) & ~s1.ring_inside_polygon & (s1.exits >= 2)]
    towns = inc.ucl_code.tolist()
    paths = pd.read_parquet(STAGE1 / "out/exit_paths.parquet")
    paths = paths[paths.ring_radius_km == 20].sort_values(["ucl_code", "exit_index"])
    path_map = {c: [list(x) for x in d.edge_ids] for c, d in paths.groupby("ucl_code")}
    rows_ucl = [(c, ucl.loc[c, "geometry"]) for c in towns]
    rel = s3run.relevant(rows_ucl, famA.geometry.values, famA.disaster_family_id.values)
    rel_bs = {c: [e for e in rel[c] if e in bs] for c in towns}
    graphs = {c: CommunityGraph(net, p, (p.centroid.x, p.centroid.y), 20000) for c, p in rows_ucl if rel_bs[c]}
    _, units, _ = s3run.build_units([c for c in towns if rel_bs[c]], rel_bs, closed, None, graphs, path_map, False)
    status = pd.Series("not touched", index=pd.Index(towns, name="ucl_code"))
    for code, evs, idx, iso, cl in units:
        if iso.any():
            status[code] = "cut off"
        elif cl.any():
            status[code] = "burned, not cut off"
    return status, ucl, len(bs)


def link_2016(ucl21):
    shp = f"/vsizip/{ZIPS['ucl2016'][0]}/UCL_2016_AUST.shp"
    u16 = pyogrio.read_dataframe(shp)
    u16 = u16[u16.STE_NAME16 == "New South Wales"].to_crs(3577)[["UCL_CODE16", "UCL_NAME16", "geometry"]]
    a = gpd.GeoDataFrame(ucl21[["UCL_CODE21", "UCL_NAME21"]], geometry=ucl21.geometry.values, crs=3577).reset_index(drop=True)
    ov = gpd.overlay(a, u16, how="intersection", keep_geom_type=True)
    ov["inter"] = ov.area
    best = ov.sort_values("inter", ascending=False).drop_duplicates("UCL_CODE21").set_index("UCL_CODE21")
    area21 = a.set_index("UCL_CODE21").area
    area16 = u16.set_index("UCL_CODE16").area
    best["iou"] = best.inter / (area21.loc[best.index].values + area16.loc[best.UCL_CODE16].values - best.inter)
    return best[["UCL_CODE16", "UCL_NAME16", "iou"]]


def compare(df, a, b, m, rng):
    x, y = df.loc[df.group == a, m].dropna(), df.loc[df.group == b, m].dropna()
    if len(x) == 0 or len(y) == 0:
        return dict(outcome=m, comparison=f"{a} vs {b}", n_a=len(x), n_b=len(y))
    est, lo, hi = median_diff_ci(x, y, rng, B)
    return dict(outcome=m, comparison=f"{a} vs {b}", n_a=len(x), n_b=len(y), median_a=float(np.median(x)),
                median_b=float(np.median(y)), diff=est, diff_lo=lo, diff_hi=hi, p_mwu=mann_whitney_p(x, y))


def main():
    t0 = dt.datetime.now(dt.timezone.utc)
    OUT.mkdir(exist_ok=True)
    inputs.verify_inputs()
    verify_zips()
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)

    status, ucl, n_bs = black_summer_status()
    link = link_2016(ucl.loc[status.index])
    c16, c21 = census(2016), census(2021)
    df = pd.DataFrame({"group": status}).join(ucl[["UCL_NAME21"]]).join(link)
    df = df.join(c21.add_suffix("_2021")).join(c16.add_suffix("_2016"), on="UCL_CODE16")
    df["pop_growth_pct"] = 100 * (df.persons_2021 - df.persons_2016) / df.persons_2016.where(df.persons_2016 > 0)
    df["hh_income_change_pct"] = 100 * (df.hh_income_2021 - df.hh_income_2016) / df.hh_income_2016
    df["emp_ratio_change_pp"] = df.emp_ratio_2021 - df.emp_ratio_2016
    df["unemp_rate_change_pp"] = df.unemp_rate_2021 - df.unemp_rate_2016
    df.to_csv(OUT / "town_change_2016_2021.csv")

    rng = np.random.default_rng(SEED)
    ok = df[df.iou >= IOU_PRIMARY]
    rows = [compare(ok, "cut off", "burned, not cut off", m, rng) for m in OUTCOMES]
    rows += [compare(ok, "cut off", "not touched", m, rng) for m in OUTCOMES]
    for thr in IOU_SENS:
        r = compare(df[df.iou >= thr], "cut off", "burned, not cut off", PRIMARY, rng)
        r["comparison"] += f" (IoU ≥ {thr})"
        rows.append(r)
    res = pd.DataFrame(rows)
    sec = (res.comparison == "cut off vs burned, not cut off") & (res.outcome != PRIMARY)
    res.loc[sec, "p_holm"] = holm(res.loc[sec, "p_mwu"].values)
    p = res[(res.outcome == PRIMARY) & (res.comparison == "cut off vs burned, not cut off")].iloc[0]
    if p.n_a < MIN_CUT:
        verdict = "NOT EVALUABLE"
    elif p.diff_hi < 0:
        verdict = "WORSE"
    elif p.diff_lo > 0:
        verdict = "BETTER"
    else:
        verdict = "NO CLEAR DIFFERENCE"
    res["verdict"] = np.where((res.outcome == PRIMARY) & (res.comparison == "cut off vs burned, not cut off"), verdict, "")
    res.to_csv(OUT / "stage8_results.csv", index=False)
    assert aussef_before == inputs.sha256(inputs.AUSSEF_DB), "aussef.duckdb changed"
    failed = df[(df.iou < IOU_PRIMARY) | df.iou.isna()]
    meta = dict(run_utc=t0.isoformat(timespec="seconds"), seed=SEED, bootstrap=B, verdict=verdict,
                black_summer_families=n_bs, towns=len(df), groups_all=df.group.value_counts().to_dict(),
                groups_after_iou=ok.group.value_counts().to_dict(),
                cut_off_towns_failing_iou=failed.loc[failed.group == "cut off", "UCL_NAME21"].tolist(),
                aussef_duckdb_sha256=aussef_before)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    import report8
    report8.write_all(res, df, meta)
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: all input and download hashes matched; aussef.duckdb unchanged; primary: "
                f"**{verdict}** (median population growth difference {p['diff']:.1f} pp, 95% CI {p.diff_lo:.1f} to {p.diff_hi:.1f}; "
                f"{int(p.n_a)} cut-off vs {int(p.n_b)} burned-not-cut-off towns).\n")
    print(json.dumps(meta, indent=2, default=str))
    print(res.round(2).to_string())


if __name__ == "__main__":
    main()
