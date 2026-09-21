"""Correlated-exit-failure pilot: one-command end-to-end run.

    uv run --with matplotlib python pilot_exit_correlation/run_pilot.py

Reads inputs read-only, verifies frozen hashes, writes only inside pilot_exit_correlation/.
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
sys.path.insert(0, str(HERE))
from src import inputs  # noqa: E402
from src.closure import closed_sets, community_matrices  # noqa: E402
from src.exits import CommunityGraph  # noqa: E402
from src.metrics import LOG5, bootstrap_log_rho, log_rho, n_eff  # noqa: E402

SEED = 20260921
B = 1000
RADII_M = [20000, 10000, 30000]  # primary first
FIRE_DISTANCE_M = 30000
MIN_EXITS, MIN_FIRES, MIN_ELIGIBLE = 2, 10, 10
PASS_SHARE, RHO_THRESHOLD = 0.20, 5.0
OUT = HERE / "out"


def main():
    t0 = time.time()
    OUT.mkdir(exist_ok=True)
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)
    hashes = inputs.verify_inputs()
    print("inputs verified", flush=True)

    net = inputs.load_network()
    overlay, members = inputs.load_overlay()
    fam = inputs.load_family_geometries(members)
    ucl = inputs.load_communities()
    closed = closed_sets(overlay)
    service_overlay_rows = int((overlay.highway == "service").sum())
    print(f"network {net['n_edges_used']:,}/{net['n_edges_all']:,} edges; {len(fam)} families; {len(ucl)} communities", flush=True)

    # Relevant fires: family footprint within 30 km of the community polygon.
    tree = shapely.STRtree(fam.geometry.values)
    fam_ids = fam.disaster_family_id.values
    relevant = {}
    for code, poly in zip(ucl.UCL_CODE21, ucl.geometry):
        hit = tree.query(poly, predicate="dwithin", distance=FIRE_DISTANCE_M)
        relevant[code] = sorted(fam_ids[hit].tolist())

    rows, path_rows = [], []
    for R in RADII_M:
        tR = time.time()
        for i, c in ucl.iterrows():
            poly = c.geometry
            cen = poly.centroid
            code = c.UCL_CODE21
            fams = relevant[code]
            base = dict(ucl_code=code, ucl_name=c.UCL_NAME21, section_of_state=c.SOS_NAME21,
                        population=int(c.population), area_km2=float(c.AREASQKM21),
                        centroid_x=cen.x, centroid_y=cen.y, ring_radius_km=R // 1000,
                        n_relevant_fires=len(fams))
            reach = shapely.get_coordinates(poly.boundary)
            ring_inside = bool(np.hypot(reach[:, 0] - cen.x, reach[:, 1] - cen.y).max() >= R)
            base["ring_inside_polygon"] = ring_inside
            if ring_inside:
                exits, paths, cg = np.nan, [], None
                base.update(n_source_nodes=np.nan, n_ring_nodes=np.nan, source_fallback=np.nan)
            else:
                cg = CommunityGraph(net, poly, (cen.x, cen.y), R)
                exits, paths = cg.exits_and_paths()
                base.update(n_source_nodes=len(cg.sources), n_ring_nodes=len(cg.ring),
                            source_fallback=cg.source_fallback)
                for j, p in enumerate(paths):
                    path_rows.append(dict(ucl_code=code, ring_radius_km=R // 1000, exit_index=j,
                                          n_edges=len(p), edge_ids=p))
            base["exits"] = exits
            elig_exits = (not ring_inside) and exits >= MIN_EXITS
            elig_fires = len(fams) >= MIN_FIRES
            for r_i, rule in enumerate(("S0", "S100")):
                row = dict(base, rule=rule, eligible_exits=elig_exits, eligible_fires=elig_fires,
                           eligible=bool(elig_exits and elig_fires))
                if cg is None or not paths or len(fams) == 0:
                    row.update(k_isolated=np.nan, P_obs=np.nan, P_ind=np.nan, log10_P_ind=np.nan,
                               rho=np.nan, log10_rho=np.nan, rho_lo=np.nan, rho_hi=np.nan,
                               boot_undefined_share=np.nan, N_eff=np.nan, excluded_never_closed=np.nan,
                               excluded_always_closed=np.nan, fires_closing_any_exit=np.nan)
                    rows.append(row)
                    continue
                iso, cl = community_matrices(cg, paths, fams, closed[rule])
                assert cl[iso].all(), f"isolation without all exits closed: {code}"
                lpo, lpi, lr = log_rho(iso, cl)
                rng = np.random.default_rng(np.random.SeedSequence([SEED, int(code), R, r_i]))
                lo, hi, und = bootstrap_log_rho(iso, cl, rng, B)
                ne, never, always = n_eff(cl)
                row.update(k_isolated=int(iso.sum()), P_obs=float(np.exp(lpo)), P_ind=float(np.exp(lpi)),
                           log10_P_ind=lpi / np.log(10), rho=float(np.exp(lr)) if np.isfinite(lr) else np.nan,
                           log10_rho=lr / np.log(10), rho_lo=float(np.exp(lo)) if np.isfinite(lo) else np.nan,
                           rho_hi=float(np.exp(hi)) if np.isfinite(hi) else np.nan,
                           log10_rho_lo=lo / np.log(10), log10_rho_hi=hi / np.log(10),
                           boot_undefined_share=und, N_eff=ne, excluded_never_closed=never,
                           excluded_always_closed=always, fires_closing_any_exit=int(cl.any(axis=1).sum()),
                           rho_gt5_and_lo_gt1=bool(np.isfinite(lr) and lr > LOG5 and np.isfinite(lo) and lo > 0))
                rows.append(row)
            if i % 100 == 0:
                print(f"  R={R//1000}km {i}/{len(ucl)} {time.time()-tR:.0f}s", flush=True)
        print(f"R={R//1000}km done in {time.time()-tR:.0f}s", flush=True)

    res = pd.DataFrame(rows)
    res["rho_gt5_and_lo_gt1"] = res["rho_gt5_and_lo_gt1"].astype("boolean")
    res["exits_minus_N_eff"] = res.exits - res.N_eff
    res.to_parquet(OUT / "community_results.parquet", index=False)
    res.drop(columns=[]).to_csv(OUT / "community_results.csv", index=False)
    pd.DataFrame(path_rows).to_parquet(OUT / "exit_paths.parquet", index=False)

    verdict = decide(res)
    aussef_after = inputs.sha256(inputs.AUSSEF_DB)
    assert aussef_before == aussef_after, "aussef.duckdb changed during run"
    meta = dict(run_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                runtime_s=round(time.time() - t0, 1), seed=SEED, bootstrap=B,
                input_hashes=hashes, aussef_duckdb_sha256=aussef_after,
                network_edges_all=net["n_edges_all"], network_edges_used=net["n_edges_used"],
                overlay_rows_service_dropped=service_overlay_rows,
                family_members_without_geometry=fam.attrs["members_without_geometry"],
                n_families=len(fam), n_communities=len(ucl), verdict=verdict)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    from src import report
    report.write_all(res, meta, net)
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: run complete in {meta['runtime_s']} s; all input hashes matched; "
                f"aussef.duckdb unchanged ({aussef_after[:12]}…); verdict **{verdict['verdict']}** "
                f"({verdict['n_pass']}/{verdict['n_eligible']} eligible).\n")
    print(json.dumps(verdict, indent=2))


def decide(res):
    p = res[(res.rule == "S0") & (res.ring_radius_km == 20)]
    elig = p[p.eligible]
    n = len(elig)
    n_pass = int(elig.rho_gt5_and_lo_gt1.fillna(False).sum())
    if n < MIN_ELIGIBLE:
        v = "NOT EVALUABLE"
    else:
        v = "PASS" if n_pass / n >= PASS_SHARE else "FAIL"
    return dict(verdict=v, n_eligible=n, n_pass=n_pass, share=(n_pass / n) if n else None,
                n_rho_defined=int(elig.rho.notna().sum()),
                fail_ring_inside=int(p.ring_inside_polygon.sum()),
                fail_exits=int((~p.ring_inside_polygon & ~p.eligible_exits).sum()),
                fail_fires=int((~p.eligible_fires).sum()), n_communities=len(p))


if __name__ == "__main__":
    main()
