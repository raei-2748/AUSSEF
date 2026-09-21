# Results: correlated-exit-failure pilot

## Verdict (pre-registered rule, S0, ring R = 20 km)

**FAIL.** 0 of 217 eligible communities (0.0%) have rho > 5 with a bootstrap lower 95% bound > 1 under S0 at R = 20 km. The pre-registered threshold was 20%.

- Communities considered: 526 NSW UCLs (population ≥ 200).
- Failing eligibility: ring inside the polygon 4; fewer than 2 exits 56; fewer than 10 relevant fires 259. The criteria overlap.
- Eligible communities with a defined rho (≥ 1 observed isolation): 5 of 217.

This is a descriptive measurement. It is not a causal estimate and it says nothing about lives saved.

## Distributions (eligible communities, S0, R = 20 km)

- rho (defined values only): n = 5; min 7.33, Q1 7.33, median 8.00, Q3 8.00, max 9.33
- Bootstrap lower bound of rho: no defined values
- N_eff: n = 115; min 1.00, Q1 1.00, median 1.00, Q3 1.28, max 2.98
- Exits: n = 217; min 2.00, Q1 3.00, median 4.00, Q3 6.00, max 17.00
- Relevant fires per community: n = 217; min 10.00, Q1 13.00, median 18.00, Q3 30.00, max 65.00
- Relevant fires closing at least one exit: n = 217; min 0.00, Q1 0.00, median 1.00, Q3 1.00, max 3.00

Under S100 at R = 20 km: rho n = 7; min 7.20, Q1 7.33, median 8.00, Q3 8.67, max 100.00; N_eff n = 156; min 1.00, Q1 1.00, median 1.60, Q3 1.99, max 3.55.

## All eligible communities (S0, R = 20 km)

