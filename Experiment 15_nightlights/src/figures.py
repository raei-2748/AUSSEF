"""Experiment 15 figures from results/ (run after analysis.py).
Run: uv run --no-project --with geopandas --with pyarrow --with matplotlib python src/figures.py
"""
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
RES, FIG = HERE / "results", HERE / "figures"
DS = Path("/Users/ray/Research/AUSSEF - Local/fire_event_dataset")
SERIES = {"inside": "#2a78d6", "ring_0_1km": "#eb6834", "ring_1_5km": "#1baf7a", "council": "#4a3aa7"}
LABEL = {"inside": "Inside the burned outline", "ring_0_1km": "0-1 km outside", "ring_1_5km": "1-5 km outside",
         "council": "Whole councils (Shoalhaven, Eurobodalla, Bega Valley)"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
GROUPS = {"south_coast": dict(title="Black Summer South Coast (Currowan, Clyde Mountain, Badja Forest Rd, Border)",
                              ids=["F_1e185c690e800a5cfe", "F_592a4d0267971025b2", "F_a543db8a50cf524023",
                                   "F_948a8dcc8a9b94a266"], S="2019-11", E="2020-03"),
          "tathra": dict(title="Tathra / Reedy Swamp fire, March 2018 (pre-COVID)", ids=["F_e69a83842cba888fd5"],
                         S="2018-03", E="2018-04")}
plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})


def pct(d):
    return 100 * (np.exp(d) - 1)


