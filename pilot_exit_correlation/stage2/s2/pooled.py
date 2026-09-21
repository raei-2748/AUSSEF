"""Pooled observed-vs-independent isolation ratio with a fire-event bootstrap."""
import numpy as np


def community_arrays(cg, paths, events, closed_by_event):
    """Per-fire isolation (n,) and exit-closure (n, m) for one community.

    Isolation implies every exit path is closed, so the graph search only runs in that case.
    """
    n, m = len(events), len(paths)
    iso = np.zeros(n, dtype=bool)
    closed = np.zeros((n, m), dtype=bool)
    path_sets = [set(p) for p in paths]
    for i, ev in enumerate(events):
        s = closed_by_event.get(ev)
        if not s:
            continue
        for j, p in enumerate(path_sets):
            closed[i, j] = not p.isdisjoint(s)
        if closed[i].all():
            iso[i] = not cg.connected_without(s)
    return iso, closed


def pooled(units, weights=None):
    """units: list of (event_index array, iso, closed). weights: (B, n_events) counts or None.

    Returns dict of O, E, N1, E1 (arrays of length B when weights are given).
    """
    O = E = N1 = E1 = 0.0
    for idx, iso, closed in units:
        if weights is None:
            w = np.ones((1, len(idx)))
        else:
            w = weights[:, idx]
        n = w.sum(axis=1)
        k = w @ iso.astype(float)
        c = w @ closed.astype(float)  # (B, m)
        any_closed = w @ closed.any(axis=1).astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            p = np.where(n[:, None] > 0, c / n[:, None], 0.0)
        O = O + k
        E = E + n * p.prod(axis=1)
        N1 = N1 + any_closed
        E1 = E1 + n * (1 - (1 - p).prod(axis=1))
    out = dict(O=O, E=E, N1=N1, E1=E1)
    if weights is None:
        out = {key: float(np.squeeze(v)) for key, v in out.items()}
    return out


def ratio(O, E):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(np.asarray(E) > 0, np.asarray(O) / np.asarray(E), np.nan)


def bootstrap(units, n_events, rng, B=1000):
    """Resample whole fire events with replacement; return (lo, hi, undefined_share) for R."""
    draws = rng.integers(0, n_events, size=(B, n_events))
    weights = np.zeros((B, n_events))
    for b in range(B):
        weights[b] = np.bincount(draws[b], minlength=n_events)
    s = pooled(units, weights)
    r = ratio(s["O"], s["E"])
    ranked = np.where(np.isfinite(r), r, -np.inf)
    lo, hi = np.quantile(ranked, [0.025, 0.975], method="inverted_cdf")
    lo = float(lo) if np.isfinite(lo) else np.nan
    hi = float(hi) if np.isfinite(hi) else np.nan
    return lo, hi, float(np.mean(~np.isfinite(r)))