| Community | Pop. | Exits | Fires | Fires closing ≥1 exit | Isolations | P_obs | P_ind | rho [95% CI] | N_eff |
|---|---|---|---|---|---|---|---|---|---|
| Sussex Inlet | 3,659 | 2 | 13 | 1 | 1 | 0.107 | 0.011 | 9.33 [missing, 9.33] | 1.00 |
| Hallidays Point - West (L) | 500 | 2 | 11 | 1 | 1 | 0.125 | 0.016 | 8.00 [missing, 8.00] | 1.00 |
| Tallwoods Village (L) | 993 | 2 | 11 | 1 | 1 | 0.125 | 0.016 | 8.00 [missing, 8.00] | 1.00 |
| Berrara - Cudmirrah (L) | 612 | 2 | 10 | 1 | 1 | 0.136 | 0.019 | 7.33 [missing, 7.33] | 1.00 |
| Diamond Beach (L) | 1,012 | 2 | 10 | 1 | 1 | 0.136 | 0.019 | 7.33 [missing, 7.33] | 1.00 |
| Newcastle | 348,539 | 17 | 46 | 1 | 0 | 0.011 | 8.59e-34 | missing [missing, missing] | 1.00 |
| Coffs Harbour | 51,069 | 9 | 40 | 0 | 0 | 0.012 | 5.97e-18 | missing [missing, missing] | missing |
| Maitland (NSW) | 89,597 | 14 | 48 | 0 | 0 | 0.010 | 1.33e-28 | missing [missing, missing] | missing |
| Armidale | 21,312 | 8 | 12 | 0 | 0 | 0.038 | 4.79e-12 | missing [missing, missing] | missing |
| Bathurst | 36,230 | 11 | 14 | 0 | 0 | 0.033 | 5.65e-17 | missing [missing, missing] | missing |
| Blue Mountains | 30,049 | 3 | 37 | 1 | 0 | 0.013 | 6.83e-06 | missing [missing, missing] | 1.00 |
| Cessnock | 23,211 | 8 | 34 | 0 | 0 | 0.014 | 1.73e-15 | missing [missing, missing] | missing |
| Dubbo | 38,783 | 10 | 15 | 1 | 0 | 0.031 | 2.66e-15 | missing [missing, missing] | 1.00 |
| Forster - Tuncurry | 20,554 | 2 | 12 | 1 | 0 | 0.038 | 4.44e-03 | missing [missing, missing] | 1.00 |
| Griffith | 20,799 | 15 | 12 | 1 | 0 | 0.038 | 1.79e-21 | missing [missing, missing] | 1.00 |
| Kurri Kurri | 20,015 | 11 | 36 | 1 | 0 | 0.014 | 8.23e-21 | missing [missing, missing] | 1.00 |
| Lismore (NSW) | 27,916 | 11 | 13 | 0 | 0 | 0.036 | 1.21e-16 | missing [missing, missing] | missing |
| Morisset - Cooranbong | 22,150 | 9 | 28 | 0 | 0 | 0.017 | 1.35e-16 | missing [missing, missing] | missing |
| Nowra - Bomaderry | 33,583 | 9 | 16 | 1 | 0 | 0.029 | 4.45e-13 | missing [missing, missing] | 1.00 |
| Port Macquarie | 47,793 | 4 | 28 | 1 | 0 | 0.017 | 2.39e-06 | missing [missing, missing] | 1.00 |
| Tamworth | 35,415 | 10 | 12 | 0 | 0 | 0.038 | 7.08e-15 | missing [missing, missing] | missing |
| Grafton | 17,155 | 9 | 58 | 1 | 0 | 8.47e-03 | 6.76e-19 | missing [missing, missing] | 1.00 |
| Kempsey | 11,073 | 9 | 30 | 3 | 0 | 0.016 | 1.66e-14 | missing [missing, missing] | 1.55 |
| Medowie | 10,019 | 3 | 29 | 0 | 0 | 0.017 | 4.63e-06 | missing [missing, missing] | missing |
| Mudgee | 11,563 | 8 | 10 | 0 | 0 | 0.045 | 1.82e-11 | missing [missing, missing] | missing |
| Raymond Terrace | 14,081 | 8 | 36 | 0 | 0 | 0.014 | 1.11e-15 | missing [missing, missing] | missing |
| Singleton | 14,229 | 6 | 17 | 1 | 0 | 0.028 | 1.38e-09 | missing [missing, missing] | 1.00 |
| St Georges Basin - Sanctuary Point | 11,000 | 4 | 13 | 1 | 0 | 0.036 | 1.46e-05 | missing [missing, missing] | 1.00 |
| Taree | 18,110 | 7 | 16 | 2 | 0 | 0.029 | 1.54e-09 | missing [missing, missing] | 1.99 |
| Camden Haven | 8,037 | 3 | 25 | 3 | 0 | 0.019 | 1.07e-04 | missing [missing, missing] | 1.99 |
| Casino | 9,968 | 8 | 15 | 2 | 0 | 0.031 | 8.19e-12 | missing [missing, missing] | 1.99 |
| Helensburgh | 6,304 | 3 | 18 | 0 | 0 | 0.026 | 1.82e-05 | missing [missing, missing] | missing |
| Inverell | 9,654 | 8 | 17 | 0 | 0 | 0.028 | 3.54e-13 | missing [missing, missing] | missing |
| Leeton | 7,437 | 12 | 20 | 1 | 0 | 0.024 | 9.96e-20 | missing [missing, missing] | 1.00 |
| Murwillumbah | 9,812 | 10 | 10 | 1 | 0 | 0.045 | 1.13e-13 | missing [missing, missing] | 1.00 |
| Nambucca Heads | 6,668 | 3 | 18 | 0 | 0 | 0.026 | 1.82e-05 | missing [missing, missing] | missing |
| Richmond North | 5,467 | 4 | 53 | 1 | 0 | 9.26e-03 | 2.21e-08 | missing [missing, missing] | 1.00 |
| Silverdale - Warragamba | 5,364 | 2 | 65 | 1 | 0 | 7.58e-03 | 1.72e-04 | missing [missing, missing] | 1.00 |
| Wauchope | 7,982 | 5 | 33 | 1 | 0 | 0.015 | 2.06e-09 | missing [missing, missing] | 1.00 |
| Woolgoolga | 5,797 | 7 | 39 | 2 | 0 | 0.013 | 4.29e-13 | missing [missing, missing] | 2.00 |
| Appin | 2,869 | 3 | 20 | 0 | 0 | 0.024 | 1.35e-05 | missing [missing, missing] | missing |
| Arrawarra | 1,820 | 6 | 41 | 1 | 0 | 0.012 | 8.54e-12 | missing [missing, missing] | 1.00 |
| Basin View | 1,583 | 4 | 13 | 1 | 0 | 0.036 | 1.46e-05 | missing [missing, missing] | 1.00 |
| Bellingen | 3,201 | 5 | 31 | 1 | 0 | 0.016 | 2.79e-09 | missing [missing, missing] | 1.00 |
| Berry | 2,467 | 6 | 10 | 1 | 0 | 0.045 | 2.65e-08 | missing [missing, missing] | 1.00 |
| Blackheath | 4,479 | 3 | 17 | 1 | 0 | 0.028 | 6.43e-05 | missing [missing, missing] | 1.00 |
| Blayney | 2,997 | 7 | 10 | 0 | 0 | 0.045 | 4.01e-10 | missing [missing, missing] | missing |
| Bonny Hills | 2,825 | 2 | 21 | 2 | 0 | 0.023 | 4.65e-03 | missing [missing, missing] | 2.00 |
| Branxton | 2,878 | 5 | 29 | 2 | 0 | 0.017 | 1.16e-08 | missing [missing, missing] | 2.00 |
| Bulahdelah | 1,163 | 4 | 14 | 0 | 0 | 0.033 | 1.23e-06 | missing [missing, missing] | missing |
| Calala | 3,930 | 3 | 10 | 0 | 0 | 0.045 | 9.39e-05 | missing [missing, missing] | missing |
| Callala Bay | 3,076 | 2 | 15 | 1 | 0 | 0.031 | 2.93e-03 | missing [missing, missing] | 1.00 |
| Cambewarra Village | 1,211 | 4 | 15 | 1 | 0 | 0.031 | 2.86e-06 | missing [missing, missing] | 1.00 |
| Coraki | 1,155 | 5 | 14 | 1 | 0 | 0.033 | 3.70e-07 | missing [missing, missing] | 1.00 |
| Corindi Beach | 1,649 | 2 | 37 | 0 | 0 | 0.013 | 1.73e-04 | missing [missing, missing] | missing |
| Culcairn | 1,112 | 6 | 10 | 0 | 0 | 0.045 | 8.82e-09 | missing [missing, missing] | missing |
| Dorrigo | 1,046 | 4 | 26 | 2 | 0 | 0.019 | 1.06e-06 | missing [missing, missing] | 2.00 |
| Douglas Park | 1,092 | 8 | 18 | 1 | 0 | 0.026 | 6.90e-13 | missing [missing, missing] | 1.00 |
| Dungog | 2,169 | 4 | 16 | 0 | 0 | 0.029 | 7.48e-07 | missing [missing, missing] | missing |
| Evans Head | 2,894 | 2 | 10 | 0 | 0 | 0.045 | 2.07e-03 | missing [missing, missing] | missing |
| Frederickton | 1,195 | 7 | 28 | 3 | 0 | 0.017 | 6.79e-12 | missing [missing, missing] | 1.99 |
| Freemans Reach | 1,343 | 5 | 51 | 1 | 0 | 9.62e-03 | 7.40e-10 | missing [missing, missing] | 1.00 |
| Galston | 1,175 | 4 | 53 | 0 | 0 | 9.26e-03 | 7.35e-09 | missing [missing, missing] | missing |
| Glossodia | 2,548 | 5 | 44 | 1 | 0 | 0.011 | 1.52e-09 | missing [missing, missing] | 1.00 |
| Gloucester | 2,469 | 3 | 12 | 0 | 0 | 0.038 | 5.69e-05 | missing [missing, missing] | missing |
| Grenfell | 2,022 | 7 | 10 | 1 | 0 | 0.045 | 1.20e-09 | missing [missing, missing] | 1.00 |
| Greta | 3,230 | 5 | 30 | 2 | 0 | 0.016 | 9.82e-09 | missing [missing, missing] | 2.00 |
| Gulmarrad | 1,844 | 3 | 19 | 2 | 0 | 0.025 | 1.41e-04 | missing [missing, missing] | 1.99 |
| Harrington | 3,240 | 2 | 17 | 2 | 0 | 0.028 | 3.86e-03 | missing [missing, missing] | 1.00 |
| Hawks Nest | 1,413 | 2 | 18 | 0 | 0 | 0.026 | 6.93e-04 | missing [missing, missing] | missing |
| Junction Hill | 1,515 | 3 | 49 | 0 | 0 | 0.010 | 1.00e-06 | missing [missing, missing] | missing |
| Karuah | 1,451 | 2 | 24 | 0 | 0 | 0.020 | 4.00e-04 | missing [missing, missing] | missing |
| Kootingal | 1,862 | 6 | 12 | 0 | 0 | 0.038 | 3.24e-09 | missing [missing, missing] | missing |
| Kurrajong | 1,159 | 4 | 46 | 1 | 0 | 0.011 | 3.84e-08 | missing [missing, missing] | 1.00 |
| Kyogle | 2,804 | 6 | 15 | 0 | 0 | 0.031 | 9.31e-10 | missing [missing, missing] | missing |
| Lake Cathie | 4,049 | 3 | 23 | 2 | 0 | 0.021 | 2.44e-04 | missing [missing, missing] | 1.80 |
| Macksville | 3,023 | 6 | 17 | 1 | 0 | 0.028 | 1.38e-09 | missing [missing, missing] | 1.00 |
| Maclean | 2,711 | 4 | 18 | 2 | 0 | 0.026 | 4.32e-06 | missing [missing, missing] | 1.99 |
| Narromine | 3,507 | 10 | 11 | 1 | 0 | 0.042 | 4.73e-14 | missing [missing, missing] | 1.00 |
| North Rothbury | 2,283 | 7 | 29 | 0 | 0 | 0.017 | 3.57e-13 | missing [missing, missing] | missing |
| Old Erowal Bay | 1,719 | 2 | 13 | 1 | 0 | 0.036 | 3.83e-03 | missing [missing, missing] | 1.00 |
| Picton | 3,847 | 6 | 12 | 1 | 0 | 0.038 | 8.74e-08 | missing [missing, missing] | 1.00 |
| Pitt Town | 3,325 | 4 | 49 | 0 | 0 | 0.010 | 1.00e-08 | missing [missing, missing] | missing |
| Portland (NSW) | 1,841 | 4 | 10 | 1 | 0 | 0.045 | 3.84e-05 | missing [missing, missing] | 1.00 |
| Quirindi | 2,602 | 7 | 17 | 0 | 0 | 0.028 | 1.28e-11 | missing [missing, missing] | missing |
| Sandy Beach - Emerald Beach | 4,459 | 6 | 39 | 1 | 0 | 0.013 | 1.14e-11 | missing [missing, missing] | 1.00 |
| Shoalhaven Heads | 3,264 | 2 | 13 | 0 | 0 | 0.036 | 1.28e-03 | missing [missing, missing] | missing |
| Smiths Lake | 1,332 | 2 | 10 | 1 | 0 | 0.045 | 6.20e-03 | missing [missing, missing] | 1.00 |
| Stanwell Park | 1,713 | 2 | 17 | 1 | 0 | 0.028 | 2.31e-03 | missing [missing, missing] | 1.00 |
| Tea Gardens | 2,837 | 2 | 19 | 0 | 0 | 0.025 | 6.25e-04 | missing [missing, missing] | missing |
| Tenterfield | 2,826 | 6 | 21 | 1 | 0 | 0.023 | 1.24e-09 | missing [missing, missing] | 1.00 |
| The Oaks | 2,171 | 4 | 17 | 1 | 0 | 0.028 | 1.61e-05 | missing [missing, missing] | 1.00 |
| Thrumster | 2,115 | 6 | 27 | 1 | 0 | 0.018 | 2.92e-10 | missing [missing, missing] | 1.00 |
| Uralla | 2,385 | 7 | 11 | 0 | 0 | 0.042 | 2.18e-10 | missing [missing, missing] | missing |
| Urunga | 2,731 | 6 | 28 | 0 | 0 | 0.017 | 2.63e-11 | missing [missing, missing] | missing |
| Vincentia | 2,705 | 2 | 14 | 1 | 0 | 0.033 | 3.33e-03 | missing [missing, missing] | 1.00 |
| Vincentia West | 1,162 | 3 | 13 | 1 | 0 | 0.036 | 1.37e-04 | missing [missing, missing] | 1.00 |
| Wallacia | 1,081 | 4 | 64 | 1 | 0 | 7.69e-03 | 1.05e-08 | missing [missing, missing] | 1.00 |
| Werris Creek | 1,349 | 4 | 17 | 0 | 0 | 0.028 | 5.95e-07 | missing [missing, missing] | missing |
| Wilberforce | 1,817 | 5 | 43 | 1 | 0 | 0.011 | 1.71e-09 | missing [missing, missing] | 1.00 |
| Wilton | 2,959 | 4 | 10 | 0 | 0 | 0.045 | 4.27e-06 | missing [missing, missing] | missing |
| Wingham | 4,556 | 5 | 13 | 2 | 0 | 0.036 | 4.71e-06 | missing [missing, missing] | 1.59 |
| Wyee | 1,980 | 4 | 18 | 0 | 0 | 0.026 | 4.80e-07 | missing [missing, missing] | missing |
| Wyee Point | 1,352 | 2 | 20 | 0 | 0 | 0.024 | 5.67e-04 | missing [missing, missing] | missing |
| Yenda | 1,070 | 9 | 12 | 0 | 0 | 0.038 | 1.84e-13 | missing [missing, missing] | missing |
| Beechwood (L) | 914 | 6 | 32 | 2 | 0 | 0.015 | 1.09e-10 | missing [missing, missing] | 2.00 |
| Belimbla Park (L) | 576 | 2 | 16 | 1 | 0 | 0.029 | 2.60e-03 | missing [missing, missing] | 1.00 |
| Boomerang Beach - Blueys Beach (L) | 668 | 2 | 10 | 1 | 0 | 0.045 | 6.20e-03 | missing [missing, missing] | 1.00 |
| Bowraville (L) | 941 | 4 | 19 | 1 | 0 | 0.025 | 1.05e-05 | missing [missing, missing] | 1.00 |
| Brandy Hill (L) | 852 | 3 | 36 | 0 | 0 | 0.014 | 2.47e-06 | missing [missing, missing] | missing |
| Burringbar (L) | 555 | 3 | 10 | 0 | 0 | 0.045 | 9.39e-05 | missing [missing, missing] | missing |
| Catherine Hill Bay (L) | 820 | 2 | 13 | 0 | 0 | 0.036 | 1.28e-03 | missing [missing, missing] | missing |
| Clarence Town (L) | 878 | 4 | 24 | 0 | 0 | 0.020 | 1.60e-07 | missing [missing, missing] | missing |
| Coleambally (L) | 566 | 5 | 11 | 1 | 0 | 0.042 | 3.77e-07 | missing [missing, missing] | 1.00 |
| Coutts Crossing (L) | 553 | 5 | 48 | 2 | 0 | 0.010 | 2.99e-09 | missing [missing, missing] | 1.80 |
| Cowan (L) | 599 | 2 | 24 | 0 | 0 | 0.020 | 4.00e-04 | missing [missing, missing] | missing |
| Crescent Head (L) | 978 | 2 | 26 | 1 | 0 | 0.019 | 1.03e-03 | missing [missing, missing] | 1.00 |
| Darlington Point (L) | 868 | 4 | 21 | 2 | 0 | 0.023 | 1.33e-06 | missing [missing, missing] | 1.00 |
| Ellalong (L) | 1,125 | 3 | 29 | 1 | 0 | 0.017 | 1.39e-05 | missing [missing, missing] | 1.00 |
| Emerald Beach West (L) | 1,427 | 6 | 37 | 1 | 0 | 0.013 | 1.56e-11 | missing [missing, missing] | 1.00 |
| Firgrove (L) | 511 | 4 | 10 | 0 | 0 | 0.045 | 4.27e-06 | missing [missing, missing] | missing |
| Glenorie (L) | 684 | 3 | 55 | 0 | 0 | 8.93e-03 | 7.12e-07 | missing [missing, missing] | missing |
| Glenreagh (L) | 562 | 4 | 45 | 3 | 0 | 0.011 | 1.13e-06 | missing [missing, missing] | 2.66 |
| Hanwood (L) | 641 | 5 | 14 | 0 | 0 | 0.033 | 4.12e-08 | missing [missing, missing] | missing |
| Henty (L) | 940 | 8 | 11 | 0 | 0 | 0.042 | 9.08e-12 | missing [missing, missing] | missing |
| Huskisson (L) | 825 | 3 | 14 | 1 | 0 | 0.033 | 3.33e-04 | missing [missing, missing] | 1.00 |
| Jilliby (L) | 777 | 8 | 19 | 0 | 0 | 0.025 | 1.53e-13 | missing [missing, missing] | missing |
| Kendall (L) | 890 | 3 | 24 | 1 | 0 | 0.020 | 2.40e-05 | missing [missing, missing] | 1.00 |
| King Creek (L) | 1,863 | 4 | 32 | 0 | 0 | 0.015 | 5.27e-08 | missing [missing, missing] | missing |
| Kingswood (L) | 980 | 2 | 11 | 0 | 0 | 0.042 | 1.74e-03 | missing [missing, missing] | missing |
| Kitchener (L) | 554 | 3 | 31 | 0 | 0 | 0.016 | 3.81e-06 | missing [missing, missing] | missing |
| Kurrajong Heights (L) | 905 | 2 | 30 | 1 | 0 | 0.016 | 7.80e-04 | missing [missing, missing] | 1.00 |
| Lawrence (L) | 925 | 2 | 30 | 1 | 0 | 0.016 | 7.80e-04 | missing [missing, missing] | 1.00 |
| Lochinvar (L) | 508 | 4 | 30 | 0 | 0 | 0.016 | 6.77e-08 | missing [missing, missing] | missing |
| Louth Park (L) | 767 | 3 | 30 | 0 | 0 | 0.016 | 4.20e-06 | missing [missing, missing] | missing |
| Medlow Bath (L) | 556 | 2 | 15 | 1 | 0 | 0.031 | 2.93e-03 | missing [missing, missing] | 1.00 |
| Menangle (L) | 656 | 4 | 25 | 0 | 0 | 0.019 | 1.37e-07 | missing [missing, missing] | missing |
| Millfield (L) | 1,071 | 4 | 28 | 0 | 0 | 0.017 | 8.84e-08 | missing [missing, missing] | missing |
| Millthorpe (L) | 750 | 5 | 10 | 0 | 0 | 0.045 | 1.94e-07 | missing [missing, missing] | missing |
| Minmi (L) | 686 | 12 | 26 | 0 | 0 | 0.019 | 1.63e-21 | missing [missing, missing] | missing |
| Moonee Beach (L) | 996 | 4 | 35 | 0 | 0 | 0.014 | 3.72e-08 | missing [missing, missing] | missing |
| Moonee Beach West (L) | 583 | 8 | 40 | 2 | 0 | 0.012 | 4.40e-15 | missing [missing, missing] | 2.00 |
| Mount Victoria (L) | 913 | 3 | 14 | 1 | 0 | 0.033 | 1.00e-03 | missing [missing, missing] | 1.00 |
| Mulgoa (L) | 844 | 4 | 63 | 1 | 0 | 7.81e-03 | 1.12e-08 | missing [missing, missing] | 1.00 |
| Murrays Beach (L) | 1,022 | 2 | 15 | 0 | 0 | 0.031 | 9.77e-04 | missing [missing, missing] | missing |
| Nabiac (L) | 656 | 5 | 16 | 2 | 0 | 0.029 | 5.94e-07 | missing [missing, missing] | 1.79 |
| Nords Wharf (L) | 895 | 3 | 15 | 0 | 0 | 0.031 | 3.05e-05 | missing [missing, missing] | missing |
| Nowra Hill (L) | 828 | 3 | 15 | 1 | 0 | 0.031 | 9.16e-05 | missing [missing, missing] | 1.00 |
| Nunderi (L) | 696 | 4 | 10 | 0 | 0 | 0.045 | 4.27e-06 | missing [missing, missing] | missing |
| Oakdale (L) | 1,179 | 2 | 12 | 0 | 0 | 0.038 | 1.48e-03 | missing [missing, missing] | missing |
| Paxton (L) | 1,160 | 3 | 29 | 1 | 0 | 0.017 | 1.39e-05 | missing [missing, missing] | 1.00 |
| Putta Bucca - Bombira (L) | 693 | 6 | 10 | 0 | 0 | 0.045 | 8.82e-09 | missing [missing, missing] | missing |
| Repton (L) | 667 | 5 | 29 | 0 | 0 | 0.017 | 1.29e-09 | missing [missing, missing] | missing |
| Safety Beach (L) | 1,103 | 2 | 38 | 0 | 0 | 0.013 | 1.64e-04 | missing [missing, missing] | missing |
| Salt Ash (L) | 1,103 | 4 | 25 | 0 | 0 | 0.019 | 1.37e-07 | missing [missing, missing] | missing |
| Smithtown - Gladstone (L) | 1,021 | 4 | 28 | 1 | 0 | 0.017 | 2.65e-07 | missing [missing, missing] | 1.00 |
| Stroud (L) | 738 | 4 | 16 | 0 | 0 | 0.029 | 7.48e-07 | missing [missing, missing] | missing |
| Tinonee (L) | 840 | 3 | 10 | 1 | 0 | 0.045 | 2.82e-04 | missing [missing, missing] | 1.00 |
| Townsend (L) | 991 | 3 | 17 | 1 | 0 | 0.028 | 6.43e-05 | missing [missing, missing] | 1.00 |
| Walla Walla (L) | 532 | 5 | 11 | 0 | 0 | 0.042 | 1.26e-07 | missing [missing, missing] | missing |
| Wallalong (L) | 963 | 3 | 35 | 0 | 0 | 0.014 | 2.68e-06 | missing [missing, missing] | missing |
| Waterfall (L) | 518 | 5 | 19 | 1 | 0 | 0.025 | 8.79e-08 | missing [missing, missing] | 1.00 |
| Waterview Heights (L) | 872 | 3 | 39 | 2 | 0 | 0.013 | 1.76e-05 | missing [missing, missing] | 2.00 |
| Wongarbon (L) | 665 | 5 | 10 | 0 | 0 | 0.045 | 1.94e-07 | missing [missing, missing] | missing |
| Woodburn (L) | 678 | 6 | 11 | 1 | 0 | 0.042 | 1.57e-08 | missing [missing, missing] | 1.00 |
| Wooroowoolgan (L) | 593 | 2 | 14 | 0 | 0 | 0.033 | 1.11e-03 | missing [missing, missing] | missing |
| Abernethy (L) | 255 | 2 | 30 | 0 | 0 | 0.016 | 2.60e-04 | missing [missing, missing] | missing |
| Agnes Banks (L) | 410 | 5 | 57 | 0 | 0 | 8.62e-03 | 4.76e-11 | missing [missing, missing] | missing |
| Awaba (L) | 362 | 3 | 23 | 1 | 0 | 0.021 | 2.71e-05 | missing [missing, missing] | 1.00 |
| Bilbul (L) | 251 | 6 | 12 | 0 | 0 | 0.038 | 3.24e-09 | missing [missing, missing] | missing |
| Bonalbo (L) | 278 | 2 | 14 | 0 | 0 | 0.033 | 1.11e-03 | missing [missing, missing] | missing |
| Bonville - East (L) | 476 | 7 | 30 | 1 | 0 | 0.016 | 8.52e-13 | missing [missing, missing] | 1.00 |
| Broke (L) | 231 | 4 | 21 | 1 | 0 | 0.023 | 8.00e-07 | missing [missing, missing] | 1.00 |
| Bundarra (L) | 374 | 4 | 14 | 0 | 0 | 0.033 | 1.23e-06 | missing [missing, missing] | missing |
| Caniaba (L) | 438 | 2 | 11 | 0 | 0 | 0.042 | 1.74e-03 | missing [missing, missing] | missing |
| Coopernook (L) | 430 | 3 | 18 | 3 | 0 | 0.026 | 4.92e-04 | missing [missing, missing] | 2.98 |
| Copmanhurst (L) | 240 | 2 | 33 | 0 | 0 | 0.015 | 2.16e-04 | missing [missing, missing] | missing |
| Coramba (L) | 389 | 3 | 35 | 2 | 0 | 0.014 | 2.41e-05 | missing [missing, missing] | 2.00 |
| Deepwater (L) | 315 | 4 | 14 | 1 | 0 | 0.033 | 3.70e-06 | missing [missing, missing] | 1.00 |
| Elizabeth Beach (L) | 268 | 2 | 10 | 2 | 0 | 0.045 | 0.019 | missing [missing, missing] | 1.98 |
| Fairy Hill (L) | 302 | 3 | 13 | 0 | 0 | 0.036 | 4.56e-05 | missing [missing, missing] | missing |
| Falls Creek (L) (NSW) | 258 | 4 | 15 | 1 | 0 | 0.031 | 2.86e-06 | missing [missing, missing] | 1.00 |
| Gilgai (L) | 399 | 5 | 17 | 0 | 0 | 0.028 | 1.65e-08 | missing [missing, missing] | missing |
| Gresford (L) | 307 | 4 | 14 | 0 | 0 | 0.033 | 1.23e-06 | missing [missing, missing] | missing |
| Hinton (L) | 374 | 3 | 37 | 0 | 0 | 0.013 | 2.28e-06 | missing [missing, missing] | missing |
| Kenthurst (L) | 436 | 2 | 56 | 0 | 0 | 8.77e-03 | 7.69e-05 | missing [missing, missing] | missing |
| Kew (L) | 363 | 4 | 23 | 2 | 0 | 0.021 | 1.70e-06 | missing [missing, missing] | 2.00 |
| Kurmond (L) | 273 | 3 | 46 | 1 | 0 | 0.011 | 3.61e-06 | missing [missing, missing] | 1.00 |
| Lansdowne (L) | 352 | 3 | 19 | 2 | 0 | 0.025 | 1.41e-04 | missing [missing, missing] | 1.99 |
| Linden (L) | 273 | 2 | 32 | 0 | 0 | 0.015 | 2.30e-04 | missing [missing, missing] | missing |
| Luddenham (L) | 456 | 4 | 65 | 0 | 0 | 7.58e-03 | 3.29e-09 | missing [missing, missing] | missing |
| Menangle Park (L) | 207 | 2 | 29 | 0 | 0 | 0.017 | 2.78e-04 | missing [missing, missing] | missing |
| Moonbi (L) | 454 | 5 | 11 | 0 | 0 | 0.042 | 1.26e-07 | missing [missing, missing] | missing |
| Mooney Mooney (L) | 448 | 6 | 26 | 0 | 0 | 0.019 | 4.03e-11 | missing [missing, missing] | missing |
| Mulbring (L) | 366 | 4 | 30 | 1 | 0 | 0.016 | 2.03e-07 | missing [missing, missing] | 1.00 |
| Nana Glen (L) | 233 | 4 | 47 | 2 | 0 | 0.010 | 1.06e-07 | missing [missing, missing] | 2.00 |
| Otford (L) | 321 | 3 | 16 | 1 | 0 | 0.029 | 2.29e-04 | missing [missing, missing] | 1.00 |
| Paterson (L) | 345 | 2 | 29 | 0 | 0 | 0.017 | 2.78e-04 | missing [missing, missing] | missing |
| Perthville (L) | 362 | 4 | 10 | 0 | 0 | 0.045 | 4.27e-06 | missing [missing, missing] | missing |
| Seaham (L) | 433 | 4 | 30 | 0 | 0 | 0.016 | 6.77e-08 | missing [missing, missing] | missing |
| Seahampton (L) | 292 | 10 | 31 | 0 | 0 | 0.016 | 8.67e-19 | missing [missing, missing] | missing |
| Stanwell Tops (L) | 483 | 2 | 16 | 1 | 0 | 0.029 | 2.60e-03 | missing [missing, missing] | 1.00 |
| Tapitallee (L) | 409 | 3 | 15 | 1 | 0 | 0.031 | 9.16e-05 | missing [missing, missing] | 1.00 |
| Telegraph Point (L) | 210 | 5 | 29 | 1 | 0 | 0.017 | 1.16e-08 | missing [missing, missing] | 1.00 |
| Tingha (L) | 445 | 4 | 18 | 1 | 0 | 0.026 | 1.44e-06 | missing [missing, missing] | 1.00 |
| Tomago (L) | 269 | 5 | 36 | 0 | 0 | 0.014 | 4.51e-10 | missing [missing, missing] | missing |
| Tomerong (L) | 388 | 3 | 14 | 1 | 0 | 0.033 | 1.11e-04 | missing [missing, missing] | 1.00 |
| Tucabia (L) | 253 | 3 | 41 | 0 | 0 | 0.012 | 1.69e-06 | missing [missing, missing] | missing |
| Tumbulgum (L) | 382 | 2 | 10 | 0 | 0 | 0.045 | 2.07e-03 | missing [missing, missing] | missing |
| Uki (L) | 211 | 3 | 10 | 0 | 0 | 0.045 | 9.39e-05 | missing [missing, missing] | missing |
| Ulmarra (L) | 418 | 4 | 43 | 0 | 0 | 0.011 | 1.67e-08 | missing [missing, missing] | missing |
| Urbenville (L) | 218 | 4 | 15 | 2 | 0 | 0.031 | 2.57e-05 | missing [missing, missing] | 1.79 |
| Wallabadah (L) | 216 | 4 | 18 | 0 | 0 | 0.026 | 4.80e-07 | missing [missing, missing] | missing |
| Whitton (L) | 346 | 5 | 25 | 3 | 0 | 0.019 | 3.95e-08 | missing [missing, missing] | 1.99 |
| Woodenbong (L) | 285 | 4 | 17 | 2 | 0 | 0.028 | 4.82e-05 | missing [missing, missing] | 1.60 |
| Woollamia (L) | 371 | 3 | 15 | 1 | 0 | 0.031 | 2.75e-04 | missing [missing, missing] | 1.00 |
| Yanco (L) | 432 | 5 | 18 | 0 | 0 | 0.026 | 1.26e-08 | missing [missing, missing] | missing |

