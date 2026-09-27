"""People affected (Bowen's X2, 受灾人口): Census residents and dwellings inside each fire's burned outline, per council.

Method
------
- Census counts at the finest ABS geography, the Mesh Block (MB): usual residents (`Person`) and dwellings (`Dwelling`)
  from ABS "Census Mesh Block Counts" (2016: cat. 2074.0; 2021: Census guide). Both files are randomly adjusted by the
  ABS to protect confidentiality, so sums differ slightly from published totals.
- MB boundaries: ABS ASGS 2016 (NSW shapefile) and ASGS Edition 3 2021 (Australia, GDA94), filtered to NSW and
  projected to EPSG:3577 (the fire outlines' CRS). MBs with no residents and no dwellings are dropped (they add
  nothing); the no-usual-address / migratory / offshore / shipping pseudo-MBs have no boundary and cannot be placed.
- Each MB is split by the ABS LGA 2021 boundaries used for the fire × council rows (src/regions.py). An MB lying in
  one council stays whole; one crossing a council line is cut, with its counts shared by area.
- **Allocation rule (an assumption):** residents in a zone = Σ MB residents × (share of the MB's area inside the zone).
  People are assumed spread evenly over each MB. Urban MBs are small (typically 30–60 dwellings), so this matters
  little in towns; large rural MBs (Primary Production, Parkland) can be hundreds of km², so a fire covering part of
  one gets that share of its residents whether or not the homestead burned. Dwellings are allocated the same way.
- Zones: the fire's burned outline (GA, merged incident; src/fires.py) and the outline buffered by 1 km and 5 km.
  Each zone is split by council through the MB pieces above, so the council value = residents of that council inside
  the zone. The buffers include the burned area. Buffers stop at the NSW border (only NSW MBs are loaded).
- Census vintage (as for SEIFA and dwellings): 2016 Census for fires starting up to 2020, 2021 Census after.
- Declared event × council: the union of the outlines of all fires linked to the declaration (AGRN, as in
  src/key_events.py), then split by council. Overlapping fires are counted once.

Outputs
-------
- data/enrich/affected_pop.parquet (+ .csv, .doc.json): one row per fire × council of out/fires.csv
  (event_id + region_id). build_all.py merges it into the fires table on its next run.
- data/enrich/affected_pop_event_council.parquet (+ .csv, .doc.json): one row per declared event × council of
  out/key_event_council.csv (agrn + region_id). Not merged anywhere automatically (no event_id column).
- data/enrich/affected_pop_checks.json: self-check results.

Blank = not computed. 0 = computed and no resident / dwelling inside the zone.

Run from fire_event_dataset/:  ../.venv/bin/python -m src.affected_pop
"""
import json
import re
import time
import urllib.request

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely

from src.common import CRS, DATA, MANIFEST, OUT, record_source

RAW = DATA / "raw" / "pop"
ENRICH = DATA / "enrich"
CACHE = DATA / "cache"
BUFFERS_M = {"1km": 1_000, "5km": 5_000}
LICENCE = "CC BY 4.0 (ABS)"

