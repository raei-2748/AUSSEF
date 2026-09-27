# Strand B: Empirical and grey literature on the economic impacts of bushfires and wildfires

*For the AUSSEF outcome index Y = f(DL, IL, FP, SL): NSW bushfires 2015–2025, measured at fire × LGA level*

Compiled 2026-09-26. **How citations were checked:** each DOI was resolved through the Crossref API. Abstracts were pulled from OpenAlex where available. Grey literature was checked against the official URL, and the PDF was read where possible. Status tags:
- **[V]**: bibliographic details confirmed and the findings checked against the abstract or full text.
- **[V-bib]**: bibliographic details confirmed, but the findings come from a secondary summary (FRAMES catalogue, publisher news, or a search snippet) and should be spot-checked before quoting.
- **[PV]**: partially verified; the caveat is stated in the entry.

---

## A. Direct losses (DL): buildings, lives, insured losses

### 1. Filkov, Ngo, Matthews, Telfer & Penman (2020) [V]
**Citation.** Filkov, A.I., Ngo, T., Matthews, S., Telfer, S., & Penman, T.D. (2020). Impact of Australia's catastrophic 2019/20 bushfire season on communities and environment. Retrospective analysis and current trends. *Journal of Safety Science and Resilience*, 1(1), 44–56. https://doi.org/10.1016/j.jnlssr.2020.06.009

**Summary.** A descriptive retrospective of fire seasons from March 2000 to March 2020 in NSW, Victoria and South Australia, using data requested from fire and forest agencies. By March 2020 Black Summer had burnt about 19 Mha, destroyed more than 3,000 houses and killed 33 people. It was unprecedented on every impact category, and NSW had the largest recorded forest fire in Australian history.

**Outcomes and measurement.**
- Outcomes: number of fires, burned area (ha), civilian and firefighter fatalities, houses lost, fire weather.
- Data: agency records.
- Unit and window: state × fire season.

**Identification.** None; descriptive trends only.

**Magnitudes.** NSW had its largest burned area in 20 years. Victoria had its most fires and second-highest house loss. South Australia had its highest house loss in 20 years.

**Implication for AUSSEF Y.** DL: supports houses destroyed, fatalities and burned area as the core DL triad. Agency-sourced house-loss counts are the standard.

### 2. Blanchi, Leonard, Haynes, Opie, James & Dimer de Oliveira (2014) [V]
**Citation.** Blanchi, R., Leonard, J., Haynes, K., Opie, K., James, M., & Dimer de Oliveira, F. (2014). Environmental circumstances surrounding bushfire fatalities in Australia 1901–2011. *Environmental Science & Policy*, 37, 192–203. https://doi.org/10.1016/j.envsci.2013.09.013

**Companion paper.** Blanchi et al. (2014). Bushfire fatalities and house loss in Australia: exploring the spatial, temporal and localised context. *Advances in Forest Fire Research*, 685–695. https://doi.org/10.14195/978-989-26-0884-6_77

**Summary.** Builds a national database of 825 bushfire fatalities across 260 fires between 1901 and 2011, and analyses 674 civilian deaths against weather (FFDI), proximity to fuel and activity at the time of death. Fatalities are highly concentrated: the 10 worst fire days account for 64% of civilian deaths, and more than half occurred on days with FFDI above 100 ("catastrophic").

**Outcomes and measurement.**
- Outcomes: fatalities (location and circumstance); the companion paper covers house loss.
- Data: CSIRO/Risk Frontiers database.
- Unit: individual fatality and fire event, geolocated.

**Identification.** Descriptive; conditional distributions over weather and fuel.

**Magnitudes.** 58% of deaths occurred in the open, 28% in structures and 8% in vehicles. Above FFDI 100, more than 60% died inside structures.

**Implication for AUSSEF Y.** DL/SL: fatalities are extremely skewed and zero for most fire × LGA cells. Use them as a severity flag or a log/indicator component rather than a linear term.

### 3. McAneney, Sandercock, Crompton, Mortlock, Musulin, Pielke & Gissing (2019) [V]
**Citation.** McAneney, J., Sandercock, B., Crompton, R., Mortlock, T., Musulin, R., Pielke Jr, R., & Gissing, A. (2019). Normalised insurance losses from Australian natural disasters: 1966–2017. *Environmental Hazards*, 18(5), 414–433. https://doi.org/10.1080/17477891.2019.1609406

**Earlier version.** Crompton, R.P., & McAneney, K.J. (2008). Normalised Australian insured losses from meteorological hazards: 1967–2006. *Environmental Science & Policy*, 11(4), 371–378. https://doi.org/10.1016/j.envsci.2008.01.005

**Summary.** Normalises the Insurance Council of Australia (ICA) Disaster List to 2017 values. It scales historical losses by the number and nominal cost of dwellings, and adjusts for building-code improvements in cyclone areas. 94% of normalised losses are weather-related (bushfire, cyclone, flood, storm). After normalisation there is no trend in losses, so rising costs are driven by exposure.

**Outcomes and measurement.**
- Outcome: insured loss per catastrophe event (AUD).
- Data: ICA Disaster List.
- Unit and window: event × season (July–June).

**Identification.** Normalisation by exposure (dwelling counts × dwelling values), not causal.

**Magnitudes.** The costliest single event is the 1999 Sydney hailstorm (AUD 5.6bn normalised). Bushfire is one of the four main weather perils.

**Implication for AUSSEF Y.** DL: supports normalising DL by the exposed dwelling stock or value (loss ÷ exposure) so events are comparable across 2015–2025. Insured losses are available only per event, not per LGA.

