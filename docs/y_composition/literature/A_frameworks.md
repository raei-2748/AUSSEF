# Strand A: Frameworks for classifying and measuring disaster impacts, and composite severity indices

Prepared for AUSSEF (NSW bushfires 2015–2025, fire × LGA; Y = f(DL, IL, FP, SL)). Compiled 26 Sep 2026.

**How items were checked.** Journal items were checked against Crossref and/or OpenAlex metadata (authors, year, title, venue, volume, pages, DOI). Grey literature was checked by finding the official landing page or PDF. For BTE Report 103, Deloitte/ABR 2016, PDNA Vol. A, the SDG 11.5.2 metadata and the ADRI summary, I downloaded the PDF and read the relevant text. Where I could get only the abstract or metadata, the item says so ("content partially verified"). Nothing below comes from memory without a check on the source's existence and bibliographic details.

---

## Part 1. Damage vs. loss typologies (international)

### 1. ECLAC (2003). *Handbook for Estimating the Socio-Economic and Environmental Effects of Disasters* (4 vols). UN Economic Commission for Latin America and the Caribbean and the International Bank for Reconstruction and Development (World Bank). LC/MEX/G.5. https://www.cepal.org/en/publications/2782-handbook-estimating-socio-economic-and-environmental-effects-disasters (PDF mirror: https://www.preventionweb.net/files/1099_eclachandbook.pdf)
- **Summary.** This handbook is the origin of the "DaLA" (Damage and Loss Assessment) method. It separates **direct damages**, meaning destroyed or damaged stocks of assets, from **indirect losses**, meaning the reduced flows of goods and services and higher costs until recovery. It then looks at overall **macroeconomic effects** such as GDP, the balance of payments and public finances. It works sector by sector (social, infrastructure, productive, environmental, cross-cutting).
- **Dimensions / measurement.** Damage is valued at replacement cost of physical units. Losses are changes in flows (lost output, higher operating costs, lost revenue). Macro effects are *not added* to damage and losses. They are a different view of the same shock.
- **Weighting / aggregation.** None across dimensions. Items are summed in money within damage and within losses. Macro effects are reported alongside.
- **Implication for AUSSEF Y:** DL (stock) and IL (flow) are separate concepts, but fiscal and macro effects are a *second view* of the same shock. Do not add FP to DL+IL as though it were extra loss without justification.

### 2. EU, UNDG and World Bank/GFDRR (2013). *Post-Disaster Needs Assessments: Volume A Guidelines*. https://www.gfdrr.org/en/publication/post-disaster-needs-assessments-guidelines-volume-2013 (PDF: https://www.gfdrr.org/sites/default/files/2017-09/PDNA-Volume-A.pdf)
- **Summary.** PDNA combines DaLA with the Human Recovery Needs Assessment (HRNA). It is organised as: *disaster effects* (on infrastructure and physical assets; on production of and access to goods and services; on governance; on risk), then *disaster impact* (macroeconomic and human development), then *recovery needs*. It is explicitly people-centred.
- **Dimensions / measurement (checked in text).** "Damages" are valued first in physical units and then at "replacement costs according to the market price prevailing just before and after the disaster". "Economic losses refer to changes in economic flows arising from the disaster which continue until the achievement of full economic recovery". Losses explicitly include "increased fiscal expenditures as opposed to reduced tax revenues". Human impact covers livelihoods, income, health, education and social services.
- **Weighting.** No composite. Results are reported by sector in money plus human-development narratives. The guide warns about double counting of needs across sectors.
- **Implication for AUSSEF Y:** PDNA puts public-finance strain *inside* "losses" (flows). If AUSSEF keeps FP as its own pillar, define it as the **public-sector incidence** of costs, not an extra cost layer.

### 3. UNISDR/UNDRR (2017; new edition 2018). *Technical guidance for monitoring and reporting on progress in achieving the global targets of the Sendai Framework for Disaster Risk Reduction*. https://www.undrr.org/publication/technical-guidance-monitoring-and-reporting-progress-achieving-global-targets-sendai. Also UN Statistics Division, *SDG indicator metadata 1.5.2 / 11.5.2* (updated 2024-12-20). https://unstats.un.org/sdgs/metadata/files/Metadata-01-05-02.pdf
- **Summary.** The UN General Assembly endorsed 38 indicators (A/71/644; res. 71/276, Feb 2017). Target A covers mortality, B affected people, C direct economic loss, D critical-infrastructure damage and disruption of basic services. Countries report by event through DesInventar-Sendai.
- **Dimensions / measurement (checked in metadata PDF).** **C-1 = (C-2 + C-3 + C-4 + C-5 + C-6) / GDP**, where C-2 = agricultural loss, C-3 = other productive assets, C-4 = housing, C-5 = critical infrastructure, C-6 = cultural heritage. Only *direct* loss is covered. Indirect loss is out of scope.
- **Weighting.** Target C components are summed in money and **normalised by GDP**. The targets are *not* combined with each other. Deaths, affected people and loss are reported side by side.
- **Implication for AUSSEF Y:** This supports a DL sub-structure (housing / productive / agriculture / infrastructure) and scaling DL by local economic size (e.g. LGA GRP or income). There is international precedent for **not** collapsing people-based and money-based impacts into one number.

