"""Experiment 16, step 2 (outcome-free): what was inside, or within 1 km of, each fire outline, BY BUILDING FUNCTION.

A. Council x fire table (the 218 rows of Experiment 9/results/ANALYSIS_TABLE.csv, keyed agrn x region_id).
   Zone = union of the outlines of all fires linked to the declared event (as fire_event_dataset/src/affected_pop.py),
   cut to the council. 'in' = inside the outline; '1km' = inside or within 1 km (outline included).
   - Census mesh blocks (MB; 2016 Census for events starting up to 2020, 2021 after, as affected_pop.py). Each MB's
     counts are spread evenly over its area (the Experiment 7 assumption), so a zone gets count x area share.
       homes = dwellings; residents = persons; farm_homes = dwellings in Primary Production MBs
       workplace_mb = Commercial + Industrial MBs (area-share-weighted MB count: 1 = one whole MB)
       public_mb = Education + Hospital/Medical MBs; farm_km2 = Primary Production land (km2)
   - OpenStreetMap, 1 Jan 2019 snapshot (data/osm2019_*.parquet from extract_osm.py). Each mapped feature (building
     footprint, tagged area or point) gets ONE class by priority public > workplace > farm > home > other building.
     Points-in-zone counts. Lines: road km by class, bridge count, railway km, power line km.
B. SA2 x financial-year exposure (all NSW fires starting in the FY, no buffer), Census 2021 MBs (SA2 2021 codes,
   as Experiment 7 Day 9):
     H = share of SA2 dwellings inside       W = share of SA2 Commercial+Industrial MBs inside
     P = share of SA2 Education+Hospital MBs inside      F = share of SA2 Primary Production land inside
     W_osm = share of the SA2's OSM workplace sites inside       A = share of SA2 land inside
   Same measures within 1 km of the outline (outline included) carry the suffix _1km.
Run: ./run.sh build_exposure.py
"""
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True   # do not leave __pycache__ in other folders
import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyogrio  # noqa: E402
import shapely  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/ray/Research/AUSSEF - Local')
DS = ROOT / 'fire_event_dataset'
sys.path.insert(0, str(DS))
from src.affected_pop import SOURCES, load_counts  # noqa: E402

DATA, RES = HERE / 'data', HERE / 'results'
CRS = 3577
LGA_SHP = Path('/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw/'
               'lga_2021/LGA_2021_AUST_GDA94.shp')
WORK, PUBLIC, FARM = {'Commercial', 'Industrial'}, {'Education', 'Hospital/Medical'}, {'Primary Production'}

# ------------------------------------------------------------------ OSM classes (priority order matters)
PUB_AMENITY = {'school', 'kindergarten', 'childcare', 'college', 'university', 'hospital', 'clinic', 'doctors',
               'dentist', 'community_centre', 'social_facility', 'fire_station', 'police', 'library', 'townhall',
               'place_of_worship', 'courthouse', 'nursing_home', 'arts_centre', 'ambulance_station', 'social_centre',
               'public_building', 'prison', 'emergency_service', 'ses', 'rescue_station'}
PUB_BUILDING = {'school', 'hospital', 'public', 'civic', 'church', 'chapel', 'government', 'fire_station',
                'kindergarten', 'university', 'college', 'cathedral', 'temple', 'mosque', 'synagogue'}
WORK_AMENITY = {'restaurant', 'cafe', 'fast_food', 'pub', 'bar', 'fuel', 'bank', 'pharmacy', 'post_office',
                'marketplace', 'car_wash', 'veterinary', 'nightclub', 'ice_cream', 'food_court', 'cinema',
                'car_rental', 'bureau_de_change'}
WORK_TOURISM = {'hotel', 'motel', 'guest_house', 'hostel', 'chalet', 'caravan_site', 'apartment',
                'bed_and_breakfast', 'resort', 'winery'}
WORK_BUILDING = {'commercial', 'retail', 'office', 'industrial', 'warehouse', 'supermarket', 'kiosk', 'hotel',
                 'manufacture', 'shop', 'service'}
