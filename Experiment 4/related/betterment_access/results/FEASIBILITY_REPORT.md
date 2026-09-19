# Experiment 4B — Queensland 2022 Betterment Fund Access

**Overall: CONDITIONAL GO for obtaining data; no model is justified now.** Audit completed 19 September 2026. The question remains open: does pre-disaster fiscal/administrative capacity add out-of-council predictive information about approval beyond independently measured project need?

| Component | Verdict | Reason |
|---|---|---|
| Decision-data feasibility | CONDITIONAL GO | Public awards and some status evidence exist; no verified eligible unsuccessful local-government case recovered. QRA register required. |
| Queensland capacity-data feasibility | CONDITIONAL GO | Three published financial measures recovered for 39 identified councils; broader capacity and application-specific availability remain incomplete. |
| Need-measurement feasibility | CONDITIONAL GO | Published criteria are clear; comparable original damage, cost, risk and quality evidence for both outcome classes is missing. |
| Modelling feasibility | NO-GO now | Gates 2–5 fail; gates 1 and 6 only partly pass. No certified two-class sample or complete need block. |
| Overall Experiment 4B | CONDITIONAL GO | Acquire and audit QRA records before reconsidering models. This is not a finding of unequal access. |

## What the official universe does and does not establish

[QRA’s 2022 program page](https://www.qra.qld.gov.au/betterment/2022) reports **123 submissions, many containing multiple projects, from 39 councils and TMR**. Its published tables contain **221 asset/works rows: 183 Category D and 38 Category E**. Of these, **194 rows name 38 councils; 27 name TMR**. Four repeated stream/applicant/asset-label groups leave 217 distinct label combinations. Neither 221 nor 217 is a certified count of unique project applications. Repeated labels may denote separate road segments or publication duplication; they are retained, not silently collapsed.

The study unit must be one distinct Betterment project application, with its parent submission and revisions linked. Public row IDs in this audit are reference keys, **not official application IDs**. The 123 submission denominator cannot be subtracted from or divided into the asset-row count. No approval rate is calculated. The difference between 39 reported submitting councils and 38 award-list councils does not identify an unsuccessful council.

Official award-list entries provide high-confidence reported approvals and imply acceptance under the program, but do not expose individual eligibility checks. Dates, requested/approved amounts, assessment scores, BCRs and application identifiers are generally absent. Blank values remain unknown, including blank approved amounts. The July 2024 page update is not an award date. Council evidence adds coarse dates for Teviotville Road: submitted December 2022, approved “early 2023”; no exact day is invented.

## Search for unsuccessful applications

`decision_evidence.csv` preserves **13 evidence observations, not 13 separate applications**. Every label has a source URL, page/section, confidence and scope assessment. `search_and_negative_findings.csv` records targeted searches across QRA, council agendas/reports, QAO and Parliament, including unsuccessful, rejected, ineligible, withdrawn, declined and not-funded wording. This is a bounded public-source search, not proof that all archives were exhausted.

* **Boulia:** [June 2023 agenda, p23](https://www.boulia.qld.gov.au/files/assets/public/v/1/council/council-meetings/agendas/2023/june-2023-ordinary-council-meeting-agenda.pdf) explicitly records April 2022 Betterment as **ineligible**, because restoration was already completed on the relevant sites. Earlier lodged and later ineligible observations are linked narratively, not counted as new applications. January 2022 Betterment is described as lodged. Nearby REPA approval and its $1.81m amount are not Betterment approval or the Betterment request.
* **Diamantina:** [September 2024 agenda, PDF p39 / printed p38](https://www.diamantina.qld.gov.au/files/assets/public/v/1/council/council-meetings/agendas-and-minutes/documents/2024-agenda-and-minutes/agenda_ordinary_council_meeting_monday_16_september_2024.pdf) reports two unsuccessful Betterment proposals, but names **TMR as applicant**. Eligibility and round remain unverified; these are outside the local-government population. The amounts are project estimates.
* **Ipswich:** [May 2023 agenda, April external-funding table](https://ipswich.infocouncil.biz/Open/2023/05/CO_20230525_AGN_3342_AT.HTM) records a lodged Betterment kerb-and-channel REPA submission requesting $988,292.95. The Betterment component, final outcome and official project identities are unresolved.
* **Somerset:** an explicit unsuccessful Kimbala Road case in [September 2016 minutes, p103](https://www.somerset.qld.gov.au/files/assets/public/v/1/your-council/documents/minutes/2016/2016_09_14-ordinary-minutespdf.pdf) concerns the **2015 Cyclone Marcia round**, not 2022.
* **Mareeba:** a rejected bridge-reinstatement scope does not establish membership of the 2022 Betterment round. Scenic Rim’s aggregate applications still under assessment do not establish terminal unsuccessful outcomes.

Thus **zero qualifying eligible unsuccessful cases were recovered**. The true number is unknown, not zero. Ineligible, withdrawn, unresolved, state-agency and wrong-round cases cannot be manufactured into controls. The RTI disclosure log indicates relevant project material may be obtainable, but a disclosure-log entry is not the underlying dossier.

## Rules and changing status matter

[June 2022 guidelines](https://www.qra.qld.gov.au/sites/default/files/2022-06/DRFA%20CAT%20D%20%26%20CAT%20E%20Queensland%20Betterment%20Guideline%20-%20Version%202_%20June%202022.pdf) distinguish damaged eligible essential public assets, base Category B reconstruction, and the incremental Betterment investment. [July 2022 annexure](https://www.qra.qld.gov.au/sites/default/files/2022-07/ANNEXURE%202%20of%20Betterment%20Funding%20Guidelines%20-%20Betterment%20funding%20rounds%20-%20eligible%20events%20-%20Version%202_July%202022.PDF) lists $150m Category D and $20m Category E pools, ordinary project caps of $5m/$3m, and different eligible-event lists. The D event list changed from June to July. Record the rule version for each decision. Indigenous councils are exempt from the normal co-contribution requirement; this policy difference needs explicit treatment.

The criteria cover hazard/risk and options, economic and nonfinancial benefits, community benefits, technical evidence and innovation, plus regional balance and alternative funding. A single numerical BCR is not established as mandatory for every project. Unsuccessful projects can be reconsidered. REPA withdrawal and re-lodgement can be an administrative revision rather than abandonment. Later funding changes, including a reported $7.2m reallocation in [Treasury’s 2025 parliamentary response](https://documents.parliament.qld.gov.au/com/GEFC-11EE/APS2024202-A09D/Response%20to%20Question%20taken%20on%20Notice.pdf), further require dated histories rather than a timeless binary label. Guideline §28 concerns design changes **after approval** and must not supply predictors.

## Queensland capacity: a concrete but partial baseline

[QAO Local government 2021, Appendix I, Figure I4 (printed pp55–60)](https://www.qao.qld.gov.au/sites/default/files/2022-05/Local%20government%202021%20%28Report%2015%E2%80%932021%E2%80%9322%29%20%E2%80%93%20Appendix%20I.pdf) supplies **117 values: three measures for 39 identified councils** (38 published-award councils plus Boulia). This is not a certified list of all 39 reported submitting councils. The three measures are operating surplus ratio, five-year average grant share of total revenue, and net financial liabilities ratio. They are separate features, not a composite capacity index. All six source-table pages were checked visually.

Most measurements end 30 June 2021; Palm Island and Richmond use 2019–20 accounts because the later audits were incomplete. The five-year grant measure is not current operating-grant dependence and cannot be complemented to infer own-source revenue. Net financial liabilities are not simply borrowing. Brisbane’s published 202% includes a service-concession accounting change; QAO discusses 127% without that change. Preserve the published number and flag it rather than silently replace it.

The report was published **11 May 2022**. Measurement predates the covered disasters, but publication does not predate all disaster onsets. Publication precedes Teviotville’s known December 2022 application; strict availability for the other undated award rows remains uncertified. Internal council knowledge and public availability are different claims. Annual-report audit signatures are not publication dates.

An Ipswich 2020–21 pilot adds 12 financial/staffing values and one population observation, making **130 numeric values in total**. Cash includes restricted funds; staff headcount is not FTE; grants include capital/contributed assets; book-value assets need valuation harmonisation. These are examples of constructible variables, not a full comparable panel. No NSW values are loaded. Blocked comparative-report endpoints and obsolete links are preserved in provenance; they do not establish data nonexistence.

## Need and project quality

`project_need_quality_audit.csv` maps each proposed field to the actual assessment criteria. Comparable application-level damage, reconstruction cost, hazard risk, original BCR/CBA assumptions, beneficiary measures and technical readiness are not recovered across both outcomes. Selected success stories and eventual construction benefits cannot stand in for original need. Geographic remoteness or council population alone does not capture project damage.

Keep underlying externally documented need separate from the quality of application presentation. Better-resourced councils may prepare stronger submissions; adjusting for presentation or assessor scores can change the question. Request the scores to understand the process, but do not use an approval recommendation as a predictor of approval. No arbitrary need index was constructed.

## Conditions for reconsidering modelling

Obtain a reconciled registry with official project and parent submission IDs, eligibility, all status transitions and a stated extract date, plus original need records. Define in advance whether the outcome is the first substantive eligible decision or final decision at a common maturity cutoff. Pending or withdrawn cases remain separate; test reconsideration in a separate sensitivity analysis. Require actual negative and positive outcomes spread over multiple distinct councils, rather than a large row count concentrated in one council. There is no universal sufficient sample size: inspect council/class distribution, potential separation and grouped uncertainty before declaring the gate passed.

If all gates later pass, compare fixed simple logistic regression and a depth-2/3 tree under M0 (need/quality) and M1 (same need/quality plus pre-event capacity). Use identical eligible cases and whole-council outer folds. Fit imputation, scaling and any parameter choice on training councils only; any tuning requires nested council grouping. Evaluate paired held-out log loss and Brier score, calibration, and ROC/PR AUC only where defined; compare a training-prevalence baseline. Retain failed/undefined folds, class counts and equal-council as well as application-weighted summaries. Estimate paired M1–M0 uncertainty by resampling councils, not application rows, and acknowledge instability with few councils. Whole-council transfer within this fund is not future-year validation. No predictive contribution proves discrimination, unfairness or causation.

**No models, model performance estimates or artificial comparison group have been produced.** All 962 pre-existing files are checked against their original hashes. The next deliverable is the unsent `QRA_DATA_REQUEST.md`, not another algorithm.
