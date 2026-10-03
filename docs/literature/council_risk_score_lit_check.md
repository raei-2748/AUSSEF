# Literature check: NSW council-level bushfire risk score validated against multi-pillar impacts

Checked 2026-09-28. Every source below was confirmed to exist through its publisher, DOI registry (Crossref), OpenAlex/Semantic Scholar record, or official web page. No ACM sources are used.

## (a) Verdict (5 lines)

1. Each part of the proposal already exists on its own. There are Australian SA2/LGA resilience and vulnerability indices (ADRI, SoVI-type indices), a NSW LGA-level multi-hazard risk assessment (SDMP), ML bushfire susceptibility maps for NSW, and US studies that validate vulnerability indices against observed disaster outcomes.
2. We found no study that builds an **all-NSW-LGA bushfire risk score from pre-fire hazard + exposure + socio-economic + council-fiscal inputs** and then **tests it out-of-sample against observed, event-level, multi-pillar impacts** (DL, IL, FP, SL) over many declared events.
3. The clearest gap is **validation against outcomes**. ADRI and the SDMP are not tested against realised bushfire impacts, and the SDMP itself says social and economic impact metrics had "not yet been established". Rufat et al. (2019) and Tellman et al. (2020) show that this kind of validation is rare even in the US.
4. The second gap is **the fiscal pillar**. Council fiscal vulnerability (as an input) and council fiscal pressure (as an outcome) are almost absent from risk indices. In Australia, evidence on how disasters hit council budgets comes from audit and inquiry reports, not peer-reviewed econometrics. The closest peer-reviewed work is from the US (Liao & Kousky 2022; Jerch et al. 2023).
5. The contribution is best described as a **multi-dimensional outcome validation of a pre-fire LGA risk score for NSW**. It is not a new index concept, not the first bushfire ML model for NSW, and not the first study to link disadvantage to Black Summer impacts.

## (b) Closest work by strand

### Strand 1: Australian resilience and vulnerability indices (LGA/SA2) and state risk tools

| Citation | What it does | How it differs from our proposal |
|---|---|---|
| Parsons et al. (2021), IJDRR 62:102422 (ADRI) | National Australian Disaster Resilience Index at SA2 level. Measures coping and adaptive capacity across 8 social, economic and institutional themes. Finds low resilience concentrated in remote areas. | Measures resilience capacity only, with no hazard or exposure layer and no bushfire-specific hazard. Not validated against observed disaster losses. Council finance appears only indirectly (institutional themes). |
| Parsons et al. (2016), IJDRR 19:1–11 | The conceptual framework behind ADRI: top-down indicator assessment of coping and adaptive capacities. | Framework paper. No outcome validation and no hazard component. |
| Wang et al. (2022), Scientific Reports 12:13665 | Nationwide fine-grained Cutter/SoVI-style social vulnerability index for Australia (41 indicators, 5 themes including built environment). Compares vulnerability inequality in areas affected by wildfire, flood and earthquake. | Vulnerability only. Overlays it on hazard footprints rather than predicting measured impacts. No fiscal dimension. |
| Wang et al. (2025), Habitat International 163:103495 | Updates the index to cover 2001–2021 (five censuses) and uses interpretable ML to relate social vulnerability to the built environment. | Uses ML to explain vulnerability, not disaster outcomes. Not bushfire-specific. |
| Solangaarachchi, Griffin & Doherty (2012), Natural Hazards 64:1873–1898 | Social vulnerability to bushfire at the urban–bush interface in two NSW councils (Blue Mountains, Ku-ring-gai). | Covers two councils rather than all of NSW. Has no statewide score and no validation against event impacts. |
| Leck (2025), AJEM Jan 2025, pp. 94–96; NSW Reconstruction Authority, State Disaster Mitigation Plan 2024–2026 | NSW statewide multi-hazard risk assessment for **all NSW LGAs** (bushfire among 7 hazards) using Average Annual Loss. Identifies higher-risk LGAs. | **Closest government tool.** Its risk measure is AAL to the built environment. The authors state that social, economic and natural impact metrics were not yet established. There is no council-fiscal pillar and no back-test against observed events. |
| FEMA, National Risk Index (US) | County/tract risk = expected annual loss × social vulnerability (SoVI) / community resilience, for 18 hazards including wildfire. | **Closest conceptual analogue** (hazard, exposure and vulnerability in one score). It is from the US and has no council-fiscal pillar. It is not validated against multi-dimensional realised impacts. |

