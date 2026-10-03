"""Figure 6 (report, simple version): Black Summer lost sales range, plain journal style, white background.
Run: python3 FINAL/make_fig6_simple.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "Experiment 18_hybrid/results/v2_IL_SUMMARY.json").read_text())
IC = S["income_consistent"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white", "text.parse_math": False})
BLUE, INK, GREY = "#2a78d6", "#111111", "#8a8984"
fig, ax = plt.subplots(figsize=(6.0, 1.5))
fig.subplots_adjust(left=0.03, right=0.97, top=0.82, bottom=0.32)
ax.plot([IC["min"] / 1000, IC["max"] / 1000], [0, 0], color=GREY, lw=1, zorder=0)
ax.barh(0, (IC["p95"] - IC["p05"]) / 1000, left=IC["p05"] / 1000, height=0.35, color=BLUE)
ax.plot([IC["median"] / 1000] * 2, [-0.17, 0.17], color="white", lw=2)
ax.text(IC["median"] / 1000, 0.3, f"middle estimate A${IC['median'] / 1000:.1f}bn", ha="center", fontsize=8)
ax.text(IC["p05"] / 1000, -0.32, f"A${IC['p05'] / 1000:.1f}bn", ha="center", va="top", fontsize=7.5)
ax.text(IC["p95"] / 1000, -0.32, f"A${IC['p95'] / 1000:.1f}bn", ha="center", va="top", fontsize=7.5)
ax.set_ylim(-0.75, 0.75)
ax.set_yticks([])
for s in ("left", "right", "top"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GREY)
ax.tick_params(axis="x", length=3, color=GREY)
ax.set_xlabel("Black Summer lost business sales, first two years (A$ billion, modelled)")
fig.savefig(ROOT / "FINAL/figures/fig6_lost_sales_simple.png", dpi=220)
print("ok")