## Largest exits − N_eff gaps (S0, R = 20 km)

N_eff counts only exits that closed in at least one relevant fire and not in every fire. The gap
therefore includes exits that never closed (they are excluded from N_eff, not counted as independent).

| Community | Population | Exits | N_eff | Exits − N_eff | Excluded (never/always closed) | Relevant fires | Isolations | rho [95% CI] |
|---|---|---|---|---|---|---|---|---|
| Newcastle | 348,539 | 17 | 1.00 | 16.00 | 16/0 | 46 | 0 | missing [missing, missing] |
| Griffith | 20,799 | 15 | 1.00 | 14.00 | 14/0 | 12 | 0 | missing [missing, missing] |
| Leeton | 7,437 | 12 | 1.00 | 11.00 | 11/0 | 20 | 0 | missing [missing, missing] |
| Kurri Kurri | 20,015 | 11 | 1.00 | 10.00 | 10/0 | 36 | 0 | missing [missing, missing] |
| Dubbo | 38,783 | 10 | 1.00 | 9.00 | 9/0 | 15 | 0 | missing [missing, missing] |
| Narromine | 3,507 | 10 | 1.00 | 9.00 | 9/0 | 11 | 0 | missing [missing, missing] |
| Murwillumbah | 9,812 | 10 | 1.00 | 9.00 | 9/0 | 10 | 0 | missing [missing, missing] |
| Nowra - Bomaderry | 33,583 | 9 | 1.00 | 8.00 | 6/0 | 16 | 0 | missing [missing, missing] |
| Grafton | 17,155 | 9 | 1.00 | 8.00 | 8/0 | 58 | 0 | missing [missing, missing] |
| Kempsey | 11,073 | 9 | 1.55 | 7.45 | 5/0 | 30 | 0 | missing [missing, missing] |

