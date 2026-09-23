"""Fetch NVIS 6.0 Major Vegetation Groups (100 m, EPSG:3577) for the NSW fire extent from the MDBA ImageServer, in tiles."""
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.common import DATA

SVC = ("https://gis.mdba.gov.au/arcgis/rest/services/Vegetation/"
       "NVIS_Version_6_0_Australia_Present_Major_Vegetation_Groups/ImageServer/exportImage")
OUT = DATA / "nvis/nvis6_mvg_nsw.tif"
X0, Y0, X1, Y1, T = 835300, -4213400, 2082700, -3206900, 2000


def main():
    W, H = (X1 - X0) // 100, (Y1 - Y0) // 100
    arr = np.full((H, W), -128, dtype=np.int16)
    tiles = DATA / "nvis/tiles"
    tiles.mkdir(parents=True, exist_ok=True)
    for r0 in range(0, H, T):
        for c0 in range(0, W, T):
            h, w = min(T, H - r0), min(T, W - c0)
            f = tiles / f"t_{r0}_{c0}.tif"
            if not f.exists():
                bb = f"{X0 + c0 * 100},{Y1 - (r0 + h) * 100},{X0 + (c0 + w) * 100},{Y1 - r0 * 100}"
                q = (f"{SVC}?bbox={bb}&bboxSR=3577&imageSR=3577&size={w},{h}&format=tiff&pixelType=S8"
                     f"&interpolation=RSP_NearestNeighbor&f=image")
                with urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": "Mozilla/5.0"}), timeout=600) as resp:
                    f.write_bytes(resp.read())
            with rasterio.open(f) as s:
                a = s.read(1)
            arr[r0:r0 + a.shape[0], c0:c0 + a.shape[1]] = a
            print(f.name, a.shape, np.unique(a)[:8], flush=True)
    with rasterio.open(OUT, "w", driver="GTiff", height=H, width=W, count=1, dtype="int16", crs="EPSG:3577",
                       transform=from_origin(X0, Y1, 100, 100), nodata=-128, compress="deflate") as d:
        d.write(arr, 1)


if __name__ == "__main__":
    main()
