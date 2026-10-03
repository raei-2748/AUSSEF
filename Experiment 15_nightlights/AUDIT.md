# Experiment 15 (night lights): independent audit

Auditor: fresh reviewer agent, 2 Oct 2026. I did not write this experiment. The only file I wrote is this report. My
two check scripts are in the scratchpad: `recompute.py` (my own version of the method, which does not import
`analysis.py`) and `bands.py` (a split by brightness, using `results/pixels_south_coast.csv`).

## What checks out

- **Locks.** `shasum -a 256 PRESPEC.md` gives b5f70635…208b, the same as LOCK.txt. `PRESPEC_AMENDMENT_1.md` gives
  6f418161…f222, the same as LOCK_AMENDMENT_1.txt. The file times fit the story: PRESPEC 22:47:06, LOCK 22:47:13,
  Amendment lock 22:58:15, `work/rad.npy` made at 23:02 (after both locks).
- **The point estimates are correct.** My own code rebuilt every South Coast and Tathra window D (3 rings × 5 windows)
  from the `work/` arrays. All 30 match `results/windows.csv` to 5 decimal places. Example: South Coast, inside, Early
  (2020-04..09): ln(Σr/ΣE) = −0.09433, which is −9.00%. Control pools also match (1,429 and 397 pixels), and so do the
  ring sizes (105/286/602 and 9/18/40). Settled pixels: 31,662, holding 2,846,474 dwellings.
- **Every number in the FINDINGS tables matches the results files**, using 100(e^D − 1). This covers the §3 and §4
  tables, the §7 sensitivity table, the placebo values from summary.json, the council block-bootstrap interval, the
  gradient (−0.057 [−0.204, +0.054]), V1 (+0.36 [−0.54, +0.85], n=10) and V2 (−0.040 [−0.103, +0.027], 8 vs 12). The
  post-hoc V2 (−0.068) also matches when I recompute it from pooled_fires.csv. The control-pool council counts in §6
  and §9 match my spatial join (QPRC 223, Shellharbour 214, Yass 173, Snowy Monaro 160, Goulburn 153, Kiama 108;
  Tathra: Snowy Monaro 235, Bega Valley 146). **No mismatches found.**
- **The code follows the PRESPEC definitions:**
  - settled pixel ≥ 5 dwellings;
  - n_cf ≥ 2, plus the 2 km hotspot and outline masks;
  - same-calendar-month baseline over S−24..S−1;
  - bands [0,1), [1,3), [3,10), [10,30), ≥30 (np.digitize is left-closed, which is correct);
  - controls 15-150 km away, not in Greater Sydney, no fire within 10 km from S−24 to E+12, and dropped once a later
    fire comes within 10 km;
  - re-burn censoring after E;
  - R(s,m) falls back to the all-band ratio when fewer than 20 controls;
  - windows set relative to E;
  - placebo baseline S−24..S−13.

  The fire file is in EPSG:3577, so the distances in prep.py are in metres, as intended.
- **Pseudo-town interval.** `[D − q97.5(null), D − q2.5(null)]` is coded as Amendment 1 says (analysis.py lines
  264-265 and 277). "Detected if the interval excludes 0" is applied correctly in every FINDINGS cell I checked.
- **Wording.** The phrase "no effect" does not appear. No ACM host appears in the bibliography part.
- **FIRE_LIGHT_CHECK quotes.** The quotes from the EOG page, Wang et al. 2016 and the Black Marble guide are faithful
  to `sources/*.txt`. Details and small issues are in findings 14-16.

## Findings

No **critical** findings: no wrong numbers and no broken lock. The problems are about interpretation: the write-up
says more than the pre-set tests show.

### 1. SEVERITY: major. Verdict (c) "Shows rebuilding: Met" depends on one odd month at the very end of the data
- **Where:** FINDINGS.md lines 59-60, line 104 (verdict row c) and line 108 ("fades by about 2025").
  summary.json `recovery_inside: "2025-01"`.
- **What I found:**
  - The only 6-month run that meets the Q3 rule is **2025-01..2025-06, the last six months in the data**. Jan 2025 is
    the last month for which "stays for 6 months" can even be checked, and the 2025-06 value is a 2-month average at
    the edge.
  - Before 2025, the 3-month average was ≥ −0.05 in only 18 of 60 months, and never for more than 6 in a row.
  - The run depends on **Feb 2025**, when D jumps by +0.28 to +0.37 in every South Coast ring, including the unburned
    1-5 km ring (+0.373) and the whole-council group (+0.370). The smoothed value for Jan 2025 is mean(−0.294, −0.131,
    +0.296) = −0.043, which only just passes.
  - If Feb 2025 is left out, Jan and Feb fail (−0.21 and −0.15) and no recovery month is found.
  - A shift that hits every ring and the councils at once is a regional or control-side shock, not rebuilding.
  - My post-hoc split (`bands.py`): the 19 inside pixels with baseline ≥ 1 nW/cm²/sr are still −14.8% below expected
    in the Later window. The 0-1 km pixels with baseline ≥ 1 are −15.9%. The near-zero Later figure comes from the dim
    pixels.
