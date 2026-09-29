"""Figure for the FP audit: are fire-row excess changes bigger than normal movement in unburned councils?

For each old FP component (plus1 window) the distribution of z (excess / robust SD of the unburned excess in the same
fire year) for unburned council-years (grey) and for the fire rows (accent). If a fire moved the ratio, the fire-row curve
would sit to the right (more pressure) or be wider. Run after audit_fp.py:  python3 make_audit_figure.py
"""
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from audit_fp import COMP, robust_sd, unburned_excess
from fpcommon import RESULTS, excess_for_rows, load_fire_flags, load_master, load_panel

GREY, ACCENT, INK, MUTED = '#8a8f98', '#c2410c', '#1f2937', '#6b7280'
LABEL = {'cash_cover': 'Cash-cover drawdown', 'service_share': 'Services crowd-out', 'renewals_ratio': 'Renewals-ratio rise'}


def main():
    m, panel, flags = load_master(), load_panel(), load_fire_flags()
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    bins = np.linspace(-3.5, 3.5, 36)
    for ax, c in zip(axes, LABEL):
        met, kind, sg, unit = COMP[c]
        u = unburned_excess(panel, flags, met, 1, kind)
        rsd = u.groupby('fy').exc.apply(robust_sd)
        zu = (u.exc / u.fy.map(rsd) * sg).dropna()
        x = excess_for_rows(panel, flags, m, met, 1, kind)
        ok = x.notna()
        zf = (x[ok] / m.fy[ok].map(rsd) * sg).dropna()
        ax.hist(np.clip(zu, -3.5, 3.5), bins=bins, density=True, color=GREY, alpha=0.55, linewidth=0)
        ax.hist(np.clip(zf, -3.5, 3.5), bins=bins, density=True, histtype='step', color=ACCENT, linewidth=2)
        ax.axvline(0, color=MUTED, linewidth=0.8)
        ax.set_title(LABEL[c] + f'\nfire rows n={len(zf)}, median z {zf.median():+.2f}; unburned n={len(zu)}',
                     fontsize=10, color=INK, loc='left')
        ax.set_xlabel('z: more pressure  →', fontsize=9, color=MUTED)
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        ax.grid(axis='y', color='#e5e7eb', linewidth=0.6)
        ax.tick_params(colors=MUTED, labelsize=8)
    axes[0].set_ylabel('density', fontsize=9, color=MUTED)
    axes[0].text(1.0, 0.62, 'unburned councils', color='#4b5563', fontsize=9, ha='left')
    axes[0].text(1.0, 0.55, 'fire rows', color=ACCENT, fontsize=9, ha='left')
    fig.suptitle('FP components: fire-row excess changes vs normal movement in unburned councils (t+1 window)',
                 fontsize=11, color=INK, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(RESULTS / 'audit_noise.png', dpi=160)


if __name__ == '__main__':
    main()
