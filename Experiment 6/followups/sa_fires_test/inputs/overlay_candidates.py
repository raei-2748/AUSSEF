"""Measured share of each council burned, for candidate extra fires (SCOPING; local files only, nothing downloaded).

Inputs already on the user's disk:
  * Geoscience Australia national historical bushfire boundaries (ga_original.zip, gdb) + fire_attributes.csv
  * ABS LGA boundary shapefiles (vintages 2015/2016/2018/2020/2021)
  * ABS ERP by LGA (32180DS0004_2001-25.xlsx) - only to label councils with a population

For each candidate event: select GA bushfire / unknown-type polygons by state, ignition-date window, minimum area
(and optionally a name pattern), dissolve them, intersect with the LGA layer of the chosen vintage and report the
share of each LGA inside the outline. This is an overlay of GA outlines on ABS LGA boundaries; it is not a loss
figure, and the polygon selection is the scoper's choice (see EVENTS). Output: overlay_candidates.csv and
overlay_summary.csv next to this file.

Run: /Users/ray/Research/AUSSEF - Local/.venv/bin/python overlay_candidates.py
"""
import re
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
import shapely

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
P1 = Path("/Users/ray/.codex/.chatgpt-projects/g-p-6a5b3606787c8191a3404241c6dbb6c0/dataset_phase1/raw")
GA_ZIP = P1 / "ga_original.zip"
GA_ATTR = P1 / "fire_attributes.csv"
GDB = f"/vsizip/{GA_ZIP}/Bushfire_Boundaries_Historical.gdb"
ERP = Path("/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/abs/32180DS0004_2001-25.xlsx")
CRS = 3577

LGA_FILES = {  # vintage -> (shapefile, code col, name col)
    "2015": ("lga_2015/LGA_2015_AUST.shp", "LGA_CODE15", "LGA_NAME15"),
    "2016": ("lga_2016/LGA_2016_AUST.shp", "LGA_CODE16", "LGA_NAME16"),
    "2018": ("lga_2018/LGA_2018_AUST.shp", "LGA_CODE18", "LGA_NAME18"),
    "2020": ("lga_2020/LGA_2020_AUST.shp", "LGA_CODE20", "LGA_NAME20"),
    "2021": ("lga_2021/LGA_2021_AUST_GDA94.shp", "LGA_CODE21", "LGA_NAME21"),
}
STATE_DIGIT = {"NSW": "1", "VIC": "2", "QLD": "3", "SA": "4", "WA": "5", "TAS": "6"}

