# Amendment 1 to PRESPEC.md (2026-09-30, written BEFORE any SA score or Y value was computed)

`PRESPEC.md` (hash in `PRESPEC.lock`) is unchanged. This amendment is locked separately (`PRESPEC_AMENDMENT_1.lock`).
What triggered it: after the lock I built the SA roster (11 council rows, identical to the scoping overlay), the BPA hazard and exposure items (`results/geo_items_sa.csv`) and parsed the LGGC PDFs (whole-state table, identity-checked).
Only X-side geometry and report layouts were read. No score, no outcome and no score-versus-outcome relation for any SA council exists yet.

## A1. Definition of "mapped" for H and E (clarifies PRESPEC section 2)
PRESPEC says H and E are built "if the council has any BPA polygon (any class)". The build showed that this test is defeated by boundary slivers: Clare and Gilbert Valleys (1,892 km2) and Wakefield (3,468 km2) each overlap the BPA layer by about 10 ha,
while Adelaide Hills, Mallala, Light, Playford, Kangaroo Island and Mount Barker are covered over practically their whole area by some class (High, Medium, General or Excluded) and Kingston by 0 ha. A 10 ha sliver is cadastral alignment noise, not mapping.
**Rule (frozen now):** a council is `mapped` if BPA polygons of any class (including Excluded and General) cover **at least 1% of the council's area**. Unmapped councils have H and E omitted (not zero), exactly as PRESPEC section 2 intends.
The 1% figure is the same tolerance as the row-inclusion rule. Consequence recorded before scores exist: Clare and Gilbert Valleys, Wakefield (both Pinery) and Kingston (Keilira) are unmapped, so their score has no H and no E.

## A2. Implementation facts that follow from the frozen text (no change of rule)
1. **Services-share denominator.** PRESPEC 4 says "Total Operating Expenses (Report 9)". Report 9 prints a Total Operating Expenses column only from FY2018-19; in FY2013-14 to FY2016-17 it does not. The denominator is therefore **Total Operating Expenses from Report 3 in every year** (the same quantity by definition; where Report 9 also prints a total, the build checks that it equals Report 3's within 0.5%).
2. **Renewals ratio.** PRESPEC 4 names the **Asset Sustainability Ratio** (Report 8). The printed Report 8 column is "Asset Sustainability Ratio (%)" in FY2013-14 to FY2016-17 and **"Asset Renewal Funding Ratio (%)" from FY2018-19** (a different measure: renewal spending against the asset-management-plan requirement). The indicator is therefore built only where both years of the pair carry the Asset Sustainability Ratio header.
   Pair Sampson Flat (FY2013-14, FY2015-16) and Pinery (FY2014-15, FY2016-17) qualify; the three 2019-20 events (FY2018-19, FY2020-21) do not, and their renewals indicator is `N/A (ratio definition changed)`.
3. **Operating ratio.** Own calculation from Reports 2 and 3 (operating surplus / operating revenue), as in PRESPEC 2.1. Report 8 prints the Operating Surplus Ratio as a whole-number percentage, so it is used only as a cross-check to rounding.
4. **Council matching.** LGGC council names are matched to ABS LGA names after removing type suffixes; unmatched names are resolved by a hand table written in `build_scores.py`, and every match is listed in `results/lggc_council_match.csv`.

## A3. Nothing else changes
Score definition, row rule (burned share >= 1%), placement rule, pre-fire vintage rule, comparison-group rule, the 30% F rule, the FP scale check, DL sourcing rule, the pooled-set definition, verdict rule, seeds and power check are as in `PRESPEC.md`.
