"""Part C: weekly traffic and freight deficits on roads near Black Summer fires (pre-COVID)."""
import numpy as np
import pandas as pd

SEASON_START = pd.Timestamp("2019-11-04")  # Monday
SEASON_END = pd.Timestamp("2020-02-23")    # Sunday, last pre-COVID week used
BASE_SEASONS = (2016, 2017, 2018)          # season starting in November of these years
MIN_DAYS_WEEK, MIN_BASE_YEARS = 6, 2


def weekly(series, season_start):
    """Weekly sums for 16 Monday-start weeks from season_start; NaN where fewer than 6 valid days."""
    out = []
    for w in range(int((SEASON_END - SEASON_START).days // 7) + 1):
        days = pd.date_range(season_start + pd.Timedelta(weeks=w), periods=7)
        v = series.reindex(days).dropna()
        out.append(float(v.sum()) if len(v) >= MIN_DAYS_WEEK else np.nan)
    return np.array(out)


def season_start_for(year):
    """Monday on or after 4 November of the given year, aligning weeks across seasons."""
    d = pd.Timestamp(f"{year}-11-04")
    return d + pd.Timedelta(days=(7 - d.weekday()) % 7)


def station_deficit(series):
    obs = weekly(series, SEASON_START)
    base_years = np.vstack([weekly(series, season_start_for(y)) for y in BASE_SEASONS])
    n_valid = np.sum(~np.isnan(base_years), axis=0)
    base = np.where(n_valid >= MIN_BASE_YEARS, np.nanmean(np.where(np.isnan(base_years), np.nan, base_years), axis=0), np.nan)
    ok = ~np.isnan(obs) & ~np.isnan(base) & (base > 0)
    ratio = np.where(ok, obs / np.where(base > 0, base, np.nan), np.nan)
    return dict(weeks_compared=int(ok.sum()), weeks_below_80=int(np.sum(ratio[ok] < 0.8)),
                deepest_ratio=float(np.nanmin(ratio)) if ok.any() else np.nan,
                net_deficit_trips=float(np.nansum((base - obs)[ok])) if ok.any() else np.nan,
                baseline_trips=float(np.nansum(base[ok])) if ok.any() else np.nan,
                weekly_ratio=[None if np.isnan(x) else round(float(x), 4) for x in ratio])