# key, state, first ignition date, last ignition date, min area ha, name regex (None = any), LGA vintage, note
EVENTS = [
    # --- Victoria
    ("VIC_2003_alpine", "VIC", "2003-01-01", "2003-03-31", 20000, None, "2015", "Jan 2003 alpine fires"),
    ("VIC_2006_07_great_divide", "VIC", "2006-11-25", "2007-02-28", 20000, None, "2015", "Great Divide fires"),
    ("VIC_2009_black_saturday", "VIC", "2009-02-04", "2009-02-09", 1000, None, "2015", "7 Feb 2009 and neighbours"),
    ("VIC_2013_jan", "VIC", "2013-01-01", "2013-01-31", 2000, None, "2015", "Jan 2013 (Aberfeldy etc.)"),
    ("VIC_2014_jan_feb", "VIC", "2014-01-01", "2014-03-15", 2000, None, "2015", "Jan-Feb 2014"),
    ("VIC_2015_wye_river_scotsburn", "VIC", "2015-12-15", "2015-12-25", 500, None, "2016", "Dec 2015"),
    ("VIC_2019_20_black_summer", "VIC", "2019-11-15", "2020-02-28", 1000, None, "2018", "2019-20 (Vic LGAs only)"),
    # --- South Australia
    ("SA_2005_wangary", "SA", "2005-01-09", "2005-01-12", 5000, None, "2015", "Wangary"),
    ("SA_2015_sampson_flat", "SA", "2015-01-01", "2015-01-10", 5000, None, "2015", "Sampson Flat"),
    ("SA_2015_pinery", "SA", "2015-11-24", "2015-11-28", 10000, None, "2016", "Pinery"),
    ("SA_2019_cudlee_creek", "SA", "2019-12-15", "2019-12-25", 1000, r"Cudlee", "2018", "Cudlee Creek"),
    ("SA_2019_20_kangaroo_island", "SA", "2019-12-15", "2020-01-31", 1000, r"^(Ravine|KI Complex)", "2018", "Ravine + KI Complex"),
    # --- Tasmania
    ("TAS_2013_jan", "TAS", "2013-01-02", "2013-01-08", 2000, None, "2015", "Jan 2013 (Dunalley/Forcett etc.)"),
    ("TAS_2016_jan", "TAS", "2016-01-10", "2016-02-15", 5000, None, "2016", "Jan-Feb 2016 (mostly WHA)"),
    ("TAS_2019_jan", "TAS", "2019-01-10", "2019-03-15", 5000, None, "2018", "Jan 2019 (Riveaux Rd etc.)"),
    # --- Queensland (remote savanna councils will show large shares; filter by population/declaration afterwards)
    ("QLD_2018_nov", "QLD", "2018-11-15", "2018-12-15", 3000, None, "2018", "Nov 2018"),
    ("QLD_2019_sep_nov", "QLD", "2019-08-15", "2019-11-30", 5000, None, "2018", "Sep-Nov 2019"),
    # --- Western Australia (remote pastoral shires will show large shares; filter by population/declaration afterwards)
    ("WA_2011_jan_perth_hills", "WA", "2011-01-01", "2011-02-15", 100, None, "2015", "Jan 2011 (Roleystone)"),
    ("WA_2011_nov_margaret_river", "WA", "2011-11-15", "2011-11-30", 1000, r"MILYEANNUP", "2015", "Nov 2011 (Margaret River)"),
    ("WA_2014_jan", "WA", "2014-01-01", "2014-01-31", 100, None, "2015", "Jan 2014 (Perth Hills)"),
    ("WA_2015_nov", "WA", "2015-11-01", "2015-11-30", 3000, None, "2016", "Nov 2015 (Esperance etc.)"),
    ("WA_2016_jan_waroona", "WA", "2016-01-01", "2016-01-31", 3000, None, "2016", "Jan 2016 (Waroona-Yarloop etc.)"),
    ("VIC_2018_mar_south_west", "VIC", "2018-03-15", "2018-03-20", 500, None, "2018", "Mar 2018 (Terang, Camperdown, Garvoc)"),
    ("VIC_2019_mar_bunyip_licola", "VIC", "2019-02-25", "2019-03-10", 2000, None, "2018", "Feb-Mar 2019 (Bunyip, Licola, Dargo)"),
    ("SA_2014_bangor", "SA", "2014-01-20", "2014-02-10", 1000, None, "2015", "Bangor Jan-Feb 2014"),
    ("SA_2019_20_keilira", "SA", "2019-12-25", "2020-01-05", 1000, r"Keilira", "2018", "Keilira"),
    ("WA_2021_wooroloo", "WA", "2021-02-01", "2021-02-06", 1000, None, "2020", "Wooroloo Feb 2021"),
    ("WA_2022_feb_wheatbelt_sw", "WA", "2022-02-01", "2022-02-28", 3000, None, "2021", "Feb 2022 (Shackleton, Narrogin East, Bridgetown)"),
    # --- NSW earlier than the existing 2015-2025 dataset (pre-amalgamation LGA 2015 boundaries)
    ("NSW_2013_jan", "NSW", "2013-01-05", "2013-01-20", 3000, None, "2015", "Jan 2013 (Wambelong etc.)"),
    ("NSW_2013_oct", "NSW", "2013-10-10", "2013-10-31", 1000, None, "2015", "Oct 2013 (State Mine, Springwood etc.)"),
]


def load_ga():
    a = pd.read_csv(GA_ATTR, low_memory=False)
    a["st"] = a.state.str.extract(r"^([A-Z]+)")[0]
    a["dt"] = pd.to_datetime(a.ignition_date, errors="coerce", utc=True).dt.tz_localize(None)
    return a[a.fire_type != "Prescribed Burn"].copy()


