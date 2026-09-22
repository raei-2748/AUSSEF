"""Stage 7: vulnerability of people in towns that get fully cut off, and their councils' own-source money.

    uv run --no-sync --with matplotlib python pilot_exit_correlation/stage7/run_stage7.py
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

HERE = Path(__file__).resolve().parent
STAGE1, STAGE6 = HERE.parent, HERE.parent / "stage6"
for p in (STAGE1, STAGE6):
    sys.path.insert(0, str(p))
from src import inputs  # noqa: E402
from run_stage6 import LGA_DIR, norm, verify_lga  # noqa: E402  (stage-6 helpers, unchanged)
from stats6 import holm, mann_whitney_p, median_diff_ci  # noqa: E402

SEED, B, MIN_TOWNS = 20260921, 2000, 15
GCP_ZIP = STAGE1 / "data/2021_GCP_UCL_for_NSW_short-header.zip"
GCP_ZIP_SHA256 = "19eca38d9d92c612d4083551535a53c730f30683205a16b26098235d17fc7aaf"
PRIMARY = "pct_65_plus"
MEASURES = {"pct_65_plus": "Residents aged 65+ (%)", "pct_no_car": "Dwellings with no car (%)",
            "pct_need_assistance": "People needing assistance with core activities (%)",
            "median_hh_income_weekly": "Median household income ($/week)"}
OUT = HERE / "out"


def census():
    got = inputs.sha256(GCP_ZIP)
    if got != GCP_ZIP_SHA256:
        raise SystemExit(f"HASH MISMATCH for {GCP_ZIP}")
    z = zipfile.ZipFile(GCP_ZIP)

    def table(t):
        name = next(n for n in z.namelist() if n.endswith(f"2021Census_{t}_NSW_UCL.csv"))
        return pd.read_csv(io.BytesIO(z.read(name))).set_index("UCL_CODE_2021")

    g01, g02, g18, g34 = table("G01"), table("G02"), table("G18"), table("G34")
    d = pd.DataFrame(index=g01.index)
    d["persons"] = g01.Tot_P_P
    d["aged_65_plus"] = g01.Age_65_74_yr_P + g01.Age_75_84_yr_P + g01.Age_85ov_P
    d["need_assistance"] = g18.P_Tot_Need_for_assistance
    ast_den = g18.P_Tot_Tot - g18.P_Tot_Need_for_assistance_ns
    d["dwellings_no_car"] = g34.Num_MVs_per_dweling_0_MVs
    car_den = g34.Num_MVs_per_dweling_Tot
    d["pct_65_plus"] = np.where(d.persons > 0, 100 * d.aged_65_plus / d.persons, np.nan)
    d["pct_no_car"] = np.where(car_den > 0, 100 * d.dwellings_no_car / car_den, np.nan)
    d["pct_need_assistance"] = np.where(ast_den > 0, 100 * d.need_assistance / ast_den, np.nan)
    d["median_hh_income_weekly"] = g02.Median_tot_hhd_inc_weekly.where(g02.Median_tot_hhd_inc_weekly > 0)
    d.index = d.index.str.removeprefix("UCL")
    return d


def main():
    t0 = dt.datetime.now(dt.timezone.utc)
    OUT.mkdir(exist_ok=True)
    inputs.verify_inputs()
    verify_lga()
    aussef_before = inputs.sha256(inputs.AUSSEF_DB)

    cl = pd.read_parquet(STAGE1 / "stage2/out/community_level.parquet")
    cl = cl[(cl.rule == "S0") & (cl.ring_radius_km == 20) & cl.part.isin(["A", "B"])]
    town = cl.groupby("ucl_code").agg(town=("ucl_name", "first"), cutoffs=("isolations", "sum"),
                                      fires_cutting_exit=("fires_closing_any_exit", "sum"))
    town["group"] = np.where(town.cutoffs > 0, "cut off",
                             np.where(town.fires_cutting_exit > 0, "fire-touched, never cut off", "never touched"))
    town = town.join(census(), how="left")

    rng = np.random.default_rng(SEED)
    cut = town[town.group == "cut off"]
    rows = []
    for comp_label, comp in (("all never-cut-off towns", town[town.group != "cut off"]),
                             ("fire-touched, never cut off", town[town.group == "fire-touched, never cut off"])):
        for m in MEASURES:
            x, y = cut[m].dropna(), comp[m].dropna()
            est, lo, hi = median_diff_ci(x, y, rng, B)
            rows.append(dict(measure=m, comparison=comp_label, n_cut_off=len(x), n_comparison=len(y),
                             median_cut_off=float(np.median(x)), median_comparison=float(np.median(y)),
                             diff=est, diff_lo=lo, diff_hi=hi, p_mwu=mann_whitney_p(x, y)))
    res = pd.DataFrame(rows)
    main_rows = (res.comparison == "all never-cut-off towns") & (res.measure != PRIMARY)
    res.loc[main_rows, "p_holm"] = holm(res.loc[main_rows, "p_mwu"].values)
    p = res[(res.measure == PRIMARY) & (res.comparison == "all never-cut-off towns")].iloc[0]
    if p.n_cut_off < MIN_TOWNS:
        verdict = "NOT EVALUABLE"
    elif p.diff_lo > 0:
        verdict = "SUPPORTED"
    elif p.diff_hi < 0:
        verdict = "OPPOSITE"
    else:
        verdict = "NOT SUPPORTED"
    res["verdict"] = np.where((res.measure == PRIMARY) & (res.comparison == "all never-cut-off towns"), verdict, "")

    # Council link (town -> council by largest overlap, as in stage 6)
    ucl = inputs.load_communities().set_index("UCL_CODE21")
    ucl = ucl.loc[ucl.index.intersection(cut.index)]
    ucl.index.name = "UCL_CODE21"
    lga = gpd.read_file(LGA_DIR / "LGA_2021_AUST_GDA94.shp")
    lga = lga[lga.STE_NAME21 == "New South Wales"].to_crs(3577)[["LGA_NAME21", "geometry"]]
    ov = gpd.overlay(ucl.reset_index()[["UCL_CODE21", "geometry"]], lga, how="intersection", keep_geom_type=True)
    ov["a"] = ov.area
    best = ov.sort_values("a", ascending=False).drop_duplicates("UCL_CODE21").set_index("UCL_CODE21")
    cut = cut.join(best.LGA_NAME21)
    cut["lga_key"] = cut.LGA_NAME21.map(norm)
    con = duckdb.connect(str(inputs.AUSSEF_DB), read_only=True)
    fin = con.sql("""select council_name, own_source_pct, total_revenue_including_capital_aud, population
                     from master.fiscal_panel_extended where year_start = 2018""").df()
    con.close()
    fin["lga_key"] = fin.council_name.map(norm)
    fin["own_source_aud"] = fin.total_revenue_including_capital_aud * fin.own_source_pct / 100
    fin = fin.groupby("lga_key").first()
    council = cut.groupby("lga_key").agg(council=("LGA_NAME21", "first"), cut_off_towns=("town", "size"),
                                         residents=("persons", "sum"), aged_65_plus=("aged_65_plus", "sum"),
                                         need_assistance=("need_assistance", "sum"),
                                         dwellings_no_car=("dwellings_no_car", "sum"))
    council = council.join(fin[["own_source_aud", "population"]], how="left")
    council["own_source_per_resident_aud"] = council.own_source_aud / council.population
    council["own_source_per_65plus_in_cutoff_towns_aud"] = council.own_source_aud / council.aged_65_plus
    council = council.sort_values("aged_65_plus", ascending=False)

    totals = dict(cut_off_towns=len(cut), residents=int(cut.persons.sum()), aged_65_plus=int(cut.aged_65_plus.sum()),
                  need_assistance=int(cut.need_assistance.sum()), dwellings_no_car=int(cut.dwellings_no_car.sum()),
                  towns_missing_census=int(cut.persons.isna().sum()))
    town.to_csv(OUT / "town_vulnerability.csv")
    res.to_csv(OUT / "stage7_results.csv", index=False)
    council.to_csv(OUT / "council_vulnerability_finance.csv")
    assert aussef_before == inputs.sha256(inputs.AUSSEF_DB), "aussef.duckdb changed"
    meta = dict(run_utc=t0.isoformat(timespec="seconds"), seed=SEED, bootstrap=B, verdict=verdict, totals=totals,
                towns=len(town), groups=town.group.value_counts().to_dict(),
                councils_missing_finance=council.loc[council.own_source_aud.isna(), "council"].tolist(),
                aussef_duckdb_sha256=aussef_before)
    (OUT / "run_meta.json").write_text(json.dumps(meta, indent=2, default=str))
    import report7
    report7.write_all(res, council, cut, meta)
    with open(HERE / "RUN_LOG.md", "a") as f:
        f.write(f"\n- {meta['run_utc']}: inputs, LGA and Census zip hashes matched; aussef.duckdb unchanged; primary: "
                f"**{verdict}** (median % aged 65+ difference {p['diff']:.1f} pp, 95% CI {p.diff_lo:.1f} to {p.diff_hi:.1f}).\n")
    print(json.dumps(meta, indent=2, default=str))
    print(res.round(3).to_string())
    print(council.round(0).to_string())


if __name__ == "__main__":
    main()