## Sensitivity: ring radius and exposure rule

| Rule | Ring R | Communities | Ring inside polygon | Exits ≥ 2 | Fires ≥ 10 | Eligible | rho defined | rho > 5 & lower > 1 | Share |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| S0 | 10 km | 526 | 9 | 465 | 267 | 217 | 5 | 0 | 0.0% |
| S0 (primary) | 20 km | 526 | 4 | 466 | 267 | 217 | 5 | 0 | 0.0% |
| S0 | 30 km | 526 | 2 | 466 | 267 | 217 | 5 | 0 | 0.0% |
| S100 | 10 km | 526 | 9 | 465 | 267 | 217 | 8 | 0 | 0.0% |
| S100 | 20 km | 526 | 4 | 466 | 267 | 217 | 7 | 0 | 0.0% |
| S100 | 30 km | 526 | 2 | 466 | 267 | 217 | 7 | 0 | 0.0% |

Only S0 at R = 20 km determines the verdict. The other rows are sensitivity analyses.

## Why no community could meet the rule (descriptive; not pre-registered)

The highest number of isolating fires in any eligible community under S0 at R = 20 km was
1. When a community has exactly one isolating fire among n, a bootstrap
resample leaves that fire out with probability (1 − 1/n)^n, which is about 35% for n = 10 to 20.
Resamples without it have undefined rho, so the 2.5th percentile is undefined and the lower bound
cannot exceed 1. Under this rule a community needs roughly four or more isolating fires before the
lower bound can clear 1. Four seasons of mapped fires (2019-20 to 2022-23) never produce that.