- **Fix:**
  - Keep the rule's literal result, but write it as: "The pre-set rule is met only at the last possible month
    (2025-01). That depends on a single month (Feb 2025) that jumped in every ring and in the council group. Recovery
    is not robust, and rebuilding is not shown."
  - Change verdict (c) to "Met by the rule, but not robust (depends on Feb 2025 at the data edge)".
  - Delete "fades by about 2025".
  - Add a line noting that 2024-10 is a different product (`ecmcfg`; see finding 15).

### 2. SEVERITY: major. "Real, local dimming" and "The signal is local" go against the pre-set locality test (Q4)
- **Where:** FINDINGS.md line 58 ("The signal is local.") and line 107 ("a real, local dimming").
- **What I found:**
  - The pre-registered test of locality is Q4, the gradient inside minus 1-5 km. It was **not detected: −0.057
    [−0.204, +0.054]** (§7, line 140). Saying "local" because the 1-5 km ring alone was not detected uses absence of
    evidence as evidence.
  - Q4 is also missing from the §6 verdict table.
  - The Early window (Apr-Sep 2020) is exactly the first COVID lockdown. The inside and 1-5 km rings are both coastal
    holiday areas, while most controls are inland towns. Q4 is therefore the one test that guards against a regional
    COVID or tourism shock, and it did not separate the rings.
  - The Q4 interval is also wide partly because the 1-5 km pseudo-towns take 42% of the control pool (FINDINGS §8
    item 5).
- **Fix:**
  - Replace "The signal is local" with: "A drop was not detected 1-5 km away (−3.6% [−9.9%, +1.7%]). But the pre-set
    test of whether the drop is bigger inside than 1-5 km away was not detected either: −0.057 [−0.204, +0.054]."
  - Replace "real, local dimming" with "a detected dimming inside and within 1 km of the outlines".
  - Add Q4 as a row in the §6 table.

### 3. SEVERITY: major. "Lasts 1.5-2.5 years" is only supported up to 1.5 years
- **Where:** FINDINGS.md line 108 (also line 53).
- **What I found:**
  - Months 19-30 were not detected, either inside (−9.6% [−20.7%, +0.3%]) or 0-1 km (−12.4% [−18.0%, +2.3%]).
  - "Lasts 1.5-2.5 years and fades by about 2025" also contradicts itself: it lasts 2.5 years, yet recovers only after
    5.
- **Fix:** "Detected through month 18 (to Sep 2021). Point estimates stay about −10% to month 30, but the intervals
  include 0 (not detected)."

### 4. SEVERITY: major. The placebo is too wide to say "tracked closely" or "not an old trend"
- **Where:** FINDINGS.md lines 56-57.
- **What I found:**
  - The placebo is −2.6% [−11.9%, +4.8%]. Its lower end (−11.9%) is larger than the effect being defended (−9.0%), so
    a pre-fire slide as large as the effect cannot be ruled out.
  - C1 passes by the pre-set rule (|D| ≤ 0.05), and that part is fine.
  - The month-by-month curves (finding 13) make this look stronger than it is, because their pre-fire part is the
    baseline period itself.
- **Fix:** "Before the fire, a gap was not detected (−2.6% [−11.9%, +4.8%]). This passes the pre-set C1 rule, but
  the interval is too wide to rule out a pre-fire decline of the same size as the effect."

### 5. SEVERITY: major. The headline (a) depends on Amendment 1, and the evidence for Amendment 1 was not saved
- **Where:** FINDINGS.md lines 102 and 133-139. PRESPEC_AMENDMENT_1.md lines 13-19 and 29.
- **What I found:**
  - The Amendment was made before the radiance was read, so it is legitimate.
  - But under the originally pre-registered block bootstrap, Q1's interval is [−16.0%, +0.7%], which covers 0. So
    verdict (a) would read "not detected" under PRESPEC as first locked.
  - Add the other weak points: the upper bound under the main interval is only −1.7%, S5 touches 0 (+0.1%), and S4
    halves the effect (−4.2%).
  - The synthetic-test numbers that justify the switch have no output file (no `results_synth/` exists): 12 null
    runs, unbiasedness +0.002/+0.014, spread 0.042 vs 0.045, and recovery of the planted −0.364. Rule 5 is not met for
    these numbers.
