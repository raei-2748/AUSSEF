# Judgment calls: stage 9

| # | Date | Decision | Reason |
|---|---|---|---|
| S1 | 2026-09-23 | Counted exits distinguish roads by `ref` where present, else `name`; unnamed crossing edges count individually. | The published method counts distinct roads; OSM route numbers are the closest available identifier. |
| S2 | 2026-09-23 | Exit edges more than 25 m from any categorised TfNSW road are labelled local (council). | The categorisation covers State and Regional roads only; everything else is local by definition. |
| S3 | 2026-09-23 | The indicative cost uses 2018-19 council road spending per km applied to burned exit kilometres. | It is the only local unit cost in the project data. It is reported as an annual maintenance-equivalent range, never as a construction estimate. |
