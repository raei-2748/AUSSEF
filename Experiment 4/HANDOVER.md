# Experiment 4 — handover

Current status at wrap-up: **NO-GO for causal modelling; conditional continuation for targeted data collection.** No final model has been fitted. Numeric budget coverage has improved, but it does not yet identify comparable ordinary infrastructure portfolios or disaster-caused reallocations.

## What is usable

The candidate store contains 62 projects across Lismore, Richmond Valley, Eurobodalla, Ballina, Snowy Valleys and Wagga Wagga: 375 project/year/stage slots, 136 nonmissing amounts and 14 numerically complete original-budget → Q1 → Q2 → Q3 → actual chains. **None is certified model-ready.** Three comparison candidates remain uncertified controls. These are coverage counts, not independent observations.

Ballina supplies most complete chains. Thirteen 2020–21 original allocations were checked against the original plan; eleven historical positive allocations were corroborated. Council records also substantiate specific deferral decisions. The April 2018 skate-project decision reduced its budget from $500,000 to $50,000 and transferred funding forward. Such records establish decisions, not disaster causation.

The preserved evidence includes missing values, conflicting amounts, uncertain links and negative findings. A full rebuild reproduced all 21 canonical tables; SQLite integrity, foreign-key and CSV/table checks passed. Successful technical checks do not establish research validity.

## Why modelling is blocked

- **Project identity and scope:** budget references can be reused for unrelated assets. Skate-project records have different development applications and site descriptions across years; a council ledger crosswalk is needed before treating them as one unchanged asset.
- **Accounting comparability:** some actuals exclude commitments/accruals; carryovers, revised allocations and new expenditure are not consistently distinguished.
- **Ordinary works versus recovery:** disaster reconstruction and documented physical damage/access restrictions are not reliably separated for every project. A regional event date does not prove local asset damage.
- **Comparison and timing:** no comparison council is certified, three comparable pre-event years remain unverified, and overlapping disasters complicate attribution.
- **Pre-event capacity:** 144 candidate capacity records are not certified predictors. Publication timing can make a prior-year figure unavailable at budget adoption; three inherited Ballina ratios conflict with audited figures. Original values and discrepancies are retained.

## Minimum additional data

Request a versioned capital-project ledger for the six pilot councils and relevant pilot years, extending to at least three comparable pre-event years for proposed comparisons. Ask for:

1. Stable job/asset IDs, names, sites and scope-change crosswalks; original adopted budgets and dated Q1/Q2/Q3 revisions.
2. Year-end actuals with separate commitments/accruals, carryovers and funding sources, plus accounting definitions and reconciliation totals.
3. Deferral/cancellation/completion dates, decision references and reasons; ordinary/reconstruction classifications, linked disaster IDs, damage estimates and access restrictions.
4. Dated original financial statements and publication/adoption evidence for fiscal-capacity measures, with definitions consistent across councils and years.

First resolve the existing pilot's identity, accounting and timing gaps. Scale only if stable ordinary portfolios, credible comparison histories and pre-event capacity can be certified. Public-source reconstruction is incomplete; this handover does not claim that public evidence has been exhausted.

## Where to continue

- Canonical evidence: [SQLite](data/experiment4.sqlite), with corresponding CSV tables under `data/`.
- Outstanding fields: [field gaps](data/field_gaps.csv).
- Reproduction instructions: [REBUILD](data/REBUILD.md); latest checks: [verification](data/rebuild_verification.json).
- Detailed findings: [Ballina history](data/BALLINA_HISTORY_FINDINGS.md), [capacity audit](data/CAPACITY_ALIGNMENT_AUDIT.md), [damage linkage](data/DAMAGE_LINKAGE_AUDIT.md), [disaster overlap](data/DISASTER_OVERLAP_SCREEN.md).

Existing experiments, source data and outputs are preserved. This handover supersedes earlier coverage counts, not the underlying evidence or unresolved findings.
