"""Stage 2: pooled exit-failure test (part A 2019-23; part B historical 1950-2019).

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage2/run_stage2.py
"""
import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import shapely

HERE = Path(__file__).resolve().parent
STAGE1 = HERE.parent
sys.path.insert(0, str(STAGE1))
sys.path.insert(0, str(HERE))
from src import inputs  # noqa: E402  (stage 1)
from src.closure import closed_sets as overlay_closed_sets  # noqa: E402
from src.exits import CommunityGraph  # noqa: E402
from s2 import historical  # noqa: E402
from s2.pooled import bootstrap, community_arrays, pooled, ratio  # noqa: E402

SEED, B = 20260921, 1000
RADII_KM = [20, 10, 30]
RULES = ["S0", "S100"]
PARTS = ["A", "B", "B_with_undated"]
FIRE_DISTANCE_M = 30000
MIN_O, MIN_N1 = 5, 20
PASS_R = 2.0
OUT = HERE / "out"
FROZEN_STAGE1_OUT = {
    STAGE1 / "out/exit_paths.parquet": "f6e2a81e291abac200898f7ca815b0eebee53199e33f45e82a5a37b08cc7df8a",
    STAGE1 / "out/community_results.parquet": "3c42ee2a0ff0e38afb05dd6dc197412ece9258d361de60a279a1ac9eb9234bee",
    historical.GA_ZIP: historical.GA_ZIP_SHA256,
}


def verify():
    hashes = inputs.verify_inputs()
    for p, h in FROZEN_STAGE1_OUT.items():
        got = inputs.sha256(p)
        if got != h:
            raise SystemExit(f"HASH MISMATCH for {p}: expected {h}, got {got}. Stopping.")
        hashes[str(p)] = got
    return hashes


def relevant_events(ucl, geoms, event_ids):
    tree = shapely.STRtree(geoms)
    out = {}
    for code, poly in zip(ucl.UCL_CODE21, ucl.geometry):
        hit = tree.query(poly, predicate="dwithin", distance=FIRE_DISTANCE_M)
        out[code] = sorted(set(event_ids[hit].tolist()))
    return out


def overlay_crosscheck(fam, closedA, net):
    """Rebuild part-A S0 closures with the part-B method and compare with the stage-1 overlay."""
    mine = historical.closed_sets(fam, fam.disaster_family_id, net)["S0"]
    used = set(net["edges"].edge_id.tolist())
    inter = union = 0
    for f in set(mine) | set(closedA["S0"]):
        a = set(closedA["S0"].get(f, ())) & used
        b = set(mine.get(f, ()))
        inter += len(a & b)
        union += len(a | b)
    return dict(edges_overlay_or_rebuilt=union, edges_in_both=inter, jaccard=inter / union if union else None)


