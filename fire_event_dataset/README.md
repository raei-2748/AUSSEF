# NSW fire-event dataset, 2015–2025

**One row per fire × council (LGA).** Covers every New South Wales bushfire from 1 January 2015 to the end of the
available records (2025), with the columns in Bowen's template order, followed by extra columns. **No models are
fitted.** `Y`, `Y_class`, `DL`, `IL`, `FP`, `SL` and `split` are left blank, to be designed in class. Raw components
are filled wherever public data exist.

Output: `out/nsw_fire_events_2015_2025.xlsx`

| Sheet | What it holds |
|---|---|
| `fires` | One row per fire × LGA it burned in. Template columns first (event_id … split), then extras |
| `lga_year` | Council × year panel, 2014–2025: population, income, SEIFA, council finances, unemployment, industry shares |
| `dictionary` | Every `fires` column: meaning, unit, source, note, **coverage %** |
| `sources` | Every input: URL, local file, SHA-256, access time, licence |

A CSV copy of each sheet is also in `out/`. Sanity-check results are in `out/checks.txt`.

**Missing is never zero.** A blank cell means no data. A zero means the data source was checked and the value really
is zero; for example, a hotspot count of 0 means DEA was queried and found no detections inside the outline.

## X/Y-labelled workbook for Bowen (`src/xy_format.py`)

`out/nsw_bushfires_2015_2025_XY.xlsx` is the combined workbook with every column labelled. Nothing is dropped; only
names, order and labels change, and the `variables` sheet maps each new name to the original one.

- Row 1 of each data sheet is a coloured band: **ID**, **Y** (DL / IL / FP / SL), **X** (fire / env / socio / council),
  **Info**. Row 2 holds the column names (`pd.read_excel(..., header=1)`).
- Y columns start `DL_`, `IL_`, `FP_`, `SL_`; `*_src_` = raw levels an indicator is built from; `*_reported_` = figures
  from declarations and inquiries. X columns: `X1`–`X23` (template) and `X_fire_`, `X_env_`, `X_socio_`, `X_council_`.
- `key_event_council` (declared event × council, 218 rows) carries the Y hierarchy: indicator → percentile rank →
  pillar DL/IL/FP/SL → composite `Y` (equal weights) → `Y_class` 1 Light / 2 Moderate / 3 Severe / 4 Extreme.
  The class comes from Y's percentile (50/30/15/5), then a direct-loss floor (sourced figures only): >=100 homes
  destroyed -> 4; >=10 homes destroyed or >=2 deaths -> at least 3; one death -> one level up, at most 3. Deaths count
  everyone the fire killed in the council, firefighters and aircrew included (EM-DAT / Sendai practice);
  `SL_deaths_type` says who died (from `data/key_events/death_types.csv`, with the source quote) and
  `Y_class_excl_responder_deaths` gives the class without responder deaths. Also written to
  `out/key_event_council_Y.csv`.

- **`master` sheet** (`out/master_event_council.csv`): one row per declared event × council with every variable,
  built by `src/master.py`:
  - the Y hierarchy and key-event columns;
  - the event's per-fire variables aggregated over its fires in the council (weighted means, max/min, and whole-fire
    totals × the fire's share inside the council);
  - every `lga_year` variable in windows: `_pre` (before the fire, X), `_event` and `_plus1` (Y source data).
    Financial-year columns use the fire FY; 30 June counts and ERP the 30 June before / ending / after it;
    calendar-year means use the year before the fire year (pre) and the fire year if the fire started January–June,
    else the next year (event). One-off columns (Census, SEIFA, TRA 2017, REDS 2020) take the latest value dated at
    or before the fire year, else the earliest after it.
  - All-blank and exactly duplicated columns are dropped and listed on `removed_columns`.
