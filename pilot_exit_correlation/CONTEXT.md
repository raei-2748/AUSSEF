# Project context: correlated exit failure in NSW bushfire towns

One-page handover covering what this project is, what it found, where the data and code live, the
rules it follows, its known weaknesses, and the options for what comes next.
Last updated 23 September 2026. Branch `pilot-exit-correlation`, latest commit `df6a737`.

---

## 1. The project

**Question.** Planners judge a town's evacuation safety by counting its roads out. That only works if
roads fail independently. Do bushfires cut *all* of a town's exits at once more often than chance?

**Answer.** Yes, far more often. Across 70 years of NSW fires, all exits were cut together about
**15×** more than independence predicts.

**Framing for AUSSEF/ISEF.** The entry is in a **social-science and public-finance** category, not
earth science. So the road analysis is the *method*; the subject is who is exposed and who pays.

**Anchor in the literature.** Fong et al., *PNAS* 2026, "Egress thresholds and wildfire fatalities":
wildfire deaths concentrate in communities with few exits, flattening at about six. It counts exits
with a 0.5 km buffer and **treats exits as independent**; its stated limits are no network-flow
analysis, no fire timing, no socioeconomic vulnerability, and US-only data. This project addresses
all four on Australian data.

---

## 2. Results by stage

| Stage | Test | Result |
|---|---|---|
| 1 | Each town separately | **FAIL** — at most 1 cut-off per town; too few events to test |
| 2 | All towns pooled, 2019–23 fires | **FAIL (narrow)** — 22 vs 3.3 expected, R = 6.6 (CI 0.90–8.5) |
| 2 | All towns pooled, 1950–2019 fires (confirmatory) | **PASS** — 24 vs 1.6, **R = 14.9 (CI 3.9–31)** |
| 3a | Only roads cut *outside* the town | **PASS** — R = 13.8 (CI 3.1–29) |
| 3b | Satellite: all exits reached within 12 h, whole 20 km route | **FAIL** — 9 of 31, R = 6.9 (CI 0–12.4) |
| 4 | Satellite: same, but within ~5 km of town | **PASS** — 11 of 31, R = 8.4 (CI 1.9–14.4) |
| 5 | Official road-closure records | Descriptive — 0 of 22 cut-offs confirmed on every exit; records too sparse |
| 6 | Do councils with cut-off towns have weaker finances? | **NOT SUPPORTED** — the opposite: own-source revenue 68% vs 62% (+6.0 pp, CI 0.9–15.0) |
| 7 | Are cut-off towns older? | **NOT SUPPORTED (borderline)** — 27.7% vs 23.1% aged 65+, CI −0.002 to 7.0 |
| 8 | 2016→2021 change, cut-off vs burned-only towns (exploratory) | "BETTER" — +6.1 pp population growth; almost certainly coastal growth, not an effect |
| 9 | Does the published count-based measure find cut-off towns? | **NOT EVALUABLE** at 6 exits (only 5 NSW towns qualify); the count does track risk directionally |

**Headline numbers to quote**
- All exits cut together **≈15× more often than chance** (historical record, CI 3.9–31).
- When a fire blocked at least one road out, it blocked **all** of them 2.0% of the time; independence predicts 0.1%.
- **80,061 people** live in the 43 towns ever fully cut off: **23,873 aged 65+**, **6,251 needing help with everyday activities**, 1,378 homes with no car.
- Timed near town, the median gap between fire reaching the first and last exit was **~22 hours**; Mogo's exits were hit within **1.9 hours**.
- **15 towns** with 3+ roads out were still fully cut off (50,638 residents, 15,954 aged 65+).
- **49%** of those towns' exit-route length, and **53%** of the exit road that burned, is **State-owned** (vs 38.8% statewide).
- Councils holding the most at-risk residents raise ~$17,000–18,000 of own revenue per resident aged 65+ in their cut-off towns; small-exposure councils raise $200k–2.4M per such resident.

---

## 3. Data

All inputs are SHA-256 verified on every run. `data/aussef.duckdb` is **never written** and its hash is
checked before and after each run. Downloads live in `pilot_exit_correlation/data/` and are git-ignored;
their URLs and hashes are in each stage's `RUN_LOG.md`.

| Input | Location | Notes |
|---|---|---|
| Road network, 1 Jan 2019 OSM | `~/.codex/.chatgpt-projects/g-p-6a5b…/transport_criticality_experiment/inputs/network_fingerprint.parquet` | 1,451,892 edges; 1,214,545 after dropping `service`; EPSG:3577 |
| Fire × road overlay 2019–23 | `…/transport_criticality.duckdb` → `analysis.fire_road_exposure_v2` | 21,712 rows, 676 families, rules S0/S100 |
| Fire families 2019–23 | same DB → `main.disaster_family_members` | 1,034 families |
| Fire perimeters 2019–23 | `…/dataset_phase1/data/event_perimeters.gpkg` | Geoscience Australia, 17,904 events |
| Historical fires 1950–2019 | `…/dataset_phase1/raw/ga_original.zip` | GA product 149017; 11,106 NSW fires → 7,729 events |
| Towns | ABS UCL 2021 + 2021 Census GCP (NSW) | 526 towns with population ≥ 200 |
| 2016 comparison | ABS 2016 Census GCP UCL + 2016 UCL boundaries | for stage 8 only |
| Satellite fire detections | DEA Hotspots WFS, cached in `stage3/data/hotspots/` | ~590,000 detections, 12 fire events, 2002→ |
| Road ownership | TfNSW "NSW Road Network Categorisation" | CC-BY; `admin_clas` S = State, R = Regional |
| Council finances | `data/aussef.duckdb` → `master.fiscal_panel_extended` (103 councils) and `master.fiscal_panel_legacy` (128) | 2012–2024; own-source %, grants %, cash cover, maintenance ratio, road km |
| Council road spending | `…/transport_criticality_experiment/inputs/olg_road_expenditure_panel.csv` | roads/bridges/footpaths expenditure by council-year |
| Road-closure records | `transport_criticality.duckdb` → `analysis.road_closure_candidates` | only 37 curated records; Live Traffic snapshots 12–31 Jan 2020 |

