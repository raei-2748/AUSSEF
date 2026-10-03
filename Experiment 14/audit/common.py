"""Auditor's own loaders (written independently of the project build code)."""
import re, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
ROOT = "/Users/ray/Research/AUSSEF - Local/"
AUD = ROOT + "Experiment 14/audit/"

def norm(s):
    s = str(s).lower().replace("(nsw)", "").replace("(new)", "").replace("&", " and ")
    s = re.sub(r"[-'.,]", " ", s)
    s = re.sub(r"\b(city|shire|regional|council|municipal|municipality|of|the|lga|a|c|s)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return ALIAS.get(s, s)

ALIAS = {"nambucca": "nambucca valley"}   # Nambucca Shire renamed Nambucca Valley (same council, same area)

def councils():
    c = pd.read_csv(ROOT + "Experiment 6/results/COUNCIL_ITEMS_v2.csv", usecols=["region_id", "region_name_x"])
    c["region_id"] = c.region_id.astype(int)
    c["key"] = c.region_name_x.map(norm)
    assert c.key.is_unique
    return c

def master():
    m = pd.read_excel(ROOT + "data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx", sheet_name="master",
                      header=2, keep_default_na=False, na_values=[""])
    m["region_id"] = m.region_id.astype(int)
    m["F"] = m.info_fire_fy.str[:4].astype(int)
    m["start"] = pd.to_datetime(m.first_fire_start)
    m["m0"] = m.start.dt.to_period("M")
    m["F_from_date"] = np.where(m.start.dt.month >= 7, m.start.dt.year, m.start.dt.year - 1)
    return m

def adjacency():
    a = pd.read_csv(ROOT + "Experiment 12/results/ADJACENCY.csv").astype(int)
    nb = {}
    for r, n in a.itertuples(index=False):
        nb.setdefault(r, set()).add(n); nb.setdefault(n, set()).add(r)   # symmetrise
    return a, nb

def burned_share_fy():
    f = pd.read_csv(ROOT + "fire_event_dataset/out/fires.csv", usecols=["region_id", "date_start", "share_of_region_burned"], low_memory=False)
    d = pd.to_datetime(f.date_start)
    f["FY"] = np.where(d.dt.month >= 7, d.dt.year, d.dt.year - 1)
    f["region_id"] = f.region_id.astype(int)
    return f.groupby(["region_id", "FY"]).share_of_region_burned.sum()

def far_sets(m=None):
    m = master() if m is None else m
    c = councils(); _, nb = adjacency(); bs = burned_share_fy()
    out = {}
    for F, g in m.groupby("F"):
        mast = set(g.region_id)
        neigh = set().union(*[nb.get(r, set()) for r in mast]) - mast
        far = []
        for r in c.region_id:
            if r in mast or r in neigh: continue
            if bs.get((r, F), 0.0) >= 0.005: continue
            far.append(r)
        out[F] = sorted(far)
    return out

def olg_long():
    o = pd.read_parquet(ROOT + "fire_event_dataset/data/olg/olg_long.parquet")
    c = councils(); k2id = dict(zip(c.key, c.region_id))
    o["key"] = o.council_name.map(norm)
    o["region_id"] = o.key.map(k2id)
    return o

# names that are pre-2016 councils sharing a key with a post-merger council
PRE2016_SAME_NAME = {"dubbo", "murrumbidgee", "parramatta"}

def olg_wide(drop_pre2016_namesakes=True):
    o = olg_long()
    o = o[o.region_id.notna()].copy()
    if drop_pre2016_namesakes:
        # old Dubbo City / Murrumbidgee Shire / Parramatta City existed only before FY2016
        o = o[~((o.key.isin(PRE2016_SAME_NAME)) & (o.fy_start < 2016))]
    o["region_id"] = o.region_id.astype(int)
    w = o.pivot_table(index=["region_id", "fy_start"], columns="metric", values="value", aggfunc="first")
    return w

def olg_groups():
    g = pd.read_excel(ROOT + "fire_event_dataset/data/olg/time-series-data-2018-2019.xlsx", sheet_name="2018_19_Councils", header=None)
    g = g.iloc[3:, :3]; g.columns = ["council", "group", "cls"]
    g = g[g.council.notna()]
    c = councils(); k2id = dict(zip(c.key, c.region_id))
    g["key"] = g.council.map(norm); g["region_id"] = g.key.map(k2id)
    return g

def rent():
    r = pd.read_parquet(ROOT + "fire_event_dataset/data/rent/rent_lga_quarter.parquet")
    r = r[r.region_id.notna()].copy()
    r["region_id"] = r.region_id.astype(int)
    return r

def bocsar_dv():
    """Monthly DV-related assault counts by region_id (auditor's own read). Cached in audit/_bocsar_dv.parquet."""
    import os
    p = AUD + "_bocsar_dv.parquet"
    if os.path.exists(p):
        return pd.read_parquet(p)
    b = pd.read_excel(ROOT + "fire_event_dataset/data/raw/bocsar/RCI_offencebymonth.xlsm", sheet_name="Data", header=0)
    cols = list(b.columns)
    b = b[b.iloc[:, 2].astype(str).str.strip() == "Domestic violence related assault"]
    long = b.melt(id_vars=cols[:3], value_vars=cols[3:], var_name="month", value_name="n")
    long.columns = ["lga", "cat", "sub", "month", "n"]
    long["month"] = pd.to_datetime(long.month).dt.to_period("M").astype(str)
    long["n"] = pd.to_numeric(long.n, errors="coerce")
    long = long[["lga", "month", "n"]]
    long.to_parquet(p)
    return long

def window_excess(series, m, far, post_offsets, pre_offsets, transform=None, min_far=5, far_override=None):
    """series: dict (region_id, fy) -> value. Own change = mean(post) - mean(pre) over available years (>=1 each).
    Excess = own - median over FAR councils (for the row's F) with a value; < min_far -> NaN."""
    f = (lambda v: v) if transform is None else transform
    def change(r, F):
        po = [f(series[(r, F + k)]) for k in post_offsets if (r, F + k) in series]
        pr = [f(series[(r, F + k)]) for k in pre_offsets if (r, F + k) in series]
        if not po or not pr: return np.nan
        return float(np.mean(po) - np.mean(pr))
    cache = {}; own = []; exc = []; ncmp = []
    for _, row in m.iterrows():
        F = row.F
        pool = far[F] if far_override is None else far_override(row)
        key = (F, tuple(pool))
        if key not in cache:
            vals = [change(x, F) for x in pool]; vals = [v for v in vals if np.isfinite(v)]
            cache[key] = (np.median(vals) if len(vals) >= min_far else np.nan, len(vals))
        o = change(row.region_id, F); own.append(o); exc.append(o - cache[key][0]); ncmp.append(cache[key][1])
    return np.array(own), np.array(exc), np.array(ncmp)
