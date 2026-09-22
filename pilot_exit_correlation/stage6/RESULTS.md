# Stage 6 results: cut-off risk versus council finances

## Verdict (pre-registered)

**NOT SUPPORTED.** Councils with at least one town that fires have fully cut off
(10 councils) raise a median **68.0%** of their revenue from their own sources.
Other councils (72) raise **62.0%**. The difference is **6.0 percentage points**
(95% CI 0.9 to 15.0; Mann–Whitney p = 0.035). A mismatch needed a difference below 0
with the whole interval below 0.

### In plain words

We checked whether the councils whose towns get completely cut off by fire are also the councils
with the least money of their own. Their own-source revenue share was higher than other councils',
by 6.0 percentage points. The whole interval is above zero, so the pattern is the **opposite** of a mismatch: councils with cut-off towns have *more* of their own revenue, not less.

This compares councils. It does not show that fires caused their finances, or the reverse, and it says nothing about lives.

## All measures (2018-19, exposed vs all other councils)

| Measure | Exposed councils | Other councils | Median exposed | Median other | Difference [95% CI] | p (Mann–Whitney) | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| Own-source revenue share (%) | 10 | 72 | 68.0 | 62.0 | 6.0 [0.9, 15.0] | 0.035 | (primary) | NOT SUPPORTED |
| Cash cover (months) | 10 | 72 | 9.2 | 12.2 | -2.9 [-4.5, 1.3] | 0.245 | 0.736 |  |
| Operating ratio (%) | 10 | 72 | 1.2 | 1.8 | -0.6 [-6.6, 3.8] | 0.595 | 1.000 |  |
| Grant dependence (% of revenue) | 10 | 72 | 32.0 | 38.0 | -6.0 [-15.8, -0.8] | 0.035 | 0.141 |  |
| Maintenance funded (% of required) | 10 | 71 | 98.5 | 100.0 | -1.5 [-9.1, 7.1] | 0.605 | 1.000 |  |
| Road km per 1,000 residents | 10 | 72 | 21.0 | 127.9 | -106.9 [-152.6, -35.1] | 0.008 | 0.041 |  |

Only own-source revenue share decides the verdict. The other measures are descriptive, with p-values adjusted for multiple comparisons (Holm).

## Sensitivity checks (no verdict)

| Comparison | Baseline | n exposed / other | Median exposed | Median other | Difference [95% CI] | p |
|---|---|---|---|---|---|---|
| fire-touched, never cut off | 2018-19 | 10 / 49 | 68.0 | 65.9 | 2.1 [-2.4, 11.7] | 0.229 |
| all other councils | 2016-17 to 2018-19 average | 10 / 72 | 69.0 | 61.6 | 7.4 [1.9, 14.2] | 0.015 |
| all other councils (legacy panel, post-hoc) | 2018-19 | 15 / 85 | 67.8 | 61.4 | 6.4 [2.2, 13.3] | 0.009 |

Spearman rank correlation between the share of a council's residents living in cut-off towns and
its own-source revenue share, across all matched councils: ρ = 0.23
(permutation p = 0.037).

## Exposed councils

| Council | Towns cut off | Residents in cut-off towns | Own-source % | Grants % | Cash cover (months) | Maintenance funded % |
|---|---|---|---|---|---|---|
| Richmond Valley | 1 | 2,894 | 60.5 | 39.5 | 9.1 | 107.1 |
| Yass Valley | 1 | 284 | 64.3 | 35.7 | 9.1 | 98.0 |
| Wollondilly | 2 | 2,443 | 66.3 | 33.7 | 12.5 | 170.9 |
| Bega Valley | 1 | 417 | 66.8 | 33.2 | 12.2 | 80.0 |
| Wingecarribee | 3 | 3,601 | 67.8 | 32.2 | 22.9 | 98.0 |
| Cessnock | 1 | 255 | 68.1 | 31.9 | 7.0 | 108.9 |
| Eurobodalla | 6 | 18,174 | 68.9 | 31.1 | 14.1 | 100.0 |
| Lake Macquarie | 2 | 1,715 | 75.8 | 24.2 | 8.2 | 93.2 |
| Blue Mountains | 1 | 556 | 82.8 | 17.2 | 3.1 | 99.0 |
| Shoalhaven | 15 | 41,515 | 82.8 | 17.2 | 9.3 | 88.5 |

## Coverage

- Towns: 461, of which 43 were cut off at least once (1950–2023).
- Councils containing these towns: 100. Matched to the fiscal panel: 82.
- Groups: 10 exposed, 49 fire-touched but never cut off, 23 other.
- Cut-off towns in matched councils: 33 of 43.
- Councils not in the fiscal panel (not compared): Armidale Regional, Central Coast (NSW), Cootamundra-Gundagai Regional, Dubbo Regional, Edward River, Federation, The Hills Shire, Hilltops, Hornsby, Inverell, Lachlan, Mid-Coast, Murray River, Murrumbidgee, Nambucca Valley, Queanbeyan-Palerang Regional, Snowy Monaro Regional, Snowy Valleys.
  Most were created by the 2016 amalgamations, which the cleaned extended panel leaves out.
  "Nambucca Valley" appears in the panel as "Nambucca" and was not matched under the exact-name rule.
- **Post-hoc coverage check** (see DEVIATIONS.md): `master.fiscal_panel_legacy` covers these councils.
  With it, 100 councils are compared, 15 of them exposed and containing
  43 cut-off towns (see the sensitivity table).
  Still unmatched: none.

Figure: `out/council_finance_by_group.png`.

## Caveats

- This is descriptive only. Fire risk and council finances share causes, such as remoteness, forest cover and small rate bases.
- Exposed councils are few, so the intervals are wide.
- Cut-offs come from fire maps (stage 2), so they are upper bounds with no timing.
- Councils use fixed 2021 boundaries; only councils in the fiscal panel are compared.

## Run

Seed 20260921, 2000 bootstrap resamples, run at 2026-09-22T02:24:53+00:00.
The inputs and the LGA boundary files were hash-verified.
`aussef.duckdb` SHA-256 was unchanged: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.
