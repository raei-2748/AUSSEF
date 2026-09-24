"""X10 elevation and X11 slope inside each fire outline (fires >= 10 ha).

Elevation: AWS Open Data "Terrain Tiles" (Mapzen terrarium PNG; in Australia built from SRTM 30 m / GA DEMs),
zoom 11 (about 65 m pixels at NSW latitudes). Slope is computed on the mosaic with true ground pixel size.
Run with: uv run --no-sync --with rasterio --with pillow python -m src.terrain
"""
import io
import json
import math
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from PIL import Image
from rasterio.features import geometry_mask
from rasterio.transform import from_origin

from src.common import DATA, record_source

Z, MIN_HA, WATER_M = 11, 0, -10
URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
CACHE = DATA / "terrain_cache"
R = 6378137.0
ORIGIN = math.pi * R


def tile_xy(lon, lat):
    n = 2 ** Z
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)


def fetch(xy):
    x, y = xy
    f = CACHE / f"{Z}_{x}_{y}.png"
    if not f.exists():
        for k in range(4):
            try:
                with urllib.request.urlopen(URL.format(z=Z, x=x, y=y), timeout=60) as r:
                    f.write_bytes(r.read())
                break
            except Exception:
                if k == 3:
                    raise
    return f


def tile_elev(x, y):
    a = np.asarray(Image.open(CACHE / f"{Z}_{x}_{y}.png").convert("RGB"), dtype=np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def one(geom4326, geom3857):
    b = geom4326.bounds
    x0, y0 = tile_xy(b[0], b[3])
    x1, y1 = tile_xy(b[2], b[1])
    rows = [np.hstack([tile_elev(x, y) for x in range(x0, x1 + 1)]) for y in range(y0, y1 + 1)]
    dem = np.vstack(rows)
    px = 2 * ORIGIN / (2 ** Z * 256)
    tr = from_origin(-ORIGIN + x0 * 256 * px, ORIGIN - y0 * 256 * px, px, px)
    lat = math.radians((b[1] + b[3]) / 2)
    g = px * math.cos(lat)  # ground metres per pixel
    dy, dx = np.gradient(dem, g)
    slope = np.degrees(np.arctan(np.hypot(dx, dy)))
    inside = geometry_mask([geom3857], out_shape=dem.shape, transform=tr, invert=True, all_touched=True)
    inside &= dem > WATER_M  # terrarium tiles include bathymetry; sea pixels are excluded
    if not inside.any():
        return dict(terrain_note="no land pixels inside the outline")
    e, s = dem[inside], slope[inside]
    return dict(X10_elevation=float(e.mean()), X11_slope=float(s.mean()), elevation_min=float(e.min()),
                elevation_max=float(e.max()), slope_p90=float(np.percentile(s, 90)), terrain_pixels=int(inside.sum()))


def run(ev, out_path):
    CACHE.mkdir(parents=True, exist_ok=True)
    big = ev[ev.burn_area_ha >= MIN_HA]
    g4326, g3857 = big.geometry.to_crs(4326), big.geometry.to_crs(3857)
    need = set()
    for b in g4326.bounds.itertuples():
        x0, y0 = tile_xy(b.minx, b.maxy)
        x1, y1 = tile_xy(b.maxx, b.miny)
        need |= {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    print("tiles", len(need), flush=True)
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(fetch, sorted(need)))
    rows = []
    for eid, a, m in zip(big.event_id, g4326, g3857):
        rows.append(dict(event_id=eid, **one(a, m)))
    out = pd.DataFrame(rows)
    out = pd.concat([out, ev.loc[ev.burn_area_ha < MIN_HA, ["event_id"]].assign(
        terrain_note=f"fire < {MIN_HA} ha: not computed")], ignore_index=True)
    out.to_parquet(out_path)
    doc = {
        "elevation_min": ["Lowest elevation inside the fire", "m", "AWS Terrain Tiles (SRTM-based)", "zoom 11, ~65 m"],
        "elevation_max": ["Highest elevation inside the fire", "m", "AWS Terrain Tiles", ""],
        "slope_p90": ["90th percentile slope inside the fire", "degrees", "computed from AWS Terrain Tiles", ""],
        "terrain_pixels": ["DEM pixels inside the outline", "count", "", ""],
        "terrain_note": ["Why terrain is blank", "str", "", ""],
    }
    Path(str(out_path).replace(".parquet", ".doc.json")).write_text(json.dumps(doc, indent=1))
    record_source("AWS Open Data Terrain Tiles (terrarium, zoom 11)", URL, None,
                  "open; SRTM (public domain) and GA DEM (CC BY 4.0) in Australia", f"{len(need)} tiles")
    return out


if __name__ == "__main__":
    ev = gpd.read_parquet(DATA / "cache/fires.parquet")
    out = run(ev, DATA / "enrich/terrain.parquet")
    print(out.describe().T.to_string())
