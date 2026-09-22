"""Stage-9 RESULTS.md and figures."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LABEL = {"pct_65_plus": "Residents aged 65+ (%)", "pct_need_assistance": "Need assistance (%)",
         "pct_no_car": "Dwellings with no car (%)", "pct_lone_person_hh": "One-person households (%)",
         "pct_rented": "Rented dwellings (%)", "median_hh_income_weekly": "Median household income ($/wk)"}


def f(x, d=1):
    if x is None or pd.isna(x):
        return "missing"
    return f"{x:,.{d}f}"


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(str(fn(r)) for _, fn in cols) + " |" for _, r in df.iterrows())


def figures(buckets, town):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    w = 0.38
    for i, (m, c) in enumerate([("counted exits (PNAS-style)", "#95a5a6"), ("max-flow exits (this project)", "#c0392b")]):
        b = buckets[buckets.measure == m]
        ax.bar(np.arange(len(b)) + (i - 0.5) * w, b.cut_off_rate_pct.fillna(0), w, label=m, color=c)
    b0 = buckets[buckets.measure == "counted exits (PNAS-style)"]
    ax.set_xticks(np.arange(len(b0)), b0.bucket.astype(str))
    ax.set_xlabel("exits attributed to the town")
    ax.set_ylabel("% of towns ever fully cut off by fire")
    ax.set_title("More exits should mean less risk. Does it?")
    ax.legend(fontsize=8)
    fig.savefig(OUT / "cutoff_rate_by_exits.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    g = town[town.group_reported == "illusory redundancy"]
    s = town[town.group_reported == "correctly rated safe"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax, m in zip(axes, ["pct_65_plus", "pct_need_assistance", "pct_no_car"]):
        data = [g[m].dropna(), s[m].dropna()]
        ax.boxplot(data, showfliers=False)
        rng = np.random.default_rng(0)
        for i, d in enumerate(data, start=1):
            ax.scatter(i + rng.uniform(-0.1, 0.1, len(d)), d, s=12, alpha=0.7, color="#c0392b" if i == 1 else "#2c3e50")
        ax.set_xticks([1, 2], ["rated safe\nbut cut off", "rated safe\nand never cut off"], fontsize=8)
        ax.set_title(LABEL[m], fontsize=9)
    fig.suptitle("Who lives in the towns a count-based standard gets wrong?", fontsize=10)
    fig.savefig(OUT / "who_lives_in_blind_spot.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(res, buckets, town, council, meta):
    figures(buckets, town)
    tt, cost = meta["illusory_totals"], meta["cost"]
    p = res[res.verdict != ""].iloc[0]
    g6 = meta["groups_T6"]
    rcols = [("Measure", lambda r: LABEL[r.measure]), ("Threshold", lambda r: f"≥ {int(r.threshold)} exits"),
             ("n (illusory / safe)", lambda r: f"{int(r.n_illusory)} / {int(r.n_safe)}"),
             ("Median illusory", lambda r: f(r.get("median_illusory"))),
             ("Median correctly safe", lambda r: f(r.get("median_safe"))),
             ("Difference [95% CI]", lambda r: f"{f(r.get('diff'))} [{f(r.get('diff_lo'))}, {f(r.get('diff_hi'))}]"),
             ("p", lambda r: f(r.get("p_mwu"), 3)), ("p (Holm)", lambda r: f(r.get("p_holm"), 3)),
             ("Verdict", lambda r: r.verdict or "")]
    bcols = [("Measure", lambda r: r.measure), ("Exits", lambda r: r.bucket), ("Towns", lambda r: int(r.towns)),
             ("Ever cut off", lambda r: int(r.cut_off)), ("Cut-off rate", lambda r: f"{f(r.cut_off_rate_pct)}%")]
    ill = town[town.group_reported == "illusory redundancy"].sort_values("persons", ascending=False)
    icols = [("Town", lambda r: r.town), ("Roads out (unhalved)", lambda r: int(r.distinct_roads_crossing)),
             ("Counted exits (halved)", lambda r: int(r.counted_exits)),
             ("Max-flow exits", lambda r: int(r.max_flow_exits)), ("Residents", lambda r: f"{int(r.persons):,}"),
             ("Aged 65+ %", lambda r: f(r.pct_65_plus)), ("State-owned share of exits", lambda r: f"{f(100 * r.state_share)}%"),
             ("Council", lambda r: r.LGA_NAME21)]
    ccols = [("Council", lambda r: r.council), ("Towns", lambda r: int(r.towns)),
             ("Residents", lambda r: f"{int(r.residents):,}"), ("Aged 65+", lambda r: f"{int(r.aged_65_plus):,}"),
             ("Burned exit km", lambda r: f(r.burned_exit_km)),
             ("Own-source $ per resident", lambda r: f"${f(r.own_source_per_resident_aud, 0)}"),
             ("Road spend per km", lambda r: f"${f(r.road_spend_per_km_aud, 0)}"),
             ("Indicative annual cost", lambda r: f"${f(r.indicative_annual_cost_aud, 0)}")]

    text = f"""# Stage 9 results: does counting exits find the towns fire cuts off, and who pays?

