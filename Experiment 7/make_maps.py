"""Experiment 7 maps (static PNG). Reads results/COUNCIL_MAP_LAYERS.csv and results/DAY2B_COUNCILS.csv.
Run: uv run --no-project --with geopandas --with shapely --with pyarrow --with matplotlib --with pandas python make_maps.py"""
from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Rectangle

matplotlib.use('Agg')
HERE = Path(__file__).resolve().parent
R = HERE / 'results'
SURFACE, INK, INK2, EDGE = '#fcfcfb', '#0b0b0b', '#52514e', '#ffffff'
ORANGE = ['#fde4d8', '#f8b597', '#f08459', '#d4541f', '#9a3810']
BLUE = ['#cde2fb', '#86b6ef', '#3987e5', '#1c5cab', '#0d366b']
# 3x3 bivariate (Stevens purple-teal): rows = likelihood tercile 1..3, cols = consequence tercile 1..3
BIV = {(1, 1): '#e8e8e8', (1, 2): '#ace4e4', (1, 3): '#5ac8c8',
       (2, 1): '#dfb0d6', (2, 2): '#a5add3', (2, 3): '#5698b9',
       (3, 1): '#be64ac', (3, 2): '#8c62aa', (3, 3): '#3b4994'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
                     'text.color': INK})


def geoms():
    g = pd.read_parquet(HERE.parent / 'fire_event_dataset/data/cache/lga2021_nsw_geom.parquet')
    g['geometry'] = shapely.from_wkb(g.geometry)
    g = gpd.GeoDataFrame(g, geometry='geometry', crs=4283).to_crs(3577)
    g['region_id'] = g.region_id.astype(int).astype(str)
    return g


def quantile_bins(x, k=5):
    qs = np.nanquantile(x, np.linspace(0, 1, k + 1))
    qs[0], qs[-1] = qs[0] - 1e-9, qs[-1] + 1e-9
    return qs


def head(ax, title, sub):
    ax.axis('off')
    ax.text(0, 1.13, title, transform=ax.transAxes, fontsize=11.5, fontweight='bold', va='bottom')
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=8.5, color=INK2, va='bottom')


def choropleth(ax, g, col, ramp, title, sub, fmt, outline=None):
    qs = quantile_bins(g[col].to_numpy())
    g.plot(column=col, ax=ax, cmap=ListedColormap(ramp), norm=BoundaryNorm(qs, len(ramp)), edgecolor=EDGE,
           linewidth=0.35)
    if outline is not None:
        g[outline].boundary.plot(ax=ax, color=INK, linewidth=0.9)
    head(ax, title, sub)
    for k, c in enumerate(ramp):
        ax.add_patch(Rectangle((0.02 + k * 0.075, 0.06), 0.07, 0.035, transform=ax.transAxes, color=c, ec=SURFACE))
        lab = fmt(qs[k + 1]) if fmt else ['lowest', '', '', '', 'highest'][k]
        ax.text(0.02 + k * 0.075 + 0.035, 0.035, lab, transform=ax.transAxes, ha='center', va='top',
                fontsize=7, color=INK2)
    ax.text(0.02, 0.11, 'quintiles, upper bound shown' if fmt else 'quintiles of the index', transform=ax.transAxes,
            fontsize=7, color=INK2)


def fig_maps(g):
    lay = pd.read_csv(R / 'COUNCIL_MAP_LAYERS.csv', dtype={'region_id': str})
    g = g.merge(lay, on='region_id', how='inner')
    lost = (g.realised_per_1000 >= 1.0).fillna(False)
    fig, axs = plt.subplots(1, 3, figsize=(17, 5.4))
    choropleth(axs[0], g, 'L', ORANGE, '1. Likelihood: where big fires go',
               'Chance of a fire burning ≥5% of the council in a decade like 2015–25\n(from bush-prone land and forest; '
               'leave-one-out AUC 0.95)', lambda v: f'{v:.0%}')
    choropleth(axs[1], g, 'C', BLUE, '2. Consequence: homes at risk if it burns',
               'Expected homes destroyed per 1,000 dwellings if 20% of the council burned\n(driven by the share of '
               'homes inside bush-prone land)', lambda v: f'{v:.1f}')
    ax = axs[2]
    g['biv'] = [BIV[(a, b)] for a, b in zip(g.L_tercile, g.C_tercile)]
    g.plot(color=g.biv, ax=ax, edgecolor=EDGE, linewidth=0.35)
    g[lost].boundary.plot(ax=ax, color=INK, linewidth=1.1)
    head(ax, '3. Priority: both together', 'Black outline = council actually lost ≥1 home per 1,000 dwellings\n'
         f'in 2015–25 fires ({int(lost.sum())} councils; the combined index ranks them with AUC 0.93)')
    for (a, b), c in BIV.items():
        ax.add_patch(Rectangle((0.03 + (b - 1) * 0.06, 0.05 + (a - 1) * 0.06), 0.06, 0.06, transform=ax.transAxes,
                               color=c, ec=SURFACE, lw=1))
    ax.text(0.12, 0.015, 'consequence →', transform=ax.transAxes, fontsize=7.5, ha='center', color=INK2)
    ax.text(0.005, 0.14, 'likelihood →', transform=ax.transAxes, fontsize=7.5, rotation=90, va='center', color=INK2)
    fig.suptitle('NSW Bushfire Housing-Loss Risk Map (pre-fire data only)', x=0.01, y=0.99, ha='left', fontsize=15,
                 fontweight='bold')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.80, bottom=0.02, wspace=0.08)
    fig.savefig(R / 'fig3_risk_maps.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


def fig_prospective(g):
    c = pd.read_csv(R / 'DAY2B_COUNCILS.csv', dtype={'region_id': str})
    g = g.merge(c, on='region_id', how='inner')
    top = g.index_pre.rank(ascending=False) <= 20
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.9))
    choropleth(axs[0], g, 'index_pre', ORANGE, 'Built before Black Summer',
               'Risk index from pre-2019 data only (black outline = top 20 councils)', None, outline=top)
    g['bs_cls'] = pd.cut(g.bs_per_1000, [-1, 0, 1, 5, 15, 100], labels=False)
    ramp = ['#f0efec'] + BLUE[1:]
    g.plot(color=[ramp[int(k)] for k in g.bs_cls], ax=axs[1], edgecolor=EDGE, linewidth=0.35)
    g[top].boundary.plot(ax=axs[1], color=INK, linewidth=0.9)
    ax = axs[1]
    head(ax, 'What happened in Black Summer 2019–20', 'Homes destroyed per 1,000 dwellings (black outline = the same top 20)')
    for k, (c_, lab) in enumerate(zip(ramp, ['0', '<1', '1–5', '5–15', '≥15'])):
        ax.add_patch(Rectangle((0.02 + k * 0.075, 0.06), 0.07, 0.035, transform=ax.transAxes, color=c_, ec=SURFACE))
        ax.text(0.02 + k * 0.075 + 0.035, 0.035, lab, transform=ax.transAxes, ha='center', va='top', fontsize=7,
                color=INK2)
    fig.suptitle('Prospective check: a map built before Black Summer flags the councils that lost homes\n'
                 '(AUC 0.91; 10 of its top 20 lost ≥1 home per 1,000 dwellings, about 3× the base rate)', x=0.01, y=0.99,
                 ha='left', fontsize=12.5, fontweight='bold')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.78, bottom=0.02, wspace=0.05)
    fig.savefig(R / 'fig4_prospective_black_summer.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    g = geoms()
    fig_maps(g)
    fig_prospective(g)
    print('maps written')
