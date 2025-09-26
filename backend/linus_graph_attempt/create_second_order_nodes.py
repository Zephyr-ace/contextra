import os
import re
import json
from typing import List, Dict
from openai import OpenAI

# ---------------------- CONFIG ----------------------
OPENAI_API_KEY = ""
MODEL_NAME = "gpt-5"                         # use "gpt-4o" if 5 is unavailable

REL_INPUT = "backend/linus_graph_attempt/apple_relationships.json"
OUT_DIR    = "backend/linus_graph_attempt/second_order_nodes"
TOP_K      = 30              # take 30 most important Apple→X connections
TARGET_N   = "between 5 and 15"           # instruction text only (model will return ~10)

# ----------------------------------------------------
client = OpenAI(api_key=OPENAI_API_KEY)
os.makedirs(OUT_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")

def clip(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[:n-1] + "…"

def load_top_targets(path: str, k: int) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Robustness: accept either a list of edges or an object with "edges"
    edges = data.get("edges", data) if isinstance(data, dict) else data
    # filter out malformed
    edges = [
        e for e in edges
        if isinstance(e, dict) and e.get("target_node") and isinstance(e.get("importance_score", 0), (int, float))
    ]
    # sort desc by importance
    edges.sort(key=lambda e: float(e.get("importance_score", 0)), reverse=True)
    return edges[:k]

def build_prompt(target: str, rel_type: str, evidence: str, score: float) -> str:
    return f"""
You are a research specialist with deep domain knowledge. Do NOT browse the web.
Using only your trained knowledge, identify the most important entities that have a
**direct and strong causal impact** on **{target}**.

Context from a prior Apple→{target} extraction:
- relationship_type: {rel_type or "unknown"}
- evidence_text: "{clip(evidence or "", 160)}"
- importance_score: {score:.2f}

ENTITIES TO FIND
- Companies (suppliers, competitors, partners, contractors)
- Sectors/Industries
- Products or Services
- Regulators / Institutions
- Countries / Regions
- Key People (executives, regulators, founders, political figures)
- Events (wars, sanctions, major court rulings)

RULES
• Focus ONLY on entities with clear, significant causal influence on {target}
  (avoid weak correlations or mere co-mentions).
• Prioritize the highest impact entities; return the most important ones FIRST.
• Deduplicate by canonical name.
• EXCLUDE Apple / Apple Inc. from results, unless absolutely unavoidable.
• Aim for around {TARGET_N} entities total across multiple categories.

OUTPUT (STRICT)
Return ONLY a valid JSON object with a single key "nodes" whose value is an array of objects.
Each object must include exactly:
- "title" (string)
- "category" (one of: "Company", "Product/Service", "Sector", "Regulation", "Country", "Person", "Event")
- "short_description" (≤20 words)

No markdown, no commentary — JSON object with a "nodes" array only.
"""

def ask_gpt_for_entities(target: str, rel_type: str, evidence: str, score: float) -> List[Dict]:
    prompt = build_prompt(target, rel_type, evidence, score)
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You extract entities precisely and return strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=1,
    )
    content = resp.choices[0].message.content
    try:
        obj = json.loads(content)
        nodes = obj.get("nodes", [])
        cleaned = []
        allowed = {"Company","Product/Service","Sector","Regulation","Country","Person","Event"}
        for n in nodes:
            title = (n.get("title") or "").strip()
            cat   = (n.get("category") or "").strip()
            desc  = clip(n.get("short_description") or "", 120)
            if not title or cat not in allowed:
                continue
            # exclude Apple variants explicitly
            if re.search(r"\bapple(\s+inc)?\b", title.lower()):
                continue
            cleaned.append({"title": title, "category": cat, "short_description": desc})
        return cleaned
    except Exception as e:
        print(f"[WARN] JSON parse failed for {target}: {e}\nRaw: {content[:300]}...")
        return []

def main():
    # 1) Load top-30 targets from Apple relationships
    top_edges = load_top_targets(REL_INPUT, TOP_K)

    for edge in top_edges:
        target = edge.get("target_node")
        rel_type = edge.get("relationship_type")
        evidence = edge.get("evidence_text")
        score = float(edge.get("importance_score", 0))

        print(f"→ Expanding: {target} (score {score:.2f})")

        nodes = ask_gpt_for_entities(target, rel_type, evidence, score)

        out_path = os.path.join(OUT_DIR, f"{sanitize_filename(target)}.json")
        payload = {"source": target, "nodes": nodes}

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"   Saved {len(nodes)} entities → {out_path}")

if __name__ == "__main__":
    main()
