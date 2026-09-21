"""DEA Hotspots WFS download with a frozen, hash-verified local cache."""
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

WFS = "https://hotspots.dea.ga.gov.au/geoserver/wfs"
PAGE = 10000
COLUMNS = ["id", "datetime", "longitude", "latitude", "satellite", "sensor", "confidence", "accuracy", "product"]


def _query_url(bbox_lonlat, t0, t1, start_index):
    lon0, lat0, lon1, lat1 = bbox_lonlat
    cql = (f"datetime BETWEEN '{t0}' AND '{t1}' AND "
           f"BBOX(geometry,{lat0:.4f},{lon0:.4f},{lat1:.4f},{lon1:.4f})")  # WFS 2.0 EPSG:4326 axis order lat, lon
    params = dict(service="WFS", version="2.0.0", request="GetFeature", typeNames="public:hotspots",
                  outputFormat="application/json", count=PAGE, startIndex=start_index, sortBy="id",
                  CQL_FILTER=cql)
    return WFS + "?" + urllib.parse.urlencode(params)


def _get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                return json.loads(r.read())
        except Exception:  # network hiccup: back off and retry
            if k == tries - 1:
                raise
            time.sleep(5 * (k + 1))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch_event(event_id, bbox_lonlat, t0, t1, cache_dir: Path):
    """Download (once) all hotspots for one event window; return a manifest row. Never re-queries a cached event."""
    out = cache_dir / f"{event_id}.parquet"
    meta = cache_dir / f"{event_id}.json"
    if out.exists() and meta.exists():
        return json.loads(meta.read_text())
    rows, start, matched = [], 0, None
    first_url = _query_url(bbox_lonlat, t0, t1, 0)
    while True:
        js = _get(_query_url(bbox_lonlat, t0, t1, start))
        matched = js.get("numberMatched", matched)
        feats = js.get("features", [])
        rows += [{c: f["properties"].get(c) for c in COLUMNS} for f in feats]
        if len(feats) < PAGE:
            break
        start += PAGE
    df = pd.DataFrame(rows, columns=COLUMNS).drop_duplicates("id").sort_values("id").reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df.datetime, utc=True)
    df.to_parquet(out, index=False)
    m = dict(event_id=event_id, query_url_first_page=first_url, window_start=t0, window_end=t1,
             bbox_lonlat=list(bbox_lonlat), number_matched=matched, rows=len(df),
             downloaded_utc=pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"), sha256=sha256(out))
    meta.write_text(json.dumps(m, indent=2, default=str))
    return m


def load_event(event_id, cache_dir: Path, expected_sha256):
    out = cache_dir / f"{event_id}.parquet"
    got = sha256(out)
    if got != expected_sha256:
        raise SystemExit(f"HOTSPOT CACHE HASH MISMATCH {out}: expected {expected_sha256}, got {got}")
    return pd.read_parquet(out)
