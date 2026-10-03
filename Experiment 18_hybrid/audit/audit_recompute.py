"""Independent audit re-derivation for Experiment 18 (written by the auditor; does not import src/ or full/ for the
re-derived numbers. src/io_model.py is imported ONLY at the end to compare against the original unit responses).
Run: python3 audit/audit_recompute.py  -> audit/audit_numbers.json
"""
import glob, json, re, sys
from pathlib import Path
import numpy as np, pandas as pd, openpyxl
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

ROOT = Path("/Users/ray/Research/AUSSEF - Local"); EXP = ROOT / "Experiment 18_hybrid"; IO = EXP / "inputs/abs_io"
TRA = Path.home() / ("Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/"
      "Fire Dataset Build Inputs (only needed to rebuild the fire dataset)/ABS Data by Region - income and labour (14100DO)/tra_lga_2017")
EXPO = ROOT / ".claude/worktrees/loving-elgamal-98a14c/Experiment 16_building_exposure/results/EXPOSURE_COUNCIL_FIRE.csv"
OUT = {}

def sheet(f):
    return list(openpyxl.load_workbook(IO / f, read_only=True, data_only=True).worksheets[1].iter_rows(values_only=True))

# ---- national IO, own parsing ----
t5 = sheet("520905500105.xlsx")
hdr = [str(c).zfill(4) if c is not None else None for c in t5[0]]
jcols = [k for k, c in enumerate(hdr) if c and re.fullmatch(r"\d{4}", c)]
codes = [hdr[k] for k in jcols]
def rowdict(rows):
    return {str(r[0]).zfill(4): r for r in rows if r[0] is not None and re.fullmatch(r"\d{3,4}", str(r[0]))}
r5 = rowdict(t5)
Z = np.array([[float(r5[i][k] or 0) for k in jcols] for i in codes])
x = np.array([float([r for r in t5 if r[1] == "Australian Production"][0][k]) for k in jcols])
A = Z / x[None, :]
t6 = sheet("520905500106.xlsx"); r6 = rowdict(t6)
A6 = np.array([[float(r6[i][k] or 0) for k in jcols] for i in codes]) / 100
OUT["n_industries"] = len(codes)
OUT["A_from_T5_vs_T6_max_abs_diff"] = float(np.abs(A - A6).max())
OUT["A_colsum_max"] = float(A6.sum(0).max())
t2 = sheet("520905500102.xlsx"); r2 = rowdict(t2)
hh = [k for k, c in enumerate(t2[1]) if c and str(c).startswith("Households")][0]
x2 = np.array([float([r for r in t2 if r[1] == "Australian Production"][0][k]) for k in jcols])
w = np.array([float([r for r in t2 if r[0] == "P1"][0][k]) for k in jcols]) / x2
hvec = np.array([float(r2[i][hh] or 0) for i in codes]) / float([r for r in t2 if r[0] == "T3"][0][hh])
t20 = sheet("520905500120.xlsx")
jobs = np.array([sum(float(r[k]) for k in (2, 3)) * 1000 for i in codes for r in t20 if str(r[0]).zfill(4) == i and isinstance(r[2], (int, float))])
assert len(jobs) == len(codes)
DIVR = dict(A=(1, 5), B=(6, 10), C=(11, 25), D=(26, 29), E=(30, 32), F=(33, 38), G=(39, 43), H=(44, 45), I=(46, 53),
            J=(54, 60), K=(62, 64), L=(66, 67), M=(69, 70), N=(72, 73), O=(75, 77), P=(80, 82), Q=(84, 87), R=(89, 92), S=(94, 96))
div = np.array([[d for d, (lo, hi) in DIVR.items() if lo <= int(c[:2]) <= hi][0] for c in codes])
CEN = dict(A="Ag_For_Fshg", B="Mining", C="Manufact", D="El_Gas_Wt_Waste", E="Constru", F="WhlesaleTde", G="RetTde",
           H="Accom_food", I="Trans_post_wrehsg", J="Info_media_teleco", K="Fin_Insur", L="RtnHir_REst", M="Pro_scien_tec",
           N="Admin_supp", O="Public_admin_sfty", P="Educ_trng", Q="HlthCare_SocAs", R="Art_recn", S="Oth_scs")

def census(y):
    g, key = ("G51", "LGA_CODE_2016") if y == 2016 else ("G54", "LGA_CODE_2021")
    cols = {}
    for f in glob.glob(str(ROOT / f"fire_event_dataset/data/abs/gcp{y}/*/{y}Census_{g}*_NSW_LGA.csv")):
        d = pd.read_csv(f).set_index(key)
        for dv, nm in CEN.items():
            if f"P_{nm}_Tot" in d:
                cols[dv] = d[f"P_{nm}_Tot"]
    c = pd.DataFrame(cols)[list(CEN)]
    c.index = [int(s.replace("LGA", "")) for s in c.index]
    return c
