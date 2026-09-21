"""Exit counting: unit-capacity max-flow from community nodes to a ring of radius R.

Undirected road links are modelled as a pair of opposite arcs, each with capacity equal to
the number of parallel road edges between the two nodes. Max-flow on this digraph equals the
maximum number of edge-disjoint undirected paths.
"""
from collections import defaultdict, deque

import networkx as nx
import numpy as np
import shapely

SRC, SNK = -1, -2


class CommunityGraph:
    def __init__(self, net, poly, centroid_xy, R):
        xy = net["node_xy"]
        e = net["edges"]
        cx, cy = centroid_xy
        d = np.hypot(xy[:, 0] - cx, xy[:, 1] - cy)
        inside = d < R
        ui, vi = e.ui.values, e.vi.values
        iu, iv = inside[ui], inside[vi]
        keep = np.flatnonzero(iu | iv)
        crossing = (iu ^ iv)
        ring = np.unique(np.concatenate([ui[crossing & ~iu], vi[crossing & ~iv]]))

        # Sources: nodes inside the polygon; fallback to endpoints of intersecting edges.
        cand = np.flatnonzero(inside)
        cand = cand[shapely.contains_xy(poly, xy[cand, 0], xy[cand, 1])]
        self.source_fallback = False
        if len(cand) == 0:
            hit = keep[shapely.intersects(net["geom"][keep], poly)]
            cand = np.unique(np.concatenate([ui[hit], vi[hit]]))
            cand = cand[inside[cand]]
            self.source_fallback = True
        self.sources = cand
        self.ring = ring
        self.n_edges = len(keep)

        # Links: undirected node pairs -> parallel edge ids.
        a = np.minimum(ui[keep], vi[keep])
        b = np.maximum(ui[keep], vi[keep])
        eid = e.edge_id.values[keep]
        length = e.length_m.values[keep]
        order = np.lexsort((eid, b, a))
        self.links = {}  # (a, b) -> [edge_ids]
        self.link_len = {}
        for i in order:
            k = (int(a[i]), int(b[i]))
            self.links.setdefault(k, []).append(int(eid[i]))
            self.link_len[k] = min(self.link_len.get(k, np.inf), length[i])
        self.edge_to_link = {x: k for k, ids in self.links.items() for x in ids}
        self.adj = defaultdict(list)
        for (p, q) in self.links:
            self.adj[p].append(q)
            self.adj[q].append(p)

    def digraph(self):
        G = nx.DiGraph()
        for (p, q), ids in self.links.items():
            w = max(1, int(round(self.link_len[(p, q)])))
            G.add_edge(p, q, capacity=len(ids), weight=w)
            G.add_edge(q, p, capacity=len(ids), weight=w)
        ring = set(self.ring.tolist())
        for s in self.sources.tolist():
            if s not in ring:
                G.add_edge(SRC, s, weight=0)
        for t in ring:
            G.add_edge(t, SNK, weight=0)
        return G

    def exits_and_paths(self, with_paths=True):
        """Return (exit_count, list of paths as lists of edge_ids)."""
        if len(self.sources) == 0 or len(self.ring) == 0:
            return 0, []
        G = self.digraph()
        if SRC not in G or SNK not in G:
            return 0, []
        k = nx.maximum_flow_value(G, SRC, SNK)
        if not with_paths or k == 0:
            return int(k), []
        flow = nx.max_flow_min_cost(G, SRC, SNK, capacity="capacity", weight="weight")
        # Net flow on each undirected link; opposite flows cancel.
        out = defaultdict(dict)
        for p, nbrs in flow.items():
            for q, f in nbrs.items():
                if f <= 0:
                    continue
                if p in (SRC,) or q in (SNK,):
                    out[p][q] = out[p].get(q, 0) + f
                    continue
                net = f - flow.get(q, {}).get(p, 0)
                if net > 0:
                    out[p][q] = net
        used = defaultdict(int)
        paths = []
        for _ in range(int(k)):
            node, path, seen = SRC, [], {SRC}
            while node != SNK:
                nxt = next(q for q in sorted(out[node]) if out[node][q] > 0)
                out[node][nxt] -= 1
                if node != SRC and nxt != SNK:
                    link = (min(node, nxt), max(node, nxt))
                    path.append(self.links[link][used[link]])
                    used[link] += 1
                if nxt in seen and nxt != SNK:
                    raise RuntimeError("cycle in flow decomposition")
                seen.add(nxt)
                node = nxt
            paths.append(path)
        return int(k), paths

    def connected_without(self, closed_edge_ids):
        """True if any source still reaches the ring once the closed edges are removed."""
        blocked_count = defaultdict(int)
        for x in closed_edge_ids:
            link = self.edge_to_link.get(x)
            if link is not None:
                blocked_count[link] += 1
        blocked = {l for l, c in blocked_count.items() if c >= len(self.links[l])}
        ring = set(self.ring.tolist())
        seen = set(self.sources.tolist())
        if seen & ring:
            return True
        dq = deque(seen)
        while dq:
            p = dq.popleft()
            for q in self.adj[p]:
                if q in seen or (min(p, q), max(p, q)) in blocked:
                    continue
                if q in ring:
                    return True
                seen.add(q)
                dq.append(q)
        return False
