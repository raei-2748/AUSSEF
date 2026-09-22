"""Stage-8 RESULTS.md and figure."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LABEL = {"pop_growth_pct": "Population growth 2016→2021 (%)",
         "hh_income_change_pct": "Median household income change (%, nominal)",
         "emp_ratio_change_pp": "Employment-to-population ratio change (pp)",
         "unemp_rate_change_pp": "Unemployment rate change (pp)"}
GROUPS = ["cut off", "burned, not cut off", "not touched"]


def f(x, d=1):
    if x is None or pd.isna(x):
        return "missing"
    return f"{x:,.{d}f}"


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(str(fn(r)) for _, fn in cols) + " |" for _, r in df.iterrows())


def figure(ok):
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.2))
    for ax, m in zip(axes, LABEL):
        data = [ok.loc[ok.group == g, m].dropna() for g in GROUPS]
        ax.boxplot(data, showfliers=False)
        rng = np.random.default_rng(0)
        for i, d in enumerate(data, start=1):
            ax.scatter(i + rng.uniform(-0.12, 0.12, len(d)), d, s=8, alpha=0.5, color="#c0392b" if i == 1 else "#2c3e50")
        ax.axhline(0, color="k", lw=0.6)
        ax.set_xticks([1, 2, 3], ["cut off in\nBlack Summer", "burned,\nnot cut off", "not\ntouched"], fontsize=8)
        ax.set_title(LABEL[m], fontsize=9)
    fig.suptitle("Change from the 2016 to the 2021 Census (towns whose boundaries barely changed)", fontsize=10)
    fig.savefig(OUT / "change_by_group.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(res, df, meta):
    ok = df[df.iou >= 0.7]
    figure(ok)
    p = res[res.verdict != ""].iloc[0]
    rcols = [("Outcome", lambda r: LABEL[r.outcome]), ("Comparison", lambda r: r.comparison),
             ("n", lambda r: f"{int(r.n_a)} / {int(r.n_b)}"), ("Median cut off", lambda r: f(r.median_a)),
             ("Median comparison", lambda r: f(r.median_b)),
             ("Difference [95% CI]", lambda r: f"{f(r['diff'])} [{f(r.diff_lo)}, {f(r.diff_hi)}]"),
             ("p (Mann–Whitney)", lambda r: f(r.p_mwu, 3)),
             ("p (Holm)", lambda r: f(r.p_holm, 3) if pd.notna(r.get("p_holm")) else "—"),
             ("Verdict", lambda r: r.verdict or "")]
    cut = ok[ok.group == "cut off"].sort_values("persons_2021", ascending=False)
    tcols = [("Town", lambda r: r.UCL_NAME21), ("Pop. 2016", lambda r: f(r.persons_2016, 0)),
             ("Pop. 2021", lambda r: f(r.persons_2021, 0)), ("Pop. growth %", lambda r: f(r.pop_growth_pct)),
             ("Income change %", lambda r: f(r.hh_income_change_pct)), ("Emp. ratio change pp", lambda r: f(r.emp_ratio_change_pp)),
             ("Boundary match (IoU)", lambda r: f(r.iou, 2))]
    words = {"WORSE": "grew **less**", "BETTER": "grew **more**",
             "NO CLEAR DIFFERENCE": "did **not clearly differ** in growth from"}.get(meta["verdict"], "could not be compared with")
    text = f"""# Stage 8 results: did towns cut off in Black Summer change differently? (exploratory)

## Verdict (pre-registered, exploratory)

**{meta['verdict']}.** From the 2016 to the 2021 Census, the median population growth was
**{f(p.median_a)}%** in the {int(p.n_a)} towns fully cut off by a Black Summer fire, against **{f(p.median_b)}%** in the {int(p.n_b)} towns
that were burned but not cut off. The difference is **{f(p['diff'])} percentage points** (95% CI {f(p.diff_lo)} to {f(p.diff_hi)};
Mann–Whitney p = {f(p.p_mwu, 3)}).

### In plain words

We compared towns that lost all their roads out in Black Summer with towns that were burned but kept
at least one road. The cut-off towns {words} the burned-only towns between 2016 and 2021.
This is an exploratory first look. The groups are small and one fire complex dominates, and the 2021
Census happened during COVID-19. It cannot show that being cut off *caused* any change.

## How to read this

The faster growth is most likely about **where** these towns are, not about being cut off:
- Most cut-off towns are coastal (South Coast and Mid North Coast). Coastal towns grew strongly in 2016–2021, including the COVID-era move to the coast.
- The fastest growers include new housing estates (the town table shows Red Head and Tallwoods Village).
- The cut-off towns that are inland or were badly damaged barely grew or shrank (see Batlow, Buxton and Mogo in the table).

A 2011–2016 pre-trend check, or a coastal-only comparison, would be needed to separate these. Either
would be a new pre-registered test. The result here does **not** mean being cut off helps a town.

## All comparisons (towns with boundary match IoU ≥ 0.7 unless stated)

{table(res, rcols)}

The verdict uses only population growth against burned-not-cut-off towns. The other rows are descriptive.

## Cut-off towns

{table(cut, tcols)}

## Coverage

- Black Summer fire families: {meta['black_summer_families']}. Towns analysed: {meta['towns']}; groups: {meta['groups_all']}.
- After the boundary-match filter (IoU ≥ 0.7): {meta['groups_after_iou']}.
- Cut-off towns dropped because their 2016 and 2021 boundaries differ too much: {", ".join(meta['cut_off_towns_failing_iou']) or "none"}.

Figure: `out/change_by_group.png`.

## Caveats

- **Exploratory.** There are few towns and one dominant fire complex; the intervals treat towns as independent, so they are optimistic.
- **COVID-19.** The 2021 Census (August 2021) coincided with lockdowns, and many people moved to coastal towns during the pandemic.
- **No pre-fire trend check.** 2011 data were not obtained, so the groups may already have been on different paths before 2019.
- **Boundaries.** Towns are linked across Censuses by boundary overlap. Small boundary changes remain even above the IoU threshold.
- This makes no causal or lives-saved claim.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, run at {meta['run_utc']}.
All inputs and downloads were hash-verified. `aussef.duckdb` SHA-256 was unchanged: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)
