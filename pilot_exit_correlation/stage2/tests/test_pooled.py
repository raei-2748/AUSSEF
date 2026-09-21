"""Checks of the pooled ratio and fire-event bootstrap on synthetic closure matrices (fixtures only)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from s2.pooled import bootstrap, pooled, ratio  # noqa: E402


def make_units(rng, n_comm, n_events, per, m, correlated):
    units = []
    for _ in range(n_comm):
        idx = rng.choice(n_events, size=per, replace=False)
        if correlated:
            hit = rng.random(per) < 0.3
            closed = np.repeat(hit[:, None], m, axis=1)
        else:
            closed = rng.random((per, m)) < 0.3
        units.append((idx, closed.all(axis=1), closed))
    return units


def test_independent_ratio_near_one():
    rng = np.random.default_rng(0)
    s = pooled(make_units(rng, 400, 5000, 200, 2, correlated=False))
    assert abs(ratio(s["O"], s["E"]) - 1) < 0.08


def test_correlated_ratio_large():
    rng = np.random.default_rng(1)
    s = pooled(make_units(rng, 50, 2000, 100, 3, correlated=True))
    assert ratio(s["O"], s["E"]) > 5


def test_bootstrap_brackets_point_and_uses_events():
    rng = np.random.default_rng(2)
    units = make_units(rng, 60, 1500, 60, 2, correlated=True)
    s = pooled(units)
    r = ratio(s["O"], s["E"])
    lo, hi, und = bootstrap(units, 1500, np.random.default_rng(3), B=300)
    assert lo <= r <= hi and und == 0.0


def test_undefined_when_no_expected():
    idx = np.arange(5)
    closed = np.zeros((5, 2), bool)
    s = pooled([(idx, closed.all(1), closed)])
    assert np.isnan(ratio(s["O"], s["E"]))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
