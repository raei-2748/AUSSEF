"""Stage 9: which towns a count-based standard rates as safe although fire cut them off; who lives there; who pays.

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage9/run_stage9.py
"""
import datetime as dt
import io
import json
import sys
import zipfile
from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

HERE = Path(__file__).resolve().parent
STAGE1, STAGE6 = HERE.parent, HERE.parent / "stage6"
for p in (STAGE1, STAGE6, HERE):
    sys.path.insert(0, str(p))
from src import inputs  # noqa: E402
from run_stage6 import LGA_DIR, norm, verify_lga  # noqa: E402
from stats6 import holm, mann_whitney_p, median_diff_ci  # noqa: E402
from s9.counted_exits import counted_exits  # noqa: E402
from s9.ownership import label_edges, length_shares, load_categorisation  # noqa: E402

SEED, B, MIN_TOWNS = 20260921, 2000, 10
T_PRIMARY, T_SECONDARY = 6, 3
DATA = STAGE1 / "data"
CAT_ZIP = DATA / "nsw_road_network_categorisation.zip"
CAT_SHA = "28f90c51f76bb4ee61a42367cfe86f80a8ca19505d141a7be2de227b91e2e168"
GCP21 = DATA / "2021_GCP_UCL_for_NSW_short-header.zip"
GCP21_SHA = "19eca38d9d92c612d4083551535a53c730f30683205a16b26098235d17fc7aaf"
OLG = inputs.W / "transport_criticality_experiment/inputs/olg_road_expenditure_panel.csv"
MEASURES = {"pct_65_plus": "Residents aged 65+ (%)", "pct_need_assistance": "Need assistance (%)",
            "pct_no_car": "Dwellings with no car (%)", "pct_lone_person_hh": "One-person households (%)",
            "pct_rented": "Rented dwellings (%)", "median_hh_income_weekly": "Median household income ($/wk)"}
PRIMARY = "pct_65_plus"
OUT = HERE / "out"


def census21():
    if inputs.sha256(GCP21) != GCP21_SHA:
        raise SystemExit(f"HASH MISMATCH for {GCP21}")
    z = zipfile.ZipFile(GCP21)

    def t(name):
        n = next(x for x in z.namelist() if x.endswith(f"2021Census_{name}_NSW_UCL.csv"))
        return pd.read_csv(io.BytesIO(z.read(n))).set_index("UCL_CODE_2021")

    g01, g02, g18, g34, g35, g37 = t("G01"), t("G02"), t("G18"), t("G34"), t("G35"), t("G37")
    d = pd.DataFrame(index=g01.index)
    d["persons"] = g01.Tot_P_P
    d["aged_65_plus"] = g01.Age_65_74_yr_P + g01.Age_75_84_yr_P + g01.Age_85ov_P
    d["need_assistance"] = g18.P_Tot_Need_for_assistance
    d["dwellings_no_car"] = g34.Num_MVs_per_dweling_0_MVs
    hh35 = g35.Total_Total
    hh37 = g37.Total_Total if "Total_Total" in g37.columns else g37.filter(regex="_Total$").sum(axis=1)
    d["pct_65_plus"] = np.where(d.persons > 0, 100 * d.aged_65_plus / d.persons, np.nan)
    ast_den = g18.P_Tot_Tot - g18.P_Tot_Need_for_assistance_ns
    d["pct_need_assistance"] = np.where(ast_den > 0, 100 * d.need_assistance / ast_den, np.nan)
    d["pct_no_car"] = np.where(g34.Num_MVs_per_dweling_Tot > 0, 100 * d.dwellings_no_car / g34.Num_MVs_per_dweling_Tot, np.nan)
    d["pct_lone_person_hh"] = np.where(hh35 > 0, 100 * g35.Num_Psns_UR_1_Total / hh35, np.nan)
    d["pct_rented"] = np.where(hh37 > 0, 100 * g37.R_Tot_Total / hh37, np.nan)
    d["median_hh_income_weekly"] = g02.Median_tot_hhd_inc_weekly.where(g02.Median_tot_hhd_inc_weekly > 0)
    d.index = d.index.str.removeprefix("UCL")
    return d


