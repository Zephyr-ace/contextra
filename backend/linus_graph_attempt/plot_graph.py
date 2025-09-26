# backend/linus_graph_attempt/plot_general_2nd_degree_apple_graph_multi.py

import os
import json
import math
import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.patches import Patch

INPUT_FILE = "backend/linus_graph_attempt/general_2nd_degree_apple_graph.json"
PLOTS_DIR  = "backend/linus_graph_attempt/plots"
APPLE_LABEL = "Apple Inc."  # center this node

# Generate 10 plots with these scale multipliers (applied to final coordinates)
SCALE_FACTORS = [1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12]

# -------------------- I/O --------------------
def ensure_dirs():
    os.makedirs(PLOTS_DIR, exist_ok=True)

def load_graph(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    return nodes, edges

# ----------------- Graph building -----------------
def build_nx_graph(nodes, edges):
    G = nx.Graph()
    id2label = {}
    id2pos   = {}

    for n in nodes:
        nid = n["id"]
        label = n.get("data", {}).get("label", nid)
        id2label[nid] = label
        pos = n.get("position", {})
        id2pos[nid] = (float(pos.get("x", 0.0)), float(pos.get("y", 0.0)))
        G.add_node(nid, label=label)

    for e in edges:
        s, t = e["source"], e["target"]
        ed = e.get("data", {}) or {}
        imp = ed.get("max_importance")
        if imp is None:
            rels = ed.get("relations", [])
            imp = max([float(r.get("importance_score", 0.0) or 0.0) for r in rels], default=0.0)
        G.add_edge(s, t, importance=float(imp))

    return G, id2label, id2pos

def find_apple_node(id2label):
    for nid, lbl in id2label.items():
        if lbl == APPLE_LABEL:
            return nid
    for nid, lbl in id2label.items():
        if "apple" in lbl.lower():
            return nid
    return None

# -------------- Layout & Styling helpers --------------
def piecewise_blue_to_red(value):
    """Importance in [0,1] -> color (≤0.6 stays very blue, → red at 1.0)."""
    v = max(0.0, min(1.0, float(value)))
    if v < 0.6:
        t = (v / 0.6) * 0.2
    else:
        t = 0.2 + ((v - 0.6) / 0.4) * 0.8
    cmap = mcolors.LinearSegmentedColormap.from_list("blue_red", ["#2563eb", "#ef4444"])
    return cmap(t)

def compute_layout(G, id2pos, apple_id):
    """Refine with a force layout to reduce overlap; Apple fixed at (0,0)."""
    init_pos = {nid: (float(x), float(y)) for nid, (x, y) in id2pos.items()}
    if apple_id is None:
        return nx.spring_layout(G, k=180, iterations=800, seed=42)

    init_pos[apple_id] = (0.0, 0.0)
    pos = nx.spring_layout(
        G,
        k=180,
        iterations=800,
        seed=42,
        pos=init_pos,
        fixed=[apple_id],
        weight="importance"
    )
    pos[apple_id] = (0.0, 0.0)
    return pos

def degree_bucket(d):
    if d <= 1:  return "1"
    if d == 2:  return "2"
    if d == 3:  return "3"
    if d == 4:  return "4"
    if 5 <= d <= 8:  return "5–8"
    if 9 <= d <= 10: return "9–10"
    return "10+"

def bucket_colors():
    random.seed(1234)
    buckets = ["1","2","3","4","5–8","9–10","10+"]
    cols = {}
    for b in buckets:
        h = random.random()
        cols[b] = mcolors.hsv_to_rgb((h, 0.55, 0.95))
    return cols

def classify_layers(G, apple_id):
    """Return (first_order_set, second_order_set)."""
    if apple_id is None or apple_id not in G:
        return set(), set(G.nodes())
    first = set(G.neighbors(apple_id))
    second = set(G.nodes()) - first - {apple_id}
    return first, second

# ------------------- Drawing -------------------
def draw_graph_scaled(G, base_pos, id2label, apple_id, scale, out_path):
    # Scale positions
    pos = {n: (x*scale, y*scale) for n, (x, y) in base_pos.items()}

    # Layer classification for node sizing
    first_order, second_order = classify_layers(G, apple_id)

    # Node degree buckets -> colors
    bc = bucket_colors()
    node_colors = []
    node_sizes  = []
    labels = {nid: id2label.get(nid, nid) for nid in G.nodes()}

    for nid in G.nodes():
        d  = G.degree(nid)
        b  = degree_bucket(d)
        c  = bc[b]
        # 3-size scheme: Apple > first-order > second-order
        if nid == apple_id:
            node_sizes.append(1800)     # Apple largest
        elif nid in first_order:
            node_sizes.append(1100)     # first-order medium
        else:
            node_sizes.append(650)      # second-order smaller
        node_colors.append(c)

    # Edge styling (very thin)
    edge_colors = []
    edge_widths = []
    edge_alphas = []
    for _, _, data in G.edges(data=True):
        imp = float(data.get("importance", 0.0))
        edge_colors.append(piecewise_blue_to_red(imp))
        edge_widths.append(0.2 + 1.6 * imp)   # ~0.2 .. 1.8
        edge_alphas.append(0.85 if imp >= 0.6 else 0.55)

    # Figure
    plt.figure(figsize=(22, 16), dpi=220)
    ax = plt.gca()
    ax.set_axis_off()

    # Edges
    ec = nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, arrows=False)
    try:
        edge_colors_with_alpha = []
        for c, a in zip(edge_colors, edge_alphas):
            rgba = list(mcolors.to_rgba(c))
            rgba[3] = a
            edge_colors_with_alpha.append(rgba)
        ec.set_color(edge_colors_with_alpha)
    except Exception:
        pass

    # Nodes
    nx.draw_networkx_nodes(G, pos,
        node_size=node_sizes,
        node_color=node_colors,
        edgecolors="#2b2b2b",
        linewidths=0.9
    )

    # Labels (names only)
    nx.draw_networkx_labels(G, pos, labels=labels,
        font_size=7.2,
        font_color="#111827",
        verticalalignment="center",
        horizontalalignment="center",
    )

    # Legend for degree buckets
    legend_handles = [Patch(facecolor=bc[b], edgecolor="#2b2b2b", label=f"deg {b}")
                      for b in ["1","2","3","4","5–8","9–10","10+"]]
    plt.legend(handles=legend_handles, loc="lower left", fontsize=9, frameon=True)

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

def main():
    ensure_dirs()
    nodes, edges = load_graph(INPUT_FILE)
    G, id2label, id2pos = build_nx_graph(nodes, edges)
    apple_id = find_apple_node(id2label)

    # One refined layout, then export multiple scales
    base_pos = compute_layout(G, id2pos, apple_id)

    for s in SCALE_FACTORS:
        s_name = str(s).replace(".", "p")
        out_path = os.path.join(PLOTS_DIR, f"general_2nd_degree_apple_graph_x{s_name}.png")
        draw_graph_scaled(G, base_pos, id2label, apple_id, s, out_path)
        print(f"Saved plot → {out_path}")

if __name__ == "__main__":
    main()
