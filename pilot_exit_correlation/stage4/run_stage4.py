"""Stage 4: satellite timing measured on the stretch of each exit road nearest the town.

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage4/run_stage4.py

Uses the frozen stage-3 hotspot cache (hash-verified); makes no network requests.
"""
import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyproj
import shapely

HERE = Path(__file__).resolve().parent
STAGE1, STAGE2, STAGE3 = HERE.parent, HERE.parent / "stage2", HERE.parent / "stage3"
for p in (STAGE1, STAGE2, STAGE3):
    sys.path.insert(0, str(p))
import run_stage3 as s3run  # noqa: E402  (stage-3 helpers, reused unchanged)
from src import inputs  # noqa: E402
from src.closure import closed_sets as overlay_closed_sets  # noqa: E402
from src.exits import CommunityGraph  # noqa: E402
from s2 import historical  # noqa: E402
from s3 import hotspots  # noqa: E402
from s3.timing import exit_hit_times, simultaneous, spread_hours  # noqa: E402

D_M, EXTRA_M = 1000, 2000
PRIMARY = (5000, 12)
VARIANTS = [(5000, 12), (2000, 12), (10000, 12), (5000, 24)]  # (K metres, window hours)
STAGE3_UNTIMED_R = 23.796142  # stage-3 satellite-era perimeter ratio, reproduced as a check
OUT = HERE / "out"


def near_town_edges(path, closed, edge_geom, poly, K):
    cut = [e for e in path if e in closed]
    if not cut:
        return []
    d = shapely.distance(np.array([edge_geom[e] for e in cut], dtype=object), poly)
    limit = max(K, d.min() + EXTRA_M)
    return [e for e, x in zip(cut, d) if x <= limit]


