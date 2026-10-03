"""Council adjacency (2021 LGA polygons, touching within 50 m). Run with geopandas env."""
from pathlib import Path
import geopandas as gpd, pandas as pd, shapely
HERE = Path(__file__).resolve().parent
g = pd.read_parquet(HERE.parent / 'fire_event_dataset/data/cache/lga2021_nsw_geom.parquet')
g['geometry'] = shapely.from_wkb(g.geometry)
g = gpd.GeoDataFrame(g, geometry='geometry', crs=4283).to_crs(3577)
g['region_id'] = g.region_id.astype(int).astype(str)
b = g.copy(); b['geometry'] = b.buffer(50)
j = gpd.sjoin(b[['region_id', 'geometry']], g[['region_id', 'geometry']], predicate='intersects')
j = j[j.region_id_left != j.region_id_right][['region_id_left', 'region_id_right']].drop_duplicates()
j.columns = ['region_id', 'neighbour_id']
j.to_csv(HERE / 'results/ADJACENCY.csv', index=False)
print(len(j), 'pairs;', j.region_id.nunique(), 'councils')
