"""Stage 10: closure validation with traffic counters, escape window, short-run disruption, fiscal go/no-go.

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage10/run_stage10.py
"""
import datetime as dt
import json
import sys
from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
import shapely

HERE = Path(__file__).resolve().parent
STAGE1, STAGE2, STAGE3, STAGE6 = HERE.parent, HERE.parent / "stage2", HERE.parent / "stage3", HERE.parent / "stage6"
for p in (STAGE1, STAGE2, STAGE3, STAGE6, HERE):
    sys.path.insert(0, str(p))
import run_stage3 as s3run  # noqa: E402
from src import inputs  # noqa: E402
from s2 import historical  # noqa: E402
from run_stage6 import LGA_DIR, norm, verify_lga  # noqa: E402
from s10 import disruption, fiscal_charts, traffic, validate  # noqa: E402

PAIR_START, PAIR_END = pd.Timestamp("2006-01-01", tz="UTC"), pd.Timestamp("2020-04-30", tz="UTC")
BS_START, BS_END = pd.Timestamp("2019-07-01", tz="UTC"), pd.Timestamp("2020-06-30", tz="UTC")
MATCH_M, CORRIDOR_M = 30, 5000
OLG = inputs.W / "transport_criticality_experiment/inputs/olg_road_expenditure_panel.csv"
OUT = HERE / "out"


