# Amendment 1 to PRESPEC.md (2026-09-29, written BEFORE any Y value or score was computed for a new-fire council)

`PRESPEC.md` (hash in `PRESPEC.lock`) is unchanged. This amendment is locked separately (`PRESPEC_AMENDMENT_1.lock`).
Cause: reading the layout of the approved Victorian income file (`6524055002do003_200506201011.xls`, ABS EPISA) after the lock, I found two facts the pre-spec assumed wrongly.
Nothing was computed from the income series; only column titles and the table notes were read (plus, by accident, the first rows of the Victoria wages-and-salaries block for four councils; no calculation was done on them).

## A1. Victoria V block: the income item is average, not median, income
EPISA publishes averages and totals of income by LGA but **no median**. PRESPEC section 2 said "ABS EPISA median income FY2007-08". Replacement (frozen now):
the V-block income item for Victorian rows is **"Average Total Income from all sources (excl. Government pensions & allowances), FY2007-08"** (EPISA Table 2, Victoria), divided by the median of the same
series across NSW LGAs in EPISA Table 1 (same release, same year), oriented lower = worse, and placed in the original ratio-to-median distribution of the 129 NSW councils' median income
(PRESPEC 1.1-1.2). Flag: `computed_substitute` (a mean stands in for a median). The other Victorian V item is SEIFA 2006 IRSD as declared.

## A2. Victoria IL income indicator: documented break in the EPISA series across the fire year
Table note (b) of EPISA: "There is an overall break in series between 2006-07 & 2007-08 and between 2007-08 & 2008-09." The IL income indicator for Black Saturday
(FY2008-09 vs FY2007-08) spans exactly this break. Decision (frozen now): the indicator is **kept as declared** (total income from all sources, excess over the Victorian no-fire median, so a common shift cancels
but a council-specific break effect does not), flagged **`computed_low_confidence`**, and one more descriptive sensitivity is added to PRESPEC 6:
**(f) Victorian IL built from business counts only (drop the income indicator).** As with all sensitivities it cannot change the verdict.
EPISA total income excludes government pensions and allowances; the NSW PIA total income (used in the master and for NSW 2013) does not exclude them. Different products, as PRESPEC already said.

## A3. Nothing else changes
Score definition, row rule (burned share ≥ 1%), percentile placement rule, comparison-group rule, verdict rule, seeds, power check and the primary test are as in `PRESPEC.md`.
