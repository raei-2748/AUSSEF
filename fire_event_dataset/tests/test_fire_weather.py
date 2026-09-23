"""Checks of the fire-weather formulas (synthetic inputs only)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.fire_weather import drought_factor, ffdi, hargreaves_pet, kbdi_series, spei3_monthly  # noqa: E402


def test_ffdi_known_value():
    # Hand computation of Noble et al. (1980): T=40, H=10, V=40, DF=10 -> 2*exp(3.7656) = 86.4
    assert abs(float(ffdi(40, 10, 40, 10)) - 86.4) < 0.3
    # Catastrophic conditions exceed 100
    assert float(ffdi(45, 5, 70, 10)) > 100


def test_kbdi_dries_and_wets():
    n = 200
    k = kbdi_series(np.zeros(n), np.full(n, 35.0), 800)
    assert np.all(np.diff(k) >= 0) and k[-1] > 100
    rain = np.zeros(n); rain[150] = 100
    k2 = kbdi_series(rain, np.full(n, 35.0), 800)
    assert k2[150] < k2[149] - 80  # 100 mm minus 5.08 mm interception


def test_drought_factor_bounds_and_rain_effect():
    kb = np.full(30, 150.0)
    dry = drought_factor(kb, np.zeros(30))
    wet = np.zeros(30); wet[-2] = 40
    after = drought_factor(kb, wet)
    assert 0 <= dry.min() and dry.max() <= 10 and after[-1] < dry[-1]


def test_pet_and_spei():
    d = pd.date_range("1991-01-01", "2025-12-31")
    pet = hargreaves_pet(np.full(len(d), 28.0), np.full(len(d), 14.0), -33.0, d)
    assert 2 < pet.mean() < 7
    rng = np.random.default_rng(0)
    daily = pd.DataFrame({"rain": rng.gamma(0.5, 4, len(d)), "pet": pet}, index=d)
    s = spei3_monthly(daily)
    ref = s[(s.index.year >= 1991) & (s.index.year <= 2020)].dropna()
    assert abs(ref.mean()) < 0.1 and 0.8 < ref.std() < 1.2


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
