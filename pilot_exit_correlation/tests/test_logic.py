"""Toy-graph checks of the exit / isolation / metric logic. Fixtures only; never used as data."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.closure import community_matrices  # noqa: E402
from src.exits import CommunityGraph  # noqa: E402
from src.metrics import bootstrap_log_rho, log_rho, n_eff  # noqa: E402


def toy_net():
    # Town node 0 at the origin; two edge-disjoint routes to nodes beyond R = 10:
    # 0-1-3 (east) and 0-2-4 (west); plus a spur 1-2 that shares no ring access.
    xy = np.array([[0, 0], [5, 0], [-5, 0], [15, 0], [-15, 0]], float)
    rows = [(10, 0, 1), (11, 1, 3), (12, 0, 2), (13, 2, 4), (14, 1, 2)]
    e = pd.DataFrame(rows, columns=["edge_id", "ui", "vi"])
    e["length_m"] = np.hypot(*(xy[e.ui] - xy[e.vi]).T)
    geom = shapely.linestrings([[xy[a], xy[b]] for a, b in zip(e.ui, e.vi)])
    return {"edges": e, "geom": geom, "node_xy": xy}


def test_two_exits_and_isolation():
    net = toy_net()
    cg = CommunityGraph(net, shapely.box(-1, -1, 1, 1), (0, 0), 10)
    k, paths = cg.exits_and_paths()
    assert k == 2
    assert sorted(map(sorted, paths)) == [[10, 11], [12, 13]]
    assert set(paths[0]).isdisjoint(paths[1])
    fams = ["a", "b", "c"]
    closed = {"a": frozenset({11}), "b": frozenset({11, 13}), "c": frozenset({14})}
    iso, cl = community_matrices(cg, paths, fams, closed)
    assert iso.tolist() == [False, True, False]
    # isolation implies every exit closed
    assert cl[iso].all()


def test_rho_missing_when_no_isolation():
    iso = np.zeros(10, bool)
    closed = np.zeros((10, 3), bool)
    _, _, lr = log_rho(iso, closed)
    assert np.isnan(lr)


def test_rho_near_one_for_independent_exits():
    rng = np.random.default_rng(1)
    closed = rng.random((200000, 2)) < 0.3
    iso = closed.all(axis=1)
    _, _, lr = log_rho(iso, closed)
    assert abs(np.exp(lr) - 1) < 0.05


def test_rho_large_for_perfectly_correlated_exits():
    x = np.r_[np.ones(3, bool), np.zeros(17, bool)]
    closed = np.c_[x, x, x]
    _, _, lr = log_rho(x, closed)
    assert np.exp(lr) > 5
    lo, hi, und = bootstrap_log_rho(x, closed, np.random.default_rng(0), B=500)
    assert lo <= np.log(np.exp(lr)) <= hi or np.isnan(lo)


def test_neff():
    x = np.r_[np.ones(5, bool), np.zeros(15, bool)]
    y = np.r_[np.zeros(10, bool), np.ones(5, bool), np.zeros(5, bool)]
    v, never, always = n_eff(np.c_[x, x, np.zeros(20, bool)])
    assert abs(v - 1.0) < 1e-9 and never == 1 and always == 0
    v2, _, _ = n_eff(np.c_[x, y])
    assert 1.0 < v2 <= 2.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
