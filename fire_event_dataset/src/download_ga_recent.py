"""Download NSW records (bushfire + unknown type) with geometry from GA 'Historical Bushfire Extents 2020–25' (layer 3)."""
import json
import time
import urllib.parse
import urllib.request

from src.common import DATA, record_source

URL = ("https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/arcgis/rest/services/"
       "Historical_Bushfire_Extents_2020%E2%80%9325_View/FeatureServer/3/query")
WHERE = "state LIKE 'NSW%' AND (fire_type IS NULL OR fire_type <> 'Prescribed burn')"
OUT = DATA / "ga_recent_nsw.geojson"
PAGE = 200


def get(params, tries=5):
    q = URL + "?" + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            with urllib.request.urlopen(q, timeout=300) as r:
                return json.loads(r.read())
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(5 * (k + 1))


def main():
    if OUT.exists():
        return OUT
    feats, offset = [], 0
    while True:
        js = get(dict(f="geojson", where=WHERE, outFields="*", outSR=4283, returnGeometry="true",
                      orderByFields="objectid", resultOffset=offset, resultRecordCount=PAGE))
        batch = js.get("features", [])
        feats += batch
        print(f"  ga recent: {len(feats)} features", flush=True)
        if len(batch) < PAGE:
            break
        offset += PAGE
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    record_source("GA Historical Bushfire Extents 2020–25 (layer 3, NSW, excl. prescribed burns)",
                  URL + "?where=" + urllib.parse.quote(WHERE), OUT, "CC BY 4.0 (Geoscience Australia)")
    return OUT


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(DATA.parent))
    main()
