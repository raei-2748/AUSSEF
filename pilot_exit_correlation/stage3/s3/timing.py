"""Exit hit times from satellite hotspots, and the timed full cut-off rule."""
import numpy as np
import pandas as pd
import shapely


def exit_hit_times(paths, closed_edges, edge_geom, fire_geom, hotspots_xy, hotspot_times, D):
    """Earliest qualifying hotspot per exit, or NaT if none (undated).

    paths: list of edge-id lists; closed_edges: set of edge ids the fire closes;
    edge_geom: dict edge_id -> LineString (EPSG:3577); hotspots_xy: (k, 2) array in EPSG:3577.
    A hotspot qualifies for exit j if within D of the fire perimeter and within D of a closed edge on path j.
    """
    times = []
    all_cut = [edge_geom[e] for p in paths for e in p if e in closed_edges]
    if len(hotspots_xy) == 0 or not all_cut:
        return [pd.NaT] * len(paths)
    # Cheap filter first (near any cut exit edge, via a spatial index), then the costly fire-perimeter test
    # on the few survivors. Same result as testing every hotspot against the perimeter.
    pts = shapely.points(hotspots_xy)
    near_road = np.unique(shapely.STRtree(pts).query(np.array(all_cut, dtype=object), predicate="dwithin", distance=D)[1])
    pts, t = pts[near_road], hotspot_times[near_road]
    if len(pts):
        near_fire = shapely.dwithin(pts, fire_geom, D)
        pts, t = pts[near_fire], t[near_fire]
    for p in paths:
        cut = [edge_geom[e] for e in p if e in closed_edges]
        if not cut or len(pts) == 0:
            times.append(pd.NaT)
            continue
        ok = shapely.dwithin(pts, shapely.union_all(cut), D)
        times.append(t[ok].min() if ok.any() else pd.NaT)
    return times


def simultaneous(times, window_h):
    """True only if every exit is dated and the spread of hit times is within the window."""
    if len(times) == 0 or any(pd.isna(x) for x in times):
        return False
    spread = (max(times) - min(times)) / pd.Timedelta(hours=1)
    return bool(spread <= window_h)


def spread_hours(times):
    if len(times) == 0 or any(pd.isna(x) for x in times):
        return np.nan
    return (max(times) - min(times)) / pd.Timedelta(hours=1)