## Headline

Published work rates a community's evacuation safety by **counting exit roads** (Fong et al., PNAS 2026:
fatality risk flattens at about six exits). We applied that counting method to NSW and checked it
against 70 years of fires.

**1. The count does track risk, in the right direction.** The share of towns ever fully cut off falls
steadily as the count rises, and no NSW town with 4 or more counted exits has ever been cut off. Our
network-based measure shows the same: towns with 6 or more independent routes were never cut off, while
a third of two-exit towns were.

**2. But the published threshold cannot be used here.** Only {g6.get('correctly rated safe', 0) + g6.get('illusory redundancy', 0)} NSW towns
in our sample reach 6 counted exits at all, so the six-exit standard does not separate Australian country
towns. The pre-registered comparison at that threshold is therefore **{meta['verdict']}**.

**3. The blind spot is real but smaller than expected.** Using the same method without its
"divide by two" step, and a threshold of 3 roads out ({meta['report_variant']}), **{tt['towns']} towns** look adequately
connected yet fire has cut every exit at once. **{tt['residents']:,} people live in them**, including
**{tt['aged_65_plus']:,} aged 65+**, **{tt['need_assistance']:,} who need help with everyday activities** and
**{tt['dwellings_no_car']:,} homes with no car**.

**4. The exits that fail are mostly the State's responsibility.** In those towns
**{f(100 * meta['state_share_illusory'])}%** of exit-route length is State-owned road (NSW Government), against
{f(100 * meta['state_share_all'])}% across all towns, and **{f(100 * meta['burned_state_share_illusory'])}%** of the exit road that actually burned
was State-owned. Councils hold the local roads and the local budget; the State holds most of the
roads that fail.

**5. Indicative scale of the affected roads:** ${f(cost['total'], 0)} a year in maintenance-equivalent
spending across {int(cost['councils'])} councils (per-council median ${f(cost['median'], 0)}). Exploratory only, see the caveat.

### In plain words

Counting roads out of town mostly works, and towns with several genuinely separate routes have not been
cut off. The problem is the towns in between: a handful have three or more roads out and were still
completely trapped, because one fire took the lot. About {tt['residents']:,} people live there, and nearly a third
of them are over 65. Most of the roads they would escape on belong to the State, not their council.

This is descriptive measurement: no causal claim and no claim about lives.

## Does having more exits mean less risk?

{table(buckets, bcols)}

Figure: `out/cutoff_rate_by_exits.png`.

## Who lives in the blind spot?

The pre-registered primary comparison (≥ 6 counted exits) is **{meta['verdict']}**: no NSW town is both
rated safe at that threshold and ever cut off. The rows below show every variant, including the
post-hoc unhalved count (DEVIATIONS U1). At the reported variant ({meta['report_variant']}), towns in the blind spot
had a median {f(res[(res.variant == meta['report_variant']) & (res.measure == 'pct_65_plus')].iloc[0].get('median_illusory'))}% of residents aged 65+, against
{f(res[(res.variant == meta['report_variant']) & (res.measure == 'pct_65_plus')].iloc[0].get('median_safe'))}% in towns rated safe and never cut off.

{table(res, rcols)}

Figure: `out/who_lives_in_blind_spot.png`. Illusory-redundancy towns by variant: {meta['illusory_towns_by_variant']}.
Groups at ≥ 6 counted exits: {g6}; at ≥ 3: {meta['groups_T3']}; unhalved at ≥ 3: {meta['groups_nohalve_T3']}.

## The towns

{table(ill, icols) if len(ill) else "No town met the illusory-redundancy definition at this threshold."}

## Who owns and funds the exits

{table(council.reset_index(drop=True), ccols) if len(council) else "No councils to report."}

Councils missing from the fiscal panel (not costed): {", ".join(meta['councils_missing_finance']) or "none"}.

## Caveats

- **The cost figure is exploratory.** It multiplies burned exit kilometres by what each council currently spends per kilometre of road. It is an annual maintenance-equivalent scale, **not** the cost of building a new road, and it carries no decision.
- Counted exits are our implementation of a published US method on Australian data. No US result is re-estimated here, and the paper's own figures are not reproduced.
- The "divide by two" step in that method is ambiguous for Australian roads; both the halved (pre-registered) and unhalved (post-hoc) counts are reported.
- The blind-spot group is small, so its social comparison is indicative, not conclusive.
- Cut-offs are inferred from fire maps (stage-2 caveats: upper bound, no timing).
- Road ownership is current and applied to a 2019 network. Edges more than 25 m from a categorised road are treated as local.
- The Census was taken in August 2021, after the 2019–20 fires.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, run at {meta['run_utc']}.
All inputs hash-verified. `aussef.duckdb` SHA-256 unchanged: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)
