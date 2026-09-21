# Judgment calls

| # | Date | Decision | Reason |
|---|---|---|---|
| D1 | 2026-09-21 | Use inputs from `transport_criticality.duckdb` and `event_perimeters.gpkg` outside `aussef.duckdb`. | `aussef.duckdb` contains no spatial road or fire data. User approved. |
| D2 | 2026-09-21 | Freeze today's SHA-256 as the baseline for `network_fingerprint.parquet` and `transport_criticality.duckdb`. | No prior hash was recorded. User approved. The PBF and perimeters match earlier manifests. |
| D3 | 2026-09-21 | rho is missing when observed isolations k = 0. | Jeffreys smoothing otherwise makes rho large without any observed joint failure. User approved. |
| D4 | 2026-09-21 | Exclude `highway = service`. | Driveways and car parks inflate exit counts. User approved. |
| D5 | 2026-09-21 | Communities are ABS UCL 2021 with 2021 Census `Tot_P_P` ≥ 200. | User approved the download. |
| D6 | 2026-09-21 | Treat the graph as undirected. | The stored network is flagged `undirected_structural_network_not_legal_vehicle_routing`; one-way tags are not reliable for emergency egress. |
| D7 | 2026-09-21 | Fire source is Geoscience Australia perimeters grouped into "fire families" (3 days / 5 km), 2019-07 to 2023-07. | This is what the existing overlay was built from; it is not FESM. A megafire complex counts as one event. |
| D8 | 2026-09-21 | UCL GDA2020 (EPSG:7844) reprojected to GDA94 Albers (EPSG:3577). | Matches the network CRS; the datum offset (~1.8 m) is negligible at these scales. |
| D9 | 2026-09-21 | Ring = outside endpoints of edges crossing the R circle around the polygon centroid. Polygons reaching the circle are flagged `ring_inside_polygon`. | Makes "nodes 20 km from the centroid" operational; a ring inside the town is meaningless. |
| D10 | 2026-09-21 | Sources = nodes inside the polygon; if there are none, endpoints of intersecting edges. | Small UCLs may have no intersection inside the polygon. |
| D11 | 2026-09-21 | Path decomposition = min-cost max-flow by edge length. | Makes "prefer shortest paths" precise (minimum total length). |
| D12 | 2026-09-21 | Stop rule: fewer than 10 eligible communities means NOT EVALUABLE. | The task said to stop if too few are eligible; 10 is the pre-registered threshold. |
| D13 | 2026-09-21 | N_eff excludes both never-closed and always-closed exits. | phi is undefined for a constant indicator. |
