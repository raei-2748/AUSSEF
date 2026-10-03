"""Impact clock figure from results/CLOCK.csv and results/REBUILD_CURVE.csv.
Run: uv run --no-project --with matplotlib --with pandas python make_figure.py"""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use('Agg')
HERE = Path(__file__).resolve().parent
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e6e5e1'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
                     'text.color': INK, 'axes.edgecolor': INK2, 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2})
C = pd.read_csv(HERE / 'results/CLOCK.csv')
C = C[(C['sample'] == 'all') & (C.dose == 'homes_in_fire')]
NAMES = [('C1_traffic', 'Tourism traffic (IL)', -1, '#3987e5', ['0-3 m', '4-12 m', '13-24 m', '25-48 m']),
         ('C2_rent', 'Rents (SL)', 1, '#8c62aa', ['0-3 m', '4-12 m', '13-24 m', '25-48 m']),
         ('C3_dv', 'Domestic violence (SL)', 1, '#be64ac', ['0-3 m', '4-12 m', '13-24 m', '25-48 m']),
         ('C4_grants_pc', 'Council grants per resident (FP)', 1, '#d4541f', ['fire FY', '+1 FY', '+2 FY', '+3 FY']),
         ('C5_fire_grant_share', 'Council fire-related grants (FP)', 1, '#9a3810', ['fire FY', '+1 FY', '+2 FY', '+3 FY']),
         ('C6_capex_share', 'Council capital spending (FP)', 1, '#f08459', ['fire FY', '+1 FY', '+2 FY', '+3 FY'])]
fig, axes = plt.subplots(2, 4, figsize=(15, 7.2))
for ax, (ch, title, sign, col, xl) in zip(axes.flat, NAMES):
    d = C[C.channel == ch].set_index('horizon').reindex(['H0', 'H1', 'H2', 'H3'])
    x = range(4)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.fill_between(x, sign * d.lo, sign * d.hi, color=col, alpha=0.18, lw=0)
    ax.plot(x, sign * d.rho, color=col, lw=2.2, marker='o')
    for i, (_, r) in enumerate(d.iterrows()):
        if r.primary:
            ax.scatter([i], [sign * r.rho], s=130, facecolor='none', edgecolor=INK, lw=1.4, zorder=5)
            ax.annotate('detected' if r.detected else 'not detected', (i, sign * r.rho), textcoords='offset points',
                        xytext=(0, 10), ha='center', fontsize=8, color=INK)
    ax.set_xticks(list(x)); ax.set_xticklabels(xl, fontsize=8)
    ax.set_ylim(-0.6, 0.85); ax.grid(axis='y', color=GRID, lw=0.6)
    ax.set_title(title, fontsize=10, loc='left', color=INK)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
axes.flat[0].set_ylabel('link with fire size\n(rho, + = worse with bigger fire)', fontsize=8.5)
axes.flat[4].set_ylabel('link with fire size\n(rho, + = worse with bigger fire)', fontsize=8.5)
rb = pd.read_csv(HERE / 'results/REBUILD_CURVE.csv')
q = rb.groupby('months').extra_per_home.quantile([0.25, 0.5, 0.75]).unstack()
ax = axes.flat[6]
ax.axhline(1, color=INK2, lw=0.8, ls='--'); ax.axhline(0, color=INK2, lw=0.8)
ax.fill_between(q.index, q[0.25], q[0.75], color='#1c5cab', alpha=0.18, lw=0)
ax.plot(q.index, q[0.5], color='#1c5cab', lw=2.2, marker='o')
ax.set_title('Rebuilding (SL): new houses approved\nper home destroyed (median, IQR)', fontsize=10, loc='left')
ax.set_xticks([6, 12, 24, 36, 48]); ax.set_xlabel('months after the fire', fontsize=8.5); ax.set_ylim(-1.5, 3)
ax.text(48, 1.05, 'all replaced', ha='right', va='bottom', fontsize=7.5, color=INK2)
ax.grid(axis='y', color=GRID, lw=0.6)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
axes.flat[7].axis('off')
axes.flat[7].text(0, 0.95, 'How to read', fontsize=10, fontweight='bold', va='top')
axes.flat[7].text(0, 0.82, 'Each panel: Spearman rho between fire size\n(homes inside the fire per 1,000) and the\n'
                  'channel\'s change vs unburned councils, at\nfour times after the fire. Shaded = 95% CI\n'
                  '(council bootstrap). Circle = the horizon fixed\nin advance from the mechanism table.\n\n'
                  '218 council x fire rows, 2014-2024.\nExperiment 11, PRESPEC.md (locked).', fontsize=8.5,
                  va='top', color=INK2)
fig.suptitle('The impact clock: when each channel moves with fire size', x=0.01, ha='left', fontsize=13,
             fontweight='bold')
plt.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(HERE / 'figures/fig1_impact_clock.png', dpi=160)
print('saved')