### 4. Insurance Council of Australia: 2019–20 bushfire catastrophe (CAT195) [PV]
**Source.** ICA catastrophe declaration and loss estimates, reported in *Insurance Catastrophe Resilience Report 2020–21* (https://insurancecouncil.com.au/wp-content/uploads/2021/09/ICA008_CatastropheReport_6.5_FA1_online.pdf) and in trade press (e.g. https://www.insurancebusinessmag.com/au/news/breaking-news/revealed-insurance-bill-for-201920-summer-catastrophes-223760.aspx).

**Summary.** The ICA declared the 2019–20 fires a catastrophe on 9 November 2019. Secondary sources report about 38,181 claims and roughly AUD 2.32bn in insured losses, 81% of them in NSW. Other reports give about AUD 1.9bn, so the figure moved as claims matured.

**Outcomes and measurement.**
- Outcomes: claims count and insured loss per CAT event.
- Unit: event, with a state split.
- Not available at LGA level publicly.

**Caveat.** Figures were taken from secondary reports; the ICA PDF was not read line by line.

**Implication for AUSSEF Y.** DL: useful for event-level validation of DL rankings. It cannot be the LGA-level DL measure, so use counts of houses destroyed or damaged instead.

### 5. NSW Bushfire Inquiry (Owens & O'Kane, 2020) [V]
**Citation.** Owens, D., & O'Kane, M. (2020). *Final Report of the NSW Bushfire Inquiry*. NSW Government, 31 July 2020. https://apo.org.au/node/307786 (mirror: https://www.bluemountains.org.au/documents/bushfires/final-report-of-the-nsw-bushfire-inquiry-31jul20.pdf)

**Summary.** The NSW Government's independent inquiry into the 2019–20 season, with 76 recommendations. For NSW it records 2,476 homes destroyed, 1,034 damaged and 5.5 Mha burned. Its impact accounting relies on RFS building impact assessments (destroyed or damaged, by type).

**Outcomes and measurement.**
- Outcomes: homes and other structures destroyed or damaged, area burned, fatalities, firefighter deaths.
- Data: RFS building impact assessment (BIA).
- Unit: fire and LGA, available in RFS BIA data.

**Identification.** Not applicable (inquiry).

**Implication for AUSSEF Y.** DL: RFS BIA "destroyed vs damaged" is the authoritative NSW source for LGA-level DL. A weighting such as destroyed = 1, damaged = 0.x is a defensible DL construction.

### 6. Royal Commission into National Natural Disaster Arrangements (2020) [V]
**Citation.** Binskin, M., Bennett, A., & Macintosh, A. (2020). *Royal Commission into National Natural Disaster Arrangements: Report*. Commonwealth of Australia, 28 October 2020. https://www.royalcommission.gov.au/natural-disasters/report (PDF: https://www.royalcommission.gov.au/system/files/2020-12/Royal%20Commission%20into%20National%20Natural%20Disaster%20Arrangements%20-%20Report%20%20%5Baccessible%5D.pdf)

**Summary.** The national inquiry, with 80 recommendations. It states that more than 3,000 homes were destroyed, that the national financial impact was estimated at over AUD 10bn, and that nearly 3 billion animals were killed or displaced. It emphasises that data on impacts and recovery costs are fragmented, and recommends national consistency in impact data.

**Outcomes and measurement.** Homes destroyed, fatalities, financial impact (secondary estimates), wildlife and ecological loss, and DRFA recovery expenditure.

**Implication for AUSSEF Y.** DL/FP: gives official headline magnitudes and legitimises DRFA recovery spending as an FP indicator. It also notes the absence of a standard impact-severity metric, which is AUSSEF's gap.

---

## B. Indirect and regional-economy losses (IL)

### 7. Hickson & Marshan (2022) [V]
**Citation.** Hickson, J., & Marshan, J. (2022). Labour market effects of bushfires and floods in Australia: A gendered perspective. *Economic Record*, 98(S1), 1–23. https://doi.org/10.1111/1475-4932.12688

**Summary.** Links HILDA individuals (Waves 1–19) to disaster exposure at SA4 level. Exposure is built from suburb-level Australian Institute for Disaster Resilience (AIDR) Knowledge Hub event records mapped to postcodes and then SA4. Floods raise labour supply for both sexes (about 13,500 jobs a year). Bushfires cut female employment probability by 1.6 pp (about 5,000 jobs a year) but raise male employment through mining and transport, with an added-worker effect.

**Outcomes and measurement.**
- Outcomes: employment, full-time status, labour force participation, hours, unemployment, household income components.
- Unit: individual, with exposure at SA4 × year.
- Data: 2000–2019.

**Identification.** Individual fixed-effects OLS with year, age and SA4 fixed effects, SA4-specific trends, and contemporaneous plus one-year-lagged disaster dummies. Details come from the authors' 2021 ACE conference slides, so treat specifics as [PV].

**Magnitudes.** Year-after effects for women: −1.4 pp full-time employment and about −AUD 1,349 a year in household asset income. For men: +1.1 pp employment and −0.7 pp unemployment in the following year.

**Implication for AUSSEF Y.** IL: aggregate employment effects of bushfires are small and gender-offsetting. An LGA unemployment-rate change may be near zero or noisy, so consider sectoral measures (retail, accommodation) and a t+1 window.

### 8. Ulubaşoğlu, Rahman, Önder, Chen & Rajabifard (2019) [V]
**Citation.** Ulubaşoğlu, M.A., Rahman, M.H., Önder, Y.K., Chen, Y., & Rajabifard, A. (2019). Floods, bushfires and sectoral economic output in Australia, 1978–2014. *Economic Record*, 95(308), 58–80. https://doi.org/10.1111/1475-4932.12446

**Summary.** A state-year panel of disaster occurrence against sectoral gross value added (GVA). Floods lower agricultural output by 5–6% in the year of the flood and the year after, and also hit mining, construction and finance. Bushfire effects on sectors are described as "more nuanced", mixed and less robust.

**Outcomes and measurement.**
- Outcome: sectoral GVA from ABS state accounts.
- Unit and window: state × year, 1978–2014.

**Identification.** Panel fixed effects with state and year effects, comparing affected and unaffected state-years.

**Implication for AUSSEF Y.** IL: at coarse spatial scales bushfire output effects are hard to detect. This argues for a finer (LGA) unit and for sectoral rather than total output.

### 9. Ulubaşoğlu & Beaini (2019), with the Deakin/BNHCRC Black Saturday income study [PV]
**Citation.** Ulubaşoğlu, M., & Beaini, F. (2019). Black Saturday bushfires: counting the cost. *Australian Journal of Emergency Management*, 34(2), 4–7. https://knowledge.aidr.org.au/media/6628/ajem-201904-02-mehmet-ulubasoglu-etal-farah-beaini.pdf

**Summary.** A practitioner summary of a Bushfire and Natural Hazards CRC study. It uses the ABS Australian Census Longitudinal Dataset (ACLD, 2006 to 2011) and SA2-level severity (share of each SA2 burnt, ranging from 0.1% to 72.2% across 37 SA2s in 12 hotspots). Individuals in fire-hit SA2s are compared with neighbouring unburnt SA2s using difference-in-differences.

**Outcomes and measurement.**
- Outcome: individual income (Census).
- Unit: individual, with SA2 exposure.
- Window: about 2 years after the fire (2009 fire, 2011 Census).

**Identification.** DiD with neighbouring control SA2s.

**Magnitudes.** Income losses of 9% for men, 14% for women, 18% for low-income earners, 8% for the employed, 14% for renters, 31% in agriculture, 13% in retail and 12% in tourism. Health-care workers gained 8%, and movers lost 19%.

**Caveat.** This is a news-and-views article, not the full peer-reviewed paper.

**Implication for AUSSEF Y.** IL/SL: supports burnt-area share of each small area as the treatment-intensity variable. Income effects at SA2 level are large for the worst-hit fires (Black Saturday scale) and are concentrated in agriculture, retail and tourism.

### 10. Akter (2023) [V]
**Citation.** Akter, S. (2023). Australia's Black Summer wildfires recovery: A difference-in-differences analysis using nightlights. *Global Environmental Change*, 83, 102743. https://doi.org/10.1016/j.gloenvcha.2023.102743

**Summary.** Uses monthly VIIRS night-time radiance at mesh-block level across NSW, January 2017 to June 2021, as an economic-activity proxy. Fire-affected and unaffected mesh blocks are compared, with Facebook movement data as a robustness check. Activity in affected areas fell by about 30% in both cities and inner-regional areas, and recovery was slower for poor and rural communities.

**Outcomes and measurement.**
- Outcome: night-time radiance (standardised).
- Unit: mesh block × month, NSW.
- Window: up to about 18 months after the fire.

**Identification.** DiD / event study, with heterogeneity by remoteness and socio-economic status.

**Magnitudes.** −0.038σ in major cities and −0.026σ in inner-regional areas, equivalent to about 30% lower activity. The author cautions that nightlights are a poor proxy in forested, remote areas.

**Implication for AUSSEF Y.** IL: the most directly comparable NSW study. Nightlights offer a monthly, sub-LGA IL proxy for 2015–2025, but are weak in remote forested LGAs.

### 11. Akter & Grafton (2025) [V]
**Citation.** Akter, S., & Grafton, R.Q. (2025). Socioeconomic well-being losses of Australia's Black Summer fires (2019–2020): Burden by burned area, poverty, and gender. *One Earth*, 8, 101454. https://doi.org/10.1016/j.oneear.2025.101454

**Summary.** An SA1-level analysis of income, housing and unpaid-work domains using Census data (2016 vs 2021). Propensity-score matching on the decadal FFDI, SEIFA decile and population is followed by panel fixed effects with SA4 × year effects. The most affected areas show significant declines, with income losses in wildland–urban interface communities and other losses concentrated in poorer SA1s. Losses persisted after government payments.

**Outcomes and measurement.**
- Outcomes: household income, housing (e.g. rent and mortgage stress, dwellings), unpaid work.
- Unit: SA1.
- Window: Census 2016 to 2021 (about 1.5 years after the fire, confounded with COVID).

**Identification.** PSM combined with FE-DiD.

**Implication for AUSSEF Y.** SL/IL: supports a multi-domain SL (income, housing, unpaid care) and burned-area share as the treatment. Poverty and gender heterogeneity suggest a vulnerability interaction term.

### 12. Reiner, Pathirana, Sun, Lenzen & Malik (2024) [V]
**Citation.** Reiner, V., Pathirana, N.L., Sun, Y.-Y., Lenzen, M., & Malik, A. (2024). Wish you were here? The economic impact of the tourism shutdown from Australia's 2019–20 'Black Summer' bushfires. *Economics of Disasters and Climate Change*, 8, 107–127. https://doi.org/10.1007/s41885-024-00142-8

**Summary.** A multi-regional input-output (IO) analysis of the short-term tourism shock. It builds a framework to separate direct fire-related tourism losses from COVID effects. Losses spread nationally, including far from the burn scars.

**Outcomes and measurement.**
- Outcomes: output, final demand, income (wages), jobs.
- Unit: IO regions × sectors.
- Window: the 2019–20 peak season.

**Identification.** IO modelling, not econometric.

**Magnitudes.** AUD 2.8bn in output, AUD 1.56bn in final demand, AUD 810m in income and about 7,300 jobs. Aviation lost the most value and accommodation the most jobs.

**Implication for AUSSEF Y.** IL: tourism is the main IL channel for NSW coastal and alpine LGAs. Accommodation takings or visitor nights, or accommodation employment, are candidate IL indicators, noting that COVID confounds 2020.

### 13. Wittwer & Waschik (2021) [V]
**Citation.** Wittwer, G., & Waschik, R. (2021). Estimating the economic impacts of the 2017–2019 drought and 2019–2020 bushfires on regional NSW and the rest of Australia. *Australian Journal of Agricultural and Resource Economics*, 65(4), 918–936. https://doi.org/10.1111/1467-8489.12441

**Summary.** A dynamic multi-regional CGE model (VU-TERM) simulating drought and bushfire shocks to farm capital, output and herds. The drought dominates; bushfires added to 2019–20 losses.

**Outcomes and measurement.**
- Outcomes: regional and national real GDP deviation from base, and the NPV of welfare loss.
- Unit: regional NSW, with TERM regions based on SA4.

**Identification.** CGE simulation against a counterfactual baseline.

**Magnitudes.**
- NSW GDP was 1.6% (AUD 10.2bn) below forecast in 2019–20, from drought and fires combined.
- National welfare loss NPV is AUD 63bn: AUD 53bn from drought and AUD 10bn from bushfires.
- The bushfire figure excludes lives, biodiversity and forestry.

**Implication for AUSSEF Y.** IL: an important confounder. NSW 2017–20 drought effects dwarf the bushfire output effects, so any IL measure for 2019–20 must control for drought (e.g. a rainfall or drought index) or use non-agricultural indicators.

### 14. RBA, Statement on Monetary Policy, February 2020, Box B [V]
**Citation.** Reserve Bank of Australia (2020). Box B: Macroeconomic effects of the drought and bushfires. *Statement on Monetary Policy – February 2020*. https://www.rba.gov.au/publications/smp/2020/feb/box-b-macroeconomic-effects-of-the-drought-and-bushfires.html

**Summary.** The RBA estimated the bushfires would reduce GDP growth by about 0.2 pp across the December 2019 and March 2020 quarters, with reconstruction broadly offsetting this by the end of 2020. Channels named are tourism (international and domestic), consumption disruption, rural exports, and local accommodation and food prices. Insurance, government support and rebuilding offset the losses.

**Outcomes and measurement.** National GDP and CPI components; quarterly.

**Identification.** Staff judgement and nowcasting.

**Implication for AUSSEF Y.** IL: aggregate effects are small and temporary, with rebuilding causing rebound. For LGA-level IL, use a t to t+2 quarter window and expect sign reversals (construction booms).

### 15. Meier, Elliott & Strobl (2023) [V]
**Citation.** Meier, S., Elliott, R.J.R., & Strobl, E. (2023). The regional economic impact of wildfires: Evidence from Southern Europe. *Journal of Environmental Economics and Management*, 118, 102787. https://doi.org/10.1016/j.jeem.2023.102787

**Summary.** Matches satellite burned-area perimeters (EFFIS) to 233 NUTS-3 regions in Portugal, Spain, Italy and Greece for 2011–2018. It estimates effects on growth in regional GDP and employment by sector.

**Outcomes and measurement.**
- Outcomes: annual GDP growth; employment growth by NACE sector.
- Data: Eurostat.
- Unit: NUTS-3 × year.

**Identification.** Panel fixed effects with instrumental variables (fire-weather instruments).

**Magnitudes.**
- A fire lowers annual GDP growth by 0.11–0.18 pp, or EUR 13–21bn a year across Southern Europe.
- Employment growth falls by 0.09–0.15 pp in retail, tourism, transport and accommodation.
- It rises by 0.13–0.22 pp in insurance, real estate and administrative services.

**Implication for AUSSEF Y.** IL: the best template for a regional (NUTS-3 ≈ large LGA) design. Expect small aggregate effects with sectoral reallocation, so tourism-sector employment is the more sensitive IL indicator.

### 16. Nielsen-Pincus, Moseley & Gebert (2013; 2014) [V-bib]
**Citations.**
- Nielsen-Pincus, M., Moseley, C., & Gebert, K. (2013). The effects of large wildfires on employment and wage growth and volatility in the western United States. *Journal of Forestry*, 111(6), 404–411. https://doi.org/10.5849/jof.13-012
- Nielsen-Pincus, M., Moseley, C., & Gebert, K. (2014). Job growth and loss across sectors and time in the western US: The impact of large wildfires. *Forest Policy and Economics*, 38, 199–206. https://doi.org/10.1016/j.forpol.2013.08.010

**Summary.** Matches large wildfires (2004–2008) to quarterly county employment and wage growth from QCEW in the western US. Employment growth rises by about 1% in quarters with active suppression, driven by local suppression spending. Volatility follows, and the 2014 paper finds a negative drag on employment growth for up to two years, with losses in leisure and hospitality and gains in natural resources and mining.

**Outcomes and measurement.**
- Outcomes: quarterly employment and wage growth and volatility, by sector.
- Unit: county × quarter.

**Identification.** Panel regression, comparing fire and non-fire county-quarters, with suppression-cost covariates.

**Implication for AUSSEF Y.** IL/FP: short-run employment can rise because of suppression and response spending. The IL window should extend to about 2 years, and FP (response spending) partly offsets IL, so avoid double-counting.

### 17. Davis, Moseley, Nielsen-Pincus & Jakes (2014) [V]
**Citation.** Davis, E.J., Moseley, C., Nielsen-Pincus, M., & Jakes, P.J. (2014). The community economic impacts of large wildfires: A case study from Trinity County, California. *Society & Natural Resources*, 27(9), 983–993. https://doi.org/10.1080/08941920.2014.905812

**Summary.** A mixed-methods case study combining labour-market data, suppression spending and interviews for the 2008 fires. Private-sector employment and wages fell over summer 2008 compared with 2007, while public-sector employment and wages rose. Interviews revealed business-level heterogeneity.

**Outcomes and measurement.** County monthly and quarterly employment and wages (public vs private), suppression spending.

**Identification.** Year-over-year comparison.

**Implication for AUSSEF Y.** IL: split IL into private and public employment, since public or response jobs mask private losses.

### 18. Jones & McDermott (2021) [V]
**Citation.** Jones, B.A., & McDermott, S. (2021). The local labor market impacts of US megafires. *Sustainability*, 13(16), 9078. https://doi.org/10.3390/su13169078

**Summary.** A nationwide US study of megafires (over 100,000 acres), 2010–2017. Counties inside a flame zone have significantly lower per-capita wage earnings for up to two years, across several earnings sources (BEA REIS/QCEW). There is preliminary evidence that the effect is nonlinear in fire size.

**Outcomes and measurement.**
- Outcomes: per-capita wage earnings; employment.
- Unit: county × year.

**Identification.** Panel fixed effects and dynamic event-time terms.

**Implication for AUSSEF Y.** IL: per-capita earnings is a more sensitive local outcome than unemployment. Consider ATO or ABS LGA wage and salary income per earner at t+1 and t+2.

### 19. Walls & Wibbenmeyer (2023) [V-bib]
**Citation.** Walls, M.A., & Wibbenmeyer, M. (2023). *How local are the local economic impacts of wildfires?* RFF Working Paper 23-03, Resources for the Future. https://www.rff.org/publications/working-papers/how-local-are-the-economic-impacts-of-wildfires/

**Summary.** Compares county-level QCEW data with establishment-level NETS data for major western US wildfires.

**Outcomes and measurement.**
- Outcomes: employment growth, total and by sector.
- Units: county-year and establishment-year, with distance to the fire.

**Identification.** Panel and event-study designs at two spatial scales.

**Magnitudes.**
- County level: no significant short- or long-run effect on employment growth.
- Establishments near the fire: job growth falls by 1.3 pp in the fire year, then recovers.
- Construction employment rises at both scales.

**Implication for AUSSEF Y.** IL: aggregation to the LGA dilutes effects. Weight IL by the share of LGA population or businesses inside or near the fire perimeter, and expect null average LGA employment effects.

### 20. Coulombe & Rao (2025) [V]
**Citation.** Coulombe, R.G., & Rao, A. (2025). Fires and local labor markets. *Journal of Environmental Economics and Management*, 130, 103109. https://doi.org/10.1016/j.jeem.2024.103109 (working paper: arXiv:2308.02739)

**Summary.** Builds a county × month burned-area measure from hourly satellite imagery (Nov 2000–May 2022) for the whole US. Local projections trace the employment response over 36 months, with smoke and spatial-lag controls. The authors argue disaster declarations and dollar damages are endogenous to local wealth and poorly timed.

**Outcomes and measurement.**
- Outcomes: monthly county employment growth (BLS QCEW) and net migration.
- Unit: county × month, horizon 0–36 months.

**Identification.** Local projections (Jordà), with heterogeneity by education, industrial concentration, labour-market slack and fire size.

**Magnitudes.**
- A mean-sized fire impulse (13 km²) reduces cumulative employment growth by 0.26 pp over 3 years, about 25% of baseline 3-year growth.
- Effects appear in the short run (1–7 months) and the medium run (2–3 years, via out-migration).
- Effects are larger in low-education, concentrated or slack economies.

**Implication for AUSSEF Y.** IL: supports physical intensity (burned area) over declaration-based treatment, windows at 1–7 months and 2–3 years, and SEIFA or industry concentration as moderators.

### 21. Borgschulte, Molitor & Zou (2024) [V]
**Citation.** Borgschulte, M., Molitor, D., & Zou, E.Y. (2024). Air pollution and the labor market: Evidence from wildfire smoke. *Review of Economics and Statistics*, 106(6), 1558–1575. https://doi.org/10.1162/rest_a_01243 (NBER WP 29952, 2022)

**Summary.** Links satellite smoke plumes (NOAA HMS) to US county labour-market outcomes, exploiting drifting smoke far from the flames.

**Outcomes and measurement.**
- Outcomes: quarterly earnings per worker, employment, labour force participation.
- Data: QCEW/QWI.
- Unit: county × quarter.

**Identification.** Panel fixed effects with smoke-day exposure as quasi-random variation.

**Magnitudes.** One extra smoke day reduces quarterly earnings by about 0.1%. Extensive-margin responses (employment, labour force exit) explain 13% of the loss. Lost-earnings welfare costs are comparable to the mortality burden.

**Implication for AUSSEF Y.** IL/SL: smoke spreads IL beyond burnt LGAs. Either include a smoke-days term for non-burnt LGAs or explicitly scope AUSSEF to the burn footprint.

### 22. Roth Tran & Wilson (2025) [V]
**Citation.** Roth Tran, B., & Wilson, D.J. (2025). The local economic impact of natural disasters. *Journal of the Association of Environmental and Resource Economists*, 12(6), 1667–1704. https://doi.org/10.1086/735533 (FRBSF WP 2020-34)

**Summary.** Almost four decades of US county data on disasters that triggered federal aid. In the long run (about 8 years), per-capita personal income, wages and home prices rise, while employment and population are unchanged. The boost increases with damages, consistent with insurance and aid inflows. Wildfires initially lower income and wages (per Coulombe & Rao's summary; not independently checked).

**Outcomes and measurement.**
- Outcomes: per-capita personal income, wages, employment, population, house prices.
- Unit: county × year, horizon up to 8+ years.

**Identification.** Local projections / event study.

**Implication for AUSSEF Y.** IL/FP: long-run local income may rise because of transfers, so IL measured beyond about 2 years is contaminated by recovery funding. Fix a short window.

### 23. McCoy & Walsh (2018) [V-bib]
**Citation.** McCoy, S.J., & Walsh, R.P. (2018). Wildfire risk, salience & housing demand. *Journal of Environmental Economics and Management*, 91, 203–228. https://doi.org/10.1016/j.jeem.2018.07.005 (NBER WP 20644)

**Summary.** Uses Colorado housing transactions and a sorting framework to show how buyers and sellers update fire-risk perceptions after major fires. Effects vary with proximity, burn-scar views and latent risk. The price discount after nearby fires is temporary.

**Outcomes and measurement.** Sale prices and transaction volumes; property-level hedonic model; years around the fire.

**Identification.** Hedonic difference-in-differences by distance and risk.

**Australian analogues.**
- Athukorala, W., Martin, W., Wilson, C., & Rajapaksa, D. (2019). Valuing bushfire risk to homeowners: Hedonic property values study in Queensland, Australia. *Economic Analysis and Policy*, 63, 44–56. https://doi.org/10.1016/j.eap.2019.04.013 [V-bib]
- Adachi & Li (2022), SSRN on the 2015 Sampson Flat fire, SA: https://doi.org/10.2139/ssrn.4222775 [V-bib; working paper]

**Implication for AUSSEF Y.** IL (optional): house-price or sales-volume change is a possible IL/SL indicator, but effects are local and short-lived and data (NSW Valuer General sales) are noisy at LGA level. Low priority.

---

## C. Cost-of-bushfire estimates (integrated DL + IL + health + social)

### 24. Johnston, Borchers-Arriagada, Morgan, Jalaludin, Palmer, Williamson & Bowman (2021) [V]
**Citation.** Johnston, F.H., Borchers-Arriagada, N., Morgan, G.G., Jalaludin, B., Palmer, A.J., Williamson, G.J., & Bowman, D.M.J.S. (2021). Unprecedented health costs of smoke-related PM2.5 from the 2019–20 Australian megafires. *Nature Sustainability*, 4, 42–47. https://doi.org/10.1038/s41893-020-00610-5

**Companion paper.** Borchers Arriagada, N., et al. (2020). Unprecedented smoke-related health burden associated with the 2019–20 bushfires in eastern Australia. *Medical Journal of Australia*, 213(6), 282–283. https://doi.org/10.5694/mja2.50545

**Summary.** Applies concentration–response functions to monitor-based smoke PM2.5 in affected jurisdictions. Outcomes are monetised with the value of a statistical life and hospital cost data, and compared with 19 previous seasons.

**Outcomes and measurement.**
- Outcomes: premature deaths, cardiovascular and respiratory hospital admissions, asthma emergency attendances, health cost (AUD).
- Unit and window: jurisdiction × fire season.

**Identification.** Health impact assessment, not causal econometrics.

**Magnitudes.**
- 429 premature deaths, 3,230 admissions and 1,523 asthma emergency attendances, costing AUD 1.95bn.
- The previous record was AUD 566m (2002–03), and the median annual cost over the previous 19 years was AUD 211m.

**Implication for AUSSEF Y.** SL (health) or IL: smoke health costs rival insured losses, but they are regional and airshed-level, not attributable to a fire × LGA cell without a dispersion model. Treat as an optional, separately reported SL add-on.

### 25. Deloitte Access Economics for the Australian Business Roundtable (2016) [V]
**Citation.** Deloitte Access Economics (2016). *The economic cost of the social impact of natural disasters*. Australian Business Roundtable for Disaster Resilience & Safer Communities, March 2016. https://australianbusinessroundtable.com.au/assets/documents/Report%20-%20Social%20costs/Report%20-%20The%20economic%20cost%20of%20the%20social%20impact%20of%20natural%20disasters.pdf

**Summary.** Case studies of the 2010–11 Queensland floods, Black Saturday 2009 and the 1989 Newcastle earthquake. It separates tangible costs (buildings, infrastructure, emergency response, business disruption) from intangible social costs, which are monetised by cost-of-illness methods (health-system, productivity, informal-care and non-pecuniary shares).

**Intangible categories.** Deaths and injury, mental health, alcohol misuse, chronic disease, family violence, crime, education, employment and community.

**Magnitudes.**
- Black Saturday: tangible costs AUD 3.1bn and intangible AUD 3.9bn, total about AUD 7bn.
- Total costs are underestimated by at least 50% if intangibles are ignored.
- Recovery spending over 2009–10 to 2012–13 was AUD 11.0bn, against AUD 225m on mitigation (citing the Productivity Commission).

**Implication for AUSSEF Y.** SL: gives empirical support for SL carrying weight comparable to DL (in this study intangible costs were about equal to or greater than tangible costs). It also supplies an SL indicator menu: mental health, family violence, alcohol, employment.

### 26. Read & Denniss (2020) [V; opinion piece]
**Citation.** Read, P., & Denniss, R. (2020, January 17). With costs approaching $100 billion, the fires are Australia's costliest natural disaster. *The Conversation*. https://theconversation.com/with-costs-approaching-100-billion-the-fires-are-australias-costliest-natural-disaster-129433

**Summary.** A back-of-envelope aggregation of property, tourism, health, productivity and ecosystem losses for Black Summer, asserting total costs approaching AUD 100bn. It is not peer-reviewed and was written mid-crisis.

**Implication for AUSSEF Y.** Mainly shows the wide range of total-cost estimates for the same event (AUD 10bn from the Royal Commission vs about AUD 100bn here), driven by whether intangibles and ecosystems are included. This supports transparent component-wise reporting over a single dollar total.

### 27. Wang, Guan, Zhu, Mac Kinnon, Geng, Zhang, Zheng, Lei, Shao, Gong & Davis (2021) [V-bib]
**Citation.** Wang, D., Guan, D., Zhu, S., et al. (2021). Economic footprint of California wildfires in 2018. *Nature Sustainability*, 4, 252–260. https://doi.org/10.1038/s41893-020-00646-7

**Summary.** Combines physical, epidemiological and supply-chain IO models.

**Magnitudes.**
- Total damages USD 148.5bn (range 126.1–192.9bn), about 1.5% of California GDP.
- Components: capital losses USD 27.7bn (19%), health costs USD 32.2bn (22%), indirect losses USD 88.6bn (59%).
- 52% of indirect losses fell outside California.

**Outcomes and measurement.** Capital stock destroyed, PM2.5 health cost, and output losses propagated through supply chains.

**Implication for AUSSEF Y.** IL/DL weighting: indirect losses can exceed direct capital losses by about 3×, but mostly outside the fire region. At LGA level, local IL is much smaller than total IL, so a local index should not import economy-wide multipliers.

### 28. Thomas, Butry, Gilbert, Webb & Fung (2017) [V]
**Citation.** Thomas, D., Butry, D., Gilbert, S., Webb, D., & Fung, J. (2017). *The costs and losses of wildfires: A literature survey*. NIST Special Publication 1215. https://doi.org/10.6028/NIST.SP.1215

**Summary.** A taxonomy of wildfire costs and losses: suppression, pre-fire mitigation, direct losses (structures, timber, infrastructure, fatalities, injuries), indirect losses (business interruption, tourism, property values, health), and post-fire rehabilitation. It documents inconsistent measurement across studies.

**Implication for AUSSEF Y.** All components. Useful as the checklist for classifying each AUSSEF indicator into DL, IL, FP or SL and avoiding double counting (e.g. suppression spending is FP, not DL).

### 29. Kochi, Donovan, Champ & Loomis (2010) [V]
**Citation.** Kochi, I., Donovan, G.H., Champ, P.A., & Loomis, J.B. (2010). The economic cost of adverse health effects from wildfire-smoke exposure: a review. *International Journal of Wildland Fire*, 19(7), 803–817. https://doi.org/10.1071/WF09077

**Summary.** Reviews studies on health costs of wildfire smoke, the epidemiology, and valuation (cost of illness, VSL, averting behaviour). It finds the literature thin, and extrapolation from urban pollution dose–response functions questionable.

**Implication for AUSSEF Y.** SL: caution on monetising health. If included, report as counts (admissions, excess deaths) rather than dollars.

---

## D. Fiscal pressure (FP) analogues

### 30. Liao & Kousky (2022) [V]
**Citation.** Liao, Y., & Kousky, C. (2022). The fiscal impacts of wildfires on California municipalities. *Journal of the Association of Environmental and Resource Economists*, 9(3), 455–493. https://doi.org/10.1086/717492

**Summary.** Links municipal finance data from the California State Controller (1990–2015) to wildfire perimeters. Treatment is fires affecting at least 10% of a municipality's population.

**Outcomes and measurement.**
- Outcomes: revenue and expenditure subcomponents, excess revenue per capita, probability of a deficit, population.
- Unit and window: municipality × year, event time −5 to +4.

**Identification.** Staggered DiD / event study.

**Magnitudes (5 years after the fire).**
- Revenues: general revenue +10.5%, property tax +21.2% (a Proposition 13 artefact).
- Expenditures: +17.3% overall, with public safety +18.5%, community development +40% and transport +17.8%.
- Net budget position: excess revenue −USD 97 per capita and a +25 pp probability of deficit.
- Population: −0.78%.
- Municipalities are relatively insulated compared with state and federal spending.

**Implication for AUSSEF Y.** FP: the closest template for council-level FP. Use NSW council financial statements (OLG Time Series Data) for expenditure by function, operating result and grants received over t to t+4. Note that NSW DRFA reimbursements flow through council books.

### 31. Deryugina (2017) [V; hurricanes, but a key FP method]
**Citation.** Deryugina, T. (2017). The fiscal cost of hurricanes: Disaster aid versus social insurance. *American Economic Journal: Economic Policy*, 9(3), 168–198. https://doi.org/10.1257/pol.20140296

**Summary.** US counties hit by hurricanes see large increases in non-disaster transfers (unemployment insurance, public medical payments) over the following decade. The present value of these exceeds direct disaster aid.

**Implication for AUSSEF Y.** FP/SL: FP should include social-security transfer increases in the LGA (DSS payment recipients, JobSeeker), not only DRFA disaster aid. Otherwise FP is underestimated.

---

## E. Social loss (SL) valuation, Australian bushfire-specific

### 32. Johnston, Önder, Rahman & Ulubaşoğlu (2021) [V-bib]
**Citation.** Johnston, D.W., Önder, Y.K., Rahman, M.H., & Ulubaşoğlu, M.A. (2021). Evaluating wildfire exposure: Using wellbeing data to estimate and value the impacts of wildfire. *Journal of Economic Behavior & Organization*, 192, 782–798. https://doi.org/10.1016/j.jebo.2021.10.029

**Summary.** Uses HILDA waves 2–11 with individual fixed effects to estimate the effect of proximity to the 2009 Black Saturday fires on life satisfaction and its domains. The loss is valued at AUD 52,300 per year, about 80% of average full-time income. The safety domain is most affected, people with low social support suffer most, and there is a delayed mental-health effect.

**Outcomes and measurement.**
- Outcomes: life satisfaction, satisfaction domains, SF-36 mental health.
- Unit: individual, with exposure by distance to the fire.

**Identification.** Individual fixed effects before and after the fire.

**Implication for AUSSEF Y.** SL: wellbeing losses are large relative to income losses, which supports a non-trivial SL weight. HILDA cannot be disaggregated to LGA, so use LGA-level proxies (mental-health service use, DV incidents from BOCSAR, DSS payments).

### 33. Ambrey, Fleming & Manning (2017) [V]
**Citation.** Ambrey, C., Fleming, C., & Manning, M. (2017). The social cost of the Black Saturday bushfires. *Australian Journal of Social Issues*, 52(4), 298–312. https://doi.org/10.1002/ajs4.21

**Summary.** Life-satisfaction valuation of Black Saturday exposure. The implied willingness to pay is AUD 2,991 of annual household income (AUD 1,039 per capita) to reduce, by one percentage point, the extent to which the local area was affected.

**Implication for AUSSEF Y.** SL: corroborates Johnston et al. (2021). Exposure is measured continuously as the share of the local area affected, consistent with a burnt-share treatment.

---

## F. Classifying or indexing fire events by impact

### 34. Tedim, Leone, Amraoui, Bouillon, Coughlan, Delogu, et al. (2018) [V]
**Citation.** Tedim, F., Leone, V., Amraoui, M., Bouillon, C., Coughlan, M.R., Delogu, G.M., et al. (2018). Defining extreme wildfire events: Difficulties, challenges, and impacts. *Fire*, 1(1), 9. https://doi.org/10.3390/fire1010009

**Summary.** Notes there is no "scale of gravity" for wildfires comparable to those for hurricanes or earthquakes. It proposes a seven-category classification based on fire behaviour (intensity, rate of spread, spotting) and suppression difficulty, with categories 5–7 defined as extreme wildfire events (EWE). EWE is conceptualised as both a process and a socio-ecological outcome.

**Implication for AUSSEF Y.** Index design: the leading classification is hazard-based, not impact-based, so an impact-based severity index (AUSSEF's Y) fills a stated gap. It is useful for separating hazard (X: intensity, FFDI, area) from outcome (Y: losses).

### Other index-relevant findings (from the entries above)
- Blanchi et al. (2014) classify days by FFDI thresholds (above 100 = "catastrophic"), a hazard classification.
- Ulubaşoğlu & Beaini (2019), Akter & Grafton (2025) and Ambrey et al. (2017) all use **share of area burnt** as a continuous severity or intensity measure at small-area level.
- The Royal Commission (2020) notes that national impact data are not standardised.
- I found **no peer-reviewed study that builds a composite economic, fiscal and social impact index for bushfire events** (the Australian Disaster Resilience Index measures pre-event resilience, not event impact). This should be stated as AUSSEF's contribution, with the caveat that the search was not exhaustive.

---

## Synthesis

### 1. Standard direct-loss (DL) indicators
Across academic and official sources the core DL indicators are:
1. Houses or buildings destroyed, with damaged often reported separately. Sources: RFS BIA (NSW), Filkov et al., the NSW Inquiry, the Royal Commission.
2. Fatalities: Blanchi et al., Filkov et al.
3. Area burnt, often as a share of the small area. This is a hazard/exposure measure, but is used as treatment intensity.
4. Insured losses, event-level only: ICA; McAneney et al.

Livestock, fencing and infrastructure appear in inquiry reports and CGE inputs (Wittwer & Waschik) but are rarely standardised. Normalising by exposed dwelling stock or value (McAneney et al.) is standard for comparing events over time. Fatalities are extremely zero-inflated and skewed.

**Recommendation for AUSSEF.** Build DL from dwellings destroyed plus a fractional weight on damaged, normalised by LGA dwelling stock, and use fatalities as a log-scaled or indicator term.

### 2. Standard indirect-loss (IL) indicators
- Employment or employment growth: QCEW in the US; HILDA / Census / Labour Force in Australia.
- Earnings or income per capita or per worker: Jones & McDermott; Borgschulte et al.; ACLD/Census in Australia.
- Sectoral output or employment, especially tourism, accommodation and retail: Meier et al.; Reiner et al.; Ulubaşoğlu et al.
- Nightlights as a high-frequency activity proxy: Akter (2023).
- Less commonly, house prices and GDP (CGE or IO).

Sector-specific measures (accommodation, food, retail, agriculture) are consistently more sensitive than aggregate unemployment.

### 3. Time windows
- **Short run:** the quarter of the fire and 1–2 quarters after (RBA; Nielsen-Pincus: suppression quarters; Coulombe & Rao: 1–7 months; Borgschulte et al.: the same quarter).
- **Medium run:** 1–2 years after, i.e. t+1 and t+2 (Hickson & Marshan: one-year lag; Jones & McDermott: up to 2 years; Nielsen-Pincus 2014: drag up to 2 years; Ulubaşoğlu: about 2 years via the 2011 Census; Akter: about 18 months).
- **Longer run:** 3–8 years (Coulombe & Rao: 2–3 years via migration; Liao & Kousky: 5-year fiscal effects; Roth Tran & Wilson: 8 years, when income may rise because of aid).

**Recommendation for AUSSEF.** Measure IL over the fire year and t+1 (with t+2 as robustness), and FP over t to t+3/4. Beyond about 2 years, recovery transfers and COVID (for Black Summer) contaminate IL.

### 4. Are local effects on unemployment, business and income large, small or null?
- **Aggregate employment and unemployment at county or LGA scale:** typically small or null on average.
  - Walls & Wibbenmeyer find no county effect.
  - Meier et al. and the RBA find small effects.
  - Nielsen-Pincus find a short-run positive effect from suppression spending, then a mild drag.
  - Hickson & Marshan find sex-offsetting effects (women −1.6 pp, men positive).
  - Coulombe & Rao find a statistically significant but modest effect (about −0.26 pp cumulative growth over 3 years for an average fire).
- **Sectoral:** consistently negative for tourism, accommodation, hospitality and retail, and positive for construction, insurance and real estate (Meier et al.; Nielsen-Pincus 2014; Walls & Wibbenmeyer; Reiner et al.). This reallocation is why totals net to near zero.
- **Income and earnings:** more consistently negative and moderately large near the fire.
  - Black Saturday: −8% to −18% individual income at SA2 level, up to −31% in agriculture.
  - US megafires: lower per-capita earnings for 2 years.
  - Smoke: −0.1% of quarterly earnings per smoke day.
  - Black Summer: SA1 income declines in wildland–urban interface areas.
- **Business activity:** nightlights show about 30% lower activity in affected NSW mesh blocks (Akter 2023). IO estimates put tourism losses at AUD 2.8bn nationally.
- **Scale dependence:** effects are large very close to the fire (establishment, mesh block, SA1/SA2) and diluted at county or LGA level. AUSSEF's fire × LGA design should therefore weight treatment by the share of the LGA's population or area burnt, and expect many LGA-level IL estimates to be noisy or near zero.

### 5. Weighting implications
- **Tangible vs intangible:** integrated cost studies consistently find social and health (intangible) costs comparable to tangible losses.
  - Deloitte: Black Saturday intangible AUD 3.9bn vs tangible AUD 3.1bn.
  - Johnston et al. (2021): smoke health cost of AUD 1.95bn vs about AUD 2.3bn insured.
  - Wellbeing valuations are large (Johnston et al. JEBO; Ambrey et al.).
  - This argues against an index dominated by DL.
- **Indirect vs direct:** indirect losses can be about 3× direct losses economy-wide (Wang et al.), but mostly outside the fire region. A local index should not import those multipliers.
- **Double-counting risks:**
  - Suppression and recovery spending shows up as positive short-run employment (IL) and as fiscal pressure (FP).
  - Aid inflows raise long-run local income (Roth Tran & Wilson).
  - Keep FP and IL windows and definitions distinct.
- **Confounding in NSW 2019–20:** the 2017–19 drought dominated output losses (Wittwer & Waschik), and COVID-19 followed from March 2020. The Black Summer IL needs drought and COVID controls, or a comparison of burnt with unburnt LGAs within the same region and quarter.