- **Fix:**
  - In §6 row (a), add: "Met under the Amendment-1 interval (fixed before data). Under the original block bootstrap,
    the interval [−16.0%, +0.7%] covers 0."
  - Re-run `SYNTH=1` for the 12 seeds and save the outputs (e.g. `results_synth/synth_summary.csv`), or label the
    amendment numbers "not saved".

### 6. SEVERITY: minor. "Did not track" is close to the banned "no effect" wording (rule 4)
- **Where:** FINDINGS.md line 110: "It did not track how many homes were destroyed across fires."
- **Fix:** "Tracking with home loss was not detected (V1 ρ = +0.36, CI [−0.54, +0.85]; V2 −0.040, CI [−0.103,
  +0.027])."

### 7. SEVERITY: minor. Some results do not come from code in `src/`, and the locked code was not kept
- **Where:**
  - `results/posthoc_v2_pool200.txt`: no code in `src/` writes it.
  - The control-pool council counts in FINDINGS lines 115-117 and 168-169: no code or results file produces them.
  - FINDINGS §8 item 6 claims the current analysis.py "differs only by" fixes 2-3, item 4 and a NaN guard. The
    locked version (sha256 96ccd2…) was not saved, so this cannot be checked. Current analysis.py: c3bcdff4….
- **What I found:** I recomputed both sets of numbers and they are right. They are not reproducible from the repo,
  though.
- **Fix:**
  - Add a small `src/posthoc.py`, labelled post-hoc, that writes `results/posthoc_v2_pool200.txt` and
    `results/control_pool_lga.csv`.
  - Restore or recreate the locked analysis.py as `src/analysis_at_lock.py` and check its hash, or delete the
    "differs only by" sentence and say the locked copy was not kept.

### 8. SEVERITY: minor. The pseudo-town intervals are broken in some cells that are still printed
- **Where:**
  - `results/windows.csv`, south_coast_councils rows: the Early interval [−0.102, −0.063] does not even contain
    D = −0.043, and Later does not contain +0.024.
  - `results/pooled_fires.csv`: Whitehall HR [−0.444, −0.119] does not contain D = −0.003. CESSNOCK RD has **3**
    control pixels.
  - Monthly 1-5 km rows, e.g. 2025-01: D = −0.032 with interval [−0.694, −0.076].
- **What I found:**
  - FINDINGS avoids using these for verdicts, which is good. But anyone reading the CSVs will be misled.
  - The PRESPEC set no minimum size for the control pool, so V2 (pre-set) includes a fire compared against 3 pixels.
- **Fix:**
  - Blank `lo`/`hi` when the ring is more than ~25% of the pool or the pool is under ~200 pixels, and add a
    `ci_valid` column.
  - Add to §8: "the pre-set V2 includes fires with 3-178 control pixels".

### 9. SEVERITY: minor. The "During" row is thin, and its interval is too narrow
- **What I found:**
  - South Coast "During" uses Nov 2019 with **8 of 105** inside pixels, and Mar 2020 with 97. FINDINGS line 44 says
    only "Nov 2019 and Mar 2020 usable".
  - Pseudo-towns keep all their pixel-months, while the treated ring keeps only 105 of 525. So the null spread is too
    small for this window.
- **Fix:** Add the pixel counts. Say the During interval understates uncertainty. It is not used for any verdict.

### 10. SEVERITY: minor. Small departures in `recovery_month` (analysis.py lines 322-332) and in S5
- **What I found:**
  - "6 months in a row" counts 6 *available* months. Missing months (2021-08, 2022-06, 2022-08) are skipped, so a run
    can cover 7-8 calendar months.
  - The smoothed value at E+1 averages in month E, a fire month.
  - S5 (`base_months=12`) also shrinks the window for excluding controls to S−12..E+12 (analysis.py line 142). This
    changes the control pool and is not stated.
  - S1 and S2 barely touch the Early window: Tathra's D is identical to the main run, and South Coast changes by
    0.0003. "Survives a wider fire mask" is therefore weak evidence.
- **Fix:** List these in §8 as known quirks. Say S1 and S2 change very few Early pixel-months.

### 11. SEVERITY: minor. Results that were pre-set or computed but are missing from FINDINGS
- **What I found:**
  - The PRESPEC "random placebo groups" check is in summary.json but is not reported. South Coast: 2.0% of random
    block groups fall below the real Early D. Tathra: 72.3%.
  - The Tathra table leaves out Months 19-30. In that window the 1-5 km ring is also detected (−14.7% [−29.8%,
    −3.2%]), so the §4 "lead" covers two windows, not one.
  - The Tathra "Later" row is labelled "(Black Summer, COVID)". Black Summer actually falls in months 19-30
    (2019-11..2020-10).
