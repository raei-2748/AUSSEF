# Graph Report - AUSSEF  (2026-09-19)

## Corpus Check
- 188 files · ~4,467,040 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 288 nodes · 248 edges · 46 communities (29 shown, 17 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- interpretation.md
- README.md
- What the diagnostics establish
- Fiscal prediction failure: evidence-based diagnosis
- README.md
- Diagnostic findings for Bowen
- data_gap_priorities.md
- README.md
- research_verdict.md
- Fiscal measures
- fesm_2016_17_425fd83a.md
- V2 retrospective forecasting results
- Operating-ratio movement audit
- Methods and limitations
- build_panel_v2.py
- NSW historical disaster-exposure panel — Version 2 candidate
- build_exposure_v2.py
- Accounting consistency and unresolved breaks
- Historical-extension feasibility
- time-series-data-2011-12-2013-14_7f50e136.md
- time-series-data-2018-2019_1fb5c676.md
- time-series-data-2019-2020_7131f414.md
- time-series-data-2020-2021_de7591e5.md
- time-series-data-2021-22_0c89786c.md
- time-series-data-2022-23_a88ac347.md
- time-series-data-2023-24_fbf08f41.md
- time-series-data-2024-2025_57b4f774.md
- document_exposure_v2.py
- process_historical_fire.py
- council_and_period_audit.md

## God Nodes (most connected - your core abstractions)
1. `Case explanations` - 98 edges
2. `V2 retrospective forecasting results` - 9 edges
3. `Diagnostic findings for Bowen` - 7 edges
4. `Operating-ratio movement audit` - 7 edges
5. `What the diagnostics establish` - 6 edges
6. `Methods and limitations` - 6 edges
7. `Fiscal measures` - 6 edges
8. `FoldPreprocessor` - 5 edges
9. `Experiment 2 — V2 retrospective fiscal forecasting` - 5 edges
10. `Fiscal prediction failure: evidence-based diagnosis` - 5 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (46 total, 17 thin omitted)

### Community 0 - "interpretation.md"
Cohesion: 0.40
Nodes (4): Overall verdict: NO-GO for further predictive modelling, Primary: operating_ratio_pct — NO-GO, Secondary: cash_cover_months — NO-GO, Secondary: maintenance_ratio_pct — CONDITIONAL GO

### Community 2 - "What the diagnostics establish"
Cohesion: 0.18
Nodes (10): 1. The tree throws away useful council-specific persistence, 2. The direction of fiscal change did not transfer across years, 3. The supplied disaster features add nothing to these fitted predictions, 4. There are very few independent years, and the forecast spans two years from the baseline, 5. The failure is not mainly a missing-value-imputation issue, and is not confined to one outlier, Did a better target representation fix it?, Fiscal prediction failure: evidence-based diagnosis, Verdict (+2 more)

### Community 3 - "Fiscal prediction failure: evidence-based diagnosis"
Cohesion: 0.02
Nodes (98): Balranald — 2021-22 (balranald_2021), Balranald — 2022-23 (balranald_2022), Balranald — 2023-24 (balranald_2023), Bathurst Regional — 2023-24 (bathurst_2023), Bellingen — 2021-22 (bellingen_2021), Bellingen — 2022-23 (bellingen_2022), Bland — 2023-24 (bland_2023), Blue Mountains — 2023-24 (bluemountains_2023) (+90 more)

### Community 5 - "Diagnostic findings for Bowen"
Cohesion: 0.25
Nodes (7): 1. A smoother model helps somewhat, but does not beat persistence, 2. Error concentration: years, councils and movements, 3. Disaster ablation and subgroup errors, 4. Change forecasting does not solve the problem, 5. What the evidence cannot establish, Conclusion, Diagnostic findings for Bowen

### Community 9 - "Fiscal measures"
Cohesion: 0.09
Nodes (18): Accounting regimes, Cash cover: a verified definition break, Definition, unit and measurement audit, Fiscal measures, Maintenance, Operating ratio and statement components, Source-specific scaling, Decision: NO-GO for an immediate predictive rerun (+10 more)

### Community 10 - "fesm_2016_17_425fd83a.md"
Cohesion: 0.18
Nodes (10): Sheet: Tab 1 - Statewide, Sheet: Tab 2 - LGA, Sheet: Tab 3 - LLS, Sheet: Tab 4 - IBRA, Sheet: Tab 5 - Tenure, Sheet: Tab 6 - NPWS Estate, Sheet: Tab 7 - Veg Formation (Keith), Sheet: Tab 8 - Soil Type and Texture (+2 more)

### Community 13 - "Operating-ratio movement audit"
Cohesion: 0.25
Nodes (7): A–F verdict, Files, Limitations, Operating-ratio movement audit, Purpose and frozen inputs, Selection and coverage, Temporal structure and errors

### Community 14 - "Methods and limitations"
Cohesion: 0.29
Nodes (6): 1. Fixed population and reference years, 2. Historical fire mapping, 3. Area-unit discrepancy and measurement breaks, 4. Declaration reconstruction and zeros, 5. Timing and future use, Methods and limitations

### Community 15 - "build_panel_v2.py"
Cohesion: 0.33
Nodes (3): key_for(), norm(), Build a candidate fiscal panel and audit eligibility. No models or imputation. R

### Community 16 - "NSW historical disaster-exposure panel — Version 2 candidate"
Cohesion: 0.09
Nodes (19): Design, Experiment 2 — V2 retrospective fiscal forecasting, Organisation record, Shared inputs, Start here, Boundaries on interpretation, Did longer history help on the same later years?, Files and reproduction (+11 more)

### Community 18 - "Accounting consistency and unresolved breaks"
Cohesion: 0.40
Nodes (4): Accounting consistency and unresolved breaks, Accounting standards: sector-wide break, not case-level attribution, Missingness and remaining checks, Specific source references

### Community 19 - "Historical-extension feasibility"
Cohesion: 0.40
Nodes (4): Historical-extension feasibility, Major breaks, Sources and observed availability, What would make extension acceptable?

### Community 20 - "time-series-data-2011-12-2013-14_7f50e136.md"
Cohesion: 0.50
Nodes (3): Sheet: 2011-12 Time Series Data, Sheet: 2012-13 Time Series Data, Sheet: 2013-14 Time Series Data

## Knowledge Gaps
- **194 isolated node(s):** `Start here`, `Design`, `Shared inputs`, `Organisation record`, `Primary: operating_ratio_pct` (+189 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Start here`, `Design`, `Shared inputs` to the rest of the system?**
  _194 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Fiscal prediction failure: evidence-based diagnosis` be split into smaller, more focused modules?**
  _Cohesion score 0.020202020202020204 - nodes in this community are weakly interconnected._
- **Should `Fiscal measures` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `NSW historical disaster-exposure panel — Version 2 candidate` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._