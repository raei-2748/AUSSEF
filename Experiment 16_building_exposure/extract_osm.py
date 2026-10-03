"""Experiment 16, step 1 (outcome-free): pull NSW buildings, places of work / public facilities, roads, bridges,
railways and power lines out of the OpenStreetMap Australia snapshot of 1 Jan 2019 (Geofabrik extract, kept on
OneDrive). One pass per OSM layer (GDAL OSM driver via pyogrio), NSW bounding box only.

Outputs (Experiment 16_building_exposure/data/):
  osm2019_features.parquet  one row per building footprint or tagged point: tags, point location (EPSG:3577),
                            footprint area (m2; 0 for points)
  osm2019_lines.parquet     roads / railways / power lines with bridge flag, EPSG:3577 lines
Run: ./run.sh extract_osm.py
"""
import re
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely

HERE = Path(__file__).resolve().parent
OUT = HERE / 'data'
PBF = ('/Users/ray/Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/'
       'Transport and Mobility Raw Data (early experiments)/OpenStreetMap Australia - snapshot 2019-01-01.osm.pbf')
BBOX = (140.95, -37.55, 153.70, -28.10)   # NSW (+ACT) in lon/lat with a small margin
CRS = 3577
KEYS = ['building', 'amenity', 'shop', 'office', 'craft', 'tourism', 'healthcare', 'landuse', 'man_made',
        'power', 'bridge', 'industrial', 'emergency', 'social_facility', 'leisure']
pyogrio.set_gdal_config_options({'OSM_MAX_TMPFILE_SIZE': '6000', 'OGR_INTERLEAVED_READING': 'NO'})


def tag(other, key):
    """value of `key` in a GDAL hstore string '"k"=>"v","k2"=>"v2"' (None if absent)."""
    pat = re.compile(r'"' + key + r'"=>"((?:[^"\\]|\\.)*)"')
    return other.map(lambda s: (m.group(1) if (isinstance(s, str) and (m := pat.search(s))) else None))


def complete(df):
    for k in KEYS:
        if k not in df.columns:
            df[k] = None
        if 'other_tags' in df.columns:
            df[k] = df[k].where(df[k].notna(), tag(df.other_tags, k))
    return df


def read(layer, where, columns):
    t = time.time()
    g = pyogrio.read_dataframe(PBF, layer=layer, where=where, bbox=BBOX, columns=columns)
    print(f'{layer}: {len(g):,} features in {time.time() - t:.0f}s', flush=True)
    return g


def main():
    like = ' OR '.join(f"other_tags LIKE '%\"{k}\"=>%'" for k in
                       ['amenity', 'shop', 'office', 'craft', 'tourism', 'healthcare', 'building', 'emergency',
                        'power', 'social_facility'])
    # ---- buildings and tagged areas
    mp = read('multipolygons',
              "building IS NOT NULL OR amenity IS NOT NULL OR shop IS NOT NULL OR office IS NOT NULL OR "
              "craft IS NOT NULL OR tourism IS NOT NULL OR landuse IN ('industrial','commercial','retail',"
              "'farmyard') OR " + like,
              ['osm_id', 'osm_way_id', 'name', 'building', 'amenity', 'shop', 'office', 'craft', 'tourism',
               'landuse', 'man_made', 'leisure', 'other_tags'])
    mp = complete(mp.to_crs(CRS))
    mp['id'] = np.where(mp.osm_id.notna(), 'r' + mp.osm_id.astype(str), 'w' + mp.osm_way_id.astype(str))
    mp['area_m2'] = shapely.area(mp.geometry.values)
    mp['geometry'] = shapely.point_on_surface(mp.geometry.values)
    mp['layer'] = 'area'
    # ---- tagged points (shops, schools, halls... mapped as a single node)
    pt = read('points', like + " OR man_made IS NOT NULL", ['osm_id', 'name', 'man_made', 'other_tags'])
    pt = complete(pt.to_crs(CRS))
    pt['id'] = 'n' + pt.osm_id.astype(str)
    pt['area_m2'] = 0.0
    pt['layer'] = 'point'
    cols = ['id', 'layer', 'name'] + KEYS + ['area_m2', 'geometry']
    feat = gpd.GeoDataFrame(pd.concat([mp[cols], pt[cols]], ignore_index=True), geometry='geometry', crs=CRS)
    feat.to_parquet(OUT / 'osm2019_features.parquet', index=False)
    print('features saved:', len(feat), feat.layer.value_counts().to_dict(), flush=True)
    del mp, pt, feat
    # ---- lines: roads, railways, power lines
    ln = read('lines', "highway IS NOT NULL OR railway IS NOT NULL OR other_tags LIKE '%\"power\"=>%'",
              ['osm_id', 'highway', 'railway', 'other_tags'])
    ln = ln.to_crs(CRS)
    ln['power'] = tag(ln.other_tags, 'power')
    ln['bridge'] = tag(ln.other_tags, 'bridge')
    ln = ln.drop(columns='other_tags')
    ln.to_parquet(OUT / 'osm2019_lines.parquet', index=False)
    print('lines saved:', len(ln), flush=True)


if __name__ == '__main__':
    main()