- **Layout:** compact columns, one merged band cell per group, severity colour codes on `master` (Y_class 1-4 green /
  yellow / orange / red; Y, Y_norm, Y_FFDI and the pillars shaded green to red). Column names are shortened with fixed
  abbreviations (`NEAT` in `src/xy_format.py`, e.g. `biz_` = CABEE businesses, `A_agri`, `_pre/_event/_plus1`); Bowen's
  template names are kept exactly, and the `variables` sheet keeps each column's original name.
- **Codes (master sheet):** row 1 = group · topic, row 2 = code, row 3 = name. Y1–Y747 are the impact variables by
  pillar (DL Y1–21, IL Y22–636, FP Y637–720, SL Y721–747) and topic; X1–X23 are Bowen's template variables or their
  event × council equivalents (column `bowen_template` on the codebook), X24–X461 our extra predictors by category
  (fire, terrain, people & economy, council) and topic. The Y targets and Y hierarchy keep their names. Codes are
  frozen in `codes/master_codes.csv` (`src/codes.py`): existing codes never change, new variables get the next free
  number. `out/master_event_council_coded.csv` uses the codes as column names.
- **Sources:** the `codebook` sheet (formerly `variables`) gives every column's code, topic, meaning, unit, source and link (`src/col_sources.py`,
  `src/col_docs.py`). Per-council home losses and deaths (`*_sourced`) carry title | URL | page | verbatim quote in
  their `_source` column (`src/dl_council.py`).
- **Direct loss for Y uses sourced figures only.** `DL_homes_destroyed_in_council` = the per-council figure of
  `src/dl_council.py`, else a council fact in `key_facts`. The area-share split of whole-fire figures is kept only as
  the proxy `homes_destroyed_area_share` (it double counts where a source already assigns a fire's losses to one
  council).
- **Council-level enrichments** joined in `src/panel_extra.py`: `src/il_sector.py` (CABEE by industry, business
  entries/exits, Jobs in Australia, insolvencies, PIA, TRA 2017), `src/grp_insurance.py` (BCARR SA4 GRP, REDS 2020 GRP,
  Census tenure insurance proxy), `src/fp_funding.py` (2019-20 recovery grants by council, OLG maintenance $).
- **Checks:** `tests/test_master.py` recomputes every window cell, fire aggregate and Y value independently.

```bash
uv run --no-sync --with openpyxl python -m src.xy_format
uv run --no-sync --with openpyxl python tests/test_master.py
```

