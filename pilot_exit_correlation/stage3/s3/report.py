"""Stage-3 RESULTS.md and figures."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "out"


def f(x, d=2):
    if x is None or pd.isna(x) or (isinstance(x, float) and not np.isfinite(x)):
        return "missing"
    return f"{x:,.{d}f}"


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(fn(r) for _, fn in cols) + " |" for _, r in df.iterrows())


def figures(res, pairs):
    r = res.copy().reset_index(drop=True)
    r["label"] = r.analysis + " · " + r["sample"].str.slice(0, 22) + " · " + r.closure + " · " + r.timing.str.slice(0, 34)
    fig, ax = plt.subplots(figsize=(10, 0.45 * len(r) + 1.5))
    y = np.arange(len(r))[::-1]
    ok = r.R.notna() & (r.R > 0)
    lo = r.R_lo.where(r.R_lo > 0)
    ax.errorbar(r.R[ok], y[ok], xerr=[(r.R - lo.fillna(r.R * 0.05))[ok], (r.R_hi - r.R)[ok].fillna(0)],
                fmt="none", ecolor="#555", capsize=3)
    ax.scatter(r.R[ok], y[ok], c=np.where(r.verdict[ok] != "", "#c0392b", "#2c3e50"), zorder=3)
    ax.axvline(1, color="k", lw=0.8, ls="--")
    ax.axvline(2, color="#c0392b", lw=0.8, ls=":")
    ax.set_yticks(y, r.label, fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("R = observed ÷ expected full cut-offs (log). 1 = luck; red dotted = pass threshold 2")
    ax.set_title("Stage 3: does the effect survive the stricter checks? (red = pre-registered verdict rows)")
    fig.savefig(OUT / "stage3_ratio_forest.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    p = pairs[~pairs.outside_town_rule] if len(pairs) else pairs
    fig, ax = plt.subplots(figsize=(7, 4))
    if len(p) and p.spread_hours_1km.notna().any():
        s = p.spread_hours_1km.dropna()
        ax.hist(np.clip(s, 0, 240), bins=np.arange(0, 252, 12), color="#2c3e50")
        ax.axvline(12, color="#c0392b", ls=":", label="12 h window")
        ax.legend()
    ax.set_xlabel("Hours between the first and last exit road being reached by fire (capped at 240)")
    ax.set_ylabel("Full cut-offs")
    ax.set_title(f"Timing of full cut-offs (satellite hotspots; {int(p.spread_hours_1km.isna().sum()) if len(p) else 0} could not be dated)")
    fig.savefig(OUT / "cutoff_timing_hist.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(res, pairs, meta):
    figures(res, pairs)
    v = res[res.verdict != ""]
    lines = [f"- **{r.analysis} · {r['sample']} · {r.closure} · {r.timing}: {r.verdict}.** R = {f(r.R)} "
             f"(95% CI {f(r.R_lo)} to {f(r.R_hi)}); {f(r.observed, 0)} full cut-offs observed vs {f(r.expected, 2)} expected."
             for _, r in v.iterrows()]
    cols = [("Check", lambda r: r.analysis), ("Sample", lambda r: r["sample"]), ("Closure", lambda r: r.closure),
            ("Timing", lambda r: r.timing), ("Observed", lambda r: f(r.observed, 0)),
            ("Expected", lambda r: f(r.expected, 2)), ("R [95% CI]", lambda r: f"{f(r.R)} [{f(r.R_lo)}, {f(r.R_hi)}]"),
            ("Verdict", lambda r: r.verdict or "(comparison / sensitivity)")]
    p = pairs[~pairs.outside_town_rule] if len(pairs) else pairs
    timing_txt = "No timing analysis was possible."
    ptable = ""
    if len(p):
        dated = p.spread_hours_1km.notna()
        timing_txt = (f"Of {len(p)} perimeter full cut-offs in the satellite era, {int(dated.sum())} could be dated on every exit "
                      f"(hotspot within 1 km). Among those, the median time between the first and last exit being reached was "
                      f"{f(p.spread_hours_1km.median(), 1)} h; {int((p.spread_hours_1km <= 12).sum())} were within 12 h, "
                      f"{int((p.spread_hours_1km <= 24).sum())} within 24 h.")
        pcols = [("Town", lambda r: r.town), ("Fire event", lambda r: r.event_id), ("Part", lambda r: r.part),
                 ("Exits", lambda r: str(r.exits)), ("Exits dated", lambda r: str(r.exits_dated_1km)),
                 ("First exit hit (UTC)", lambda r: str(r.first_hit_1km)[:16] if pd.notna(r.first_hit_1km) else "undated"),
                 ("Hours first→last exit", lambda r: f(r.spread_hours_1km, 1))]
        ptable = table(p.sort_values("first_hit_1km"), pcols)

    text = f"""# Stage 3 results: stricter checks

## Verdicts (pre-registered)

{chr(10).join(lines)}

### In plain words

- **3a (outside-the-town check):** a road only counts as cut if it burns *outside* the town. This removes cases where the fire map simply surrounds the town.
- **3b (timing check):** a cut-off only counts if satellites show fire reaching *every* road out within 12 hours. Cut-offs that satellites could not date count as "not at the same time", so this check is deliberately strict.

The true effect likely lies between the stage-2 figure (upper bound, no timing) and the 3b timed
figure (conservative).

This is a descriptive measurement. It is not a causal estimate and says nothing about lives saved.

## All results

{table(res, cols)}

Rows marked "(comparison / sensitivity)" carry no verdict. The 3a rows with the stage-2 rule reproduce
stage 2 exactly (a built-in check).

## Timing of each full cut-off (satellite era, S0)

{timing_txt}

{ptable}

## Figures

- `out/stage3_ratio_forest.png`: every ratio with its 95% interval.
- `out/cutoff_timing_hist.png`: hours between the first and last exit being reached.

## Important limit of the timing check

The timing rule compares when fire **first reached** each exit route. Each route is stored all the
way out to the 20 km ring, so its "hit time" is the earliest hotspot anywhere along it, which can be
far from the town. A road first reached on day 1 may still be closed, or may have reopened, weeks
later. The check therefore tests "fire first arrived at every exit within W hours". That is stricter
than "every exit was closed at the same moment", which would need closure durations (how long each
road stayed shut). No such data exist in this project. Some long gaps in the table, such as about 35
days for Batemans Bay in the 2019–20 Currowan fire, reflect this: fire reached one exit route early,
far from town, and another much later.

## Required caveats

- Hotspots are satellite detections: ±375 m to ±1 km location error, a few overpasses a day, and gaps under smoke and cloud. A hotspot near a road does not prove the road was impassable, and a missing hotspot does not prove it was open.
- Closure is inferred from fire maps and satellite detections, not from recorded road closures.
- Fires are not independent replications. The bootstrap resamples whole fire events.
- The 2019 road network is used for all fires.
- Satellite timing is only possible for fires from September 2002 onwards.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, runtime {meta['runtime_s']} s, run at {meta['run_utc']}.
Hotspots: {meta['hotspot_events']} fire events, {meta['hotspot_rows']:,} detections (DEA Hotspots; manifest in `out/hotspot_manifest.csv`).
`aussef.duckdb` SHA-256 was unchanged before and after: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)


if __name__ == "__main__":
    import json

    write_all(pd.read_csv(OUT / "stage3_results.csv").fillna({"verdict": ""}),
              pd.read_parquet(OUT / "timing_pairs.parquet"), json.loads((OUT / "run_meta.json").read_text()))
