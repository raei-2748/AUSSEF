"""Static PNG figures for Experiment 9. Run: python3 make_figures.py   (after run_models.py and shap_step.py)"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data import OUT

FIG = Path(__file__).resolve().parent / 'figures'
FIG.mkdir(exist_ok=True)
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
SERIES = {'rf': '#2a78d6', 'ridge': '#eb6834', 'size_line': '#1baf7a'}
MODEL_LABEL = {'rf': 'Random forest', 'ridge': 'Ridge (linear)', 'size_line': 'Fire-size line'}
TLABEL = {'Y_comp': 'Composite Y (main)', 'Y_v1': 'Composite Y (workbook v1)', 'DL': 'DL: direct loss',
          'IL': 'IL: indirect loss', 'FP': 'FP: fiscal pressure', 'SL': 'SL: social loss'}
FLABEL = {'H': 'Hazard H', 'E2': 'Exposure E2', 'V': 'Vulnerability V', 'F': 'Fiscal F',
          'log_share': 'Share of council burned', 'peak_ffdi': 'Peak FFDI', 'severity_high_extreme': 'High/extreme severity',
          'log_homes_in_fire_per_1000': 'Homes inside fire', 'log_homes_within_1km_per_1000': 'Homes within 1 km'}
PANELS = ['Y_comp', 'DL', 'IL', 'FP', 'SL']
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF, 'text.color': INK})


def fig_skill():
    M = pd.read_csv(OUT / 'METRICS.csv')
    M = M[(M.cv == 'season') & M.target.isin(TLABEL)]
    targets = list(TLABEL)[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, xs in zip(axes, ['PRE', 'PRE+FIRE']):
        for k, (mod, col) in enumerate(SERIES.items()):
            s = M[(M.xset == xs) & (M.model == mod)].set_index('target').reindex(targets)
            yy = np.arange(len(targets)) + (1 - k) * 0.22
            ax.errorbar(s.rho, yy, xerr=[s.rho - s.rho_lo, s.rho_hi - s.rho], fmt='o', ms=6, color=col, ecolor=col,
                        elinewidth=2, capsize=0, label=MODEL_LABEL[mod], mec=SURF, mew=1)
        ax.axvline(0, color=INK2, lw=1)
        ax.set_yticks(range(len(targets)), [TLABEL[t] for t in targets])
        ax.set_xlim(-0.6, 0.9)
        ax.grid(axis='x', color=GRID, lw=0.8)
        ax.set_title(f'X = {"pre-fire only" if xs == "PRE" else "pre-fire + fire"}', color=INK, loc='left')
        ax.set_xlabel('Spearman rho, predicted vs actual (unseen fire season), 95% CI')
    axes[1].legend(frameon=False, loc='lower right')
    fig.suptitle('Out-of-season prediction skill, pillar by pillar', x=0.01, ha='left', fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(FIG / 'fig1_skill_by_pillar.png', dpi=200)


def bars(ax, s, val, lo=None, hi=None, color=SERIES['rf']):
    s = s.sort_values(val)
    y = np.arange(len(s))
    ax.barh(y, s[val], color=color, height=0.6)
    if lo:
        ax.errorbar(s[val], y, xerr=[s[val] - s[lo], s[hi] - s[val]], fmt='none', ecolor=INK2, elinewidth=1)
    ax.set_yticks(y, [FLABEL[f] for f in s.feature])
    ax.axvline(0, color=INK2, lw=1)
    ax.grid(axis='x', color=GRID, lw=0.8)


def fig_importance():
    I = pd.read_csv(OUT / 'PERM_IMPORTANCE.csv')
    I = I[I.xset == 'PRE+FIRE']
    fig, axes = plt.subplots(1, 5, figsize=(16, 3.6))
    for ax, t in zip(axes, PANELS):
        bars(ax, I[I.target == t], 'mae_increase', 'lo', 'hi')
        ax.set_title(TLABEL[t], loc='left', color=INK)
        ax.set_xlabel('MAE increase when shuffled')
    fig.suptitle('Permutation importance on held-out fire seasons (random forest, pre-fire + fire X). '
                 'Bars near 0 = the model does not use it for out-of-season prediction', x=0.01, ha='left', fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / 'fig2_permutation_importance.png', dpi=200)


def fig_shap():
    p = OUT / 'SHAP_IMPORTANCE.csv'
    if not p.exists():
        return
    S = pd.read_csv(p)
    fig, axes = plt.subplots(1, 5, figsize=(16, 3.6))
    for ax, t in zip(axes, PANELS):
        bars(ax, S[S.target == t], 'mean_abs_shap')
        ax.set_title(TLABEL[t], loc='left', color=INK)
        ax.set_xlabel('mean |SHAP|')
    fig.suptitle('SHAP importance (random forest fitted on all rows; descriptive, in-sample)', x=0.01, ha='left',
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / 'fig3_shap_importance.png', dpi=200)


def fig_pred_actual():
    O = pd.read_csv(OUT / 'OOF_PREDICTIONS.csv')
    M = pd.read_csv(OUT / 'METRICS.csv')
    fig, axes = plt.subplots(1, 5, figsize=(16, 3.5))
    for ax, t in zip(axes, PANELS):
        o = O[(O.target == t) & (O.xset == 'PRE+FIRE')]
        ax.plot([0, 1], [0, 1], color=INK2, lw=1, ls='--')
        ax.scatter(o.actual, o.pred_rf, s=16, color=SERIES['rf'], alpha=0.7, edgecolor=SURF, linewidth=0.5)
        r = M[(M.target == t) & (M.xset == 'PRE+FIRE') & (M.cv == 'season') & (M.model == 'rf')].iloc[0]
        ax.text(0.03, 0.97, f'rho {r.rho:+.2f} [{r.rho_lo:+.2f}, {r.rho_hi:+.2f}]\nn = {int(r.n)}',
                transform=ax.transAxes, va='top', color=INK)
        ax.set(xlim=(0, 1), ylim=(0, 1), xlabel='Actual (0-1, 1 = worst)')
        ax.set_title(TLABEL[t], loc='left', color=INK)
        ax.grid(color=GRID, lw=0.8)
    axes[0].set_ylabel('Predicted, season held out')
    fig.suptitle('Random forest: predicted vs actual for unseen fire seasons (pre-fire + fire X)', x=0.01,
                 ha='left', fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / 'fig4_predicted_vs_actual.png', dpi=200)


def fig_shuffle():
    p = OUT / 'SHUFFLE_NULLS.json'
    if not p.exists():
        return
    N = json.load(open(p))
    S = pd.read_csv(OUT / 'SHUFFLE_CHECK.csv')
    fig, axes = plt.subplots(1, len(N), figsize=(3 * len(N), 2.8), sharey=False)
    for ax, (k, null) in zip(axes, N.items()):
        t, xs = k.split('|')
        r = S[(S.target == t) & (S.xset == xs)].iloc[0]
        ax.hist(null, bins=25, color=GRID, edgecolor=INK2, linewidth=0.4)
        ax.axvline(r.real_rho, color=SERIES['rf'], lw=2)
        ax.set_title(f'{t}, {xs}\nreal rho {r.real_rho:+.2f}, p = {r.p:.3f}', loc='left', fontsize=9, color=INK)
        ax.set_xlabel('rho with shuffled Y')
    fig.suptitle('Shuffled-Y check: grey = random forest skill when Y is shuffled; blue line = real skill',
                 x=0.01, ha='left', fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / 'fig5_shuffled_y.png', dpi=200)


if __name__ == '__main__':
    for f in (fig_skill, fig_importance, fig_shap, fig_pred_actual, fig_shuffle):
        f()
    print('figures written to', FIG)
