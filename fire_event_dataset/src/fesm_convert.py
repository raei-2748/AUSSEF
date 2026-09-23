"""One-off: stream the 2021-22 FESM grid (66 GB inside its zip) into a compressed 30 m GeoTIFF (nearest-neighbour, every
3rd 10 m pixel), so fires can be read by window. Sequential strip reads keep zip decompression linear."""
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window

from src.common import DATA

SRC = "/vsizip/" + str(DATA / "fesm/fesm_202122.zip") + "/fesm202122"
DST = DATA / "fesm/fesm_202122_30m.tif"
K, STRIP = 3, 3 * 1024

with rasterio.open(SRC) as s:
    H, W = s.height // K, s.width // K
    prof = dict(driver="GTiff", height=H, width=W, count=1, dtype="uint8", crs=s.crs, nodata=s.nodata,
                transform=s.transform * rasterio.Affine.scale(K, K), compress="deflate", tiled=True,
                blockxsize=512, blockysize=512, BIGTIFF="YES")
    with rasterio.open(DST, "w", **prof) as d:
        for r0 in range(0, H * K, STRIP):
            h = min(STRIP, H * K - r0)
            a = s.read(1, window=Window(0, r0, W * K, h), out_shape=(h // K, W), resampling=Resampling.nearest)
            d.write(a, 1, window=Window(0, r0 // K, W, a.shape[0]))
            print(f"rows {r0 + h}/{H * K}", flush=True)
