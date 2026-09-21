"""RESULTS.md and PNG maps, generated from out/community_results.parquet."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "out"


def fmt(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)) or pd.isna(x):
        return "missing"
    if abs(x) >= 1e4 or (abs(x) < 1e-2 and x != 0):
        return f"{x:.2e}"
    return f"{x:.{d}f}"


def quant_table(s):
    s = s.dropna()
    if s.empty:
        return "no defined values"
    q = s.quantile([0, 0.25, 0.5, 0.75, 1.0])
    return (f"n = {len(s)}; min {fmt(q[0])}, Q1 {fmt(q[0.25])}, median {fmt(q[0.5])}, "
            f"Q3 {fmt(q[0.75])}, max {fmt(q[1.0])}")


def sensitivity(res):
    lines = ["| Rule | Ring R | Communities | Ring inside polygon | Exits ≥ 2 | Fires ≥ 10 | Eligible | rho defined | rho > 5 & lower > 1 | Share |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for rule in ("S0", "S100"):
        for R in (10, 20, 30):
            p = res[(res.rule == rule) & (res.ring_radius_km == R)]
            e = p[p.eligible]
            n_pass = int(e.rho_gt5_and_lo_gt1.fillna(False).sum())
            share = f"{n_pass / len(e):.1%}" if len(e) else "missing"
            tag = " (primary)" if (rule, R) == ("S0", 20) else ""
            lines.append(f"| {rule}{tag} | {R} km | {len(p)} | {int(p.ring_inside_polygon.sum())} | "
                         f"{int(p.eligible_exits.sum())} | {int(p.eligible_fires.sum())} | {len(e)} | "
                         f"{int(e.rho.notna().sum())} | {n_pass} | {share} |")
    return "\n".join(lines)


def community_table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    body = []
    for _, r in df.iterrows():
        body.append("| " + " | ".join(f(r) for _, f in cols) + " |")
    return head + "\n" + "\n".join(body)


def maps(res, net):
    p = res[(res.rule == "S0") & (res.ring_radius_km == 20)]
    e = net["edges"]
    major = e.highway.isin(["motorway", "trunk", "primary"]).values
    lines = shapely.get_coordinates(net["geom"][major], return_index=True)

    def base(ax):
        xy, idx = lines
        brk = np.flatnonzero(np.diff(idx)) + 1
        segs = np.split(xy, brk)
        from matplotlib.collections import LineCollection
        ax.add_collection(LineCollection(segs, colors="#cccccc", linewidths=0.3, zorder=0))
        ax.scatter(p.centroid_x, p.centroid_y, s=4, c="#bbbbbb", zorder=1, label="not eligible")
        ax.set_xlim(p.centroid_x.min() - 5e4, p.centroid_x.max() + 5e4)
        ax.set_ylim(p.centroid_y.min() - 5e4, p.centroid_y.max() + 5e4)
        ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])

    el = p[p.eligible]
    # Map 1: rho
    fig, ax = plt.subplots(figsize=(9, 9))
    base(ax)
    d = el[el.rho.notna()]
    m = el[el.rho.isna()]
    ax.scatter(m.centroid_x, m.centroid_y, s=28, facecolors="none", edgecolors="black", linewidths=0.8,
               zorder=2, label="eligible, rho missing (0 isolations)")
    if len(d):
        sc = ax.scatter(d.centroid_x, d.centroid_y, s=45, c=d.log10_rho, cmap="viridis", zorder=3,
                        edgecolors="black", linewidths=0.4, label="eligible, rho defined")
        fig.colorbar(sc, ax=ax, shrink=0.6, label="log10 rho (S0, R = 20 km)")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Correlation penalty rho by community (S0, ring 20 km)\nUpper bound: final perimeters assume simultaneous closure")
    fig.savefig(OUT / "map_rho_S0_R20.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Map 2: exits vs N_eff
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 8), gridspec_kw={"width_ratios": [1.4, 1]})
    base(ax)
    d = el[el.N_eff.notna()]
    m = el[el.N_eff.isna()]
    ax.scatter(m.centroid_x, m.centroid_y, s=28, facecolors="none", edgecolors="black", linewidths=0.8,
               zorder=2, label="eligible, N_eff missing (no exit ever closed)")
    if len(d):
        sc = ax.scatter(d.centroid_x, d.centroid_y, s=20 + 6 * d.exits.clip(upper=30), c=d.exits_minus_N_eff,
                        cmap="magma_r", zorder=3, edgecolors="black", linewidths=0.4, label="eligible (size = exits)")
        fig.colorbar(sc, ax=ax, shrink=0.6, label="exits − N_eff")
        ax2.scatter(d.exits, d.N_eff, c=d.exits_minus_N_eff, cmap="magma_r", edgecolors="black", linewidths=0.4)
        mx = float(max(d.exits.max(), 2))
        ax2.plot([0, mx], [0, mx], "k--", lw=0.8, label="N_eff = exits")
        ax2.set_xlabel("exits (edge-disjoint paths)"); ax2.set_ylabel("N_eff (closed-at-least-once exits)")
        ax2.legend(fontsize=8)
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Exit count vs effective exits (S0, ring 20 km)")
    fig.savefig(OUT / "map_exits_vs_neff_S0_R20.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(res, meta, net):
    maps(res, net)
    v = meta["verdict"]
    p = res[(res.rule == "S0") & (res.ring_radius_km == 20)]
    el = p[p.eligible]
    p100 = res[(res.rule == "S100") & (res.ring_radius_km == 20)]
    el100 = p100[p100.eligible]

    if v["verdict"] == "NOT EVALUABLE":
        headline = (f"**NOT EVALUABLE.** Only {v['n_eligible']} communities were eligible under S0 at R = 20 km "
                    f"(pre-registered minimum 10). No verdict is issued.")
    else:
        headline = (f"**{v['verdict']}.** {v['n_pass']} of {v['n_eligible']} eligible communities "
                    f"({v['share']:.1%}) have rho > 5 with a bootstrap lower 95% bound > 1 under S0 at R = 20 km. "
                    f"The pre-registered threshold was 20%.")

    gap = el[el.N_eff.notna()].sort_values("exits_minus_N_eff", ascending=False).head(10)
    top_cols = [("Community", lambda r: r.ucl_name), ("Population", lambda r: f"{r.population:,}"),
                ("Exits", lambda r: fmt(r.exits, 0)), ("N_eff", lambda r: fmt(r.N_eff)),
                ("Exits − N_eff", lambda r: fmt(r.exits_minus_N_eff)),
                ("Excluded (never/always closed)", lambda r: f"{fmt(r.excluded_never_closed,0)}/{fmt(r.excluded_always_closed,0)}"),
                ("Relevant fires", lambda r: str(r.n_relevant_fires)), ("Isolations", lambda r: fmt(r.k_isolated, 0)),
                ("rho [95% CI]", lambda r: f"{fmt(r.rho)} [{fmt(r.rho_lo)}, {fmt(r.rho_hi)}]")]
    all_cols = [("Community", lambda r: r.ucl_name), ("Pop.", lambda r: f"{r.population:,}"),
                ("Exits", lambda r: fmt(r.exits, 0)), ("Fires", lambda r: str(r.n_relevant_fires)),
                ("Fires closing ≥1 exit", lambda r: fmt(r.fires_closing_any_exit, 0)),
                ("Isolations", lambda r: fmt(r.k_isolated, 0)), ("P_obs", lambda r: fmt(r.P_obs, 3)),
                ("P_ind", lambda r: fmt(r.P_ind, 3)),
                ("rho [95% CI]", lambda r: f"{fmt(r.rho)} [{fmt(r.rho_lo)}, {fmt(r.rho_hi)}]"),
                ("N_eff", lambda r: fmt(r.N_eff))]

    text = f"""# Results: correlated-exit-failure pilot