FARM_BUILDING = {'farm_auxiliary', 'barn', 'shed', 'stable', 'cowshed', 'greenhouse', 'silo', 'sty', 'hangar'}
HOME_BUILDING = {'house', 'residential', 'detached', 'apartments', 'semidetached_house', 'terrace', 'bungalow',
                 'cabin', 'farm', 'dormitory', 'hut', 'static_caravan', 'duplex', 'townhouse', 'villa'}
MAJOR_ROAD = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'motorway_link', 'trunk_link', 'primary_link',
              'secondary_link', 'tertiary_link'}
LOCAL_ROAD = {'residential', 'unclassified', 'road', 'living_street'}


def osm_class(f):
    b, a = f.building.fillna(''), f.amenity.fillna('')
    pub = (a.isin(PUB_AMENITY) | b.isin(PUB_BUILDING) | f.healthcare.notna() | (f.office == 'government') |
           f.emergency.isin(['ambulance_station', 'ses_station']))
    work = (f.shop.notna() | (f.office.notna() & (f.office != 'government')) | f.craft.notna() |
            a.isin(WORK_AMENITY) | f.tourism.isin(WORK_TOURISM) | b.isin(WORK_BUILDING) |
            f.landuse.isin(['retail', 'commercial', 'industrial']) | (f.man_made == 'works'))
    farm = b.isin(FARM_BUILDING) | (f.landuse == 'farmyard') | (f.man_made == 'silo')
    home = b.isin(HOME_BUILDING)
    other_b = (b != '') & (b != 'no')
    cls = np.select([pub, work, farm, home, other_b], ['public', 'workplace', 'farm', 'home', 'other_building'],
                    default='')
    return pd.Series(cls, index=f.index)


def load_osm():
    f = gpd.read_parquet(DATA / 'osm2019_features.parquet')
    f['cls'] = osm_class(f)
    f = f[f.cls != ''].reset_index(drop=True)
    sub = np.select([f.amenity.isin(['school', 'kindergarten', 'childcare', 'college', 'university']) |
                     f.building.isin(['school', 'kindergarten', 'university', 'college']),
                     f.amenity.isin(['hospital', 'clinic', 'doctors', 'dentist', 'nursing_home']) |
                     f.healthcare.notna() | (f.building == 'hospital'),
                     f.amenity.isin(['fire_station', 'police', 'ambulance_station', 'ses', 'rescue_station',
                                     'emergency_service']) | f.emergency.notna() | (f.building == 'fire_station'),
                     f.amenity.isin(['community_centre', 'townhall', 'library', 'social_centre', 'arts_centre']),
                     f.amenity.eq('place_of_worship') | f.building.isin(['church', 'chapel', 'cathedral', 'temple'])],
                    ['school', 'health', 'emergency', 'hall_library', 'worship'], default='')
    f['pub_sub'] = np.where(f.cls == 'public', sub, '')
    ln = gpd.read_parquet(DATA / 'osm2019_lines.parquet')
    hw = ln.highway.fillna('')
    ln['lcls'] = np.select([hw.isin(MAJOR_ROAD), hw.isin(LOCAL_ROAD), hw.eq('track'), ln.railway.eq('rail'),
                            ln.power.isin(['line', 'minor_line'])],
                           ['major_road', 'local_road', 'track', 'rail', 'power_line'], default='')
    ln = ln[ln.lcls != ''].reset_index(drop=True)
    ln['is_bridge'] = ln.bridge.isin(['yes', 'viaduct', 'movable']) & ln.lcls.isin(['major_road', 'local_road',
                                                                                     'track', 'rail'])
    return f, ln


