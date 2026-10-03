"""Figure 5: out-of-season predicted vs observed homes destroyed, area-only (R0) vs rapid estimate (R2)."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
R = Path(__file__).resolve().parent / 'results'
d = pd.read_csv(R / 'DAY8_ROWS.csv')
SURF, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.facecolor': SURF, 'axes.facecolor': SURF,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': GRID})
fig, axs = plt.subplots(1, 2, figsize=(11.5, 5.2), sharey=True)
bs = d.F == 2019
for ax, col, ttl in ((axs[0], 'pred_homes_R0', 'Area burned only'), (axs[1], 'pred_homes_R2', 'Homes inside/near the fire + burn severity')):
    x, y = d[col] + 1, d.homes + 1
    ax.plot([1, 3000], [1, 3000], color=INK2, lw=1, ls='--')
    ax.fill_between([1, 3000], [0.5, 1500], [2, 6000], color='#f0efec', zorder=0)
    ax.scatter(x[~bs], y[~bs], s=34, color='#86b6ef', edgecolors=SURF, lw=1, label='Other seasons')
    ax.scatter(x[bs], y[bs], s=34, color='#1c5cab', edgecolors=SURF, lw=1, label='Black Summer')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(0.8, 3000); ax.set_ylim(0.8, 3000)
    ax.set_title(ttl, loc='left', fontsize=11, fontweight='bold')
    ax.set_xlabel('Predicted homes destroyed + 1 (season held out)', color=INK2)
    ax.grid(color=GRID, lw=.6)
axs[0].set_ylabel('Actual homes destroyed + 1', color=INK2)
axs[1].legend(frameon=False, loc='lower right')
axs[0].text(1.1, 1500, 'Black Summer predicted: 133\nactual: 2,483', fontsize=9, color=INK2)
axs[1].text(1.1, 1500, 'Black Summer predicted: 1,442\nactual: 2,483', fontsize=9, color=INK2)
fig.suptitle('Rapid damage estimate: knowing which homes were inside the fire cuts prediction error by 88%',
             x=0.01, ha='left', fontsize=12.5, fontweight='bold')
fig.text(0.01, -0.02, 'Each dot = one council × fire. Dashed line = perfect; grey band = within a factor of 2. '
         'Every prediction made with that fire season left out of training.', fontsize=8, color=INK2)
fig.tight_layout()
fig.savefig(R / 'fig5_rapid_estimate.png', dpi=200, bbox_inches='tight')
