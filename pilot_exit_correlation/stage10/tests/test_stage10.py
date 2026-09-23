"""Synthetic checks for stage 10 (fixtures only; never used as data)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from s10.traffic import baseline  # noqa: E402
from s10.validate import interpret, wilson  # noqa: E402
from s10.fiscal_charts import gate  # noqa: E402


def test_wilson_reference():
    # Reference: 8 of 10, Wilson 95% = (0.4902, 0.9433)
    p, lo, hi = wilson(8, 10)
    assert abs(p - 0.8) < 1e-12 and abs(lo - 0.4902) < 1e-3 and abs(hi - 0.9433) < 1e-3


def test_baseline_same_calendar_window():
    idx = pd.date_range("2016-01-01", "2020-12-31")
    s = pd.Series(1000.0, index=idx)
    s[(idx.month == 12) & (idx.day >= 20)] = 3000.0  # holiday peak each year
    base, n = baseline(s, pd.date_range("2019-12-28", "2019-12-30"))
    assert n >= 7 and base > 1000.0  # uses the same holiday window, not an average day


def test_closure_vs_outage_logic():
    # A 5%-of-baseline valid day counts as closed; a missing (NaN) day is ignored, not zero.
    win = pd.Series([950.0, 50.0, np.nan])
    assert (win.dropna() / 1000.0).min() <= 0.20
    assert np.isnan(win.iloc[2])


def test_interpret_bands():
    base = dict(pred_closed_pairs=10, rate_untouched=0.1)
    assert interpret({**base, "rate_pred_closed": 0.8, "rate_pred_closed_lo": 0.5}) == "RULE SUPPORTED"
    assert interpret({**base, "rate_pred_closed": 0.3, "rate_pred_closed_lo": 0.1}) == "RULE UNRELIABLE"
    assert interpret({**base, "rate_pred_closed": 0.5, "rate_pred_closed_lo": 0.2}) == "INCONCLUSIVE"
    assert interpret({**base, "pred_closed_pairs": 3, "rate_pred_closed": 1.0, "rate_pred_closed_lo": 0.4}) == "NOT EVALUABLE"


def test_gate():
    gaps = pd.Series({2016: 2.0, 2017: -3.0, 2018: 0.0, 2019: 10.0, 2020: 4.0})
    assert gate(gaps)[0] is True
    assert gate(pd.Series({2016: 2.0, 2017: -12.0, 2018: 0.0, 2019: 10.0, 2020: 4.0}))[0] is False


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
