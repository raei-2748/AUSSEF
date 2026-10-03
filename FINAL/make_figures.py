"""Report figures for FINAL/figures. Figures 3, 4, 5 and 7 are copies of experiment figures (source folders are not
touched). Figures 0 (graphical abstract), 1 (who pays), 2 (council money clock) and 6 (lost sales check) are drawn
here from the experiments' result files, following the dataviz rules: palette validated (slots 1-4, light surface),
colour follows the entity, text in ink colours, thin marks with surface gaps, selective direct labels.
Run: python3 FINAL/make_figures.py"""
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "FINAL/figures"
OUT.mkdir(parents=True, exist_ok=True)
COPIES = {
    "fig5_shap_drivers.png": "Experiment 18_hybrid/figures/fig3_shap_y_measured.png",
    "fig7_night_lights_south_coast.png": "Experiment 15_nightlights/figures/curves_south_coast.png",
}
for dst, src in COPIES.items():
    shutil.copy2(ROOT / src, OUT / dst)

# reference palette (dataviz palette.md, light mode); validated: slots 1-4 pass adjacent CVD and normal-vision gates
SURF, INK, INK2, MUTED, GRIDC = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
GREYMARK = "#c9c8c3"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": GRIDC, "axes.linewidth": 0.8,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.dpi": 220, "savefig.facecolor": SURF,
                     "axes.spines.top": False, "axes.spines.right": False, "xtick.major.size": 0,
                     "ytick.major.size": 0, "text.parse_math": False})
GAP = 2.0  # surface gap between touching fills (pt)


def hairline_grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRIDC, linewidth=0.6, linestyle="-")
    ax.set_axisbelow(True)


def title(fig, main, sub=None, y=0.97):
    fig.text(0.02, y, main, fontsize=10, fontweight="bold", color=INK, va="top")
    if sub:
        fig.text(0.02, y - 0.075, sub, fontsize=7.5, color=INK2, va="top")


# ------------------------------------------------------------------ Figure 1: who pays (Exp 17)
acc = pd.read_csv(ROOT / "Experiment 17_cost_accounts/results/BLACK_SUMMER_ACCOUNT.csv").set_index("line")["mid"]
ENT = {"Insurers": BLUE, "Commonwealth": ORANGE, "NSW Government": AQUA, "Households": YELLOW}
rows = [("Losses\n(who carried them)", [("Insurers", acc.loss_insurers), ("Commonwealth", acc.loss_commonwealth_cleanup),
                                         ("NSW Government", acc.loss_nsw_cleanup), ("Households", acc.loss_households_uninsured)]),
        ("Recovery money\n(paid afterwards)", [("Commonwealth", acc.rec_commonwealth), ("NSW Government", acc.rec_nsw)])]
fig, ax = plt.subplots(figsize=(7.0, 3.0))
fig.subplots_adjust(left=0.17, right=0.9, top=0.66, bottom=0.2)
for yi, (lab, parts) in enumerate(rows):
    y = 1 - yi
    left, tot = 0.0, sum(v for _, v in parts)
    for name, v in parts:
        ax.barh(y, v, left=left, height=0.42, color=ENT[name], edgecolor=SURF, linewidth=GAP)
        left += v
    ax.text(tot + 25, y, f"A${tot / 1000:.2f}bn", va="center", fontsize=8.5, fontweight="bold", color=INK)
# selective labels: big segments get value + share; the two clean-up halves share one label
L = dict(rows[0][1]); R = dict(rows[1][1]); tl, tr = sum(L.values()), sum(R.values())
ax.text(L["Insurers"] / 2, 1.30, f"Insurers  A${L['Insurers']:,.0f}m ({L['Insurers'] / tl:.0%})", ha="center", fontsize=7.5)
cu = L["Commonwealth"] + L["NSW Government"]
ax.annotate(f"Clean-up, half each\nA${cu:,.0f}m ({cu / tl:.0%})", xy=(L["Insurers"] + cu / 2, 0.79),
            xytext=(L["Insurers"] + cu / 2, 0.47), ha="center", va="top", fontsize=7.5,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
hx = L["Insurers"] + cu + L["Households"] / 2
ax.text(hx, 1.30, f"Households\nA${L['Households']:,.0f}m ({L['Households'] / tl:.0%})", ha="center", fontsize=7.5)
ax.text(R["Commonwealth"] / 2, -0.30, f"Commonwealth\nA${R['Commonwealth']:,.0f}m ({R['Commonwealth'] / tr:.0%})",
        ha="center", va="top", fontsize=7.5)
ax.text(R["Commonwealth"] + R["NSW Government"] / 2, -0.30,
        f"NSW Government\nA${R['NSW Government']:,.0f}m ({R['NSW Government'] / tr:.0%})", ha="center", va="top", fontsize=7.5)
ax.set_yticks([1, 0], [r[0] for r in rows], fontsize=8, color=INK)
ax.set_ylim(-0.75, 1.65)
ax.set_xlim(0, tl * 1.0)
ax.set_xlabel("A$ million, middle estimates")
hairline_grid(ax)
ax.spines["left"].set_visible(False)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in ENT.values()]
fig.legend(handles, list(ENT), loc="upper left", bbox_to_anchor=(0.17, 0.80), ncol=4, frameon=False, fontsize=7.5,
           handlelength=1.0, handleheight=0.8, columnspacing=1.4)
