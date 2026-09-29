"""Fetch NSW Bush Fire Prone Land (official ePlanning service, layer 229) as paged GeoJSON.

Source: NSW RFS / DPHI 'NSW Bush Fire Prone Land' (Data.NSW, CC-BY), served at
mapprod3.environment.nsw.gov.au/arcgis/rest/services/ePlanning/Planning_Portal_Hazard/MapServer/229
Geometry is generalised to ~30 m (maxAllowableOffset 0.0003 deg) to keep the download small.
Pages are cached; reruns skip pages already on disk.
"""
import json, time, urllib.request
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'fire_event_dataset/data/bfpl'
OUT.mkdir(parents=True, exist_ok=True)
BASE = ('https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/ePlanning/'
        'Planning_Portal_Hazard/MapServer/229/query')
Q = ('where=1%3D1&outFields=OBJECTID,Category&returnGeometry=true&maxAllowableOffset=0.0003'
     '&geometryPrecision=5&orderByFields=OBJECTID&resultRecordCount=2000&f=geojson&resultOffset=')
N = 235537
for off in range(0, N, 2000):
    f = OUT / f'page_{off:06d}.json'
    if f.exists() and f.stat().st_size > 1000:
        continue
    for attempt in range(5):
        try:
            with urllib.request.urlopen(BASE + '?' + Q + str(off), timeout=180) as r:
                data = r.read()
            json.loads(data)
            f.write_bytes(data)
            break
        except Exception as e:
            print('retry', off, e, flush=True)
            time.sleep(5 * (attempt + 1))
    else:
        raise SystemExit(f'failed at offset {off}')
    print('ok', off, flush=True)
print('done')
