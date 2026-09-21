"""Synthetic checks of the timing rule and the outside-town filter (fixtures only; never used as data)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from s3.timing import exit_hit_times, simultaneous, spread_hours  # noqa: E402

T = pd.Timestamp("2020-01-01T00:00Z")


def test_window():
    times = [T, T + pd.Timedelta(hours=3)]
    assert simultaneous(times, 12) and not simultaneous(times, 1)
    assert spread_hours(times) == 3


def test_undated_is_not_simultaneous():
    assert not simultaneous([T, pd.NaT], 24)
    assert np.isnan(spread_hours([T, pd.NaT]))


def test_hit_times_use_nearest_qualifying_hotspot():
    edge_geom = {1: shapely.LineString([(0, 0), (1000, 0)]), 2: shapely.LineString([(0, 5000), (1000, 5000)])}
    fire = shapely.box(-2000, -2000, 3000, 7000)
    xy = np.array([[500, 200], [500, 4900], [500, 300], [50000, 0]], float)
    t = pd.DatetimeIndex([T + pd.Timedelta(hours=h) for h in (5, 2, 1, 0)])
    got = exit_hit_times([[1], [2]], {1, 2}, edge_geom, fire, xy, t, D=500)
    assert got == [T + pd.Timedelta(hours=1), T + pd.Timedelta(hours=2)]
    # exit 2 not closed by the fire -> undated
    got2 = exit_hit_times([[1], [2]], {1}, edge_geom, fire, xy, t, D=500)
    assert pd.isna(got2[1])


def test_outside_town_filter():
    town = shapely.box(0, 0, 100, 100)
    edges = {1: shapely.LineString([(50, 50), (150, 50)]), 2: shapely.LineString([(200, 0), (300, 0)])}
    inside = {e for e, g in edges.items() if g.intersects(town)}
    assert inside == {1}
    assert {1, 2} - inside == {2}


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
