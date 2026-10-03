"""Builds extraction_raw.csv for Snowy Valleys (17080) from hand-verified values (PDFs are scanned images;
values read visually from page renders, OCR used only to locate rows). Values below are as printed ($000 unless noted)."""
import csv, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extraction_raw.csv")
RID, CN = 17080, "Snowy Valleys Council"
D = "fire_event_dataset/data/raw/council_pdfs/qbrs/17080/"
rows = []
def num(s):
    s = str(s).strip().replace(",", "").replace("$", "")
    if s in ("-", "–"): return 0
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    v = float(s)
    return -v if neg else v
def add(ctx, item, val, page, label, table, notes="", units=None, printed=None):
    u = units or ctx["units"]
    v = num(val)
    if u == "$000": v = v * 1000
    v = int(round(v))
    pp = printed if printed is not None else (ctx["pp"](page) if ctx.get("pp") else "")
    n = notes
    if str(val).strip() in ("-", "–"): n = (n + "; " if n else "") + "printed as '-' (nil)"
    rows.append([RID, CN, ctx["fy"], ctx["q"], item, v, u, page, pp, label, table, D + ctx["file"], n])
MAIN = dict(orig="original_budget", rev="revised_budget_prior", var="variation_this_quarter", proj="projected_year_end", ytd="ytd_actual")
DIS = dict(orig="original", rev="revised_prior", var="variation", proj="projected", ytd="ytd_actual")
KEYS = ["orig", "rev", "var", "proj", "ytd"]
def series(ctx, kind, vals, page, label, table, notes="", hdr=None):
    """kind: capex/opex/opinc or disaster:<category>; vals: 5-tuple (orig, rev_prior, var, proj, ytd); None = blank cell, skipped."""
    h = hdr or ctx["hdr"]
    for k, v in zip(KEYS, vals):
        if v is None: continue
        item = (kind + ":" + DIS[k]) if kind.startswith("disaster") else (kind + "_" + MAIN[k])
        add(ctx, item, v, page, label, table + " | " + h[k], notes)

# ---------------- FY2018-19 Q1 (scanned; printed page = PDF page + 157)
c = dict(fy="2018-19", q="Q1", file="17080_FY2018-19_Q1_QBRS_Sep2018_att1.pdf", units="$000", pp=lambda p: p + 157,
         hdr=dict(orig="Original Budget 2018/19", rev="Revised Budget 2018/19", var="Variations for this Sep Qtr", proj="Projected Year End Result", ytd="Actual YTD figures"))
IE = "Income & Expenses Budget Review Statement - Council Consolidated"
CAP = "Capital Budget Review Statement - Council Consolidated"
CON = "consolidated total (Council Consolidated); Approved Changes columns (Carry Forwards / Other than by QBRS) shown nil"
series(c, "opinc", ("46,463", "46,463", "(1,000)", "45,463", "20,635"), 4, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("42,777", "42,777", "44", "42,821", "12,748"), 4, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "3,686", 4, "Net Operating Result from Continuing Operations", IE + " | Original Budget 2018/19", "after capital grants & contributions")
add(c, "opres_projected_year_end", "2,642", 4, "Net Operating Result from Continuing Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(3,679)", 4, "Net Operating Result before Capital Items", IE + " | Original Budget 2018/19", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(3,723)", 4, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("20,675", "22,157", "(427)", "21,730", "1,323"), 8, "Total Capital Expenditure", CAP,
       "consolidated; total includes Loan Repayments (Principal) 647; revised budget 22,157 includes carry forwards 1,482")
FS = "function line 'Fire Service Levy, Protection, Emergency' (routine fire/emergency services function: RFS levy/contributions), not disaster-specific"
series(c, "disaster:other", ("235", "235", None, "235", "-"), 5, "Fire Service Levy, Protection, Emergency", IE + " (by function) - Income", "income; " + FS)
series(c, "disaster:operating_expense", ("755", "755", None, "755", "487"), 5, "Fire Service Levy, Protection, Emergency", IE + " (by function) - Expenses", "expense; " + FS)
series(c, "disaster:other", ("160", "160", None, "160", "160"), 10, "Visy Emergency Works", "Cash & Investments Budget Review Statement - Internally Restricted",
       "internally restricted cash reserve balance (not income/expense); label names emergency works")

# ---------------- FY2018-19 Q2 (scanned; printed page = PDF page + 100)
c = dict(fy="2018-19", q="Q2", file="17080_FY2018-19_Q2_QBRS_Dec2018_att1.pdf", units="$000", pp=lambda p: p + 100,
         hdr=dict(orig="Original Budget 2018/19", rev="Revised Budget 2018/19", var="Variations for this Dec Qtr", proj="Projected Year End Result", ytd="Actual YTD figures"))
