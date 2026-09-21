"""Stage 3: outside-the-town check (3a) and satellite timing check (3b).

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage3/run_stage3.py

The first run downloads DEA Hotspots for the isolating fire events into stage3/data/hotspots/ (git-ignored).
Later runs use that frozen cache and verify its hashes.
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
STAGE1, STAGE2 = HERE.parent, HERE.parent / "stage2"
for p in (STAGE1, STAGE2, HERE):
    sys.path.insert(0, str(p))
from src import inputs  # noqa: E402  (stage 1)
from src.closure import closed_sets as overlay_closed_sets  # noqa: E402
from src.exits import CommunityGraph  # noqa: E402
from s2 import historical  # noqa: E402  (stage 2)
from s2.pooled import bootstrap, community_arrays, pooled, ratio  # noqa: E402
from s3 import hotspots  # noqa: E402
from s3.timing import exit_hit_times, simultaneous, spread_hours  # noqa: E402

SEED, B, R_KM, FIRE_DISTANCE_M = 20260921, 1000, 20, 30000
ERA_START = pd.Timestamp("2002-09-01", tz="UTC")
NO_END_DAYS, PAD_BEFORE, PAD_AFTER, PAD_DEG = 30, 1, 7, 0.02
MIN_O, MIN_N1, PASS_R = 5, 20, 2.0
WINDOWS_H, DISTANCES_M = [12, 6, 24], [1000, 500]
OUT, CACHE = HERE / "out", HERE / "data" / "hotspots"
STAGE2_FROZEN = {
    STAGE1 / "out/exit_paths.parquet": "f6e2a81e291abac200898f7ca815b0eebee53199e33f45e82a5a37b08cc7df8a",
    STAGE1 / "out/community_results.parquet": "3c42ee2a0ff0e38afb05dd6dc197412ece9258d361de60a279a1ac9eb9234bee",
    historical.GA_ZIP: historical.GA_ZIP_SHA256,
}
STAGE2_R = {"A": 6.647576180795725, "B": 14.910501263151545}  # stage-2 primary, for the cross-check


def verify():
    hashes = inputs.verify_inputs()
    for p, h in STAGE2_FROZEN.items():
        got = inputs.sha256(p)
        if got != h:
            raise SystemExit(f"HASH MISMATCH for {p}: expected {h}, got {got}. Stopping.")
        hashes[str(p)] = got
    return hashes


def event_tables(members, famA, g, evB):
    """Event id -> (start, end, geometry), for part A families and part B historical events."""
    a = members.groupby("disaster_family_id").agg(start=("family_start_date", "min"), end=("family_end_date", "max"))
    a = a.join(famA.set_index("disaster_family_id").geometry)
    a["part"] = "A"
    gb = g.assign(event_id=evB.values)
    b = gb.groupby("event_id").agg(start=("ign", "min"), end=("ext", "max"))
    b = b.join(gb.dissolve("event_id").geometry)
    b["part"] = "B"
    ev = pd.concat([a, b])
    ev["start"] = pd.to_datetime(ev.start, utc=True)
    ev["end"] = pd.to_datetime(ev.end, utc=True)
    ev["end"] = ev.end.where(ev.end.notna() & (ev.end >= ev.start), ev.start + pd.Timedelta(days=NO_END_DAYS))
    return ev


def relevant(ucl_rows, geoms, ids):
    tree = shapely.STRtree(geoms)
    return {c: sorted(set(ids[tree.query(p, predicate="dwithin", distance=FIRE_DISTANCE_M)].tolist()))
            for c, p in ucl_rows}


def build_units(towns, rel, closed, inside_edges, graphs, path_map, outside_only):
    """Pooled units plus the list of isolating (town, event) pairs."""
    universe, units, iso_pairs = {}, [], []
    for code in towns:
        evs = rel[code]
        if not evs:
            continue
        cl_map = closed
        if outside_only:
            ins = inside_edges[code]
            cl_map = {e: closed[e] - ins for e in evs if e in closed}
        iso, cl = community_arrays(graphs[code], path_map[code], evs, cl_map)
        idx = np.array([universe.setdefault(e, len(universe)) for e in evs])
        units.append((code, np.array(evs), idx, iso, cl))
        iso_pairs += [(code, e) for e in np.array(evs)[iso]]
    return universe, units, iso_pairs


def summarise(units, n_events, seed_key, iso_override=None):
    u = [(idx, iso if iso_override is None else iso_override[i], cl) for i, (_, _, idx, iso, cl) in enumerate(units)]
    s = pooled(u)
    lo, hi, und = bootstrap(u, n_events, np.random.default_rng(np.random.SeedSequence([SEED, *seed_key])), B)
    return dict(observed=s["O"], expected=s["E"], pairs_any_exit_closed=s["N1"], R=float(ratio(s["O"], s["E"])),
                R_lo=lo, R_hi=hi, boot_undefined_share=und, fire_events=n_events, towns=len(u))


def verdict(row, min_n1=True):
    if row["observed"] < MIN_O or (min_n1 and row["pairs_any_exit_closed"] < MIN_N1):
        return "NOT EVALUABLE"
    ok = np.isfinite(row["R"]) and row["R"] >= PASS_R and np.isfinite(row["R_lo"]) and row["R_lo"] > 1
    return "PASS" if ok else "FAIL"


def main():
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)
    hashes = verify()
    print("inputs verified", flush=True)

    net = inputs.load_network()
    overlay, members = inputs.load_overlay()
    famA = inputs.load_family_geometries(members)
    ucl = inputs.load_communities().set_index("UCL_CODE21", drop=False)
    g, _ = historical.load_fires()
    evB = historical.families(g)
    closed = {"A": overlay_closed_sets(overlay)["S0"], "B": historical.closed_sets(g, evB, net)["S0"]}
    events = event_tables(members, famA, g, evB)
    print("loaded", flush=True)

    s1 = pd.read_parquet(STAGE1 / "out/community_results.parquet")
    inc = s1[(s1.rule == "S0") & (s1.ring_radius_km == R_KM) & ~s1.ring_inside_polygon & (s1.exits >= 2)]
    towns = inc.ucl_code.tolist()
    paths = pd.read_parquet(STAGE1 / "out/exit_paths.parquet")
    paths = paths[paths.ring_radius_km == R_KM].sort_values(["ucl_code", "exit_index"])
    path_map = {c: [list(x) for x in d.edge_ids] for c, d in paths.groupby("ucl_code")}
    rows_ucl = [(c, ucl.loc[c, "geometry"]) for c in towns]
    rel = {"A": relevant(rows_ucl, famA.geometry.values, famA.disaster_family_id.values),
           "B": relevant(rows_ucl, g.geometry.values, evB.values)}
    edge_tree = shapely.STRtree(net["geom"])
    edge_ids = net["edges"].edge_id.values
    inside_edges = {c: set(edge_ids[edge_tree.query(p, predicate="intersects")].tolist()) for c, p in rows_ucl}
    graphs = {}
    for c, p in rows_ucl:
        cen = p.centroid
        graphs[c] = CommunityGraph(net, p, (cen.x, cen.y), R_KM * 1000)
    print(f"graphs built {time.time()-t0:.0f}s", flush=True)

    results = []
    # ---------------- 3a: outside-the-town closure ----------------
    for p_i, part in enumerate(("A", "B")):
        for f_i, outside in enumerate((False, True)):
            uni, units, _ = build_units(towns, rel[part], closed[part], inside_edges, graphs, path_map, outside)
            row = dict(analysis="3a", sample=part, closure="S0 outside town" if outside else "S0 (stage-2 rule)",
                       timing="none (perimeter)", **summarise(units, len(uni), (3, p_i, f_i)))
            if outside:
                row["verdict"] = verdict(row)
            else:
                row["verdict"] = ""
                assert abs(row["R"] - STAGE2_R[part]) < 1e-9, f"stage-2 cross-check failed for {part}: {row['R']}"
            results.append(row)
    print("3a done; stage-2 R reproduced exactly", flush=True)

    # ---------------- 3b: satellite timing ----------------
    era = set(events.index[(events.part == "A") | (events.start >= ERA_START)])
    rel_era = {c: sorted([e for e in rel["A"][c]] + [e for e in rel["B"][c] if e in era]) for c in towns}
    closed_era = {**closed["A"], **{e: s for e, s in closed["B"].items() if e in era}}
    variants = {}
    for f_i, outside in enumerate((False, True)):
        variants[outside] = build_units(towns, rel_era, closed_era, inside_edges, graphs, path_map, outside)
    uni, units, iso_pairs = variants[False]
    untimed = dict(analysis="3b", sample="satellite era (2002-09 to 2023)", closure="S0", timing="none (perimeter)",
                   **summarise(units, len(uni), (4, 0, 0)))
    untimed["verdict"] = ""
    results.append(untimed)
    print(f"3b era: {untimed['observed']:.0f} perimeter cut-offs from {len(set(e for _, e in iso_pairs))} events", flush=True)

    manifest, pair_rows = [], []
    if untimed["observed"] < MIN_O:
        timed_verdict = "NOT EVALUABLE"
    else:
        iso_events = sorted(set(e for _, e in iso_pairs))
        to_ll = pyproj.Transformer.from_crs(3577, 4326, always_xy=True)
        to_alb = pyproj.Transformer.from_crs(4326, 3577, always_xy=True)
        hs = {}
        for e in iso_events:
            geom = events.loc[e, "geometry"]
            x0, y0, x1, y1 = geom.bounds
            lon, lat = to_ll.transform([x0, x1, x0, x1], [y0, y0, y1, y1])
            bbox = (min(lon) - PAD_DEG, min(lat) - PAD_DEG, max(lon) + PAD_DEG, max(lat) + PAD_DEG)
            w0 = (events.loc[e, "start"] - pd.Timedelta(days=PAD_BEFORE)).strftime("%Y-%m-%dT00:00:00Z")
            w1 = (events.loc[e, "end"] + pd.Timedelta(days=PAD_AFTER)).strftime("%Y-%m-%dT23:59:59Z")
            m = hotspots.fetch_event(e, bbox, w0, w1, CACHE)
            manifest.append(m)
            df = hotspots.load_event(e, CACHE, m["sha256"])
            x, y = to_alb.transform(df.longitude.astype(float).values, df.latitude.astype(float).values)
            hs[e] = (np.c_[x, y], pd.DatetimeIndex(df.datetime))
            print(f"  hotspots {e}: {m['rows']:,} rows", flush=True)
        edge_geom = dict(zip(edge_ids, net["geom"]))
        times = {}
        for outside in (False, True):
            _, _, pairs_v = variants[outside]
            for code, e in pairs_v:
                cl = closed_era[e] - inside_edges[code] if outside else closed_era[e]
                for D in DISTANCES_M:
                    xy, t = hs[e]
                    times[(outside, code, e, D)] = exit_hit_times(path_map[code], cl, edge_geom,
                                                                  events.loc[e, "geometry"], xy, t, D)
                tt = times[(outside, code, e, 1000)]
                pair_rows.append(dict(ucl_code=code, town=ucl.loc[code, "UCL_NAME21"], event_id=e,
                                      part=events.loc[e, "part"], outside_town_rule=outside, exits=len(tt),
                                      exits_dated_1km=int(sum(pd.notna(x) for x in tt)),
                                      first_hit_1km=min([x for x in tt if pd.notna(x)], default=pd.NaT),
                                      spread_hours_1km=spread_hours(tt),
                                      spread_hours_500m=spread_hours(times[(outside, code, e, 500)])))
        for outside in (False, True):
            uni_v, units_v, _ = variants[outside]
            for D in DISTANCES_M:
                for W in WINDOWS_H:
                    if outside and (D, W) != (1000, 12):
                        continue
                    override = [np.array([iso[i] and simultaneous(times[(outside, code, ev_arr[i], D)], W)
                                          for i in range(len(ev_arr))], dtype=bool)
                                for code, ev_arr, _, iso, _ in units_v]
                    row = dict(analysis="3b", sample="satellite era (2002-09 to 2023)",
                               closure="S0 outside town" if outside else "S0",
                               timing=f"all exits hit within {W} h (hotspot ≤ {D} m)",
                               **summarise(units_v, len(uni_v), (5, int(outside), D, W), override))
                    primary = (not outside) and (D, W) == (1000, 12)
                    row["verdict"] = verdict(row, min_n1=False) if primary else ""
                    results.append(row)
        timed_verdict = next(r["verdict"] for r in results if r["analysis"] == "3b" and r["verdict"])

    res = pd.DataFrame(results)
    res.to_csv(OUT / "stage3_results.csv", index=False)
    pd.DataFrame(pair_rows).to_parquet(OUT / "timing_pairs.parquet", index=False)
    pd.DataFrame(manifest).to_csv(OUT / "hotspot_manifest.csv", index=False)
    aussef_after = inputs.sha256(inputs.AUSSEF_DB)
    assert aussef_before == aussef_after, "aussef.duckdb changed during run"
    meta = dict(run_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                runtime_s=round(time.time() - t0, 1), seed=SEED, bootstrap=B, input_hashes=hashes,
                aussef_duckdb_sha256=aussef_after, timed_verdict=timed_verdict,
                hotspot_events=len(manifest), hotspot_rows=int(sum(m["rows"] for m in manifest)))
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    from s3 import report
    report.write_all(res, pd.DataFrame(pair_rows), meta)
    v = res[res.verdict != ""]
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: run complete in {meta['runtime_s']} s; all input hashes matched; "
                f"aussef.duckdb unchanged ({aussef_after[:12]}…); "
                + "; ".join(f"{r.analysis} {r.sample[:12]}: **{r.verdict}** (R = {r.R:.2f})" for r in v.itertuples()) + ".\n")
    print(v[["analysis", "sample", "closure", "timing", "observed", "expected", "R", "R_lo", "R_hi", "verdict"]].to_string())


if __name__ == "__main__":
    main()
