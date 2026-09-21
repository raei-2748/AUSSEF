"""Closed-edge sets per fire family and per-community closure / isolation matrices."""
import numpy as np

RULES = {
    "S0": lambda ov: ov.direct_burned_m > 0,
    "S100": lambda ov: ov.nearest_burn_distance_m <= 100,
}


def closed_sets(overlay):
    """{rule: {family_id: frozenset(edge_id)}}. Rows with a missing measure are never treated as closed."""
    out = {}
    for rule, pred in RULES.items():
        sel = overlay[pred(overlay).fillna(False).astype(bool)]
        out[rule] = {f: frozenset(g.edge_id.tolist()) for f, g in sel.groupby("disaster_family_id")}
    return out


def community_matrices(cg, paths, families, closed_by_family):
    """Return iso (n,) bool and closed (n, m) bool for the given relevant families."""
    n, m = len(families), len(paths)
    iso = np.zeros(n, dtype=bool)
    closed = np.zeros((n, m), dtype=bool)
    path_sets = [set(p) for p in paths]
    for i, f in enumerate(families):
        s = closed_by_family.get(f)
        if not s:
            continue
        s = {x for x in s if x in cg.edge_to_link}
        if not s:
            continue
        for j, p in enumerate(path_sets):
            closed[i, j] = not p.isdisjoint(s)
        iso[i] = not cg.connected_without(s)
    return iso, closed