# ------------------------------------------------------------------ mesh blocks (all of them, not only populated)
def load_mb_all(year):
    c = load_counts(year)
    if year == 2016:
        src, code = f"/vsizip/{SOURCES['mb_2016_bnd']['path']}/MB_2016_NSW.shp", 'MB_CODE16'
        g = pyogrio.read_dataframe(src, columns=[code, 'SA2_MAIN16'])
        g = g.rename(columns={code: 'MB_CODE', 'SA2_MAIN16': 'SA2'})
    else:
        src, code = f"/vsizip/{SOURCES['mb_2021_bnd']['path']}/MB_2021_AUST_GDA94.shp", 'MB_CODE21'
        g = pyogrio.read_dataframe(src, columns=[code, 'STE_CODE21', 'SA2_CODE21', 'SA3_CODE21', 'GCC_CODE21'],
                                   where="STE_CODE21 = '1'")
        g = g.rename(columns={code: 'MB_CODE', 'SA2_CODE21': 'SA2', 'SA3_CODE21': 'SA3', 'GCC_CODE21': 'GCCSA'})
    g['MB_CODE'] = g.MB_CODE.astype(str)
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    g = g.merge(c, on='MB_CODE', how='inner').to_crs(CRS)
    g['geometry'] = shapely.make_valid(g.geometry.values)
    g['area'] = shapely.area(g.geometry.values)
    g = g[g.area > 0].reset_index(drop=True)
    print(year, 'MBs with boundary and counts:', len(g), flush=True)
    return g


def inter(a, b):
    """intersection that survives GEOS topology errors: retry on repaired inputs, then on a 0.5 m precision grid."""
    try:
        return shapely.intersection(a, b)
    except shapely.errors.GEOSException:
        a, b = shapely.make_valid(a), shapely.make_valid(b)
        try:
            return shapely.intersection(a, b)
        except shapely.errors.GEOSException:
            return shapely.intersection(a, b, grid_size=0.5)


def area_shares(zone, geoms, tree, areas):
    """indices of `geoms` touching `zone` and the share of each one's area inside it."""
    if zone is None or shapely.is_empty(zone):
        return np.array([], int), np.array([])
    zone = shapely.make_valid(zone)
    shapely.prepare(zone)
    idx = tree.query(zone, predicate='intersects')
    if not len(idx):
        return idx, np.array([])
    g = geoms[idx]
    share = np.ones(len(idx))
    edge = ~shapely.contains_properly(zone, g)
    if edge.any():
        clipped = [shapely.clip_by_rect(zone, *b) for b in shapely.bounds(g[edge])]
        share[edge] = shapely.area(inter(g[edge], np.array(clipped, dtype=object))) / areas[idx][edge]
    return idx, np.clip(share, 0, 1)


def line_lengths(zone, geoms, tree):
    zone = shapely.make_valid(zone)
    shapely.prepare(zone)
    idx = tree.query(zone, predicate='intersects')
    if not len(idx):
        return idx, np.array([])
    g = geoms[idx]
    length = shapely.length(g)
    edge = ~shapely.contains_properly(zone, g)
    if edge.any():
        clipped = [shapely.clip_by_rect(zone, *b) for b in shapely.bounds(g[edge])]
        length[edge] = shapely.length(inter(g[edge], np.array(clipped, dtype=object)))
    return idx, length


def mb_summary(mb, idx, share, suffix):
    s = mb.iloc[idx]
    cat = s.category.values
    r = {'residents': (s.person.values * share).sum(), 'homes': (s.dwelling.values * share).sum(),
         'farm_homes': (s.dwelling.values * share)[np.isin(cat, list(FARM))].sum(),
         'workplace_mb': share[np.isin(cat, list(WORK))].sum(),
         'commercial_mb': share[cat == 'Commercial'].sum(), 'industrial_mb': share[cat == 'Industrial'].sum(),
         'public_mb': share[np.isin(cat, list(PUBLIC))].sum(),
         'education_mb': share[cat == 'Education'].sum(), 'health_mb': share[cat == 'Hospital/Medical'].sum(),
         'farm_km2': (s.area.values * share)[np.isin(cat, list(FARM))].sum() / 1e6}
    return {f'{k}_{suffix}': float(v) for k, v in r.items()}


def osm_summary(f, ftree, ln, ltree, zone, suffix):
    zone = shapely.make_valid(zone)
    shapely.prepare(zone)
    i = ftree.query(zone, predicate='contains')
    s = f.iloc[i]
    r = {f'osm_{c}': int((s.cls == c).sum()) for c in ['home', 'workplace', 'public', 'farm', 'other_building']}
    r.update({f'osm_public_{c}': int((s.pub_sub == c).sum()) for c in
              ['school', 'health', 'emergency', 'hall_library', 'worship']})
    j, L = line_lengths(zone, ln.geometry.values, ltree)
    lc = ln.lcls.values[j]
    r.update({f'{c}_km': float(L[lc == c].sum() / 1000) for c in
              ['major_road', 'local_road', 'track', 'rail', 'power_line']})
    r['bridges'] = int(ln.is_bridge.values[j].sum())
    return {f'{k}_{suffix}': v for k, v in r.items()}


