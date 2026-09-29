"""Figures for FINDINGS.md (reads results/, writes results/*.png). Palette: reference categorical slots 1-4 (blue, orange,
aqua, yellow), light surface; thin marks, direct labels, zero line, no dual axes."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_lib import RES

BLUE, ORANGE, AQUA, YELLOW = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'text.color': INK, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb', 'savefig.facecolor': '#fcfcfb'})
r = pd.read_csv(RES / 'ALLROWS_MODELS.csv')
v = pd.read_csv(RES / 'VERDICTS.csv')
sl = pd.read_csv(RES / 'SIMPLE_SLOPES.csv')
san = pd.read_csv(RES / 'SANITY_CHECK.csv')
mde = pd.read_csv(RES / 'SANITY_MDE.csv')
BLK = ['H', 'E', 'V', 'F']
NAME = {'H': 'H hazard', 'E': 'E exposure', 'V': 'V vulnerability', 'F': 'F fiscal'}

# ---- Fig 1: interaction g_B on Y
fig, ax = plt.subplots(figsize=(7.2, 3.6))
for i, b in enumerate(BLK):
    for off, sm, col, lab in [(-0.13, 'all', BLUE, 'all 218 rows'), (0.13, 'excl_BS', ORANGE, 'without Black Summer (168 rows)')]:
        x = r[(r.model == 'M1_primary') & (r.target == 'Y') & (r['sample'] == sm) & (r.term == f'g_{b}')].iloc[0]
        y = len(BLK) - 1 - i + off
        ax.plot([x.lo, x.hi], [y, y], color=col, lw=1.6, solid_capstyle='round')
        ax.plot(x.est, y, 'o', color=col, ms=6, mec='#fcfcfb', mew=1.5, label=lab if i == 0 else None)
ax.axvline(0, color=INK2, lw=0.8)
ax.set_yticks(range(len(BLK)))
ax.set_yticklabels([NAME[b] for b in BLK][::-1])
ax.set_xlabel('interaction g: change in the block\'s effect on Y per +1 SD of (log) burned share\n(SD of Y per SD of block per SD of size; 95% jackknife CI by council)')
ax.set_title('No block\'s effect on impact Y clearly grows with fire size', loc='left', fontsize=11, pad=22)
ax.legend(frameon=False, loc='lower right', bbox_to_anchor=(1.0, 1.0), ncol=2, fontsize=8.5)
ax.grid(axis='x', color=GRID, lw=0.6)
fig.tight_layout()
fig.savefig(RES / 'fig1_interactions_Y.png', dpi=170)
plt.close(fig)

# ---- Fig 2: pillars
fig, axes = plt.subplots(1, 4, figsize=(9.6, 2.9), sharey=True)
for ax, t in zip(axes, ['DL', 'IL', 'FP', 'SL']):
    for i, b in enumerate(BLK):
        x = r[(r.model == 'M1_primary') & (r.target == t) & (r['sample'] == 'all') & (r.term == f'g_{b}')].iloc[0]
        y = len(BLK) - 1 - i
        ax.plot([x.lo, x.hi], [y, y], color=BLUE, lw=1.6, solid_capstyle='round')
        ax.plot(x.est, y, 'o', color=BLUE, ms=6, mec='#fcfcfb', mew=1.5)
    n = int(r[(r.model == 'M1_primary') & (r.target == t) & (r['sample'] == 'all')].n.iloc[0])
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_title(f'{t} (n={n})', loc='left', fontsize=10)
    ax.set_yticks(range(len(BLK)))
    ax.set_yticklabels(BLK[::-1])
    ax.grid(axis='x', color=GRID, lw=0.6)
    ax.set_xlim(-0.6, 0.65)
axes[0].set_ylabel('block')
fig.supxlabel('interaction g with (log) burned share, all rows, 95% CI. None survives Holm across the 16 tests.', fontsize=9, color=INK2)
fig.tight_layout()
fig.savefig(RES / 'fig2_interactions_pillars.png', dpi=170)
plt.close(fig)

# ---- Fig 3: simple slopes of each block across burned share (Y, all rows)
fig, axes = plt.subplots(1, 4, figsize=(9.6, 2.9), sharey=True)
for ax, b, col in zip(axes, BLK, [BLUE, ORANGE, AQUA, YELLOW]):
    s = sl[(sl.target == 'Y') & (sl['sample'] == 'all') & (sl.block == b)].sort_values('share')
    ax.fill_between(s.share * 100, s.lo, s.hi, color=col, alpha=0.18, lw=0)
    ax.plot(s.share * 100, s.est, '-o', color=col, lw=2, ms=5, mec='#fcfcfb', mew=1.2)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xscale('log')
    ax.set_xticks([0.1, 1, 5, 20])
    ax.set_xticklabels(['0.1', '1', '5', '20'])
    ax.set_title(NAME[b], loc='left', fontsize=10)
    ax.grid(axis='y', color=GRID, lw=0.6)
axes[0].set_ylabel('effect of +1 SD of block on Y')
fig.supxlabel('share of the council burned (%), log scale; line = effect at that fire size, band = 95% CI', fontsize=9, color=INK2)
fig.tight_layout()
fig.savefig(RES / 'fig3_simple_slopes_Y.png', dpi=170)
plt.close(fig)

# ---- Fig 4: power from the planted-effect check (all rows vs without Black Summer)
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.2), sharey=True)
for ax, sm, ttl in zip(axes, ['all', 'excl_BS'], ['all 218 rows', 'without Black Summer (168 rows)']):
    for b, col in zip(BLK, [BLUE, ORANGE, AQUA, YELLOW]):
        s = san[(san.scenario == 'int') & (san.model == 'M1_primary') & (san.planted == b) & (san['sample'] == sm) &
                (san.term == f'g_{b}')].sort_values('implied_g')
        nul = san[(san.scenario == 'null_stratum') & (san.model == 'M1_primary') & (san['sample'] == sm) &
                  (san.term == f'g_{b}')].iloc[0]
        g = np.r_[0, s.implied_g]
        p = np.r_[nul.power_pos_pct, s.power_pos_pct]
        ax.plot(g, p, '-o', color=col, lw=1.8, ms=4, mec='#fcfcfb', mew=1)
        ax.text(g[-1] + 0.005, p[-1], b, color=INK2, va='center', fontsize=9)
    ax.axhline(80, color=INK2, lw=0.8, ls=(0, (4, 3)))
    ax.set_title(ttl, loc='left', fontsize=10)
    ax.set_xlabel('true interaction g planted in fake Y')
    ax.grid(axis='y', color=GRID, lw=0.6)
    ax.set_xlim(0, 0.36)
axes[0].set_ylabel('% of simulations where g > 0 is detected\n(unadjusted 95% CI; dashed = 80%)')
fig.tight_layout()
fig.savefig(RES / 'fig4_power_planted_interaction.png', dpi=170)
plt.close(fig)
print('figures written')