Audit fixes of 2026-09-27 (an independent cell-by-cell trace against the raw files found them):
- OLG spending shares are divided by the sum of the spending-by-function lines (OLG's definition), not total operating
  expenses (Gwydir 2023-24 was 112%). A published $0 roads line is treated as not reported.
- Rent annual values need all four quarters (suppressed quarters had summed to 0; 2017 had only two quarters).
- Hotspot counts and the ICA loss proxy are split by the fire's share inside each council before summing.
- Audit Office council figures keep bushfire-only amounts (flood damage and grants were mixed in).
- Four facts moved to the right declaration or council (`data/key_events/corrections.csv`, new action `set_agrn`).

## How to rebuild

Run from the repository root. `uv --with` adds packages for the run without changing the project lock file.

```bash
uv run --no-sync --with openpyxl python fire_event_dataset/build_all.py
```

Enrichment steps: each caches its downloads under `data/` and writes `data/enrich/<name>.parquet`. Reruns make no new
requests.

```bash
cd fire_event_dataset
../.venv/bin/python -m src.weather                              # X2, X3, X7–X9 (Open-Meteo + NASA POWER)
../.venv/bin/python -m src.hotspots                             # X5 (DEA Hotspots)
uv run --no-sync --with rasterio --with pillow python -m src.terrain   # X10–X11
uv run --no-sync --with rasterio python -m src.fesm_convert     # once: 2021-22 FESM grid -> 30 m GeoTIFF
uv run --no-sync --with rasterio python -m src.severity         # X6 (FESM)
uv run --no-sync --with rasterio python -m src.nvis_fetch       # once: NVIS raster for NSW
uv run --no-sync --with rasterio python -m src.vegetation       # X12–X13
uv run --no-sync --with openpyxl python -m src.economy          # SALM, remoteness X18, Census industry
uv run --no-sync --with openpyxl python -m src.ica              # DL_insurance_loss_raw
uv run --no-sync --with openpyxl python -m src.olg              # NSW OLG council finance time series
../.venv/bin/python -m src.dwellings                           # dwellings_census (ABS Census 2016 G32 / 2021 G36)
uv run --no-sync --with openpyxl python -m src.rent             # SL_rent_change_* (NSW DCJ Rent and Sales Report)
uv run --no-sync python checks.py                               # sanity checks -> out/checks.txt
../.venv/bin/python tests/test_fire_weather.py                  # formula tests
```

## Fires

- **Source:** Geoscience Australia bushfire boundaries.
  - Historical layer, frozen by SHA-256.
  - "Historical Bushfire Extents 2020–25" layer 3 (NSW, all records downloaded).
  - Linked through the phase-1 event inventory.
- **Excluded:** prescribed burns. Fires with an unknown type are kept and flagged (`fire_type_flag`).
- **Duplicates:** records found in both layers are removed when outlines overlap (IoU ≥ 0.5) and start dates are within 3 days; the recent-layer record is kept.
- **One row per incident:** records that started within 10 days of each other are merged into one fire when they overlap by 50% or more (IoU), or when the smaller one lies 80% or more inside the larger. These are duplicate mappings and spot fires absorbed by the main fire. The largest record gives the ID and name; the outline is the union, the start the earliest, the end the latest. `merged_record_count`, `merged_event_ids` and `merged_event_names` list what was combined (330 records into 254 fires). Reburns months later stay separate.
- **Validation:** the 2019-20 season totals 5.4 Mha (union of outlines), matching the official ~5.5 Mha for NSW.
- **Size filter:** none. Tiny fires are kept, and weather, hotspot, terrain, severity and vegetation values are computed for every fire. For fires smaller than one raster pixel, the pixels the outline touches are used.
- **Council split:** each fire is split by ABS LGA 2021 boundaries. `region_burn_area_ha` is the area inside that council, and `X1_burn_area` is the whole fire.
- **Not synthetic:** every row is a mapped fire.

## Key definitions and choices

| Column | Definition | Choice / caveat |
|---|---|---|
| X2_FFDI | Maximum daily McArthur Mark 5 FFDI from the day before the start to the end (at most 60 days) | Daily Tmax, RH min and wind max from Open-Meteo ERA5 at the fire centroid. The drought factor is Griffiths (1999), from KBDI computed on NASA POWER daily rain (days under 1 mm count as dry, because gridded rain drizzles). ERA5 wind is a daily value on a 25 km grid, so peaks are below station FFDI. Use it to rank fires, not as an official FFDI |
| X3_SPEI | SPEI-3 at the ignition month | NASA POWER rain minus Hargreaves PET; normal fit per calendar month; 1991–2020 reference |
| X5_hotspot_density | DEA hotspots inside the outline + 500 m buffer during the fire, divided by the area of that buffered outline (km²) | All DEA products are counted; a VIIRS-only density is also given. Dividing by the searched area keeps tiny fires comparable |
| X6_severity | Share of burnt FESM pixels in the high or extreme class | Uses the season of the start date, or the next season if the start season maps less than 20% of the outline. 2021-22 is read at 30 m. FESM concentrates on forested and park land, so many western grass and crop fires are not mapped (`severity_note`). Fires mapped entirely as unburnt have a blank X6; `severity_share_*` shows the class mix |
| X12 / X13 | Dominant NVIS 6.0 vegetation group; mean Hansen 2000 tree cover | NVIS 7.0 is only published as a FileGDB raster, which this GDAL build cannot read |
| X15 | LGA population in the year before the fire ÷ LGA area | ABS Regional population 2024-25 (2025 boundaries) |
| X16 | Blank | No official LGA GDP exists. Proxy: total personal income (ABS) in `X16_regional_GDP_proxy_total_income_aud` |
| X17 | IRSD score | 2016 Census for fires up to 2020; 2021 Census after |
| X18 | ABS Remoteness Area at the fire centroid | 0 major city … 4 very remote |
| X19–X21 | Council cash expense cover (months), own-source revenue %, debt service ratio % | Financial year before the fire. NSW OLG Time Series Data (2013-14 to 2023-24), with AUSSEF fiscal panels filling gaps. OLG did not collect ratios for 2024-25 |
| X22 | Declared disasters for the LGA in the previous 10 years | AUSSEF disaster declarations (all hazards). Most declarations have no date field, so dates are parsed from the declaration name (e.g. "8 – 18 December 2023"). The table has few declarations before 2018, so fires before about 2020 are undercounted |
| IL_job_loss_raw | Unemployed persons in the quarter after the fire-start quarter, minus the same quarter a year earlier | DEWR SALM, smoothed LGA series |
| SL_income_drop_raw | % change in median income, fire FY vs the previous FY | ABS Personal Income in Australia. The latest release ends at FY 2022-23, so fires after June 2023 are blank |
| DL_insurance_loss_raw | Original insured loss of the ICA catastrophe linked by date | **Catastrophe level**: every linked fire shows the same value, and Black Summer includes QLD/SA/VIC. `DL_insurance_loss_area_share_proxy` splits it by burned area (an assumption, not an ICA figure) |
| DL_house_loss_raw, FP_reconstruction_gap_raw, FP_budget_crowd_out_raw, SL_vulnerable_loss_raw, IL_GRP_change_raw, X23 | Blank | No public data at fire or council level; the reason is in `dictionary` |

## Added for the Y composition (2026-09-26)

See `docs/y_composition/README.md` for why each column is needed.

| Column | Definition | Choice / caveat |
|---|---|---|
| `dwellings_census` | Private dwellings in the council, occupied + unoccupied | ABS Census; 2016 for fires to 2020, 2021 after. The 2016 interim codes of merged councils are recoded (`RECODE_2016` in `src/dwellings.py`) |
| `DL_homes_destroyed_per_1000_dwellings` (key events) | Homes destroyed in the council ÷ dwellings × 1,000 | Uses a council-specific reported figure if one exists, else whole-fire figures split by burned-area share (`DL_homes_destroyed_basis`) |
| `SL_rent_change_pct`, `_excess_pct` | Median weekly rent for new bonds, quarter after the fire vs a year earlier | NSW DCJ, Sep 2017 – Jun 2026, so fires from mid-2017. Blank where DCJ suppresses the median (10 or fewer bonds) |
| `FP_renewals_ratio_change_{event,plus1}_excess` | Building & infrastructure renewals ratio (renewal spending ÷ depreciation), change vs FY before | Capital-side rebuilding. OLG publishes no capital expenditure in dollars |
| `FP_grants_per_capita_change_{event,plus1}_excess` | Grants & contributions per resident (grants % × total revenue ÷ population) | Transfer intensity (DRFA arrives here): a control, not a loss |

## Excess-change ("abnormal") Y columns

Bowen asked for the **abnormal** impact around a fire, not the natural movement of economic or fiscal variables. A raw
before/after change also carries statewide movements: unemployment rose more in unburned NSW councils than in Black
Summer councils in 2019→2020, because of COVID. So for each council-level Y component there is also an `_excess` column:

    excess = change in this council − median change, over the same period, in NSW councils with no fire of 100 ha or more burning inside them

| Column | Change measured |
|---|---|
| `IL_unemployment_rate_change_excess_pp` | unemployment rate, quarter after the fire-start quarter vs a year earlier (SALM) |
| `SL_income_drop_excess_pct`, `SL_income_change_plus1_excess_pct` | median income, fire FY (and FY after) vs FY before (ABS PIA) |
| `IL_total_income_change_excess_pct` | total personal income, fire FY vs FY before (GRP proxy) |
| `FP_debt_ratio_change_*_excess`, `FP_operating_ratio_change_*_excess`, `FP_cash_cover_change_*_excess` | council finances, fire FY (`event`) and FY after (`plus1`) vs FY before |

Also: `SL_vulnerable_loss_excess` (income-support recipients per 1,000, DSS), `IL_business_count_change_excess_pct`
(ABS business counts; both years from the same ABS release), and `FP_service_share_change_*_excess` (crowd-out).

These are descriptive comparisons, not causal estimates. The comparison councils are mostly metropolitan, so part of
any gap can be rural-vs-city difference rather than fire. The values are still council-by-year, so every fire in the same
council-year shares them.

## Rules followed

- `data/aussef.duckdb` is opened read-only. Its hash is checked before and after every build.
- No synthetic fires. No results are described as causal.
- Downloads (under `data/`, git-ignored) are listed with hashes in the `sources` sheet.

## Key-events dataset (declared bushfire disasters)

`out/nsw_key_bushfire_events.xlsx` is the compact "key information" view: **125 declared NSW bushfire disasters** since
2015. Declarations come from three sources: the AUSSEF disasters table (2018 onward), the AUSSEF Experiment 2 ledger
(NSW RAA annual reports, 2012–17), and 21 FY2017-18 declarations recovered from an archived NSW Government page.

| Sheet | What it holds |
|---|---|
| `events` | One row per declaration: name, dates, councils, main fires, a 2–4 sentence summary, headline facts, `key_facts` (every verified fact in words) |
| `event_council` | One row per declaration × council (218): the event's fires in that council (area, share burned, peak FFDI, severity, homes destroyed), council context (X15–X22) and the Y columns with their `_excess` versions |
| `facts` | Every reported fact (181) with source, date, verbatim quote and `value_check` |
| `dictionary` | Column meanings |

Facts were collected from official reports and reputable news (spec: `data/key_events/SPEC.md`). Rules enforced by
`src/key_events.py`:
- **The number must be in its quote.** Otherwise the value is blanked (`value_check`). One named death counts as 1.
- **Hedged numbers are blanked.** For example "more than 700 ha". The original is kept in `value_as_submitted`.
- **Manual fixes after spot checks** are listed in `data/key_events/corrections.csv`.
- **Disagreements stay visible.** When sources disagree, each figure is its own row; the headline prefers the latest official source.

Most small declarations have no news coverage. Their summaries say so, and their facts stay blank.

A fire can link to two declarations when the same council was declared twice within weeks.
`also_under_declarations` flags these cases, so add up event × council rows with care.

An "X onwards" declaration runs until the council's next bushfire declaration begins, at most 180 days. A declaration
named with a single date runs 30 days.

## Sources and link checks

Every value traces to a source. The build enforces this:
- **Dictionary sources.** Every column in `dictionary` and `lga_year_dictionary` has a `source`, and the build fails if
  one is blank. Template columns with no public data say so explicitly ("none: …" or "not a data column: …").
- **Download links.** `download_links` holds the exact file, API example or page for every input.
- **Declaration documents.** Every declared event carries `declaration_source_url`: the NSW Reconstruction Authority
  FY page, the NSW RAA annual-report PDF with its page number, or the archived FY2017-18 page.
- **Fact sources.** Every fact carries `source_url`, a verbatim `quoted_text` and a `link_status`.

`src/linkcheck.py` checks every cited URL and writes the results to `out/link_check.csv`:
- A dead link with a Wayback Machine copy is replaced by the copy. The original is kept in `source_url_original`.
- A site that refuses automated checks also gets its Wayback copy where one exists.
- Links that fail the check are removed from summaries and listed in `links_removed`. These are mostly DisasterAssist
  addresses the research agents guessed, bare homepages, and Wikipedia, which is not accepted as a source.
- Local copies cited by the agents are replaced by the official file after a SHA-256 match (e.g. the NSW Bushfire
  Inquiry final report).