def main():
    t0 = dt.datetime.now(dt.timezone.utc)
    OUT.mkdir(exist_ok=True)
    inputs.verify_inputs()
    verify_lga()
    if inputs.sha256(CAT_ZIP) != CAT_SHA:
        raise SystemExit(f"HASH MISMATCH for {CAT_ZIP}")
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)
    print("inputs verified", flush=True)

    net = inputs.load_network()
    edges, geom = net["edges"], net["geom"]
    # load_network keeps only the columns earlier stages used; counted exits also need ref/name.
    import pyarrow.parquet as pq
    tags = pq.read_table(inputs.NETWORK, columns=["edge_id", "ref", "name"]).to_pandas().drop_duplicates("edge_id")
    edges = edges.merge(tags, on="edge_id", how="left")
    ucl = inputs.load_communities().set_index("UCL_CODE21", drop=False)
    cl = pd.read_parquet(STAGE1 / "stage2/out/community_level.parquet")
    cl = cl[(cl.rule == "S0") & (cl.ring_radius_km == 20) & cl.part.isin(["A", "B"])]
    town = cl.groupby("ucl_code").agg(town=("ucl_name", "first"), max_flow_exits=("exits", "max"),
                                      cutoffs=("isolations", "sum"))
    town["ever_cut_off"] = town.cutoffs > 0

    tree = shapely.STRtree(geom)
    cnt = {c: counted_exits(ucl.loc[c, "geometry"], edges, geom, tree) for c in town.index}
    town["counted_exits"] = [cnt[c][0] for c in town.index]
    town["distinct_roads_crossing"] = [cnt[c][1] for c in town.index]
    town = town.join(census21())
    for T, tag in ((T_PRIMARY, "T6"), (T_SECONDARY, "T3")):
        town[f"group_{tag}"] = np.where(town.counted_exits < T, "rated at risk",
                                        np.where(town.ever_cut_off, "illusory redundancy", "correctly rated safe"))
        # Post-hoc variant without the "divide by two" (DEVIATIONS U1), reported alongside.
        town[f"group_nohalve_{tag}"] = np.where(town.distinct_roads_crossing < T, "rated at risk",
                                                np.where(town.ever_cut_off, "illusory redundancy", "correctly rated safe"))
    print("classified", town.group_T6.value_counts().to_dict(), flush=True)

    # ---- social comparisons
    rng = np.random.default_rng(SEED)
    rows = []
    for T, tag in ((T_PRIMARY, "T6"), (T_SECONDARY, "T3"), (T_PRIMARY, "nohalve_T6"), (T_SECONDARY, "nohalve_T3")):
        a = town[town[f"group_{tag}"] == "illusory redundancy"]
        b = town[town[f"group_{tag}"] == "correctly rated safe"]
        for m in MEASURES:
            x, y = a[m].dropna(), b[m].dropna()
            r = dict(threshold=T, variant=tag, measure=m, n_illusory=len(x), n_safe=len(y))
            if len(x) and len(y):
                est, lo, hi = median_diff_ci(x, y, rng, B)
                r.update(median_illusory=float(np.median(x)), median_safe=float(np.median(y)),
                         diff=est, diff_lo=lo, diff_hi=hi, p_mwu=mann_whitney_p(x, y))
            rows.append(r)
    res = pd.DataFrame(rows)
    sec = (res.variant == "T6") & (res.measure != PRIMARY) & res.get("p_mwu", pd.Series(dtype=float)).notna()
    if sec.any():
        res.loc[sec, "p_holm"] = holm(res.loc[sec, "p_mwu"].values)
    p = res[(res.variant == "T6") & (res.measure == PRIMARY)].iloc[0]
    if min(p.n_illusory, p.n_safe) < MIN_TOWNS:
        verdict = "NOT EVALUABLE"
    elif pd.notna(p.get("diff_lo")) and p.diff_lo > 0:
        verdict = "SUPPORTED"
    elif pd.notna(p.get("diff_hi")) and p.diff_hi < 0:
        verdict = "OPPOSITE"
    else:
        verdict = "NOT SUPPORTED"
    res["verdict"] = np.where((res.variant == "T6") & (res.measure == PRIMARY), verdict, "")

    # ---- cut-off rate by measure bucket
    def bucket_rate(col):
        b = pd.cut(town[col], [-0.1, 0.9, 1.9, 2.9, 3.9, 5.9, np.inf],
                   labels=["0", "1", "2", "3", "4-5", "6+"])
        g = town.groupby(b, observed=False).agg(towns=("ever_cut_off", "size"), cut_off=("ever_cut_off", "sum"))
        g["cut_off_rate_pct"] = 100 * g.cut_off / g.towns.replace(0, np.nan)
        return g.reset_index().rename(columns={col: "bucket"})

    buckets = pd.concat([bucket_rate("counted_exits").assign(measure="counted exits (PNAS-style)"),
                         bucket_rate("max_flow_exits").assign(measure="max-flow exits (this project)")])
    buckets.columns = ["bucket", "towns", "cut_off", "cut_off_rate_pct", "measure"]

    # ---- ownership of exit routes
    cat_geom, cat_class = load_categorisation(CAT_ZIP)
    paths = pd.read_parquet(STAGE1 / "out/exit_paths.parquet")
    paths = paths[paths.ring_radius_km == 20]
    used = sorted({int(e) for lst in paths.edge_ids for e in lst})
    pos = pd.Series(np.arange(len(edges)), index=edges.edge_id.values)
    idx = pos.loc[used].values
    labels = label_edges(np.array(used), np.asarray(geom, dtype=object)[idx], cat_geom, cat_class)
    elen = dict(zip(edges.edge_id.values, edges.length_m.values))
    con = duckdb.connect(str(inputs.TRANSPORT_DB), read_only=True)
    ov = con.sql("select disaster_family_id, edge_id from analysis.fire_road_exposure_v2 where direct_burned_m > 0").df()
    con.close()
    closed_any = set(ov.edge_id.astype(int)) & set(used)
    own_rows = []
    for code, g in paths.groupby("ucl_code"):
        eids = [int(e) for lst in g.edge_ids for e in lst]
        lens = [elen[e] for e in eids]
        sh = length_shares(eids, lens, labels)
        cut_e = [e for e in eids if e in closed_any]
        sh_cut = length_shares(cut_e, [elen[e] for e in cut_e], labels) if cut_e else {}
        own_rows.append(dict(ucl_code=code, exit_km=sum(lens) / 1000,
                             state_share=sh.get("State", 0.0), regional_share=sh.get("Regional", 0.0),
                             local_share=sh.get("local", 0.0), burned_exit_km=sum(elen[e] for e in cut_e) / 1000,
                             burned_state_share=sh_cut.get("State", np.nan),
                             burned_regional_share=sh_cut.get("Regional", np.nan),
                             burned_local_share=sh_cut.get("local", np.nan)))
    own = pd.DataFrame(own_rows).set_index("ucl_code")
    town = town.join(own)

    # ---- councils
    ucl_t = ucl.loc[ucl.index.intersection(town.index)]
    ucl_t.index.name = "UCL_CODE21"
    lga = gpd.read_file(LGA_DIR / "LGA_2021_AUST_GDA94.shp")
    lga = lga[lga.STE_NAME21 == "New South Wales"].to_crs(3577)[["LGA_NAME21", "geometry"]]
    ovl = gpd.overlay(ucl_t.reset_index(drop=True)[["UCL_CODE21", "geometry"]], lga, how="intersection", keep_geom_type=True)
    ovl["a"] = ovl.area
    best = ovl.sort_values("a", ascending=False).drop_duplicates("UCL_CODE21").set_index("UCL_CODE21")
    town = town.join(best.LGA_NAME21)
    town["lga_key"] = town.LGA_NAME21.map(norm)
    con = duckdb.connect(str(inputs.AUSSEF_DB), read_only=True)
    fin = con.sql("""select council_name, own_source_pct, grants_pct, total_revenue_including_capital_aud,
                     population, road_km from master.fiscal_panel_extended where year_start = 2018""").df()
    con.close()
    fin["lga_key"] = fin.council_name.map(norm)
    fin["own_source_aud"] = fin.total_revenue_including_capital_aud * fin.own_source_pct / 100
    fin = fin.groupby("lga_key").first()
    # Reporting variant: the pre-registered primary (T6) when it yields towns, else the first variant that does
    # (pre-registered secondary T3, then the unhalved variants). Logged in DECISIONS.md / DEVIATIONS.md.
    variants = ["T6", "T3", "nohalve_T6", "nohalve_T3"]
    totals_by_variant = {v: int((town[f"group_{v}"] == "illusory redundancy").sum()) for v in variants}
    report_variant = max(variants, key=lambda v: totals_by_variant[v]) if any(totals_by_variant.values()) else "T6"
    ill = town[town[f"group_{report_variant}"] == "illusory redundancy"]
    council = ill.groupby("lga_key").agg(council=("LGA_NAME21", "first"), towns=("town", "size"),
                                         residents=("persons", "sum"), aged_65_plus=("aged_65_plus", "sum"),
                                         burned_exit_km=("burned_exit_km", "sum"),
                                         state_share=("state_share", "mean")).join(fin, how="left")
    council["own_source_per_resident_aud"] = council.own_source_aud / council.population
    council["own_source_per_65plus_aud"] = council.own_source_aud / council.aged_65_plus.replace(0, np.nan)

    # ---- exploratory indicative cost
    olg = pd.read_csv(OLG)
    olg = olg[olg.year_start == 2018][["council_name", "roads_bridges_footpaths_expenditure_aud"]]
    olg["lga_key"] = olg.council_name.map(norm)
    spend = olg.groupby("lga_key").roads_bridges_footpaths_expenditure_aud.first()
    council = council.join(spend)
    council["road_spend_per_km_aud"] = council.roads_bridges_footpaths_expenditure_aud / council.road_km
    council["indicative_annual_cost_aud"] = council.road_spend_per_km_aud * council.burned_exit_km
    q = council.indicative_annual_cost_aud.dropna()
    cost = dict(councils=len(q), total=float(q.sum()) if len(q) else np.nan,
                q1=float(q.quantile(0.25)) if len(q) else np.nan, median=float(q.median()) if len(q) else np.nan,
                q3=float(q.quantile(0.75)) if len(q) else np.nan,
                spend_per_km_median=float(council.road_spend_per_km_aud.median(skipna=True)))

    town.to_csv(OUT / "town_classification.csv")
    res.to_csv(OUT / "stage9_results.csv", index=False)
    buckets.to_csv(OUT / "cutoff_rate_by_bucket.csv", index=False)
    town[["town", "exit_km", "state_share", "regional_share", "local_share", "burned_exit_km",
          "burned_state_share", "burned_local_share", "group_T6"]].to_csv(OUT / "ownership_by_town.csv")
    council.to_csv(OUT / "council_capacity.csv")
    assert aussef_before == inputs.sha256(inputs.AUSSEF_DB), "aussef.duckdb changed"
    tt = dict(towns=int(len(ill)), residents=int(ill.persons.sum()), aged_65_plus=int(ill.aged_65_plus.sum()),
              need_assistance=int(ill.need_assistance.sum()), dwellings_no_car=int(ill.dwellings_no_car.sum()))
    town["group_reported"] = town[f"group_{report_variant}"]
    meta = dict(run_utc=t0.isoformat(timespec="seconds"), seed=SEED, bootstrap=B, verdict=verdict,
                groups_T6=town.group_T6.value_counts().to_dict(), groups_T3=town.group_T3.value_counts().to_dict(),
                groups_nohalve_T6=town.group_nohalve_T6.value_counts().to_dict(),
                groups_nohalve_T3=town.group_nohalve_T3.value_counts().to_dict(),
                illusory_towns_by_variant=totals_by_variant, report_variant=report_variant,
                illusory_totals=tt, cost=cost,
                state_share_all=float(town.state_share.mean()), state_share_illusory=float(ill.state_share.mean()),
                burned_state_share_illusory=float(ill.burned_state_share.mean(skipna=True)),
                councils_missing_finance=council.loc[council.own_source_aud.isna(), "council"].tolist(),
                aussef_duckdb_sha256=aussef_before)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    import report9
    report9.write_all(res, buckets, town, council, meta)
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: all input hashes matched; aussef.duckdb unchanged; "
                f"illusory-redundancy towns (T=6): {tt['towns']} with {tt['residents']:,} residents; primary social "
                f"verdict **{verdict}**.\n")
    print(json.dumps(meta, indent=2, default=str))
    print(res.round(2).to_string())
    print(buckets.to_string(index=False))


if __name__ == "__main__":
    main()