## Verdict (pre-registered rule, S0, ring R = 20 km)

{headline}

- Communities considered: {v['n_communities']} NSW UCLs (population ≥ 200).
- Failing eligibility: ring inside the polygon {v['fail_ring_inside']}; fewer than 2 exits {v['fail_exits']}; fewer than 10 relevant fires {v['fail_fires']}. The criteria overlap.
- Eligible communities with a defined rho (≥ 1 observed isolation): {v['n_rho_defined']} of {v['n_eligible']}.

This is a descriptive measurement. It is not a causal estimate and it says nothing about lives saved.

## Distributions (eligible communities, S0, R = 20 km)

- rho (defined values only): {quant_table(el.rho)}
- Bootstrap lower bound of rho: {quant_table(el.rho_lo)}
- N_eff: {quant_table(el.N_eff)}
- Exits: {quant_table(el.exits)}
- Relevant fires per community: {quant_table(el.n_relevant_fires.astype(float))}
- Relevant fires closing at least one exit: {quant_table(el.fires_closing_any_exit)}

Under S100 at R = 20 km: rho {quant_table(el100.rho)}; N_eff {quant_table(el100.N_eff)}.

## All eligible communities (S0, R = 20 km)

{community_table(el.sort_values('rho', ascending=False, na_position='last'), all_cols) if len(el) else 'None.'}

