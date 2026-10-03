"""Experiment 18: input-output (IO) model of the Indirect Loss (IL) pillar.

Implements PRESPEC.md section A (locked 2026-10-02 23:30). Interpretation choices are listed in ../DEVIATIONS.md.
All money in A$ million (mixed years; only shares are used for checks and ranks).
"""
from pathlib import Path
import re
import glob
import numpy as np
import pandas as pd
import openpyxl

ROOT = Path("/Users/ray/Research/AUSSEF - Local")
EXP = ROOT / "Experiment 18_hybrid"
IO = EXP / "inputs" / "abs_io"
TRA_DIR = Path.home() / ("Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/"
                         "Fire Dataset Build Inputs (only needed to rebuild the fire dataset)/"
                         "ABS Data by Region - income and labour (14100DO)/tra_lga_2017")
EXPOSURE = ROOT / "Experiment 16_building_exposure/results/EXPOSURE_COUNCIL_FIRE.csv"  # copied from worktree loving-elgamal-98a14c, byte-identical
ANALYSIS = ROOT / "Experiment 14/results/ANALYSIS_TABLE.csv"

REBUILD_COST_M = 0.3443          # A$344,300 per home (Exp 17, E17R-038/040)
TOURISM_IND = ["3901", "4401", "4501", "4601"]   # Retail, Accommodation, Food & beverage, Road transport
CONSTRUCTION_IND = "3001"        # Residential building construction
ACCOM_FOOD_IND = ["4401", "4501"]

# ANZSIC 2006 division by 2-digit subdivision (IO codes are 4-digit; first 2 = subdivision)
DIV_RANGES = [("A", 1, 5), ("B", 6, 10), ("C", 11, 25), ("D", 26, 29), ("E", 30, 32), ("F", 33, 38), ("G", 39, 43),
              ("H", 44, 45), ("I", 46, 53), ("J", 54, 60), ("K", 62, 64), ("L", 66, 67), ("M", 69, 70), ("N", 72, 73),
              ("O", 75, 77), ("P", 80, 82), ("Q", 84, 87), ("R", 89, 92), ("S", 94, 96)]
CENSUS_DIV = {"A": "Ag_For_Fshg", "B": "Mining", "C": "Manufact", "D": "El_Gas_Wt_Waste", "E": "Constru",
              "F": "WhlesaleTde", "G": "RetTde", "H": "Accom_food", "I": "Trans_post_wrehsg",
              "J": "Info_media_teleco", "K": "Fin_Insur", "L": "RtnHir_REst", "M": "Pro_scien_tec",
              "N": "Admin_supp", "O": "Public_admin_sfty", "P": "Educ_trng", "Q": "HlthCare_SocAs",
              "R": "Art_recn", "S": "Oth_scs"}
DIVS = list(CENSUS_DIV)
N = 115                          # IO industries in the 2023-24 tables (header cols 2..116)


def div_of(code):
    s = int(code[:2])
    for d, lo, hi in DIV_RANGES:
        if lo <= s <= hi:
            return d
    raise ValueError(code)


def _rows(fname):
    ws = openpyxl.load_workbook(IO / fname, read_only=True, data_only=True).worksheets[1]
    return list(ws.iter_rows(values_only=True))


def _code(v):
    return None if v is None or str(v).strip() == "" else str(v).strip().zfill(4)


