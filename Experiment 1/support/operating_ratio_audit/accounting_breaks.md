# Accounting consistency and unresolved breaks

These checks document issues; they do not alter the original CSV or predictions. PDF page numbers below are one-based. A period coincidence is not an explanation of an individual case.

| Issue | Observed evidence | Implication |
|---|---|---|
| Source units | The retrieved OLG financial-total headers use thousands in FY2019–20 and FY2022–23 but dollars in FY2020–21, FY2021–22 and FY2023–24. Individual rate/maintenance fields have their own units. | Every recovered component retains its header, cell, raw unit and conversion. Do not apply a workbook-wide multiplier. |
| Percentage storage | FY2023–24 OLG operating performance is a fraction despite its percent header; the original panel uses percentage points. | Multiplying that raw field by 100 reproduces panel values in the selected years. This is not a correction to the frozen panel. |
| OP definition | Performance notes exclude specified gains/losses and revaluation effects. Capital grants are excluded from the OP denominator. | Total continuing revenue and before-capital result are not automatically the ratio denominator/numerator. No back-solving from ratios is used. |
| Grant timing | Carrathool FY2021–22 and FY2022–23 commentary identifies advance FAG recognition; Hay identifies prepayments. | A reported surplus can move because funds for a later year are recognised now. General FAG is distinct from disaster assistance. |
| Maintenance classification | Hay FY2021–22 explicitly reports reclassification from maintenance to capital. | Operating expense reduction need not mean a reduction in work; capitalisation and crowd-out are distinct questions. |
| Restatement — Snowy Monaro | Original FY2021–22 ratio −0.34%; 2023 comparative −1.37%. The FY2021 report also marks earlier comparative revisions. | Do not mix report vintages or silently replace historical forecast inputs with later revisions. |
| Restatement/vintage — Murray River | FY2022–23 panel/report ratio −25.90%; 2024 comparative −26.22%. | Difference documented; exact revision cause not established here. |
| Inconsistent prose — Liverpool Plains | FY2022–23 performance table −4.24%, commentary says −4.64%. | Preserve both and flag discrepancy; use frozen panel value for case selection. |
| Hilltops | FY2021–22 narrative says significant operating-grant income, but does not quantify its contribution to the two-year rebound. FY2024 performance commentary mentions a material prior error affecting the 2023 comparative. | The selected FY2021–22 case remains unexplained. Do not attribute an earlier target to a later restatement. |
| Broken Hill | The 2023 report's 2022 comparative ratio 1.50% differs from the frozen 1.77%. | Further vintage reconciliation required. The 2023 insurance explanation cannot explain a target ending June 2022. |
| Asset accounting | Snowy landfill expense and Wollongong remediation/depreciation evidence show different routes through the accounts. | Revaluation in equity, expense through income, and adjusted OP exclusions must be separated. |
| Reporting period | Hilltops' first accounts cover 13 May 2016–30 June 2017. | A longer-than-12-month first period cannot be treated as a normal annual flow. |
| Boundary/reorganisation | 2016 amalgamations changed legal council entities; the panel's own boundary and exposure flags remain in case tables. | Old names are not a stable legal-entity crosswalk. Do not add predecessor ratios or assume unchanged exposure boundaries. |

## Specific source references

- [Carrathool 2022](https://carrathool.nsw.gov.au/wp-content/uploads/IPR/Annual-Report/Annual-Report-2021-22-FINAL.pdf), PDF pp47, 69, 111, 114; [Carrathool 2023](https://carrathool.nsw.gov.au/wp-content/uploads/IPR/Annual-Report/2022-2023-Final-Annual-Report.pdf), pp68, 119, 122.
- [Hay 2022](https://www.hay.nsw.gov.au/LinkClick.aspx?fileticket=H1oYw0BKpL8%3D&portalid=0), pp73, 76.
- [Snowy Monaro 2022](https://www.snowymonaro.nsw.gov.au/files/assets/public/v/2/council/ipr/annual-financial-statements-2022.pdf), p73; [Snowy Monaro 2023](https://www.snowymonaro.nsw.gov.au/files/assets/public/v/2/council/ipr/annual-reports/annual_financial_statements-gpfs-2023-19-12-23.pdf), p74; [Snowy Monaro 2021](https://www.snowymonaro.nsw.gov.au/files/assets/public/v/1/council/annual-amp-financial-reports/combined-financial-statements-2020-2021.pdf), pp83, 91.
- [Murray River 2023](https://www.murrayriver.nsw.gov.au/files/assets/public/v/1/documents/financial-statements/2022-2023-murray-river-council-annual-financial-statements.pdf), pp35–36, 92; [Murray River 2024](https://www.murrayriver.nsw.gov.au/files/assets/public/v/1/documents/ipampr-docs-and-budgets/mrc-annual_financial_statements-2023-2024.pdf), p80.
- [Liverpool Plains 2023](https://www.liverpoolplains.nsw.gov.au/files/sharedassets/public/v/1/media-and-public-notices/media-release-images-new/lpsc-annual-financial-statements-30-june-2023.pdf), pp63, 66.
- [Hilltops 2022](https://www.hilltops.nsw.gov.au/wp-content/uploads/2023/03/Annual_Financial_Statements-2021-2022.pdf), p87; [Hilltops 2024](https://www.hilltops.nsw.gov.au/wp-content/uploads/2024/10/Annual_Financial_Statements-2023-2024.pdf), p87; [Hilltops first reporting period](https://www.hilltops.nsw.gov.au/wp-content/uploads/2021/07/Annual-Financial-Statements-YE-1617-Hilltops-Council.pdf), cover.
- [Broken Hill 2023](https://www.brokenhill.nsw.gov.au/files/assets/public/v/1/documents/public-notices/annual_financial_statements-2023-final-inclusive-of-audit-reports.pdf), auditor performance commentary p73.
- [Wollongong 2024](https://www.wollongong.nsw.gov.au/__data/assets/pdf_file/0032/258836/Annual-Financial-Statements-for-the-year-ended-30-June-2024.pdf), PDF pp4, 9, browser-readable; direct download failed with HTTP403.

## Accounting standards: sector-wide break, not case-level attribution

The [NSW Audit Office 2019 report, section 2.3](https://www.audit.nsw.gov.au/our-work/reports/report-on-local-government-2019) identifies AASB9 for June2019; AASB15, AASB1058 and AASB16 for June2020; and AASB1059 for June2021. Its [2020 report](https://www.audit.nsw.gov.au/sites/default/files/documents/Report%20on%20Local%20Government%202020.pdf) confirms the revenue standards became effective for councils on 1 July2019. This is especially relevant to grant recognition across older years. An individual movement is not assigned to AASB adoption without its transition note and quantified effect. No universal denominator break was established for every council.

The [official YourCouncil definitions](https://yourcouncil.nsw.gov.au/nsw-overview/finances/) distinguish operating performance, own-source revenue and debt service cover. Individual audited performance-note exclusions remain the source for exact bridges.

## Missingness and remaining checks

All selected original OLG operating-ratio cells reconcile to the frozen panel within rounding. This validates extraction, not the underlying economic measure. Extreme observations are retained. Granular accounts were transcribed for five councils, with documentary review of additional sources; most selected cases remain unresolved. Missing detailed components are not zero. Scanned/inaccessible sources and duplicate or irrelevant report downloads remain visible in manifests. No declared disaster is presumed to have caused a movement. Randwick, Warren and Dungog's added high-ridge-error cases remain unexplained; numerical model sensitivity has not been relabelled an accounting cause.
