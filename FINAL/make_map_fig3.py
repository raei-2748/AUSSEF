"""Figure 3 (report): Black Summer map, plain journal style, white background. Data as Experiment 11
make_report_figures.py (fig2); that experiment folder is not touched.
Run: uv run --no-project --with geopandas --with shapely --with pyarrow --with matplotlib --with pandas python FINAL/make_map_fig3.py"""
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
WHITE, INK, INK2, NODATA = "#ffffff", "#111111", "#555555", "#ececec"
BLUE = ["#f4f4f4", "#9ec5f4", "#5598e7", "#256abf", "#0d366b"]
ORANGE = ["#fde4d8", "#f8b597", "#f08459", "#d4541f", "#9a3810"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "figure.facecolor": WHITE, "axes.facecolor": WHITE,
                     "savefig.facecolor": WHITE, "text.color": INK})

g = pd.read_parquet(ROOT / "fire_event_dataset/data/cache/lga2021_nsw_geom.parquet")
g["geometry"] = shapely.from_wkb(g.geometry)
g = gpd.GeoDataFrame(g, geometry="geometry", crs=4283).to_crs(3577)
g["region_id"] = g.region_id.astype(int).astype(str)
T = pd.read_csv(ROOT / "Experiment 9/results/ANALYSIS_TABLE.csv", dtype={"region_id": str})
R = pd.read_csv(ROOT / "Experiment 11/results/CLOCK_ROWS.csv", dtype={"region_id": str})
bs = T[T.season == 2019].groupby("region_id").agg(homes1000=("homes_per_1000_v2_inferred", "sum")).reset_index()
gr = R[R.F == 2019].groupby("region_id")[["C4_grants_pc_H1", "C4_grants_pc_H2", "C4_grants_pc_H3"]].mean()
gr["grants_rise_pct"] = 100 * (np.exp(gr.mean(axis=1)) - 1)
m = g.merge(bs, on="region_id", how="left").merge(gr[["grants_rise_pct"]].reset_index(), on="region_id", how="left")

fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4))
fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.02, wspace=0.02)
specs = [("homes1000", [-0.01, 0.0001, 1, 5, 15, 1e9], BLUE, ["0", "<1", "1-5", "5-15", "15+"],
          "a", "Homes destroyed per 1,000 dwellings"),
         ("grants_rise_pct", [-1e9, 0, 10, 25, 50, 1e9], ORANGE, ["below unburned", "0-10%", "10-25%", "25-50%", "50%+"],
          "b", "Rise in council grants per resident, years 1-3")]
for ax, (col, bins, cols, labs, letter, name) in zip(axes, specs):
    m[m[col].isna()].plot(ax=ax, color=NODATA, edgecolor=WHITE, linewidth=0.25)
    m[m[col].notna()].plot(ax=ax, column=col, cmap=ListedColormap(cols), norm=BoundaryNorm(bins, 5),
                           edgecolor=WHITE, linewidth=0.25)
    ax.set_axis_off()
    ax.text(0.0, 1.01, letter, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")
    ax.text(0.06, 1.01, name, transform=ax.transAxes, fontsize=8, va="bottom")
    ax.legend(handles=[Patch(facecolor=c, edgecolor="#cccccc", linewidth=0.3, label=l) for c, l in zip(cols, labs)] +
              [Patch(facecolor=NODATA, label="no data")], loc="lower left", fontsize=6.5, frameon=False,
              handlelength=1.0, handleheight=0.8)
fig.savefig(ROOT / "FINAL/figures/fig3_nsw_cost_map.png", dpi=220, bbox_inches="tight", pad_inches=0.05)
print("ok")
