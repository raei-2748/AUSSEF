"""Extra report figures (descriptive), from existing results only.
fig2: NSW map, Black Summer: homes destroyed per 1,000 dwellings vs council grants per resident 3 years later.
fig3: the 9 hardest-hit Black Summer councils: fire-related grants and capital spending, before / fire year / after.
fig4: rebuilding paths per council (new houses approved above the pre-fire rate per home destroyed).
Run: uv run --no-project --with geopandas --with shapely --with pyarrow --with matplotlib --with pandas python make_report_figures.py
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
ROOT = HERE.parent
FIG = HERE / 'figures'
SURFACE, INK, INK2, NODATA, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e6e5e1', '#e6e5e1'
ORANGE = ['#fde4d8', '#f8b597', '#f08459', '#d4541f', '#9a3810']
BLUE = ['#cde2fb', '#86b6ef', '#3987e5', '#1c5cab', '#0d366b']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
                     'text.color': INK, 'axes.edgecolor': INK2, 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2})


def clean(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- fig2 map
g = pd.read_parquet(ROOT / 'fire_event_dataset/data/cache/lga2021_nsw_geom.parquet')
g['geometry'] = shapely.from_wkb(g.geometry)
g = gpd.GeoDataFrame(g, geometry='geometry', crs=4283).to_crs(3577)
g['region_id'] = g.region_id.astype(int).astype(str)
T = pd.read_csv(ROOT / 'Experiment 9/results/ANALYSIS_TABLE.csv', dtype={'region_id': str})
R = pd.read_csv(HERE / 'results/CLOCK_ROWS.csv', dtype={'region_id': str})
bs = T[T.season == 2019].groupby('region_id').agg(homes1000=('homes_per_1000_v2_inferred', 'sum')).reset_index()
gr = R[R.F == 2019].groupby('region_id')[['C4_grants_pc_H1', 'C4_grants_pc_H2', 'C4_grants_pc_H3']].mean()
gr['grants_rise_pct'] = 100 * (np.exp(gr.mean(axis=1)) - 1)
m = g.merge(bs, on='region_id', how='left').merge(gr[['grants_rise_pct']].reset_index(), on='region_id', how='left')

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
ax = axes[0]
m[m.homes1000.isna()].plot(ax=ax, color=NODATA, edgecolor='white', linewidth=0.3)
bins = [-0.01, 0.0001, 1, 5, 15, 1e9]
cols = ['#f2f1ed'] + BLUE[1:]
m[m.homes1000.notna()].plot(ax=ax, column='homes1000', cmap=ListedColormap(cols), norm=BoundaryNorm(bins, 5),
                            edgecolor='white', linewidth=0.3)
ax.set_axis_off()
ax.set_title('Homes destroyed per 1,000 dwellings', loc='left', fontsize=12, fontweight='bold')
ax.text(0, 1.0, 'Black Summer 2019-20, councils with fire rows', transform=ax.transAxes, fontsize=9, color=INK2, va='bottom')
ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(cols, ['0', '<1', '1-5', '5-15', '15+'])] +
          [Patch(color=NODATA, label='not in the Black Summer panel')], loc='lower left', fontsize=8, frameon=False)
ax = axes[1]
m[m.grants_rise_pct.isna()].plot(ax=ax, color=NODATA, edgecolor='white', linewidth=0.3)
gb = [-1e9, 0, 10, 25, 50, 1e9]
m[m.grants_rise_pct.notna()].plot(ax=ax, column='grants_rise_pct', cmap=ListedColormap(ORANGE), norm=BoundaryNorm(gb, 5),
                                  edgecolor='white', linewidth=0.3)
ax.set_axis_off()
ax.set_title('Council grants per resident, years 1-3 after', loc='left', fontsize=12, fontweight='bold')
ax.text(0, 1.0, 'Rise vs the 2 years before, above unburned councils (%)', transform=ax.transAxes, fontsize=9,
        color=INK2, va='bottom')
ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(ORANGE, ['below unburned', '0-10%', '10-25%', '25-50%', '50%+'])] +
          [Patch(color=NODATA, label='no data / not in panel')], loc='lower left', fontsize=8, frameon=False)
fig.suptitle('Where the Black Summer cost landed: homes at once, council grants for years after', x=0.01, ha='left',
             fontsize=13, fontweight='bold')
fig.text(0.01, 0.01, 'OLG council data; grants = grants and contributions per resident; excess = minus the median of NSW '
         'councils without a fire that year. Descriptive.', fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 0.95))
fig.savefig(FIG / 'fig2_map_black_summer_cost.png', dpi=160)
plt.close(fig)

# ---------------------------------------------------------------- fig3 nine councils
b = pd.read_csv(ROOT / 'Experiment 10/A_fire_councils/BLACK_SUMMER_FIRST_LOOK.csv', header=[0, 1], index_col=0)
homes = b[('homes', 'Unnamed: 10_level_1')]
order = homes.sort_values().index
fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), sharey=True)
for ax, key, title, unit in ((axes[0], 'pct_of_spending', 'Fire-related grants', '% of council spending'),
                             (axes[1], 'capex_pct', 'Capital (rebuilding) spending', '% of council spending')):
    yrs = ['2018-19', '2019-20', '2020-21']
    for i, c in enumerate(order):
        v = [b.loc[c, (key, y)] for y in yrs]
        ax.plot([v[0], max(v[1:])], [i, i], color=GRID, lw=3, zorder=1)
        ax.scatter(v[0], i, color='#86b6ef', s=55, zorder=2, label='2018-19 (before)' if i == 0 else None)
        ax.scatter(v[1], i, color='#f08459', s=55, zorder=3, label='2019-20 (fire year)' if i == 0 else None)
        ax.scatter(v[2], i, color='#9a3810', s=55, zorder=4, label='2020-21 (year after)' if i == 0 else None)
    ax.set_title(title, loc='left', fontsize=11, fontweight='bold')
    ax.set_xlabel(unit, fontsize=9)
    ax.grid(axis='x', color=GRID, lw=0.6)
    clean(ax)
axes[0].set_yticks(range(len(order)))
axes[0].set_yticklabels([f'{c} ({int(homes[c])} homes)' for c in order], fontsize=9)
axes[0].legend(loc='lower right', fontsize=8, frameon=False)
fig.suptitle('The 9 hardest-hit Black Summer councils: grants jump in the fire year or the year after; rebuilding follows',
             x=0.01, ha='left', fontsize=12, fontweight='bold')
fig.text(0.01, 0.01, 'Audited financial statements (FY2019-20 and FY2020-21; 2018-19 from the prior-year column). '
         'Fire-related grants = bushfire / emergency services / rural fire / recovery lines, storm and flood excluded.',
         fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.04, 1, 0.94))
fig.savefig(FIG / 'fig3_nine_councils.png', dpi=160)
plt.close(fig)

# ---------------------------------------------------------------- fig4 rebuilding in the hardest-hit councils
fr = []
for f in sorted((ROOT / 'fire_event_dataset/data/raw/abs_building_approvals').glob('BA_LGA20*.csv')):
    d = pd.read_csv(f, dtype=str)
    if 'REGION_TYPE' in d:
        fr.append(d[d.REGION_TYPE.str.startswith('LGA') & d.REGION.str.startswith('1')][['REGION', 'TIME_PERIOD', 'OBS_VALUE']])
d = pd.concat(fr)
d['v'] = pd.to_numeric(d.OBS_VALUE, errors='coerce')
mo = pd.PeriodIndex(d.TIME_PERIOD, freq='M')
d['fy'] = np.where(mo.month >= 7, mo.year, mo.year - 1)
ann = d.groupby(['REGION', 'fy']).v.sum().unstack()
cn = {'12750': ('Eurobodalla', 510), '10550': ('Bega Valley', 467), '16950': ('Shoalhaven', 285),
      '17080': ('Snowy Valleys', 193), '11730': ('Clarence Valley', 168), '13010': ('Glen Innes Severn', 75)}
fys = list(range(2018, 2025))
fig, axes = plt.subplots(2, 3, figsize=(13, 6.6), sharex=True)
for ax, (rid, (name, lost)) in zip(axes.flat, cn.items()):
    v = ann.loc[rid, fys]
    cols = ['#86b6ef'] + ['#d4541f'] * (len(fys) - 1)
    ax.bar(range(len(fys)), v.values, color=cols, width=0.7)
    ax.axhline(v.iloc[0], color=INK2, lw=0.8, ls='--')
    ax.set_title(f'{name}: {lost} homes destroyed', loc='left', fontsize=10, fontweight='bold')
    extra = (v.iloc[1:6] - v.iloc[0]).sum()
    ax.text(0.98, 0.95, f'extra approvals, 5 yrs after: {extra:+.0f}', transform=ax.transAxes, ha='right', va='top',
            fontsize=8.5, color=INK)
    ax.set_xticks(range(len(fys))); ax.set_xticklabels([f'{y % 100:02d}-{(y + 1) % 100:02d}' for y in fys], fontsize=8)
    ax.grid(axis='y', color=GRID, lw=0.6); clean(ax)
for ax in axes[:, 0]:
    ax.set_ylabel('new houses approved per year', fontsize=8.5)
fig.suptitle('No rebuilding surge: new house approvals in the hardest-hit councils stayed near pre-fire levels',
             x=0.01, ha='left', fontsize=12, fontweight='bold')
fig.text(0.01, 0.01, 'ABS building approvals, new houses, by council and financial year (blue = 2018-19, before Black Summer; '
         'dashed = that level). Approvals are not completions; rebuilds may have displaced other building.',
         fontsize=8, color=INK2)
plt.tight_layout(rect=(0, 0.03, 1, 0.94))
fig.savefig(FIG / 'fig4_rebuild_paths.png', dpi=160)
print('saved fig2, fig3, fig4')
