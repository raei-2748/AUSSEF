"""PNAS-style counted exits: distinct higher-order roads crossing a 0.5 km buffer, divided by two."""
import numpy as np
import shapely

HIGHER_ORDER = {"motorway", "trunk", "primary", "secondary", "tertiary",
                "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link"}
BUFFER_M = 500


def counted_exits(poly, edges, geom, tree=None):
    """edges: DataFrame with highway/ref/name; geom: matching geometry array. Returns (count, crossings)."""
    ring = shapely.boundary(shapely.buffer(poly, BUFFER_M))
    idx = (tree.query(ring, predicate="intersects") if tree is not None
           else np.flatnonzero(shapely.intersects(geom, ring)))
    if len(idx) == 0:
        return 0, 0
    sub = edges.iloc[idx]
    keep = sub.highway.isin(HIGHER_ORDER).values
    sub = sub[keep]
    if len(sub) == 0:
        return 0, 0
    named = sub.ref.fillna("").where(sub.ref.notna() & (sub.ref != ""), sub.name.fillna(""))
    distinct = named[named != ""].nunique() + int((named == "").sum())
    # Pre-registered PNAS-style count halves the total; `distinct` is the unhalved variant (DEVIATIONS U1).
    return int(distinct // 2), int(distinct)
