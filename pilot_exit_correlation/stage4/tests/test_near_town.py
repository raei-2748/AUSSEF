"""Synthetic check of the near-town stretch rule (fixture only)."""
import sys
from pathlib import Path

import shapely

HERE = Path(__file__).resolve().parents[1]
for p in (HERE.parent, HERE.parent / "stage2", HERE.parent / "stage3", HERE):
    sys.path.insert(0, str(p))
from run_stage4 import near_town_edges  # noqa: E402


def test_near_town_edges():
    town = shapely.box(0, 0, 100, 100)
    geom = {i: shapely.LineString([(100 + 1000 * i, 50), (100 + 1000 * (i + 1), 50)]) for i in range(20)}
    path = list(range(20))
    # all closed: keep edges within 5 km of town
    near = near_town_edges(path, set(path), geom, town, 5000)
    assert near == [0, 1, 2, 3, 4, 5]
    # only far edges closed (from 12 km): keep the closest burned stretch (d_min + 2 km)
    near = near_town_edges(path, set(range(12, 20)), geom, town, 5000)
    assert near == [12, 13, 14]
    assert near_town_edges(path, set(), geom, town, 5000) == []


if __name__ == "__main__":
    test_near_town_edges()
    print("PASS test_near_town_edges")