CON = "consolidated total (Council Consolidated); revised budget = after Sep QBRS (approved changes)"
series(c, "opinc", ("46,463", "45,463", "5,770", "51,233", "31,357"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("42,777", "42,821", "1,575", "44,396", "22,987"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "3,686", 3, "Net Operating Result from Continuing Operations", IE + " | Original Budget 2018/19", "after capital grants & contributions")
add(c, "opres_projected_year_end", "6,837", 3, "Net Operating Result from Continuing Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(3,679)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2018/19", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(2,403)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("20,675", "22,525", "1,013", "23,538", "6,302"), 7, "(unlabelled total row under Capital Expenditure)", CAP,
       "consolidated; total row printed without a label (Total Capital Expenditure position); includes Loan Repayments (Principal) 647; revised 22,525 includes carry forwards 1,482, other than by QBRS 795, Sep QBRS (427)")
series(c, "disaster:other", ("235", "235", None, "235", "671"), 4, "Fire Service Levy, Protection, Emergency", IE + " (by function) - Income", "income; " + FS)
series(c, "disaster:operating_expense", ("755", "755", None, "755", "1,025"), 4, "Fire Service Levy, Protection, Emergency", IE + " (by function) - Expenses", "expense; " + FS)
series(c, "disaster:other", ("160", "160", None, "160", "160"), 9, "Visy Emergency Works", "Cash & Investments Budget Review Statement - Internally Restricted",
       "internally restricted cash reserve balance (not income/expense); label names emergency works")

# ---------------- FY2018-19 Q3 (scanned; printed page = PDF page + 98)
c = dict(fy="2018-19", q="Q3", file="17080_FY2018-19_Q3_QBRS_Mar2019_att1.pdf", units="$000", pp=lambda p: p + 98,
         hdr=dict(orig="Original Budget 2018/19", rev="Revised Budget 2018/19", var="Variations for this Mar Qtr", proj="Projected Year End Result", ytd="Actual YTD figures"))
CON = "consolidated total (Council Consolidated); revised budget = after Sep and Dec QBRS"
series(c, "opinc", ("46,463", "51,233", "(2,400)", "48,833", "39,863"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("42,777", "44,396", "(52)", "44,344", "31,238"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "3,686", 3, "Net Operating Result from Continuing Operations", IE + " | Original Budget 2018/19", "after capital grants & contributions")
add(c, "opres_projected_year_end", "4,489", 3, "Net Operating Result from Continuing Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(3,679)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2018/19", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(2,351)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("20,675", "23,538", "(2,541)", "20,997", "11,246"), 6, "(unlabelled total row under Capital Expenditure)", CAP,
       "consolidated; total row printed without a label; includes Loan Repayments (Principal) 647 (YTD 976)")
series(c, "disaster:other", ("235", "235", None, "235", "880"), 4, "Fire Service Levy, Protection, Emergency", IE + " (by function) - Income", "income; " + FS)
series(c, "disaster:operating_expense", ("755", "755", None, "755", "1,375"), 4, "Fire Service Levy, Protection, Emergency", IE + " (by function) - Expenses", "expense; " + FS)
series(c, "disaster:other", ("160", "160", None, "160", "160"), 8, "Visy Emergency Works", "Cash & Investments Budget Review Statement - Internally Restricted",
       "internally restricted cash reserve balance (not income/expense); label names emergency works")

# ---------------- FY2019-20 Q1 att1a UPDATED (text layer; no agenda page stamps)
H1920 = dict(orig="Original Budget 2019/20", rev="Revised Budget 2019/20", var="Variations for this Sep Qtr", proj="Projected Year End Result", ytd="Actual YTD figures")
for fname, pp, tag in (("17080_FY2019-20_Q1_QBRS_Sep2019_att1a_updated.pdf", None, "updated version att1a (preferred)"),
                       ("17080_FY2019-20_Q1_QBRS_Sep2019_att1.pdf", (lambda p: p + 157), "SUPERSEDED original att1 (scanned); summary values identical to att1a; use att1a")):
    c = dict(fy="2019-20", q="Q1", file=fname, units="$000", pp=pp, hdr=H1920)
    CON = "consolidated total (Council Consolidated); I&E table has no revised-budget column this quarter (Original -> Variations -> Projected); " + tag
    series(c, "opinc", ("44,312", None, "3,232", "47,544", "22,739"), 4, "Total Income from Continuing Operations", IE, CON)
    series(c, "opex", ("40,710", None, "6,096", "46,806", "12,995"), 4, "Total Expenses from Continuing Operations", IE, CON)
    add(c, "opres_original_budget", "3,602", 4, "Net Operating Result from All Operations", IE + " | Original Budget 2019/20", "after capital grants & contributions; summary table shows 'from All Operations' (same value as 'from Continuing Operations' on p6); " + tag)
    add(c, "opres_projected_year_end", "738", 4, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions; " + tag)
    add(c, "opres_before_capital_original_budget", "(1,775)", 4, "Net Operating Result before Capital Items", IE + " | Original Budget 2019/20", "before capital grants & contributions; " + tag)
    add(c, "opres_before_capital_projected_year_end", "(4,639)", 4, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions; " + tag)
    series(c, "capex", ("24,223", "27,421", "832", "28,253", "2,914"), 8, "Total Capital Expenditure", CAP,
           "consolidated; no loan repayment line this year; revised 27,421 = original + carry forwards 3,198; " + tag)
    if pp is None:
        FE = "function line 'Fire and Emergency Services' (routine fire/emergency services function), not disaster-specific; " + tag
        series(c, "disaster:other", ("246", None, None, "246", "(340)"), 5, "Fire and Emergency Services", IE + " (by function) - Income", "income; " + FE)
        series(c, "disaster:operating_expense", ("768", None, None, "768", "225"), 6, "Fire and Emergency Services", IE + " (by function) - Expenses", "expense; " + FE)

# ---------------- FY2019-20 Q2 (scanned; printed page = PDF page + 175)
c = dict(fy="2019-20", q="Q2", file="17080_FY2019-20_Q2_QBRS_Dec2019_att1.pdf", units="$000", pp=lambda p: p + 175,
         hdr=dict(H1920, var="Variations for this Dec Qtr"))
CON = "consolidated total (Council Consolidated); revised budget = after Sep QBRS"
series(c, "opinc", ("44,312", "47,544", "1,819", "49,363", "27,937"), 4, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("40,710", "46,806", "1,137", "47,943", "26,338"), 4, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "3,602", 4, "Net Operating Result from All Operations", IE + " | Original Budget 2019/20", "after capital grants & contributions")
add(c, "opres_projected_year_end", "1,420", 4, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(1,775)", 4, "Net Operating Result before Capital Items", IE + " | Original Budget 2019/20", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(3,957)", 4, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("24,223", "28,478", "364", "28,842", "8,682"), 7, "Total Capital Expenditure", CAP,
       "consolidated; revised 28,478 = original + carry forwards 3,198 + other than by QBRS 225 + Sep QBRS 832")
FE = "function line 'Fire and Emergency Services'; Dec Qtr variation 1,000 = note 1 ($1m immediate base payment for severely fire impacted councils)"
series(c, "disaster:other", ("246", "246", "1,000", "1,246", "110"), 5, "Fire and Emergency Services", IE + " (by function) - Income", "income; " + FE)
series(c, "disaster:operating_expense", ("768", "768", "1,000", "1,768", "528"), 5, "Fire and Emergency Services", IE + " (by function) - Expenses", "expense; " + FE)
add(c, "disaster:grant_income:narrative", "1,000,000.00", 6, "Immediate base payment for severely fire impacted councils to help rebuild vital infrastructure and streghten community resilience. Expenditure has been increased inline with the grant received.",
    "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note 1", "narrative note 1; $ as printed; corresponds to Grants & Contributions - Operating and Other Expenses Dec Qtr variations (Bushfire Recovery base payment, Black Summer)", units="$")
c2 = dict(fy="2019-20", q="Q2", file="17080_FY2019-20_Q2_BusinessPaper_Feb2020.pdf", units="$", pp=lambda p: p - 3, hdr=c["hdr"])
add(c2, "disaster:other:narrative", "1,135,000", 58, "it is estimated that the contamination of the site with friable asbestos will increase the contracted price by an additional $1.135m",
    "Business paper item 9.6 Quarterly Budget Review as at 31 December 2019 - Recovery (narrative)",
    "cover report narrative: Batlow Cannery impacted by Dunns Road fire, demolition contract variation estimate; printed as $1.135m; unfunded disaster-related cost (may be funded from council's own budget)")

# ---------------- FY2019-20 Q3 (scanned; printed page = PDF page + 127)
c = dict(fy="2019-20", q="Q3", file="17080_FY2019-20_Q3_QBRS_Mar2020_att1.pdf", units="$000", pp=lambda p: p + 127,
         hdr=dict(H1920, var="Variations for this Mar Qtr"))
CON = "consolidated total (Council Consolidated); revised budget = after Sep and Dec QBRS"
series(c, "opinc", ("44,312", "49,363", "2,010", "51,373", "38,488"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("40,710", "47,943", "3,108", "51,051", "38,713"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "3,602", 3, "Net Operating Result from All Operations", IE + " | Original Budget 2019/20", "after capital grants & contributions")
add(c, "opres_projected_year_end", "322", 3, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(1,775)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2019/20", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(5,055)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("24,223", "28,842", "182", "29,024", "11,820"), 6, "Total Capital Expenditure", CAP,
       "consolidated; Mar Qtr variation includes 486 Land & Buildings for emergency accommodation at Batlow (note 4)")
FE = "function line 'Fire and Emergency Services'; Mar Qtr variation 2,275 = notes 1,3 ($275k Fire Recovery Grant + $2m S.44 claim Dunns Road Bushfire)"
series(c, "disaster:other", ("246", "1,246", "2,275", "3,521", "1,353"), 4, "Fire and Emergency Services", IE + " (by function) - Income", "income; " + FE)
series(c, "disaster:operating_expense", ("768", "1,768", "2,275", "4,043", "3,595"), 4, "Fire and Emergency Services", IE + " (by function) - Expenses", "expense; " + FE)
NT = "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note "
add(c, "disaster:grant_income:narrative", "275,000.00", 5, "Fire Recovery Grant received, offset by an increase in expenditure", NT + "1", "narrative; $ as printed", units="$")
add(c, "disaster:grant_income:narrative", "2,000,000.00", 5, "Recognise estimated S.44 claim for the Dunns Road Bushfire Disaster. This is a claim based on actual expenditure incurred during the event.", NT + "3",
    "narrative; S.44 (Rural Fires Act) cost-recovery claim, booked in Other Revenues (+2,000); categorised grant_income as disaster reimbursement income", units="$")
add(c, "disaster:operating_expense:narrative", "700,000", 5, "Employee Costs have been increased by $700k", NT + "3", "narrative; part of S.44 Dunns Road Bushfire claim expenditure; printed '$700k'", units="$")
add(c, "disaster:operating_expense:narrative", "1,300,000", 5, "Materials and Contracts by $1.3m", NT + "3", "narrative; part of S.44 Dunns Road Bushfire claim expenditure; printed '$1.3m'", units="$")
add(c, "disaster:operating_expense:narrative", "800,000.00", 5, "Increased demolition costs resulting from the damage to the Batlow Cannery during the Dunns Road Bushfire Disaster", NT + "5", "narrative; in Materials & Contracts variation (notes 4,5); unfunded", units="$")
add(c, "disaster:capital_expense:narrative", "486,000", 7, "Purchase and installation of emergency accomodation at Batlow. Currently there is no funding however it is being actively pursued",
    "Capital Budget Review Statement - Recommended changes to revised budget | Note 4", "narrative; post-bushfire emergency accommodation (Land & Buildings new assets +486); label does not literally say fire", units="$")
c2 = dict(fy="2019-20", q="Q3", file="17080_FY2019-20_Q3_BusinessPaper_May2020.pdf", units="$", pp=lambda p: p - 3, hdr=c["hdr"])
BP = "Business paper item 10.8 Quarterly Budget Review as at 31 March 2020 (cover report narrative)"
add(c2, "disaster:grant_income:narrative", "1,275,000", 62, "$1.275M was received on behalf of the Department of the Prime Minister and Cabinet for Bushfire Recovery", BP + " - Income",
    "printed '$1.275M'; may overlap the $1m base payment (Dec Qtr) + $275k Fire Recovery Grant (Mar Qtr note 1)")
add(c2, "disaster:other:narrative", "437,000", 63, "water usage income was reduced by $437K for the Council approved fire fighting discount", BP + " - Water Fund",
    "printed '$437K'; revenue foregone (fire fighting water discount); no budget adjustment made")
add(c2, "disaster:capital_expense:narrative", "476,000", 64, "the purchase of emergency accommodation for the Batlow Caravan Park ($476K)", BP + " - Unrestricted Cash",
    "printed '$476K' here but '$486K' earlier on same page and in QBRS capital note 4 (inconsistency in source; QBRS 486,000 recorded separately)")

# ---------------- FY2020-21 Q1 (scanned; printed page = PDF page + 326)
H2021 = dict(orig="Original Budget 2020/21", rev="Revised Budget 2020/21", var="Variations for this Sep Qtr", proj="Projected Year End Result", ytd="Actual YTD figures")
c = dict(fy="2020-21", q="Q1", file="17080_FY2020-21_Q1_QBRS_Sep2020_att1.pdf", units="$000", pp=lambda p: p + 326, hdr=H2021)
CON = "consolidated total (Council Consolidated, summary by nature, excludes internal transactions); no revised-budget column in I&E this quarter"
series(c, "opinc", ("46,767", None, "3,615", "50,382", "25,101"), 3, "Total Income from Continuing Operations", IE, CON + "")
series(c, "opex", ("42,708", None, "1,003", "43,711", "14,034"), 3, "Total Expenses from Continuing Operations", IE, CON + "")
add(c, "opres_original_budget", "4,059", 3, "Net Operating Result from All Operations", IE + " | Original Budget 2020/21", "after capital grants & contributions")
add(c, "opres_projected_year_end", "6,671", 3, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(3,251)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2020/21", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(639)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("23,161", "30,008", "35", "30,043", "1,304"), 7, "Total Capital Expenditure", CAP, "consolidated; revised 30,008 = original + carry forwards 6,847 (approved 20 Aug 2020)")
IEF = "Income & Expenses Budget Review Statement - Council Consolidated (by function, including internal transactions)"
series(c, "disaster:other", ("246", None, "3,420", "3,666", "1,147"), 4, "Fire and Emergency Services", IEF + " - Income",
       "income; function line includes internal transactions; Sep Qtr variation notes 8,9,10,11 (incl. $1.154m fire & emergency works recoverable, $854,488 Batlow Cannery removal funding, $1.3m Disaster Recovery funding)")
series(c, "disaster:operating_expense", ("800", None, "1,154", "1,954", "1,409"), 5, "Fire and Emergency Services", IEF + " - Expenses",
       "expense; function line includes internal transactions; Sep Qtr variation note 9 (Fire and Emergency Works offset by external funding)")
NT = "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note "
add(c, "disaster:other:narrative", "1,154,000", 6, "Fire and Emergency Works to be recovered from external funding Offset by expenditure from external funding", NT + "9",
    "narrative; amount appears as both income (recoverable) and expense in Fire and Emergency Services", units="$")
add(c, "disaster:grant_income:narrative", "854,488", 6, "Funding received for removal of Batlow Cannery", NT + "10",
    "narrative; Batlow Cannery was damaged in the Dunns Road bushfire (per FY2019-20 Q2/Q3 reports); booked to Fire and Emergency Services income", units="$")
add(c, "disaster:grant_income:narrative", "1,300,000", 6, "Disaster Recovery funding for prior years work", NT + "11", "narrative; booked to Fire and Emergency Services income", units="$")

# ---------------- FY2020-21 Q2 (scanned; printed page = PDF page + 133)
c = dict(fy="2020-21", q="Q2", file="17080_FY2020-21_Q2_QBRS_Dec2020_att1.pdf", units="$000", pp=lambda p: p + 133, hdr=dict(H2021, var="Variations for this Dec Qtr"))
CON = "consolidated total (Council Consolidated, summary by nature); revised budget = after Sep QBRS"
series(c, "opinc", ("46,767", "50,382", "6,059", "56,441", "35,103"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("42,708", "43,711", "4,750", "48,461", "30,210"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "4,059", 3, "Net Operating Result from All Operations", IE + " | Original Budget 2020/21", "after capital grants & contributions")
add(c, "opres_projected_year_end", "7,980", 3, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(3,251)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2020/21", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(848)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("23,161", "30,043", "(2,920)", "27,123", "5,627"), 7, "Total Capital Expenditure", CAP, "consolidated; revised 30,043 = original + carry forwards 6,847 + Sep QBRS 35")
DR = "function line includes internal transactions; Dec Qtr variation 4,541 = note 7 Disaster Recovery Funding Arrangement (DRFA), expenditure offset by Other income"
series(c, "disaster:other", ("246", "3,666", "4,541", "8,207", "620"), 4, "Fire and Emergency Services", IEF + " - Income", "income; " + DR)
series(c, "disaster:operating_expense", ("800", "1,954", "4,541", "6,495", "5,767"), 5, "Fire and Emergency Services", IEF + " - Expenses", "expense; " + DR)
add(c, "disaster:grant_income:narrative", "4,541,000", 6, "Disaster Recovery Funding Arrangement (DRFA) Expenditure is offset by Other income",
    "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note 7 (Effect on Budget Positive/(Negative) = 0)", "narrative; DRFA income in Other Income (+4,541) with matching Materials & Contracts expenditure", units="$")
add(c, "disaster:capital_expense:narrative", "705,000", 8, "Increase to heavy patching program due to accelerated deterioration of the local roads network resulting from wet weather and increased truck movements in response to fire recovery - offset by reduction in Road and Kerb & Gutter renewal programs",
    "Capital Budget Review Statement - Recommended changes to revised budget | Note 17", "narrative; fire-recovery-related road damage; offset by reductions of 100,000 and 605,000 (net 0)", units="$")
add(c, "disaster:other:narrative", "780,164", 12, "MR85 Bush Fire Recovery Works", "Contracts Budget Review Statement - Part A Contracts Listing | Contract Value",
    "contract value (SAYCO), start 09/09/20, duration to February 2021, Budgeted N", units="$")

# ---------------- FY2020-21 Q3 (scanned; printed page = PDF page + 49)
c = dict(fy="2020-21", q="Q3", file="17080_FY2020-21_Q3_QBRS_Mar2021_att1.pdf", units="$000", pp=lambda p: p + 49, hdr=dict(H2021, var="Variations for this Mar Qtr"))
CON = "consolidated total (Council Consolidated, summary by nature); revised budget = after Sep and Dec QBRS"
series(c, "opinc", ("46,767", "56,441", "11,787", "68,228", "52,672"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("42,708", "48,461", "10,255", "58,716", "51,792"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "4,059", 3, "Net Operating Result from All Operations", IE + " | Original Budget 2020/21", "after capital grants & contributions")
add(c, "opres_projected_year_end", "9,512", 3, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(3,251)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2020/21", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(3,283)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("23,161", "27,123", "3,234", "30,357", "10,839"), 9, "Total Capital Expenditure", CAP, "consolidated; revised 27,123 = original + carry forwards 6,847 + Sep QBRS 35 + Dec QBRS (2,920)")
series(c, "disaster:other", ("246", "8,207", "925", "9,132", "5,903"), 4, "Fire and Emergency Services", IEF + " - Income",
       "income; function line includes internal transactions; Mar Qtr variation notes 35,44 (ESL offset funding 208,121; Fire & Emergency grants incl. bushfire road corridor clean-up 717,461)")
series(c, "disaster:operating_expense", ("800", "6,495", "3,847", "10,342", "8,932"), 5, "Fire and Emergency Services", IEF + " - Expenses",
       "expense; function line includes internal transactions; Mar Qtr variation note 44 (bushfire road corridor clean-up project expenditure)")
NT = "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note "
add(c, "disaster:grant_income:narrative", "90,000", 6, "Bushfire RVM Grant income and Expenditure", NT + "8 (Effect on Budget 0)", "narrative; income with offsetting expenditure", units="$")
add(c, "disaster:grant_income:narrative", "336,000", 6, "Bushfire Industry Recovery Package Income - Wondalga Road", NT + "9", "narrative", units="$")
add(c, "disaster:grant_income:narrative", "152,984", 6, "BLER Funding - Aerodrome Upgrade", NT + "19",
    "narrative; BLER = Bushfire Local Economic Recovery fund; same amount repeated in capital note 115 (not recorded twice)", units="$")
add(c, "disaster:other:narrative", "344,000", 7, "Insurance claim received - Bushfire 2019/2020 Progress Payment", NT + "31", "narrative; insurance recovery income (not a grant)", units="$")
add(c, "disaster:other:narrative", "208,121", 7, "Additional State funding received to offset increase in Emergency Service Levy", NT + "35",
    "narrative; Emergency Services Levy (funds RFS/fire services) - routine levy, not disaster recovery; label does not name fire/disaster explicitly", units="$")
add(c, "disaster:grant_income:narrative", "717,461", 7, "Fire & Emergency grants, Connecting Communities $54K, Brungle Rd Culvert $35K Additional Bushfire funding road corridor clean-up Project $682K", NT + "44",
    "narrative; total Fire & Emergency grants income", units="$")
add(c, "disaster:grant_income:narrative", "682,000", 7, "Additional Bushfire funding road corridor clean-up Project $682K", NT + "44",
    "narrative; component of the 717,461 above; printed '$682K'", units="$")
add(c, "disaster:operating_expense:narrative", "3,847,401", 7, "Additional Bushfire funding road corridor clean-up Project Expenditure", NT + "44 (Effect on Budget (3,847,401))", "narrative", units="$")
add(c, "disaster:capital_expense:narrative", "100,000", 10, "BLER - Aerodrome Upgrade Expense Budget Entry for 20/21",
    "Capital Budget Review Statement - Recommended changes to revised budget | Note 82", "narrative; BLER = Bushfire Local Economic Recovery", units="$")

# ---------------- FY2021-22 Q1 (scanned; printed page = PDF page + 217)
H2122 = dict(orig="Original Budget 2021/22", rev="Revised Budget 2021/22", var="Variations for this Sep Qtr", proj="Projected Year End Result", ytd="Actual YTD figures")
c = dict(fy="2021-22", q="Q1", file="17080_FY2021-22_Q1_QBRS_Sep2021_att1.pdf", units="$000", pp=lambda p: p + 217, hdr=H2122)
CON = "consolidated total (Council Consolidated summary); NOTE totals include 'Internal Income' 7,476 / 'Internal Expense' 4,428 lines from FY2021-22 (not comparable with earlier years); no revised-budget column this quarter"
series(c, "opinc", ("74,119", None, "9,117", "83,236", "27,076"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("56,880", None, "2,482", "59,362", "17,750"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "17,239", 3, "Net Operating Result from All Operations", IE + " | Original Budget 2021/22", "after capital grants & contributions")
add(c, "opres_projected_year_end", "23,874", 3, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(1,814)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2021/22", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(3,221)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("35,411", None, "(296)", "36,979", "4,030"), 8, "Total Capital Expenditure", CAP,
       "consolidated; table has Original, Approved Changes Carry Forwards 1,864, Variations, Projected - no revised-budget column printed")
series(c, "disaster:other", ("450", None, "-", "450", "47"), 4, "Fire and Emergency Services", IEF + " - Income", "income; function line includes internal transactions; routine fire/emergency function")
series(c, "disaster:operating_expense", ("968", None, None, "968", "520"), 5, "Fire and Emergency Services", IEF + " - Expenses", "expense; function line includes internal transactions; routine fire/emergency function")
NT = "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note "
NC = "Capital Budget Review Statement - Recommended changes to revised budget | Note "
for n, nc, amt, lab in ((22, 34, "900,000", "BLERF Upgrade Tumut Pool Stage 2"), (23, 35, "660,000", "BLERF Upgrade Khancoban Pool"), (24, 36, "1,750,000", "BLERF Upgrade Batlow Pool")):
    add(c, "disaster:grant_income:narrative", amt, 7, lab + " Grant income offset by capital expenditure (NSW Bushfire Local Economic Recovery Fund)", NT + str(n), "narrative; BLERF grant income", units="$")
    add(c, "disaster:capital_expense:narrative", amt, 9, lab + " Grant income offset by capital expenditure (NSW Bushfire Local Economic Recovery Fund)", NC + str(nc), "narrative; matching BLERF-funded capital expenditure (Effect on Budget negative)", units="$")

# ---------------- FY2021-22 Q2 (scanned; printed page = PDF page + 57)
c = dict(fy="2021-22", q="Q2", file="17080_FY2021-22_Q2_QBRS_Dec2021_att1.pdf", units="$000", pp=lambda p: p + 57, hdr=dict(H2122, var="Variations for this Dec Qtr"))
CON = "consolidated total (Council Consolidated summary); totals include Internal Income 7,476 / Internal Expense 4,775 lines; revised budget = after Sep QBRS"
series(c, "opinc", ("74,119", "83,236", "5,996", "89,232", "50,457"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("56,880", "59,362", "4,665", "64,027", "39,289"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "17,239", 3, "Net Operating Result from All Operations", IE + " | Original Budget 2021/22", "after capital grants & contributions")
add(c, "opres_projected_year_end", "25,205", 3, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(1,814)", 3, "Net Operating Result before Capital Items", IE + " | Original Budget 2021/22", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(3,396)", 3, "Net Operating Result before Capital Items", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("35,411", None, "1,818", "38,797", "8,485"), 7, "Total Capital Expenditure", CAP,
       "consolidated; columns Original, Carry Forwards 1,864, Sep QBRS (296), Dec Qtr variation, Projected - no revised-budget column printed")
series(c, "disaster:other", ("450", "450", "-", "450", "48"), 4, "Fire and Emergency Services", IEF + " - Income", "income; function line includes internal transactions; routine fire/emergency function")
series(c, "disaster:operating_expense", ("968", "968", "-", "968", "970"), 5, "Fire and Emergency Services", IEF + " - Expenses", "expense; function line includes internal transactions; routine fire/emergency function")
NT = "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note "
add(c, "disaster:grant_income:narrative", "320,050", 6, "EPA Bushfire Recovery Program for Council Landfills Phase 2 Grant income offset by expenditure in Capital Budget", NT + "1", "narrative", units="$")
add(c, "disaster:grant_income:narrative", "999,600", 6, "Note: Total grant income will be $999,600 with $320,050 expected this financial year", NT + "1 (sub-note)", "narrative; multi-year total of EPA Bushfire Recovery Program Phase 2 grant", units="$")
add(c, "disaster:grant_income:narrative", "4,490,414", 6, "EPA Bushfire Greenwaste Cleanup Recognition of grant income, offset by operational expenditure", NT + "7 (Effect on Budget 0)",
    "narrative; grant income in Grants & Contributions - Operating (+4,490) with offsetting operating expenditure", units="$")
add(c, "disaster:capital_expense:narrative", "320,050", 8, "EPA Bushfire Recovery Program for Council Landfills Phase 2 Recognition of expenditure, offset by grant income",
    "Capital Budget Review Statement - Recommended changes to revised budget | Note 17", "narrative", units="$")

# ---------------- FY2021-22 Q3 (text layer; printed page numbers equal PDF page index)
c = dict(fy="2021-22", q="Q3", file="17080_FY2021-22_Q3_QBRS_Mar2022_att1.pdf", units="$000", pp=None, hdr=dict(H2122, var="Variations for this Mar Qtr"))
CON = "consolidated total (Council Consolidated summary); totals include Internal Income 7,476 / Internal Expense 4,775 lines; revised budget = after Sep and Dec QBRS"
series(c, "opinc", ("74,119", "89,232", "(1,695)", "87,537", "56,804"), 3, "Total Income from Continuing Operations", IE, CON)
series(c, "opex", ("56,880", "64,027", "3,504", "67,531", "46,752"), 3, "Total Expenses from Continuing Operations", IE, CON)
add(c, "opres_original_budget", "17,239", 3, "Net Operating Result from All Operations", IE + " | Original Budget 2021/22", "after capital grants & contributions")
add(c, "opres_projected_year_end", "20,006", 3, "Net Operating Result from All Operations", IE + " | Projected Year End Result", "after capital grants & contributions")
add(c, "opres_before_capital_original_budget", "(1,814)", 3, "Net Operating Result before Capital Items - Surplus/(Deficit)", IE + " | Original Budget 2021/22", "before capital grants & contributions")
add(c, "opres_before_capital_projected_year_end", "(2,057)", 3, "Net Operating Result before Capital Items - Surplus/(Deficit)", IE + " | Projected Year End Result", "before capital grants & contributions")
series(c, "capex", ("35,411", None, "(10,717)", "28,080", "14,210"), 9, "Total Capital Expenditure", CAP,
       "consolidated; columns Original, Carry Forwards 1,864, Sep QBRS (296), Dec QBRS 1,818, Mar Qtr variation, Projected - no revised-budget column printed")
FE = "function line includes internal transactions; Mar Qtr variation notes 18,26,27 (emergency works: Goobaragandra Rd, Jan 2022 storm & flood, Nov 2021 flood; Regional Roads Emergency Works Feb 2021 storms & floods, Oct 2020 storm)"
series(c, "disaster:other", ("450", "450", "3,656", "4,106", "1,288"), 4, "Fire and Emergency Services", IEF + " - Income", "income; " + FE)
series(c, "disaster:operating_expense", ("968", "968", "3,655", "4,623", "2,369"), 5, "Fire and Emergency Services", IEF + " - Expenses", "expense; " + FE)
NT = "Income & Expenses Budget Review Statement - Recommended changes to revised budget | Note "
NC = "Capital Budget Review Statement - Recommended changes to revised budget | Note "
for n, nc in ((1, 40), (2, 41)):
    town = "Tumbarumba" if n == 1 else "Batlow"
    lab = "EPA Bushfire Recovery Program " + town + " Resource Recovery Centre (RRC) Upgrade Originally reported as operational, adjustment to recognise project as Capital Expenditure"
    add(c, "disaster:operating_expense:narrative", "308,375", 6, lab, NT + str(n) + " (Effect +308,375)", "narrative; reclassification out of operating expenditure (reduction)", units="$")
    add(c, "disaster:capital_expense:narrative", "308,375", 10, lab, NC + str(nc) + " (Effect (308,375))", "narrative; reclassified into capital expenditure", units="$")
for n, amt, tot, lab in ((8, "528,000", "660,000", "Khancoban Pool Upgrade"), (9, "1,400,000", "1,750,000", "Batlow Pool Upgrade"), (10, "720,000", "900,000", "Tumut Pool Upgrade")):
    add(c, "disaster:grant_income:narrative", amt, 6, lab + ", works and expenditure deferred to next year (Grant Funded - Bushfire Local Economic Recovery Stream 1 - BLER 1)", NT + str(n),
        "narrative; deferral = reduction this year (Effect negative) of BLER-funded grant/works; capital note %d repeats the same amount as capital expenditure deferral" % (n + 34), units="$")
    add(c, "disaster:capital_expense:narrative", amt, 10, lab + ", works and expenditure deferred to next year (Grant Funded - Bushfire Local Economic Recovery Stream 1 - BLER 1)", NC + str(n + 34),
        "narrative; capital expenditure deferral = reduction this year (Effect positive)", units="$")
    add(c, "disaster:grant_income:narrative", tot, 6, "$" + tot + " Grant Funded - Bushfire Local Economic Recovery Stream 1 - BLER 1", NT + str(n) + " sub-note 'Note 1'", "narrative; total BLER 1 grant for " + lab + " (multi-year)", units="$")
add(c, "disaster:grant_income:narrative", "500,000", 6, "Emergency Evacuation and Multi-Purpose Centre - current year forecast expenditure", NT + "13", "narrative; BLER 1 grant funded; effect (500,000)", units="$")
add(c, "disaster:grant_income:narrative", "10,685,333", 6, "$10,685,333 Grant Funded - Bushfire Local Economic Recovery Stream 1 - BLER 1", NT + "13 sub-note 'Note 2'", "narrative; total project budget Emergency Evacuation and Multi-Purpose Centre (multi-year; balance $10,185,333 in 2022-23/2023-24)", units="$")
add(c, "disaster:capital_expense:narrative", "500,000", 10, "Emergency Evacuation and Multi-Purpose Centre - current year forecast expenditure", NC + "45", "narrative; BLER 1 grant funded", units="$")
add(c, "disaster:other:narrative", "2,626,000", 7, "Emergency works offset by grant income", NT + "18 (Effect 0)", "narrative; emergency works income and matching Materials & Contracts expenditure", units="$")
add(c, "disaster:other:narrative", "1,127,000", 7, "$1,127K - Goobaragandra Road", NT + "18 component", "narrative; component of emergency works 2,626,000; printed '$1,127K'", units="$")
add(c, "disaster:other:narrative", "634,000", 7, "$634K - January 2022 Storm & Flood Event", NT + "18 component", "narrative; component of emergency works 2,626,000; printed '$634K'", units="$")
add(c, "disaster:other:narrative", "865,000", 7, "$865K - November Flood Event", NT + "18 component", "narrative; component of emergency works 2,626,000; printed '$865K' (November 2021)", units="$")
add(c, "disaster:grant_income:narrative", "602,372", 7, "Regional Roads Emergency Works income offset by expenditure in materials & contracts Transport NSW Grant Income - February 2021 Storms & Floods", NT + "26 (Effect 0)", "narrative", units="$")
add(c, "disaster:grant_income:narrative", "427,633", 7, "Regional Roads Emergency Works Income offset by expenditure in materials & contracts Transport NSW Other Income - October 2020 Storm Event", NT + "27 (Effect 0)", "narrative; booked as Other Income", units="$")
add(c, "disaster:grant_income:narrative", "126,817", 7, "Reimbursement for Community Recovery Officer (CRO)", NT + "29", "narrative; disaster (bushfire) community recovery officer reimbursement - label does not name the disaster", units="$")
add(c, "disaster:other:narrative", "490,000", 10, "RHB building refurbishment works deferred to next year Delayed due to need to rectify flooding issues prior to refurbishment works", NC + "49",
    "narrative; capital deferral (effect +490,000); building flooding issue, not clearly a natural-disaster event", units="$")

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["region_id", "council", "fy", "quarter", "item", "value_aud", "units_in_pdf", "page", "printed_page", "label", "table_title", "file", "notes"])
    w.writerows(rows)
print(len(rows), "rows ->", OUT)
