"""Split each fire by NSW council (LGA 2021) and measure road exposure inside each piece."""
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from src.common import CRS, PHASE1, REPO

sys.path.insert(0, str(REPO / "pilot_exit_correlation"))
from src_pilot_shim import load_network  # noqa: E402  (thin shim, see below)

LGA_SHP = PHASE1 / "raw/lga_2021/LGA_2021_AUST_GDA94.shp"


def load_lgas():
    lga = gpd.read_file(LGA_SHP)
    lga = lga[lga.STE_NAME21 == "New South Wales"].to_crs(CRS)
    return lga[["LGA_CODE21", "LGA_NAME21", "AREASQKM21", "geometry"]].reset_index(drop=True)


def split_by_lga(ev, lga):
    pieces = gpd.overlay(ev[["event_id", "geometry"]], lga, how="intersection", keep_geom_type=True)
    pieces["region_burn_area_ha"] = pieces.area / 1e4
    tot = ev.set_index("event_id").burn_area_ha
    pieces["region_share_of_fire"] = pieces.region_burn_area_ha / pieces.event_id.map(tot)
    pieces["share_of_region_burned"] = pieces.region_burn_area_ha / (pieces.AREASQKM21 * 100)
    return pieces


def road_exposure(pieces):
    """Road km (2019 OSM, excluding service roads) inside each fire × LGA piece, and within 100 m of it."""
    net = load_network()
    tree = shapely.STRtree(net["geom"])
    geoms = pieces.geometry.values
    km_in, km_100 = [], []
    for g in geoms:
        idx = tree.query(g, predicate="intersects")
        km_in.append(float(shapely.length(shapely.intersection(net["geom"][idx], g)).sum()) / 1000 if len(idx) else 0.0)
        buf = shapely.buffer(g, 100)
        idx2 = tree.query(buf, predicate="intersects")
        km_100.append(float(shapely.length(shapely.intersection(net["geom"][idx2], buf)).sum()) / 1000 if len(idx2) else 0.0)
    pieces["road_km_inside"] = km_in
    pieces["road_km_within_100m"] = km_100
    return pieces
