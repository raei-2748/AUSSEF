# AUSSEF

Research on how NSW bushfires (2015-2025) affect councils and communities: Bowen's composite impact
Y = DL + IL + FP + SL, the X variables, random forest + importance, severity tiers and a pre-fire council risk map.
Report due 11 Nov 2026.

## Start here

| Folder | What it is | Read first |
|---|---|---|
| `fire_event_dataset/` | The 96-fire x council panel (218 rows) and how it was built | [README](fire_event_dataset/README.md) |
| `Experiment 5/` | Panel random forest within councils, tested by time | [REPORT](Experiment%205/REPORT.md) |
| `Experiment 6/` | Pre-fire council risk score (Bush Fire Prone Land), tested on the 96 fires; follow-ups incl. NSW 2013, Victoria 2009 and SA fresh tests | [REPORT](Experiment%206/REPORT.md) |
| `Experiment 7/` | What fires measurably do to councils (Days 1-11): housing loss predictable, socioeconomic effects mostly below detection; rapid post-fire estimate | [README](Experiment%207/README.md) |
| `Experiment 8/` | Mechanism review: 55 ways fires affect people and councils, from 141 sources, sorted into DL/IL/FP/SL | [MECHANISMS](Experiment%208/MECHANISMS.md) |
| `Experiment 9/` | Bowen's pipeline: random forest on the composite Y, by pillar | [FINDINGS](Experiment%209/FINDINGS.md) |
| `Experiment 10/` | Council recovery costs from audited financial statements (and stopped quarterly budget reviews) | [HANDOFF](Experiment%2010/HANDOFF.md) |
| `bibliography/` | Every source used or searched, with link checks | [README](bibliography/README.md) |

Experiments 1-4 (fiscal forecasting, matched history, crowd-out, budget revisions) and the exit-road pilot are finished
and live on OneDrive (`Extracurriculars/AUSSEF/06 Finished Experiments`); they are also in git history.

## Where everything else is

- **Master workbook (live)**: `data/master_workbook/nsw_bushfires_2015_2025_XY.xlsx` (sha256 123423ea...ec3); every
  script reads it here. Do not edit it.
- **OneDrive `Extracurriculars/AUSSEF/`**: ARCHIVE ONLY, for material we no longer use (finished experiments, raw
  downloads, council PDFs already extracted, old dataset versions). Start with `00 README - What is where.md` there.
- **Google Drive `Application Folder - Ray/Extracurriculars/AUSSEF/`**: Google Docs/Sheets/Slides (Logbook, Notes,
  Syllabus, Bibliography sheet) plus the original copies of files now also on OneDrive.
- **What moved where and when**: `docs/storage/` (`MOVED_FILES.txt`, `data_archive_moves_2026-10-02.csv`).

## Other folders

```text
data/                master workbook (data/master_workbook/), canonical DuckDB model (aussef.duckdb) and build receipt
NSW Data Panel.csv   OLG council time-series panel (frozen source)
docs/                stack notes, literature notes, Y composition, storage logs
schemas/, scripts/   validation schemas and setup/export scripts
graphify-out/        code knowledge graph (tooling)
aussef_duckdb/, generated/, _site/, reports/   older database store, graph cache, site build
```

The environment is declared in `pyproject.toml` and locked by `uv.lock`.

## Research rules

- Every new statistical test is fixed in a hash-locked PRESPEC first; later changes are labelled deviations.
- Every source is logged in `bibliography/parts/`. No Australian Community Media sources.
- Missing is kept distinct from zero; "not detected" is reported with its bound, never as "no effect".
- No data or evidence files are deleted; moved files are logged in `docs/storage/`.
