"""Stage 6: are cut-off-prone towns in councils with weaker finances? (descriptive public-finance comparison)

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage6/run_stage6.py
"""
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
STAGE1 = HERE.parent
sys.path.insert(0, str(STAGE1))
sys.path.insert(0, str(HERE))
from src import inputs  # noqa: E402
from stats6 import holm, mann_whitney_p, median_diff_ci, spearman_perm  # noqa: E402

SEED, B = 20260921, 2000
BASE_YEAR, AVG_YEARS = 2018, (2016, 2017, 2018)
MIN_EXPOSED = 8
LGA_DIR = inputs.W / "dataset_phase1/raw/lga_2021"
LGA_PARTS = ["CPG", "dbf", "prj", "shp", "shx"]
PRIMARY = "own_source_pct"
SECONDARY = ["cash_cover_months", "operating_ratio_pct", "grants_pct", "maintenance_ratio_pct", "road_km_per_1000"]
LABEL = {"own_source_pct": "Own-source revenue share (%)", "cash_cover_months": "Cash cover (months)",
         "operating_ratio_pct": "Operating ratio (%)", "grants_pct": "Grant dependence (% of revenue)",
         "maintenance_ratio_pct": "Maintenance funded (% of required)", "road_km_per_1000": "Road km per 1,000 residents"}
OUT = HERE / "out"


def norm(name):
    s = str(name).lower().replace("(nsw)", "")
    s = re.sub(r"\b(city|council|shire|regional|municipal|of|the)\b", " ", s)
    return re.sub(r"[^a-z]", "", s)


def verify_lga():
    con = duckdb.connect(str(inputs.TRANSPORT_DB), read_only=True)
    rec = dict(con.sql("select path, sha256 from analysis.supplementary_input_hashes where path ilike '%lga_2021%'").fetchall())
    con.close()
    for part in LGA_PARTS:
        p = LGA_DIR / f"LGA_2021_AUST_GDA94.{part}"
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if rec.get(str(p)) != got:
            raise SystemExit(f"HASH MISMATCH or missing provenance for {p}")


