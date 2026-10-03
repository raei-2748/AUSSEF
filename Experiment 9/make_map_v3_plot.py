"""Plot the v3 NSW council map from results/MAP_COUNCILS_V3.csv (descriptive).
Run: uv run --no-project --with geopandas --with shapely --with pyarrow --with matplotlib --with pandas python make_map_v3_plot.py
"""
from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

matplotlib.use('Agg')
HERE = Path(__file__).resolve().parent
SURFACE, INK, INK2, NODATA = '#fcfcfb', '#0b0b0b', '#52514e', '#e6e5e1'
ORANGE = ['#fde4d8', '#f8b597', '#f08459', '#d4541f', '#9a3810']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'text.color': INK})

g = pd.read_parquet(HERE.parent / 'fire_event_dataset/data/cache/lga2021_nsw_geom.parquet')
g['geometry'] = shapely.from_wkb(g.geometry)
g = gpd.GeoDataFrame(g, geometry='geometry', crs=4283).to_crs(3577)
g['region_id'] = g.region_id.astype(int).astype(str)
d = pd.read_csv(HERE / 'results/MAP_COUNCILS_V3.csv', dtype={'region_id': str})
g = g.merge(d, on='region_id', how='left')


def panel(ax, col, title, sub):
    x = g[col]
    qs = np.nanquantile(x, np.linspace(0, 1, 6)); qs[0] -= 1e-9; qs[-1] += 1e-9
    g[g[col].isna()].plot(ax=ax, color=NODATA, edgecolor='white', linewidth=0.3)
    g[g[col].notna()].plot(ax=ax, column=col, cmap=ListedColormap(ORANGE), norm=BoundaryNorm(qs, 5),
                           edgecolor='white', linewidth=0.3)
    ax.set_axis_off()
    ax.set_title(title, loc='left', fontsize=12, fontweight='bold', color=INK)
    ax.text(0, 1.0, sub, transform=ax.transAxes, fontsize=8.5, color=INK2, va='bottom')
    labs = [f'{qs[i]:.2f}–{qs[i + 1]:.2f}' for i in range(5)]
    h = [Patch(color=c, label=l) for c, l in zip(ORANGE, labs)]
    if g[col].isna().any():
        h.append(Patch(color=NODATA, label='no fire rows'))
    ax.legend(handles=h, loc='lower left', fontsize=7.5, frameon=False, title='quintiles (0–1, 1 = worst)',
              title_fontsize=7.5)


fig, axes = plt.subplots(1, 2, figsize=(13, 6.6))
panel(axes[0], 'pred_Y_v3_prefire', 'Pre-fire risk of composite Y (v3)',
      'Random forest on pre-fire traits (H, E2, V, F, X23), all 129 councils')
panel(axes[1], 'obs_Y_v3_mean', 'Observed composite Y (v3), mean over fires',
      '69 councils with fire rows, 2014–2024')
fig.text(0.01, 0.01, 'Y v3 = DL + IL + FP + SL (equal weights), fire-matched indicators (Experiment 9, PRESPEC Addendum v3). '
         'Descriptive map; out-of-season skill is in METRICS.csv.', fontsize=7.5, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 1))
(HERE / 'figures').mkdir(exist_ok=True)
fig.savefig(HERE / 'figures/fig6_nsw_map_y_v3.png', dpi=170)
print('saved figures/fig6_nsw_map_y_v3.png')
