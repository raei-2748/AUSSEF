"""Figure 4 (report): pre-2019 risk map vs Black Summer homes destroyed, plain journal style, white background.
Data as Experiment 7 make_maps.py fig_prospective (results/DAY2B_COUNCILS.csv); that folder is not touched.
Run: uv run --no-project --with geopandas --with shapely --with pyarrow --with matplotlib --with pandas python FINAL/make_map_fig4.py"""
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
WHITE, INK = "#ffffff", "#111111"
ORANGE = ["#fde4d8", "#f8b597", "#f08459", "#d4541f", "#9a3810"]
BLUE = ["#f4f4f4", "#9ec5f4", "#5598e7", "#256abf", "#0d366b"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "figure.facecolor": WHITE, "axes.facecolor": WHITE,
                     "savefig.facecolor": WHITE, "text.color": INK})
g = pd.read_parquet(ROOT / "fire_event_dataset/data/cache/lga2021_nsw_geom.parquet")
g["geometry"] = shapely.from_wkb(g.geometry)
g = gpd.GeoDataFrame(g, geometry="geometry", crs=4283).to_crs(3577)
g["region_id"] = g.region_id.astype(int).astype(str)
c = pd.read_csv(ROOT / "Experiment 7/results/DAY2B_COUNCILS.csv", dtype={"region_id": str})
g = g.merge(c, on="region_id", how="inner")
top = g.index_pre.rank(ascending=False) <= 20
qs = np.nanquantile(g.index_pre, np.linspace(0, 1, 6)); qs[0] -= 1e-9; qs[-1] += 1e-9

fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4))
fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.02, wspace=0.02)
ax = axes[0]
g.plot(column="index_pre", ax=ax, cmap=ListedColormap(ORANGE), norm=BoundaryNorm(qs, 5), edgecolor=WHITE, linewidth=0.25)
g[top].boundary.plot(ax=ax, color=INK, linewidth=0.7)
leg_a = [Patch(facecolor=col, label=l) for col, l in zip(ORANGE, ["lowest fifth", "", "", "", "highest fifth"])]
ax = axes[1]
cls = pd.cut(g.bs_per_1000, [-1, 0, 1, 5, 15, 100], labels=False)
g.plot(color=[BLUE[int(k)] for k in cls], ax=ax, edgecolor=WHITE, linewidth=0.25)
g[top].boundary.plot(ax=ax, color=INK, linewidth=0.7)
leg_b = [Patch(facecolor=col, edgecolor="#cccccc", linewidth=0.3, label=l) for col, l in zip(BLUE, ["0", "<1", "1-5", "5-15", "15+"])]
outline = Line2D([], [], color=INK, lw=0.9, label="top 20 risk councils")
for ax, letter, name, leg in ((axes[0], "a", "Risk index from pre-2019 data", leg_a + [outline]),
                              (axes[1], "b", "Homes destroyed per 1,000 dwellings, Black Summer", leg_b + [outline])):
    ax.set_axis_off()
    ax.text(0.0, 1.01, letter, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")
    ax.text(0.06, 1.01, name, transform=ax.transAxes, fontsize=8, va="bottom")
    ax.legend(handles=leg, loc="lower left", fontsize=6.5, frameon=False, handlelength=1.0, handleheight=0.8)
fig.savefig(ROOT / "FINAL/figures/fig4_prefire_map_black_summer.png", dpi=220, bbox_inches="tight", pad_inches=0.05)
print("ok")
