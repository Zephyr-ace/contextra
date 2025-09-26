import os
import re
import json
import math
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any, Optional

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = "backend/linus_graph_attempt"
APPLE_NODES_FILE = os.path.join(BASE, "apple_nodes.json")
APPLE_REL_FILE   = os.path.join(BASE, "apple_relationships.json")
SEC_NODES_DIR    = os.path.join(BASE, "second_order_nodes_with_aliases")  # input
SEC_EDGES_DIR    = os.path.join(BASE, "second_order_edges")               # optional input
OUT_FILE         = os.path.join(BASE, "general_2nd_degree_apple_graph.json")
# ──────────────────────────────────────────────────────────────────────────────

APPLE_CANON = "Apple Inc."  # central node canonical label


# ── Utilities ─────────────────────────────────────────────────────────────────
def norm(s: str) -> str:
    """Normalize a string for alias lookups (case-insensitive, strip punctuation & company suffixes)."""
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[\W_]+", " ", s)  # non-letters to space
    s = re.sub(r"\b(the|and|of|co|corp|inc|ltd|llc|plc|company|corporation|limited|sa|ag|nv|bv)\b", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s.lower()

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_json_files(folder: str) -> List[str]:
    if not os.path.isdir(folder):
        return []
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".json")]

def sorted_pair(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


# ── Canonicalization via Aliases ──────────────────────────────────────────────
def build_alias_index(apple_nodes_path: str, sec_nodes_dir: str) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Returns:
      alias2canon: maps normalized alias -> canonical name
      canon2aliases: canonical -> list of aliases (incl. canonical)
    """
    alias2canon: Dict[str, str] = {}
    canon2aliases: Dict[str, List[str]] = defaultdict(list)

    # 1) Seed with apple_nodes.json (authoritative)
    try:
        apple_nodes = load_json(apple_nodes_path)
        for n in apple_nodes:
            canon = (n.get("name") or "").strip()
            if not canon:
                continue
            aliases = set([canon])
            for a in n.get("aliases", []) or []:
                if a:
                    aliases.add(a.strip())
            for a in sorted(aliases):
                alias2canon[norm(a)] = canon
            canon2aliases[canon] = sorted(aliases)
    except Exception:
        pass

    # 2) Learn from second_order_nodes_with_aliases (their "Aliases" may include canonical names)
    for path in list_json_files(sec_nodes_dir):
        try:
            blob = load_json(path)
            nodes = blob.get("nodes", []) if isinstance(blob, dict) else (blob if isinstance(blob, list) else [])
            for n in nodes:
                title = (n.get("title") or "").strip()
                if not title:
                    continue
                aliases_here = set([title])
                for a in n.get("Aliases", []) or []:
                    if a:
                        aliases_here.add(a.strip())
                # If any alias_here maps to a known canonical, map ALL to that canonical
                mapped_canon = None
                for a in aliases_here:
                    c = alias2canon.get(norm(a))
                    if c:
                        mapped_canon = c
                        break
                # If still none, we don't invent; just add self-maps so repeats collapse
                canon = mapped_canon or title
                for a in aliases_here:
                    alias2canon.setdefault(norm(a), canon)
                if canon not in canon2aliases:
                    canon2aliases[canon] = sorted(aliases_here)
                else:
                    canon2aliases[canon] = sorted(set(canon2aliases[canon]).union(aliases_here))
        except Exception:
            continue

    # Guarantee Apple canonical exists
    if APPLE_CANON not in canon2aliases:
        canon2aliases[APPLE_CANON] = [APPLE_CANON]
        alias2canon[norm(APPLE_CANON)] = APPLE_CANON

    return alias2canon, canon2aliases


def canonicalize(name: str, alias2canon: Dict[str, str]) -> str:
    return alias2canon.get(norm(name or ""), name or "")


# ── Graph aggregation ─────────────────────────────────────────────────────────
def add_edge(agg: Dict[Tuple[str, str], Dict[str, Any]],
             a: str, b: str,
             relation: Dict[str, Any]) -> None:
    """
    Aggregates an undirected edge between a and b.
    relation = {relationship_type, evidence_text, importance_score, source_tag}
    """
    if not a or not b or a == b:
        return
    key = sorted_pair(a, b)
    bucket = agg.setdefault(key, {
        "pair": key,
        "relations": [],
        "max_importance": 0.0,
        "sum_importance": 0.0,
        "count": 0,
        "type_counts": Counter(),
    })
    bucket["relations"].append(relation)
    imp = float(relation.get("importance_score", 0.0) or 0.0)
    bucket["max_importance"] = max(bucket["max_importance"], imp)
    bucket["sum_importance"] += imp
    bucket["count"] += 1
    rtype = (relation.get("relationship_type") or "").strip()
    if rtype:
        bucket["type_counts"][rtype] += 1


def load_first_order_edges(path: str, alias2canon: Dict[str, str]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    agg: Dict[Tuple[str, str], Dict[str, Any]] = {}
    try:
        data = load_json(path)
        edges = data.get("edges", data) if isinstance(data, dict) else data
        for e in edges:
            src = canonicalize(e.get("source_node") or APPLE_CANON, alias2canon)
            tgt = canonicalize(e.get("target_node") or "", alias2canon)
            if not tgt:
                continue
            add_edge(agg, src, tgt, {
                "relationship_type": e.get("relationship_type"),
                "evidence_text": e.get("evidence_text"),
                "importance_score": e.get("importance_score"),
                "source_tag": "apple_relationships"
            })
    except Exception:
        pass
    return agg


def load_second_order_edges(folder: str, alias2canon: Dict[str, str]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    agg: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for path in list_json_files(folder):
        try:
            edges = load_json(path)
            if isinstance(edges, dict):
                # Some pipelines save {"edges":[...]} — support both
                edges = edges.get("edges", [])
            if not isinstance(edges, list):
                continue
            for e in edges:
                src = canonicalize(e.get("source_node") or "", alias2canon)
                tgt = canonicalize(e.get("target_node") or "", alias2canon)
                if not src or not tgt:
                    continue
                add_edge(agg, src, tgt, {
                    "relationship_type": e.get("relationship_type"),
                    "evidence_text": e.get("evidence_text"),
                    "importance_score": e.get("importance_score"),
                    "source_tag": f"second_order:{os.path.basename(path)}",
                })
        except Exception:
            continue
    return agg


# ── Layout (simple radial: Apple center, L1 ring, L2 ring) ───────────────────
def make_layout(nodes: List[str],
                apple_neighbors: List[Tuple[str, float]],
                edges_agg: Dict[Tuple[str, str], Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Returns positions {name: {"x":..., "y":...}}
    - Apple at (0,0)
    - Level 1 (neighbors of Apple) on ring R1 sorted by importance
    - Level 2 on ring R2 near their strongest Level-1 neighbor
    """
    pos: Dict[str, Dict[str, float]] = {}
    pos[APPLE_CANON] = {"x": 0.0, "y": 0.0}

    # L1 ring
    R1 = 600.0
    R2 = 1100.0
    n1 = len(apple_neighbors)
    for i, (name, _imp) in enumerate(apple_neighbors):
        angle = 2 * math.pi * i / max(1, n1)
        pos[name] = {"x": R1 * math.cos(angle), "y": R1 * math.sin(angle)}

    # Identify L2 candidates = nodes not Apple and not in L1
    l1_set = {n for n, _ in apple_neighbors}
    others = [n for n in nodes if n not in l1_set and n != APPLE_CANON]

    # Helper to get max importance to any L1 neighbor
    def best_anchor(nm: str) -> Tuple[str, float]:
        best = ("", -1.0)
        for l1, _ in apple_neighbors:
            key = sorted_pair(nm, l1)
            bucket = edges_agg.get(key)
            if not bucket:
                continue
            imp = bucket["max_importance"]
            if imp > best[1]:
                best = (l1, imp)
        return best

    # Cluster around best L1 anchor
    cluster_children: Dict[str, List[str]] = defaultdict(list)
    for nm in others:
        anchor, _ = best_anchor(nm)
        if anchor:
            cluster_children[anchor].append(nm)
        else:
            # If totally disconnected from L1 (unlikely), place on R2 anyway
            cluster_children["__misc__"].append(nm)

    # Place per cluster
    for anchor, kids in cluster_children.items():
        base_angle = 0.0
        if anchor in pos:
            ax, ay = pos[anchor]["x"], pos[anchor]["y"]
            base_angle = math.atan2(ay, ax)
        k = len(kids)
        spread = max(1, k)
        for i, nm in enumerate(kids):
            a = base_angle + (i - (k - 1) / 2.0) * (math.pi / max(2, k))  # local spread
            pos[nm] = {"x": R2 * math.cos(a), "y": R2 * math.sin(a)}

    return pos


# ── ReactFlow conversion ──────────────────────────────────────────────────────
def edge_style_from_importance(imp: float) -> Dict[str, Any]:
    # Stroke width 2..8
    w = max(2, min(8, int(round(2 + 6 * float(imp or 0.0)))))
    return {"strokeWidth": w}

def to_reactflow(nodes_set: List[str],
                 edges_agg: Dict[Tuple[str, str], Dict[str, Any]]) -> Dict[str, Any]:
    # Compute L1 neighbors and importance for layout
    apple_neighbors: List[Tuple[str, float]] = []
    for (a, b), bucket in edges_agg.items():
        if APPLE_CANON in (a, b):
            other = b if a == APPLE_CANON else a
            apple_neighbors.append((other, bucket["max_importance"]))
    # Sort L1 by descending importance
    apple_neighbors.sort(key=lambda t: t[1], reverse=True)

    # Layout
    positions = make_layout(nodes_set, apple_neighbors, edges_agg)

    # Build nodes
    rf_nodes: List[Dict[str, Any]] = []
    for name in nodes_set:
        rf_nodes.append({
            "id": slug(name),
            "position": {"x": positions.get(name, {}).get("x", 0.0), "y": positions.get(name, {}).get("y", 0.0)},
            "data": {"label": name},
            "type": "custom",
            "draggable": True,
        })

    # Build edges (undirected; normalized id & pair)
    rf_edges: List[Dict[str, Any]] = []
    for (a, b), bucket in edges_agg.items():
        if a == b:
            continue
        edge_id = f"{slug(a)}--{slug(b)}"
        # Summaries
        max_imp = bucket["max_importance"]
        avg_imp = (bucket["sum_importance"] / max(1, bucket["count"]))
        type_counts = {k: int(v) for k, v in bucket["type_counts"].items()}
        # Tooltip: short readable summary
        tooltip = f"Types: {', '.join([f'{t}({c})' for t,c in type_counts.items()])} | max={max_imp:.2f}, avg={avg_imp:.2f}"
        # Full relation list
        relations = []
        for r in bucket["relations"]:
            relations.append({
                "relationship_type": r.get("relationship_type"),
                "evidence_text": r.get("evidence_text"),
                "importance_score": r.get("importance_score"),
                "source_tag": r.get("source_tag"),
            })
        rf_edges.append({
            "id": edge_id,
            "source": slug(a),
            "target": slug(b),
            "type": "floating",
            "data": {
                "undirected": True,
                "tooltip": tooltip,
                "max_importance": max_imp,
                "avg_importance": avg_imp,
                "relationship_types": type_counts,
                "relations": relations,  # raw details
            },
            "style": edge_style_from_importance(max_imp),
        })

    return {"nodes": rf_nodes, "edges": rf_edges}


# ── Main build ────────────────────────────────────────────────────────────────
def main():
    # 1) Build alias indices
    alias2canon, canon2aliases = build_alias_index(APPLE_NODES_FILE, SEC_NODES_DIR)

    # 2) Aggregate edges
    agg: Dict[Tuple[str, str], Dict[str, Any]] = {}

    # 2a) Apple → first-order
    agg_first = load_first_order_edges(APPLE_REL_FILE, alias2canon)
    for k, v in agg_first.items():
        agg.setdefault(k, v)
        if agg[k] is not v:  # merge if key existed
            for r in v["relations"]:
                add_edge(agg, k[0], k[1], r)

    # 2b) Second-order edges (if available)
    if os.path.isdir(SEC_EDGES_DIR):
        agg_second = load_second_order_edges(SEC_EDGES_DIR, alias2canon)
        for k, v in agg_second.items():
            if k not in agg:
                agg[k] = v
            else:
                for r in v["relations"]:
                    add_edge(agg, k[0], k[1], r)

    # 3) Build full node set from aggregated edges
    node_names = set()
    for (a, b) in agg.keys():
        node_names.add(a)
        node_names.add(b)
    # Ensure Apple exists even if no edges (defensive)
    node_names.add(APPLE_CANON)

    # 4) Convert to ReactFlow JSON
    rf_graph = to_reactflow(sorted(node_names), agg)

    # 5) Save
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(rf_graph, f, indent=2, ensure_ascii=False)

    print(f"Wrote graph with {len(rf_graph['nodes'])} nodes and {len(rf_graph['edges'])} edges → {OUT_FILE}")


if __name__ == "__main__":
    main()
