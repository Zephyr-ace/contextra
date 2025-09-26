import os
import json
from openai import OpenAI

# ⚠️ Hardcoded API key (local use only!)
API_KEY = ""

# Initialize OpenAI client with hardcoded key
client = OpenAI(api_key=API_KEY)

# Input/output file paths
INPUT_FILE = "backend/linus_graph_attempt/apple_nodes.json"
OUTPUT_FILE = "backend/linus_graph_attempt/apple_relationships.json"


def build_prompt(node):
    return f"""
You are given information about Apple Inc. and another entity. Extract a structured relationship
between Apple Inc. (source) and the entity (target). Follow the schema strictly.

Entity Info:
Name: {node['name']}
Aliases: {', '.join(node.get('aliases', []))}
Description: {node['description']}
Type: {node['type']}

Return ONLY valid JSON with:
- source_node (always "Apple Inc.")
- target_node (entity name)
- relationship_type (one of: supplies_to, competes_with, regulates, customer_of, partner_with)
- evidence_text (verbatim, ≤100 chars, from the description above)
- importance_score (float 0.00–1.00, per provided rules)

RULES:
• Only extract relationships with direct causal relevance.
• Do not include mere co-mentions.
"""


def main():
    # Load input JSON
    with open(INPUT_FILE, "r") as f:
        nodes = json.load(f)

    results = []
    
    for node in nodes:
        if node["name"] == "Apple Inc.":
            continue  # Skip self

        prompt = build_prompt(node)

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # safer model name than "gpt-4.0"
            messages=[
                {"role": "system", "content": "You are a precise JSON relationship extractor."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}  # ensures JSON response
        )

        try:
            result = json.loads(response.choices[0].message.content)
            results.append(result)
        except Exception as e:
            print(f"Error parsing JSON for node {node['name']}: {e}")

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} relationships to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