### Strand 2: ML bushfire susceptibility and risk mapping (NSW/Australia)

| Citation | What it does | How it differs from our proposal |
|---|---|---|
| Zakari, Malik & Wee-Hong (2025), Natural Hazards 121:15331–15357 | Compares RF, XGBoost, AdaBoost and SVM for NSW wildfire susceptibility, with 15 factors (climate, environment, topography, socio-economic) and SHAP. Target is 2019–20 fire occurrence. XGBoost performs best. | **Closest NSW ML work.** The outcome is fire occurrence (hazard), not impacts on people, economies or councils. The unit is pixels/points, not LGAs. |
| Hosseini & Lim (2021), Geomatics, Natural Hazards and Risk 12:2367–2386 | Gene expression programming and ensemble models for Victorian bushfire susceptibility, evaluated by AUC. | Hazard-only susceptibility in Victoria. No socio-economic vulnerability and no impact outcome. |
| Zheng, Zhou & Shen (2025), IJDRR 118:105222 | Victorian bushfire risk mapping that combines hazard, exposure and vulnerability indices (natural environment, socio-economic factors, historical bushfire disasters) with scale division and factor analysis. | **Closest integrated H–E–V bushfire risk map in Australia.** It covers Victoria, not NSW. It uses factor analysis rather than outcome-based validation. There is no fiscal or multi-pillar impact test. |

### Strand 3: Validating vulnerability or risk indices against observed impacts

| Citation | What it does | How it differs from our proposal |
|---|---|---|
| Rufat, Tate, Emrich & Antolini (2019), Annals AAG 109:1131–1153 | Construct validation of four social vulnerability models against Hurricane Sandy outcomes (assistance applicants, renters, housing damage, property loss) using spatial regression. The indices explain assistance well and property loss poorly. | **Methodological template** for validating against several outcome types. It covers one US hurricane and does not include wildfire or fiscal outcomes. |
| Tellman et al. (2020), Sustainability 12:6006 | Validates SoVI and individual socio-demographic variables against deaths and damage from 11,629 US flood events. Individual variables outperform the composite index. | Validates across many events (similar to our 96-event design) but for floods in the US. Has no fiscal or income pillar. |
| Syphard et al. (2026), IJDRR 136:106066 | Relates six domain-specific social vulnerability indices to wildfire exposure and **structure loss** in California (2013–2022), with ML variable importance. | **Closest wildfire validation study.** It covers California and has only one impact outcome (structures). It works at housing-cluster scale, not the jurisdiction level with fiscal outcomes. |
| Arabadjis et al. (2026), Annals AAG 116:1211–1234 | Examines uncertainty when combining social and locational (e.g. fuel moisture) vulnerability into a wildfire risk index. | Focuses on index-construction uncertainty rather than outcome validation. Warns that composite scores are sensitive to design choices, which is relevant for our weighting. |

### Strand 4: Fiscal impact of disasters on local governments

