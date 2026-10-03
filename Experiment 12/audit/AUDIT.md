# Audit of Experiment 9 v3 indicators and Experiment 11 impact clock

2 Oct 2026. Independent audit of `Experiment 9/build_v3_indicators.py` (-> `inputs/v3_indicators.csv`) and
`Experiment 11/run_clock.py` (-> `results/CLOCK.csv`, `CLOCK_ROWS.csv`). No existing file was edited. All scripts and
outputs are in this folder; the re-derivations use my own code (they do not import project code).

## Bottom line

**The two "detected" results in Experiment 11 stand.** I re-derived both from raw files with my own code and got the same
n and rho to machine precision: C4 grants per resident, FY F+1: **n = 199, rho = +0.213**. C5 fire-related grant share,
FY F+1: **n = 50, rho = +0.445**. Both survive every stricter comparison and de-duplication check I tried.

**The traffic results change because of a data artefact.** Experiment 11 says "tourism traffic falls with fire size in the
first year, then reverses". Experiment 9 v3 says "IL1 tourism traffic fall tracks the fire (+0.25, n = 98)". Neither
holds up:
1. On about 15% of days at two-direction counting stations, only one direction was recorded, so the daily total is
   roughly halved. These half-counted days become more common after the fire in higher-dose rows (rho +0.22, n = 93).
   I made two corrections: dropping those days, or scaling them back up to both directions. With either one, C1 H0
   goes from rho -0.25 to **-0.03 to -0.05** (permutation p about 0.85).
2. The H2/H3 "reversal" is built into the method. Its baseline is "the same months 12 and 24 months earlier", which for
   months 13-48 after the fire falls inside the fire and its aftermath.
3. 14 more rows get traffic data if old council names are mapped correctly. This does not change rho on its own
   (-0.24).

The traffic primary verdict ("not detected") does not change. The descriptive traffic claims in both FINDINGS files
should be withdrawn.

## Table of checks

