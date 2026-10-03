# Project bibliography — summary (2 Oct 2026)

## What is here
| File | What it is |
|---|---|
| `BIBLIOGRAPHY.xlsx` | The bibliography to check. Sheet **All** plus one sheet per source type. |
| `BIBLIOGRAPHY.csv` | The same table as CSV. |
| `parts/*.csv` | Each session's own list. Never edited by the merge. `parts/backfill_existing.csv` holds everything that was already in the project before today. |
| `BROKEN_LINKS.csv` | Rows whose link is broken, failed or gave a server error (281). |
| `MISSING_URLS.csv` | Rows with no URL and no DOI (136). |
| `ACM_FLAGGED_EXCLUDED.csv` | 38 ACM newspaper links found during the backfill and **left out** of it. |
| `acm_hosts.txt` | List of ACM websites. The merge uses it to fill the `acm_flag` column. |
| `link_status.csv` | Link-check results, one row per URL. |
| `merge_bibliography.py` | Re-run after any session adds rows: `python3 bibliography/merge_bibliography.py` |
| `check_links.py` | Checks links, then re-merges: `python3 bibliography/check_links.py`. It skips URLs checked in the last 7 days. |

**How the merge works.** It joins every `parts/*.csv`. Two rows count as the same source when they have the same URL (ignoring http/https, `www.` and a trailing slash), the same DOI or the same sha256. Merged rows keep every `used_in` value and every note.

**Columns the merge adds.** `bib_id`, `acm_flag`, `link_status`, `http_code`, `final_url` (where a redirect ended up), `link_checked_date`, `part_file` (which part files the row came from) and `n_merged` (how many rows were merged into it).

**Moved files.** Some files were moved to Google Drive (see `../MOVED_FILES.txt`), for example the 238 QBRS PDFs. For those rows the part files still give the old `local_path`, and the merged table adds a note saying where the file now lives on Drive.

## Counts
**Total: 4,340 distinct sources**, merged from 4,452 rows in 7 part files. Of the 4,340, 2,172 are marked "searched, not used". Most of those come from Experiment 8's mechanism searches and from the Experiment 10 council-PDF searches.

| source_type | count |
|---|---|
| other | 1,470 |
| government_page | 715 |
| financial_statement | 595 |
| dataset | 370 |
| pdf_report | 347 |
| budget_review | 302 |
| web_page | 237 |
| journal_article | 137 |
| news | 122 |
| survey | 38 |
| working_paper | 7 |

- **Where "other" comes from.** Almost all of it (1,449 rows) is Experiment 8's search log, which labelled its search hits "other".
- **Rows per part file:**

| Part file | Rows |
|---|---|
| exp8_mechanisms | 1,768 |
| backfill_existing | 987 |
| exp10_A_fire_councils | 612 |
| exp10_B_qbrs | 611 |
| exp10_A_comparison_councils | 387 |
| exp9_rf_pipeline | 8 |

**Backfill on its own** (`parts/backfill_existing.csv`, 987 sources):
- 281 datasets, 251 government pages, 185 PDF reports, 95 journal articles, 92 news items, 59 web pages, 17 other, 7 working papers.
- How it was built: 1,363 harvested rows were deduplicated down to these 987.
- Sources it covers:
  - fire_event_dataset: manifest, download_links, link_check, both copies of the workbook (key_sources, key_facts, download_links, data_sources, codebook, insured_loss_reported) and the house-loss and death reference columns, with quotes.
  - Experiment 6 and Experiment 7: FINDINGS, PRESPEC, DAY7_DOWNLOADS and the papers they cite.
  - `docs/literature` and `docs/y_composition`.
  - The literature and ISEF notes in memory.
- Accuracy check: 30 randomly chosen URLs were each found word for word in the project files or the workbooks, so none look invented.

## Link check (2 Oct 2026)
Each link got a HEAD request, then a GET if needed. The checker used a normal browser User-Agent and waited at least 2 seconds between requests to the same site.

| link_status | rows | meaning |
|---|---|---|
| OK | 2,852 | link works |
| BLOCKED | 1,058 | the site refused an automated check (mostly 403). These are mostly council websites: Mid-Western, Snowy Valleys, Clarence, Coffs Harbour, Eurobodalla, Cessnock and others. A further 41 are journal DOIs. They usually open fine in a browser, so check by hand. |
| BROKEN | 181 | 404 or another 4xx error |
| FAILED | 92 | the site could not be reached at all (DNS, timeout or SSL error) |
| REDIRECT | 13 | left on a redirect (data.gov.au) |
| SERVER ERROR | 8 | 5xx error |
| NO URL | 136 | no URL or DOI recorded |

**Broken or failed links worth knowing about** (full list in `BROKEN_LINKS.csv`):
- **Backfill: 37 broken, 6 failed, 1 server error.**
  - Several are API base addresses or URL templates rather than real pages: NASA POWER, the DEA Hotspots WFS, the terrain-tile `{z}/{x}/{y}` template, and the night-lights and REDS folders. Called without parameters they return an error, but the data was downloaded fine. These are not real problems.
  - The rest are genuinely dead. They include 27 disasterassist.gov.au disaster pages, Blue Mountains Council (15) and Kyogle Council (11) pages, and a few news stories.
  - The project's earlier `link_check.csv` had already marked 27 links dead.
- **Experiment 8: 90 broken links**, mostly search hits.
  - It also contains 56 addresses on development or test servers that are not public sites, such as `devweb.dga.links.com.au`, `phoenix.*.edsqa01.aws.sbs.com.au` and `uatweb.datansw.links.com.au`. These should be replaced with the public URL or dropped. That is a job for the Experiment 8 session, since its part file is not edited here.

## Items missing URLs (136; full list in `MISSING_URLS.csv`)
- 117 are from the backfill, all marked "NEEDS URL" in notes. 75 of them have a local copy (`local_path`).
- The main groups:
  - 41 files saved in `fire_event_dataset/data/house_loss/` with no original link recorded: 7 AIDR reports, 8 RFS annual reports, 25 RFS media releases and the Coroners Court paper.
  - A handful of codebook sources that are named but never linked, such as ABS Census, ABS Weekly Payroll Jobs and the Tourism Research Australia LGA profiles. The profile URLs are in `fire_event_dataset/data/raw/il/urls.txt`.
  - Papers and ISEF projects mentioned in notes or memory with no DOI or link.
- 19 are from other sessions: Experiment 8 (10), Experiment 9 (7) and Experiment 10A (2).

## ACM (Australian Community Media)
- **Backfill.** 38 ACM articles were found in the workbooks and left out (`ACM_FLAGGED_EXCLUDED.csv`). They are from the Newcastle Herald, Canberra Times, The Land, Bega District News, Northern Daily Leader and others.
  - Two of them (Bega District News and Canberra Times) are cited as evidence in the workbook: an insured-loss figure and a key fact.
  - Those two need a non-ACM replacement source.
- **Other sessions.** Their part files still contain 106 ACM rows: 105 in Experiment 8 (mostly "searched, not used") and 1 in Experiment 10B.
  - These are marked `acm_flag = "ACM - do not use"` in the merged table, not removed, because those files belong to other sessions.
- `cvnews.com.au` (Clarence Valley) was kept because ACM ownership could not be confirmed.
