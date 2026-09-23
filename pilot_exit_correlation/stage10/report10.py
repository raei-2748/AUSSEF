"""Stage-10 RESULTS.md and figures."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
RULE = {"s0": "outline touches road (S0)", "s0_half": "≥ 50% of segment inside outline", "s100": "within 100 m (S100)"}


def f(x, d=1):
    if x is None or (isinstance(x, float) and np.isnan(x)) or pd.isna(x):
        return "missing"
    return f"{x:,.{d}f}"


def pct(x):
    return "missing" if x is None or pd.isna(x) else f"{100 * x:.0f}%"


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(str(fn(r)) for _, fn in cols) + " |" for _, r in df.iterrows())


def figures(pairs, tp, fiscal_idx):
    e = pairs[pairs.eligible]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for flag, lab, c in ((True, "outline touches road", "#c0392b"), (False, "fire within 500 m, road untouched", "#2c3e50")):
        v = e.loc[e.s0 == flag, "min_ratio"].clip(upper=1.5)
        ax.hist(v, bins=np.linspace(0, 1.5, 16), alpha=0.7, label=f"{lab} (n={len(v)})", color=c)
    ax.axvline(0.2, color="k", ls=":", label="20% of normal = 'closed'")
    ax.set_xlabel("lowest daily traffic during the fire, as a share of normal for that date")
    ax.set_ylabel("counter × fire pairs")
    ax.set_title("Did traffic actually stop on roads the fire outline touched?")
    ax.legend(fontsize=8)
    fig.savefig(OUT / "closure_validation.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    s = tp.spread_hours_K5km.dropna()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(np.clip(s, 0, 240), bins=np.arange(0, 252, 12), color="#2c3e50")
    for h, c in ((12, "#c0392b"), (24, "#e67e22")):
        ax.axvline(h, color=c, ls=":", label=f"{h} h")
    ax.set_xlabel("hours between fire reaching the first and the last road out (near town, capped at 240)")
    ax.set_ylabel("cut-offs")
    ax.set_title("The escape window")
    ax.legend()
    fig.savefig(OUT / "escape_window.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, m in zip(axes, ["road spending", "total grants"]):
        d = fiscal_idx[fiscal_idx.measure == m].pivot(index="year_start", columns="group", values="median_index")
        for gname, c in (("cut off", "#c0392b"), ("burned only", "#e67e22"), ("untouched", "#95a5a6")):
            if gname in d:
                ax.plot(d.index, d[gname], marker="o", color=c, label=gname)
        ax.axvline(2018.5, color="k", ls=":", lw=0.8)
        ax.set_title(f"Council {m} (median, 2018-19 = 100)")
        ax.set_xlabel("financial year starting")
        ax.legend(fontsize=8)
    fig.savefig(OUT / "fiscal_index.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(pairs, resA, partB, tp, totC, partC, fiscal_idx, meta):
    figures(pairs, tp, fiscal_idx)
    a = resA[(resA.rule == "s0") & (resA.threshold_pct == 20)].iloc[0]
    acols = [("Closure rule", lambda r: RULE[r.rule]), ("Traffic threshold", lambda r: f"≤ {int(r.threshold_pct)}% of normal"),
             ("Rule says closed: traffic stopped", lambda r: f"{int(r.pred_closed_observed)} / {int(r.pred_closed_pairs)} = {pct(r.rate_pred_closed)} [{pct(r.rate_pred_closed_lo)}–{pct(r.rate_pred_closed_hi)}]"),
             ("Road untouched: traffic stopped", lambda r: f"{int(r.untouched_observed)} / {int(r.untouched_pairs)} = {pct(r.rate_untouched)} [{pct(r.rate_untouched_lo)}–{pct(r.rate_untouched_hi)}]"),
             ("Interpretation", lambda r: r.interpretation or "(sensitivity)")]
    ep = pairs[pairs.eligible].sort_values(["s0", "min_ratio"], ascending=[False, True])
    pcols = [("Counter", lambda r: r.station_key), ("Fire event", lambda r: r.event_id),
             ("Fire start", lambda r: str(pd.Timestamp(r.start).date())),
             ("Outline touches", lambda r: "yes" if r.s0 else "no"), ("Share inside", lambda r: pct(r.inside_share)),
             ("Lowest day vs normal", lambda r: pct(r.min_ratio)), ("Lowest day", lambda r: r.min_day),
             ("Valid days", lambda r: int(r.window_days_valid))]
    ccols = [("Vehicles", lambda r: r.vehicle_class), ("Counters", lambda r: int(r.stations)),
             ("Counters with ≥ 1 week below 80%", lambda r: int(r.stations_any_week_below_80)),
             ("Counter-weeks below 80%", lambda r: f"{int(r.station_weeks_below_80)} of {int(r.weeks_compared)}"),
             ("Median deepest week", lambda r: pct(r.median_deepest_ratio)),
             ("Net missing trips", lambda r: f"{f(r.net_deficit_trips, 0)} ({f(r.net_deficit_pct)}% of normal)")]
    gates = meta["partD_gates"]
    gtxt = "\n".join(f"- **{k}:** largest post-fire gap (cut off − burned only) {f(v['post_max_gap'])} index points vs largest pre-fire gap {f(v['pre_max_abs_gap'])}; councils {v['councils']}; **{v['status']}**."
                     for k, v in gates.items())
    b = partB
    text = f"""# Stage 10 results: were the roads really closed, how long was the escape window, and what did isolation cost?

