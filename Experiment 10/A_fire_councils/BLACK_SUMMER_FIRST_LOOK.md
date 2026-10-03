# Black Summer first look: council fire grants and capital spending (descriptive only)

2 Oct 2026. No statistical test; nothing pre-registered. Table: `BLACK_SUMMER_FIRST_LOOK.csv`.

## Data
- 18 audited statements (FY2019-20 and FY2020-21) for the 9 councils with the most Black Summer homes destroyed:
  Eurobodalla, Bega Valley, Shoalhaven, Snowy Valleys, Clarence Valley, Mid-Coast, Glen Innes Severn, Kempsey,
  Wingecarribee (1,960 of 2,483 Black Summer homes destroyed in the panel). FY2018-19 comes from the prior-year column.
- 14 fetched by script (Ray approved, 2 Oct); Eurobodalla and Shoalhaven downloaded by Ray in a browser.
  Files: OneDrive `05 Data Archive/Council Financial Statements .../Fire councils/`. Log: `work/batch_bs/`.
- Extracted from the PDF text layer (pypdf): income statement, cash flow, and fire-related lines of the grants note.
  Check: every FY2019-20 value was compared with the prior-year column of the FY2020-21 statement: 49 match,
  6 differ because the council restated total expenses or depreciation (all under 1%). Pages were not rendered
  (no PDF renderer on this machine).

## Measure
"Fire grants" = grants-note lines labelled bushfire and emergency services, bushfire services, (NSW) rural fire
services, fire protection, emergency services, or federal bushfire relief (operating + capital), as % of total
expenses. Storm/flood lines are excluded.

**Rule change.** Experiment 10's summary treated "Bushfire and emergency services" as routine RFS funding. In these
statements it is where Black Summer recovery money was booked (Snowy Valleys: A$1.6m to A$11.4m; Bega Valley: A$0.6m
to A$6.9m plus a new A$2.2m "Bushfire services" line). So this category cannot be dropped by label; its jump above the
council's own pre-fire level is the signal.

## What it shows
| | FY2018-19 (before) | FY2019-20 (fire year) | FY2020-21 (year after) |
|---|---|---|---|
| Fire grants, % of spending, median of 9 councils | 0.5% | 2.2% | 1.3% |
| Capital spending, % of total expenses, median | 27% | 33% | 37% |

- 8 of 9 councils show a rise in fire grants from about 0.5% of spending to 1.5-17%; the peak is in the fire year or the
  year after (Bega Valley and Snowy Valleys a year late). Largest: Snowy Valleys 17.0%, Bega Valley 8.4%, Eurobodalla 5.9%.
- Shoalhaven shows no rise in these lines (0.6% to 0.3%); its recovery money must be booked under other headings.
- Capital spending rises the year after the fire in the hardest-hit councils (Eurobodalla 31% to 57%, Bega Valley
  35% to 54%, Kempsey 33% to 43%): the rebuild shows up a year later.
- Comparison councils (unburned) on the same fire-service lines: median 0.6% (FY2018-19), 0.6%, 0.8%; a few spike
  (Narromine 13.6% in FY2020-21, Hay 4.9%), probably RFS capital projects. So single spikes happen without fires;
  the fire signal is the consistent rise across the burned councils.

## Limits
- 9 councils, one fire season, label-based lines; not a test.
- Recovery money also arrives under other headings (transport, community, "natural disaster" flood/storm lines; e.g.
  Clarence Valley's A$7.08m storm/flood grants described as bushfire/flood funding are excluded), so these figures
  are a lower bound.
