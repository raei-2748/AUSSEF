# Shared instructions for the DL-fill source scan

CONTEXT. The AUSSEF dataset has one row per (NSW declared bushfire event = DRFA declaration 'agrn') x (council/LGA). 218 rows. The direct-loss
variable DL is built from HOMES DESTROYED in that council for that event, divided by the council's dwellings. It is filled for only 90 rows;
128 rows are missing, nearly all small fires (median 0.3% of the council burned). Your job: for the missing rows in your slice, find a
published figure for HOMES/HOUSES/DWELLINGS/RESIDENCES destroyed (and damaged if given), or an explicit statement that NO homes were lost, for the
fire(s) in that event in that council.

The missing rows for your slice are in the brief file named in your task (event, council, fire start, burned ha, main fires, towns).
`used_sources.txt` lists sources already used - do not spend time re-reporting those, but a NEW fact from them (a fire nobody extracted) is welcome.

RULES (strict).
1. Preferred sources, best first: NSW RFS (media releases, Bush Fire Bulletin issues, annual reports, RFS incident pages, Building Impact Assessment),
   NSW Reconstruction Authority / Resilience NSW / NSW Government ministerial releases, Disaster Assist (disasterassist.gov.au) and DRFA pages, NSW Parliament Hansard and
   answers to questions on notice, NSW Coroner, AIDR Knowledge Hub / Major Incidents Reports, council websites/minutes/annual reports, Natural Hazards Research Australia,
   ABC News (ABC is allowed), NSW Police/SES releases. Label each source_type as official / council / news / other.
2. NEVER use Australian Community Media (ACM) mastheads or anything on these domains: newcastleherald, canberratimes, northerndailyleader, namoivalleyindependent, armidaleexpress,
   gleninnesexaminer, inverelltimes, tenterfieldstar, dailyliberal, westernadvocate, goulburnpost, cowraguardian, centralwesterndaily, mudgeeguardian, lithgowmercury, singletonargus,
   muswellbrookchronicle, sconeadvocate, maitlandmercury, illawarramercury, begadistrictnews, naroomanewsonline, bayandbasin, southcoastregister, portnews, macleayargus, manningrivertimes,
   theland.com.au, farmonline, cessnockadvertiser, portstephensexaminer, greatlakesadvocate, dailyexaminer, coffscoastadvocate (ACM bars AI use). If a search result is on those domains, skip it.
3. You may READ pages with WebSearch and WebFetch (including PDFs). Do NOT download or save any file to disk (no curl/wget -o, no saving PDFs). Do not modify anything outside the `research/` folder named in your task.
4. WebFetch answers are produced by a small model and can paraphrase or hallucinate. Ask it for VERBATIM sentences ("quote the exact sentence containing the number"). Set quote_verified=yes ONLY when the tool
   returned the sentence in quotation marks and it clearly comes from the page; otherwise quote_verified=no. Never invent a quote. Quotes <= 25 words.
5. Never invent a number. Zero is allowed only when a source says no homes/houses/properties were lost/destroyed for that fire or event (state which).
6. Fire-to-row matching is the hard part. State in match_note WHICH fire the figure is for, and whether the figure is for the whole event, a named fire inside the council (a lower bound if other
   fires burned in that council), or the whole council. If a fire crosses two councils and the source does not say where the houses were, put scope=multi_council and list the councils; do not pick one.
7. Record negative results too (what you searched, what you found nothing on) - they tell us the coverage of each source.
8. Pronouns: use they/them for people whose pronouns are unknown.

OUTPUT. Write exactly two files in the `research/` folder (absolute path in your task):
 (a) findings_<slice>.csv with columns: agrn, region_name, metric (homes_destroyed | homes_damaged | no_homes_lost), value (integer; 0 for no_homes_lost), hedged (True/False, e.g. "more than", "about"),
     scope (council_total | fire_in_council | whole_event | multi_council | season_total), source_type, source_title, url, page_or_section, quote, quote_verified (yes/no), as_of_date,
     confidence (high|medium|low), match_note
 (b) notes_<slice>.md: (i) a table of every agrn in the slice with rows_missing, rows_you_could_fill, main source; (ii) sources you searched with no result; (iii) any NEW dataset/portal you found that lists building
     damage per fire or per LGA (URL + what it holds + how far back it goes + whether it needs a download); (iv) a candid reliability comment.
Return a 10-line summary in your final message.
