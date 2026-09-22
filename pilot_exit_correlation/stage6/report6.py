"""Stage-6 RESULTS.md and figure."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
LABEL = {"own_source_pct": "Own-source revenue share (%)", "cash_cover_months": "Cash cover (months)",
         "operating_ratio_pct": "Operating ratio (%)", "grants_pct": "Grant dependence (% of revenue)",
         "maintenance_ratio_pct": "Maintenance funded (% of required)", "road_km_per_1000": "Road km per 1,000 residents"}
GROUPS = ["exposed", "fire-touched, never cut off", "other"]


def f(x, d=1):
    if x is None or pd.isna(x):
        return "missing"
    return f"{x:,.{d}f}"


def table(df, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols)
    return head + "\n" + "\n".join("| " + " | ".join(str(fn(r)) for _, fn in cols) + " |" for _, r in df.iterrows())


def figure(council):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, m in zip(axes, ["own_source_pct", "grants_pct", "maintenance_ratio_pct"]):
        data = [council.loc[council.group == g, m].dropna() for g in GROUPS]
        ax.boxplot(data, showfliers=False)
        rng = np.random.default_rng(0)
        for i, d in enumerate(data, start=1):
            ax.scatter(i + rng.uniform(-0.12, 0.12, len(d)), d, s=12, alpha=0.7,
                       color="#c0392b" if i == 1 else "#2c3e50")
        ax.set_xticks([1, 2, 3], ["cut off\n≥ once", "fire-touched,\nnever cut off", "other"], fontsize=8)
        ax.set_title(LABEL[m], fontsize=9)
    fig.suptitle("NSW council finances in 2018-19, by whether their towns were ever fully cut off by fire", fontsize=10)
    fig.savefig(OUT / "council_finance_by_group.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(res, sens, council, meta):
    figure(council)
    p = res[res.measure == "own_source_pct"].iloc[0]
    rcols = [("Measure", lambda r: LABEL[r.measure]), ("Exposed councils", lambda r: int(r.n_exposed)),
             ("Other councils", lambda r: int(r.n_comparison)), ("Median exposed", lambda r: f(r.median_exposed)),
             ("Median other", lambda r: f(r.median_comparison)),
             ("Difference [95% CI]", lambda r: f"{f(r['diff'])} [{f(r.diff_lo)}, {f(r.diff_hi)}]"),
             ("p (Mann–Whitney)", lambda r: f(r.p_mwu, 3)),
             ("p (Holm)", lambda r: f(r.p_holm, 3) if "p_holm" in r and pd.notna(r.p_holm) else "(primary)"),
             ("Verdict", lambda r: r.verdict or "")]
    scols = [("Comparison", lambda r: r.comparison), ("Baseline", lambda r: r.baseline),
             ("n exposed / other", lambda r: f"{int(r.n_exposed)} / {int(r.n_comparison)}"),
             ("Median exposed", lambda r: f(r.median_exposed)), ("Median other", lambda r: f(r.median_comparison)),
             ("Difference [95% CI]", lambda r: f"{f(r['diff'])} [{f(r.diff_lo)}, {f(r.diff_hi)}]"),
             ("p", lambda r: f(r.p_mwu, 3))]
    ex = council[council.group == "exposed"].sort_values("own_source_pct")
    ecols = [("Council", lambda r: r.lga_name), ("Towns cut off", lambda r: int(r.towns_cut_off)),
             ("Residents in cut-off towns", lambda r: f"{int(r.residents_in_cut_off_towns):,}"),
             ("Own-source %", lambda r: f(r.own_source_pct)), ("Grants %", lambda r: f(r.grants_pct)),
             ("Cash cover (months)", lambda r: f(r.cash_cover_months)),
             ("Maintenance funded %", lambda r: f(r.maintenance_ratio_pct))]
    direction = "lower" if p["diff"] < 0 else "higher"
    if p.diff_hi < 0:
        interp = "The whole interval is below zero, so this is a clear mismatch: less own revenue where the cut-off risk is."
    elif p.diff_lo > 0:
        interp = ("The whole interval is above zero, so the pattern is the **opposite** of a mismatch: councils with "
                  "cut-off towns have *more* of their own revenue, not less.")
    else:
        interp = "The interval includes zero, so the data show no clear difference on this measure."
    text = f"""# Stage 6 results: cut-off risk versus council finances

