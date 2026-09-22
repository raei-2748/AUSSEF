"""Check the hand-written statistics against known values (fixtures only)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stats6 import holm, mann_whitney_p, median_diff_ci  # noqa: E402


def test_mann_whitney_reference():
    # Reference: scipy.stats.mannwhitneyu([1..5], [6..10], alternative='two-sided', method='asymptotic') -> p = 0.01193
    p = mann_whitney_p([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
    assert abs(p - 0.01193) < 5e-4, p
    assert mann_whitney_p([1, 2, 3], [1, 2, 3]) > 0.9


def test_median_diff_ci_brackets():
    rng = np.random.default_rng(0)
    x, y = rng.normal(0, 1, 200), rng.normal(1, 1, 200)
    est, lo, hi = median_diff_ci(x, y, np.random.default_rng(1))
    assert lo < est < hi and hi < 0


def test_holm():
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