title(fig, "Insurers carried most of Black Summer's counted loss",
      "NSW, 2019-20. The two accounts are not added: recovery money shows who spent money afterwards,\n"
      "and part of it went to the same households.")
fig.savefig(OUT / "fig1_who_pays.png")
plt.close(fig)

# ------------------------------------------------------------------ Figure 2: council money clock (Exp 11)
# Journal style: no title inside the image (the caption carries it), panel letters, error bars, one colour.
c = pd.read_csv(ROOT / "Experiment 11/results/CLOCK.csv")
c = c[(c["sample"] == "all") & (c.dose == "homes_in_fire")]
panels = [("C4_grants_pc", "a", "Council grants per resident", "H1"),
          ("C5_fire_grant_share", "b", "Fire-related grant lines", "H1")]
fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.6), sharey=True)
fig.subplots_adjust(left=0.1, right=0.98, top=0.86, bottom=0.17, wspace=0.08)
for ax, (ch, letter, name, locked) in zip(axes, panels):
    d = c[c.channel == ch].set_index("horizon").loc[["H0", "H1", "H2", "H3"]]
    x = [0, 1, 2, 3]
    ax.axhline(0, color=MUTED, lw=0.7)
    ax.errorbar(x, d.rho, yerr=[d.rho - d.lo, d.hi - d.rho], fmt="none", ecolor=BLUE, elinewidth=1, capsize=2.5)
    ax.plot(x, d.rho, "-", color=BLUE, lw=1)
    for xi, h in zip(x, d.index):
        filled = h != locked
        ax.plot(xi, d.loc[h, "rho"], "o", ms=5, mfc=BLUE if filled else SURF, mec=BLUE, mew=1.2, zorder=3)
    ax.set_xticks(x, ["0", "1", "2", "3"])
    ax.set_xlabel("Years after the fire")
    ax.set_xlim(-0.4, 3.4)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color(INK2)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(length=3, color=INK2)
    ax.text(-0.02, 1.04, letter, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom", ha="left")
    ax.text(0.06, 1.04, name, transform=ax.transAxes, fontsize=8, va="bottom", ha="left")
axes[0].set_ylabel("Spearman \u03c1 with fire size")
axes[0].set_ylim(-0.1, 0.8)
axes[1].plot([], [], "o", ms=5, mfc=SURF, mec=BLUE, mew=1.2, label="test fixed in advance")
axes[1].legend(loc="lower right", frameon=False, fontsize=7, handletextpad=0.3)
fig.savefig(OUT / "fig2_council_money_clock.png")
plt.close(fig)

# ------------------------------------------------------------------ Figure 6: lost sales fair check (Exp 18 v2)
S = json.loads((ROOT / "Experiment 18_hybrid/results/v2_IL_SUMMARY.json").read_text())
D, IC = S["default"]["descriptive_checks_not_valid_tests"], S["income_consistent"]
checks = [("M2", "Income, postcode (ATO)", True, "% per 10 pp of homes inside"),
          ("M2b", "Income, small area (ABS)", True, "% per 10 pp of homes inside"),
          ("M1", "Unemployment rate, council", False, "firms keep staff through short dips"),
          ("M3", "Accommodation and food business count", False, "counts businesses, not their sales")]
fig = plt.figure(figsize=(7.0, 5.0))
gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 0.35, 1.5], width_ratios=[1, 1], hspace=1.25, wspace=0.08,
                      left=0.03, right=0.97, top=0.80, bottom=0.10)
