# backend/linus_graph_attempt/add_aliases_to_second_order_nodes.py

import os
import re
import json
from typing import List, Dict, Any
from openai import OpenAI

# ── Config ─────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = ""
MODEL_NAME = "gpt-4o"

APPLE_NODES_FILE = "backend/linus_graph_attempt/apple_nodes.json"
IN_DIR  = "backend/linus_graph_attempt/second_order_nodes"
OUT_DIR = "backend/linus_graph_attempt/second_order_nodes_with_aliases"
# ───────────────────────────────────────────────────────────────────────────────

client = OpenAI(api_key=OPENAI_API_KEY)
os.makedirs(OUT_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")

def clip(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[:n-1] + "…"

def load_apple_nodes(path: str) -> List[Dict[str, Any]]:
    """Returns a list of dicts: {"name": str, "aliases": [..], "type": str, "description": str}"""
    with open(path, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    # normalize
    out = []
    for n in nodes:
        out.append({
            "name": n.get("name", "").strip(),
            "aliases": [a.strip() for a in (n.get("aliases") or []) if a and a.strip()],
            "type": n.get("type", "").strip(),
            "description": (n.get("description") or "").strip(),
        })
    return out

def build_candidate_block(apple_nodes: List[Dict[str, Any]]) -> str:
    """
    Produce a compact list of all Apple-network entities for GPT to choose from.
    We will require GPT to only return strings present here.
    """
    lines = []
    for n in apple_nodes:
        nm = n["name"]
        als = ", ".join(n["aliases"]) if n["aliases"] else "(none)"
        lines.append(f"- {nm} | aliases: {als}")
    return "\n".join(lines)

def build_prompt(target_node: Dict[str, Any], candidates_block: str) -> str:
    """
    Ask GPT to decide if target_node is the same real-world entity as any of the
    Apple-list entities. If so, return the canonical name FIRST and include ALL of
    that entity's names (canonical + aliases) exactly as they appear in the list.
    """
    return f"""
You will receive a TARGET entity and a fixed list of CANDIDATE entities (canonical names with aliases).
Decide if the TARGET refers to the SAME real-world entity as ANY candidate.

TARGET
- title: {target_node.get("title")}
- category: {target_node.get("category")}
- short_description: "{clip(target_node.get('short_description',''), 220)}"

CANDIDATES (canonical name | aliases):
{candidates_block}

MATCHING RULES
• Only consider exact matches, common abbreviations, or well-known brand/company alias mappings.
• Be conservative: if unsure, return no matches.
• If TARGET matches a candidate, return the candidate's **canonical name FIRST** followed by
  ALL its aliases **exactly as written in the candidate list**.
• If multiple candidates match (rare), include each matched candidate the same way.
• If TARGET does not match any candidate, return an empty list.

OUTPUT (STRICT)
Return ONLY valid JSON:
{{
  "Aliases": ["<canonical/alias strings from the list above>", ...]
}}
- Use strings ONLY from the candidate list. Do not invent new variants.
- If no match: "Aliases": []
"""

def ask_gpt_for_aliases(target_node: Dict[str, Any], candidates_block: str) -> List[str]:
    prompt = build_prompt(target_node, candidates_block)
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are an entity resolution assistant. Output strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    try:
        obj = json.loads(raw)
        aliases = obj.get("Aliases", [])
        # sanitize to list of strings
        if isinstance(aliases, list):
            aliases = [str(a).strip() for a in aliases if isinstance(a, (str,))]
            return aliases
        return []
    except Exception:
        # If the model fails JSON mode for any reason, return no aliases.
        return []

def load_second_order(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Accept legacy formats: either {"source":..., "nodes":[...]} or a plain list
    if isinstance(data, dict) and "nodes" in data:
        return {"source": data.get("source"), "nodes": data.get("nodes", [])}
    elif isinstance(data, list):
        return {"source": os.path.splitext(os.path.basename(path))[0], "nodes": data}
    else:
        return {"source": None, "nodes": []}

def main():
    # Load Apple canonical list (this is what aliases MUST come from)
    apple_nodes = load_apple_nodes(APPLE_NODES_FILE)
    candidates_block = build_candidate_block(apple_nodes)

    in_files = [f for f in os.listdir(IN_DIR) if f.lower().endswith(".json")]

    for fname in in_files:
        in_path  = os.path.join(IN_DIR, fname)
        out_path = os.path.join(OUT_DIR, fname)

        payload = load_second_order(in_path)
        source = payload.get("source")
        nodes  = payload.get("nodes", [])

        if not nodes:
            # write through an empty shell to keep parity
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"source": source, "nodes": []}, f, indent=2, ensure_ascii=False)
            print(f"[SKIP] {fname}: no nodes")
            continue

        print(f"Resolving aliases for: {source}  ({len(nodes)} nodes)")

        enriched = []
        for node in nodes:
            # Copy over original node
            new_node = dict(node)
            # Query GPT to resolve aliases against the Apple list
            aliases = ask_gpt_for_aliases(node, candidates_block)
            new_node["Aliases"] = aliases  # always add the key (possibly empty)
            enriched.append(new_node)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"source": source, "nodes": enriched}, f, indent=2, ensure_ascii=False)

        print(f"   → Saved: {out_path}")

if __name__ == "__main__":
    main()