C = {y: census(y) for y in (2016, 2021)}

def L_of(rid, yr, delta, typ):
    c = C[yr]; e = c.loc[rid].astype(float); nsw = c.sum()
    lqd = (e / e.sum()) / (nsw / nsw.sum()); lq = lqd[div].to_numpy()
    lam = np.log2(1 + e.sum() / nsw.sum()) ** delta
    with np.errstate(divide="ignore", invalid="ignore"):
        cilq = np.where(lq[None, :] > 0, lq[:, None] / lq[None, :], 0.0)
    np.fill_diagonal(cilq, lq)
    Ar = A6 * np.minimum(1, cilq * lam)
    n = len(codes)
    if typ == 1:
        return np.linalg.inv(np.eye(n) - Ar), e, lq, lam
    M = np.zeros((n + 1, n + 1)); M[:n, :n] = Ar
    M[:n, n] = hvec * np.minimum(1, lq * lam)
    M[n, :n] = w * np.minimum(1, lam / np.where(lq > 0, lq, np.inf))
    return np.linalg.inv(np.eye(n + 1) - M)[:n, :n], e, lq, lam

ix = {c: k for k, c in enumerate(codes)}
TOUR = ["3901", "4401", "4501", "4601"]
tour = np.zeros(len(codes)); tw = np.array([hvec[ix[c]] for c in TOUR]); tour[[ix[c] for c in TOUR]] = tw / tw.sum()
cons = np.zeros(len(codes)); cons[ix["3001"]] = 1

# ---- (1) multipliers for 3 councils ----
mult = {}
for name, rid, yr in [("Bega Valley (South Coast, Black Summer)", 10550, 2016), ("Blue Mountains", 10900, 2016),
                      ("Armidale Regional (2021 Census fallback)", 10180, 2021)]:
    L1, e, lq, lam = L_of(rid, yr, 0.3, 1); L2 = L_of(rid, yr, 0.3, 2)[0]
    mult[name] = dict(jobs=float(e.sum()), lq_accom_food=float(lq[ix["4401"]]), lambda_=float(lam),
                      typeI_accom=float(L1[:, ix["4401"]].sum()), typeII_accom=float(L2[:, ix["4401"]].sum()),
                      typeI_tourism_bundle=float((L1 @ tour).sum()), typeII_tourism_bundle=float((L2 @ tour).sum()),
                      typeII_construction=float(L2[:, ix["3001"]].sum()))
L_nat = np.linalg.inv(np.eye(len(codes)) - A6)
t7 = sheet("520905500107.xlsx"); r7 = rowdict(t7)
L7 = np.array([[float(r7[i][k] or 0) for k in jcols] for i in codes])
L7 = L7 / 100 if L7.max() > 50 else L7
OUT["national_typeI_accom_own_inverse"] = float(L_nat[:, ix["4401"]].sum())
OUT["national_typeI_accom_ABS_Table7"] = float(L7[:, ix["4401"]].sum())
OUT["national_L_vs_Table7_max_abs_diff"] = float(np.abs(L_nat - L7).max())
OUT["multipliers_delta0.3"] = mult

# ---- (2) five rows, own row model ----
def tra(name):
    f = [p for p in TRA.glob("*.xlsx") if re.sub(r" \((A|C)\)", "", p.stem) == name][0]
    rows = list(openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0].iter_rows(max_row=60, values_only=True))
    for k, r in enumerate(rows):
        if "Spend ($m)" in r:
            hdrk = [kk for kk in range(k, -1, -1) if "TOTAL" in rows[kk]][0]
            return float(r[rows[hdrk].index("TOTAL")])