def main():
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)
    hashes = verify()
    print("inputs verified", flush=True)

    net = inputs.load_network()
    overlay, members = inputs.load_overlay()
    famA = inputs.load_family_geometries(members)
    ucl = inputs.load_communities().set_index("UCL_CODE21", drop=False)
    closed = {"A": overlay_closed_sets(overlay)}
    xcheck = overlay_crosscheck(famA, closed["A"], net)
    print("overlay cross-check", xcheck, flush=True)

    counts, events_geo = {}, {}
    for part, undated in (("B", False), ("B_with_undated", True)):
        g, c = historical.load_fires(include_undated=undated)
        ev = historical.families(g)
        c["events"] = int(ev.nunique())
        counts[part] = c
        closed[part] = historical.closed_sets(g, ev, net)
        events_geo[part] = (g.geometry.values, ev.values)
        print(part, c, flush=True)
    events_geo["A"] = (famA.geometry.values, famA.disaster_family_id.values)
    relevant = {p: relevant_events(ucl, *events_geo[p]) for p in PARTS}

    s1 = pd.read_parquet(STAGE1 / "out/community_results.parquet")
    s1 = s1[s1.rule == "S0"]
    paths = pd.read_parquet(STAGE1 / "out/exit_paths.parquet")

    rows, comm_rows = [], []
    for R in RADII_KM:
        tR = time.time()
        inc = s1[(s1.ring_radius_km == R) & ~s1.ring_inside_polygon & (s1.exits >= 2)]
        pr = paths[paths.ring_radius_km == R].sort_values(["ucl_code", "exit_index"])
        path_map = {c: [list(x) for x in g.edge_ids] for c, g in pr.groupby("ucl_code")}
        units = {(p, r): [] for p in PARTS for r in RULES}
        universe = {p: {} for p in PARTS}
        for n_done, code in enumerate(inc.ucl_code):
            poly = ucl.loc[code, "geometry"]
            cen = poly.centroid
            cg = CommunityGraph(net, poly, (cen.x, cen.y), R * 1000)
            cpaths = path_map[code]
            assert len(cpaths) == int(inc.set_index("ucl_code").loc[code, "exits"])
            for part in PARTS:
                evs = relevant[part][code]
                if not evs:
                    continue
                idx = np.array([universe[part].setdefault(e, len(universe[part])) for e in evs])
                for rule in RULES:
                    iso, cl = community_arrays(cg, cpaths, evs, closed[part][rule])
                    units[(part, rule)].append((idx, iso, cl))
                    s = pooled([(idx, iso, cl)])
                    comm_rows.append(dict(ucl_code=code, ucl_name=ucl.loc[code, "UCL_NAME21"],
                                          population=int(ucl.loc[code, "population"]), part=part, rule=rule,
                                          ring_radius_km=R, exits=len(cpaths), n_relevant_fires=len(evs),
                                          fires_closing_any_exit=s["N1"], isolations=s["O"],
                                          expected_isolations_independent=s["E"],
                                          expected_any_closed_independent=s["E1"]))
            if n_done % 100 == 0:
                print(f"  R={R}km {n_done}/{len(inc)} {time.time()-tR:.0f}s", flush=True)
        for p_i, part in enumerate(PARTS):
            for r_i, rule in enumerate(RULES):
                u = units[(part, rule)]
                s = pooled(u)
                rng = np.random.default_rng(np.random.SeedSequence([SEED, p_i, r_i, R]))
                lo, hi, und = bootstrap(u, len(universe[part]), rng, B)
                r = float(ratio(s["O"], s["E"]))
                row = dict(part=part, rule=rule, ring_radius_km=R, communities=len(u),
                           fire_events=len(universe[part]), pairs_any_exit_closed=s["N1"],
                           observed_isolations=s["O"], expected_isolations=s["E"], R=r, R_lo=lo, R_hi=hi,
                           boot_undefined_share=und,
                           share_all_given_any_observed=s["O"] / s["N1"] if s["N1"] else np.nan,
                           share_all_given_any_expected=s["E"] / s["E1"] if s["E1"] else np.nan)
                row["primary"] = (rule, R) == ("S0", 20) and part in ("A", "B")
                row["verdict"] = verdict(row) if row["primary"] else ""
                rows.append(row)
        print(f"R={R}km done in {time.time()-tR:.0f}s", flush=True)

    res = pd.DataFrame(rows)
    res.to_csv(OUT / "pooled_results.csv", index=False)
    comm = pd.DataFrame(comm_rows)
    comm.to_parquet(OUT / "community_level.parquet", index=False)
    aussef_after = inputs.sha256(inputs.AUSSEF_DB)
    assert aussef_before == aussef_after, "aussef.duckdb changed during run"
    meta = dict(run_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                runtime_s=round(time.time() - t0, 1), seed=SEED, bootstrap=B, input_hashes=hashes,
                aussef_duckdb_sha256=aussef_after, part_b_counts=counts, overlay_crosscheck=xcheck,
                part_a_families=len(famA))
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    from s2 import report
    report.write_all(res, comm, meta)
    prim = res[res.primary]
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: run complete in {meta['runtime_s']} s; all input hashes matched; "
                f"aussef.duckdb unchanged ({aussef_after[:12]}…); "
                + "; ".join(f"part {r.part}: **{r.verdict}** (R = {r.R:.2f})" for r in prim.itertuples()) + ".\n")
    print(prim.to_string())


def verdict(row):
    if row["observed_isolations"] < MIN_O or row["pairs_any_exit_closed"] < MIN_N1:
        return "NOT EVALUABLE"
    ok = np.isfinite(row["R"]) and row["R"] >= PASS_R and np.isfinite(row["R_lo"]) and row["R_lo"] > 1
    return "PASS" if ok else "FAIL"


if __name__ == "__main__":
    main()
