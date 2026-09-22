"""Stage-7 RESULTS.md and figure."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LABEL = {"pct_65_plus": "Residents aged 65+ (%)", "pct_no_car": "Dwellings with no car (%)",
         "pct_need_assistance": "Need assistance with core activities (%)",
         "median_hh_income_weekly": "Median household income ($/week)"}


def f(x, d=1):
    if x is None or pd.isna(x):
        return "missing"
    return f"{x:,.{d}f}"


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(str(fn(r)) for _, fn in cols) + " |" for _, r in df.iterrows())


def figure(town_csv):
    t = pd.read_csv(town_csv, dtype={"ucl_code": str})
    groups = ["cut off", "fire-touched, never cut off", "never touched"]
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.2))
    for ax, m in zip(axes, LABEL):
        data = [t.loc[t.group == g, m].dropna() for g in groups]
        ax.boxplot(data, showfliers=False)
        rng = np.random.default_rng(0)
        for i, d in enumerate(data, start=1):
            ax.scatter(i + rng.uniform(-0.12, 0.12, len(d)), d, s=8, alpha=0.5, color="#c0392b" if i == 1 else "#2c3e50")
        ax.set_xticks([1, 2, 3], ["cut off\n≥ once", "fire-touched,\nnever cut off", "never\ntouched"], fontsize=8)
        ax.set_title(LABEL[m], fontsize=9)
    fig.suptitle("Who lives in NSW towns that fires have fully cut off? (2021 Census)", fontsize=10)
    fig.savefig(OUT / "vulnerability_by_group.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(res, council, cut, meta):
    figure(OUT / "town_vulnerability.csv")
    p = res[res.verdict != ""].iloc[0]
    tt = meta["totals"]
    main = res[res.comparison == "all never-cut-off towns"]
    sec = res[res.comparison != "all never-cut-off towns"]
    rcols = [("Measure", lambda r: LABEL[r.measure]), ("Cut-off towns", lambda r: int(r.n_cut_off)),
             ("Comparison towns", lambda r: int(r.n_comparison)), ("Median cut-off", lambda r: f(r.median_cut_off)),
             ("Median comparison", lambda r: f(r.median_comparison)),
             ("Difference [95% CI]", lambda r: f"{f(r['diff'])} [{f(r.diff_lo)}, {f(r.diff_hi)}]"),
             ("p (Mann–Whitney)", lambda r: f(r.p_mwu, 3)),
             ("p (Holm)", lambda r: f(r.p_holm, 3) if pd.notna(r.get("p_holm")) else "—"),
             ("Verdict", lambda r: r.verdict or "")]
    ccols = [("Council", lambda r: r.council), ("Cut-off towns", lambda r: int(r.cut_off_towns)),
             ("Residents", lambda r: f"{int(r.residents):,}"), ("Aged 65+", lambda r: f"{int(r.aged_65_plus):,}"),
             ("Need assistance", lambda r: f"{int(r.need_assistance):,}"), ("Homes with no car", lambda r: f"{int(r.dwellings_no_car):,}"),
             ("Council own-source $ per resident", lambda r: f"${f(r.own_source_per_resident_aud, 0)}"),
             ("Own-source $ per 65+ resident in cut-off towns", lambda r: f"${f(r.own_source_per_65plus_in_cutoff_towns_aud, 0)}")]
    tcols = [("Town", lambda r: r.town), ("Residents", lambda r: f"{int(r.persons):,}" if pd.notna(r.persons) else "missing"),
             ("Aged 65+ %", lambda r: f(r.pct_65_plus)), ("No car %", lambda r: f(r.pct_no_car)),
             ("Need assistance %", lambda r: f(r.pct_need_assistance)), ("Median household income $/wk", lambda r: f(r.median_hh_income_weekly, 0)),
             ("Council", lambda r: r.LGA_NAME21)]
    if meta["verdict"] == "SUPPORTED":
        older = "older than"
    elif meta["verdict"] == "OPPOSITE":
        older = "younger than"
    else:
        older = (f"older at the median ({f(p.median_cut_off)}% vs {f(p.median_comparison)}% aged 65+), but the 95% range "
                 f"({p.diff_lo:.3f} to {p.diff_hi:.1f} points) just reaches zero, so by the rule set in advance this is "
                 f"not a clear difference from")
    text = f"""# Stage 7 results: who lives in towns that get fully cut off?

## Verdict (pre-registered)

**{meta['verdict']}.** The median share of residents aged 65+ is **{f(p.median_cut_off)}%** in the
{int(p.n_cut_off)} towns that fires have fully cut off, against **{f(p.median_comparison)}%** in the {int(p.n_comparison)} towns never cut off.
The difference is **{f(p['diff'])} percentage points** (95% CI {p.diff_lo:.3f} to {f(p.diff_hi)}; Mann–Whitney p = {f(p.p_mwu, 3)}).

### In plain words

- **{tt['residents']:,} people** live in the {tt['cut_off_towns']} towns where fire has cut every road out at least once.
- Among them are **{tt['aged_65_plus']:,} people aged 65 or over**, **{tt['need_assistance']:,} people who need help with everyday activities**, and **{tt['dwellings_no_car']:,} homes with no car**. These are the people who would find it hardest to get out.
- Cut-off towns are {older} other towns.

This is descriptive. It does not show that fires caused these patterns, and it says nothing about lives.

## Town comparison (2021 Census)

{table(main, rcols)}

The verdict uses only the share of residents aged 65+. The other rows are descriptive, with Holm-adjusted p-values.

Against towns touched by fire but never cut off:

{table(sec, rcols)}

## Councils: vulnerable residents in cut-off towns, and the council's own-source money (2018-19)

{table(council, ccols)}

"Own-source $" is council revenue raised from rates, fees and charges rather than grants
(`total_revenue_including_capital_aud` × `own_source_pct`). It is the council's whole budget of
its own money, not money set aside for evacuation roads. Councils missing from the fiscal panel:
{", ".join(meta['councils_missing_finance']) or "none"}.

## All cut-off towns

{table(cut.sort_values("persons", ascending=False), tcols)}

Figure: `out/vulnerability_by_group.png`.

## Caveats

- One fire can cut off several neighbouring towns, so the town-level intervals are optimistic.
- The Census was taken in August 2021, after the 2019–20 fires.
- Single-exit towns (outside the stage-2 sample) are not included, though they may be the most exposed.
- Cut-offs come from fire maps (stage 2), so they are upper bounds with no timing.
- Many exit roads are state roads; council money is only part of the picture.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, run at {meta['run_utc']}.
The inputs, LGA files and Census zip were hash-verified. `aussef.duckdb` SHA-256 was unchanged: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)
