# Can the satellite tell fire light from house light? (answered before any analysis)

Written 2 Oct 2026, before PRESPEC.md. Every claim has a row in
`bibliography/parts/exp15_nightlights_2026-10-02.csv` (source ids in brackets).

## Short answer

**Not in the files we have.** Ray's memory is right.

1. **Our files.** The 264 files are the Earth Observation Group (EOG) monthly composites, version 1. For 131 of
   the 132 months the names contain `vcm-slexcl` or `ecm-slexcl`, meaning cloud-masked with stray light excluded.
   2024-10 exists only as `ecmcfg`, a different configuration (E15-P01, E15-P02). We got them from the World
   Bank "Light Every Night" copy on Amazon (E15-008, E15-009).
2. **Monthly files are not fire-filtered.** Before averaging, EOG removes data hit by "stray light, lightning, lunar
   illumination, and cloud-cover". But "Version 1 has NOT been filtered to screen out lights from aurora, fires,
   boats, and other temporal lights" (E15-002, the provider's description in the Google Earth Engine catalogue).
   EOG's own page says the same thing indirectly: its first-step composites contain "lights, fires, aurora and
   background", and the extra cleaning of "ephemeral lights" is described only for the annual products (E15-001).
3. **The annual VNL V2 product is fire-filtered.** EOG: "The new method uses the twelve-month median radiance to
   discard high and low radiance outliers, filtering out most fires and isolating the background" (E15-001). But it
   gives one number per year, so it cannot show which month lights fell or came back. It is also not in the open
   Amazon bucket (E15-009), so getting it would be a new download.
4. **Smoke dims lights.** In a model of how light passes through the atmosphere, raising aerosol optical depth from 0
   to 0.5 changes how much city light reaches VIIRS by about 30% (Wang et al. 2016, Atmospheric Environment 124:55-63,
   Fig. 1b; E15-003). The EOG monthly page lists no smoke or aerosol correction (E15-001). NASA's Black Marble product
   does correct for aerosols (user guide PDF p.9; E15-004).
5. **Burnt trees can make lights look brighter.** NASA's Black Marble light model includes a term for light getting
   up "through the urban vegetation canopy" (user guide PDF p.10; E15-004). If a fire strips the trees, the same houses can
   look brighter from space. This is one possible reason why Experiment 7 saw council-level lights *rise* after heavy
   fires (Experiment 7/FINDINGS_DAY1.md, deviation 2; E15-P05).

So in a fire month a pixel can be **brighter** (flames) or **darker** (smoke, power cuts, people gone), and after
the fire it can be **brighter** (no canopy). The satellite cannot tell these apart by itself.

## Ways to separate them, and what we use

| Option | What it is | Can we use it now? |
|---|---|---|
| A. Annual VNL V2 (fire-filtered) | EOG yearly maps with fires removed (E15-001) | Not in the project; new download (EOG login or Google Earth Engine). **Proposed as a cross-check only; waiting for Ray.** |
| B. EOG VIIRS Nightfire | Finds burning spots using short-wave infrared at night (E15-005) | Since 10 Jan 2025 the data are under a "VIIRS Nightfire Data Use License" (E15-005). Not used. |
| C. NASA Black Marble VNP46A2/A3 | Moonlight- and aerosol-corrected lights. Quality flag 1 means "Outlier, Potential cloud contamination or other issues". There is no separate fire flag (E15-004, PDF p.51). | Needs a NASA Earthdata login and a large download. Not used now. |
| **D. Mask with our own fire data (chosen)** | DEA Hotspots (satellite fire detections from VIIRS, MODIS and others) already cached for every mapped fire (E15-P03), plus the mapped fire outlines and their dates | **Yes: no download needed** |

**Design that follows from this (fixed in PRESPEC.md):**
- A pixel-month is thrown out if any cached hotspot lies within 2 km in that month, or if a mapped fire outline
  within 2 km was burning that month. This removes flame light and same-month smoke very close to the pixel. It cannot remove smoke
  that spread hundreds of kilometres (that part only partly cancels through the comparison, below).
- A pixel-month is thrown out if it has fewer than 2 cloud-free looks (`n_cf`). EOG warns that users must check
  the cloud-free file and not read a zero as "no lights" (E15-001).
- Each month is compared with **the same calendar month** in the two years before the fire. This removes holiday
  seasons and the seasonal change in night length.
- Each burned pixel is compared with **similar unburned settled pixels in the same region** (same brightness band,
  10 km or more from any fire). Regional smoke, COVID lockdowns and product changes (2017-04, 2018-01, 2024-10) that hit both
  groups equally cancel out. Changes that hit coast and inland differently only partly cancel.
- The main read uses **months after the fire was out**, when the flames are gone. Some effects that have nothing to
  do with people remain. Canopy loss would push lights up. Dark burnt ground or damaged power networks could push them
  down. So the direction of this bias is unknown.
- Hotspot cache gap: it only covers the mapped fires' own boxes and dates. Unmapped fires, such as hazard-reduction
  burns (the GA outlines leave out prescribed burns), are not masked. This is listed as a limitation. A full-NSW
  hotspot download would close the gap, but it is a new download and needs Ray's OK.

*Edited after the independent audit (AUDIT.md, findings 14-15): smoke, cancel-out and canopy wording softened;
2024-10 product, licence wording and PDF page numbers corrected.*
