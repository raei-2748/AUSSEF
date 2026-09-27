"""Short codes for the master sheet: Y1, Y2 … (impact measures) and X1, X2 … (predictors).

- One sequence each, grouped: Y pillar by pillar (DL, IL, FP, SL), X category by category (fire, terrain, people &
  economy, council), topic by topic inside. Bowen's template variables (X1-X23, DL/IL/FP/SL raw) were examples: they
  are numbered like the rest, first in their topic, and marked in the codebook column bowen_template.
- Codes are frozen in codes/master_codes.csv: a variable keeps its code across rebuilds; a new variable gets the next
  free number (so it may sit out of numeric order inside its category); a variable that disappears keeps its code
  reserved. Y targets and the Y hierarchy (Y, Y_class, pillar scores, ranks), IDs and info columns are not coded.
"""
import re

import pandas as pd

from src.common import ROOT

CODE_FILE = ROOT / "codes/master_codes.csv"

# Bowen's example variable -> its column in the master sheet (event × council level); for the bowen_template column
BOWEN_X = {
    "X1": ("X1_burn_area", "X_fire_burn_area_in_council_ha", "burned area inside this council"),
    "X2": ("X2_FFDI", "X_fire_max_ffdi", "highest FFDI of the event's fires in this council"),
    "X3": ("X3_SPEI", "X_fire_min_spei3", "lowest SPEI-3 at ignition of these fires"),
    "X4": ("X4_fire_duration", "X_fire_max_fire_duration_days", "longest duration of these fires"),
    "X5": ("X5_hotspot_density", "X_fire_hotspot_density_max", "highest hotspot density of these fires"),
    "X6": ("X6_severity", "X_fire_severity_high_extreme_share", "area-weighted high/extreme severity share"),
    "X7": ("X7_temp_max", "X_fire_max_temp_c", "highest temperature during these fires"),
    "X8": ("X8_humidity_min", "X_fire_min_rh_pct", "lowest humidity during these fires"),
    "X9": ("X9_wind_max", "X_fire_max_wind_kmh", "highest wind during these fires"),
    "X10": ("X10_elevation", "X_env_elevation_wmean", "burned-area-weighted mean elevation"),
    "X11": ("X11_slope", "X_env_mean_slope_deg", "burned-area-weighted mean slope"),
    "X12": ("X12_vegetation", "X_env_dominant_vegetation", "vegetation group of the largest fire"),
    "X13": ("X13_canopy_cover", "X_env_mean_canopy_pct", "canopy cover of the largest fire"),
    "X14": ("X14_road_exposure", "X_env_road_km_burned", "road km inside these fires"),
    "X15": ("X15_pop_density", "X_socio_pop_density", ""),
    "X16": ("X16_regional_GDP", "X_socio_grp_sa4_proxy_aud_m", "proxy: SA4 GRP × population share (no council GRP "
                                                           "is public)"),
    "X17": ("X17_SEIFA", "X_socio_SEIFA", ""),
    "X18": ("X18_remoteness", "X_socio_remoteness", ""),
    "X19": ("X19_cash_reserve", "X_council_cash_reserve", ""),
    "X20": ("X20_own_source_revenue_ratio", "X_council_own_source_revenue_ratio", ""),
    "X21": ("X21_debt_burden", "X_council_debt_burden", ""),
    "X22": ("X22_historical_disaster_count", "X_council_historical_disaster_count", ""),
    "X23": ("X23_insurance_coverage", "X_council_insurance_proxy_share", "proxy: share of dwellings mortgaged or flats (no "
                                                                   "insured share is public)"),
}
BOWEN_Y = {"DL_insurance_loss_raw": "DL_insurance_loss_raw", "DL_homes_destroyed_in_council": "DL_house_loss_raw",
           "IL_job_loss_raw": "IL_job_loss_raw", "FP_budget_crowd_out_raw": "FP_budget_crowd_out_raw",
           "SL_income_drop_raw": "SL_income_drop_raw", "SL_vulnerable_loss_raw": "SL_vulnerable_loss_raw"}