def load_lga(v):
    f, code, name = LGA_FILES[v]
    g = gpd.read_file(P1 / f.split("/")[0] / f.split("/")[1]).to_crs(CRS)
    g = g.rename(columns={code: "lga_code", name: "lga_name"})
    g["lga_code"] = g.lga_code.astype(str)
    g = g[g.lga_code.str.match(r"^\d{5}$")]  # drop 'unincorporated'/'no usual address' style codes
    g["lga_area_km2"] = g.geometry.area / 1e6
    g["geometry"] = shapely.make_valid(g.geometry.values)
    return g[["lga_code", "lga_name", "lga_area_km2", "geometry"]]


def load_erp():
    t = pd.read_excel(ERP, sheet_name="Table 1", header=None, skiprows=6)
    t = t.iloc[:, [0, 1, 17]]  # col 17 = 2016 (2001 is col 2)
    t.columns = ["lga_code", "erp_name", "erp_2016"]
    t["lga_code"] = t.lga_code.astype(str).str.strip()
    t["erp_2016"] = pd.to_numeric(t.erp_2016, errors="coerce")
    return t.dropna(subset=["erp_2016"])


def main():
    ga, erp = load_ga(), load_erp()
    lga_cache, rows, summ = {}, [], []
    for key, st, d0, d1, minha, pat, vint, note in EVENTS:
        sel = ga[(ga.st == st) & (ga.dt >= pd.Timestamp(d0)) & (ga.dt <= pd.Timestamp(d1) + pd.Timedelta(days=1)) & (ga.area_ha >= minha)]
        if pat:
            sel = sel[sel.fire_name.fillna("").str.contains(pat, flags=re.I, regex=True)]
        if sel.empty:
            summ.append(dict(event=key, note=note, n_polygons=0)); continue
        fids = sel.source_objectid.astype(int).sort_values().values
        g = pyogrio.read_dataframe(GDB, fids=fids, columns=["state", "area_ha"])
        chk = sel.set_index("source_objectid").loc[fids]
        assert len(g) == len(fids) and np.allclose(g.area_ha.values, chk.area_ha.values), f"{key}: FID/attribute mismatch"
        g = g.to_crs(CRS)
        geom = shapely.union_all(shapely.make_valid(g.geometry.values))
        ev = gpd.GeoDataFrame({"event": [key]}, geometry=[geom], crs=CRS)
        if vint not in lga_cache:
            lga_cache[vint] = load_lga(vint)
        L = lga_cache[vint]
        L = L[L.lga_code.str[0] == STATE_DIGIT[st]]
        hit = gpd.overlay(L, ev, how="intersection", keep_geom_type=True)
        hit["burned_km2"] = hit.geometry.area / 1e6
        hit["share"] = hit.burned_km2 / hit.lga_area_km2
        hit = hit.merge(erp[["lga_code", "erp_2016"]], on="lga_code", how="left")
        hit["event"], hit["lga_vintage"], hit["state"] = key, vint, st
        rows.append(hit.drop(columns="geometry"))
        s = hit.share
        summ.append(dict(event=key, note=note, state=st, lga_vintage=vint, n_polygons=len(sel),
                         polygon_area_ha_sum=float(sel.area_ha.sum()), union_km2=geom.area / 1e6,
                         n_lga_ge_2pct=int((s >= .02).sum()), n_lga_ge_5pct=int((s >= .05).sum()),
                         n_lga_ge_10pct=int((s >= .10).sum()), n_lga_ge_20pct=int((s >= .20).sum()),
                         n_lga_ge_5pct_pop_ge_2000=int(((s >= .05) & (hit.erp_2016 >= 2000)).sum()),
                         n_lga_ge_20pct_pop_ge_2000=int(((s >= .20) & (hit.erp_2016 >= 2000)).sum())))
        print(f"{key:32s} polys={len(sel):3d} union={geom.area / 1e6:9.0f} km2  >=5%: {int((s >= .05).sum()):2d}  >=20%: {int((s >= .20).sum()):2d}", flush=True)
    out = pd.concat(rows).sort_values(["event", "share"], ascending=[True, False])
    out["share"] = out.share.round(4)
    out["burned_km2"] = out.burned_km2.round(1)
    out["lga_area_km2"] = out.lga_area_km2.round(1)
    out.to_csv(HERE / "overlay_candidates.csv", index=False)
    pd.DataFrame(summ).to_csv(HERE / "overlay_summary.csv", index=False)


if __name__ == "__main__":
    main()