def main():
    t0 = dt.datetime.now(dt.timezone.utc)
    OUT.mkdir(exist_ok=True)
    inputs.verify_inputs()
    verify_lga()
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)

    # Towns and their cut-off history (stage 2, S0, 20 km)
    cl = pd.read_parquet(STAGE1 / "stage2/out/community_level.parquet")
    cl = cl[(cl.rule == "S0") & (cl.ring_radius_km == 20) & cl.part.isin(["A", "B"])]
    town = cl.groupby("ucl_code").agg(town=("ucl_name", "first"), population=("population", "first"),
                                      cutoffs=("isolations", "sum"), fires_cutting_exit=("fires_closing_any_exit", "sum"))
    town["ever_cut_off"] = town.cutoffs > 0
    town["fire_touched"] = town.fires_cutting_exit > 0

    # Town -> council by largest area overlap
    ucl = inputs.load_communities().set_index("UCL_CODE21")
    ucl = ucl.loc[ucl.index.intersection(town.index)]
    ucl.index.name = "UCL_CODE21"
    lga = gpd.read_file(LGA_DIR / "LGA_2021_AUST_GDA94.shp")
    lga = lga[lga.STE_NAME21 == "New South Wales"].to_crs(3577)[["LGA_CODE21", "LGA_NAME21", "geometry"]]
    ov = gpd.overlay(ucl.reset_index()[["UCL_CODE21", "geometry"]], lga, how="intersection", keep_geom_type=True)
    ov["a"] = ov.area
    best = ov.sort_values("a", ascending=False).drop_duplicates("UCL_CODE21").set_index("UCL_CODE21")
    town = town.join(best[["LGA_CODE21", "LGA_NAME21"]])
    town["lga_key"] = town.LGA_NAME21.map(norm)

    # Council finances
    con = duckdb.connect(str(inputs.AUSSEF_DB), read_only=True)
    fin = con.sql("""select council_id, council_name, year_start, own_source_pct, cash_cover_months, operating_ratio_pct,
                     grants_pct, maintenance_ratio_pct, road_km, population from master.fiscal_panel_extended""").df()
    con.close()
    fin["lga_key"] = fin.council_name.map(norm)
    fin["road_km_per_1000"] = np.where(fin.population > 0, fin.road_km / fin.population * 1000, np.nan)
    measures = [PRIMARY] + SECONDARY
    base = fin[fin.year_start == BASE_YEAR].groupby("lga_key")[measures + ["council_name", "population"]].first()
    avg = fin[fin.year_start.isin(AVG_YEARS)].groupby("lga_key")[measures].mean()

    # Council table
    g = town.groupby("lga_key").agg(lga_name=("LGA_NAME21", "first"), towns=("town", "size"),
                                    towns_cut_off=("ever_cut_off", "sum"), towns_fire_touched=("fire_touched", "sum"),
                                    residents_in_cut_off_towns=("population", lambda s: s[town.loc[s.index, "ever_cut_off"]].sum()))
    council = g.join(base, how="left")
    matched = council.council_name.notna()
    unmatched = council.loc[~matched, "lga_name"].tolist()
    council = council[matched].copy()
    council["group"] = np.where(council.towns_cut_off > 0, "exposed",
                                np.where(council.towns_fire_touched > 0, "fire-touched, never cut off", "other"))
    council["exposed_resident_share"] = council.residents_in_cut_off_towns / council.population
    council.to_csv(OUT / "council_table.csv")

    rng = np.random.default_rng(SEED)
    exp = council[council.group == "exposed"]
    rows = []

    def compare(measure, a, b, label_b, baseline):
        x, y = a[measure].dropna(), b[measure].dropna()
        if len(x) == 0 or len(y) == 0:
            return dict(measure=measure, comparison=label_b, baseline=baseline, n_exposed=len(x), n_comparison=len(y))
        est, lo, hi = median_diff_ci(x, y, rng, B)
        return dict(measure=measure, comparison=label_b, baseline=baseline, n_exposed=len(x), n_comparison=len(y),
                    median_exposed=float(np.median(x)), median_comparison=float(np.median(y)),
                    diff=est, diff_lo=lo, diff_hi=hi, p_mwu=mann_whitney_p(x, y))

    others = council[council.group != "exposed"]
    for m in measures:
        rows.append(compare(m, exp, others, "all other councils", "2018-19"))
    res = pd.DataFrame(rows)
    sec = res.measure.isin(SECONDARY)
    res.loc[sec, "p_holm"] = holm(res.loc[sec, "p_mwu"].values)
    # sensitivity
    sens = [compare(PRIMARY, exp, council[council.group == "fire-touched, never cut off"],
                    "fire-touched, never cut off", "2018-19")]
    av = council[["group"]].join(avg)
    sens.append(compare(PRIMARY, av[av.group == "exposed"], av[av.group != "exposed"], "all other councils",
                        "2016-17 to 2018-19 average"))
    # Post-hoc (DEVIATIONS.md W1): the legacy panel covers the 2016-amalgamated councils missing from the extended panel.
    con = duckdb.connect(str(inputs.AUSSEF_DB), read_only=True)
    leg = con.sql(f"select council, own_source_pct from master.fiscal_panel_legacy where year_start = {BASE_YEAR}").df()
    con.close()
    leg["lga_key"] = leg.council.map(norm)
    leg = leg.groupby("lga_key").own_source_pct.first()
    allg = g.assign(group=np.where(g.towns_cut_off > 0, "exposed", "not exposed")).join(leg, how="inner")
    legacy_unmatched = sorted(set(g.lga_name) - set(g.loc[allg.index, "lga_name"]))
    sens.append(compare(PRIMARY, allg[allg.group == "exposed"], allg[allg.group != "exposed"],
                        "all other councils (legacy panel, post-hoc)", "2018-19"))
    sens = pd.DataFrame(sens)
    ok = council[[PRIMARY, "exposed_resident_share"]].dropna()
    rho, p_rho = spearman_perm(ok.exposed_resident_share, ok[PRIMARY], np.random.default_rng(SEED + 1))

    prim = res[res.measure == PRIMARY].iloc[0]
    if prim.n_exposed < MIN_EXPOSED:
        verdict = "NOT EVALUABLE"
    else:
        verdict = "SUPPORTED" if (prim["diff"] < 0 and prim.diff_hi < 0) else "NOT SUPPORTED"
    res["verdict"] = np.where(res.measure == PRIMARY, verdict, "")
    res.to_csv(OUT / "stage6_results.csv", index=False)
    sens.to_csv(OUT / "stage6_sensitivity.csv", index=False)
    assert aussef_before == inputs.sha256(inputs.AUSSEF_DB), "aussef.duckdb changed"
    meta = dict(run_utc=t0.isoformat(timespec="seconds"), seed=SEED, bootstrap=B, verdict=verdict,
                towns=len(town), towns_without_lga=int(town.LGA_NAME21.isna().sum()),
                councils_with_towns=len(g), councils_matched=len(council), councils_unmatched=unmatched,
                exposed_councils=int((council.group == "exposed").sum()),
                fire_touched_councils=int((council.group == "fire-touched, never cut off").sum()),
                other_councils=int((council.group == "other").sum()),
                cut_off_towns_total=int(town.ever_cut_off.sum()),
                cut_off_towns_in_matched_councils=int(council.towns_cut_off.sum()),
                spearman_rho_exposed_share_vs_own_source=rho, spearman_perm_p=p_rho,
                legacy_councils_matched=len(allg), legacy_exposed=int((allg.group == "exposed").sum()),
                legacy_cut_off_towns=int(allg.towns_cut_off.sum()), legacy_unmatched=legacy_unmatched,
                aussef_duckdb_sha256=aussef_before)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    import report6
    report6.write_all(res, sens, council, meta)
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: inputs and LGA hashes matched; aussef.duckdb unchanged; primary: **{verdict}** "
                f"(median own-source difference {prim['diff']:.1f} pp, 95% CI {prim.diff_lo:.1f} to {prim.diff_hi:.1f}; "
                f"{int(prim.n_exposed)} exposed vs {int(prim.n_comparison)} other councils).\n")
    print(json.dumps({k: v for k, v in meta.items() if k not in ("councils_unmatched", "legacy_unmatched")}, indent=2, default=str))
    print("legacy unmatched:", legacy_unmatched)
    print("unmatched:", unmatched)
    print(res.round(3).to_string())
    print(sens.round(3).to_string())


if __name__ == "__main__":
    main()