def main():
    t0 = dt.datetime.now(dt.timezone.utc)
    OUT.mkdir(exist_ok=True)
    inputs.verify_inputs()
    verify_lga()
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)
    con = duckdb.connect(str(inputs.AUSSEF_DB), read_only=True)
    n_rows, fp = traffic.fingerprint(con)
    print(f"inputs verified; traffic raw rows {n_rows:,} fingerprint {fp[:16]}", flush=True)

    # ---- network, fires, events
    net = inputs.load_network()
    overlay, members = inputs.load_overlay()
    famA = inputs.load_family_geometries(members)
    g, _ = historical.load_fires()
    evB = historical.families(g)
    events = s3run.event_tables(members, famA, g, evB)
    edge_ids = net["edges"].edge_id.values

    # ---- stations -> edges
    active = {r[0] for r in con.sql(" union ".join(f"select distinct station_key from raw.{t}" for t in traffic.tables(con))).fetchall()}
    ref = traffic.station_locations(con)
    ref = ref[ref.station_key.isin(active)].reset_index(drop=True)
    tr = pyproj.Transformer.from_crs(4326, 3577, always_xy=True)
    x, y = tr.transform(ref.lon.values, ref.lat.values)
    tree = shapely.STRtree(net["geom"])
    i, j = tree.query_nearest(shapely.points(np.c_[x, y]), max_distance=MATCH_M, return_distance=False, all_matches=False)
    station_edge = pd.DataFrame({"station_key": ref.station_key.values[i], "edge_id": edge_ids[j]}).drop_duplicates("station_key")
    edge_geom = dict(zip(edge_ids, net["geom"]))
    print(f"stations with data {len(active)}, matched to an edge within {MATCH_M} m: {len(station_edge)}", flush=True)

    # ---- Part A
    pairs = validate.build_pairs(station_edge, edge_geom, events, PAIR_START, PAIR_END)
    dA = traffic.daily(con, sorted(set(pairs.station_key)), ("0", "2", "3"))
    allA = traffic.all_vehicles(dA)
    pairs = validate.observe(pairs, allA)
    rows = [validate.summarise(pairs, rule, thr) for rule in ("s0", "s0_half", "s100") for thr in (20, 50)]
    resA = pd.DataFrame(rows)
    resA["interpretation"] = [validate.interpret(r) if (r["rule"], r["threshold_pct"]) == ("s0", 20) else ""
                              for r in resA.to_dict("records")]
    verdictA = resA.loc[(resA.rule == "s0") & (resA.threshold_pct == 20), "interpretation"].iloc[0]
    pairs.drop(columns=[]).to_csv(OUT / "closure_validation_pairs.csv", index=False)
    resA.to_csv(OUT / "closure_validation_summary.csv", index=False)
    print("Part A:", verdictA, resA.round(3).to_dict("records")[0], flush=True)

    # ---- Part B
    tp = pd.read_parquet(STAGE1 / "stage4/out/timing_pairs_near_town.parquet")
    s = tp.spread_hours_K5km
    partB = dict(cutoffs=len(tp), dated=int(s.notna().sum()), undated=int(s.isna().sum()),
                 median_h=float(s.median()), q1_h=float(s.quantile(0.25)), q3_h=float(s.quantile(0.75)),
                 within_6h=int((s <= 6).sum()), within_12h=int((s <= 12).sum()), within_24h=int((s <= 24).sum()))
    tp.sort_values("spread_hours_K5km")[["town", "event_id", "part", "exits", "spread_hours_K5km", "first_hit_K5km"]] \
        .to_csv(OUT / "escape_window.csv", index=False)

    # ---- Part C
    bs = events[(events.part == "A") & (events.start >= BS_START) & (events.start <= BS_END)]
    sg = np.asarray([edge_geom[e] for e in station_edge.edge_id], dtype=object)
    near = np.unique(shapely.STRtree(sg).query(np.asarray(bs.geometry.values, dtype=object), predicate="dwithin", distance=CORRIDOR_M)[1])
    c_stations = station_edge.station_key.values[near]
    dC = traffic.daily(con, sorted(set(c_stations)), ("0", "2", "3"))
    allC = traffic.all_vehicles(dC)
    heavyC = dC[dC.cls == "3"]
    crow = []
    for label, frame in (("all vehicles", allC), ("heavy (freight)", heavyC)):
        for st, grp in frame.groupby("station_key"):
            r = disruption.station_deficit(grp.set_index("d").volume)
            crow.append(dict(station_key=st, vehicle_class=label, **r))
    partC = pd.DataFrame(crow)
    partC.to_csv(OUT / "corridor_disruption.csv", index=False)
    cmp_ = partC[partC.weeks_compared > 0]
    totC = cmp_.groupby("vehicle_class").agg(stations=("station_key", "nunique"), weeks_compared=("weeks_compared", "sum"),
                                              station_weeks_below_80=("weeks_below_80", "sum"),
                                              stations_any_week_below_80=("weeks_below_80", lambda x: int((x > 0).sum())),
                                              net_deficit_trips=("net_deficit_trips", "sum"),
                                              baseline_trips=("baseline_trips", "sum"),
                                              median_deepest_ratio=("deepest_ratio", "median")).reset_index()
    totC["net_deficit_pct"] = 100 * totC.net_deficit_trips / totC.baseline_trips
    totC.to_csv(OUT / "corridor_disruption_totals.csv", index=False)
    print("Part C:", totC.round(3).to_dict("records"), flush=True)

    # ---- Part D
    town = pd.read_csv(STAGE1 / "stage8/out/town_change_2016_2021.csv", dtype={"ucl_code": str}).set_index("ucl_code")
    ucl = inputs.load_communities().set_index("UCL_CODE21", drop=False)
    ucl_t = ucl.loc[ucl.index.intersection(town.index)].reset_index(drop=True)
    lga = gpd.read_file(LGA_DIR / "LGA_2021_AUST_GDA94.shp")
    lga = lga[lga.STE_NAME21 == "New South Wales"].to_crs(3577)[["LGA_NAME21", "geometry"]]
    ov = gpd.overlay(ucl_t[["UCL_CODE21", "geometry"]], lga, how="intersection", keep_geom_type=True)
    ov["a"] = ov.area
    best = ov.sort_values("a", ascending=False).drop_duplicates("UCL_CODE21").set_index("UCL_CODE21")
    town = town.join(best.LGA_NAME21)
    town["lga_key"] = town.LGA_NAME21.map(norm)
    cg = town.groupby("lga_key").group.agg(lambda s: "cut off" if (s == "cut off").any()
                                           else ("burned only" if (s == "burned, not cut off").any() else "untouched"))
    olg = pd.read_csv(OLG)
    olg["lga_key"] = olg.council_name.map(norm)
    olg = olg.groupby(["lga_key", "year_start"]).roads_bridges_footpaths_expenditure_aud.first().reset_index()
    fin = con.sql("select council_name, year_start, capital_grants_aud, operating_grants_aud from master.fiscal_panel_extended").df()
    con.close()
    fin["lga_key"] = fin.council_name.map(norm)
    fin["total_grants_aud"] = fin.capital_grants_aud + fin.operating_grants_aud
    fin = fin.groupby(["lga_key", "year_start"]).total_grants_aud.first().reset_index()
    gates, idx_rows = {}, []
    for label, df, col in (("road spending", olg, "roads_bridges_footpaths_expenditure_aud"),
                           ("total grants", fin, "total_grants_aud")):
        ind = fiscal_charts.index_panel(df[df.lga_key.isin(cg.index)].copy(), col)
        ind["group"] = ind.lga_key.map(cg)
        med, gaps = fiscal_charts.gap_by_year(ind)
        go, pre, post = fiscal_charts.gate(gaps)
        gates[label] = dict(go=go, pre_max_abs_gap=pre, post_max_gap=post,
                            councils=ind.groupby("group").lga_key.nunique().to_dict())
        m = med.reset_index().melt(id_vars="year_start", var_name="group", value_name="median_index")
        m["measure"] = label
        idx_rows.append(m)
    fiscal_idx = pd.concat(idx_rows)
    fiscal_idx.to_csv(OUT / "fiscal_index.csv", index=False)
    for v in gates.values():
        v["status"] = "GO" if v["go"] else ("NOT EVALUABLE (data missing)" if pd.isna(v["post_max_gap"]) or pd.isna(v["pre_max_abs_gap"]) else "NO-GO")
    verdictD = "GO" if any(v["go"] for v in gates.values()) else "NO-GO"
    print("Part D:", verdictD, gates, flush=True)

    assert aussef_before == inputs.sha256(inputs.AUSSEF_DB), "aussef.duckdb changed"
    meta = dict(run_utc=t0.isoformat(timespec="seconds"), traffic_raw_rows=n_rows, traffic_fingerprint_sha256=fp,
                stations_with_data=len(active), stations_matched=len(station_edge),
                partA_verdict=verdictA, pairs_total=len(pairs), pairs_eligible=int(pairs.eligible.sum()),
                partB=partB, partC_stations=int(len(set(c_stations))), partD_verdict=verdictD, partD_gates=gates,
                aussef_duckdb_sha256=aussef_before)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    import report10
    report10.write_all(pairs, resA, partB, tp, totC, partC, fiscal_idx, meta)
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: inputs and LGA hashes matched; traffic raw layer {n_rows:,} rows, "
                f"fingerprint `{fp}`; aussef.duckdb unchanged; Part A **{verdictA}** "
                f"({meta['pairs_eligible']} eligible pairs); Part D **{verdictD}**.\n")
    print(json.dumps({k: v for k, v in meta.items() if k not in ("partD_gates",)}, indent=2, default=str))


if __name__ == "__main__":
    main()
