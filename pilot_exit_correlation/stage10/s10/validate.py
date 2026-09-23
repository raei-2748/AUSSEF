"""Part A: does the fire-outline closure rule match what traffic counters recorded?"""
import math

import numpy as np
import pandas as pd
import shapely

from s10.traffic import baseline

MIN_WINDOW_DAYS, MIN_BASE_DAYS = 3, 7


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return np.nan, np.nan, np.nan
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h


def build_pairs(station_edge, edge_geom, events, start, end, max_dist=500):
    """station_edge: DataFrame station_key, edge_id. events: DataFrame index=event_id with start, end, geometry."""
    ev = events[(events.start >= start) & (events.start <= end)]
    geoms = np.asarray(ev.geometry.values, dtype=object)
    tree = shapely.STRtree(geoms)
    sg = np.asarray([edge_geom[e] for e in station_edge.edge_id], dtype=object)
    a, b = tree.query(sg, predicate="dwithin", distance=max_dist)
    p = pd.DataFrame({"station_key": station_edge.station_key.values[a], "edge_id": station_edge.edge_id.values[a],
                      "event_id": ev.index.values[b], "event_part": ev.part.values[b],
                      "start": ev.start.values[b], "end": ev.end.values[b]})
    eg, fg = sg[a], geoms[b]
    p["s0"] = shapely.intersects(eg, fg)
    p["s100"] = shapely.dwithin(eg, fg, 100)
    inter = shapely.length(shapely.intersection(eg, fg))
    p["inside_share"] = np.where(shapely.length(eg) > 0, inter / shapely.length(eg), np.nan)
    p["s0_half"] = p.inside_share >= 0.5
    return p.drop_duplicates(["station_key", "event_id"]).reset_index(drop=True)


def observe(pairs, daily0, pad_before=1, pad_after=7):
    """Adds window/baseline stats and observed-closure flags (20% and 50%)."""
    by_station = {s: g.set_index("d").volume for s, g in daily0.groupby("station_key")}
    rows = []
    for r in pairs.itertuples():
        s = by_station.get(r.station_key)
        w0 = pd.Timestamp(r.start).tz_localize(None).normalize() - pd.Timedelta(days=pad_before)
        w1 = pd.Timestamp(r.end).tz_localize(None).normalize() + pd.Timedelta(days=pad_after)
        days = pd.date_range(w0, w1)
        if s is None:
            rows.append(dict(window_days_valid=0, base=np.nan, base_days=0, min_ratio=np.nan))
            continue
        win = s.reindex(days).dropna()
        base, nb = baseline(s, days)
        ratio = (win / base).min() if (len(win) and base and base > 0) else np.nan
        rows.append(dict(window_days_valid=int(len(win)), base=base, base_days=nb, min_ratio=float(ratio) if pd.notna(ratio) else np.nan,
                         min_day=str(win.idxmin().date()) if len(win) else ""))
    out = pd.concat([pairs, pd.DataFrame(rows)], axis=1)
    out["eligible"] = (out.window_days_valid >= MIN_WINDOW_DAYS) & (out.base_days >= MIN_BASE_DAYS) & (out.base > 0)
    out["obs_closed_20"] = np.where(out.eligible, out.min_ratio <= 0.20, np.nan)
    out["obs_closed_50"] = np.where(out.eligible, out.min_ratio <= 0.50, np.nan)
    return out


def summarise(pairs, rule, threshold):
    e = pairs[pairs.eligible]
    obs = e[f"obs_closed_{threshold}"].astype(bool)
    pred = e[rule].astype(bool)
    k1, n1 = int((obs & pred).sum()), int(pred.sum())
    k0, n0 = int((obs & ~pred).sum()), int((~pred).sum())
    p1, l1, h1 = wilson(k1, n1)
    p0, l0, h0 = wilson(k0, n0)
    return dict(rule=rule, threshold_pct=threshold, pred_closed_pairs=n1, pred_closed_observed=k1,
                rate_pred_closed=p1, rate_pred_closed_lo=l1, rate_pred_closed_hi=h1,
                untouched_pairs=n0, untouched_observed=k0, rate_untouched=p0, rate_untouched_lo=l0, rate_untouched_hi=h0,
                difference=(p1 - p0) if n1 and n0 else np.nan)


def interpret(row, min_pairs=5):
    if row["pred_closed_pairs"] < min_pairs:
        return "NOT EVALUABLE"
    if row["rate_pred_closed"] >= 0.60 and row["rate_pred_closed_lo"] > (row["rate_untouched"] if pd.notna(row["rate_untouched"]) else 0):
        return "RULE SUPPORTED"
    if row["rate_pred_closed"] < 0.40:
        return "RULE UNRELIABLE"
    return "INCONCLUSIVE"
