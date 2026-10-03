# Experiment 18 inputs: inventory (2 Oct 2026 night)

## Downloaded (official abs.gov.au only, release 2023-24, published 25 Mar 2026)
Folder: inputs/abs_io/ (sizes and sha256 are in bibliography/parts/exp18_hybrid_2026-10-03.csv, rows E18-IO0..IO5)
- 520905500105.xlsx  Table 5, industry-by-industry flow table (direct allocation of imports), 114 industries
- 520905500106.xlsx  Table 6, direct requirement coefficients
- 520905500107.xlsx  Table 7, total requirement coefficients (Leontief inverse; gives Type I output multipliers)
- 520905500102.xlsx  Table 2, inputs by industry (includes compensation of employees row P1, needed for Type II household-income closing)
- 520905500120.xlsx  Table 20, employment by industry (persons and FTE, for jobs per $ of output)
- release_page_latest.html  the release page used to find the files
All files are well under 40 MB (each 0.2-0.3 MB). Nothing else was downloaded.
Note: Table 7 is a national table. It must be regionalised with location quotients before use for a council.
Type II needs household consumption shares, which are in the final-use columns of Table 2 (not yet processed).

## On disk, usable
1. Tourism visitor profiles by council (TRA). 62 NSW LGA files for 2017 (visitors, nights, spend in $m, split international / domestic overnight / domestic day; 4-year average 2014-17).
   2024 file is only a list of LGA names (no numbers). So spend by council exists for 2017 only.
   NOTE: the paths in the task text (fire_event_dataset/data/raw/il/...) no longer exist locally. The files were moved to OneDrive:
   ~/Library/CloudStorage/OneDrive-KnoxGrammarSchool/Extracurriculars/AUSSEF/05 Data Archive/Fire Dataset Build Inputs (only needed to rebuild the fire dataset)/ABS Data by Region - income and labour (14100DO)/tra_lga_2017/ and tra_lga_profiles_2024_list.xlsx
   (also listed in docs/storage/data_archive_moves_2026-10-02.csv). Read-only use is fine.
   Gap: some NSW councils may have no 2017 file, and unreliable cells are marked 'np' or '-'. Missing stays missing.
2. Census industry of employment by LGA, NSW: 2016 (G51A-D) and 2021 (G54A-D) CSVs under fire_event_dataset/data/abs/gcp2016 and gcp2021. Counts by industry division, sex and age. Enough for location quotients (council share / NSW share) at division level.
   Master industry shares also come from Experiment 7/build_y2.py load().
3. Fire outlines (fire_event_dataset/data/cache/fires.parquet) and manifest.csv, for linking fires to councils.

## Farm output per hectare
Nothing usable on disk. The manifest holds only news and report pages that mention hectares burned. There is no farm output, farm gross value or land-use area table. Not downloaded (rule).
Consequence: farm losses cannot be priced from data in hand. Use the Census agriculture employment share and the IO agriculture rows only, and label farm output as missing.

## Match between IO industries and Census divisions
IO has 114 industries; Census has ~19 divisions. A concordance (IO to ANZSIC division) is needed. IO industry codes follow ANZSIC, so this is a lookup, not a data problem.
