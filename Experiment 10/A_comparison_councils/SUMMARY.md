# Experiment 10, Source A: audited financial statements of comparison councils (plain-English summary)

**What this is.** The audited annual General Purpose Financial Statements (GPFS) of 25 NSW councils that were NOT among the
69 fire councils, FY 2015-16 to 2023-24. They are the comparison group for the fire councils' recovery costs
(collected by the separate A_fire_councils session). No statistics were run; Ray will approve a locked prespec first.

**Scope change (2 Oct 2026, Ray via the coordinator).** The original plan covered all 59 non-fire councils. Ray capped it
at about 25 councils that look like the fire councils: OLG class Rural, Large Rural or Regional Town/City (no Metropolitan),
close to the fire zones, and of similar size. Councils already collected were kept. The fire councils' median population is
23,000 (middle half 9,700 to 56,500).

## The 25 councils and why each was chosen
Class = OLG classification from the OLG time-series data (NSW Data Panel.csv, column `classification`).
Distance = shortest distance from the council boundary to any fire council boundary (2021 LGA boundaries;
0 km = the councils share a border).

| region_id | council | OLG class | population | km to nearest fire council | years with all 5 core items | years with disaster lines | why chosen |
|---|---|---|---|---|---|---|---|
| 10050 | Albury | Regional Town/City | 50,990 | borders a fire council | 9/9 | 0 | already collected and extracted before the scope change; Regional Town/City, borders a fire council, pop 50,990 |
| 13910 | Hilltops | Large Rural | 18,776 | borders a fire council | 8/9 | 7 | already collected and extracted before the scope change; Large Rural, borders a fire council, pop 18,776 |
| 15050 | Maitland | Regional Town/City | 75,695 | borders a fire council | 8/9 | 8 | already collected and extracted before the scope change; Regional Town/City, borders a fire council, pop 75,695 |
| 16900 | Shellharbour | Regional Town/City | 68,658 | borders a fire council | 9/9 | 0 | already collected and extracted before the scope change; Regional Town/City, borders a fire council, pop 68,658 |
| 13550 | Gunnedah | Large Rural | 12,468 | borders a fire council | 9/9 | 4 | already collected and extracted before the scope change; Large Rural, borders a fire council, pop 12,468 |
| 14300 | Junee | Large Rural | 6,283 | borders a fire council | 9/9 | 4 | already collected and extracted before the scope change; Large Rural, borders a fire council, pop 6,283 |
| 15850 | Narromine | Large Rural | 6,721 | borders a fire council | 9/9 | 1 | already collected and extracted before the scope change; Large Rural, borders a fire council, pop 6,721 |
| 18200 | Wentworth | Large Rural | 6,877 | 108 km | 9/9 | 2 | already collected and extracted before the scope change; Large Rural, 108 km, pop 6,877 |
| 12900 | Forbes | Large Rural | 9,698 | borders a fire council | 8/9 | 5 | already downloaded before the scope change; Large Rural, borders a fire council, pop 9,698 |
| 11150 | Bourke | Rural | 2,870 | borders a fire council | 9/9 | 3 | already downloaded before the scope change; Rural, borders a fire council, pop 2,870 |
| 11600 | Carrathool | Rural | 2,800 | borders a fire council | 7/9 | 7 | already downloaded before the scope change; Rural, borders a fire council, pop 2,800 |
| 14950 | Lockhart | Rural | 3,117 | borders a fire council | 5/9 | 4 | already downloaded before the scope change; Rural, borders a fire council, pop 3,117 |
| 13850 | Hay | Rural | 3,005 | 95 km | 8/9 | 0 | already downloaded before the scope change; Rural, 95 km, pop 3,005 |
| 12870 | Federation | Large Rural | 12,499 | borders a fire council | 8/9 | 8 | added for similarity; Large Rural, borders a fire council, pop 12,499 |
| 14600 | Lachlan | Large Rural | 6,624 | borders a fire council | 4/9 | 4 | added for similarity; Large Rural, borders a fire council, pop 6,624 |
| 15800 | Narrandera | Large Rural | 6,015 | borders a fire council | 0/9 | 0 | added for similarity; Large Rural, borders a fire council, pop 6,015 |
| 17350 | Temora | Large Rural | 6,098 | borders a fire council | 9/9 | 9 | added for similarity; Large Rural, borders a fire council, pop 6,098 |
| 14400 | Kiama | Regional Town/City | 21,612 | borders a fire council | 9/9 | 2 | added for similarity; Regional Town/City, borders a fire council, pop 21,612 |
| 16150 | Orange | Regional Town/City | 40,619 | borders a fire council | 9/9 | 2 | added for similarity; Regional Town/City, borders a fire council, pop 40,619 |
| 12950 | Gilgandra | Rural | 4,382 | borders a fire council | 5/9 | 0 | added for similarity; Rural, borders a fire council, pop 4,382 |
| 10800 | Bland | Large Rural | 6,034 | 22 km | 9/9 | 9 | added for similarity; Large Rural, 22 km, pop 6,034 |
| 14750 | Leeton | Large Rural | 11,408 | 36 km | 9/9 | 6 | added for similarity; Large Rural, 36 km, pop 11,408 |
| 10650 | Berrigan | Large Rural | 8,519 | 48 km | 9/9 | 0 | added for similarity; Large Rural, 48 km, pop 8,519 |
| 13450 | Griffith | Regional Town/City | 25,942 | 74 km | 7/9 | 6 | added for similarity; Regional Town/City, 74 km, pop 25,942 |
| 18100 | Weddin | Rural | 3,706 | borders a fire council | 8/9 | 8 | added for similarity; Rural, borders a fire council, pop 3,706 |