### 4. Meyer, V., Becker, N., Markantonis, V., Schwarze, R., van den Bergh, J. C. J. M., Bouwer, L. M., et al. (2013). Review article: Assessing the costs of natural hazards – state of the art and knowledge gaps. *Natural Hazards and Earth System Sciences*, 13, 1351–1373. https://doi.org/10.5194/nhess-13-1351-2013
- **Summary.** This is the synthesis of the EU FP7 **CONHAZ** project (2010–2012; https://www.ufz.de/index.php?en=35939). It reviews cost assessment for droughts, floods, coastal and Alpine hazards. It finds practice "often incomplete and biased": direct costs get most attention, while intangible and indirect effects are rarely counted. All stages carry large uncertainty.
- **Dimensions.** Five cost types: (i) direct tangible damages; (ii) losses from business interruption (BI); (iii) indirect damages (knock-on effects outside the hazard area and period); (iv) intangible effects (health, environment, cultural); (v) risk-mitigation costs.
- **Weighting.** Money for tangible items. Intangibles are valued in money through methods such as willingness to pay (WTP), DALYs and value of a statistical life (VSL), or kept as multi-criteria indicators. The paper recommends reporting uncertainty ranges.
- **Implication for AUSSEF Y:** BI belongs in IL, not DL. SL (intangible) should be kept visible, not dropped. Report uncertainty bands for each pillar.

### 5. Merz, B., Kreibich, H., Schwarze, R., & Thieken, A. (2010). Review article "Assessment of economic flood damage". *Natural Hazards and Earth System Sciences*, 10, 1697–1724. https://doi.org/10.5194/nhess-10-1697-2010
- **Summary.** This is the standard 2×2 typology: **direct/indirect × tangible/intangible**, with examples in each cell. It also reviews damage functions, the choice of spatial scale, and the choice of economic versus financial perspective.
- **Dimensions.** Direct means caused by physical contact with the hazard. Indirect means induced by the direct impacts, in space or time. Tangible means it has a market price. Intangible means it has none (fatalities, health, ecological and cultural losses).
- **Weighting.** Monetary aggregation of tangible cells only. Intangibles are handled separately.
- **Implication for AUSSEF Y:** Map each AUSSEF variable to one cell of this 2×2 before building the index. This is the simplest guard against double counting. DL = direct tangible; IL = indirect tangible; SL = mostly intangible.

### 6. Hallegatte, S., & Przyluski, V. (2010). *The economics of natural disasters: Concepts and methods*. World Bank Policy Research Working Paper 5507. https://doi.org/10.1596/1813-9450-5507
- **Summary.** Different "disaster cost" estimates disagree because disaster impacts have many dimensions, cause large redistributions, and serve different purposes, each with its own analytic boundary. The paper argues that direct cost (the value of what is destroyed) "is not a sufficient indicator of disaster seriousness", and that indirect losses are essential for welfare. It reviews reconstruction dynamics and methods for indirect loss (input–output, CGE, econometric).
- **Dimensions.** Direct (stock) vs indirect (flow, including reconstruction dynamics). Distributional and redistributive effects matter. The perimeter, local or national, determines what counts as a loss.
- **Weighting.** Conceptual paper. Total cost = direct + indirect within a *specified perimeter*, with transfers netted out at the national level.
- **Implication for AUSSEF Y:** Fix and state the perimeter. At fire × LGA level, transfers into the LGA (disaster assistance) are *gains to the LGA* but *costs to the state*. That is why FP needs a clear viewpoint.

### 7. Rose, A. (2004). Economic principles, issues, and research priorities in hazard loss estimation. In Y. Okuyama & S. E. Chang (Eds.), *Modeling Spatial and Economic Impacts of Disasters* (Advances in Spatial Science, pp. 13–36). Springer. https://doi.org/10.1007/978-3-540-24787-6_2
- **Summary** (bibliographic details verified; abstract not openly available, so the content summary is *partially verified* against the chapter's well-known framing). Rose separates **stock** losses (property damage) from **flow** losses (lost output). He defines "direct" and "indirect" flow losses as first-order and higher-order (supply-chain, multiplier or general-equilibrium) effects. He stresses resilience (substitution, inventories, relocation), which reduces BI. He warns against adding a stock loss to the capitalised flow from the same asset.
- **Dimensions.** Property damage (stock); direct BI (flow); indirect BI (flow).
- **Weighting.** Monetary. Flows are measured in value added (GRP), not gross sales.
- **Implication for AUSSEF Y:** IL should be measured as **lost value added / income / employment relative to a counterfactual**, not turnover. It should not also include the lost rental or productive value of assets already counted in DL.

### 8. Hallegatte, S., Vogt-Schilb, A., Bangalore, M., & Rozenberg, J. (2017 [online Nov 2016]). *Unbreakable: Building the Resilience of the Poor in the Face of Natural Disasters*. Climate Change and Development Series. World Bank. https://doi.org/10.1596/978-1-4648-1003-9
- **Summary.** The report argues that asset losses alone understate a disaster's gravity, because "$1 in losses does not mean the same thing to a rich person that it does to a poor person". It introduces **well-being (welfare) losses**, meaning the consumption-equivalent loss after accounting for distribution, and **socioeconomic resilience** = asset losses ÷ well-being losses. It estimates global well-being losses to be well above asset losses (see the report for figures).
- **Dimensions.** Asset losses; income and consumption losses over the recovery period; distribution across income groups; the smoothing role of transfers, savings and insurance.
- **Weighting.** Welfare weighting: losses to poorer households get more weight through concave utility. This is an explicit **equity weight**.
- **Implication for AUSSEF Y:** This is a principled reason to scale DL/IL by local income or wealth (e.g. relative to LGA median income, or SEIFA). It also gives SL a clear meaning: the extra welfare burden on vulnerable communities.

### 9. Kousky, C. (2014). Informing climate adaptation: A review of the economic costs of natural disasters. *Energy Economics*, 46, 576–592. https://doi.org/10.1016/j.eneco.2013.09.029
- **Summary** (metadata verified; content from the abstract and standard review structure, *partially verified*). The paper reviews empirical evidence on direct losses, indirect/BI losses, macroeconomic effects and non-market impacts (health, mortality, environment). It flags heavy reliance on insured-loss data and inconsistent definitions.
- **Dimensions.** Direct damage; BI; regional/macro growth; mortality and health; displacement.
- **Weighting.** None (review).
- **Implication for AUSSEF Y:** Insurance-based DL undercounts uninsured and public assets. Document how AUSSEF's DL sources cover each asset class.

### 10. Botzen, W. J. W., Deschenes, O., & Sanders, M. (2019). The economic impacts of natural disasters: A review of models and empirical studies. *Review of Environmental Economics and Policy*, 13(2), 167–188. https://doi.org/10.1093/reep/rez004
- **Summary** (metadata verified; content partially verified). The paper compares model-based estimates of indirect loss (input–output and CGE) with ex-post econometric estimates (panel, difference-in-differences, synthetic control). It notes that IO models tend to overstate indirect loss (no substitution) and CGE models tend to understate it (too much flexibility). Empirical results depend strongly on disaster size and on the unit and time horizon.
- **Weighting.** None (review).
- **Implication for AUSSEF Y:** At LGA level, an empirical **counterfactual (DiD / synthetic control) estimate of IL** is defensible and transparent. If AUSSEF uses multipliers instead, say which bias direction applies.

---

## Part 2. Australian frameworks and cost estimates

### 11. Bureau of Transport Economics (BTE) (2001). *Economic Costs of Natural Disasters in Australia*. Report 103. Canberra: BTE. https://www.bitre.gov.au/publications/2001/report_103 (PDF: https://www.bitre.gov.au/sites/default/files/report_103.pdf)
- **Summary (checked in PDF).** The report builds a costing framework and estimates national costs for 1967–1999 from the Emergency Management Australia (EMA) disasters database. Losses are grouped into three categories: **tangible direct, tangible indirect, intangible**. It reports that bushfires cost about $77 million per year on average over the period. It sets out "general principles": measure **economic, not financial**, costs; measure "**with and without** the disaster" rather than "before and after", because before/after "would overstate the cost"; and "**Do not double count**", using lost *value added* rather than lost sales plus wages and profits, and not counting both an asset's lost value and its lost value added.
- **Dimensions.** Direct tangible (buildings, contents, infrastructure, crops, emergency response and clean-up); indirect tangible (BI, network disruption); intangible (deaths, injuries, psychological, environmental), which is largely unvalued except for deaths and injuries.
- **Weighting.** Monetary sum from a **national perspective**. Government assistance and insurance payouts are treated as **transfers and excluded** from economic cost. The report notes that a local-perspective total would be larger than the national one.
- **Implication for AUSSEF Y:** In the Australian reference framework, **public relief/recovery spending is a transfer, not an extra economic loss**. AUSSEF's FP must be justified as a *burden-incidence* dimension (who pays, relative to capacity), and IL must be measured against a counterfactual.

### 12. Deloitte Access Economics (2016). *The economic cost of the social impact of natural disasters*. Report for the Australian Business Roundtable for Disaster Resilience & Safer Communities, March 2016. https://australianbusinessroundtable.com.au/assets/documents/Report%20-%20Social%20costs/Report%20-%20The%20economic%20cost%20of%20the%20social%20impact%20of%20natural%20disasters.pdf
- **Summary (checked in PDF).** Following the Productivity Commission, the report defines costs as **direct tangible** (market value of damage to property and infrastructure), **indirect tangible** (flow-on effects such as business and network disruption) and **intangible** ("death and injury, impacts on health and wellbeing, and community connectedness"). It costs intangibles for the 2009 Black Saturday bushfires (**intangible about $3.9b vs tangible about $3.1b**, from its Chart iii), the 2010–11 Queensland floods, and the 1989 Newcastle earthquake. It concludes that social costs are "at least as high as the tangible costs" and that total cost in 2015 exceeded $9b.
- **Dimensions.** Fatality; injury and disability; mental health (psychological distress); alcohol and drug misuse; chronic disease; family violence; crime; environmental; employment and education effects. Values come from VSL/VSLY and DALY-type unit costs × prevalence uplift in affected populations.
- **Weighting.** Monetisation (all in $). The report explicitly avoids double counting, e.g. "To avoid double counting, unemployment has not been quantified separately" because it is already inside the health-outcome costs.
- **Implication for AUSSEF Y:** This is direct Australian precedent for an **SL pillar at least as large as DL for bushfires**. SL indicators (deaths, injuries, mental health, family violence, displacement) can be monetised with standard unit values. Watch employment effects: count them in IL *or* SL, not both.

### 13. Ladds, M., Keating, A., Handmer, J., & Magee, L. (2017). How much do disasters cost? A comparison of disaster cost estimates in Australia. *International Journal of Disaster Risk Reduction*, 21, 419–429. https://doi.org/10.1016/j.ijdrr.2017.01.004
- **Summary** (metadata verified; content from secondary abstract summaries, *partially verified*). The paper compares five aggregate Australian disaster-loss estimates and finds large differences. These come from the lack of a standard retrospective method: different thresholds, cost categories, insured-to-total multipliers and normalisation.
- **Weighting.** None (comparison).
- **Implication for AUSSEF Y:** DL levels are very sensitive to source and multiplier. Use **ranks or normalised scores** and test robustness across DL sources rather than relying on absolute dollar levels.

### 14. Handmer, J., Ladds, M., & Magee, L. (2018). Updating the costs of disasters in Australia. *Australian Journal of Emergency Management*, 33(2), 40–46. https://knowledge.aidr.org.au/resources/ajem-apr-2018-updating-the-costs-of-disasters-in-australia/
- **Summary (landing page checked).** The authors build the AUS-DIS database (1967–2013; 310 events above A$10m loss or 3+ deaths), updating BTE (2001). They integrate ICA and EMA data, normalise for CPI, population and wealth, and value deaths with a VSL of about $4.2m. They find total losses of about $171.5b (2013 prices), with the bushfire share rising to about 17%.
- **Weighting.** Monetisation: deaths are added to dollar losses through VSL. Losses are normalised for inflation, population and wealth.
- **Implication for AUSSEF Y:** This is a precedent for converting deaths and injuries to dollars with VSL so they sit on the same scale as DL. It also supports **normalising losses by exposure/wealth** before comparing across fires and years.

### 15. Parsons, M., Glavac, S., Hastings, P., Marshall, G., McGregor, J., McNeill, J., Morley, P., Reeve, I., & Stayner, R. (2016). Top-down assessment of disaster resilience: A conceptual framework using coping and adaptive capacities. *International Journal of Disaster Risk Reduction*, 19, 1–11. https://doi.org/10.1016/j.ijdrr.2016.07.005 — **and** Parsons, M., Reeve, I., McGregor, J., Hastings, P., et al. (2021). Disaster resilience in Australia: A geographic assessment using an index of coping and adaptive capacity. *IJDRR*, 62, 102422. https://doi.org/10.1016/j.ijdrr.2021.102422 — **and** Parsons, M. et al. (2020). *The Australian Disaster Resilience Index: a summary*. BNHCRC Report No. 588.2020. https://www.naturalhazards.com.au/resources/publications/report/australian-disaster-resilience-index
- **Summary (summary PDF checked).** The ADRI is a hierarchical composite built on OECD (2008). It has **77 indicators**, grouped into **8 themes** (sub-index factors), which form **coping** and **adaptive capacity** sub-indices, which form the overall index. The unit is **SA2** (2,084 of 2,214 SA2s). SA2s are also clustered into resilience profile groups. It measures *capacity*, not realised impact.
- **Weighting.** Hierarchical aggregation (theme, then capacity, then overall). The exact normalisation and weighting rules are in the technical report and the 2021 paper; I could not read them in full text (*partially verified*).
- **Implication for AUSSEF Y:** ADRI is an **exposure/vulnerability covariate (X), not part of Y**. It is also a local template for a hierarchical, OECD-compliant index that could be matched to LGAs (via an SA2–LGA concordance).

---

## Part 3. Composite severity/impact indices and weighting methods

### 16. EM-DAT / CRED (Université catholique de Louvain). *EM-DAT Documentation: Entry Criteria*. https://doc.emdat.be/docs/protocols/entry-criteria/ (reference paper: Delforge, D., et al. (2025). EM-DAT: the Emergency Events Database. *IJDRR*, https://www.sciencedirect.com/science/article/pii/S2212420925003334. Title, venue and year confirmed; full author list and DOI not confirmed, so *partially verified*.)
- **Summary (checked).** An event qualifies if it has "at least ten deaths", "at least 100 affected (people affected, injured, or homeless)", or "a call for international assistance or an emergency declaration". Impact variables (deaths, injured, affected, homeless, total/insured damage) are recorded separately.
- **Weighting.** **OR-rule (non-compensatory) thresholds.** No composite.
- **Implication for AUSSEF Y:** This is a precedent for a threshold/max-type severity grade. A fire × LGA qualifies as "severe" if *any* pillar passes a threshold, as an alternative or robustness check to a weighted sum.

### 17. Caldera, H. J., & Wirasinghe, S. C. (2022 [online 30 Nov 2021]). A universal severity classification for natural disasters. *Natural Hazards*, 111, 1533–1573. https://doi.org/10.1007/s11069-021-05106-9 (open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC8630994)
- **Summary (OA text checked).** The paper proposes a 0–10 **logarithmic** severity scale based on "the most influential impact factor". In the current version this is **fatalities** (level 1 = 1–10 deaths, 2 = 10–100, 3 = 100–1,000 … up to extinction). The single factor is justified by high rank correlations with injuries (ρ≈0.78) and damage (ρ≈0.83). Thresholds are informed by extreme value theory. A multidimensional extension is left for future work.
- **Weighting.** No weighting: a single dominant indicator with log-scale class breaks.
- **Implication for AUSSEF Y:** It supports **log-scaling** heavy-tailed impacts and **order-of-magnitude class breaks** for severity grades. But NSW bushfires 2015–25 have few deaths in most fire × LGA cells, so a death-only scale would not discriminate. That is an argument for a multidimensional Y.

### 18. Eshghi, K., & Larson, R. C. (2008). Disasters: lessons from the past 105 years. *Disaster Prevention and Management*, 17(1), 62–82. https://doi.org/10.1108/09653560810855883
- **Summary** (abstract checked; details of the scale not read in full, *partially verified*). The paper reviews global disasters from 1900 to 2005, draws more than 40 statistical lessons, and proposes a two-dimensional probability-density classification and a "new scaling system … to determine the actual damage of disasters to human life". The scale combines human-impact counts (deaths, affected) rather than money.
- **Weighting.** Classification on a two-dimensional (human-impact) space, not a weighted sum.
- **Implication for AUSSEF Y:** Severity grades can be defined on a **two-dimensional grid** (e.g. economic pillar × human pillar) instead of one weighted score. This keeps the trade-off visible.

### 19. Noy, I. (2016 [online 2015]). A global comprehensive measure of the impact of natural hazards and disasters. *Global Policy*, 7(1), 56–65. https://doi.org/10.1111/1758-5899.12272
- **Summary (abstract checked).** Impacts are usually reported separately (deaths, injuries, affected people, financial damage). Noy proposes a single **"lifeyears"** index based on the DALY concept. It converts deaths, injuries, people affected *and* destroyed capital and housing into life-years lost; capital is converted via income per capita.
- **Weighting.** **Common-unit conversion** (life-years). This is an implicit, theory-based weighting that replaces statistical or expert weights.
- **Implication for AUSSEF Y:** An alternative to monetisation: convert DL/IL into "life-year" or "income-year" equivalents using LGA income per capita. This builds in equity scaling, as in *Unbreakable*.

### 20. OECD & JRC European Commission (Nardo, M., Saisana, M., Saltelli, A., Tarantola, S., Hoffman, A., & Giovannini, E.) (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. Paris: OECD Publishing. https://doi.org/10.1787/9789264043466-en
- **Summary.** The standard reference, with a 10-step checklist: theoretical framework, data selection, imputation, multivariate analysis, **normalisation**, **weighting and aggregation**, uncertainty and sensitivity analysis, back to the data, links to other indicators, and visualisation.
- **Normalisation options.** Ranking, z-scores, min–max, distance to reference, categorical scales, indicators above/below the mean, percentage change. Log transforms are used for skewed data. Min–max is sensitive to outliers.
- **Weighting options.** Equal weights; statistical (PCA/factor analysis, data envelopment analysis, benefit-of-the-doubt, unobserved components model, regression); participatory (budget allocation, public opinion, **AHP**, conjoint analysis).
- **Aggregation.** In linear (additive) aggregation, weights act as **trade-offs, not importance coefficients**, and compensation is full. Geometric aggregation gives partial compensation. Non-compensatory multi-criteria methods (e.g. Condorcet-type) give none. The handbook warns that correlated indicators give implicit double weight.
- **Implication for AUSSEF Y:** Follow the 10 steps. Treat the DL/IL/FP/SL weights as explicit **substitution rates**. Report equal-weight, PCA and expert/AHP variants with uncertainty and sensitivity analysis. Consider geometric aggregation so that one extreme pillar cannot be fully offset.

### 21. Saisana, M., Saltelli, A., & Tarantola, S. (2005). Uncertainty and sensitivity analysis techniques as tools for the quality assessment of composite indicators. *Journal of the Royal Statistical Society: Series A*, 168(2), 307–323. https://doi.org/10.1111/j.1467-985X.2005.00350.x
- **Summary** (metadata verified; content well established and summarised in OECD 2008). The paper sets out Monte Carlo uncertainty analysis over construction choices (normalisation, weights, aggregation, imputation) and variance-based (Sobol') sensitivity analysis. Together they show how stable each unit's rank is and which choices drive that instability.
- **Implication for AUSSEF Y:** Report each fire × LGA's **grade with a rank interval** across alternative index designs, and which design choice matters most.

### 22. Tate, E. (2012). Social vulnerability indices: a comparative assessment using uncertainty and sensitivity analysis. *Natural Hazards*, 63(2), 325–347. https://doi.org/10.1007/s11069-012-0152-2
- **Summary** (metadata verified; findings from abstract summaries). Tate applies global uncertainty and sensitivity analysis to **deductive, hierarchical and inductive (SoVI-type, PCA)** index designs. Hierarchical designs were most accurate and inductive most precise. **Deductive indices were most sensitive to the transformation/normalisation method, hierarchical indices to the weighting scheme, and inductive indices to the indicator set and scale of analysis.** He gives stage-specific recommendations for transparency and robustness.
- **Implication for AUSSEF Y:** AUSSEF's Y is **hierarchical** (4 pillars → Y), so **weighting is the decision that most needs sensitivity testing**. A single set of weights should not be presented as definitive.

### 23. Cutter, S. L., Boruff, B. J., & Shirley, W. L. (2003). Social vulnerability to environmental hazards. *Social Science Quarterly*, 84(2), 242–261. https://doi.org/10.1111/1540-6237.8402002
- **Summary.** The origin of SoVI. It uses 42 US county-level socioeconomic variables, reduced by **PCA** to 11 factors, which are summed with **equal weights** (factor signs set by theory) into a county score. Scores are classified by standard deviations from the mean.
- **Implication for AUSSEF Y:** The inductive PCA + equal-weights template is common in the hazards field. But it applies to vulnerability (X). For an outcome index Y with only four theory-defined pillars, PCA weights are of limited use (see Becker et al. 2017).

### 24. Becker, W., Saisana, M., Paruolo, P., & Vandecasteele, I. (2017). Weights and importance in composite indicators: Closing the gap. *Ecological Indicators*, 80, 12–22. https://doi.org/10.1016/j.ecolind.2017.03.056
- **Summary (abstract checked).** Nominal weights are **not** equal to an indicator's actual importance in the composite. Importance depends on the indicators' variances and correlations. The paper measures importance with the nonlinear correlation ratio (Gaussian-process estimate) and gives an optimisation to back out weights that deliver target importances.
- **Implication for AUSSEF Y:** Even "equal weights" on DL/IL/FP/SL will not give equal influence if, for example, DL is much more variable or correlated with IL. Check the **realised importance** of each pillar (correlation ratio or SHAP on Y) and adjust.

### 25. Greco, S., Ishizaka, A., Tasiou, M., & Torrisi, G. (2019 [online 2018]). On the methodological framework of composite indices: A review of the issues of weighting, aggregation, and robustness. *Social Indicators Research*, 141, 61–94. https://doi.org/10.1007/s11205-017-1832-9
- **Summary** (abstract checked). A comprehensive review of weighting methods (equal, PCA/FA, DEA/benefit-of-the-doubt, regression, **entropy**, AHP, budget allocation, conjoint), aggregation methods (additive, geometric, multi-criteria/outranking) and robustness analysis. It identifies weighting and aggregation as the steps that attract the most criticism.
- **Implication for AUSSEF Y:** Use this as the methods citation for justifying the choice among entropy, AHP, PCA and equal weights. **Entropy weights reward dispersion, not importance.** They will up-weight whichever pillar is most unequal across fire × LGA cells, which may be an artefact of data coverage.

### 26. Asadzadeh, A., Kötter, T., Salehi, P., & Birkmann, J. (2017). Operationalizing a concept: The systematic review of composite indicator building for measuring community disaster resilience. *IJDRR*, 25, 147–162. https://doi.org/10.1016/j.ijdrr.2017.09.015
- **Summary (abstract checked).** The paper proposes an **eight-step** construction procedure and a quality-assessment framework (19 dimensions, 36 metrics). It applies them to 17 disaster-resilience indices and finds no agreed standard procedure and weak methodological documentation, especially on weighting and sensitivity.
- **Implication for AUSSEF Y:** Use the eight-step checklist as a documentation template in the AUSSEF methods section.

### 27. Marzi, S., Mysiak, J., Essenfelder, A. H., Amadio, M., Giove, S., & Fekete, A. (2019). Constructing a comprehensive disaster resilience index: The case of Italy. *PLOS ONE*, 14(9), e0221585. https://doi.org/10.1371/journal.pone.0221585
- **Summary (abstract checked; the authors after Amadio come from the article page and are *partially verified*).** A municipal-level disaster resilience index for Italy that tests how **normalisation** (linear vs non-linear) and **aggregation** (OWA, LSP operators) change rankings. Robust rankings are defined by **dominance across methods**.
- **Implication for AUSSEF Y:** Instead of one "correct" design, grade fire × LGA cells by **dominance across a set of plausible designs**. A cell is "severe" if it is in the top class in most designs.

### 28. (Example of hybrid AHP + entropy weighting in hazards.) Lightning disaster risk zoning in Jiangsu Province, China, based on the Analytic Hierarchy Process and Entropy Weight Method. *Frontiers in Environmental Science* (2022). https://doi.org/10.3389/fenvs.2022.943000 (title, venue, year and DOI verified via OpenAlex; authors not recorded here, *partially verified*).
- **Summary.** This is typical of a large, mostly Chinese applied literature that combines subjective AHP weights with objective entropy weights (e.g. multiplicative or linear blending) for hazard risk or loss grading.
- **Implication for AUSSEF Y:** If the mentor's framework uses entropy weighting, a **blended AHP + entropy** scheme has precedent. Its quality is uneven, so it should sit alongside OECD-style sensitivity analysis.

---

## Part 4. Counterfactual ("excess") measurement of impact

### 29. Cavallo, E., Galiani, S., Noy, I., & Pantano, J. (2013). Catastrophic natural disasters and economic growth. *Review of Economics and Statistics*, 95(5), 1549–1561. https://doi.org/10.1162/REST_a_00413
- **Summary (abstract checked).** The paper builds **synthetic controls** for each country hit by a large disaster to estimate counterfactual GDP. Only extremely large disasters reduce output, and even those effects disappear once post-disaster political revolutions are controlled for.
- **Implication for AUSSEF Y:** A template for **IL = observed minus synthetic-control counterfactual** for each affected LGA (e.g. employment, business counts, GRP), using unaffected NSW LGAs as the donor pool.

### 30. Strobl, E. (2011). The economic growth impact of hurricanes: Evidence from U.S. coastal counties. *Review of Economics and Statistics*, 93(2), 575–589. https://doi.org/10.1162/REST_a_00082
- **Summary** (metadata verified; content partially verified). The paper builds a physical hurricane destruction index at county level (from wind-field modelling × exposure) and estimates its effect on county growth in a panel with fixed effects. Local growth falls in the hurricane year, with smaller effects at state and national levels as spatial offsetting takes hold.
- **Implication for AUSSEF Y:** It shows that **local (LGA) impacts exceed aggregate ones** because activity shifts. IL at LGA level is partly redistribution within NSW, which matters for interpretation and for summing across LGAs.

### 31. Belasen, A. R., & Polachek, S. W. (2009). How disasters affect local labor markets: The effects of hurricanes in Florida. *Journal of Human Resources*, 44(1), 251–276. https://doi.org/10.3368/jhr.44.1.251
- **Summary (abstract checked).** A generalised difference-in-differences design with county-quarter employment and wage data (QCEW). In hit counties, earnings rise by up to 4% while employment growth slows. Neighbouring counties lose earnings. Stronger hurricanes have larger effects.
- **Implication for AUSSEF Y:** A county (≈ LGA) DiD design is standard for indirect labour-market loss. Include **spillover LGAs** as a separate group, not as controls.

### 32. Deryugina, T. (2017). The fiscal cost of hurricanes: Disaster aid versus social insurance. *American Economic Journal: Economic Policy*, 9(3), 168–198. https://doi.org/10.1257/pol.20140296
- **Summary (abstract checked).** In an event-study / DiD design, US hurricanes cause large increases in **non-disaster** government transfers (unemployment insurance, public medical payments) in affected counties over the following decade. Their present value "significantly exceeds that of direct disaster aid". Fiscal costs of disasters have therefore been "significantly underestimated".
- **Implication for AUSSEF Y:** Strong support for an **FP pillar measured as excess (counterfactual) public outlays**. In Australia this would mean excess JobSeeker/DSS payments, council expenditure and DRFA claims, not just declared disaster-assistance lines. It also makes clear that FP overlaps with IL: transfers are responses to income loss.

---

## Synthesis

### (a) Which dimensions should a disaster-impact index have?
- Every major framework separates **stocks from flows**: ECLAC/DaLA damage vs losses, PDNA, Rose (2004), Hallegatte & Przyluski (2010), BTE (2001). Every major framework also separates **market from non-market** impacts: Merz et al. (2010), Meyer et al. (2013)/CONHAZ, Deloitte (2016). AUSSEF's **DL** (direct tangible, stock), **IL** (indirect tangible, flows until recovery) and **SL** (intangible or human) line up with the standard typology.
- **Human impacts must be explicit.** Sendai Targets A/B, EM-DAT, Caldera & Wirasinghe and Noy all treat deaths, injured, affected and displaced as core severity measures. Deloitte (2016) shows that for Black Saturday intangibles exceeded tangibles (about $3.9b vs $3.1b). Dropping SL would understate bushfire severity by roughly half.
- **FP is the least standard pillar.** DaLA/PDNA fold fiscal effects into "losses" or the macro impact. BTE (2001) treats government assistance as a **transfer, excluded from economic cost**. Deryugina (2017) shows that fiscal costs are large and under-measured. AUSSEF should therefore define FP as a **public-sector burden/incidence** dimension (excess public outlays and lost revenue *relative to fiscal capacity*, e.g. per council own-source revenue). It is not an additive component of total economic cost. Its viewpoint (council, state or Commonwealth) must be stated.
- Resilience and vulnerability measures (ADRI, SoVI) are **inputs (X), not outcomes (Y)**. Keep them out of Y to avoid circularity in the prediction stage.

### (b) Normalisation
- Scale by **exposure or economic size** before comparing units. Sendai C-1 divides by GDP. Handmer et al. (2018) normalise for CPI, population and wealth. *Unbreakable* and Noy (2016) implicitly scale by income. For LGAs, use per-capita, per-dwelling, or share-of-GRP/revenue forms, with CPI deflation to a common year.
- Impact distributions are extremely heavy-tailed (most fire × LGA cells are near zero, a few are catastrophic). Use a **log transform** or ranks/percentiles before min–max (OECD 2008). Caldera & Wirasinghe use order-of-magnitude (log₁₀) class breaks, which suit severity *grades*.
- Normalisation choice matters most for simple deductive indices (Tate 2012) and for rankings (Marzi et al. 2019). Test min–max vs z-score vs percentile rank.

### (c) Weighting and aggregation
- **There is no consensus method.** OECD (2008), Greco et al. (2019) and Asadzadeh et al. (2017) all treat the weighting choice as a normative decision that must be justified and stress-tested. Tate (2012) finds that for **hierarchical** indices like AUSSEF's Y, **weighting is the single most influential choice**.
- Options, and what the literature says about each:
  - **Equal weights**: the default in SoVI and many resilience indices. Transparent, but still a value judgement.
  - **PCA/FA**: reflects correlation structure, not importance. Unstable with only four pillars.
  - **Entropy**: rewards dispersion, not importance. Common in applied Chinese hazard work, often blended with AHP.
  - **AHP / expert or budget allocation**: explicit value judgements. Needs documented panels and consistency ratios.
  - **Common-unit conversion**: money (BTE, Deloitte, Handmer: VSL) or life-years (Noy). Replaces weights with prices, and is the most theory-consistent option if data allow.
- With linear aggregation, weights are **trade-off rates** (OECD 2008). Nominal weights ≠ realised importance (Becker et al. 2017), so check each pillar's actual contribution. Consider **geometric or non-compensatory** aggregation, or EM-DAT-style OR-thresholds, so that a catastrophic SL cannot be offset by a low FP.
- Recommended practice: report a headline Y plus **uncertainty and sensitivity analysis** (Saisana et al. 2005; OECD 2008) across normalisation × weighting × aggregation choices. Give severity grades as **modal class with rank interval**, or by dominance across designs (Marzi et al. 2019). A two-dimensional grade (economic × human; Eshghi & Larson 2008) is a transparent alternative.

### (d) Direct vs indirect double-counting pitfalls
1. **Asset value vs lost income from the same asset.** Counting both destroyed-asset value (DL) and that asset's lost rent or production (IL) double counts. Use repair or replacement cost *or* the capitalised flow, not both (BTE 2001; Rose 2004).
2. **Sales vs value added.** Count lost value added / income, not turnover plus wages plus profits (BTE 2001).
3. **Transfers (insurance payouts, disaster assistance, DRFA, social security) are not additional economic losses** from a national perspective (BTE 2001; Hallegatte & Przyluski 2010). If FP is included, treat it as incidence or burden. Do not also count the underlying damage that the spending repairs as a separate FP loss in a *sum* of pillars. Alternatively, net it out, or make the index explicitly multi-perspective.
4. **FP ↔ IL overlap.** Excess unemployment and income-support payments are responses to IL (Deryugina 2017). Count the income loss in IL and the *public share of cushioning* in FP, and document the overlap. Correlated pillars get implicit double weight in additive indices (OECD 2008; Becker et al. 2017).
5. **IL ↔ SL overlap.** Unemployment effects already inside health or social-outcome costs should not be counted again (Deloitte 2016 explicitly excludes them).
6. **Before/after vs with/without.** Before/after comparisons attribute trends to the fire and "overstate the cost" (BTE 2001). Use counterfactual designs (DiD, synthetic control: Cavallo et al. 2013; Belasen & Polachek 2009) to measure IL and excess FP.
7. **Perimeter / spillovers.** LGA-level IL includes activity displaced to neighbouring LGAs (Strobl 2011; Belasen & Polachek 2009). Summing LGA losses across NSW overstates state-level loss, and control groups must exclude spillover LGAs.
8. **Reconstruction boost.** Construction activity rises after disasters (PDNA notes flows may be positive in construction). Net measures of IL can therefore understate gross disruption. Report sector-specific IL where possible.
