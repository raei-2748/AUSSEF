"""Stage-4 RESULTS.md and figure."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def f(x, d=2):
    if x is None or pd.isna(x) or (isinstance(x, float) and not np.isfinite(x)):
        return "missing"
    return f"{x:,.{d}f}"


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(fn(r) for _, fn in cols) + " |" for _, r in df.iterrows())


def figure(pairs):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bins = np.arange(0, 252, 12)
    for col, lab, colr in (("stage3_spread_hours_whole_route", "whole route (stage 3)", "#95a5a6"),
                           ("spread_hours_K5km", "near town, within 5 km (stage 4)", "#c0392b")):
        s = pairs[col].dropna()
        ax.hist(np.clip(s, 0, 240), bins=bins, alpha=0.7, label=f"{lab}: {len(s)} dated", color=colr)
    ax.axvline(12, color="k", ls=":", label="12 h window")
    ax.set_xlabel("Hours between fire reaching the first and the last exit road (capped at 240)")
    ax.set_ylabel("Full cut-offs")
    ax.set_title("Measuring near the town vs along the whole route")
    ax.legend(fontsize=8)
    fig.savefig(OUT / "timing_near_town_vs_route.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(res, pairs, meta):
    figure(pairs)
    prim = res[res.verdict != ""].iloc[0]
    base = res.iloc[0]
    cols = [("Timing rule", lambda r: r.timing), ("Timed cut-offs", lambda r: f(r.observed, 0)),
            ("Expected", lambda r: f(r.expected, 2)), ("R [95% CI]", lambda r: f"{f(r.R)} [{f(r.R_lo)}, {f(r.R_hi)}]"),
            ("Verdict", lambda r: r.verdict or "(comparison / sensitivity)")]
    pcols = [("Town", lambda r: r.town), ("Event", lambda r: r.event_id), ("Exits", lambda r: str(r.exits)),
             ("Dated near town", lambda r: str(r.exits_dated_K5km)),
             ("First exit reached (UTC)", lambda r: str(r.first_hit_K5km)[:16] if pd.notna(r.first_hit_K5km) else "undated"),
             ("Hours first→last, near town", lambda r: f(r.spread_hours_K5km, 1)),
             ("Hours, whole route (stage 3)", lambda r: f(r.stage3_spread_hours_whole_route, 1))]
    s = pairs.spread_hours_K5km
    text = f"""# Stage 4 results: timing near the town

## Verdict (pre-registered; a follow-up motivated by stage 3, not an independent test)

**{prim.verdict}.** When each exit is dated by when fire reached it within about 5 km of the town,
{f(prim.observed, 0)} of {f(base.observed, 0)} satellite-era full cut-offs had fire reach every exit within 12 hours.
R_timed = {f(prim.R)} (95% CI {f(prim.R_lo)} to {f(prim.R_hi)}) against {f(prim.expected, 2)} expected under independence.
PASS needed R_timed ≥ 2 and a lower bound > 1.

### In plain words

Stage 3 timed each road by the first fire detected anywhere along it, up to 20 km out, which could be
weeks before fire reached the town. Stage 4 times each road near the town, where people get trapped.
Measured this way, the typical gap between fire reaching the first and the last road out was
{f(s.median(), 1)} hours ({int(s.notna().sum())} of {len(pairs)} cut-offs could be dated on every road). For comparison,
the whole-route gap in stage 3 was {f(pairs.stage3_spread_hours_whole_route.median(), 1)} hours.

This is a descriptive measurement. It is not a causal estimate and says nothing about lives saved.

## All results

{table(res, cols)}

The first row is the stage-3 perimeter sample, reproduced exactly as a built-in check.

## Each full cut-off

{table(pairs.sort_values("first_hit_K5km"), pcols)}

Figure: `out/timing_near_town_vs_route.png`.

## Caveats

- This test was designed after seeing the stage-3 per-town timing table, so treat it as supporting evidence, not independent confirmation.
- Hotspots have ±375 m to ±1 km location error and a few overpasses a day, and smoke or cloud can hide fire. A hotspot near a road does not prove the road was closed.
- Timing within about 5 km of town still measures when fire *arrived*, not how long roads stayed shut.
- Fires are not independent; the bootstrap resamples whole fire events. The 2019 road network is used throughout.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, runtime {meta['runtime_s']} s, run at {meta['run_utc']}.
The stage-3 hotspot cache was hash-verified; no network requests were made.
`aussef.duckdb` SHA-256 was unchanged before and after: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)
