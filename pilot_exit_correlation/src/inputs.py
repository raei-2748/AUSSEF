"""Read-only input loading with SHA-256 verification against the frozen RUN_LOG baseline."""
import hashlib
from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import shapely

REPO = Path(__file__).resolve().parents[2]
PILOT = REPO / "pilot_exit_correlation"
W = Path("/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0")

NETWORK = W / "transport_criticality_experiment/inputs/network_fingerprint.parquet"
TRANSPORT_DB = W / "transport_criticality_experiment/transport_criticality.duckdb"
PERIMETERS = W / "dataset_phase1/data/event_perimeters.gpkg"
UCL_SHP = PILOT / "data/ucl_2021/UCL_2021_AUST_GDA2020.shp"
UCL_POP = PILOT / "data/gcp_ucl_nsw/2021 Census GCP Urban Centres and Localities for NSW/2021Census_G01_NSW_UCL.csv"

FROZEN = {
    NETWORK: "5d6049c30fcb63f66c21b3cf75edbc5d542c05a4a385e07352d7668bc90a5026",
    TRANSPORT_DB: "b9779b309dcacb0a7b5c65168537e85e41c6c77b5e8c80e01e1e8e25f3bb3119",
    PERIMETERS: "75fb91a17a6ce65c44a34ccc8e0f2350151e38201ef715feecb5c26c6efb542c",
    UCL_SHP: "c8b3902ca189abe7acf7676cf5339cd8673682a9a05a20592aad7d80fb937641",
    UCL_POP: "bded5c0201c9f92168db6497a239c8227ae68f4a3a643bc0c18971a29fa4374c",
}
AUSSEF_DB = REPO / "data/aussef.duckdb"
CRS = 3577


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def verify_inputs() -> dict:
    """Stop on any mismatch; return observed hashes."""
    observed = {}
    for path, expected in FROZEN.items():
        got = sha256(path)
        observed[str(path)] = got
        if got != expected:
            raise SystemExit(f"HASH MISMATCH for {path}: expected {expected}, got {got}. Stopping.")
    return observed


def load_network():
    """Edges excluding highway=service, with integer node indices and coordinates."""
    t = pq.read_table(NETWORK, columns=["edge_id", "u", "v", "highway", "length_m", "geometry"])
    df = t.to_pandas()
    n_all = len(df)
    df = df[df.highway != "service"].reset_index(drop=True)
    geom = shapely.from_wkb(df.geometry.values)
    first = shapely.get_coordinates(shapely.get_point(geom, 0))
    last = shapely.get_coordinates(shapely.get_point(geom, -1))
    df = df.drop(columns="geometry")
    # Node ids -> coordinates (first seen wins; shared nodes have identical coordinates).
    ids = np.concatenate([df.u.values, df.v.values])
    xy = np.vstack([first, last])
    node_ids, idx = np.unique(ids, return_index=True)
    node_xy = xy[idx]
    df["ui"] = np.searchsorted(node_ids, df.u.values)
    df["vi"] = np.searchsorted(node_ids, df.v.values)
    loop = (df.ui == df.vi).values  # drop self-loops
    df, geom = df[~loop].reset_index(drop=True), geom[~loop]
    return {"edges": df, "geom": geom, "node_ids": node_ids, "node_xy": node_xy,
            "n_edges_all": n_all, "n_edges_used": len(df)}


def load_overlay():
    con = duckdb.connect(str(TRANSPORT_DB), read_only=True)
    ov = con.sql("""select disaster_family_id, edge_id, highway, direct_burned_m, nearest_burn_distance_m
                    from analysis.fire_road_exposure_v2""").df()
    members = con.sql("select * from main.disaster_family_members").df()
    con.close()
    return ov, members


def load_family_geometries(members: pd.DataFrame) -> gpd.GeoDataFrame:
    fires = gpd.read_file(PERIMETERS)[["event_id", "geometry"]]
    assert fires.crs.to_epsg() == CRS
    m = members[["disaster_family_id", "event_id", "fire_season", "family_start_date"]].merge(fires, on="event_id", how="left")
    missing = m.geometry.isna().sum()
    fam = gpd.GeoDataFrame(m.dropna(subset=["geometry"]), geometry="geometry", crs=CRS)
    fam = fam.dissolve("disaster_family_id", aggfunc={"fire_season": "first", "family_start_date": "min"}).reset_index()
    fam.attrs["members_without_geometry"] = int(missing)
    return fam


def load_communities() -> gpd.GeoDataFrame:
    ucl = gpd.read_file(UCL_SHP)
    ucl = ucl[(ucl.STE_NAME21 == "New South Wales") & ucl.geometry.notna()].copy()
    pop = pd.read_csv(UCL_POP, usecols=["UCL_CODE_2021", "Tot_P_P"])
    pop["UCL_CODE21"] = pop.UCL_CODE_2021.str.removeprefix("UCL")
    ucl = ucl.merge(pop[["UCL_CODE21", "Tot_P_P"]], on="UCL_CODE21", how="left")
    ucl = ucl.rename(columns={"Tot_P_P": "population"})
    ucl = ucl[ucl.population >= 200].to_crs(CRS).reset_index(drop=True)
    return ucl[["UCL_CODE21", "UCL_NAME21", "SOS_NAME21", "population", "AREASQKM21", "geometry"]]
