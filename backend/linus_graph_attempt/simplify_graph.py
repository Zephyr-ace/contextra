# backend/linus_graph_attempt/simplify_graph.py
"""
Simplify the Apple-centered graph and plot it.

SCORING (toward Apple):
- First-order F: score(F) = max_importance(Apple—F).
- Second-order Y via connector F: score(Y) = max_F [ max_importance(Apple—F) * max_importance(F—Y) ].
  (Product rule: 0.9*0.9=0.81 beats a lone weak 0.5.)

SELECTION:
1) Keep the top 10 nodes by score (first- OR second-order).
2) Additionally keep the top 5 nodes that are second-order only.
3) For any selected second-order node, also include its strongest connector F.
4) Always keep Apple.

Outputs:
- backend/linus_graph_attempt/simplified_graph/simplified_graph.json
- backend/linus_graph_attempt/simplified_graph/simplified_graph.png
"""

import os
import re
import json
from typing import Dict, Tuple, List, Any

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

# -------- Paths / constants --------
BASE = "backend/linus_graph_attempt"
INPUT_JSON = os.path.join(BASE, "general_2nd_degree_apple_graph.json")

OUT_DIR  = os.path.join(BASE, "simplified_graph")
OUT_JSON = os.path.join(OUT_DIR, "simplified_graph.json")
OUT_PNG  = os.path.join(OUT_DIR, "simplified_graph.png")

APPLE_LABEL_DEFAULT = "Apple Inc."
TOP_OVERALL = 10
TOP_SECOND_ONLY = 5


# -------- Helpers --------
def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)

