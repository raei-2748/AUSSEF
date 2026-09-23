"""Raw TfNSW permanent-counter data: fingerprint, day-level quality checks and daily volumes."""
import hashlib

import numpy as np
import pandas as pd

MIN_HOURS = 20
HOURS = [f"hour_{h:02d}" for h in range(24)]


def tables(con):
    return [t for (t,) in con.sql("""select table_name from information_schema.tables
            where table_schema = 'raw' and table_name like 'manual_traffic_hourly_permanent_%'
            order by table_name""").fetchall()]


def fingerprint(con):
    """Row count and SHA-256 over sorted (station, date, direction, class, daily_total) rows."""
    u = " union all ".join(f"select station_key, date, traffic_direction_seq, classification_seq, daily_total from raw.{t}"
                           for t in tables(con))
    h, n = hashlib.sha256(), 0
    rel = con.sql(f"select * from ({u}) order by 1, 2, 3, 4")
    reader = rel.fetch_record_batch(500_000)
    for batch in reader:
        df = batch.to_pandas()
        h.update(df.astype(str).agg("|".join, axis=1).str.cat(sep="\n").encode())
        n += len(df)
    return n, h.hexdigest()


def station_locations(con):
    ref = con.sql("""select station_key, wgs84_latitude lat, wgs84_longitude lon
                     from raw.manual_traffic_station_reference""").df()
    ref = ref.dropna()
    ref["lat"] = pd.to_numeric(ref.lat, errors="coerce")
    ref["lon"] = pd.to_numeric(ref.lon, errors="coerce")
    return ref.dropna().drop_duplicates("station_key")


def daily(con, stations, classes=("0",)):
    """Per station × date × class: volume (sum over directions) and validity. Missing is never zero."""
    st = ",".join(f"'{s}'" for s in stations)
    cl = ",".join(f"'{c}'" for c in classes)
    nh = " + ".join(f"(case when {h} is not null and {h} <> '' then 1 else 0 end)" for h in HOURS)
    u = " union all ".join(
        f"""select station_key, cast(substr(date, 1, 10) as date) d, traffic_direction_seq dir,
                   classification_seq cls, try_cast(daily_total as bigint) total, {nh} n_hours
            from raw.{t} where station_key in ({st}) and classification_seq in ({cl})"""
        for t in tables(con))
    rows = con.sql(u).df()
    rows = rows.drop_duplicates(["station_key", "d", "dir", "cls"])
    # usual directions: those present on >= 50% of the station-class's days
    days = rows.groupby(["station_key", "cls"]).d.nunique().rename("ndays")
    dir_days = rows.groupby(["station_key", "cls", "dir"]).d.nunique().rename("dir_days").reset_index()
    dir_days = dir_days.join(days, on=["station_key", "cls"])
    usual = dir_days[dir_days.dir_days >= 0.5 * dir_days.ndays].groupby(["station_key", "cls"]).dir.apply(set)
    rows["ok_dir"] = (rows.n_hours >= MIN_HOURS) & rows.total.notna()
    g = rows.groupby(["station_key", "cls", "d"])
    out = g.agg(volume=("total", "sum"), dirs_ok=("dir", lambda s: set(s[rows.loc[s.index, "ok_dir"]]))).reset_index()
    out["usual"] = [usual.get((s, c), set()) for s, c in zip(out.station_key, out.cls)]
    out["valid"] = [len(u) > 0 and u <= ok for u, ok in zip(out.usual, out.dirs_ok)]
    out["volume"] = out.volume.where(out.valid)
    out["d"] = pd.to_datetime(out.d)
    return out[["station_key", "cls", "d", "volume", "valid"]]


def all_vehicles(daily_rows):
    """All-vehicle daily volume: class 0 where valid, else light (2) + heavy (3) when both are valid (DEVIATIONS V1).

    Many counters record light and heavy vehicles separately and never publish a class-0 total.
    """
    w = daily_rows.pivot_table(index=["station_key", "d"], columns="cls", values="volume", aggfunc="first")
    c0 = w["0"] if "0" in w else pd.Series(np.nan, index=w.index)
    c23 = (w["2"] + w["3"]) if ("2" in w and "3" in w) else pd.Series(np.nan, index=w.index)
    vol = c0.where(c0.notna(), c23)
    src = np.where(c0.notna(), "class 0", np.where(c23.notna(), "light + heavy", "missing"))
    out = vol.rename("volume").reset_index()
    out["source"] = src
    out["cls"] = "all"
    return out


def baseline(series_by_date, window_days, years_back=3, pad=7):
    """Median valid volume over the same calendar window (day of year ± pad) in the preceding years."""
    vals = []
    for k in range(1, years_back + 1):
        for day in window_days:
            ref = day - pd.DateOffset(years=k)
            rng = pd.date_range(ref - pd.Timedelta(days=pad), ref + pd.Timedelta(days=pad))
            vals.append(series_by_date.reindex(rng))
    if not vals:
        return np.nan, 0
    v = pd.concat(vals)
    v = v[~v.index.duplicated()].dropna()
    return (float(v.median()) if len(v) else np.nan), int(len(v))