## Verdict (pre-registered)

**{meta['verdict']}.** Councils with at least one town that fires have fully cut off
({int(p.n_exposed)} councils) raise a median **{f(p.median_exposed)}%** of their revenue from their own sources.
Other councils ({int(p.n_comparison)}) raise **{f(p.median_comparison)}%**. The difference is **{f(p['diff'])} percentage points**
(95% CI {f(p.diff_lo)} to {f(p.diff_hi)}; Mann–Whitney p = {f(p.p_mwu, 3)}). A mismatch needed a difference below 0
with the whole interval below 0.

### In plain words

We checked whether the councils whose towns get completely cut off by fire are also the councils
with the least money of their own. Their own-source revenue share was {direction} than other councils',
by {f(abs(p['diff']))} percentage points. {interp}

This compares councils. It does not show that fires caused their finances, or the reverse, and it says nothing about lives.

## All measures (2018-19, exposed vs all other councils)

{table(res, rcols)}

Only own-source revenue share decides the verdict. The other measures are descriptive, with p-values adjusted for multiple comparisons (Holm).

## Sensitivity checks (no verdict)

{table(sens, scols)}

Spearman rank correlation between the share of a council's residents living in cut-off towns and
its own-source revenue share, across all matched councils: ρ = {f(meta['spearman_rho_exposed_share_vs_own_source'], 2)}
(permutation p = {f(meta['spearman_perm_p'], 3)}).

## Exposed councils

{table(ex, ecols)}

## Coverage

- Towns: {meta['towns']}, of which {meta['cut_off_towns_total']} were cut off at least once (1950–2023).
- Councils containing these towns: {meta['councils_with_towns']}. Matched to the fiscal panel: {meta['councils_matched']}.
- Groups: {meta['exposed_councils']} exposed, {meta['fire_touched_councils']} fire-touched but never cut off, {meta['other_councils']} other.
- Cut-off towns in matched councils: {meta['cut_off_towns_in_matched_councils']} of {meta['cut_off_towns_total']}.
- Councils not in the fiscal panel (not compared): {", ".join(meta['councils_unmatched']) or "none"}.
  Most were created by the 2016 amalgamations, which the cleaned extended panel leaves out.
  "Nambucca Valley" appears in the panel as "Nambucca" and was not matched under the exact-name rule.
- **Post-hoc coverage check** (see DEVIATIONS.md): `master.fiscal_panel_legacy` covers these councils.
  With it, {meta['legacy_councils_matched']} councils are compared, {meta['legacy_exposed']} of them exposed and containing
  {meta['legacy_cut_off_towns']} cut-off towns (see the sensitivity table).
  Still unmatched: {", ".join(meta['legacy_unmatched']) or "none"}.

Figure: `out/council_finance_by_group.png`.

## Caveats

- This is descriptive only. Fire risk and council finances share causes, such as remoteness, forest cover and small rate bases.
- Exposed councils are few, so the intervals are wide.
- Cut-offs come from fire maps (stage 2), so they are upper bounds with no timing.
- Councils use fixed 2021 boundaries; only councils in the fiscal panel are compared.

## Run

Seed {meta['seed']}, {meta['bootstrap']} bootstrap resamples, run at {meta['run_utc']}.
The inputs and the LGA boundary files were hash-verified.
`aussef.duckdb` SHA-256 was unchanged: `{meta['aussef_duckdb_sha256']}`.
"""
    (HERE / "RESULTS.md").write_text(text)