def load_io():
    """National IO pieces, 114 industries."""
    t6 = _rows("520905500106.xlsx")
    codes = [_code(c) for c in t6[0][2:117]]
    assert len(codes) == N and codes[0] == "0101" and codes[-1] == "9502" and t6[1][117] == "Total Industry Uses"
    rmap = {_code(r[0]): r for r in t6[3:] if _code(r[0]) in codes}
    A = np.array([[float(rmap[ci][2 + j] or 0) for j in range(N)] for ci in codes]) / 100.0  # percent -> share

    t5 = _rows("520905500105.xlsx")
    prod = [r for r in t5 if r[1] == "Australian Production"][0]
    x = np.array([float(v) for v in prod[2:117]])                      # output $m

    t2 = _rows("520905500102.xlsx")
    p1 = [r for r in t2 if r[0] == "P1"][0]
    prod2 = [r for r in t2 if r[1] == "Australian Production"][0]
    w = np.array([float(v) for v in p1[2:117]]) / np.array([float(v) for v in prod2[2:117]])  # labour income / output
    hh_col = 118
    assert "Households" in str(t2[1][hh_col])
    r2 = {_code(r[0]): r for r in t2[3:] if _code(r[0]) in codes}
    hh = np.array([float(r2[c][hh_col] or 0) for c in codes])
    t3 = [r for r in t2 if r[0] == "T3"][0]
    hh_total = float(t3[hh_col])
    h = hh / hh_total                                                  # domestic-production share of household spend
    tour_split = pd.Series(hh, index=codes)[TOURISM_IND]
    tour_split = tour_split / tour_split.sum()

    t20 = _rows("520905500120.xlsx")
    emp = {}
    for r in t20:
        c = _code(r[0])
        if c in codes and isinstance(r[2], (int, float)):
            emp[c] = (float(r[2]) + float(r[3])) * 1000.0               # persons (FT + PT)
    jobs = np.array([emp[c] for c in codes])
    divs = np.array([div_of(c) for c in codes])
    return dict(codes=codes, A=A, x=x, w=w, h=h, jobs=jobs, divs=divs, tour_split=tour_split)


def load_census(year):
    g, key = ("G51", "LGA_CODE_2016") if year == 2016 else ("G54", "LGA_CODE_2021")
    fs = sorted(glob.glob(str(ROOT / f"fire_event_dataset/data/abs/gcp{year}/*/{year}Census_{g}*_NSW_LGA.csv")))
    d = pd.concat([pd.read_csv(f).set_index(key) for f in fs], axis=1)
    d = d.loc[:, ~d.columns.duplicated()]
    out = pd.DataFrame({k: d[f"P_{v}_Tot"] for k, v in CENSUS_DIV.items()})
    out.index = out.index.str.replace("LGA", "").astype(int)
    return out


def load_tra():
    """Annual visitor spend $m (TRA 2017 profile, 2014-17 average). 'np' / '-' -> missing."""
    out = {}
    for f in sorted(TRA_DIR.glob("*.xlsx")):
        ws = openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0]
        val = np.nan
        for r in ws.iter_rows(max_row=40, values_only=True):
            if r[1] == "Spend ($m)":
                v = r[8]
                val = float(v) if isinstance(v, (int, float)) else np.nan
                break
        name = re.sub(r" \((A|C)\)", "", f.stem)
        out[name] = val
    s = pd.Series(out)
    s = s.rename({"Nambucca": "Nambucca Valley"})  # renamed council, same area (DEVIATIONS D3)
    return s


def regional_matrices(io, lq, lam):
    """FLQ regionalisation. lq: LQ for each of 114 industries (from its division)."""
    cilq = lq[:, None] / np.where(lq[None, :] > 0, lq[None, :], np.nan)
    cilq = np.nan_to_num(cilq, nan=0.0)
    np.fill_diagonal(cilq, lq)                    # FLQ convention: diagonal uses the industry's own LQ
    Ar = io["A"] * np.minimum(1.0, cilq * lam)
    hr = io["h"] * np.minimum(1.0, lq * lam)       # households as buyer (LQ_hh = 1): CILQ = LQ_i
    wr = io["w"] * np.minimum(1.0, lam / np.where(lq > 0, lq, np.inf))  # households as seller: CILQ = 1/LQ_j
    return Ar, hr, wr


def leontief(Ar, hr, wr, typ):
    n = Ar.shape[0]
    if typ == 1:
        return np.linalg.inv(np.eye(n) - Ar)
    M = np.zeros((n + 1, n + 1))
    M[:n, :n] = Ar
    M[:n, n] = hr
    M[n, :n] = wr
    return np.linalg.inv(np.eye(n + 1) - M)[:n, :n]