# ------------------------------------------------------------------ A. council x fire
def council_fire(osm, ln):
    rows = pd.read_csv(ROOT / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'agrn': str, 'region_id': str},
                       usecols=['agrn', 'region_id', 'region_name', 'season', 'dwellings'])
    fx = pd.read_csv(DS / 'out/fires.csv', dtype={'region_id': str}, low_memory=False,
                     usecols=['event_id', 'region_id', 'official_declaration_agrn'])
    fx['agrn'] = fx.official_declaration_agrn.fillna('').astype(str).str.split(';')
    fx = fx.explode('agrn')
    fx = fx[fx.agrn != '']
    ev = gpd.read_parquet(DS / 'data/cache/fires.parquet')[['event_id', 'start', 'geometry']].set_index('event_id')
    assert ev.crs.to_epsg() == CRS
    lga = gpd.read_file(LGA_SHP)
    lga = lga[lga.STE_NAME21 == 'New South Wales'].to_crs(CRS).set_index('LGA_CODE21')
    lga['geometry'] = shapely.make_valid(lga.geometry.values)
    mbs = {y: load_mb_all(y) for y in (2016, 2021)}
    trees = {y: shapely.STRtree(m.geometry.values) for y, m in mbs.items()}
    ftree, ltree = shapely.STRtree(osm.geometry.values), shapely.STRtree(ln.geometry.values)
    out, t0 = [], time.time()
    for a, g in rows.groupby('agrn'):
        ids = fx[fx.agrn == a].event_id.unique()
        ids = [e for e in ids if e in ev.index]
        if not ids:
            print('no outline for agrn', a)
            continue
        U = shapely.make_valid(shapely.union_all(ev.geometry.loc[ids].values))
        B = shapely.buffer(U, 1000, quad_segs=8)
        y = 2016 if pd.Timestamp(ev.start.loc[ids].min()).year <= 2020 else 2021
        mb = mbs[y]
        for r in g.itertuples():
            L = lga.geometry.loc[r.region_id]
            zi, zb = inter(U, L), inter(B, L)
            rec = dict(agrn=a, region_id=r.region_id, region_name=r.region_name, season=r.season, census_year=y,
                       n_fires=len(ids), burned_km2=float(shapely.area(zi) / 1e6),
                       council_km2=float(shapely.area(L) / 1e6))
            for z, suf in ((zi, 'in'), (zb, '1km')):
                idx, sh = area_shares(z, mb.geometry.values, trees[y], mb.area.values)
                rec.update(mb_summary(mb, idx, sh, suf))
                rec.update(osm_summary(osm, ftree, ln, ltree, z, suf))
            # council totals (same Census vintage) for scaling
            idx, sh = area_shares(L, mb.geometry.values, trees[y], mb.area.values)
            rec.update({k.replace('_all', '_council'): v for k, v in mb_summary(mb, idx, sh, 'all').items()})
            out.append(rec)
        print(f'agrn {a}: {len(g)} councils, {time.time() - t0:.0f}s', flush=True)
    t = pd.DataFrame(out)
    t = rows[['agrn', 'region_id']].merge(t, on=['agrn', 'region_id'], how='left', validate='1:1')
    return t


