# Stage 8 results: did towns cut off in Black Summer change differently? (exploratory)

## Verdict (pre-registered, exploratory)

**BETTER.** From the 2016 to the 2021 Census, the median population growth was
**10.3%** in the 19 towns fully cut off by a Black Summer fire, against **4.2%** in the 119 towns
that were burned but not cut off. The difference is **6.1 percentage points** (95% CI 2.2 to 12.7;
Mann–Whitney p = 0.006).

### In plain words

We compared towns that lost all their roads out in Black Summer with towns that were burned but kept
at least one road. The cut-off towns grew **more** the burned-only towns between 2016 and 2021.
This is an exploratory first look. The groups are small and one fire complex dominates, and the 2021
Census happened during COVID-19. It cannot show that being cut off *caused* any change.

## How to read this

The faster growth is most likely about **where** these towns are, not about being cut off:
- Most cut-off towns are coastal (South Coast and Mid North Coast). Coastal towns grew strongly in 2016–2021, including the COVID-era move to the coast.
- The fastest growers include new housing estates (the town table shows Red Head and Tallwoods Village).
- The cut-off towns that are inland or were badly damaged barely grew or shrank (see Batlow, Buxton and Mogo in the table).

A 2011–2016 pre-trend check, or a coastal-only comparison, would be needed to separate these. Either
would be a new pre-registered test. The result here does **not** mean being cut off helps a town.

## All comparisons (towns with boundary match IoU ≥ 0.7 unless stated)

| Outcome | Comparison | n | Median cut off | Median comparison | Difference [95% CI] | p (Mann–Whitney) | p (Holm) | Verdict |
|---|---|---|---|---|---|---|---|---|
| Population growth 2016→2021 (%) | cut off vs burned, not cut off | 19 / 119 | 10.3 | 4.2 | 6.1 [2.2, 12.7] | 0.006 | — | BETTER |
| Median household income change (%, nominal) | cut off vs burned, not cut off | 19 / 119 | 17.7 | 19.9 | -2.3 [-9.1, 4.5] | 0.253 | 0.759 |  |
| Employment-to-population ratio change (pp) | cut off vs burned, not cut off | 19 / 119 | 0.4 | 1.1 | -0.7 [-3.5, 2.3] | 0.652 | 1.000 |  |
| Unemployment rate change (pp) | cut off vs burned, not cut off | 19 / 119 | -2.0 | -1.8 | -0.2 [-1.1, 1.1] | 0.800 | 1.000 |  |
| Population growth 2016→2021 (%) | cut off vs not touched | 19 / 291 | 10.3 | 2.5 | 7.8 [4.4, 14.2] | 0.000 | — |  |
| Median household income change (%, nominal) | cut off vs not touched | 19 / 291 | 17.7 | 19.5 | -1.9 [-8.5, 4.7] | 0.455 | — |  |
| Employment-to-population ratio change (pp) | cut off vs not touched | 19 / 291 | 0.4 | 1.7 | -1.3 [-3.6, 1.7] | 0.308 | — |  |
| Unemployment rate change (pp) | cut off vs not touched | 19 / 291 | -2.0 | -1.9 | -0.2 [-1.0, 1.1] | 0.884 | — |  |
| Population growth 2016→2021 (%) | cut off vs burned, not cut off (IoU ≥ 0.5) | 20 / 124 | 9.8 | 4.6 | 5.3 [2.4, 11.3] | 0.006 | — |  |
| Population growth 2016→2021 (%) | cut off vs burned, not cut off (IoU ≥ 0.85) | 18 / 114 | 9.5 | 4.3 | 5.2 [1.9, 10.7] | 0.009 | — |  |

The verdict uses only population growth against burned-not-cut-off towns. The other rows are descriptive.

## Cut-off towns

| Town | Pop. 2016 | Pop. 2021 | Pop. growth % | Income change % | Emp. ratio change pp | Boundary match (IoU) |
|---|---|---|---|---|---|---|
| Ulladulla | 13,054 | 14,396 | 10.3 | 27.6 | 3.6 | 0.86 |
| Batemans Bay | 11,294 | 12,263 | 8.6 | 24.4 | 2.8 | 1.00 |
| Sussex Inlet | 3,363 | 3,659 | 8.8 | 12.3 | 3.5 | 0.95 |
| Malua Bay | 2,205 | 2,372 | 7.6 | 17.7 | -0.2 | 1.00 |
| Buxton (NSW) | 1,715 | 1,741 | 1.5 | 7.8 | -1.7 | 1.00 |
| Milton | 1,309 | 1,538 | 17.5 | 21.0 | -2.7 | 0.80 |
| Hallidays Point - Black Head | 947 | 1,106 | 16.8 | 7.8 | -2.1 | 1.00 |
| Batlow | 1,021 | 1,022 | 0.1 | 12.2 | -3.3 | 1.00 |
| Diamond Beach (L) | 886 | 1,012 | 14.2 | 12.1 | 0.4 | 1.00 |
| Tallwoods Village (L) | 705 | 993 | 40.9 | 4.6 | 1.6 | 1.00 |
| Red Head (L) | 514 | 798 | 55.3 | 19.1 | -1.7 | 1.00 |
| Lake Tabourie (L) | 645 | 670 | 3.9 | 16.2 | 1.0 | 1.00 |
| Berrara - Cudmirrah (L) | 575 | 612 | 6.4 | 32.6 | 6.4 | 1.00 |
| Hallidays Point - West (L) | 406 | 500 | 23.2 | 19.8 | -1.6 | 1.00 |
| Cobargo (L) | 388 | 417 | 7.5 | 24.3 | 10.5 | 1.00 |
| Balmoral (L) | 325 | 365 | 12.3 | 33.7 | 5.1 | 1.00 |
| Kioloa (L) | 254 | 284 | 11.8 | 28.9 | 7.7 | 1.00 |
| Mogo (L) | 253 | 249 | -1.6 | 9.4 | -1.6 | 1.00 |
| Nelligen (L) | 209 | 245 | 17.2 | 8.0 | -5.3 | 1.00 |

## Coverage

- Black Summer fire families: 291. Towns analysed: 466; groups: {'not touched': 311, 'burned, not cut off': 133, 'cut off': 22}.
- After the boundary-match filter (IoU ≥ 0.7): {'not touched': 291, 'burned, not cut off': 119, 'cut off': 19}.
- Cut-off towns dropped because their 2016 and 2021 boundaries differ too much: Moruya, Bawley Point (L), Rosedale - Guerilla Bay (L).

Figure: `out/change_by_group.png`.

## Caveats

- **Exploratory.** There are few towns and one dominant fire complex; the intervals treat towns as independent, so they are optimistic.
- **COVID-19.** The 2021 Census (August 2021) coincided with lockdowns, and many people moved to coastal towns during the pandemic.
- **No pre-fire trend check.** 2011 data were not obtained, so the groups may already have been on different paths before 2019.
- **Boundaries.** Towns are linked across Censuses by boundary overlap. Small boundary changes remain even above the IoU threshold.
- This makes no causal or lives-saved claim.

## Run

Seed 20260921, 2000 bootstrap resamples, run at 2026-09-22T06:30:19+00:00.
All inputs and downloads were hash-verified. `aussef.duckdb` SHA-256 was unchanged: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.
