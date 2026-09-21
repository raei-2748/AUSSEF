"""Stage-2 RESULTS.md and figures."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "out"
LABEL = {"A": "A: 2019–23 fires", "B": "B: 1950–2019 fires", "B_with_undated": "B + undated fires"}


def f(x, d=2):
    if x is None or pd.isna(x) or (isinstance(x, float) and not np.isfinite(x)):
        return "missing"
    return f"{x:,.{d}f}"


def figures(res):
    r = res.copy()
    r["label"] = r.apply(lambda x: f"{LABEL[x.part]} · {x.rule} · {x.ring_radius_km} km", axis=1)
    r = r.sort_values(["part", "rule", "ring_radius_km"], ascending=[False, False, True]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(r) + 1.5))
    y = np.arange(len(r))
    ok = r.R.notna()
    lo = np.where(r.R_lo.notna(), r.R_lo, np.nan)
    ax.errorbar(r.R[ok], y[ok], xerr=[(r.R - lo)[ok].fillna(0), (r.R_hi - r.R)[ok].fillna(0)], fmt="none",
                ecolor="#555", capsize=3)
    ax.scatter(r.R[ok], y[ok], c=np.where(r.primary[ok], "#c0392b", "#2c3e50"), zorder=3)
    ax.axvline(1, color="k", lw=0.8, ls="--")
    ax.axvline(2, color="#c0392b", lw=0.8, ls=":")
    ax.set_yticks(y, r.label)
    ax.set_xscale("log")
    ax.set_xlabel("R = observed ÷ expected full cut-offs (log scale). 1 = no different from luck; red dotted = pass threshold 2")
    ax.set_title("Pooled ratio with 95% interval (red = pre-registered primary)")
    fig.savefig(OUT / "pooled_ratio_forest.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    p = res[res.primary]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(p))
    ax.bar(x - 0.2, 100 * p.share_all_given_any_expected, 0.4, label="expected if roads failed independently", color="#95a5a6")
    ax.bar(x + 0.2, 100 * p.share_all_given_any_observed, 0.4, label="observed", color="#c0392b")
    ax.set_xticks(x, [LABEL[v] for v in p.part])
    ax.set_ylabel("% of fires that cut ALL roads out,\namong fires that cut at least one")
    ax.set_title("When a fire blocks one road out, how often does it block them all?")
    ax.legend(fontsize=8)
    fig.savefig(OUT / "all_given_any.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(fn(r) for _, fn in cols) + " |" for _, r in df.iterrows())


def diagnostics_section():
    loo_p, iso_p = OUT / "diagnostic_leave_top_event_out.csv", OUT / "diagnostic_isolating_events.csv"
    if not (loo_p.exists() and iso_p.exists()):
        return "## Post-hoc diagnostics\n\nNot run. Run `diagnostics.py` to add this section."
    loo, iso = pd.read_csv(loo_p), pd.read_csv(iso_p)
    lcols = [("Part", lambda r: LABEL[r.part]), ("Fire events", lambda r: r.events),
             ("Observed", lambda r: f(r.observed, 0)), ("Expected", lambda r: f(r.expected, 1)),
             ("R [95% CI]", lambda r: f"{f(r.R)} [{f(r.R_lo)}, {f(r.R_hi)}]")]
    lines = []
    for part in ("B", "A"):
        x = iso[iso.part == part]
        top = x.event_id.value_counts()
        lines.append(f"- {LABEL[part]}: {len(x)} cut-offs from {x.event_id.nunique()} fire events; the largest single "
                     f"event accounts for {top.iloc[0]}. In {int((x.share_of_town_inside_fire >= 0.5).sum())} of {len(x)} "
                     f"cut-offs, at least half the town's area lies inside the mapped fire (median {f(100 * x.share_of_town_inside_fire.median(), 0)}%).")
    return f"""## Post-hoc diagnostics (descriptive; NOT pre-registered; see DEVIATIONS.md)

**Where the cut-offs come from (S0, 20 km):**

{chr(10).join(lines)}

When most of a town lies inside a final fire perimeter, a "full cut-off" may mean the map draws the
fire around the town, not that every exit road was separately cut. Per-event detail is in
`out/diagnostic_isolating_events.csv`.

**Leaving out the single most influential fire event:**

{table(loo, lcols)}

