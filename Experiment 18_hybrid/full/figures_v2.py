"""Experiment 18 addendum B figures. v1 figures are left unchanged.
fig5: which measured data can check the IO model, and Black Summer lost sales (income-consistent range).
fig6: Black Summer who pays (Exp 17 counted costs) without the withdrawn v1 indirect-loss panel.
Run: python3 full/figures_v2.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

EXP = Path(__file__).resolve().parent.parent
RES, FIG = EXP / "results", EXP / "figures"
INK, INK2, GRID, SURF, MUTE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#b9b8b3"
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.dpi": 200,
                     "axes.spines.top": False, "axes.spines.right": False})
S = json.loads((RES / "v2_IL_SUMMARY.json").read_text())
D = S["default"]["descriptive_checks_not_valid_tests"]
IC = S["income_consistent"]

# ---------- fig5 ----------
rows = [("M2", "Income, postcode (ATO)", True, "% per 10 pp of homes inside"),
        ("M2b", "Income, small area (ABS)", True, "% per 10 pp of homes inside"),
        ("M1", "Unemployment rate, council", False, "firms keep staff through short dips; JobKeeper"),
        ("M3", "Accommodation & food business count", False, "counts businesses, not their sales")]
fig = plt.figure(figsize=(6.6, 4.6))
gs = fig.add_gridspec(len(rows) + 2, 1, height_ratios=[1] * len(rows) + [0.25, 1.5])
for j, (k, name, valid, why) in enumerate(rows):
    ax = fig.add_subplot(gs[j])
    lo, hi, sl = D[k]["measured_lo"], D[k]["measured_hi"], D[k]["slope"]
    col = C1 if valid else MUTE
    ax.axvspan(lo, hi, color=GRID if valid else "#efeeea", zorder=0)
    ax.plot([lo, hi], [0, 0], color=INK2 if valid else MUTE, lw=2, solid_capstyle="butt")
    ax.axvline(0, color=INK2, lw=0.6, ls=":")
    ax.plot(sl, 0.6, "o", color=C2 if valid else MUTE, ms=6, mec=SURF)
    xs = [lo, hi, sl, 0]
    pad = 0.15 * (max(xs) - min(xs))
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(-0.5, 1.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    tag = f"valid check, {why}" if valid else f"cannot check the model: {why}"
    ax.set_title(f"{name}  ({tag})", fontsize=7, loc="left", color=INK if valid else INK2)
    if j == 0:
        ax.text(lo, -0.3, "measured 95% CI ", fontsize=6, color=INK2, va="center", ha="right")
        ax.text(sl, 0.6, "  model, default settings", fontsize=6, color=C2, va="center")
ax = fig.add_subplot(gs[-1])
lo, p05, med, p95, hi = IC["min"], IC["p05"], IC["median"], IC["p95"], IC["max"]
ax.plot([lo, hi], [0, 0], color=MUTE, lw=1.2)
ax.plot([p05, p95], [0, 0], color=C1, lw=7, solid_capstyle="butt")
ax.plot(med, 0, "|", color=SURF, ms=12, mew=2)
dv = S["default"]["bs_gross_lost_trade_Am"]
ax.plot(dv, 0.35, "v", color=C2, ms=6)
ax.text(dv, 0.55, f"default settings A${dv:,.0f}m", fontsize=6.5, color=C2, ha="left")
ax.text(med, -0.45, f"middle A${med:,.0f}m", fontsize=6.5, color=INK, ha="center")
ax.text(p05, -0.45, f"A${p05:,.0f}m", fontsize=6.5, color=C1, ha="right")
ax.text(p95, -0.45, f"A${p95:,.0f}m", fontsize=6.5, color=C1, ha="center")
ax.set_ylim(-0.7, 0.8)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.set_xlabel("Black Summer lost sales, first 24 months, A$m (modelled; gross output, not in the payer accounts)")
ax.set_title(f"Lost sales over the {IC['n']} model settings that agree with both income checks "
             f"(bar: middle 90% of settings; line: all)", fontsize=7, loc="left")
fig.tight_layout()
fig.savefig(FIG / "fig5_lost_trade_fair_check.png")
plt.close(fig)

# ---------- fig6 ----------
# Exp 17 keeps two accounts: losses, and government recovery money. They are NOT added (some recovery money goes back
# to the same households, so adding would count a transfer as a cost).
acc = pd.read_csv(EXP.parent / "Experiment 17_cost_accounts/results/BLACK_SUMMER_ACCOUNT.csv").set_index("line")
blocks = [("Losses (who carried them)", [("Insurers", "loss_insurers", C1), ("Households (uninsured rebuild)", "loss_households_uninsured", C4),
                                         ("Governments (clean-up, 50:50)", ("loss_commonwealth_cleanup", "loss_nsw_cleanup"), C3)]),
          ("Recovery money (paid after)", [("Commonwealth", "rec_commonwealth", C2), ("NSW Government", "rec_nsw", C3)])]
tot_loss = acc.loc["loss_account", "mid"]
fig, axes = plt.subplots(2, 1, figsize=(6.6, 3.0), sharex=True)
for ax, (title, parts) in zip(axes, blocks):
    val = lambda k: sum(acc.loc[x, "mid"] for x in k) if isinstance(k, tuple) else acc.loc[k, "mid"]
    tot = sum(val(k) for _, k, _ in parts)
    left = 0
    for j, (n, k, col) in enumerate(parts):
        v = val(k)
        ax.barh(0, v, left=left, color=col, height=0.5, edgecolor=SURF, linewidth=2)
        up = j % 2 == 0
        ax.text(left + v / 2, 0.32 if up else -0.32, f"{n}\nA${v:,.0f}m ({v / tot:.0%})", ha="center",
                va="bottom" if up else "top", fontsize=6.2, color=INK)
        left += v
    ax.set_ylim(-1.2, 1.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title(f"{title}: A${tot / 1000:,.2f}bn", fontsize=7.5, loc="left")
axes[0].set_xlim(0, tot_loss * 1.02)
axes[1].set_xlabel("A$m, Black Summer (NSW), mid estimates (Experiment 17).\nThe two accounts are not added: some recovery "
                   "money goes back to the same households.", fontsize=6.5)
fig.tight_layout()
fig.savefig(FIG / "fig6_black_summer_who_pays.png")
print("ok", tot_loss)
