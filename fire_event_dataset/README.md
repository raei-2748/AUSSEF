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

These are descriptive comparisons, not causal estimates. The values are still council-by-year, so every fire in the same
council-year shares them.

## Rules followed

- `data/aussef.duckdb` is opened read-only. Its hash is checked before and after every build.
- No synthetic fires. No results are described as causal.
- Downloads (under `data/`, git-ignored) are listed with hashes in the `sources` sheet.