ABS_OLD = "https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&"
SOURCES = {
    "mb_2016_bnd": dict(
        name="ABS ASGS 2016 Vol 1 Mesh Blocks, NSW, ESRI shapefile (1270.0.55.001, GDA94)",
        url=ABS_OLD + "1270055001_mb_2016_nsw_shape.zip&1270055001&Data%20Cubes&E9FA17AFA7EB9FEBCA257FED0013A5F5&0"
                      "&July%202016&12.07.2016&Latest",
        path=RAW / "MB_2016_NSW_shape.zip", note="Mesh Block boundaries for Census 2016 counts"),
    "mb_2021_bnd": dict(
        name="ABS ASGS Edition 3 Mesh Blocks 2021, Australia, shapefile GDA94",
        url="https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/"
            "edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/MB_2021_AUST_SHP_GDA94.zip",
        path=RAW / "MB_2021_AUST_SHP_GDA94.zip", note="Mesh Block boundaries for Census 2021 counts; NSW (STE 1) used"),
    "mb_2016_counts": dict(
        name="ABS 2074.0 Census of Population and Housing: Mesh Block Counts, Australia, 2016 (CSV)",
        url=ABS_OLD + "2016%20census%20mesh%20block%20counts.csv&2074.0&Data%20Cubes&1DED88080198D6C6CA2581520083D113"
                      "&0&2016&04.07.2017&Latest",
        path=RAW / "2016_census_mesh_block_counts.csv",
        note="usual residents (Person) and dwellings per MB; randomly adjusted by ABS"),
    # already downloaded by src/grp_insurance.py and in the manifest: reused, not downloaded again
    "mb_2021_counts": dict(
        name="ABS Mesh Block Counts, 2021 (NSW tables 1 and 1.1)",
        url="https://www.abs.gov.au/census/guide-census-data/mesh-block-counts/2021/Mesh%20Block%20Counts%2C%202021.xlsx",
        path=DATA / "raw/grp_insurance/asgs/Mesh_Block_Counts_2021.xlsx",
        note="usual residents (Person) and dwellings per MB; randomly adjusted by ABS"),
    "qs_2016": dict(
        name="ABS 2016 Census QuickStats, New South Wales (state total people)",
        url="https://www.abs.gov.au/census/find-census-data/quickstats/2016/1",
        path=RAW / "quickstats_2016_nsw.html", note="published NSW total for the self-check"),
    "qs_2021": dict(
        name="ABS 2021 Census QuickStats, New South Wales (state total people)",
        url="https://www.abs.gov.au/census/find-census-data/quickstats/2021/1",
        path=RAW / "quickstats_2021_nsw.html", note="published NSW total for the self-check"),
}


# ------------------------------------------------------------------ downloads
def _in_manifest(path):
    if not MANIFEST.exists():
        return False
    m = pd.read_csv(MANIFEST, dtype=str)
    return str(path) in set(m.local_path.dropna())