---

## 4. Method in brief

1. **Exits** = the maximum number of routes sharing no road segment from the town to a ring 20 km out (unit-capacity max-flow). One minimum-length set of routes is stored per town.
2. **Closure**: a fire closes a road segment if its mapped perimeter touches it (S0) or comes within 100 m (S100).
3. **Full cut-off**: after removing every segment a fire closes, no route reaches the ring.
4. **Expected under independence**: for each town, p_j = share of nearby fires closing exit j; expected = n × Π p_j. Observed and expected are summed over all towns.
5. **R = observed ÷ expected.** R = 1 means no different from chance.
6. **Uncertainty**: bootstrap over whole fire events (1,000 resamples, seed 20260921), because one fire hits many towns.
7. **Decision rule fixed in advance**: PASS if R ≥ 2 and the lower 95% bound > 1.

---

## 5. Code and conventions

```
pilot_exit_correlation/
  WRITEUP.md CONTEXT.md README.md
  PREREGISTRATION.md DECISIONS.md DEVIATIONS.md RUN_LOG.md RESULTS.md   # stage 1
  run_pilot.py  src/{inputs,exits,closure,metrics,report}.py  tests/
  stage2/  pooled test (s2/{historical,pooled,report}.py)
  stage3/  outside-town + satellite timing (s3/{hotspots,timing,report}.py), hotspot cache
  stage4/  timing near town
  stage5/  official closure records
  stage6/  council finances (stats6.py: Mann-Whitney, bootstrap, Holm)
  stage7/  vulnerability of cut-off towns
  stage8/  2016→2021 change (exploratory)
  stage9/  published count measure, blind spot, road ownership, indicative cost
  data/    downloads (git-ignored)
```

Every stage has the same six documents (pre-registration, decisions, deviations, run log, README,
results), a one-command runner and tests.

**Rules followed throughout**
- The pre-registration is **committed to git before any result exists**; deviations are logged with reasons.
- Inputs are read-only and hash-verified; `aussef.duckdb` is never modified.
- Missing is never zero. No synthetic fires.
- Every run is reproducible: fixed seed, byte-identical outputs on a re-run.
- No causal language, and no claims about lives.
- Run with `uv run --no-sync --with matplotlib python <stage>/run_*.py` (this leaves the project lock untouched).

---

## 6. Known weaknesses (say these before a judge does)

1. **Closure is inferred from fire maps, not observed.** Final perimeters assume everything inside closed at once, so R is an upper bound. Official closure records were too sparse to confirm even one town.
2. **Relevance is loose.** A fire counts as "relevant" if it burned within 30 km, even if the town was never threatened. The sharper question is *given the town was threatened, how often were all exits cut?*
3. **Fire only.** Smoke, fallen trees, burnt bridges, post-fire landslides and debris flows, and floods also close the same corridors. Our numbers are a floor for road failure, not a ceiling.
4. **Few events.** The historical result rests on 24 cut-offs from 13 fires; 2019–23 on 22 from 4 fires. One fire complex often dominates.
5. **Timing measures arrival, not duration.** We know when fire reached a road, not how long it stayed shut.
6. **Coverage.** Historical fire maps come from national-parks records; satellite timing only exists from 2002; the 2019 road network is applied to all years.
7. **Stage 8 is confounded** by coastal and COVID-era migration.

---

## 7. Where it could go next

**A. Conditional analysis (small, sharpens everything).** Restrict to fires that actually threatened the town (e.g. burned within 5 km) and re-ask the question. Fixes weakness 2, and gives the number a planner wants.

**B. Machine learning, in the defensible form (discussed, not yet built).** Two separate models:
- *Model 1 (physical):* predict which towns get cut off from network and fire-history features only, trained on pre-July-2019 fires and tested on Black Summer. No fiscal inputs.
- *Model 2 (fiscal, the headline):* predict which councils fail to restore or maintain roads after disaster exposure, from pre-disaster fiscal indicators. About 1,100 council-year rows, train to 2018 and test 2019–23, compared against simple baselines, reported with AUC and precision-recall rather than accuracy.
- **Do not** predict cut-offs from council finances: budgets don't shape fire geometry, only 43 towns qualify, and a "91% accurate" model is just predicting "never".

**C. Multi-hazard extension.** Do the same exit roads also close in floods and storms? 8,185 NSW closure records with causes exist, though the data are thin.

**D. Victoria replication.** The historical fire file already holds ~77,000 Victorian records; the road and town data cover all of Australia.

---

## 8. Git history

| Commit | Contents |
|---|---|
| `1e8cd4f` | Stages 1–2 |
| `08fbe52` / `2154785` | Stage 3 pre-registration / results |
| `f27b5c5` / `60329e6` | Stage 4 |
| `2851eea` / `e4833ca` | Stage 5 |
| `b7f0124` / `115641d` | Stage 6 |
| `b52d066` / `19b9502` | Stage 7 |
| `57e3835` / `01b6852` | Stage 8 |
| `ef4642f` / `a4d5f96` | Stage 9 |
| `b668391`, `df6a737` | Consolidated write-up |