def curves(name, g):
    fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True, sharey=True)
    S, E = pd.Timestamp(g["S"]), pd.Timestamp(g["E"]) + pd.offsets.MonthEnd(0)
    for ax, ring in zip(axes, ["inside", "ring_0_1km", "ring_1_5km"]):
        m = pd.read_csv(RES / f"monthly_{name}_{ring}.csv")
        m["t"] = pd.to_datetime(m.month)
        m = m[m.t >= S - pd.DateOffset(months=24)]
        c = SERIES[ring]
        ax.axvspan(S - pd.DateOffset(months=24), S - pd.DateOffset(days=1), color="#f7f6f2", zorder=0)
        ax.axvspan(S, E, color="#e1e0d9", zorder=0)
        ax.axhline(0, color="#c3c2b7", lw=1)
        ax.fill_between(m.t, pct(m.lo), pct(m.hi), color=c, alpha=0.18, lw=0)
        ax.plot(m.t, pct(m.D), color=c, lw=2, marker="o", ms=3)
        ax.set_title(f"{LABEL[ring]}", loc="left", color=INK, fontsize=9)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_ylim(-60, 60)
    axes[1].set_ylabel("Lights vs expected (%)")
    axes[0].text(E, -52, " darker band: fire burning (flame months masked)", color=MUTED, fontsize=8, va="bottom")
    axes[0].text(S - pd.DateOffset(months=24), 52, " baseline months: near 0 by construction (not a trend test)",
                 color=MUTED, fontsize=8, va="top")
    fig.suptitle(g["title"] + "\nNight lights compared with similar unburned settled places; band = 95% interval "
                 "(pseudo-towns); y-axis clipped at \u00b160%", x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(FIG / f"curves_{name}.png", dpi=160)
    plt.close(fig)


def maps(name, g):
    p = pd.read_csv(RES / f"pixels_{name}.csv")
    f = gpd.read_parquet(DS / "data/cache/fires.parquet")
    f = f[f.event_id.isin(g["ids"])].to_crs(4326)
    wins = [("early", "First 6 months after the fire"), ("y1_2", "Months 7-18"), ("later", "Month 31 to mid-2025")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 9.5) if name == "south_coast" else (13, 4.8), layout="constrained")
    pad = 0.05
    for ax, (w, title) in zip(axes, wins):
        q = p[(p.window == w) & (p.ring != "ring_1_5km")] if name == "south_coast" else p[p.window == w]
        f.boundary.plot(ax=ax, color="#898781", lw=0.6)
        sc = ax.scatter(q.lon, q.lat, c=pct(q.D).clip(-60, 60), cmap="RdBu", vmin=-60, vmax=60,
                        s=(14 if name == "south_coast" else 40) + 90 * np.sqrt(q.dwell / q.dwell.max()), edgecolor="#fcfcfb", linewidth=0.4)
        ax.set_xlim(q.lon.min() - pad, q.lon.max() + pad)
        ax.set_ylim(q.lat.min() - pad, q.lat.max() + pad)
        ax.set_aspect(1 / np.cos(np.deg2rad(q.lat.mean())))
        ax.set_title(title, loc="left", color=INK, fontsize=9)
        ax.tick_params(labelsize=7)
        ax.ticklabel_format(useOffset=False)
    cb = fig.colorbar(sc, ax=axes, shrink=0.7, label="Lights vs expected (%) (red = darker, blue = brighter)")
    cb.outline.set_visible(False)
    fig.suptitle(g["title"] + "\nEach dot = one settled pixel (>= 5 homes) inside or near the outline; dot size = homes; "
                 "grey line = fire outline", x=0.01, ha="left", fontsize=10, color=INK)
    fig.savefig(FIG / f"map_{name}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def dose():
    d = pd.read_csv(RES / "pooled_fires.csv").dropna(subset=["D_early"])
    fig, ax = plt.subplots(figsize=(8, 4.8))
    has = d.homes_per_1000_dwell_in.notna()
    x = d.loc[has, "homes_per_1000_dwell_in"]
    ax.errorbar(x, pct(d.loc[has, "D_early"]), yerr=[pct(d.loc[has, "D_early"]) - pct(d.loc[has, "lo"]),
                                                    pct(d.loc[has, "hi"]) - pct(d.loc[has, "D_early"])],
                fmt="o", color="#2a78d6", ecolor="#86b6ef", ms=6, capsize=0, lw=1.2)
    for r in d[has].itertuples():
        ax.annotate(r.event_name.split(",")[0], (r.homes_per_1000_dwell_in, pct(r.D_early)), fontsize=7,
                    color=MUTED, xytext=(4, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.axhline(0, color="#c3c2b7", lw=1)
    ax.grid(color=GRID, lw=0.6)
    ax.set_xlabel("Homes destroyed per 1,000 homes inside the outline (official figures, log scale)")
    ax.set_ylabel("Lights in first 6 months after (%)")
    ax.set_title("Does the light drop grow with home loss? (10 fires with an official figure; bars = 95% interval)",
                 loc="left", fontsize=9, color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "dose_pooled.png", dpi=160)
    plt.close(fig)


def dilution():
    w = pd.read_csv(RES / "windows.csv")
    rows = [("south_coast", "inside"), ("south_coast", "ring_0_1km"), ("south_coast", "ring_1_5km"),
            ("south_coast_councils", "council")]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    for i, (g, r) in enumerate(rows):
        q = w[(w.group == g) & (w.ring == r) & (w.window == "early")].iloc[0]
        lo, hi = (q.boot_lo, q.boot_hi) if r == "council" else (q.lo, q.hi)
        ax.barh(i, pct(q.D), color=SERIES[r], height=0.55)
        ax.plot([pct(lo), pct(hi)], [i, i], color=INK, lw=1.2)
        ax.text(min(pct(lo), pct(q.D)) - 1, i, f"{pct(q.D):+.0f}%", va="center", ha="right", fontsize=8, color=INK)
    ax.set_yticks(range(len(rows)), [LABEL[r] + (" *" if r == "council" else "") for _, r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.axvline(0, color="#c3c2b7", lw=1)
    ax.set_xlim(-35, 10)
    ax.set_xlabel("Lights in first 6 months after the fire vs expected (%), line = 95% interval")
    fig.suptitle("Black Summer South Coast: averaging over whole councils dilutes the signal", x=0.01, ha="left",
                 fontsize=9, color=INK)
    fig.text(0.01, 0.01, "* council interval from the block bootstrap (too big for pseudo-towns)", fontsize=7,
             color=MUTED)
    fig.tight_layout()
    fig.savefig(FIG / "dilution_south_coast.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    for n, g in GROUPS.items():
        curves(n, g)
        maps(n, g)
    dose()
    dilution()
    print(sorted(p.name for p in FIG.iterdir()))
