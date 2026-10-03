# Experiment 14, Step 1: data check (before any download)

2 Oct 2026. Nothing has been downloaded and no v4 value has been computed. Every page opened or searched is logged in
`bibliography/parts/exp14_y_v4_2026-10-02.csv` (E14-01 to E14-23, in the main project folder).

## a) Disaster payments to households by council

| Dataset | Who / where | What it covers | Geography | Size | Status today |
|---|---|---|---|---|---|
| **Location-Based Disaster Assistance Payments** (`disaster_history_payments_2026_April_17.csv`) | NEMA; was on data.gov.au as `disaster-history-payment-by-lga` (E14-06, E14-07) | Services Australia payments (AGDRP, Disaster Payments, DRA) plus a summary of DRFA measures. Described as "Disaster history payment by LGA from 2020 onwards". Metadata reference period: **14/04/2020 to 14/11/2023**. The measures (claims, people, dollars) cannot be seen without opening the file. | LGA. NEMA's own note says some AGDRP/DRA data are summed from suburb to LGA, so a suburb that crosses two LGAs can be counted in both. | archived record 83,098 bytes (compressed), far below 40 MB | **Removed from data.gov.au.** The page now returns 404 and the catalogue API says "access denied", so it was withdrawn or made private after May 2026. The only public copy I found is the Internet Archive snapshot of the April 2026 file (E14-08). |
| DRFA Activation History by LGA (E14-11) | NEMA, data.gov.au, updated 11 Aug 2026 | Which LGAs had DRFA (and AGDRP/DRA) **activated** for each event, 2006 to now | LGA x event | 367,919 bytes CSV | Live. Gives only yes/no, with no counts of people or dollars. |
| AGD "DRP and DRA Management Information", "DRP/DRA Activation Information", NDRRA claims (E14-12 to E14-14) | Attorney-General's Dept, data.gov.au (2023 records) | Money at activation level or state level | not LGA | no files attached | Not useful. |
| NEMA LGA profiles (E14-15) | nema.gov.au | Used to be an LGA map of disaster history and assistance | LGA | n/a | "Currently being redeveloped", so not available. |
| NSW Disaster Relief Grants (E14-18, E14-19) | NSW Government / Resilience NSW | Grants to low-income, uninsured households | program pages only | n/a | I could find **no counts or dollars published by LGA**. |

**What this means for the panel.** Rows by fire season: 2014-2018 = 82 rows, 2019 (Black Summer) = 57, 2022-2024 = 79.
- Seasons up to 2018 come before the payments data start, so they cannot be covered.
- Black Summer AGDRP was mostly paid between November 2019 and March 2020. That is before the stated reference period
  (from 14 Apr 2020), so it is unclear whether Black Summer is in the file.
- 2022-2024 rows are covered only where AGDRP or DRA was activated, which is rare for smaller fires.

My expectation is that very few of the 218 rows will get a fire-matched payments value. The only way to know is to
open the file.

## b) Insurance by council

- **ICA Historical Catastrophe List** (on disk, E14-21): losses and claim counts are given **per event only**. Each
  event also lists the **postcodes affected**. For example, CAT195 (the 2019/20 bushfires) lists 159 postcodes, with
  A$2.32 bn in losses and 38,936 claims. There is no loss or claim count per postcode or per council. The master
  columns `DL_insurance_loss_raw` and `DL_insurance_loss_area_share_proxy_in_council` divide each event's loss by
  burned-area share, so they are a proxy, not a council-level measure.
- **PERILS AG** (E14-20) holds insured bushfire losses by postcode for 2019/20 (A$1,861 m footprint), but sells them
  to subscribers only. They are not public.
- **APRA, the NSW Government and ICA media releases** (E14-22, E14-23) give only state-level shares (for example,
  NSW was about 81% of 2019/20 losses, A$1.88 bn). Nothing is published by council or postcode.
- **Conclusion:** no public insured-loss or claims data exist at council level for NSW bushfires 2015-2025. v4 leaves
  insurance out of the pillars. X23 (share of homes owned outright) stays as the underinsurance proxy.

## Other facts checked for the PRESPEC (on disk, no download)
- Deaths: master `SL_deaths_sourced` is recorded for 142 rows, 17 of them above 0 (29 deaths in total).
- Injuries: `SL_injuries_sourced` is recorded for 10 rows (48 in total), so it stays descriptive only.
- Experiment 13: its `audit/` folder is empty (22:19 today), so it is not finished and audited. v4 IL = v3 IL without
  traffic.

## Decisions needed from Ray
1. Download the archived NEMA payments CSV from the Internet Archive copy (about 0.1-1 MB)? It is the official NEMA
   file, but it is served by a third-party archive because data.gov.au has withdrawn it.
2. Also download DRFA Activation History by LGA (368 KB, live on data.gov.au)? It would let us tell "no payment
   because nothing was activated" (a true zero) apart from "missing".
3. Where should Experiment 14 live? Experiments 5-13 and `bibliography/` exist only in the main project folder (they
   are untracked in git), but this session runs in a git worktree, and a safety hook blocks file writes to the main
   folder.

## After Ray's OK (2 Oct 2026): what the two files contain
Both files were downloaded into `raw/` (bibliography E14-24, E14-25, with sha256). Both are keyed by disaster AGRN,
the same event ID the panel uses.
- **Payments file** (5,825 rows; columns: location, disaster AGRN, payment type, eligible / ineligible / received
  claims, dollars granted and paid; small counts shown as "<20"). The main Black Summer event (**AGRN 871**, 50 panel
  rows) is **not in the file**. For the North Coast fires (**AGRN 880**, 7 panel rows), household payments (AGDRP)
  are listed for Armidale (380 eligible claims), Inverell (552), Tenterfield (449), Kyogle (38) and Tamworth (<20);
  only **Kyogle** has an AGRN 880 panel row. No AGDRP or DRA is listed for any 2022-2024 panel event. Some "Date of
  Data" values for AGRN 880 fall before the event started, so the dates in this file are not reliable.
- **DRFA activation file**: the AGDRP and DRA flags are set only for events starting in 2021 or later, and are 0 for
  every panel AGRN.
- **Decision (in PRESPEC, before any v4 value):** payments are not a v4 indicator. In the end they cover 1 of the 218
  rows (Kyogle, 4.3 eligible AGDRP claims per 1,000 residents; `results/DESC_PAYMENTS_AGRN880.csv`).
