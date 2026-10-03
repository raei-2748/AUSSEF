"""Experiment 18 figures (small, static PNG).
Run: uv run --no-project --with matplotlib --with pandas python full/figures.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

EXP = Path(__file__).resolve().parent.parent
RES, FIG = EXP / "results", EXP / "figures"
FIG.mkdir(exist_ok=True)
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.dpi": 200,
                     "axes.spines.top": False, "axes.spines.right": False})

# ---------- Figure 1: measured CI vs model slope, per channel ----------
chk = pd.read_csv(RES / "IL_CHECKS.csv")
chk = chk[chk["sample"] == "B"]
summ = json.loads((RES / "IL_SUMMARY.json").read_text())
labels = {"M1": "M1 Unemployment, council\n(pts per 10% residents near fire)",
          "M1b": "M1b Unemployment, SA2 (secondary)\n(pts per 10 pp homes inside)",
          "M2": "M2 Income, ATO postcode\n(% per 10 pp homes inside)",
          "M2b": "M2b Income, SA2 PIA (secondary)\n(% per 10 pp homes inside)",
          "M3": "M3 Accommodation & food\n(% per 10 pp homes inside)"}
fig, axes = plt.subplots(6, 1, figsize=(6.2, 7.2))
setting_style = [("unconstrained", "Model, default settings", C2, "o"),
                 ("constrained", "Model, held to measured limits", C1, "D"),
                 ("P_calibrated", "Model, held to pre-2019 limits only", C3, "s")]
for ax, k in zip(axes, ["M1", "M1b", "M2", "M2b", "M3"]):
    c = chk[chk.check == k]
    lo, hi = c.measured_lo.iloc[0], c.measured_hi.iloc[0]
    ax.axvspan(lo, hi, color=GRID, zorder=0)
    ax.plot([lo, hi], [0, 0], color=INK2, lw=2, solid_capstyle="butt")
    ax.axvline(0, color=INK2, lw=0.6, ls=":")
    xs = [lo, hi]
    for j, (s, lab, col, mk) in enumerate(setting_style):
        r = c[c.setting == s].iloc[0]
        y = 0.5 + 0.35 * j
        ax.plot(r.model_slope, y, mk, color=col, ms=6, mec=SURF, mew=1, label=lab)
        ax.annotate(r.verdict, (r.model_slope, y), xytext=(6, 0), textcoords="offset points", color=INK2, fontsize=6, va="center")
        xs.append(r.model_slope)
    pad = 0.12 * (max(xs) - min(xs))
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(-0.4, 1.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title(labels[k], fontsize=7.5, loc="left", color=INK)
    ax.text(hi, -0.3, " measured 95% CI", color=INK2, fontsize=6, va="center")
ax = axes[-1]
d_pick = summ["settings"]["constrained"]["d"]
ax.axvspan(18, 30, color=GRID)
ax.text(24, 0.0, "night lights dip\n(inside / 1 km), 18-30 months", ha="center", va="center", fontsize=6, color=INK2)
ax.plot(summ["settings"]["unconstrained"]["d"], 0.9, "o", color=C2, ms=6, mec=SURF)
ax.plot(d_pick, 0.9, "D", color=C1, ms=6, mec=SURF)
ax.set_xlim(0, 31)
ax.set_ylim(-0.6, 1.4)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.set_title("Disruption length d (months), model setting vs night lights", fontsize=7.5, loc="left", color=INK)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=3, frameon=False, fontsize=7, bbox_to_anchor=(0.5, 1.0))
fig.suptitle("Modelled indirect loss vs measured limits (Black Summer slopes; M1 all seasons). Model = partly assumed.",
             fontsize=8, y=0.965, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(FIG / "fig1_measured_vs_modelled_limits.png")
plt.close(fig)

# ---------- Figure 2: Black Summer who pays, plus modelled indirect loss ----------
acc = pd.read_csv(EXP.parent / "Experiment 17_cost_accounts/results/BLACK_SUMMER_ACCOUNT.csv").set_index("line")
payers = [("Insurers", acc.loc["loss_insurers", "mid"]),
          ("Commonwealth", acc.loc["loss_commonwealth_cleanup", "mid"] + acc.loc["rec_commonwealth", "mid"]),
          ("NSW Government", acc.loc["loss_nsw_cleanup", "mid"] + acc.loc["rec_nsw", "mid"]),
          ("Households (uninsured rebuild)", acc.loc["loss_households_uninsured", "mid"])]
tot = sum(v for _, v in payers)
bs = summ["totals"]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.0), gridspec_kw=dict(height_ratios=[1.1, 1]))
left = 0
for (n, v), col in zip(payers, [C1, C2, C3, C4]):
    a1.barh(0, v, left=left, color=col, height=0.5, edgecolor=SURF, linewidth=2)
    up = n in ("Insurers", "Commonwealth", "Households (uninsured rebuild)")
    a1.text(left + v / 2, 0.3 if up else -0.3, f"{n}\nA${v:,.0f}m ({v / tot:.0%})", ha="center",
            va="bottom" if up else "top", fontsize=6.5, color=INK)
    left += v
a1.set_xlim(0, tot * 1.02)
a1.set_ylim(-0.9, 1.0)
a1.set_yticks([])
a1.spines["left"].set_visible(False)
a1.set_title(f"Counted costs, Black Summer NSW (Exp 17 loss + recovery accounts, mid): A${tot / 1000:.2f}bn",
             fontsize=7.5, loc="left", color=INK)
items = [("Default settings", bs["unconstrained"]["black_summer"], C2),
         ("Held to measured limits", bs["constrained"]["black_summer"], C1)]
for j, (n, t, col) in enumerate(items):
    y = 1 - j
    a2.barh(y, t["output_loss_gross_Am"], color=col, height=0.35)
    a2.barh(y - 0.35, -t["offset_in_24m_Am"], color=INK2, height=0.25, alpha=0.5)
    a2.text(t["output_loss_gross_Am"] + 10, y, f"{n}: lost local output A${t['output_loss_gross_Am']:,.0f}m",
            va="center", fontsize=6.5, color=INK)
    a2.text(-t["offset_in_24m_Am"] - 10, y - 0.35, f"rebuild demand +A${t['offset_in_24m_Am']:,.0f}m", va="center",
            ha="right", fontsize=6, color=INK2)
a2.axvline(0, color=INK2, lw=0.6)
a2.set_xlim(-700, 1100)
a2.set_yticks([])
a2.spines["left"].set_visible(False)
a2.set_xlabel("A$m, first 24 months (output, not cost; not added to the bar above)")
n_rows = bs["constrained"]["black_summer"]["rows"]
a2.set_title(f"Modelled indirect loss to local businesses and workers (IO model, partly assumed; {n_rows} of 57 "
             "Black Summer rows)", fontsize=7.5, loc="left", color=INK)
fig.tight_layout()
fig.savefig(FIG / "fig2_black_summer_who_pays.png")
plt.close(fig)

# ---------- Figure 3: SHAP for Y_measured ----------
sh = pd.read_csv(RES / "SHAP_SUMMARY.csv")
oof = pd.read_csv(RES / "SHAP_OOF_Y_measured.csv")
nice = {"H": "H hazard", "E2": "E2 exposure (BFPL)", "V": "V vulnerability", "F": "F fiscal", "X23": "X23 underinsurance",
        "log_share": "share burned (log)", "peak_ffdi": "peak FFDI", "severity_high_extreme": "high/extreme severity",
        "log_homes_in_fire_per_1000": "homes inside fire (log)", "log_homes_within_1km_per_1000": "homes within 1 km (log)"}
s = sh[(sh.target == "Y_v4") & (sh.xset == "PRE+FIRE")].sort_values("mean_abs_shap")
fig, (b1, b2) = plt.subplots(1, 2, figsize=(7.8, 3.6), gridspec_kw=dict(width_ratios=[1.2, 1]))
for i, f in enumerate(s.feature):
    x = oof[f"x_{f}"].to_numpy()
    v = oof[f"shap_{f}"].to_numpy()
    q = pd.Series(x).rank(pct=True).to_numpy()
    jit = (np.random.default_rng(i).random(len(v)) - 0.5) * 0.5
    b1.scatter(v, i + jit, c=q, cmap="Blues", vmin=-0.2, vmax=1, s=6, linewidths=0)
b1.axvline(0, color=INK2, lw=0.6)
b1.set_yticks(range(len(s)))
b1.set_yticklabels([nice[f] for f in s.feature], fontsize=7)
b1.set_xlabel("SHAP value (effect on predicted Y_measured)\ndot shade: light = low feature value, dark = high")
b1.set_title("Y_measured, PRE+FIRE, out-of-fold SHAP", fontsize=7.5, loc="left", color=INK)
targets = ["Y_v4", "DL", "IL", "FP", "SL"]
order = list(s.feature)[::-1]
M = np.array([[sh[(sh.target == t) & (sh.xset == "PRE+FIRE") & (sh.feature == f)].share_of_total.iloc[0]
               for t in targets] for f in order])
b2.imshow(M, cmap="Blues", vmin=0, vmax=M.max(), aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        b2.text(j, i, f"{M[i, j]:.0%}", ha="center", va="center", fontsize=6,
                color="white" if M[i, j] > 0.6 * M.max() else INK)
met = pd.read_csv(RES / "MODEL_METRICS.csv")
rho = {t: met[(met.target == t) & (met.xset == "PRE+FIRE") & (met.cv == "season") & (met.model == "rf")].rho.iloc[0]
       for t in targets}
b2.set_xticks(range(len(targets)))
b2.set_xticklabels([f"{'Y' if t == 'Y_v4' else t}\n{rho[t]:+.2f}" for t in targets], fontsize=6.5)
b2.set_xlabel("target (RF rho, PRE+FIRE, season-out)", fontsize=6.5)
b2.set_yticks(range(len(order)))
b2.set_yticklabels([nice[f] for f in order], fontsize=6.5)
b2.set_title("Share of mean |SHAP| by target", fontsize=7.5, loc="left", color=INK)
for sp in b2.spines.values():
    sp.set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "fig3_shap_y_measured.png")
plt.close(fig)

# ---------- Figure 4: RF skill, measured vs hybrid ----------
rows = [("Y_measured (Y_v4)", "Y_v4", C1), ("  DL", "DL", C1), ("  IL measured", "IL", C1), ("  FP", "FP", C1),
        ("  SL", "SL", C1), ("Y_hybrid (partly assumed)", "Y_hybrid", C2), ("  IL_model (partly assumed)", "IL_model", C2)]
fig, ax = plt.subplots(figsize=(5.6, 3.0))
for i, (lab, t, col) in enumerate(rows):
    for k, (xs, mk, dy) in enumerate([("PRE", "o", -0.15), ("PRE+FIRE", "D", 0.15)]):
        r = met[(met.target == t) & (met.xset == xs) & (met.cv == "season") & (met.model == "rf")].iloc[0]
        y = len(rows) - 1 - i + dy
        ax.plot([r.rho_lo, r.rho_hi], [y, y], color=col, lw=2, alpha=0.5 if xs == "PRE" else 1)
        ax.plot(r.rho, y, mk, color=col, ms=5, mec=SURF, alpha=0.5 if xs == "PRE" else 1,
                label=xs if i == 0 else None)
ax.axvline(0, color=INK2, lw=0.6)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=7)
ax.set_xlabel("RF Spearman rho, leave-one-fire-season-out\n(95% council-bootstrap CI)")
ax.legend(frameon=False, fontsize=7, loc="lower right")
ax.set_title("How well X predicts each target (light = PRE only, dark = PRE+FIRE)", fontsize=7.5, loc="left")
fig.tight_layout()
fig.savefig(FIG / "fig4_rf_skill_measured_vs_hybrid.png")
plt.close(fig)
print("figures done")