| # | Check | Result | Severity |
|---|---|---|---|
| a1 | Name matching: TfNSW traffic station `lga` field | The field uses **pre-2016 council names**. 44 of 153 names are unmatched (29 of 103 among permanent stations), and the project rule silently drops them. Councils that lose all their stations: Central Coast (Gosford 13 + Wyong 4 permanent stations), Mid-Coast, Snowy Monaro, Snowy Valleys, Queanbeyan-Palerang, Armidale Regional, Cootamundra-Gundagai, Nambucca Valley (fire councils), plus Northern Beaches, Inner West, Cumberland, Canterbury-Bankstown, Bayside, Georges River, Hilltops, Federation, Edward River, Murray River (comparison pool). Dubbo Regional loses Wellington. No wrong matches. Fixing the names adds 14 C1 rows (98 -> 112) and rho stays at -0.24. | minor (n loss, no change in rho) |
| a2 | Name matching: BOCSAR | 128 of 129 councils matched, and all 69 fire councils. Unmatched: "In Custody", "Lord Howe Island", "Unincorporated Far West" (so Unincorporated NSW has no DV series). No wrong matches. | none |
| a3 | Name matching: OLG | All 128 councils match for FY2016+. 41 pre-2016 names are unmatched; these are former councils, so this is expected. Three pre-2016 entities share a name with a post-merger council and are **silently matched to it**: old Dubbo City -> Dubbo Regional, old Murrumbidgee Shire -> Murrumbidgee (new), old Parramatta -> City of Parramatta. Dropping them leaves C4 H1 unchanged (n 199, rho +0.2133). No two OLG names map to one council in the same FY. | minor |
| a4 | Name matching: rent | Joined directly on region_id. 128 ids, all fire councils present. The rent file's names differ for 3 ids (Gundagai / Western Plains Regional / Nambucca), but the ids are correct. | none |
| a5 | Snowy Valleys vs Snowy Monaro, Central Coast, Upper Hunter, city vs shire | No collisions: no two of the 129 councils share a normalised key, and no source name maps two councils to one id. | none |
| b1 | Re-derive C4 grants per resident, FY F+1 | **n = 199, rho = +0.213**, identical row by row (max difference 1e-16). My within-season permutation p (10,000 shuffles) is 0.005; Experiment 11 got 0.003 with 2,000. The Holm-adjusted p is still < 0.05. | none |
| b2 | Re-derive C5 fire-grant share, FY F+1 | **n = 50, rho = +0.445**, identical row by row. If the undocumented "has-lines" rule is removed (see f4), I get n = 51, rho +0.449. Using the council's own change without the comparison gives +0.489. | none |
| c1 | Excess logic: comparison = no master row in F, same window | Confirmed. `unburned_fn` = 129 councils minus those with a master row in F. Comparison values come from the same m0 / F windows as the row (the cache key is (F, m0)). C5 uses the fixed Experiment 10 comparison councils (24 with data, not 25), and none of them has a master row in any F. | none |
| c2 | Comparison pool contains burned councils | "No master row" is not the same as "not burned". Councils with ≥ 0.5% of their area burned in FY F but no master row stay in the pool: 16 of 103 for F = 2023, 1-8 in other years. Councils burned in neighbouring years also stay in. C4 H1 with these excluded: +0.221 / +0.221. Comparing only within the same OLG group (metro / regional / rural): +0.228. | minor (no effect) |
| d1 | Traffic sign | log(window / baseline), so a fall is negative and the expected sign is -1. Correct. | none |
| d2 | Statement values in AUD, x1000 applied once | Statement total expenses / OLG total expenses for the same council-FY: median ratio 1.000; only 1 of 207 (fire) and 1 of 193 (comparison) fall outside 0.8-1.25 (13660 FY2017: 1.34; 12870 FY2018: 1.26). No x1000 errors. FY labels match OLG fy_start ('2018-19' -> 2018). | none |
| d3 | Capex sign | No negative capex_ippe values. 1 negative fire/disaster line (fire file) and 11 negative lines (comparison file); these are tiny. | none |
| d4 | OLG grants per resident magnitude | Median A$1,057 per resident (1%: A$119; 99%: A$10,931). Extremes are small remote councils (Brewarrina 2021 A$28,947; Central Darling about A$25,000), consistent with populations of about 1,500. Plausible. | none |
| e1 | Time alignment (5 hand spot-checks, `spot_checks.md`) | Bega Valley (871, start 2019-12-26 -> m0 2019-12, F 2019, H1 = FY2020-21); Eurobodalla (871); Kempsey 2023 fire (1071, 2023-08-15 -> F 2023); Brewarrina (1052, 2023-03-14 -> F 2022); Tenterfield 2016. m0, F, FY labels and window months are all correct. The C4 excess recomputed by hand matches CLOCK_ROWS exactly (e.g. Bega: FY2017 A$824, FY2018 A$1,049, FY2020 A$1,892 per resident; own +0.710, comparison median +0.249, excess +0.462). | none |
| f1 | **Traffic: one-direction (half-counted) days** | 541 of 742 permanent stations switch between 2 and 1 recorded directions. At two-direction stations, 14.9% of station-days since 2013 have only one direction, and the code sums directions, so those days count about half. The share of such days rises after the fire with dose (rho +0.22, n = 93). C1 H0: rho -0.254 as published; -0.046 with only full-direction days; -0.031 with one-direction days scaled up; -0.040 with the project's names plus full days only. Permutation p 0.85-0.88. The same values are Experiment 9 IL1 (identical to C1 H0, n = 98). | **changes results** (descriptive traffic claims in Experiment 11 and Experiment 9 v3) |
| f2 | **Traffic H2/H3 baseline overlaps the fire** | For window months 13-24 the baseline is months 1-12 and -11..0. For months 25-48 it is months 1-36 after the fire. So "traffic higher 1-4 years later" is largely the H0/H1 dip showing up again as a low baseline. This follows PRESPEC, but the "reverses" reading is not valid. | **changes results** (descriptive) |
| f3 | Several rows share one council-FY (FY channels) | C4 H1: 90 of 199 rows share a council-FY with another row (152 distinct). C5 H1: 17 of 50 (41 distinct). They carry the same outcome with different doses, which the row-level permutation treats as independent. With one row per council-FY (dose = max, or homes summed): C4 rho +0.270, p 0.002; C5 rho +0.519-0.525, p 0.002. Holm across the five primary tests: 0.008 for both. Both results get stronger, not weaker. | minor |
| f4 | Undocumented C5 / FP2 rule | The code sets fire share to missing for fire councils with statements but no fire-related line in any year (13660, 15900, 16100, 16490). Neither PRESPEC states this. It removes 1 row at C5 H1 (rho +0.449 -> +0.445). It should be listed as a deviation. | minor |
| f5 | OLG data gaps and carry-forwards | FY2015 has 108 councils and FY2016 has no grants % for the 20 merged councils. FY2019 grants % equals FY2018 exactly for 6 councils (Bayside, **Bega Valley**, Bourke, Kiama, Murrumbidgee, Narrabri), probably carried forward in the source or parse. Population for FY2024 equals FY2023 for all 128 councils. This affects C4 H0 for Black Summer rows and H3 for F = 2021, not the H1 primary result. | minor |
| f6 | Duplicate statement lines | Some council-FY-item-label combinations appear twice with different values (e.g. Richmond Valley "Bushfire and emergency services", operating, 809k + 577k), and both are summed. I could not tell from the tidy file whether this double-counts current and comparative columns. The year pattern suggests two genuine lines, not a current/prior pair. Worth checking against the PDFs. | minor (unverified) |
| f7 | C4 by season | The positive rho comes from F = 2016-2019 (+0.16 to +0.32). F = 2022 and 2023 are slightly negative (-0.10). On ranks within each season, rho is +0.156. | none (descriptive) |
| f8 | FINDINGS wording on "without Black Summer" | It says C4 "holds without Black Summer (+0.16 / +0.28)". In CLOCK.csv, C4 H1 without Black Summer is +0.164 with CI [-0.005, +0.33], which includes 0. The +0.28 is H3, not H2 (H2 is +0.08). This is overstated. | minor (reporting) |
| f9 | X23 code matching (Experiment 9) | No 2016 Census code matches the wrong council: 2016 vs 2021 shares differ by at most 0.06. Fallback for 6 rows, as already stated in deviation 1. | none |
| f10 | Experiment 9 IL1 cache | `inputs/_il1_cache.csv` equals v3 IL1 and equals Experiment 11 C1 H0 row by row, so it is not stale. It has the same f1/a1 problems. | see f1 |