The FAIL therefore reflects too few joint-failure events for the pre-registered test, as well as
what those events show. It is not evidence that exits fail independently. The rule was not changed.

## Observed isolations outside the eligible set (descriptive; not pre-registered)

Communities with at least one S0 isolation at R = 20 km that failed eligibility. They are reported
for context only and play no part in the verdict.

| Community | Pop. | Exits | Relevant fires | Isolations | Why ineligible |
|---|---|---|---|---|---|
| Ulladulla | 14,396 | 3 | 7 | 1 | fires < 10 |
| Batemans Bay | 12,263 | 5 | 3 | 1 | fires < 10 |
| Old Bar | 4,485 | 1 | 14 | 1 | exits < 2 |
| Moruya | 2,762 | 4 | 4 | 1 | fires < 10 |
| Malua Bay | 2,372 | 3 | 3 | 1 | fires < 10 |
| Long Beach - Maloneys Beach (L) | 2,231 | 1 | 3 | 1 | exits < 2; fires < 10 |
| Iluka | 1,764 | 1 | 14 | 1 | exits < 2 |
| Buxton (NSW) | 1,741 | 3 | 4 | 1 | fires < 10 |
| Milton | 1,538 | 3 | 6 | 1 | fires < 10 |
| Moruya Heads (L) | 1,125 | 1 | 4 | 1 | exits < 2; fires < 10 |
| Hallidays Point - Black Head | 1,106 | 2 | 9 | 1 | fires < 10 |
| Batlow | 1,022 | 3 | 4 | 1 | fires < 10 |
| Wallabi Point (L) | 884 | 1 | 12 | 1 | exits < 2 |
| Red Head (L) | 798 | 2 | 9 | 1 | fires < 10 |
| Cunjurong Point - Manyana (L) | 785 | 1 | 9 | 1 | exits < 2; fires < 10 |
| Bawley Point (L) | 716 | 2 | 3 | 1 | fires < 10 |
| Lake Tabourie (L) | 670 | 2 | 2 | 1 | fires < 10 |
| Lake Conjola (L) | 656 | 1 | 9 | 1 | exits < 2; fires < 10 |
| Kings Point (L) | 609 | 1 | 3 | 1 | exits < 2; fires < 10 |
| Wooli (L) | 503 | 1 | 30 | 1 | exits < 2 |
| Fishermans Paradise (L) | 491 | 1 | 10 | 1 | exits < 2 |
| Wooloweyah (L) | 419 | 1 | 15 | 1 | exits < 2 |
| Cobargo (L) | 417 | 4 | 3 | 1 | fires < 10 |
| Balmoral (L) | 365 | 2 | 5 | 1 | fires < 10 |
| South Durras (L) | 319 | 1 | 3 | 1 | exits < 2; fires < 10 |
| Conjola Park (L) | 291 | 1 | 9 | 1 | exits < 2; fires < 10 |
| Kioloa (L) | 284 | 2 | 3 | 1 | fires < 10 |
| Rosedale - Guerilla Bay (L) | 283 | 3 | 3 | 1 | fires < 10 |
| Mogo (L) | 249 | 4 | 3 | 1 | fires < 10 |
| Brooms Head (L) | 248 | 1 | 23 | 1 | exits < 2 |
| Nelligen (L) | 245 | 4 | 2 | 1 | fires < 10 |
| Manning Point (L) | 228 | 1 | 15 | 1 | exits < 2 |
| Talbingo (L) | 212 | 1 | 4 | 1 | exits < 2; fires < 10 |