- **Fix:** Add the random-placebo line and the Tathra months 19-30 row, and fix the label.

### 12. SEVERITY: minor. Statements with no support, or that do not match their source
- **Where:**
  - FINDINGS line 62-63: "This supports the reason night lights were dropped at council level in Experiment 7." But
    Experiment 7 dropped them because council lights *rose* after heavy fires (Experiment 7/FINDINGS_DAY1.md line 65),
    while here the council gap is a *fall*. These are different reasons.
  - Lines 54-55: "Many homes sit on the bush edge" has no source.
- **Fix:**
  - Change the first to: "consistent with council averages being a weak measure: the inside signal is diluted at
    council level".
  - Mark the bush-edge point as a guess, or drop it.

### 13. SEVERITY: minor. The month-by-month curves can mislead
- **Where:** `figures/curves_south_coast.png` and `curves_tathra.png`, from figures.py line 40.
- **What I found:**
  - The plotted pre-fire months are S−24..S−1, which is the **baseline period itself**. D sits near 0 there by
    construction, yet it looks like a parallel-trends check.
  - The y-axis is clipped at ±60%, so many Tathra values from 2023-2025 are off the chart, and the figure does not
    say so.
  - The 1-5 km bands come from pseudo-towns that use 42% of the pool (see finding 8).
- **Fix:**
  - Shade S−24..S−1 and label it "baseline months (near 0 by construction)". Optionally overlay the placebo-window
    curve instead.
  - Note the clipping.

### 14. SEVERITY: minor. FIRE_LIGHT_CHECK.md overstates what the design achieves
- **Where:**
  - Line 44-45: the masks remove "most of the nearby smoke".
  - Line 51-52: regional smoke and COVID "hit both groups, so they cancel out". This conflicts with FINDINGS line
    166-167 ("can only partly cancel").
  - Line 53-54: "Burnt trees can only push lights up, so a drop … is, if anything, an under-estimate".
- **What I found:**
  - A 2 km same-month mask cannot remove Black Summer smoke, which spread across hundreds of km. No source is given.
  - The canopy point is reasonable as a guess. But "if anything an under-estimate" ignores reasons for dimming that
    have nothing to do with people: charred, dark ground reflecting less street and house light, and damaged power
    networks.
  - My post-hoc split weakens the dark-ground idea: the drop is bigger in brighter pixels (−11.6% vs −6.8% in dim
    ones). But nothing has tested it.
- **Fix:**
  - "removes flame light and same-month smoke very close to the pixel".
  - "partly cancel".
  - "Canopy loss would push lights up. Other non-people effects (dark burnt ground, power damage) could push them
    down, so the bias direction is unknown."

### 15. SEVERITY: minor. Small factual slips in FIRE_LIGHT_CHECK.md
- **What I found:**
  - Line 10-11: "Their names contain `vcm-slexcl` or `ecm-slexcl`". The manifest shows 262 such files. The other 2
    (2024-10 avg and n_cf) are `ecmcfg`, which bibliography row E15-P01 already notes. That 2024-10 product switch,
    inside the South Coast Later window, is also missing from FINDINGS §9 "Product changes" (only 2017-04 and 2018-01
    are listed). The project's own econ_quarterly.py lines 20-21 list it.
  - Line 39: VNF "needs a licence application". The saved page says data are "available through a VIIRS Nightfire
    Data Use License". Better: "now under a data-use licence".
  - The Black Marble page numbers (p9, p10, p51) are PDF page numbers. The printed page numbers are 3-4 and 45. The
    quality-flag table also appears on PDF p23. Write "PDF p.".
- **Fix:** As above.