Not chosen (non-metropolitan, but less similar or impossible to collect): Wollongong (population 206,000, far above the
fire councils; site blocks downloads), Coolamon (statements hosted only on a non-government Squarespace site), Central
Darling (population 1,900, very remote), and Murrumbidgee, Balranald, Edward River, Murray River and Broken Hill (50 to
240 km from the nearest fire council).

**Supplementary set (not in the 25).** Before the scope change, statements of 7 metropolitan councils had already been
extracted: Sydney, North Sydney, Mosman, Cumberland, Bayside, Canterbury-Bankstown and Canada Bay. Ray chose to keep them as
a separate set (supplementary_metro_extraction_raw.csv). They were not worked on further and are not verified.

## What was collected
- 25 councils x 9 years = 225 council-years. **193 council-years (86%) have all five core items**: capital spending,
  operating grants, capital grants, total expenses and depreciation. 32 council-years have no values.
- Gaps: Narrandera (all 9 years: its statements are no longer posted on its current website, and old links now redirect
  to the homepage); Lachlan 2015-16 to 2019-20; Gilgandra and Lockhart 2015-16 to 2018-19; Carrathool and Griffith
  2015-16 and 2016-17; Forbes 2023-24; Maitland 2019-20; 2015-16 for Hilltops and Federation (formed by the 2016
  amalgamations; earlier years belong to the predecessor councils), and for Hay and Weddin.
- 99 council-years contain at least one disaster-related line, mostly flood or storm restoration grants (e.g. "Flood
  restoration", "Storm/flood damage", "Natural disaster"). The largest totals of disaster grants over the period are
  Forbes, Weddin, Hilltops, Lachlan and Carrathool (about A$12m to A$21m each). These are raw descriptive sums, not a test.
- Downloads: 263 PDFs kept, 1.48 GB in total for the whole session, including the 59-council pass before the scope change
  (limit 4 GB; no file over 40 MB). All files are under
  OneDrive `Extracurriculars/AUSSEF/05 Data Archive/Council Financial Statements (NSW councils FY2015-16 to FY2023-24)/` (moved and renamed 2 Oct 2026; see `../PDF_RENAME_MAP_2026-10-02.csv`).

## How it was done
1. Finder agents (Sonnet), one per group of about 5 or 6 councils, looked on each council's own website (official
   *.gov.au hosts only) and downloaded through tools/dl.py. That script enforces the domain rule, the 40 MB and 4 GB
   limits and a check that the file is a real PDF, and logs URL, bytes and sha256. Each file was opened to confirm the
   council and the "year ended 30 June" date; wrong files were discarded (logged, status "discarded").
2. Extraction agents (session model), one per council, recorded each value with its exact printed label, PDF page number,
   units and column (current year vs prior year). Scanned PDFs were read as page images.
3. Verifier agents (Sonnet), one per group, re-checked a fixed sample: every 8th row plus up to 25 disaster rows per
   group. **477 of 2,934 extracted rows (16.3%) were checked against the PDF page; all 477 were confirmed** (label on
   the page, value, and current/prior column).

## Rules worth knowing when using the data
- statements_tidy.csv uses each year's **own** audited statement. A year is filled from the next year's prior-year column
  only when its own statement is missing (133 rows; the `file` column shows which document was used).
- Councils sometimes **restate** earlier figures. Examples: Shellharbour 2016-17 (total expenses 84.7m originally vs
  103.6m restated); Forbes moved 2017-18 flood money from operating to capital grants. Both versions are kept in
  extraction_raw.csv (column = prior_year rows), and the tidy table keeps the original audited figure.
- "Bushfire and emergency services" grants are funding for the Rural Fire Service and SES, **not** disaster recovery.
  They have their own item code (bushfire_emergency_services_grant).
- One disaster line can appear as two rows (an operating column and a capital column), and a council-year can have several
  disaster lines. Sum by item when needed; the `label` column tells them apart.
- disaster_expense rows include asset write-offs labelled as flood or fire damage, e.g. Gunnedah "Roads - Multiple flood
  damaged". These are accounting losses, not cash spent.
- Values are in Australian dollars (converted from $'000); capital spending is recorded as a positive number.

## Access notes
- Many council websites refuse Python's downloader (HTTP 403) but serve plain `curl` normally. With Ray's OK the downloader
  uses plain curl with its default identity: no fake browser identity, no captcha bypass. Sites that still refused curl
  were left alone and logged as blocked.
- Randwick (metropolitan, now out of scope) posts its statements via a non-government Amazon S3 link, so they were not
  downloaded.

## Files
| file | what it is |
|---|---|
| selected_25.csv | the 25 councils, class, population, distance, reason |
| downloads_log.csv | every download attempt (URL, source page, bytes, sha256, local path, status) |
| extraction_raw.csv | every line found, both columns, with page, exact label and notes (25 councils) |
| statements_tidy.csv | region_id, council, fy, item, value_aud, page, label, file (current-year values) |
| verification.csv | the 477 spot-checked rows and verdicts |
| coverage_report.csv / .md | per council-year: items found, disaster lines, finder notes |
| supplementary_metro_extraction_raw.csv | the 7 metropolitan councils extracted before the scope change |
| SPEC.md, tools/ | agent instructions and the scripts (dl.py, pdftext.py, logsrc.py, discard.py, merge.py) |
| ../../bibliography/parts/exp10_A_comparison_councils.csv | every source: downloaded PDFs (with pages used) and pages searched |
