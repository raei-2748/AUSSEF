# Key-events research spec (shared by all agents)

Goal: for each **declared NSW bushfire disaster** in your group, collect the key facts reported by official sources and
reputable news, so the mentor has a compact "key information" dataset. Input list: `seed_events.csv` in this folder
(columns: agrn, declaration_name, decl_start, decl_end, councils, main_fires, linked_burn_area_ha ...).
`agrn` values starting `RAA-` are declarations taken from NSW Rural Assistance Authority annual reports with no AGRN
number recorded; try to find the real AGRN and the declaration name.

## Sources (in order of preference)
1. Official: NSW RFS media releases / annual reports / Bush Fire Bulletin, NSW Reconstruction Authority / Resilience NSW,
   DisasterAssist event pages (you may open individual AGRN pages; do not bypass any CAPTCHA or script the search page),
   NSW Government media releases, coronial reports, AIDR Knowledge Hub, council media releases.
2. Reputable news: ABC News, SMH, The Guardian Australia, regional papers (e.g. Canberra Times, Newcastle Herald, local
   ACM mastheads), AAP. No paywall bypassing.
3. Wikipedia only as a pointer to a primary source (record the primary source, not Wikipedia).
Use WebSearch / WebFetch; if a site blocks fetching, use curl with a browser User-Agent ("Mozilla/5.0"); if still
blocked, skip it.

## Output 1: `facts_<group>.csv` (one row per fact per source)
Columns: `agrn, declaration_name, council, fire_name, fact, value, unit, as_of_date, source_title, publisher,
source_url, source_type, quoted_text, notes`
- `council`: the NSW LGA the fact refers to, or `ALL` if it is for the whole event.
- `fact` must be one of: `homes_destroyed`, `homes_damaged`, `outbuildings_destroyed`, `facilities_destroyed`,
  `deaths`, `injuries`, `people_evacuated`, `evacuation_centres`, `livestock_lost`, `agricultural_loss_aud`,
  `fencing_km_lost`, `businesses_affected`, `power_customers_without_supply`, `roads_closed`, `schools_closed`,
  `area_burned_ha`, `insured_loss_aud`, `insurance_claims`, `recovery_funding_aud`, `emergency_warning_level`
  (value = highest warning: Advice / Watch and Act / Emergency Warning), `fire_danger_rating`
  (value = highest, e.g. Catastrophic), `cause`, `other`.
- `value`: the number exactly as reported (text allowed only for warning level, danger rating, cause, other).
- `quoted_text`: short verbatim quote containing the value (under 30 words).
- `as_of_date`: date of the report (figures change; later official totals are preferred but keep both rows).
- NEVER estimate, round, add up, or infer a number. If a source says "more than 60", put value blank and the words in
  notes. Blank is not zero. Different sources disagreeing = separate rows.

## Output 2: `summaries_<group>.csv` (one row per event)
Columns: `agrn, real_agrn_if_found, declaration_name, official_name_if_found, start_date, end_date, councils,
main_fires, towns_affected, summary, key_sources`
- `summary`: 2–4 sentences in your own words (no copying): what burned, where, when, main impacts.
- `key_sources`: up to 3 URLs.

## Rules
- Write only inside `/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/key_events/`.
- Never write to `/Users/ray/Research/AUSSEF - Local/data/aussef.duckdb`; no git commits; no Google Sheets; send no personal data.
- Spend effort where impact is: events with many councils / large burned area / known losses first. It is fine to
  record "no news coverage found" in the summary for small events.
- Report back: events covered, facts per type, events with no coverage, real AGRNs found, conflicts, and any caveats.

## Saving (important)
Append to your CSVs after EACH event is finished (write the header once, then append rows), so work survives if you
are stopped. Before starting, read your own facts_/summaries_ files if they exist and skip events already summarised.