### 16. SEVERITY: minor. Bibliography gaps (rule 1)
- **What I found:**
  - E15-002 (Google Earth Engine catalogue) has no saved copy. It holds the key quote ("has NOT been filtered …"), and
    the second quote used in FIRE_LIGHT_CHECK line 13 ("stray light, lightning, lunar illumination, and
    cloud-cover") is not recorded anywhere, so neither can be checked locally. Save the page text to `sources/` with
    its sha256 and add the second quote to `quote_or_value`.
  - E15-D06 (ABS LGA 2021) has no URL. E15-D04 and E15-D05 have no URL either; their notes point to the manifest,
    which is acceptable.
  - FINDINGS §10.3 mentions "FESM 2019-20, already on OneDrive" but has no bibliography row. Add one: mentioned, not
    opened.
  - FIRE_LIGHT_CHECK line 29 cites "Experiment 7/FINDINGS_DAY1.md" without its id. Add [E15-P05].
  - E15-004 year: the PDF title page says "October 2024", so 2024 is correct. The URL path says 2025-05, which is the
    upload date. That is fine; add a note.
  - No ACM sources were found.

### 17. SEVERITY: minor. FINDINGS refers to an audit file that does not exist yet
- **Where:** FINDINGS.md line 7: "Independent audit: see AUDIT.md (done before this was reported)".
- **What I found:** AUDIT.md is not in the folder.
- **Fix:** Save this audit as AUDIT.md and add a short list of what was changed in response.

## Suggested §6 wording (plain English)

| Rule | Result |
|---|---|
| (a) Measures the shock | Met under the Amendment-1 interval (fixed before data): −9.0% [−20.4%, −1.7%]. Fragile: the original block bootstrap gives [−16.0%, +0.7%], the 12-month baseline touches 0, and the per-pixel average halves it. |
| Q4 Gradient (inside − 1-5 km) | Not detected: −0.057 [−0.204, +0.054]. So it is not shown that the drop is specific to the burned area rather than a regional (e.g. COVID-season) change. |
| (b) Tracks home loss | Not detected: V1 ρ +0.36 [−0.54, +0.85]; V2 −0.040 [−0.103, +0.027]. |
| (c) Shows rebuilding | The rule is met only at the last possible month (2025-01). This depends on one month (Feb 2025) that jumped in every ring, so it is not robust. Brighter pixels inside are still about 15% below expected in 2022-25 (post-hoc). |

---

## Responses (main analyst, 2 Oct 2026)

The auditor's check scripts are saved in `audit_scripts/`.

| # | Response |
|---|---|
| 1 | **Accepted.** Verdict (c) now reads "met by the letter only, not robust". "Fades by about 2025" was removed. The Feb 2025 jump and the "no recovery without Feb 2025" result are now produced by `src/posthoc.py` (`results/posthoc_recovery_checks.txt`). The brightness split was added, labelled post-hoc. |
| 2 | **Accepted.** "Local" wording was removed. The Q4 gradient (not detected) is now a row in the §6 verdict table, with the COVID / coast-vs-inland point. |
| 3 | **Accepted.** Now reads "detected through month 18 (to Sep 2021)". Months 19-30 are "not detected". |
| 4 | **Accepted.** Placebo wording changed: a pre-fire decline as big as the effect cannot be ruled out. |
| 5 | **Accepted.** Verdict row (a) now states the block-bootstrap result [−16.0%, +0.7%] and the S5 / S4 weak points. The synthetic test was re-run and saved in `results_synth/`. The numbers match those in the amendment. |
| 6 | **Accepted.** Now reads "a link with home loss was not detected". |
| 7 | **Accepted.** `src/posthoc.py` now writes the post-hoc V2 and the control-pool councils. The "differs only by" sentence was replaced: the locked analysis.py copy was not kept. |
| 8 | **Accepted.** `ci_valid` and `ci_note` columns were added to `results/windows.csv` and `results/pooled_fires.csv`. FINDINGS §5 notes the 3-178 pixel pools. |
| 9 | **Accepted.** The pixel counts and the "understates uncertainty" note were added to the During row. |
| 10 | **Accepted.** Listed in FINDINGS §7 (S1/S2 weak, S5 also changes the control window) and §8 item 7 (recovery-rule quirks). |
| 11 | **Accepted.** The random-block-groups row was added to §7. Tathra months 19-30 were added, and the Black Summer label was moved to that row. |
| 12 | **Accepted.** The Experiment 7 sentence was reworded. The "bush edge" claim was removed. |
| 13 | **Accepted.** Curves now shade the baseline months and label them "near 0 by construction (not a trend test)". The ±60% clipping is stated in the title. |
| 14 | **Accepted.** FIRE_LIGHT_CHECK.md now says the mask removes only flame light and nearby same-month smoke, that differences only partly cancel, and that the bias direction is unknown. |
| 15 | **Accepted.** The 2024-10 `ecmcfg` product is in FIRE_LIGHT_CHECK.md and FINDINGS §9. Licence wording fixed. Page numbers now say "PDF p.". |
| 16 | **Accepted.** Saved copy and both quotes for E15-002. URL added for E15-D06. FESM row E15-D07 added. [E15-P05] cited. Note added to E15-004. Audit row E15-P07 added. |
| 17 | **Accepted.** This file is now AUDIT.md. |