## Re-derived numbers (FY F+1, dose = log(1 + dwellings in fire per 1,000))

| Quantity | Experiment 11 | Audit |
|---|---|---|
| C4 grants per resident, n / rho | 199 / +0.213 | 199 / +0.213 |
| C4, pre-2016 same-name OLG entities dropped | - | 199 / +0.213 |
| C4, comparison also excluding councils burned ≥ 0.5% in F | - | 199 / +0.221 |
| C4, comparison = same OLG group | - | 199 / +0.228 |
| C4, one row per council-FY | - | 152 / +0.270 (perm p 0.002) |
| C5 fire-grant share, n / rho | 50 / +0.445 | 50 / +0.445 |
| C5, literal PRESPEC (no has-lines rule) | - | 51 / +0.449 |
| C5, one row per council-FY | - | 41 / +0.519 (perm p 0.002) |
| C1 traffic H0, n / rho | 98 / -0.254 | 98 / -0.254 (project rule) |
| C1, old names mapped | - | 112 / -0.242 |
| C1, old names + half-counted days fixed | - | 101-112 / -0.03 to -0.05 (p about 0.85) |

## Unmatched names (full lists in `name_matching.txt`, `unmatched_*.csv`)

**Traffic `lga` field, all stations (44 unmatched, station counts in brackets):** Armidale Dumaresq (4), Ashfield (4),
Auburn (12), Bankstown (29), Bombala (6), Boorowa (5), Botany Bay (17), Canterbury (9), Conargo (7), Cooma-Monaro (6),
Cootamundra (11), Corowa (16), Deniliquin (8), Gloucester (2), Gosford (36), Great Lakes (12), Greater Taree (13),
Gundagai (12), Guyra (5), Harden (7), Holroyd (14), Hurstville (5), Jerilderie (11), Kogarah (3), Leichhardt (10),
Manly (3), Marrickville (12), Murray (10), NULL (2), Nambucca (4), Palerang (13), Pittwater (6), Queanbeyan (9),
Rockdale (16), Snowy River (17), Tumbarumba (8), Tumut (14), Unincorporated Far West (3), Urana (5), Wakool (15),
Warringah (16), Wellington (4), Wyong (16), Young (7).
- Councils (of 129) with no traffic match at all: 20. Among permanent stations, which are what the code uses: 55, of
  which **29 are fire councils**. 8 of those 29 are lost only because of old names: Armidale Regional, Central Coast,
  Cootamundra-Gundagai, Mid-Coast, Nambucca Valley, Queanbeyan-Palerang, Snowy Monaro, Snowy Valleys. The other 21 have
  no permanent station: Bellingen, Blayney, Brewarrina, Coffs Harbour, Coonamble, Cowra, Dungog, Greater Hume, Gwydir,
  Kyogle, Lismore, Mid-Western, Narrabri, Oberon, Parkes, Tenterfield, Uralla, Wagga Wagga, Walcha, Walgett, Warren.

**BOCSAR (3 unmatched):** In Custody, Lord Howe Island, Unincorporated Far West. No fire council missing.

**OLG (41 unmatched, all pre-2016 former councils):** armidale dumaresq, ashfield, auburn, bankstown, bombala, boorowa,
botany bay, canterbury, conargo, cooma monaro, cootamundra, corowa, deniliquin, gloucester, gosford, great lakes,
greater taree, gundagai, guyra, harden, holroyd, hurstville, jerilderie, kogarah, leichhardt, manly, marrickville,
murray, palerang, pittwater, queanbeyan, rockdale, snowy river, tumbarumba, tumut, urana, wakool, warringah, wellington,
wyong, young. No fire council is missing for FY2016+. Only Unincorporated NSW has no match in any year.

**Rent:** direct ids. Unincorporated NSW is missing; no fire council is missing.

## Files
- `01_name_matching.py` -> `name_matching.txt`, `unmatched_*.csv` (check a)
- `02_rederive_c4_c5.py` -> `rederived_c4_c5_rows.csv`, `rederived_c4_c5_summary.csv` (check b)
- `03_traffic_c1.py` -> `c1_variants.csv`, `c1_rows.csv` (a1, f1); `04_traffic_direction_diag.py` -> `c1_one_direction_diag.csv`
- `05_excess_and_sensitivity.py` -> `comparison_sets.csv`, `c4_sensitivity.csv` (c, f7)
- `06_duplicate_council_years.py` -> `council_year_dedup.csv` (f3)
- `07_units.py` -> `units_statement_vs_olg_outliers.csv` (d); `08_spot_checks.py` -> `spot_checks.md` (e)
