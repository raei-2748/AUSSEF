"""Part B fire events: GA historical bushfire boundaries (NSW), families, and road-closure overlay."""
import numpy as np
import pandas as pd
import pyogrio
import shapely

from src.inputs import W, CRS  # stage-1 module (on sys.path via run_stage2.py)

GA_ZIP = W / "dataset_phase1/raw/ga_original.zip"
GA_ZIP_SHA256 = "715907c149e32e0917f2533639937f5716550783c11086428cc20d5dc143e9fa"
GA_LAYER = f"/vsizip/{GA_ZIP}/Bushfire_Boundaries_Historical.gdb"
WINDOW = (pd.Timestamp("1950-07-01", tz="UTC"), pd.Timestamp("2019-06-30 23:59:59", tz="UTC"))
COMPOSITE = r"burnt\s*\d{4}|\bwf\s*\d{4}\s*[-/]\s*\d{2,4}|fire season|wildfire\s*\d{4}"
LINK_DAYS, LINK_M = 3, 5000


def load_fires(include_undated=False):
    """NSW bushfires in the window, composites removed. Returns GeoDataFrame in EPSG:3577 plus counts."""
    g = pyogrio.read_dataframe(GA_LAYER, where="state LIKE 'NSW%' AND fire_type = 'Bushfire'")
    counts = {"nsw_bushfires": len(g)}
    comp = g.fire_name.fillna("").str.lower().str.contains(COMPOSITE, regex=True)
    counts["season_composites_removed"] = int(comp.sum())
    g = g[~comp].copy()
    g["ign"] = pd.to_datetime(g.ignition_date, errors="coerce", utc=True)
    g["ext"] = pd.to_datetime(g.extinguish_date, errors="coerce", utc=True)
    undated = g.ign.isna()
    counts["undated_non_composite"] = int(undated.sum())
    in_window = g.ign.between(*WINDOW)
    counts["dated_outside_window"] = int((~undated & ~in_window).sum())
    keep = in_window | (undated if include_undated else False)
    g = g[keep & g.geometry.notna()].copy()
    g = g.to_crs(CRS)
    g["geometry"] = shapely.make_valid(g.geometry.values)
    g = g[~g.geometry.is_empty].reset_index(drop=True)
    g["fire_idx"] = np.arange(len(g))
    counts["fires_used"] = len(g)
    return g, counts


def families(g):
    """Connected components: date intervals within LINK_DAYS and perimeters within LINK_M.

    Undated fires are always singleton families.
    """
    parent = np.arange(len(g))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    dated = g.ign.notna().values
    start = g.ign.dt.tz_convert(None).values.astype("datetime64[D]")
    end_ts = g.ext.where(g.ext.notna() & (g.ext >= g.ign), g.ign)
    end = end_ts.dt.tz_convert(None).values.astype("datetime64[D]")
    tree = shapely.STRtree(g.geometry.values)
    left, right = tree.query(g.geometry.values, predicate="dwithin", distance=LINK_M)
    m = (left < right) & dated[left] & dated[right]
    left, right = left[m], right[m]
    gap = np.maximum(start[left] - end[right], start[right] - end[left]).astype("timedelta64[D]").astype(np.int64)
    for a, b in zip(left[gap <= LINK_DAYS], right[gap <= LINK_DAYS]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    root = np.array([find(i) for i in range(len(g))])
    return pd.Series([f"HB_{r:06d}" for r in root], index=g.index, name="event_id")


def closed_sets(g, event_id, net):
    """{rule: {event_id: frozenset(edge_id)}} from direct intersection (S0) and 100 m (S100)."""
    tree = shapely.STRtree(net["geom"])
    edge_ids = net["edges"].edge_id.values
    out = {}
    for rule, kw in (("S0", dict(predicate="intersects")), ("S100", dict(predicate="dwithin", distance=100))):
        fi, ei = tree.query(g.geometry.values, **kw)
        df = pd.DataFrame({"event_id": event_id.values[fi], "edge_id": edge_ids[ei]})
        out[rule] = {e: frozenset(x.edge_id) for e, x in df.groupby("event_id")}
    return out