## Maps

- `out/map_rho_S0_R20.png`: communities coloured by log10 rho.
- `out/map_exits_vs_neff_S0_R20.png`: exits against N_eff.

## Required caveats

- **rho is an upper bound.** Final fire perimeters assume every road inside closed at the same moment, which overstates simultaneous failure. A later stage will use daily satellite fire progression to test timing.
- **Closure is inferred** from mapped footprints (the direct intersection S0 or the 100 m buffer S100), not from observed road-closure records.
- **Fires are not independent replications.** Fire events affecting the same community share weather, terrain and season. The bootstrap over fires treats them as exchangeable, so the intervals are optimistic.

## Other limitations

- Fire footprints are Geoscience Australia perimeters grouped into fire families (events within 3 days and 5 km). They cover only four seasons, 2019-20 to 2022-23, and are not FESM. A megafire complex counts as one event.
- The 2019 OSM network is treated as undirected, and `service` roads are excluded. Fire trails and tracks are not in the network.
- Hashes for the network parquet and the transport DB were frozen on 2026-09-21. No earlier provenance record exists for them. The OSM PBF and the event perimeters match earlier manifests.
- Exit paths are one minimum-total-length decomposition. Decompositions are not unique, so p_j and N_eff depend on that choice. P_obs does not, because isolation is tested on the whole graph.
- rho is missing, not zero, when a community had no observed isolation. With few fires per community the Jeffreys-smoothed probabilities remain coarse.
- P_ind multiplies across all exits, so communities with many exits get very small P_ind. rho is reported on a log10 scale in the CSV for that reason.
- Relevant fires include families that touch no road. They count in n with no closures.
- Communities are 2021 UCL boundaries against a January 2019 road network.

## Run

Seed 20260921, 1000 bootstrap resamples, runtime 931.8 s, run at 2026-09-21T12:40:52+00:00.
The network had 1,214,545 of 1,451,892 edges after excluding service roads and self-loops.
2,866 overlay rows on service roads were ignored.
`aussef.duckdb` SHA-256 was unchanged before and after the run: `ce294c7ef50964b334a13d83b627f0732e35d2237c70ddf7ce3a26b06f1cba59`.
