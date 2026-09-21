# Step 3 scoping: did the exits close at the same time?

Status: scoping only. Nothing has been downloaded or computed, and this needs its own plan and approval.

## Why timing matters
Stages 1 and 2 use final fire perimeters, as if every road inside closed at the same moment. That
overstates simultaneous failure, so R is an upper bound. The real question for evacuation is whether a
town's exits were cut **at the same time**, or one after another with time to leave in between.
Daily satellite fire detections can date when fire reached each exit road.

## Candidate data sources (checked read-only on 2026-09-21)

| Source | Coverage | Detail | Access | Notes |
|---|---|---|---|---|
| **DEA Hotspots** (Geoscience Australia) | 27 Aug 2002 to present | MODIS (Aqua), VIIRS (S-NPP, NOAA-20/21), Himawari AHI (geostationary, about every 10 min) | Public WFS/WMS; no account for the web service | Location accurate to ±375 m at best (VIIRS). Polar orbiters pass 4–7 times a day. Cloud, smoke and canopy hide fires, and cool fires are often missed. GA says it is "not designed to be used in isolation". |
| **NASA FIRMS** | MODIS from Nov 2000; VIIRS S-NPP from Jan 2012; VIIRS NOAA-20 from Apr 2018 | 1 km (MODIS), 375 m (VIIRS) | Archive download by emailed request; the API needs a free MAP_KEY | **You would need to register for the key or request yourself.** I can't create accounts. |

Sources: [DEA Hotspots knowledge hub](https://knowledge.dea.ga.gov.au/data/product/dea-hotspots/index.html),
[DEA Hotspots WFS](https://hotspots.dea.ga.gov.au/geoserver/wfs?service=wfs&version=1.1.1&request=getcapabilities),
[FIRMS archive download](https://firms.modaps.eosdis.nasa.gov/download/),
[FIRMS data availability API](https://firms.modaps.eosdis.nasa.gov/api/data_availability/).

**Coverage fit:** part A (2019–23) is fully covered. Part B (1950–2019) is covered only for fires
from late 2002 onwards (DEA) or late 2000 onwards (FIRMS MODIS). Older fires cannot be timed with satellites.

## Proposed method (to be pre-registered separately)
1. For every town–fire pair where at least one exit was cut, find each cut exit's burned road edges.
2. Date each exit's closure as the earliest hotspot within about 375 m (VIIRS) or 1 km (MODIS) of those edges, inside the fire's date window.
3. Call a full cut-off **simultaneous** only if all exits were dated within a set window, for example the same 12 hours. The window would be pre-registered, with sensitivity at 6 and 24 hours.
4. Recompute the pooled ratio with that stricter definition (R_timed ≤ R). If R_timed stays above 1, the finding survives the timing correction.
5. Report exits with no hotspot as "undated", never as "not closed".

## Risks
- Smoke and cloud during big fires hide detections, so some exits will be undated.
- ±375 m to 1 km location error is coarse next to a road; a hotspot near a road does not prove the road burned.
- Satellite passes give a few observations a day, so timing is only known to within hours.
- Download size depends on the chosen area and dates. It should be scoped per fire (bounding box and date range) rather than all of NSW.

## Decisions needed from you
- Data source: DEA Hotspots (public, no account, recommended) or also NASA FIRMS (you register).
- The simultaneity window.
- Whether to time part A only (fully covered) or also part B fires from 2002 onwards.