# (group, [(topic, regex on the column name)]); display order = list order; the first regex that matches wins
TOPICS = {
    "DL": [("Insured losses", r"insurance|ica_"), ("Homes lost", r"homes_|house_"),
           ("Other buildings lost", r"facilities|outbuildings|properties"), ("Farm losses", r"fencing|livestock")],
    "IL": [("Regional output", r"grp|GRP|nsw_sfd"), ("Income", r"income|pia_"), ("Jobs", r"jobs_|payroll"),
           ("Unemployment", r"job_loss|unemp|labour_force|unemployed"),
           ("Business entries & exits", r"biz_entries|biz_exits"), ("Insolvencies", r"insolv"),
           ("Business counts", r"biz|arts_rec"), ("Night-time lights", r"ntl_"),
           ("Infrastructure outages", r"power")],
    "FP": [("Revenue", r"revenue|own_source"),
           ("Recovery grants & transfers", r"reported_|capital_grants|grants_"),
           ("Operating result", r"operating|net_op"), ("Spending mix", r"exp_|share|crowd_out|total_expenses"),
           ("Liquidity", r"cash_cover|unrestricted"), ("Debt", r"debt"),
           ("Assets & maintenance", r"maint|renewals|backlog|road_km"), ("Council size", r"council_population")],
    "SL": [("Deaths & injuries", r"deaths|injuries"), ("Income support", r"vulnerable|income_support|jobseeker"),
           ("Household income", r"income"), ("Housing & rent", r"rent"), ("Population", r"population")],
    "fire": [("Size & extent", r"burn_area|share_of_council|largest_fire|fires_n|area_burned"),
             ("Duration", r"duration"), ("Fire danger", r"ffdi|danger"), ("Drought", r"spei|kbdi|drought"),
             ("Weather", r"temp|rh_pct|humid|wind|rain"), ("Hotspots", r"hotspot"), ("Severity", r"sever"),
             ("Cause", r"cause|ignition")],
    "env": [("Terrain", r"elev|slope"), ("Vegetation", r"veg|canopy"), ("Roads", r"road")],
    "socio": [("People exposed", r"pop_in_fire|pop_within|dwellings_in_fire|dwellings_within"),
              ("Population", r"population|pop_density|X15"), ("Disadvantage", r"seifa|SEIFA"),
              ("Remoteness", r"remoteness"), ("Economic size", r"grp|X16|nsw_sfd|total_income|income_proxy"),
              ("Income", r"median_income|income_earners|pia_"), ("Labour market", r"unemp|labour_force|unemployed"),
              ("Jobs", r"jobs_|payroll"), ("Industry mix", r"ind_share|employed_persons|accom_food_biz_share"),
              ("Business counts", r"biz_(?!entries|exits)|^X_socio_biz"),
              ("Business entries & exits", r"biz_entries|biz_exits"), ("Insolvencies", r"insolv"),
              ("Tourism", r"tra_"), ("Night-time lights", r"ntl_"),
              ("Income support", r"income_support|jobseeker"), ("Housing & rent", r"rent|dw_|dwellings"),
              ("Council area", r"area_km2")],
    "council": [("Disaster history", r"X22|historical"), ("Insurance (proxy)", r"insurance|X23"),
                ("Revenue & grants", r"revenue|own_source|X20|grants"), ("Operating result", r"operating|net_op"),
                ("Spending mix", r"exp_|share_pct|total_expenses"), ("Liquidity", r"cash|unrestricted|X19"),
                ("Debt", r"debt|X21"), ("Assets & maintenance", r"maint|renewals|backlog|road_km|asset"),
                ("Council size", r"council_population")],
}
X_CATEGORIES = ["fire", "env", "socio", "council"]
Y_PILLARS = ["DL", "IL", "FP", "SL"]


def topic(name, group):
    for t, pat in TOPICS.get(group, []):
        if re.search(pat, name):
            return t
    return "Other"


def topic_rank(t, group):
    names = [x for x, _ in TOPICS.get(group, [])]
    return names.index(t) if t in names else len(names)


def assign(table, is_hierarchy):
    """table: master rows of the variables table (column, original_column, group, role).
    Returns it with `code`, `topic`, `bowen_template` and a `sort` key, codes frozen in CODE_FILE."""
    t = table.copy()
    t["topic"] = [topic(c, g) if r in ("X", "Y") else "" for c, g, r in zip(t.column, t.group, t.role)]
    bowen_x = {col: code for code, (_, col, _) in BOWEN_X.items()}
    t["bowen_template"] = [BOWEN_X[bowen_x[c]][0] + (f" ({BOWEN_X[bowen_x[c]][2]})" if BOWEN_X[bowen_x[c]][2] else "")
                           if c in bowen_x else BOWEN_Y.get(c, "") for c in t.column]
    codable = [(r in ("X", "Y")) and not is_hierarchy(c) for c, r in zip(t.column, t.role)]
    old = pd.read_csv(CODE_FILE) if CODE_FILE.exists() else pd.DataFrame(columns=["code", "key", "name"])
    known = dict(zip(old.key, old.code))
    used = set(old.code)

    def order_key(i):
        c, g, r = t.column[i], t.group[i], t.role[i]
        # pillar / category, then topic; Bowen's template variable heads its topic
        if r == "Y":
            return (0, Y_PILLARS.index(g), topic_rank(t.topic[i], g), 0 if c in BOWEN_Y else 1, i)
        return (1, X_CATEGORIES.index(g), topic_rank(t.topic[i], g), 0 if c in bowen_x else 1, i)

    rows = sorted([i for i in t.index if codable[i]], key=order_key)
    nxt = {"X": max([int(c[1:]) for c in used if c.startswith("X")] + [0]) + 1,
           "Y": max([int(c[1:]) for c in used if c.startswith("Y")] + [0]) + 1}
    codes = {}
    for i in rows:
        key = t.original_column[i]
        if key in known:
            codes[i] = known[key]
        else:
            p = t.role[i][0]
            codes[i] = f"{p}{nxt[p]}"
            nxt[p] += 1
    t["code"] = [codes.get(i, "") for i in t.index]
    t["sort"] = [order_key(i) if codable[i] else None for i in t.index]
    assert not t.code[t.code != ""].duplicated().any(), "duplicate codes"
    new = pd.DataFrame({"code": t.code, "key": t.original_column, "name": t.column})[t.code != ""]
    keep = old[~old.key.isin(new.key)]  # codes of variables no longer in the master stay reserved
    CODE_FILE.parent.mkdir(exist_ok=True)
    pd.concat([new, keep]).to_csv(CODE_FILE, index=False)
    return t