# ------------------------------------------------------------------ B. SA2 x financial year
def sa2_fy(osm):
    mb = load_mb_all(2021)
    tree = shapely.STRtree(mb.geometry.values)
    # OSM workplace sites -> SA2 (point in mesh block)
    w = osm[osm.cls == 'workplace']
    pi, mi = tree.query(w.geometry.values, predicate='within')
    w_sa2 = pd.Series(mb.SA2.values[mi], index=pi).groupby(level=0).first()
    w = w.assign(SA2=w_sa2.reindex(range(len(w))).values)
    wtree = shapely.STRtree(w.geometry.values)
    f = gpd.read_parquet(DS / 'data/cache/fires.parquet')
    f = f[f.geometry.notna() & ~f.geometry.is_empty]
    st = pd.to_datetime(f.start_date)
    f['fy'] = np.where(st.dt.month >= 7, st.dt.year, st.dt.year - 1)
    cat = mb.category.values
    tot = pd.DataFrame({'SA2': mb.SA2, 'dw': mb.dwelling, 'work': np.isin(cat, list(WORK)).astype(float),
                        'pub': np.isin(cat, list(PUBLIC)).astype(float),
                        'farm': np.where(np.isin(cat, list(FARM)), mb.area, 0.0), 'area': mb.area}
                       ).groupby('SA2').sum()
    tot['osm_work'] = w.groupby('SA2').size().reindex(tot.index).fillna(0)
    info = mb.groupby('SA2').agg(SA3=('SA3', 'first'), GCCSA=('GCCSA', 'first'), pop=('person', 'sum'))
    def measure(zone, fy, suf):
        idx, sh = area_shares(zone, mb.geometry.values, tree, mb.area.values)
        s = mb.iloc[idx]
        c = s.category.values
        d = pd.DataFrame({'SA2': s.SA2.values, 'dw': s.dwelling.values * sh,
                          'work': np.isin(c, list(WORK)) * sh, 'pub': np.isin(c, list(PUBLIC)) * sh,
                          'farm': np.where(np.isin(c, list(FARM)), s.area.values * sh, 0.0),
                          'area': s.area.values * sh}).groupby('SA2').sum()
        z = shapely.make_valid(zone)
        shapely.prepare(z)
        wi = wtree.query(z, predicate='contains')
        d['osm_work'] = w.iloc[wi].groupby('SA2').size().reindex(d.index).fillna(0)
        T = tot.loc[d.index]
        return pd.DataFrame({'SA2': d.index.values, 'fy': int(fy),
                             'H' + suf: d.dw / T.dw.replace(0, np.nan), 'W' + suf: d.work / T.work.replace(0, np.nan),
                             'P' + suf: d['pub'] / T['pub'].replace(0, np.nan),
                             'F' + suf: d.farm / T.farm.replace(0, np.nan),
                             'W_osm' + suf: d.osm_work / T.osm_work.replace(0, np.nan), 'A' + suf: d.area / T.area,
                             'homes' + suf: d.dw, 'workplace_mb' + suf: d.work, 'osm_work' + suf: d.osm_work}
                            ).reset_index(drop=True)

    rows = []
    for fy, sub in f.groupby('fy'):
        zone = shapely.make_valid(shapely.union_all(sub.geometry.values))
        e_in = measure(zone, fy, '')                                    # inside the outline (primary)
        e_1k = measure(shapely.buffer(zone, 1000, quad_segs=8), fy, '_1km')  # inside or within 1 km (secondary)
        e = e_1k.merge(e_in, on=['SA2', 'fy'], how='left')
        rows.append(e)
        print(fy, len(sub), 'fires;', int(e.H.notna().sum()), 'SA2s touched inside,', len(e), 'within 1 km',
              flush=True)
    e = pd.concat(rows, ignore_index=True)
    for c in ['H', 'W', 'P', 'F', 'W_osm', 'A']:
        for sfx in ('', '_1km'):
            e[c + sfx] = e[c + sfx].fillna(0.0).clip(0, 1)   # no such buildings in the SA2 -> nothing exposed
    tot.join(info).reset_index().to_parquet(DATA / 'sa2_totals_2021.parquet', index=False)
    return e


def main():
    osm, ln = load_osm()
    print('OSM classes:', osm.cls.value_counts().to_dict(), '| lines:', ln.lcls.value_counts().to_dict(), flush=True)
    osm[['id', 'layer', 'cls', 'pub_sub', 'geometry']].to_parquet(DATA / 'osm2019_classified.parquet', index=False)
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('both', 'sa2'):
        e = sa2_fy(osm)
        e.to_parquet(DATA / 'sa2_fy_exposure.parquet', index=False)
    if which in ('both', 'council'):
        t = council_fire(osm, ln)
        t.to_csv(RES / 'EXPOSURE_COUNCIL_FIRE.csv', index=False)
        print(t.describe().T.round(1).to_string())


if __name__ == '__main__':
    main()