| Citation | What it does | How it differs from our proposal |
|---|---|---|
| Liao & Kousky (2022), JAERE 9(3):455–493 | Panel of California municipal budgets 1990–2015 matched to wildfire perimeters. Wildfires raise revenues and spending, with a net negative budget effect. | **Closest fiscal study for wildfire.** It estimates fiscal impact after the fact and does not predict it from a pre-fire risk score. It is from the US, where the tax base differs from NSW councils. |
| Jerch, Kahn & Lin (2023), J. Urban Economics 134:103516 | US local governments hit by hurricanes: revenues fall 6–7% after major storms, spending on public goods falls about 6%, and default risk rises. Effects are larger for minority communities. | Evidence for a lasting fiscal-pressure channel, but for hurricanes in the US. Not a risk index. |
| Audit Office of NSW (2023), *Natural disasters* (1 June 2023) | Reports about $349m in damage to council infrastructure across more than 80 NSW LGAs in 2021–22. Costs exceeded the grant funding received. | Descriptive audit, mostly about floods. Shows that council fiscal pressure is real and measurable in NSW, but does not model or predict it. |
| Productivity Commission (2014), *Natural Disaster Funding Arrangements*, Inquiry Report No. 74 | National review finding disaster funding arrangements "not efficient, equitable or sustainable", with too little spent on mitigation compared with recovery. | Policy context for the FP pillar. No LGA-level quantitative analysis. |

### Strand 5: Regional socio-economic impacts of bushfires

| Citation | What it does | How it differs from our proposal |
|---|---|---|
| Hickson & Marshan (2022), Economic Record 98(S1):1–23 | Labour-market effects of bushfires and floods in Australia over about 20 years. Bushfires cut female employment probability by 1.6 pp (about 5,000 jobs a year), and there is an added-worker effect. | Estimates the IL-type impact of past fires. Does not test whether pre-fire risk predicts which areas suffer. Uses individual/household data, not LGAs. |
| Ulubaşoğlu et al. (2018/2019), Economic Record 95:58–80 | State-level effects of floods and bushfires on sectoral output, 1978–2014. | State scale, too coarse for councils. Impact estimation only. |
| Akter & Grafton (2021), Climatic Change 165:53 | Black Summer: SEIFA disadvantage is positively related to wildfire hazard exposure (fire extent × proximity). | Links disadvantage to exposure, not to measured losses. Has no predictive score and no fiscal or income outcomes. |
| Akter (2023), Global Environmental Change 83:102743 | Difference-in-differences on night-time lights: NSW Black Summer recovery at mesh-block level, with recovery pace varying by socio-economic group. | Measures NSW economic impact (an IL proxy) for one event. Not a risk-score validation. |
| Akter & Grafton (2025), One Earth 8:101454 | Black Summer well-being losses in income, housing and unpaid work, by poverty, gender and location. Urban–wildland areas saw income declines. | Multi-domain impact evidence (close to our IL/SL pillars) for one event, with no pre-fire risk model. |
| Reiner et al. (2024), Economics of Disasters and Climate Change 8:107–127 | Input–output estimate of the Black Summer tourism shutdown: AU$2.8b in lost output. | Supply-chain economic loss for one event. Not an LGA risk validation. |

## (c) Claims we must NOT make

- **Do not say we built the "first Australian (or NSW) disaster risk/vulnerability index".** ADRI, the Wang et al. SoVI-style indices and the NSW SDMP LGA assessment all exist.
- **Do not say we built the "first ML bushfire model for NSW" or the "first to include socio-economic factors in an ML bushfire model".** Zakari et al. (2025) did both, although for fire occurrence.
- **Do not say we are the "first to combine hazard, exposure and vulnerability for bushfire in Australia".** Zheng et al. (2025) did this for Victoria.
- **Do not say we are the "first to validate a vulnerability index against disaster outcomes".** Rufat et al. (2019), Tellman et al. (2020) and Syphard et al. (2026, wildfire) have done this.
- **Do not say we are the "first to show that disadvantaged communities were hit harder by Black Summer".** Akter & Grafton (2021, 2025) showed this.
- **Do not say that "no one has studied the fiscal impact of disasters on local government".** Liao & Kousky (2022), Jerch et al. (2023), the NSW Audit Office (2023) and the Productivity Commission (2014) have.
- **Do not say that "random forest variable importance shows causes".** RF importance is predictive association, not causal.
- **Do not say that "the SDMP ignores bushfire".** It includes bushfire. Its stated gap is social, economic and natural impact metrics.
- **Safe framing:** "To our knowledge, no published study has tested a pre-fire, LGA-level bushfire risk score for all NSW councils against observed multi-dimensional impacts (direct loss, income/business change, council fiscal pressure and social-support uptake) across multiple declared events." Keep "to our knowledge", and keep every qualifier. Dropping any of them makes the claim false.

