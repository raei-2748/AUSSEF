"""Synthetic checks of the counted-exit rule and the ownership match (fixtures only)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from s9.counted_exits import counted_exits  # noqa: E402
from s9.ownership import label_edges, length_shares  # noqa: E402


def test_counted_exits_four_crossings_give_two():
    town = shapely.box(-200, -200, 200, 200)
    # Two named highways crossing the 500 m buffer twice each (in and out) = 4 crossing edges.
    geom = shapely.linestrings([[(-5000, 0), (5000, 0)], [(0, -5000), (0, 5000)]])
    edges = pd.DataFrame({"highway": ["primary", "primary"], "ref": ["A1", "B52"], "name": ["North Rd", "East Rd"]})
    # each line crosses the ring twice but is one edge here; emulate 4 separate crossing edges:
    geom4 = shapely.linestrings([[(-5000, 0), (-100, 0)], [(100, 0), (5000, 0)],
                                 [(0, -5000), (0, -100)], [(0, 100), (0, 5000)]])
    edges4 = pd.DataFrame({"highway": ["primary"] * 4, "ref": ["A1", "A1", "B52", "B52"],
                           "name": ["North Rd", "North Rd", "East Rd", "East Rd"]})
    assert counted_exits(town, edges4, geom4)[0] == 1  # 2 distinct roads / 2
    edges8 = pd.concat([edges4, edges4.assign(ref=["C1", "C1", "D9", "D9"])], ignore_index=True)
    geom8 = np.r_[geom4, geom4]
    assert counted_exits(town, edges8, geom8)[0] == 2  # 4 distinct roads / 2
    # residential roads are ignored
    assert counted_exits(town, edges4.assign(highway="residential"), geom4)[0] == 0
    assert counted_exits(town, edges, geom)[0] == 1


def test_ownership_match_distance():
    cat = shapely.linestrings([[(0, 0), (1000, 0)]])
    labels = label_edges(np.array([7, 8]),
                         np.array(shapely.linestrings([[(0, 10), (1000, 10)], [(0, 100), (1000, 100)]]), dtype=object),
                         cat, np.array(["State"]))
    assert labels[7] == "State" and labels[8] == "local"
    shares = length_shares([7, 8], [100.0, 300.0], labels)
    assert abs(shares["State"] - 0.25) < 1e-9 and abs(shares["local"] - 0.75) < 1e-9


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