def load_rf_graph(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("nodes", []), data.get("edges", [])

def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()

def sorted_pair(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)

def edge_importance(edge: Dict[str, Any]) -> float:
    d = edge.get("data", {}) or {}
    if d.get("max_importance") is not None:
        return float(d["max_importance"])
    rels = d.get("relations", []) or []
    if rels:
        return max(float(r.get("importance_score", 0.0) or 0.0) for r in rels)
    return 0.0

def blue_to_red(value: float):
    """Importance [0,1] → color; ≤0.6 stays blue; → bright red at 1.0."""
    v = max(0.0, min(1.0, float(value)))
    if v < 0.6:
        t = (v / 0.6) * 0.2
    else:
        t = 0.2 + ((v - 0.6) / 0.4) * 0.8
    cmap = mcolors.LinearSegmentedColormap.from_list("blue_red", ["#2563eb", "#ef4444"])
    return cmap(t)


# -------- Index ReactFlow graph by labels --------
def build_indexes(nodes, edges):
    id2label = {n["id"]: n.get("data", {}).get("label", n["id"]) for n in nodes}
    label2id = {lbl: nid for nid, lbl in id2label.items()}
    pair2imp: Dict[Tuple[str, str], float] = {}

    for e in edges:
        a = id2label[e["source"]]
        b = id2label[e["target"]]
        imp = edge_importance(e)
        key = sorted_pair(a, b)
        pair2imp[key] = max(pair2imp.get(key, 0.0), imp)

    return id2label, label2id, pair2imp


# -------- Compute scores to Apple --------
def compute_scores(apple: str, pair2imp: Dict[Tuple[str, str], float]):
    # direct neighbors
    direct_scores: Dict[str, float] = {}
    labels = set()
    for (u, v), imp in pair2imp.items():
        labels.update([u, v])
        if apple in (u, v):
            other = v if u == apple else u
            direct_scores[other] = max(direct_scores.get(other, 0.0), imp)

    effective_scores: Dict[str, float] = {}
    best_connector: Dict[str, str] = {}

    for x in labels:
        if x == apple:
            continue
        if x in direct_scores:
            effective_scores[x] = direct_scores[x]
        else:
            # product rule via best connector F
            best = 0.0
            best_f = None
            for f, af in direct_scores.items():
                s_fx = pair2imp.get(sorted_pair(f, x), 0.0)
                score = af * s_fx
                if score > best:
                    best = score
                    best_f = f
            effective_scores[x] = best
            if best_f:
                best_connector[x] = best_f

    return direct_scores, effective_scores, best_connector


# -------- Select subset --------
def select_nodes(apple, direct_scores, effective_scores, best_connector):
    ranked_all = sorted(
        [(n, s) for n, s in effective_scores.items() if n != apple],
        key=lambda t: t[1], reverse=True
    )
    top_overall = [n for n, _ in ranked_all[:TOP_OVERALL]]

    ranked_second = sorted(
        [(n, s) for n, s in effective_scores.items() if (n not in direct_scores and n != apple)],
        key=lambda t: t[1], reverse=True
    )
    top_second_only = [n for n, _ in ranked_second[:TOP_SECOND_ONLY]]

    selected = set(top_overall) | set(top_second_only)
    # include connectors
    for n in list(selected):
        if n not in direct_scores:
            f = best_connector.get(n)
            if f:
                selected.add(f)
    selected.add(apple)  # always keep Apple

    return selected, top_overall, top_second_only


# -------- Build subgraph & layout (labels as nodes) --------
def build_label_graph(selected: set, pair2imp: Dict[Tuple[str, str], float], apple_label: str):
    """Create NetworkX graph on labels and compute a fresh layout.

    IMPORTANT FIX:
    When fixing nodes in spring_layout, NetworkX requires initial positions in `pos`
    for each fixed node. We pass `pos={apple_label: (0.0, 0.0)}` and `fixed=[apple_label]`.
    """
    G = nx.Graph()
    for lbl in selected:
        G.add_node(lbl)
    for (u, v), imp in pair2imp.items():
        if u in selected and v in selected:
            G.add_edge(u, v, importance=imp)

    if apple_label in G.nodes:
        init_pos = {apple_label: (0.0, 0.0)}
        pos = nx.spring_layout(
            G,
            k=2.6,                 # spacing (bigger → more spread)
            iterations=800,
            seed=42,
            weight="importance",
            pos=init_pos,          # <-- provide initial positions for fixed nodes
            fixed=[apple_label],   # <-- fix Apple at the center
        )
        pos[apple_label] = (0.0, 0.0)
    else:
        pos = nx.spring_layout(G, k=2.6, iterations=800, seed=42, weight="importance")

    # scale positions for readability
    SCALE = 450.0
    pos = {n: (float(x) * SCALE, float(y) * SCALE) for n, (x, y) in pos.items()}
    return G, pos


# -------- Convert to ReactFlow JSON --------
def to_reactflow(G, pos):
    nodes = []
    for lbl in G.nodes():
        nodes.append({
            "id": slug(lbl),
            "position": {"x": pos[lbl][0], "y": pos[lbl][1]},
            "data": {"label": lbl},
            "type": "custom",
            "draggable": True
        })

    edges = []
    for u, v, d in G.edges(data=True):
        imp = float(d.get("importance", 0.0))
        edges.append({
            "id": f"{slug(u)}--{slug(v)}",
            "source": slug(u),
            "target": slug(v),
            "type": "floating",
            "data": {"max_importance": imp}
        })

    return {"nodes": nodes, "edges": edges}


# -------- Plot --------
def plot_graph(G, pos, out_png, apple_label: str):
    plt.figure(figsize=(14, 10), dpi=220)
    ax = plt.gca(); ax.set_axis_off()

    first_order = set(G.neighbors(apple_label)) if apple_label in G else set()

    node_sizes = []
    node_colors = []
    labels = {n: n for n in G.nodes()}  # labels are the node names (labels)

    for n in G.nodes():
        if n == apple_label:
            node_sizes.append(1600)
        elif n in first_order:
            node_sizes.append(1100)
        else:
            node_sizes.append(700)
        node_colors.append("#ffffff")

    edge_colors, edge_widths = [], []
    for u, v, d in G.edges(data=True):
        imp = float(d.get("importance", 0.0))
        edge_colors.append(blue_to_red(imp))
        edge_widths.append(0.3 + 1.5 * imp)

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, arrows=False)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors,
                           edgecolors="#1f2937", linewidths=1.0)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_color="#111827")

    plt.tight_layout()
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()


# --------------------- main ---------------------
def main():
    ensure_dirs()

    nodes, edges = load_rf_graph(INPUT_JSON)
    id2label = {n["id"]: n.get("data", {}).get("label", n["id"]) for n in nodes}
    label2id = {v: k for k, v in id2label.items()}

    # Resolve Apple label robustly
    apple_label = APPLE_LABEL_DEFAULT if APPLE_LABEL_DEFAULT in label2id else \
                  next((l for l in label2id if "apple" in l.lower()), APPLE_LABEL_DEFAULT)

    _, _, pair2imp = build_indexes(nodes, edges)

    # Scores & selection
    direct_scores, effective_scores, best_connector = compute_scores(apple_label, pair2imp)
    # select_nodes adds Apple automatically
    selected, top_overall, top_second_only = select_nodes(apple_label, direct_scores, effective_scores, best_connector)

    # Build subgraph and layout (with Apple fixed at (0,0) using initial pos)
    G, pos = build_label_graph(selected, pair2imp, apple_label)

    # Export simplified JSON
    rf = to_reactflow(G, pos)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rf, f, indent=2, ensure_ascii=False)

    # Plot
    plot_graph(G, pos, OUT_PNG, apple_label)

    print(f"Simplified graph written:\n  JSON → {OUT_JSON}\n  PNG  → {OUT_PNG}")
    print(f"Top-10 overall: {top_overall}")
    print(f"Top-5 second-order-only: {top_second_only}")


if __name__ == "__main__":
    main()
