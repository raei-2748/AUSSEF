"""Figures for Experiment 6: NSW council risk map and score-vs-impact scatter.
Run: uv run --no-sync --with geopandas --with shapely --with pyarrow --with matplotlib --with scipy python make_figures.py"""
from pathlib import Path
import geopandas as gpd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np, pandas as pd, shapely
from scipy.stats import spearmanr
ROOT = Path(__file__).resolve().parent; R = ROOT / 'results'
g = pd.read_parquet(ROOT.parent / 'fire_event_dataset/data/cache/lga2021_nsw_geom.parquet')
g['geometry'] = shapely.from_wkb(g.geometry); g = gpd.GeoDataFrame(g, geometry='geometry', crs=4283).to_crs(3577)
g['region_id'] = g.region_id.astype(int)
sc = pd.read_csv(R / 'COUNCIL_RISK_SCORE.csv'); rows = pd.read_csv(R / 'ROWS_WITH_SCORE.csv')
big = rows[rows.share >= 0.05].region_id.unique()
g = g.merge(sc[['region_id', 'H', 'V', 'risk_add', 'risk_HV_mean']], on='region_id', how='left')
fig, ax = plt.subplots(1, 3, figsize=(17, 6.5))
for a, (col, ttl) in zip(ax, [('H', 'Hazard block H\n(BFPL Cat 1/1-2 + forest)'), ('V', 'Vulnerability block V\n(SEIFA, income, unemployment)'),
                              ('risk_add', 'Pre-specified score (H, E, V, F equal weight)')]):
    g.plot(column=col, cmap='YlOrRd', ax=a, edgecolor='grey', linewidth=0.15, legend=True,
           legend_kwds=dict(shrink=0.6, label='percentile score (1 = higher risk)'))
    g[g.region_id.isin(big)].boundary.plot(ax=a, color='black', linewidth=0.7)
    a.set_title(ttl, fontsize=11); a.axis('off')
fig.suptitle('NSW council pre-fire scores (black outline = council had a fire burning >= 5% of it, 2015-25)', fontsize=12)
plt.tight_layout(); plt.savefig(R / 'risk_map.png', dpi=130); plt.close()

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
for a, (s, ttl) in zip(ax, [('risk_add', 'Pre-specified score'), ('V', 'Vulnerability block V'), ('risk_HV_mean', 'Exploratory H+V')]):
    for lab, mask, col in [('other fires', rows.share < 0.05, '#9aa5b1'), ('>=5% burned', rows.share >= 0.05, '#c0392b')]:
        a.scatter(rows.loc[mask, s], rows.loc[mask, 'Y'], s=18, alpha=.75, c=col, label=lab)
    big_rows = rows[rows.share >= 0.05]
    rho = spearmanr(big_rows[s], big_rows.Y)[0]; rho_all = spearmanr(rows[s], rows.Y)[0]
    a.set_title(f'{ttl}\nrho all rows {rho_all:+.2f}; rho >=5% fires {rho:+.2f}', fontsize=10)
    a.set_xlabel('council pre-fire score'); a.set_ylabel('Y (composite impact)')
ax[0].legend(); plt.tight_layout(); plt.savefig(R / 'score_vs_Y.png', dpi=130); plt.close()