## A. Did traffic actually stop on roads the fire outline touched?

**{meta['partA_verdict']}.** On {int(a.pred_closed_pairs)} counter × fire cases where our rule says the road was
closed, traffic fell to 20% of normal or less on at least one day in {pct(a.rate_pred_closed)} of cases
(95% interval {pct(a.rate_pred_closed_lo)}–{pct(a.rate_pred_closed_hi)}). On {int(a.untouched_pairs)} cases where a fire was within 500 m but did not touch
the road, it happened in {pct(a.rate_untouched)} of cases.

{table(resA, acols)}

**In plain words.** We checked our "fire map touches road = road closed" rule against real traffic
counters. The table shows how often traffic really stopped when our rule said it would, and how often
it stopped anyway when the fire was nearby but didn't touch the road. With this few cases, the check
can only catch a badly wrong rule; it cannot measure accuracy precisely.

**What this means for the project.** On roads the fire outline touched, daily traffic usually kept
flowing: the lowest day was typically half or more of normal, and never close to zero. The
"outline touches road = road closed" rule therefore **overstates closure** at the level of whole days.
Every earlier stage built on that rule (stages 2–4 and 6–9) should be read as measuring **exposure of
roads to fire footprints**, not confirmed closures. Two limits remain: daily totals can hide closures
lasting only hours (an hourly check would be a new, separately pre-registered test), and there are
only 7 cases, mostly smaller historical fires.

Every case is listed below, so anyone can check it. Figure: `out/closure_validation.png`.

{table(ep, pcols) if len(ep) else 'No eligible cases.'}

All-vehicle volumes use the counter's published total where it exists, otherwise light + heavy
vehicles added together (many counters never publish a total; see DEVIATIONS.md V1).

Coverage: {meta['stations_with_data']} counters with data, {meta['stations_matched']} matched to a road; {meta['pairs_total']} counter × fire pairs
within 500 m (2006–2020), of which {meta['pairs_eligible']} had enough valid days and a baseline.

## B. The escape window (from stage 4, restated)

Of {b['cutoffs']} satellite-era full cut-offs, {b['dated']} could be dated on every exit near town.
The time between fire reaching the **first** and the **last** road out was:
median **{f(b['median_h'])} hours** (middle half {f(b['q1_h'])}–{f(b['q3_h'])} h); within 6 h in {b['within_6h']}, within 12 h in
{b['within_12h']}, within 24 h in {b['within_24h']}. {b['undated']} could not be dated.

**In plain words.** Once fire reaches one road out of town, residents typically have about a day
before the others go too, and sometimes only a few hours. This is the evacuation window. People who
can't leave quickly (older residents, people needing help, people without cars, visitors) are the ones
this window matters most for. Figure: `out/escape_window.png`; list: `out/escape_window.csv`.

## C. Short-run disruption to movement of people and freight (Black Summer, pre-COVID)

Counters within 5 km of a Black Summer fire, weekly totals from 4 November 2019 to 23 February 2020,
compared with the same weeks in the three previous summers.

{table(totC, ccols) if len(totC) else 'No counters with comparable weeks.'}

**In plain words.** This shows how much movement of people and goods on roads near the fires fell
below normal over the summer. It measures disrupted trips, not dollars, and not every drop is due to
closures (evacuation orders, tourists told to leave, and smoke all cut traffic). Per-counter detail:
`out/corridor_disruption.csv`.

## D. Is a council-finance model worth building? (pre-set go / no-go rule)

**{meta['partD_verdict']}.**

{gtxt}

Figure: `out/fiscal_index.png`; data: `out/fiscal_index.csv`. The rule: GO only if councils with
cut-off towns jump more than burned-only councils after the fire, by more than the gap between the same
groups in the years before it.

## Caveats

- **Few validation cases.** Counters rarely sit exactly on the roads fires touched, so the intervals are wide.
- **Traffic stopping is not the same as an official closure.** Evacuation orders, tourist leave zones and smoke reduce traffic too, and a road can be closed without a counter on it.
- **Counters are fixed points.** A closure elsewhere on a road may not show at the counter.
- **Raw data.** Traffic counts come from the raw database layer (approved). Days with missing hours or directions are excluded, never treated as zero.
- **Pre-COVID only.** Parts A and C stop before March 2020 effects where relevant.
- Descriptive throughout: no causal claims, and no claims that anyone was trapped.

## Run

Run at {meta['run_utc']}. Traffic raw layer: {meta['traffic_raw_rows']:,} rows, fingerprint `{meta['traffic_fingerprint_sha256']}`.
`aussef.duckdb` SHA-256 unchanged: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)