an = pd.read_csv(ROOT / "Experiment 14/results/ANALYSIS_TABLE.csv")
ex = pd.read_csv(EXPO)
ilm = pd.read_csv(EXP / "results/IL_MODELLED.csv")
divout = pd.Series(x).groupby(div).sum(); divjobs = pd.Series(jobs).groupby(div).sum()
within = x / pd.Series(x).groupby(div).transform("sum").to_numpy()
jpm = jobs / x
SET = dict(unconstrained=dict(d=6, r="1km", b=0.66, delta=0.3, typ=2), constrained=dict(d=1, r="inside", b=0.66, delta=0.3, typ=2))
five = []
for idx in [114, 124, 116, 112, 5]:
    a = an.iloc[idx]; r = ex[(ex.agrn == a.agrn) & (ex.region_id == a.region_id) & (ex.season == a.season)].iloc[0]
    yr = 2016 if a.season <= 2020 else 2021
    if a.region_id not in C[yr].index: yr = 2021
    S = tra(a.region_name)
    rec = dict(row=int(idx), council=a.region_name, season=int(a.season), tra_spend_m=S)
    for nm, s in SET.items():
        L, e, lq, lam = L_of(a.region_id, yr, s["delta"], s["typ"])
        bi = sum(np.where(div == d, within * e[d] * divout[d] / divjobs[d], 0) for d in CEN)
        base_out = bi.sum()
        ex_sh = {"inside": r.residents_in, "1km": r.residents_1km, "council": r.residents_council}[s["r"]] / r.residents_council
        wsh = r.workplace_mb_in / r.workplace_mb_council
        flow = S * ex_sh * tour + wsh * bi
        dx = L @ (flow * min(s["d"], 24) / 12) - L @ (a.homes_v2 * 0.3443 * s["b"] * cons) * (18 / 30)
        dx12 = L @ (flow * min(s["d"], 12) / 12) - L @ (a.homes_v2 * 0.3443 * s["b"] * cons) * (6 / 30)
        rec[f"{nm}_loss_m_audit"] = float(dx.sum())
        rec[f"{nm}_il_share_audit"] = float(dx.sum() / (2 * base_out))
        rec[f"{nm}_y_unemp_audit"] = float((dx12 * jpm).sum() / e.sum() * 100)
        o = ilm.iloc[idx]
        rec[f"{nm}_loss_m_original"] = float(o[f"{nm}_loss_m"]); rec[f"{nm}_il_share_original"] = float(o[f"{nm}_il_share"])
        rec[f"{nm}_y_unemp_original"] = float(o[f"{nm}_y_unemp"])
    five.append(rec)
OUT["five_rows"] = five

# ---- (4) RF leave-one-season-out, own loop ----
T = pd.read_csv(EXP / "pipeline/results/ANALYSIS_TABLE_exp14_copy.csv")
T = T.merge(ilm[["agrn", "region_id", "season", "IL_model"]], on=["agrn", "region_id", "season"], how="left", validate="1:1")
H = T[["DL", "IL", "FP", "SL"]].copy(); H["IL"] = T.IL_model
T["Y_hybrid_audit"] = H.mean(axis=1, skipna=True)   # equal weights, re-normalised over present pillars
Y4 = T[["DL", "IL", "FP", "SL"]].mean(axis=1, skipna=True)
OUT["Y_v4_equals_mean_of_present_pillars_max_diff"] = float((Y4 - T.Y_v4).abs().max())
ht = pd.read_csv(EXP / "results/HYBRID_TABLE.csv")
OUT["Y_hybrid_audit_vs_original_max_diff"] = float((T.Y_hybrid_audit.to_numpy() - ht.Y_hybrid.to_numpy()).__abs__().max())
X = ["H", "E2", "V", "F", "X23", "log_share", "peak_ffdi", "severity_high_extreme", "log_homes_in_fire_per_1000", "log_homes_within_1km_per_1000"]
rf_out = {}
for tgt in ["Y_v4", "Y_hybrid_audit"]:
    d = T.dropna(subset=[tgt]).reset_index(drop=True); p = np.full(len(d), np.nan)
    for s in sorted(d.season.unique()):
        tr, te = d.season != s, d.season == s
        m = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(500, max_features=0.3333, min_samples_leaf=5, random_state=20261002, n_jobs=-1))
        p[te.to_numpy()] = m.fit(d.loc[tr, X], d.loc[tr, tgt]).predict(d.loc[te, X])
    rf_out[tgt] = dict(n=len(d), seasons=int(d.season.nunique()), rho=float(spearmanr(p, d[tgt])[0]),
                       rho_trainmean_baseline_note="mean baseline has rho undefined/constant within fold")
OUT["rf_loso_PRE+FIRE"] = rf_out

# ---- (5) leakage guard pieces ----
OUT["spearman_ILmodel_vs_DL_audit"] = float(spearmanr(T.IL_model, T.DL, nan_policy="omit")[0])
OUT["overlap_X_present_in_X"] = [c for c in ["log_share", "log_homes_in_fire_per_1000", "log_homes_within_1km_per_1000"] if c in X]

# ---- compare multipliers with original code (read-only import) ----
sys.path.insert(0, str(EXP / "src")); import io_model as m
io = m.load_io()
OUT["orig_vs_audit_A_max_diff"] = float(np.abs(io["A"] - A6).max())
OUT["orig_vs_audit_h_max_diff"] = float(np.abs(io["h"] - hvec).max())
OUT["orig_vs_audit_w_max_diff"] = float(np.abs(io["w"] - w).max())
json.dump(OUT, open(EXP / "audit/audit_numbers.json", "w"), indent=1, default=float)
print(json.dumps(OUT, indent=1, default=float))