def fetch_all():
    RAW.mkdir(parents=True, exist_ok=True)
    for s in SOURCES.values():
        p = s["path"]
        if not p.exists():
            req = urllib.request.Request(s["url"], headers={"User-Agent": "Mozilla/5.0 (research data download)"})
            with urllib.request.urlopen(req, timeout=600) as r, open(p, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
        if not _in_manifest(p):
            record_source(s["name"], s["url"], p, LICENCE, s["note"])


# ------------------------------------------------------------------ Census counts
def load_counts(year):
    """All NSW MB counts (including the pseudo-MBs without a boundary): MB_CODE (str), category, person, dwelling."""
    if year == 2016:
        d = pd.read_csv(SOURCES["mb_2016_counts"]["path"], dtype={"MB_CODE_2016": str}, encoding="latin-1")
        d = d.rename(columns={"MB_CODE_2016": "MB_CODE", "MB_CATEGORY_NAME_2016": "category"})
    else:
        p = SOURCES["mb_2021_counts"]["path"]
        d = pd.concat([pd.read_excel(p, sheet_name=t, header=6, dtype={"MB_CODE_2021": str})
                       for t in ("Table 1", "Table 1.1")], ignore_index=True)
        d = d.rename(columns={"MB_CODE_2021": "MB_CODE", "MB_CATEGORY_NAME_2021": "category"})
    d = d[d.MB_CODE.astype(str).str.fullmatch(r"\d{11}", na=False)].copy()  # drop footnote rows
    d = d[pd.to_numeric(d.State, errors="coerce") == 1]
    d["person"] = pd.to_numeric(d.Person, errors="coerce").fillna(0.0)
    d["dwelling"] = pd.to_numeric(d.Dwelling, errors="coerce").fillna(0.0)
    assert not d.MB_CODE.duplicated().any()
    return d[["MB_CODE", "category", "person", "dwelling"]].reset_index(drop=True)


def load_mb(year, counts):
    """NSW MB polygons with counts, EPSG:3577, only MBs with residents or dwellings."""
    if year == 2016:
        src, code, where = f"/vsizip/{SOURCES['mb_2016_bnd']['path']}/MB_2016_NSW.shp", "MB_CODE16", None
    else:
        src, code, where = (f"/vsizip/{SOURCES['mb_2021_bnd']['path']}/MB_2021_AUST_GDA94.shp", "MB_CODE21",
                            "STE_CODE21 = '1'")
    # the filter field must be among the columns read, or GDAL silently returns no rows
    g = pyogrio.read_dataframe(src, columns=[code] + (["STE_CODE21"] if where else []), where=where)
    g = g.rename(columns={code: "MB_CODE"})[["MB_CODE", "geometry"]]
    g["MB_CODE"] = g.MB_CODE.astype(str)
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    info = {"boundary_mbs": int(len(g))}
    g = g.merge(counts[["MB_CODE", "person", "dwelling"]], on="MB_CODE", how="left")
    info["boundary_mbs_without_counts"] = int(g.person.isna().sum())
    g = g[(g.person.fillna(0) > 0) | (g.dwelling.fillna(0) > 0)].copy()
    g = g.to_crs(CRS)
    g["geometry"] = shapely.make_valid(g.geometry.values)
    info["mbs_with_people_or_dwellings"] = int(len(g))
    return g.reset_index(drop=True), info


def split_mb_by_lga(mb, lga):
    """Cut MBs at council lines. Returns pieces with region_id, person, dwelling (area-shared) and geometry."""
    lg = lga.geometry.values
    shapely.prepare(lg)
    tree = shapely.STRtree(lg)
    mi, li = tree.query(mb.geometry.values, predicate="intersects")
    hits = np.bincount(mi, minlength=len(mb))
    area = shapely.area(mb.geometry.values)
    rows = []
    # MBs touching exactly one council: whole
    one = np.where(hits == 1)[0]
    first = pd.Series(li, index=mi).groupby(level=0).first()
    rows.append(pd.DataFrame({"mb": one, "lga": first.loc[one].values, "frac": 1.0,
                              "geometry": mb.geometry.values[one]}))
    # MBs touching several councils: cut
    multi = np.isin(mi, np.where(hits > 1)[0])
    a, b = mi[multi], li[multi]
    parts = shapely.intersection(mb.geometry.values[a], lg[b])
    frac = shapely.area(parts) / area[a]
    keep = frac > 1e-9
    rows.append(pd.DataFrame({"mb": a[keep], "lga": b[keep], "frac": frac[keep], "geometry": parts[keep]}))
    p = pd.concat(rows, ignore_index=True)
    # MBs in no council polygon (e.g. offshore slivers) are reported, not placed
    none = np.where(hits == 0)[0]
    # renormalise so each MB's counts are kept exactly (fractions of cut MBs can sum to 1 +/- boundary noise)
    p["frac"] = p.frac / p.groupby("mb").frac.transform("sum")
    p["region_id"] = lga.LGA_CODE21.astype(str).values[p.lga.values]
    p["person"] = mb.person.fillna(0).values[p.mb.values] * p.frac
    p["dwelling"] = mb.dwelling.fillna(0).values[p.mb.values] * p.frac
    p["area"] = shapely.area(p.geometry.values)
    p = p[p.area > 0].reset_index(drop=True)
    info = {"mbs_cut_by_council_lines": int((hits > 1).sum()), "mbs_outside_all_councils": int(len(none)),
            "persons_outside_all_councils": float(mb.person.fillna(0).values[none].sum())}
    return p, info


# ------------------------------------------------------------------ allocation
def allocate(zone, parts, tree):
    """Σ counts × area share of each MB piece inside `zone`, by council. Returns DataFrame region_id, person, dwelling."""
    if zone is None or shapely.is_empty(zone):
        return pd.DataFrame(columns=["region_id", "person", "dwelling"])
    shapely.prepare(zone)
    idx = tree.query(zone, predicate="intersects")
    if not len(idx):
        return pd.DataFrame(columns=["region_id", "person", "dwelling"])
    geoms = parts.geometry.values[idx]
    inside = shapely.contains_properly(zone, geoms)
    share = np.ones(len(idx))
    edge = ~inside
    if edge.any():
        # clip the zone to each edge piece's box first: much faster than intersecting with a huge outline
        eg = geoms[edge]
        bx = shapely.bounds(eg)
        clipped = [shapely.clip_by_rect(zone, *b) for b in bx]
        share[edge] = shapely.area(shapely.intersection(eg, np.array(clipped, dtype=object))) / parts.area.values[idx][edge]
    share = np.clip(share, 0, 1)
    d = pd.DataFrame({"region_id": parts.region_id.values[idx], "person": parts.person.values[idx] * share,
                      "dwelling": parts.dwelling.values[idx] * share})
    return d.groupby("region_id", as_index=False)[["person", "dwelling"]].sum()


def _zones(geom):
    z = {"in_fire": geom}
    for k, m in BUFFERS_M.items():
        z[k] = shapely.buffer(geom, m, quad_segs=8)
    return z


def compute(units, geoms, vintages, parts, trees, keys):
    """units: DataFrame of rows to fill (keys + region_id); geoms: {unit key: outline}; vintages: {unit key: year}."""
    out = []
    t0 = time.time()
    regions = units.groupby("_key").region_id.apply(list).to_dict()
    for i, (k, g) in enumerate(geoms.items()):
        v = vintages[k]
        z = _zones(g)
        res = {name: allocate(zg, parts[v], trees[v]).set_index("region_id") for name, zg in z.items()}
        for rid in regions.get(k, []):
            r = dict(zip(keys, k if isinstance(k, tuple) else (k,)))
            r["region_id"] = rid
            r["census_year"] = v
            for name, d in res.items():
                p = float(d.person.get(rid, 0.0)) if len(d) else 0.0
                w = float(d.dwelling.get(rid, 0.0)) if len(d) else 0.0
                col = "in_fire" if name == "in_fire" else f"within_{name}"
                r[f"pop_{col}"] = p
                r[f"dwellings_{col}"] = w
            # whole zone, all NSW councils (buffers spill into councils the fire did not burn)
            r["pop_within_5km_all_councils"] = float(res["5km"].person.sum()) if len(res["5km"]) else 0.0
            out.append(r)
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(geoms)} outlines, {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(out)


# ------------------------------------------------------------------ inputs
def fire_rows():
    f = pd.read_csv(OUT / "fires.csv", low_memory=False, dtype={"region_id": str},
                    usecols=["event_id", "event_name", "region_id", "region_name", "date_start",
                             "official_declaration_agrn", "DL_house_loss_raw"])
    ev = gpd.read_parquet(CACHE / "fires.parquet")[["event_id", "start", "geometry"]]
    assert ev.crs.to_epsg() == CRS
    missing = set(f.event_id) - set(ev.event_id)
    assert not missing, f"{len(missing)} fires in out/fires.csv have no cached outline"
    return f, ev.set_index("event_id")


def vintage(year):
    return 2016 if year <= 2020 else 2021


def published_total(year):
    t = SOURCES[f"qs_{year}"]["path"].read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))
    m = re.search(r"People ([\d,]+)", t)
    return int(m.group(1).replace(",", ""))


