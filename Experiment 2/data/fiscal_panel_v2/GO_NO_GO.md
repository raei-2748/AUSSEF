# Decision: NO-GO for an immediate predictive rerun

The historical extension provides useful additional measurements, but the combination of historical exposure, consistent financial definitions and demonstrably pre-target financial information is not yet sufficient to justify rerunning the existing persistence–ridge–tree experiment as an ex-ante forecast.

| Gate | Evidence | Result |
|---|---|---|
| Continuing-council extension | 103 councils; five earlier financial years;515 additional rows | Candidate construction achieved |
| Common definitions | Cash-cover break in2013–14; road-scope change; operating-vintage discrepancies; maintenance measurement conflicts | Partial; explicit exclusions/flags needed |
| Broad new financial mechanisms | Historical aggregate revenue/expenses and rating categories; only two new detailed statement council-years | Insufficient broad operating/capital-grant component coverage |
| Dated ex-ante information | Eight statewide advance-grant announcements, seven with primary outcomes | Useful but limited independent variation and no council-specific payment coverage |
| Same disaster design gains | At most four potential folds versus three on the same V1-period subset | One extra potential test year, not five |
| Financial-only design gains | Eight potential folds under existing embargo/minimum training rule | Upper bound; would omit the original disaster requirement and still needs vintage checks |
| Verified complete as-of bundles | Zero certified by this audit | Fails current forecast-readiness gate |

Potential fold counts use observed primary-target/prior-value pairs; train targets precede test target−1, and training must contain at least100 rows. They do not assume imputation creates absent outcomes or certify source availability. `potential_forward_folds.csv` retains every candidate test year, including invalid/empty years. There was no model fit or performance-based year selection.

The data do **not** establish that fiscal prediction is impossible. They show that this extension alone has not solved the weak design's information limitations. More rows of related ratios can increase training size without adding the timing and mechanisms needed to predict abrupt fiscal changes.

## Smallest useful next data task

1. Validate original publication vintages for a bounded set of prior-year financial predictors and target years, with explicit as-of dates and matched values. Resolve the Albury discrepancy as a worked example rather than assuming all archived ratios are first releases.
2. Extend disaster exposure before2017 on the same definition and audit when mapped products/declarations became available. Without this, the original question cannot use most of the extra fiscal history.
3. Build comparable council-specific prior operating/capital grants, total rates/charges, cash payments and material expense components from released statements. Prioritise broad target-year coverage over a few isolated examples; do not substitute realised target-year grants.

Only after these checks should the existing small-model comparison be rerun on a declared common sample, with unchanged forward-validation rules and all preprocessing confined to training folds. A claim of improved prediction requires held-out performance against persistence; no such claim is made by this audit.

All earlier data and outputs remain unchanged. The V2 panel is a separate candidate research artefact, not a replacement certified training set.
