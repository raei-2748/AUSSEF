"""Post-hoc descriptive diagnostics (NOT pre-registered; see DEVIATIONS.md). Primary cell: S0, ring 20 km.

1. Which fire events produced each full cut-off, and what share of the town lies inside that fire.
2. Pooled R with the single most influential fire event left out (part A and part B).

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage2/diagnostics.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shapely

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from src import inputs  # noqa: E402
from src.closure import closed_sets as overlay_closed_sets  # noqa: E402
from src.exits import CommunityGraph  # noqa: E402
from s2 import historical  # noqa: E402
from s2.pooled import bootstrap, community_arrays, pooled, ratio  # noqa: E402

SEED, B, R_KM = 20260921, 1000, 20


def main():
    inputs.verify_inputs()
    net = inputs.load_network()
    overlay, members = inputs.load_overlay()
    famA = inputs.load_family_geometries(members)
    ucl = inputs.load_communities().set_index("UCL_CODE21", drop=False)
    g, _ = historical.load_fires()
    evB = historical.families(g)
    parts = {
        "A": (famA.geometry.values, famA.disaster_family_id.values, overlay_closed_sets(overlay)["S0"],
              famA.set_index("disaster_family_id").geometry),
        "B": (g.geometry.values, evB.values, historical.closed_sets(g, evB, net)["S0"],
              g.assign(event_id=evB.values).dissolve("event_id").geometry),
    }
    s1 = pd.read_parquet(HERE.parent / "out/community_results.parquet")
    inc = s1[(s1.rule == "S0") & (s1.ring_radius_km == R_KM) & ~s1.ring_inside_polygon & (s1.exits >= 2)]
    paths = pd.read_parquet(HERE.parent / "out/exit_paths.parquet")
    paths = paths[paths.ring_radius_km == R_KM].sort_values(["ucl_code", "exit_index"])
    path_map = {c: [list(x) for x in d.edge_ids] for c, d in paths.groupby("ucl_code")}

    iso_rows, loo_rows = [], []
    for p_i, (part, (geoms, ev_ids, closed, ev_geom)) in enumerate(parts.items()):
        tree = shapely.STRtree(geoms)
        universe, units, unit_events = {}, [], []
        for code in inc.ucl_code:
            poly = ucl.loc[code, "geometry"]
            evs = sorted(set(ev_ids[tree.query(poly, predicate="dwithin", distance=30000)].tolist()))
            if not evs:
                continue
            cen = poly.centroid
            cg = CommunityGraph(net, poly, (cen.x, cen.y), R_KM * 1000)
            iso, cl = community_arrays(cg, path_map[code], evs, closed)
            idx = np.array([universe.setdefault(e, len(universe)) for e in evs])
            units.append((idx, iso, cl))
            unit_events.append(np.array(evs))
            for e in np.array(evs)[iso]:
                inside = shapely.intersection(poly, ev_geom.loc[e]).area / poly.area
                iso_rows.append(dict(part=part, town=ucl.loc[code, "UCL_NAME21"], population=int(ucl.loc[code, "population"]),
                                     exits=len(path_map[code]), event_id=e, share_of_town_inside_fire=round(inside, 3)))
        iso_df = pd.DataFrame([r for r in iso_rows if r["part"] == part])
        top = iso_df.event_id.value_counts().index[0]
        for label, drop in (("all events", None), (f"without {top}", top)):
            u = []
            for (idx, iso, cl), evs in zip(units, unit_events):
                keep = evs != drop
                if keep.any():
                    u.append((idx[keep], iso[keep], cl[keep]))
            s = pooled(u)
            rng = np.random.default_rng(np.random.SeedSequence([SEED, 99, p_i, 0 if drop is None else 1]))
            lo, hi, _ = bootstrap(u, len(universe), rng, B)
            loo_rows.append(dict(part=part, events=label, observed=s["O"], expected=s["E"],
                                 R=float(ratio(s["O"], s["E"])), R_lo=lo, R_hi=hi))

    out = HERE / "out"
    iso = pd.DataFrame(iso_rows)
    iso.to_csv(out / "diagnostic_isolating_events.csv", index=False)
    loo = pd.DataFrame(loo_rows)
    loo.to_csv(out / "diagnostic_leave_top_event_out.csv", index=False)
    print(loo.to_string(index=False))
    print(iso.groupby("part").share_of_town_inside_fire.describe().to_string())
    print(iso.assign(mostly_inside=iso.share_of_town_inside_fire >= 0.5).groupby("part").mostly_inside.agg(["sum", "count"]).to_string())


if __name__ == "__main__":
    main()