## (d) References

1. Akter, S. (2023). Australia's Black Summer wildfires recovery: A difference-in-differences analysis using nightlights. *Global Environmental Change*, 83, 102743. https://doi.org/10.1016/j.gloenvcha.2023.102743
2. Akter, S., & Grafton, R. (2021). Do fires discriminate? Socio-economic disadvantage, wildfire hazard exposure and the Australian 2019–20 'Black Summer' fires. *Climatic Change*, 165, 53. https://doi.org/10.1007/s10584-021-03064-6
3. Akter, S., & Grafton, R. (2025). Socioeconomic well-being losses of Australia's Black Summer fires (2019–2020): Burden by burned area, poverty, and gender. *One Earth*, 8, 101454. https://doi.org/10.1016/j.oneear.2025.101454
4. Arabadjis, S., Zheng, Z., Strange, L., Murray, A., & Sweeney, S. (2026). Social vulnerability, locational vulnerability, and uncertainty in wildfire risk index construction. *Annals of the American Association of Geographers*, 116, 1211–1234. https://doi.org/10.1080/24694452.2025.2604851
5. Audit Office of New South Wales. (2023, 1 June). *Natural disasters*. https://www.audit.nsw.gov.au/our-work/reports/natural-disasters
6. FEMA. *National Risk Index for Natural Hazards* (v1.20, Dec 2025). https://www.fema.gov/flood-maps/products-tools/national-risk-index
7. Hickson, J., & Marshan, J. (2022). Labour market effects of bushfires and floods in Australia: A gendered perspective. *Economic Record*, 98(S1), 1–23. https://doi.org/10.1111/1475-4932.12688
8. Hosseini, M., & Lim, S. (2021). Gene expression programming and ensemble methods for bushfire susceptibility mapping: a case study of Victoria, Australia. *Geomatics, Natural Hazards and Risk*, 12, 2367–2386. https://doi.org/10.1080/19475705.2021.1964618
9. Jerch, R., Kahn, M., & Lin, G. (2023). Local public finance dynamics and hurricane shocks. *Journal of Urban Economics*, 134, 103516. https://doi.org/10.1016/j.jue.2022.103516 (NBER WP 28050: https://doi.org/10.3386/w28050)
10. Leck, A. (2025). The State Disaster Mitigation Plan guides and unifies disaster risk reduction efforts in New South Wales. *Australian Journal of Emergency Management*, January 2025, 94–96. https://knowledge.aidr.org.au/resources/ajem-january-2025-the-state-disaster-mitigation-plan-guides-and-unifies-disaster-risk-reduction-efforts-in-new-south-wales/
11. Liao, Y., & Kousky, C. (2022). The fiscal impacts of wildfires on California municipalities. *Journal of the Association of Environmental and Resource Economists*, 9(3), 455–493. https://doi.org/10.1086/717492
12. NSW Reconstruction Authority. (2024). *State Disaster Mitigation Plan 2024–2026*. https://www.nsw.gov.au/departments-and-agencies/nsw-reconstruction-authority/our-work/disaster-adaptation-plans/guidelines/state-disaster-mitigation-plan
13. Parsons, M., Glavac, S., Hastings, P., Marshall, G., McGregor, J., McNeill, J., Morley, P., Reeve, I., & Stayner, R. (2016). Top-down assessment of disaster resilience: A conceptual framework using coping and adaptive capacities. *International Journal of Disaster Risk Reduction*, 19, 1–11. https://doi.org/10.1016/j.ijdrr.2016.07.005
14. Parsons, M., Reeve, I., McGregor, J., Hastings, P., Marshall, G., McNeill, J., Stayner, R., & Glavac, S. (2021). Disaster resilience in Australia: A geographic assessment using an index of coping and adaptive capacity. *International Journal of Disaster Risk Reduction*, 62, 102422. https://doi.org/10.1016/j.ijdrr.2021.102422
15. Productivity Commission. (2014). *Natural Disaster Funding Arrangements* (Inquiry Report No. 74). https://www.pc.gov.au/inquiries/completed/disaster-funding/report
16. Reiner, V., Pathirana, N., Sun, Y., Lenzen, M., & Malik, A. (2024). Wish you were here? The economic impact of the tourism shutdown from Australia's 2019–20 'Black Summer' bushfires. *Economics of Disasters and Climate Change*, 8, 107–127. https://doi.org/10.1007/s41885-024-00142-8
17. Rufat, S., Tate, E., Emrich, C., & Antolini, F. (2019). How valid are social vulnerability models? *Annals of the American Association of Geographers*, 109, 1131–1153. https://doi.org/10.1080/24694452.2018.1535887
18. Solangaarachchi, D., Griffin, A., & Doherty, M. (2012). Social vulnerability in the context of bushfire risk at the urban-bush interface in Sydney: a case study of the Blue Mountains and Ku-ring-gai local council areas. *Natural Hazards*, 64, 1873–1898. https://doi.org/10.1007/s11069-012-0334-y
19. Syphard, A., Rustigian-Romsos, H., Rodriguez, C., Conlisk, E., Jennings, M., & Greenberg, M. (2026). The relationship between social vulnerability and wildfire structure loss across California. *International Journal of Disaster Risk Reduction*, 136, 106066. https://doi.org/10.1016/j.ijdrr.2026.106066
20. Tellman, B., Schank, C., Schwarz, B., Howe, P., & de Sherbinin, A. (2020). Using disaster outcomes to validate components of social vulnerability to floods: Flood deaths and property damage across the USA. *Sustainability*, 12, 6006. https://doi.org/10.3390/su12156006
21. Ulubaşoğlu, M., Rahman, M., Önder, Y., Chen, Y., & Rajabifard, A. (2019). Floods, bushfires and sectoral economic output in Australia, 1978–2014. *Economic Record*, 95, 58–80. https://doi.org/10.1111/1475-4932.12446 (Crossref issue date 2018; journal volume 95 = 2019)
22. Wang, S., Zhang, M., Huang, X., Hu, T., Sun, Q., Corcoran, J., & Liu, Y. (2022). Urban–rural disparity of social vulnerability to natural hazards in Australia. *Scientific Reports*, 12, 13665. https://doi.org/10.1038/s41598-022-17878-6
23. Wang, S., Liu, H., Cai, W., Huang, X., & Sun, Q. (2025). Australian nationwide assessment of social vulnerability in two decades through its linkage to the built environment. *Habitat International*, 163, 103495. https://doi.org/10.1016/j.habitatint.2025.103495
24. Zakari, R., Malik, O., & Wee-Hong, O. (2025). Machine learning-driven wildfire susceptibility mapping in New South Wales, Australia using remote sensing and explainable artificial intelligence. *Natural Hazards*, 121, 15331–15357. https://doi.org/10.1007/s11069-025-07395-w
25. Zheng, Q., Zhou, A., & Shen, S. (2025). Mapping bushfire risk based on scale division and factor analysis: A case study from Victoria, Australia. *International Journal of Disaster Risk Reduction*, 118, 105222. https://doi.org/10.1016/j.ijdrr.2025.105222

### Verification notes
- Metadata (title, authors, year, venue, volume, pages) for all journal items came from Crossref DOI records. Abstracts came from Semantic Scholar/OpenAlex or the publisher page. Government items were opened directly.
- Full texts were not read for Solangaarachchi et al. (2012) or Zheng et al. (2025). Their descriptions come from the title, the publisher search snippet and the Crossref record, so check the method details before quoting them.
- Author initials follow the Crossref records (first initial only). Add middle initials from the publisher pages if the citation style requires them.
