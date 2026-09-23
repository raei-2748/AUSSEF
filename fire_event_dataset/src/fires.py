"""NSW fire events since 2015 from Geoscience Australia records (GA_V2 historical + GA_RECENT_3), with attributes.

One event = one inventory event_id (GA records sharing an event). Prescribed burns are excluded.
When the historical and recent GA layers both hold the same fire (overlapping outlines, starts within
3 days), the recent layer's record is kept.
"""
import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely

from src.common import CRS, DATA, PHASE1, START

GA_ZIP = PHASE1 / "raw/ga_original.zip"
GA_ZIP_SHA256 = "715907c149e32e0917f2533639937f5716550783c11086428cc20d5dc143e9fa"

TYPE_RANK = {"Bushfire": 0, "Unknown": 1, "Prescribed burn": 2, "Prescribed Burn": 2}


def _attributes():
    v2 = pd.read_csv(PHASE1 / "raw/fire_attributes.csv", low_memory=False)
    v2["src"], v2["oid"] = "GA_V2", v2.source_objectid.astype(str)
    rc = pd.read_csv(PHASE1 / "raw/recent_attributes_3.csv", low_memory=False)
    rc["src"], rc["oid"] = "GA_RECENT_3", rc.objectid.astype(str)
    for d in (rc,):
        for c in ("ignition_date", "capture_date", "extinguish_date"):
            d[c] = pd.to_datetime(pd.to_numeric(d[c], errors="coerce"), unit="ms", utc=True).dt.tz_localize(None)
    for c in ("ignition_date", "capture_date", "extinguish_date"):
        v2[c] = pd.to_datetime(v2[c], errors="coerce", utc=True).dt.tz_localize(None)
    cols = ["src", "oid", "fire_id", "fire_name", "ignition_date", "capture_date", "extinguish_date",
            "fire_type", "ignition_cause", "capt_method", "area_ha", "agency"]
    return pd.concat([v2[cols], rc[cols]], ignore_index=True)


def load_fire_events():
    inv = pd.read_csv(PHASE1 / "data/event_inventory.csv", low_memory=False)
    inv = inv[inv.state.astype(str).str.contains("NSW|New South", regex=True)].copy()
    inv["start"] = pd.to_datetime(inv.start_date, errors="coerce")
    inv = inv[inv.start >= START].copy()
    n_inventory = len(inv)

    # link events to their GA source records
    link = inv[["event_id", "source_objectids"]].copy()
    link["rec"] = link.source_objectids.astype(str).str.split(";")
    link = link.explode("rec")
    link[["src", "oid"]] = link.rec.str.split(":", n=1, expand=True)
    link["oid"] = link.oid.str.split("|")
    link = link.explode("oid")
    link["oid"] = link.oid.str.strip()
    att = link.merge(_attributes(), on=["src", "oid"], how="left")
    att["type_rank"] = att.fire_type.map(TYPE_RANK).fillna(1)

    def first_nonnull(s):
        s = s.dropna()
        return s.iloc[0] if len(s) else np.nan

    agg = att.sort_values("type_rank").groupby("event_id").agg(
        fire_type=("fire_type", "first"),
        type_rank=("type_rank", "min"),
        ga_fire_ids=("fire_id", lambda s: ";".join(sorted({str(x) for x in s.dropna()}))),
        ignition_cause=("ignition_cause", first_nonnull),
        capture_method=("capt_method", first_nonnull),
        agency=("agency", first_nonnull),
        ga_area_ha=("area_ha", "sum"),
        ignition_date_attr=("ignition_date", "min"),
        capture_date=("capture_date", "max"),
        extinguish_date=("extinguish_date", "max"),
        records_linked=("fire_type", "size"),
    )
    ev = inv.merge(agg, left_on="event_id", right_index=True, how="left")
    counts = {"nsw_inventory_events_since_2015": n_inventory,
              "prescribed_removed": int((ev.type_rank >= 2).sum())}
    ev = ev[ev.type_rank < 2].copy()
    ev["fire_type_flag"] = np.where(ev.type_rank == 0, "bushfire", "type unknown (not prescribed)")

    # geometry: rebuilt from the original GA records (historical gdb for GA_V2, downloaded layer for GA_RECENT_3)
    recs = link[link.event_id.isin(ev.event_id)][["event_id", "src", "oid"]]
    v2_ids = recs[recs.src == "GA_V2"].oid.astype(int).unique()
    gdb = f"/vsizip/{GA_ZIP}/Bushfire_Boundaries_Historical.gdb"
    v2_ids = np.sort(v2_ids)
    v2 = pyogrio.read_dataframe(gdb, fids=v2_ids, columns=["state"])  # rows come back in fids order
    assert len(v2) == len(v2_ids) and v2.state.astype(str).str.startswith("NSW").all()
    v2 = v2.to_crs(CRS)
    v2 = pd.DataFrame({"src": "GA_V2", "oid": v2_ids.astype(str), "geometry": v2.geometry.values})
    rc = gpd.read_file(DATA / "ga_recent_nsw.geojson").to_crs(CRS)
    rc = pd.DataFrame({"src": "GA_RECENT_3", "oid": rc.objectid.astype(str), "geometry": rc.geometry.values})
    g = recs.merge(pd.concat([v2, rc], ignore_index=True), on=["src", "oid"], how="inner")
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=CRS)
    g["geometry"] = shapely.make_valid(g.geometry.values)
    geom = g.dissolve("event_id").geometry
    counts["recent_layer_records_not_in_inventory"] = int((~rc.oid.isin(link[link.src == "GA_RECENT_3"].oid)).sum())
    ev = gpd.GeoDataFrame(ev.merge(geom.rename("geometry"), left_on="event_id", right_index=True, how="left"),
                          geometry="geometry", crs=CRS)
    counts["events_without_geometry"] = int(ev.geometry.isna().sum())
    ev = ev[ev.geometry.notna()].copy()
    ev["geometry"] = shapely.make_valid(ev.geometry.values)

    # de-duplicate the same fire held in both GA layers: keep GA_RECENT_3
    ev = ev.reset_index(drop=True)
    tree = shapely.STRtree(ev.geometry.values)
    a, b = tree.query(ev.geometry.values, predicate="intersects")
    m = (a < b) & (ev.source.values[a] != ev.source.values[b])
    a, b = a[m], b[m]
    drop = set()
    for i, j in zip(a, b):
        gi, gj = ev.geometry.values[i], ev.geometry.values[j]
        inter = shapely.area(shapely.intersection(gi, gj))
        iou = inter / max(shapely.area(shapely.union(gi, gj)), 1)
        if iou >= 0.5 and abs((ev.start.values[i] - ev.start.values[j]) / np.timedelta64(1, "D")) <= 3:
            drop.add(i if ev.source.values[i] == "GA_V2" else j)
    counts["cross_source_duplicates_removed"] = len(drop)
    ev = ev.drop(index=list(drop)).reset_index(drop=True)

    ev["end"] = pd.to_datetime(ev.end_date, errors="coerce")
    ev["end"] = ev.end.fillna(ev.extinguish_date).fillna(ev.capture_date)
    ev["duration_days"] = np.where(ev.end.notna() & (ev.end >= ev.start), (ev.end - ev.start).dt.days + 1, np.nan)
    ev["burn_area_ha"] = ev.geometry.area / 1e4
    cen = ev.geometry.representative_point()
    ll = gpd.GeoSeries(cen, crs=CRS).to_crs(4326)
    ev["centroid_lon"], ev["centroid_lat"] = ll.x.values, ll.y.values
    ev["year"] = ev.start.dt.year
    counts["fire_events"] = len(ev)
    return ev, counts