# ------------------------------------------------------------------ docs
SRC_TXT = ("ABS Census Mesh Block Counts 2016 (2074.0) / 2021 × ABS ASGS Mesh Block boundaries 2016 / 2021 × GA fire "
           "outline × ABS LGA 2021")
AREA_NOTE = ("Area-weighted: each Mesh Block's residents are assumed spread evenly over its area, so a zone gets "
             "(MB count × share of the MB's area inside it). ABS randomly adjusts MB counts; values are not rounded")
DOC = {
    "pop_in_fire": ["Usual residents of this council living inside the fire's burned outline", "persons", SRC_TXT,
                    AREA_NOTE + ". 2016 Census for fires starting to 2020, 2021 after (census_year)"],
    "pop_within_1km": ["Usual residents of this council within 1 km of the burned outline (outline included)",
                       "persons", SRC_TXT, AREA_NOTE + ". NSW Mesh Blocks only: the buffer stops at the state border"],
    "pop_within_5km": ["Usual residents of this council within 5 km of the burned outline (outline included)",
                       "persons", SRC_TXT, AREA_NOTE + ". NSW Mesh Blocks only: the buffer stops at the state border"],
    "pop_within_5km_all_councils": ["Usual residents within 5 km of the whole fire, all NSW councils (a whole-fire "
                                    "figure: repeated on each council row, do not sum across rows)", "persons",
                                    SRC_TXT, "Includes councils the buffer reaches but the fire did not burn"],
    "dwellings_in_fire": ["Dwellings of this council inside the fire's burned outline", "dwellings", SRC_TXT,
                          AREA_NOTE + ". ABS MB dwelling count: occupied dwellings (private and non-private) plus "
                                      "unoccupied private dwellings, except those in caravan parks, marinas and "
                                      "manufactured home estates. Not the same as Census 'private dwellings'"],
    "dwellings_within_1km": ["Dwellings of this council within 1 km of the burned outline", "dwellings", SRC_TXT,
                             AREA_NOTE],
    "dwellings_within_5km": ["Dwellings of this council within 5 km of the burned outline", "dwellings", SRC_TXT,
                             AREA_NOTE],
    "census_year": ["Census year of the Mesh Block counts and boundaries used", "year", "ABS Census",
                    "2016 for fires starting to 2020, 2021 after (same rule as SEIFA and dwellings_census)"],
}
DOC_EC = {k: [v[0].replace("the fire's burned outline", "the union of the declared event's fire outlines")
              .replace("the burned outline", "the union of the event's fire outlines")
              .replace("the whole fire", "the whole event"), *v[1:]] for k, v in DOC.items()}
