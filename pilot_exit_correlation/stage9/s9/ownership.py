"""Label road edges as State / Regional / local using the TfNSW road categorisation."""
import numpy as np
import pyogrio
import shapely

MATCH_M = 25
CLASS_NAME = {"S": "State", "R": "Regional"}


def load_categorisation(zip_path):
    """Returns (geometries in EPSG:3577, class labels)."""
    layer = f"/vsizip/{zip_path}/NSW_Road_Network_Categorisation.shp"
    df = pyogrio.read_dataframe(layer).to_crs(3577)
    cls = df.admin_clas.astype(str).str.strip().str.upper().map(CLASS_NAME).fillna("Regional")
    return shapely.force_2d(df.geometry.values), cls.values


def label_edges(edge_ids, edge_geom, cat_geom, cat_class):
    """Nearest categorised line within MATCH_M; unmatched -> 'local'. Returns dict edge_id -> label."""
    tree = shapely.STRtree(cat_geom)
    nearest = tree.query_nearest(edge_geom, max_distance=MATCH_M, all_matches=False, return_distance=False)
    out = {int(e): "local" for e in edge_ids}
    src, dst = (nearest[0], nearest[1]) if nearest.ndim == 2 else (np.arange(len(edge_geom)), nearest)
    for i, j in zip(src, dst):
        out[int(edge_ids[i])] = cat_class[j]
    return out


def length_shares(edge_ids, lengths, labels):
    """Share of total length by owner label."""
    total = float(np.sum(lengths))
    if total <= 0:
        return {}
    acc = {}
    for e, L in zip(edge_ids, lengths):
        acc[labels.get(int(e), "local")] = acc.get(labels.get(int(e), "local"), 0.0) + float(L)
    return {k: v / total for k, v in acc.items()}