def main():
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)
    hashes = s3run.verify()
    manifest = pd.read_csv(STAGE3 / "out/hotspot_manifest.csv")
    print("inputs verified", flush=True)

    net = inputs.load_network()
    overlay, members = inputs.load_overlay()
    famA = inputs.load_family_geometries(members)
    ucl = inputs.load_communities().set_index("UCL_CODE21", drop=False)
    g, _ = historical.load_fires()
    evB = historical.families(g)
    closed = {"A": overlay_closed_sets(overlay)["S0"], "B": historical.closed_sets(g, evB, net)["S0"]}
    events = s3run.event_tables(members, famA, g, evB)

    s1 = pd.read_parquet(STAGE1 / "out/community_results.parquet")
    inc = s1[(s1.rule == "S0") & (s1.ring_radius_km == 20) & ~s1.ring_inside_polygon & (s1.exits >= 2)]
    towns = inc.ucl_code.tolist()
    paths = pd.read_parquet(STAGE1 / "out/exit_paths.parquet")
    paths = paths[paths.ring_radius_km == 20].sort_values(["ucl_code", "exit_index"])
    path_map = {c: [list(x) for x in d.edge_ids] for c, d in paths.groupby("ucl_code")}
    rows_ucl = [(c, ucl.loc[c, "geometry"]) for c in towns]
    rel = {"A": s3run.relevant(rows_ucl, famA.geometry.values, famA.disaster_family_id.values),
           "B": s3run.relevant(rows_ucl, g.geometry.values, evB.values)}
    graphs = {c: CommunityGraph(net, p, (p.centroid.x, p.centroid.y), 20000) for c, p in rows_ucl}
    era = set(events.index[(events.part == "A") | (events.start >= s3run.ERA_START)])
    rel_era = {c: sorted(rel["A"][c] + [e for e in rel["B"][c] if e in era]) for c in towns}
    closed_era = {**closed["A"], **{e: s for e, s in closed["B"].items() if e in era}}
    uni, units, iso_pairs = s3run.build_units(towns, rel_era, closed_era, None, graphs, path_map, False)
    untimed = s3run.summarise(units, len(uni), (6, 0))
    assert abs(untimed["R"] - STAGE3_UNTIMED_R) < 1e-5 and untimed["observed"] == 31, untimed
    print(f"sample reproduced: {untimed['observed']:.0f} cut-offs, R = {untimed['R']:.3f}", flush=True)

    to_alb = pyproj.Transformer.from_crs(4326, 3577, always_xy=True)
    hs = {}
    for m in manifest.itertuples():
        df = hotspots.load_event(m.event_id, STAGE3 / "data/hotspots", m.sha256)
        x, y = to_alb.transform(df.longitude.astype(float).values, df.latitude.astype(float).values)
        hs[m.event_id] = (np.c_[x, y], pd.DatetimeIndex(df.datetime))
    assert {e for _, e in iso_pairs} <= set(hs), "hotspot cache does not cover every isolating event"
    edge_geom = dict(zip(net["edges"].edge_id.values, net["geom"]))

    times, pair_rows = {}, []
    for code, e in iso_pairs:
        poly = ucl.loc[code, "geometry"]
        xy, t = hs[e]
        row = dict(ucl_code=code, town=ucl.loc[code, "UCL_NAME21"], event_id=e, part=events.loc[e, "part"],
                   exits=len(path_map[code]))
        for K in sorted({k for k, _ in VARIANTS}):
            near = [near_town_edges(p, closed_era[e], edge_geom, poly, K) for p in path_map[code]]
            tt = exit_hit_times(near, set().union(*map(set, near)), edge_geom, events.loc[e, "geometry"], xy, t, D_M)
            times[(code, e, K)] = tt
            row[f"exits_dated_K{K//1000}km"] = int(sum(pd.notna(x) for x in tt))
            row[f"spread_hours_K{K//1000}km"] = spread_hours(tt)
            if K == PRIMARY[0]:
                row["first_hit_K5km"] = min([x for x in tt if pd.notna(x)], default=pd.NaT)
                row["last_hit_K5km"] = max([x for x in tt if pd.notna(x)], default=pd.NaT)
        pair_rows.append(row)

    results = [dict(analysis="stage 4", timing="none (perimeter; stage-3 sample)", verdict="", **untimed)]
    for i, (K, W) in enumerate(VARIANTS):
        override = [np.array([iso[j] and simultaneous(times[(code, ev[j], K)], W) for j in range(len(ev))], dtype=bool)
                    for code, ev, _, iso, _ in units]
        row = dict(analysis="stage 4", timing=f"all exits reached within {W} h near town (K = {K//1000} km)",
                   **s3run.summarise(units, len(uni), (7, K, W), override))
        row["verdict"] = s3run.verdict(row, min_n1=False) if (K, W) == PRIMARY else ""
        results.append(row)

    res = pd.DataFrame(results)
    res.to_csv(OUT / "stage4_results.csv", index=False)
    pairs = pd.DataFrame(pair_rows)
    s3pairs = pd.read_parquet(STAGE3 / "out/timing_pairs.parquet")
    s3pairs = s3pairs[~s3pairs.outside_town_rule][["ucl_code", "event_id", "spread_hours_1km"]]
    pairs = pairs.merge(s3pairs.rename(columns={"spread_hours_1km": "stage3_spread_hours_whole_route"}),
                        on=["ucl_code", "event_id"], how="left")
    pairs.to_parquet(OUT / "timing_pairs_near_town.parquet", index=False)
    aussef_after = inputs.sha256(inputs.AUSSEF_DB)
    assert aussef_before == aussef_after, "aussef.duckdb changed during run"
    meta = dict(run_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                runtime_s=round(time.time() - t0, 1), seed=s3run.SEED, bootstrap=s3run.B,
                input_hashes=hashes, aussef_duckdb_sha256=aussef_after)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    import report4
    report4.write_all(res, pairs, meta)
    prim = res[res.verdict != ""].iloc[0]
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: run complete in {meta['runtime_s']} s; all input and hotspot-cache hashes matched; "
                f"aussef.duckdb unchanged ({aussef_after[:12]}…); stage 4 primary: **{prim.verdict}** "
                f"(R_timed = {prim.R:.2f}, 95% CI {prim.R_lo:.2f}–{prim.R_hi:.2f}).\n")
    print(res[["timing", "observed", "expected", "R", "R_lo", "R_hi", "verdict"]].to_string())


if __name__ == "__main__":
    main()
