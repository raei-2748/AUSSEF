"""Fire-weather formulas: KBDI, Griffiths drought factor, McArthur Mark 5 FFDI, Hargreaves PET, SPEI-3 (normal fit).

References
- Noble, Bary & Gill (1980) McArthur's fire-danger meters expressed as equations (FFDI Mark 5).
- Griffiths (1999) Improved formula for the drought factor in McArthur's Forest Fire Danger Meter.
- Keetch & Byram (1968), metric form as used by the Bureau of Meteorology (KBDI, 0–203.2 mm).
- Hargreaves & Samani (1985) reference evapotranspiration.
- Vicente-Serrano et al. (2010) SPEI; here standardised with a normal fit per calendar month (approximation).
"""
import numpy as np
import pandas as pd


def kbdi_series(rain_mm, tmax_c, mean_annual_rain_mm, start=0.0):
    """Daily KBDI (mm, 0–203.2). The first 5.08 mm of each rain spell is lost to interception."""
    rain = np.nan_to_num(np.asarray(rain_mm, float))
    tmax = np.asarray(tmax_c, float)
    R = max(float(mean_annual_rain_mm), 1.0)
    k, spell, out = start, 0.0, np.empty(len(rain))
    for i in range(len(rain)):
        if rain[i] > 0:
            before = spell
            spell += rain[i]
            net = max(0.0, spell - 5.08) - max(0.0, before - 5.08)
            k = max(0.0, k - net)
        else:
            spell = 0.0
        t = tmax[i] if np.isfinite(tmax[i]) else 20.0
        et = (203.2 - k) * (0.968 * np.exp(0.0875 * t + 1.5552) - 8.30) / (1 + 10.88 * np.exp(-0.001736 * R)) * 1e-3
        k = min(203.2, max(0.0, k + max(et, 0.0)))
        out[i] = k
    return out


def drought_factor(kbdi, rain_mm):
    """Griffiths (1999) drought factor (0–10) from KBDI and the largest rain event in the previous 20 days."""
    rain = np.nan_to_num(np.asarray(rain_mm, float))
    df = np.empty(len(rain))
    for i in range(len(rain)):
        lo = max(0, i - 19)
        window = rain[lo:i + 1]
        # rain events = runs of consecutive rain days; take the largest total and its age (days since its last day)
        best_p, best_n, run, run_end = 0.0, 0, 0.0, None
        for j in range(len(window) - 1, -1, -1):
            if window[j] > 0:
                if run == 0.0:
                    run_end = j
                run += window[j]
            if (window[j] == 0 or j == 0) and run > 0:
                n = len(window) - 1 - run_end
                if run > best_p:
                    best_p, best_n = run, n
                run = 0.0
        I = kbdi[i]
        if best_p > 2:
            n = max(best_n, 0.8) if best_n == 0 else best_n
            x = n ** 1.3 / (n ** 1.3 + best_p - 2)
        else:
            x = 1.0
        xlim = 1 / (1 + 0.1135 * I) if I < 20 else 75 / (270.525 - 1.267 * I)
        x = min(x, xlim)
        d = 10.5 * (1 - np.exp(-(I + 30) / 40)) * (41 * x * x + x) / (40 * x * x + x + 1)
        df[i] = min(10.0, max(0.0, d))
    return df


def ffdi(temp_c, rh_pct, wind_kmh, df):
    """McArthur Mark 5 forest fire danger index (Noble et al. 1980)."""
    df = np.maximum(np.asarray(df, float), 1e-6)
    return 2 * np.exp(-0.450 + 0.987 * np.log(df) - 0.0345 * np.asarray(rh_pct, float)
                      + 0.0338 * np.asarray(temp_c, float) + 0.0234 * np.asarray(wind_kmh, float))


def hargreaves_pet(tmax, tmin, lat_deg, dates):
    """Daily reference evapotranspiration (mm/day), Hargreaves–Samani with FAO-56 extraterrestrial radiation."""
    doy = pd.DatetimeIndex(dates).dayofyear.values
    phi = np.radians(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1, 1))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws))
    tmean = (np.asarray(tmax) + np.asarray(tmin)) / 2
    return 0.0023 * 0.408 * ra * (tmean + 17.8) * np.sqrt(np.clip(np.asarray(tmax) - np.asarray(tmin), 0, None))


def spei3_monthly(daily, ref=(1991, 2020)):
    """daily: DataFrame indexed by date with 'rain' and 'pet'. Returns monthly SPEI-3 (normal fit per calendar month)."""
    m = daily[["rain", "pet"]].resample("MS").sum(min_count=20)
    bal = (m.rain - m.pet).rolling(3, min_periods=3).sum()
    ref_mask = (bal.index.year >= ref[0]) & (bal.index.year <= ref[1])
    out = pd.Series(np.nan, index=bal.index)
    for month in range(1, 13):
        sel = bal.index.month == month
        base = bal[sel & ref_mask].dropna()
        if len(base) >= 20 and base.std() > 0:
            out[sel] = (bal[sel] - base.mean()) / base.std()
    return out