DOC_EC["census_year"][3] = "Year of the event's first fire start: 2016 Census to 2020, 2021 after"


# ------------------------------------------------------------------ main
def main():
    fetch_all()
    checks = {}
    from src.regions import load_lgas
    lga = load_lgas()

    counts, parts, trees = {}, {}, {}
    for y in (2016, 2021):
        c = load_counts(y)
        counts[y] = c
        mb, info = load_mb(y, c)
        p, info2 = split_mb_by_lga(mb, lga)
        parts[y], trees[y] = p, shapely.STRtree(p.geometry.values)
        pub = published_total(y)
        tot = float(c.person.sum())
        spatial = float(mb.person.sum())
        checks[f"census_{y}"] = dict(
            nsw_mb_persons_total=tot, published_nsw_people=pub, diff=tot - pub, diff_pct=100 * (tot - pub) / pub,
            pass_within_0_1pct=bool(abs(tot - pub) / pub < 0.001),
            nsw_mb_dwellings_total=float(c.dwelling.sum()),
            persons_in_mbs_without_boundary=float(c.person.sum() - spatial),
            persons_placed_on_council_pieces=float(p.person.sum()),
            conservation_ok=bool(abs(p.person.sum() + info2["persons_outside_all_councils"] - spatial) < 1e-3),
            # nearly everyone must sit in an MB with a boundary (only the no-usual-address etc. pseudo-MBs have none)
            share_persons_placed=float(p.person.sum() / tot),
            pass_placed_ge_99_5pct=bool(p.person.sum() / tot >= 0.995),
            **info, **info2)
        print(y, checks[f"census_{y}"], flush=True)
        del mb

    f, ev = fire_rows()
    # ---- fire × council
    f["_key"] = f.event_id
    ids = list(dict.fromkeys(f.event_id))
    geoms = {e: ev.geometry.loc[e] for e in ids}
    vint = {e: vintage(pd.Timestamp(ev.start.loc[e]).year) for e in ids}
    print(f"fire × council: {len(f)} rows, {len(ids)} fires", flush=True)
    r = compute(f[["_key", "region_id"]], geoms, vint, parts, trees, ["event_id"])
    r = r.sort_values(["event_id", "region_id"]).reset_index(drop=True)
    assert len(r) == len(f) and not r.duplicated(["event_id", "region_id"]).any()

    # ---- declared event × council (union of the linked fires' outlines)
    kc = pd.read_csv(OUT / "key_event_council.csv", dtype={"agrn": str, "region_id": str},
                     usecols=["agrn", "region_id", "region_name", "first_fire_start"])
    fx = f.assign(agrn=f.official_declaration_agrn.fillna("").astype(str).str.split(";")).explode("agrn")
    fx = fx[fx.agrn != ""]
    kc["_key"] = kc.agrn
    eg, ev_v = {}, {}
    for a, g in fx.groupby("agrn"):
        if a not in set(kc.agrn):
            continue
        eg[a] = shapely.union_all(ev.geometry.loc[g.event_id.unique()].values)
        ev_v[a] = vintage(pd.Timestamp(ev.start.loc[g.event_id.unique()].min()).year)
    print(f"event × council: {len(kc)} rows, {len(eg)} declared events", flush=True)
    rec = compute(kc[kc.agrn.isin(eg)][["_key", "region_id"]], eg, ev_v, parts, trees, ["agrn"])
    rec = kc[["agrn", "region_id"]].merge(rec, on=["agrn", "region_id"], how="left")

    # ---- plausibility checks on known fires
    names = {"F_e69a83842cba888fd5": "Reedy Swamp / Tathra, 18 Mar 2018 (Bega Valley)",
             "F_376183e9aca0552837": "Sir Ivan, Feb 2017",
             "F_aea39039701790dc8a": "Busbys Flat Rd (Rappville), Oct 2019",
             "F_69e8b2057c2d321b84": "Old School Road, Busbys Flat, Sep 2024 (2021 Census)"}
    lab = f.drop_duplicates(["event_id", "region_id"]).set_index(["event_id", "region_id"])
    pl = []
    for e, nm in names.items():
        for x in r[r.event_id == e].itertuples():
            pl.append(dict(fire=nm, council=lab.loc[(e, x.region_id), "region_name"], census_year=x.census_year,
                           pop_in_fire=round(x.pop_in_fire, 1), pop_within_1km=round(x.pop_within_1km, 1),
                           pop_within_5km=round(x.pop_within_5km, 1), dwellings_in_fire=round(x.dwellings_in_fire, 1),
                           whole_fire_homes_destroyed_reported=lab.loc[(e, x.region_id), "DL_house_loss_raw"]))
    pl = pd.DataFrame(pl)
    print(pl.to_string(), flush=True)
    t = r[r.event_id == "F_e69a83842cba888fd5"].iloc[0]
    mono = bool(((r.pop_in_fire <= r.pop_within_1km + 1e-6) & (r.pop_within_1km <= r.pop_within_5km + 1e-6)).all())
    checks["plausibility"] = dict(
        known_fires=pl.to_dict("records"),
        tathra_pop_in_fire_in_100_to_2000=bool(100 <= t.pop_in_fire <= 2000),
        tathra_dwellings_in_fire_ge_homes_destroyed_65=bool(t.dwellings_in_fire >= 65),
        buffers_monotone_all_rows=mono,
        no_negative=bool((r.select_dtypes("number") >= -1e-9).all().all()))
    checks["coverage"] = dict(
        fire_council_rows=int(len(r)), fires=int(r.event_id.nunique()),
        rows_census_2016=int((r.census_year == 2016).sum()), rows_census_2021=int((r.census_year == 2021).sum()),
        rows_pop_in_fire_gt0=int((r.pop_in_fire > 0).sum()), rows_pop_in_fire_ge1=int((r.pop_in_fire >= 1).sum()),
        rows_pop_within_5km_gt0=int((r.pop_within_5km > 0).sum()),
        total_pop_in_fire_2019_20_season_rows=float(r[r.event_id.isin(
            ev.index[(ev.start >= "2019-07-01") & (ev.start < "2020-07-01")])].pop_in_fire.sum()),
        event_council_rows=int(len(rec)), event_council_rows_computed=int(rec.pop_in_fire.notna().sum()))
    print(json.dumps(checks["plausibility"] | {"known_fires": "above"}, indent=1, default=str))
    print(json.dumps(checks["coverage"], indent=1))

    ENRICH.mkdir(parents=True, exist_ok=True)
    cols = ["event_id", "region_id", "census_year", "pop_in_fire", "pop_within_1km", "pop_within_5km",
            "pop_within_5km_all_councils", "dwellings_in_fire", "dwellings_within_1km", "dwellings_within_5km"]
    r = r[cols]
    r["census_year"] = r.census_year.astype("Int64")
    r.to_parquet(ENRICH / "affected_pop.parquet", index=False)
    r.to_csv(ENRICH / "affected_pop.csv", index=False)
    (ENRICH / "affected_pop.doc.json").write_text(json.dumps(DOC, indent=1, ensure_ascii=False))
    rec = rec[["agrn"] + cols[1:]]
    rec["census_year"] = rec.census_year.astype("Int64")
    rec.to_parquet(ENRICH / "affected_pop_event_council.parquet", index=False)
    rec.to_csv(ENRICH / "affected_pop_event_council.csv", index=False)
    (ENRICH / "affected_pop_event_council.doc.json").write_text(json.dumps(DOC_EC, indent=1, ensure_ascii=False))
    checks["sources"] = {k: dict(url=v["url"], local=str(v["path"])) for k, v in SOURCES.items()}
    (ENRICH / "affected_pop_checks.json").write_text(json.dumps(checks, indent=1, default=str, ensure_ascii=False))
    ok = all([checks["census_2016"]["pass_within_0_1pct"], checks["census_2021"]["pass_within_0_1pct"],
              checks["census_2016"]["conservation_ok"], checks["census_2021"]["conservation_ok"],
              checks["census_2016"]["pass_placed_ge_99_5pct"], checks["census_2021"]["pass_placed_ge_99_5pct"],
              checks["plausibility"]["tathra_pop_in_fire_in_100_to_2000"], mono, checks["plausibility"]["no_negative"]])
    print("SELF-CHECK", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    main()
