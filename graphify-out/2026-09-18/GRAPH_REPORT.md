# Graph Report - AUSSEF  (2026-09-18)

## Corpus Check
- 5 files · ~55,554 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 20 nodes · 16 edges · 5 communities (3 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- interpretation.md
- README.md
- What the diagnostics establish
- Fiscal prediction failure: evidence-based diagnosis
- README.md

## God Nodes (most connected - your core abstractions)
1. `What the diagnostics establish` - 6 edges
2. `Fiscal prediction failure: evidence-based diagnosis` - 5 edges
3. `AUSSEF exploratory fiscal decision tree` - 1 edges
4. `Primary: operating_ratio_pct — NO-GO` - 1 edges
5. `Secondary: cash_cover_months — NO-GO` - 1 edges
6. `Secondary: maintenance_ratio_pct — CONDITIONAL GO` - 1 edges
7. `Overall verdict: NO-GO for further predictive modelling` - 1 edges
8. `Fiscal prediction diagnostics` - 1 edges
9. `Verdict` - 1 edges
10. `1. The tree throws away useful council-specific persistence` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities (5 total, 2 thin omitted)

### Community 0 - "interpretation.md"
Cohesion: 0.40
Nodes (4): Overall verdict: NO-GO for further predictive modelling, Primary: operating_ratio_pct — NO-GO, Secondary: cash_cover_months — NO-GO, Secondary: maintenance_ratio_pct — CONDITIONAL GO

### Community 2 - "What the diagnostics establish"
Cohesion: 0.33
Nodes (6): 1. The tree throws away useful council-specific persistence, 2. The direction of fiscal change did not transfer across years, 3. The supplied disaster features add nothing to these fitted predictions, 4. There are very few independent years, and the forecast spans two years from the baseline, 5. The failure is not mainly a missing-value-imputation issue, and is not confined to one outlier, What the diagnostics establish

### Community 3 - "Fiscal prediction failure: evidence-based diagnosis"
Cohesion: 0.40
Nodes (4): Did a better target representation fix it?, Fiscal prediction failure: evidence-based diagnosis, Verdict, What remains unknown and what to do next

## Knowledge Gaps
- **14 isolated node(s):** `AUSSEF exploratory fiscal decision tree`, `Primary: operating_ratio_pct — NO-GO`, `Secondary: cash_cover_months — NO-GO`, `Secondary: maintenance_ratio_pct — CONDITIONAL GO`, `Overall verdict: NO-GO for further predictive modelling` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `What the diagnostics establish` connect `What the diagnostics establish` to `Fiscal prediction failure: evidence-based diagnosis`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Why does `Fiscal prediction failure: evidence-based diagnosis` connect `Fiscal prediction failure: evidence-based diagnosis` to `What the diagnostics establish`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **What connects `AUSSEF exploratory fiscal decision tree`, `Primary: operating_ratio_pct — NO-GO`, `Secondary: cash_cover_months — NO-GO` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._