These intervals use a different random stream from the pre-registered run, so the "all events" rows
differ slightly from the verdict table. Part A's lower bound sits close to 1: it was 0.90 in the
pre-registered run and 1.10 here. So part A's FAIL is borderline and depends on bootstrap randomness.
The pre-registered FAIL stands. Part B stays well above 1 either way."""


def write_all(res, comm, meta):
    figures(res)
    prim = res[res.primary].set_index("part")
    lines = []
    for part in ("B", "A"):
        r = prim.loc[part]
        lines.append(f"- **Part {LABEL[part]}: {r.verdict}.** R = {f(r.R)} (95% CI {f(r.R_lo)} to {f(r.R_hi)}); "
                     f"{f(r.observed_isolations, 0)} full cut-offs observed vs {f(r.expected_isolations, 1)} expected "
                     f"if exits failed independently; {f(r.pairs_any_exit_closed, 0)} town–fire pairs with ≥ 1 exit cut, "
                     f"across {r.communities} towns and {r.fire_events:,} fire events.")
    plain = []
    for part in ("B", "A"):
        r = prim.loc[part]
        plain.append(f"- {LABEL[part]}: when a fire blocked at least one road out of a town, it blocked **all** of them "
                     f"{f(100 * r.share_all_given_any_observed, 1)}% of the time. If roads failed independently we would expect "
                     f"{f(100 * r.share_all_given_any_expected, 1)}%.")

    cols = [("Part", lambda r: LABEL[r.part]), ("Rule", lambda r: r.rule), ("Ring", lambda r: f"{r.ring_radius_km} km"),
            ("Towns", lambda r: str(r.communities)), ("Fire events", lambda r: f"{r.fire_events:,}"),
            ("Pairs ≥1 exit cut", lambda r: f(r.pairs_any_exit_closed, 0)),
            ("Observed", lambda r: f(r.observed_isolations, 0)), ("Expected", lambda r: f(r.expected_isolations, 1)),
            ("R [95% CI]", lambda r: f"{f(r.R)} [{f(r.R_lo)}, {f(r.R_hi)}]"),
            ("All-cut share obs / exp", lambda r: f"{f(100*r.share_all_given_any_observed,1)}% / {f(100*r.share_all_given_any_expected,1)}%"),
            ("Verdict", lambda r: r.verdict if isinstance(r.verdict, str) and r.verdict else "(sensitivity)")]

    cp = comm[(comm.rule == "S0") & (comm.ring_radius_km == 20)]
    top = (cp[cp.part == "B"].sort_values(["isolations", "population"], ascending=False).head(15))
    tcols = [("Town", lambda r: r.ucl_name), ("Pop.", lambda r: f"{r.population:,}"), ("Exits", lambda r: str(r.exits)),
             ("Relevant fires", lambda r: str(r.n_relevant_fires)), ("Fires cutting ≥1 exit", lambda r: f(r.fires_closing_any_exit, 0)),
             ("Full cut-offs", lambda r: f(r.isolations, 0)), ("Expected if independent", lambda r: f(r.expected_isolations_independent, 2))]
    c = meta["part_b_counts"]
    x = meta["overlay_crosscheck"]

    text = f"""# Stage 2 results: pooled exit-failure test

## Verdict (pre-registered: S0, ring 20 km, PASS needs R ≥ 2 and lower 95% bound > 1)

{chr(10).join(lines)}

Part B, the independent historical record, is the confirmatory result. Part A is the discovery sample.

### In plain words

{chr(10).join(plain)}

R compares how often fires cut **every** road out of a town with how often that would happen by luck,
if each road failed independently. R = 1 means no different from luck. R = 2 means twice as often.

This is a descriptive measurement. It is not a causal estimate and says nothing about lives saved.

## All results (primary and sensitivity)

{table(res.sort_values(['part','rule','ring_radius_km']), cols)}

Only the two rows marked with a verdict (S0, 20 km, parts A and B) decide the outcome.

## Towns with the most full cut-offs in the historical record (part B, S0, 20 km)

{table(top, tcols)}

## Figures

- `out/pooled_ratio_forest.png`: R with its 95% interval for every analysis.
- `out/all_given_any.png`: when one road is blocked, how often are all blocked (observed vs expected).

{diagnostics_section()}

## Data checks

- Part B fire records: {c['B']['nsw_bushfires']:,} NSW bushfire records.
  - {c['B']['season_composites_removed']:,} season composites removed.
  - {c['B']['undated_non_composite']:,} undated records removed (they are used only in the "B + undated" sensitivity).
  - {c['B']['dated_outside_window']:,} dated outside July 1950 to June 2019.
  - **{c['B']['fires_used']:,} fires used, grouped into {c['B']['events']:,} fire events.**
- Overlay method check: rebuilding part A's S0 road closures with the part-B method matched the stage-1 overlay on {f(100 * x['jaccard'], 1) if x['jaccard'] else 'missing'}% of edges ({x['edges_in_both']:,} of {x['edges_overlay_or_rebuilt']:,}, Jaccard, service roads excluded).
- Exit paths were reused unchanged from stage 1 (hash-verified).

## Required caveats

- **R is an upper bound.** Fire maps show the final burned area only, as if every road inside was cut at the same moment. Roads that burned days apart are counted as cut together. A later stage will test timing with daily satellite fire data (see `TIMING_SCOPING.md`).
- **Closure is inferred** from mapped footprints, not from recorded road closures.
- **Fires are not independent.** The bootstrap resamples whole fire events, which handles one fire hitting many towns, but not shared weather or seasons.
- **Part B uses the 2019 road network** for fires back to 1950. Some roads did not exist then, and others have since closed.
- **Part B coverage** comes from NSW national-parks mapping. Fires away from park land, and older fires, may be missing or less precise.
- Relevant fires include those that touch no road. They add to the number of fires but not to closures.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, runtime {meta['runtime_s']} s, run at {meta['run_utc']}.
`aussef.duckdb` SHA-256 was unchanged before and after: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)


if __name__ == "__main__":
    import json

    write_all(pd.read_csv(OUT / "pooled_results.csv"), pd.read_parquet(OUT / "community_level.parquet"),
              json.loads((OUT / "run_meta.json").read_text()))