for j, (k, name, valid, why) in enumerate(checks):
    ax = fig.add_subplot(gs[j // 2, j % 2])
    lo, hi, sl = D[k]["measured_lo"], D[k]["measured_hi"], D[k]["slope"]
    ax.barh(0, hi - lo, left=lo, height=0.5, color=GRIDC if valid else "#efeeea", edgecolor=SURF, lw=0)
    ax.plot(sl, 0, "o", ms=7, color=ORANGE if valid else GREYMARK, mec=SURF, mew=1.5, zorder=3)
    ax.axvline(0, color=INK2, lw=0.8)
    xs = [lo, hi, sl, 0]
    pad = 0.18 * (max(xs) - min(xs))
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(-0.6, 0.6)
    ax.set_yticks([])
    for s in ("left",):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=7)
    ax.text(0, 1.30, name, transform=ax.transAxes, fontsize=8, color=INK if valid else INK2, va="bottom",
            fontweight="bold" if valid else "normal")
    ax.text(0, 1.06, "valid check" if valid else f"cannot test the model: {why}", transform=ax.transAxes,
            fontsize=6.8, color=INK2, va="bottom")
ax = fig.add_subplot(gs[2, :])
ax.axis("off")
ax.plot([0.04], [0.55], "o", ms=7, color=ORANGE, mec=SURF, mew=1.5, transform=ax.transAxes)
ax.text(0.06, 0.55, "model, default settings", transform=ax.transAxes, va="center", fontsize=7.5, color=INK)
ax.add_patch(plt.Rectangle((0.30, 0.47), 0.04, 0.16, color=GRIDC, transform=ax.transAxes))
ax.text(0.355, 0.55, "measured 95% interval", transform=ax.transAxes, va="center", fontsize=7.5, color=INK)
ax.text(0.62, 0.55, "Units differ between panels.", transform=ax.transAxes, va="center", fontsize=7.5, color=INK2)
ax = fig.add_subplot(gs[3, :])
ax.plot([IC["min"], IC["max"]], [0, 0], color=MUTED, lw=1.2, solid_capstyle="round")
ax.barh(0, IC["p95"] - IC["p05"], left=IC["p05"], height=0.34, color=BLUE, edgecolor=SURF, lw=0)
ax.plot([IC["median"]] * 2, [-0.17, 0.17], color=SURF, lw=2)
dv = S["default"]["bs_gross_lost_trade_Am"]
ax.plot(dv, 0, "o", ms=7, color=ORANGE, mec=SURF, mew=1.5, zorder=3)
ax.annotate(f"default A${dv:,.0f}m", (dv, 0), xytext=(0, 13), textcoords="offset points", ha="center",
            fontsize=7.5, color=INK)
ax.annotate(f"middle A${IC['median']:,.0f}m", (IC["median"], 0.17), xytext=(4, 6), textcoords="offset points",
            ha="left", va="bottom", fontsize=7.5, color=INK)
ax.text(IC["p05"], -0.30, f"A${IC['p05']:,.0f}m", ha="right", va="top", fontsize=7.5, color=INK)
ax.text(IC["p95"], -0.30, f"A${IC['p95']:,.0f}m", ha="center", va="top", fontsize=7.5, color=INK)
ax.set_ylim(-0.7, 0.8)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
hairline_grid(ax)
ax.set_xlabel("Black Summer lost sales, first 24 months, A$ million (modelled gross output; not in the payer accounts)")
ax.text(0, 1.20, f"Lost sales over the {IC['n']} of 1,620 model settings that agree with both income checks",
        transform=ax.transAxes, fontsize=8, fontweight="bold", color=INK, va="bottom")
ax.text(0, 1.05, "Bar: middle 90% of settings (a spread over assumptions, not a confidence interval). Line: all settings.",
        transform=ax.transAxes, fontsize=6.8, color=INK2, va="bottom")
title(fig, "Checked fairly, the economic model agrees with measured income",
      "Black Summer, effect per 10 percentage points of homes inside the fire, years 1-2.", y=0.985)
fig.savefig(OUT / "fig6_lost_sales_fair_check.png")
plt.close(fig)

# ------------------------------------------------------------------ Figure 0: graphical abstract
fig = plt.figure(figsize=(7.4, 3.3))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 45)
ax.axis("off")


def box(x, y, w, h, head, body, accent):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc="#f3f2ee", ec="none"))
    ax.add_patch(plt.Rectangle((x, y + h - 0.9), w, 0.9, color=accent, lw=0))
    ax.text(x + 1.6, y + h - 3.2, head, fontsize=8, fontweight="bold", va="top", color=INK)
    ax.text(x + 1.6, y + h - 6.4, body, fontsize=7, va="top", color=INK2, linespacing=1.45)


ax.text(2, 43, "Where does a bushfire's cost go, and can we see it coming?", fontsize=10.5, fontweight="bold",
        va="top", color=INK)
box(2, 2, 24, 36, "Data",
    "218 council-fire rows\n69 NSW councils, 96 fires\n2014-2024\n\nFire outlines x Census\nhomes = homes inside\nthe fire\n\n"
    "Every value sourced;\ntests locked before\nrunning", GRIDC)
box(32, 27, 66, 11, "1  Who pays (receipts)",
    f"Black Summer losses A${acc.loss_account / 1000:.2f}bn: insurers 77%, households 12%, governments 11%.\n"
    "Council grants keep rising for 3 years after a fire.", BLUE)
box(32, 14.5, 66, 11, "2  Seeing it coming (random forest + SHAP)",
    "Pre-2019 map picked the councils that lost homes (AUC 0.91).\nHomes lost ranked on unseen fire seasons, ρ +0.73.",
    ORANGE)
box(32, 2, 66, 11, "3  Lost sales (model, checked against measured income)",
    f"Black Summer lost sales A${IC['p05'] / 1000:.1f}bn to A${IC['p95'] / 1000:.1f}bn in the first two years\n"
    "(not in the payers' bill above).", AQUA)
for yy in (32.5, 20, 7.5):
    ax.add_patch(FancyArrowPatch((26.6, 20), (31.4, yy), arrowstyle="-|>", mutation_scale=8, color=MUTED, lw=0.9,
                                 connectionstyle="arc3,rad=0"))
fig.savefig(OUT / "fig0_graphical_abstract.png")
plt.close(fig)
print("ok", sorted(p.name for p in OUT.iterdir()))
