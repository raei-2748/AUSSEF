"""Day 1 figures (static PNG for the report). Reads results/*.csv; run after build_y2.py and deviations_day1.py."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
R = HERE / 'results'
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
RAMP = ['#86b6ef', '#3987e5', '#1c5cab', '#0d366b']          # sequential blue, steps 250/400/550/700 (ordinal)
BINS = ['<1%', '1-5%', '5-20%', '>=20%']
BIN_TXT = ['<1%', '1–5%', '5–20%', '≥20%']
NAMES = {'total_income': 'Total personal income', 'biz_count': 'Number of businesses',
         'cash_cover': 'Council cash reserves', 'services_share': 'Services share of spending',
         'renewals_ratio': 'Asset renewals', 'income_support': 'Income-support recipients'}
ORDER = ['total_income', 'biz_count', 'cash_cover', 'services_share', 'renewals_ratio', 'income_support']

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': SURFACE,
                     'axes.facecolor': SURFACE, 'axes.spines.top': False, 'axes.spines.right': False})


def fig_dose():
    dl = pd.read_csv(R / 'DEV_D2_DL_BY_BIN.csv').set_index('bin').loc[BINS]
    se = pd.read_csv(R / 'DEV_D2_AVERAGE_EFFECTS.csv')
    se = se[(se.variant == 'V2b_noNTL') & se.bin.isin(BINS)]
    fig = plt.figure(figsize=(12.5, 5.6))
    gs = fig.add_gridspec(2, 5, width_ratios=[1.35, .15, 1, 1, 1], hspace=.55, wspace=.35)
    ax = fig.add_subplot(gs[:, 0])
    x = np.arange(4)
    ax.bar(x, dl.homes_destroyed_per_1000, color=RAMP, width=.62, edgecolor=SURFACE, linewidth=2)
    ax.errorbar(x, dl.homes_destroyed_per_1000, yerr=[dl.homes_destroyed_per_1000 - dl.ci_low,
                                                      dl.ci_high - dl.homes_destroyed_per_1000],
                fmt='none', ecolor=INK2, elinewidth=1.2, capsize=3)
    for xi, v, n, hi in zip(x, dl.homes_destroyed_per_1000, dl.rows, dl.ci_high):
        ax.text(xi, hi + .3, f'{v:.1f}', ha='center', va='bottom', color=INK, fontsize=10)
        ax.text(xi, -.9, f'n={n}', ha='center', va='top', color=INK2, fontsize=8)
    ax.set_xticks(x, BIN_TXT)
    ax.set_xlabel('Share of the council burned by the fire')
    ax.set_ylabel('Homes destroyed per 1,000 dwellings')
    ax.set_ylim(-1.6, 14)
    ax.axhline(0, color=GRID, lw=1)
    ax.set_title('Direct loss rises steeply with fire size', loc='left', fontsize=11.5, fontweight='bold')
    ax.grid(axis='y', color=GRID, lw=.6)
    ax.set_axisbelow(True)
    for k, ind in enumerate(ORDER):
        a = fig.add_subplot(gs[k // 3, 2 + k % 3])
        d = se[se.indicator == ind].set_index('bin').loc[BINS]
        a.axhspan(-1, 1, color='#f0efec', zorder=0)
        a.axhline(0, color=INK2, lw=.8, zorder=1)
        a.errorbar(x, d.change_sd, yerr=[d.change_sd - d.ci_low, d.ci_high - d.change_sd], fmt='none', ecolor=INK2,
                   elinewidth=1, capsize=2.5, zorder=2)
        a.scatter(x, d.change_sd, s=46, c=RAMP, edgecolors=SURFACE, linewidths=1.5, zorder=3)
        a.set_xticks(x, BIN_TXT, fontsize=8)
        a.set_ylim(-1.6, 1.6)
        a.set_yticks([-1, 0, 1])
        a.set_title(NAMES[ind], loc='left', fontsize=9.5)
        if k % 3 == 0:
            a.set_ylabel('Change vs normal\n(SD of year-to-year noise)', fontsize=8.5)
    fig.text(.435, .985, '...council socioeconomic indicators do not', fontsize=11.5, fontweight='bold', color=INK)
    fig.text(.435, .945, 'Change after the fire vs the council\'s own pre-fire years, in SD of normal year-to-year '
             'noise (+ = worse)', fontsize=9, color=INK2)
    fig.text(.435, .02, 'Grey band = ±1 SD of normal year-to-year variation. Bars/whiskers: mean and 95% interval '
             '(council-cluster bootstrap). 218 NSW council×fire rows, 2015–25.', fontsize=8, color=INK2)
    fig.savefig(R / 'fig1_dose_response.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


def fig_event():
    e = pd.read_csv(R / 'EVENT_PROFILE.csv')
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.2), sharex=True)
    for ax, ind in zip(axs.ravel(), ORDER):
        d = e[e.indicator == ind].sort_values('rel')
        ax.axvspan(-.5, 1.5, color='#f0efec', zorder=0)
        ax.axhline(0, color=INK2, lw=.8)
        ax.fill_between(d.rel, d.ci_low, d.ci_high, color='#b7d3f6', lw=0, zorder=1)
        ax.plot(d.rel, d.z_mean, color='#2a78d6', lw=2, zorder=2)
        ax.scatter(d.rel, d.z_mean, s=30, color='#2a78d6', edgecolors=SURFACE, linewidths=1.5, zorder=3)
        ax.set_title(NAMES[ind], loc='left', fontsize=10)
        ax.set_ylim(-1.3, 1.3)
        ax.grid(axis='y', color=GRID, lw=.6)
    for ax in axs[1]:
        ax.set_xlabel('Years relative to the fire (0 = fire year)')
    for ax in axs[:, 0]:
        ax.set_ylabel('Worse than expected (SD units)')
    fig.suptitle('Councils with ≥20% burned (23, all Black Summer): no clear jump after the fire except cash reserves',
                 x=.01, ha='left', fontsize=12, fontweight='bold', color=INK)
    fig.text(.01, -.01, 'Line = mean deviation from the expected path (council + rural/regional/metro year effects); '
             'band = 95% interval. Shaded = fire year and year after.', fontsize=8, color=INK2)
    fig.tight_layout()
    fig.savefig(R / 'fig2_event_profile.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    fig_dose()
    fig_event()
    print('figures written')
