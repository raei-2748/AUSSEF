# Project bibliography (every source, every session)

Ray's rule (2 Oct 2026): nothing is read, scraped, downloaded or cited without being recorded here. At the end of the
project this becomes one big bibliography that Ray can check link by link.

## How to record
Each session/agent appends rows to ITS OWN file `bibliography/parts/<session-or-experiment>.csv` (never edit another
session's file; avoids write clashes). A consolidation step merges all parts into `bibliography/BIBLIOGRAPHY.csv` and
`BIBLIOGRAPHY.xlsx`.

Columns (CSV, UTF-8, header row):
source_id, title, author_or_publisher, year, source_type (dataset | pdf_report | financial_statement | budget_review |
journal_article | working_paper | news | web_page | government_page | survey | other), url, doi, accessed_date (YYYY-MM-DD),
local_path (if downloaded, relative to /Users/ray/Research/AUSSEF - Local), bytes, sha256, used_in (experiment / file),
what_it_was_used_for, pages_or_table (exact page/table/cell used), quote_or_value (short, <= 25 words), notes

Rules: one row per distinct source (a PDF, a dataset file, an article, a web page). If a page was only searched but
not used, still record it with used_in = "searched, not used". Never invent URLs; if a link fails, record it with
notes = "link failed <date>".