def build_rows(season=2019):
    a = pd.read_csv(ANALYSIS)
    a = a[a.season == season].copy()
    e = pd.read_csv(EXPOSURE)
    rows = a[["agrn", "region_id", "region_name", "season", "share", "homes_v2", "DL", "IL", "FP", "SL", "Y_v4"]].merge(
        e, on=["agrn", "region_id", "season"], how="left", suffixes=("", "_e"))
    assert len(rows) == len(a)
    tra = load_tra()
    rows["tra_spend_m"] = rows.region_name.map(tra)
    rows["census_year"] = np.where(rows.season <= 2020, 2016, 2021)   # fires before Jul 2021 -> 2016
    return rows


def unit_responses(rows, io, deltas=(0.1, 0.2, 0.3, 0.4, 0.5), exclude_zero_jobs=False):
    """For every row x delta x type: multiplier response to three unit shocks.
    Returns dict[(i, delta, typ)] -> dict of response vectors (output change per $m of shock) and baselines.
    exclude_zero_jobs (addendum B): drop industries with no employment (owner-occupied dwellings) from the
    business-interruption shock and the per-job ratios. False reproduces v1 exactly.
    """
    cens = {y: load_census(y) for y in (2016, 2021)}
    nsw = {y: c.sum() for y, c in cens.items()}
    xk = io["x"] * (io["jobs"] > 0) if exclude_zero_jobs else io["x"]
    div_out = pd.Series(xk).groupby(io["divs"]).sum()
    div_jobs = pd.Series(io["jobs"]).groupby(io["divs"]).sum()
    div_lab = pd.Series(xk * io["w"]).groupby(io["divs"]).sum()
    codes = io["codes"]
    ci = {c: k for k, c in enumerate(codes)}
    # within-division output shares (to spread division-level job losses over IO industries)
    within = xk / pd.Series(xk).groupby(io["divs"]).transform("sum").values
    tour = np.zeros(N)
    for c, s in io["tour_split"].items():
        tour[ci[c]] = s
    cons = np.zeros(N)
    cons[ci[CONSTRUCTION_IND]] = 1.0
    out = {}
    base = {}
    for i, r in rows.iterrows():
        yr = r.census_year
        if r.region_id not in cens[yr].index:          # code changed between Censuses: use the other one (DEVIATIONS D4)
            yr = 2021 if yr == 2016 else 2016
            if r.region_id not in cens[yr].index:
                continue
        rows.loc[i, "census_used"] = yr
        c = cens[yr]
        emp = c.loc[r.region_id].astype(float)
        tot = emp.sum()
        lq_div = (emp / tot) / (nsw[yr] / nsw[yr].sum())
        lq = np.array([lq_div[d] for d in io["divs"]])
        # business-interruption unit shock: output lost per 1 "council-year of all jobs" spread by industry mix
        bi = np.zeros(N)
        for d in DIVS:
            out_d = emp[d] * div_out[d] / div_jobs[d]
            bi += np.where(io["divs"] == d, within * out_d, 0.0)
        base[i] = dict(jobs=tot,
                       out=float(sum(emp[d] * div_out[d] / div_jobs[d] for d in DIVS)),
                       lab=float(sum(emp[d] * div_lab[d] / div_jobs[d] for d in DIVS)),
                       af_out=float(emp["H"] * div_out["H"] / div_jobs["H"]),
                       bi_annual=bi)
        lam_base = np.log2(1 + tot / nsw[yr].sum())
        for dl in deltas:
            Ar, hr, wr = regional_matrices(io, lq, lam_base ** dl)
            for typ in (1, 2):
                L = leontief(Ar, hr, wr, typ)
                out[(i, dl, typ)] = dict(tour=L @ tour, bi=L @ bi, cons=L @ cons)
    return out, base


def summarise(dx, io):
    """Output change vector ($m) -> totals."""
    jobs_per_m = io["jobs"] / io["x"]
    ci = [io["codes"].index(c) for c in ACCOM_FOOD_IND]
    return dict(output=dx.sum(), jobs=(dx * jobs_per_m).sum(), lab=(dx * io["w"]).sum(), af=dx[ci].sum())