## Largest exits − N_eff gaps (S0, R = 20 km)

N_eff counts only exits that closed in at least one relevant fire and not in every fire. The gap
therefore includes exits that never closed (they are excluded from N_eff, not counted as independent).

{community_table(gap, top_cols) if len(gap) else 'No eligible community has a defined N_eff.'}

## Sensitivity: ring radius and exposure rule

{sensitivity(res)}

Only S0 at R = 20 km determines the verdict. The other rows are sensitivity analyses.

## Why no community could meet the rule (descriptive; not pre-registered)

The highest number of isolating fires in any eligible community under S0 at R = 20 km was
{fmt(el.k_isolated.max(), 0)}. When a community has exactly one isolating fire among n, a bootstrap
resample leaves that fire out with probability (1 − 1/n)^n, which is about 35% for n = 10 to 20.
Resamples without it have undefined rho, so the 2.5th percentile is undefined and the lower bound
cannot exceed 1. Under this rule a community needs roughly four or more isolating fires before the
lower bound can clear 1. Four seasons of mapped fires (2019-20 to 2022-23) never produce that.

The FAIL therefore reflects too few joint-failure events for the pre-registered test, as well as
what those events show. It is not evidence that exits fail independently. The rule was not changed.

## Observed isolations outside the eligible set (descriptive; not pre-registered)

Communities with at least one S0 isolation at R = 20 km that failed eligibility. They are reported
for context only and play no part in the verdict.

{community_table(p[(~p.eligible) & (p.k_isolated > 0)].sort_values('population', ascending=False),
                 [("Community", lambda r: r.ucl_name), ("Pop.", lambda r: f"{r.population:,}"),
                  ("Exits", lambda r: fmt(r.exits, 0)), ("Relevant fires", lambda r: str(r.n_relevant_fires)),
                  ("Isolations", lambda r: fmt(r.k_isolated, 0)),
                  ("Why ineligible", lambda r: "; ".join(x for x, bad in [("exits < 2", not r.eligible_exits), ("fires < 10", not r.eligible_fires)] if bad))])}

## Maps

- `out/map_rho_S0_R20.png`: communities coloured by log10 rho.
- `out/map_exits_vs_neff_S0_R20.png`: exits against N_eff.

## Required caveats

- **rho is an upper bound.** Final fire perimeters assume every road inside closed at the same moment, which overstates simultaneous failure. A later stage will use daily satellite fire progression to test timing.
- **Closure is inferred** from mapped footprints (the direct intersection S0 or the 100 m buffer S100), not from observed road-closure records.
- **Fires are not independent replications.** Fire events affecting the same community share weather, terrain and season. The bootstrap over fires treats them as exchangeable, so the intervals are optimistic.

## Other limitations

- Fire footprints are Geoscience Australia perimeters grouped into fire families (events within 3 days and 5 km). They cover only four seasons, 2019-20 to 2022-23, and are not FESM. A megafire complex counts as one event.
- The 2019 OSM network is treated as undirected, and `service` roads are excluded. Fire trails and tracks are not in the network.
- Hashes for the network parquet and the transport DB were frozen on 2026-09-21. No earlier provenance record exists for them. The OSM PBF and the event perimeters match earlier manifests.
- Exit paths are one minimum-total-length decomposition. Decompositions are not unique, so p_j and N_eff depend on that choice. P_obs does not, because isolation is tested on the whole graph.
- rho is missing, not zero, when a community had no observed isolation. With few fires per community the Jeffreys-smoothed probabilities remain coarse.
- P_ind multiplies across all exits, so communities with many exits get very small P_ind. rho is reported on a log10 scale in the CSV for that reason.
- Relevant fires include families that touch no road. They count in n with no closures.
- Communities are 2021 UCL boundaries against a January 2019 road network.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, runtime {meta['runtime_s']} s, run at {meta['run_utc']}.
The network had {meta['network_edges_used']:,} of {meta['network_edges_all']:,} edges after excluding service roads and self-loops.
{meta['overlay_rows_service_dropped']:,} overlay rows on service roads were ignored.
`aussef.duckdb` SHA-256 was unchanged before and after the run: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)


if __name__ == "__main__":
    # Regenerate RESULTS.md and maps from saved outputs without recomputing.
    import json
    import sys

    sys.path.insert(0, str(HERE))
    from src import inputs

    res = pd.read_parquet(OUT / "community_results.parquet")
    meta = json.loads((OUT / "run_meta.json").read_text())
    write_all(res, meta, inputs.load_network())
