promptNodeExtractor = """TASK — NODE EXTRACTION  
From the provided text, extract all relevant entities as **nodes**.  
Allowed node categories: Company, Product/Service, Sector, Regulation, Country, Person, Event.  
For each node, return:  
- title (string)  
- category (one of the allowed categories)  
- short description (≤20 words)  

RULES:  
• Only include entities with clear and meaningful relevance to the text.  
• Deduplicate by canonical name (e.g., “Apple” → “Apple Inc.”).  
• Skip vague or generic mentions.  """



promptEdgeExtractor = """TASK — EDGE EXTRACTION  
Using the node list {node_titles}, extract **explicit causal relationships** between pairs of nodes.  
For each edge, return:  
- source_node (must match {node_titles})  
- target_node (must match {node_titles})  
- relationship_type (e.g., supplies_to, competes_with, regulates, customer_of, partner_with)  
- evidence_text (≤100 chars, verbatim from source text)  
- importance_score (float between 0.5–1; 0.5 = weak, 0.75 = neutral, 1 = very strong)  

RULES:  
• Only extract relationships with **direct causal relevance**.  
• Do not include mere co-mentions.  
• Exclude connections weaker than 0.5.  
• If symmetric (e.g., competes_with, partners_with), importance_score must apply equally both ways.  

GOAL:  
Produce a clean set of nodes and strong edges that form a simple, causality-focused graph of the text."""


promptDeepresearch = """You are a research specialist building a context graph around {target}.  
Your task is to identify the most important entities that have a **direct and strong causal impact** on {target}.  

ENTITIES TO FIND  
- Companies (suppliers, competitors, partners, contractors)  
- Sectors/Industries  
- Products or Services  
- Regulators / Institutions  
- Countries / Regions  
- Key People (executives, regulators, founders, political figures)  

RULES  
• Focus only on entities with **clear, significant causal influence** on {target} (not just mentions or weak correlations).  
• Weigh entities by **relevance and impact strength**; prioritize the biggest drivers.  
• Output should highlight the **most important entities first** — those with the largest potential effect on {target}.  

GOAL  
Return a structured list of high-impact entities to serve as nodes for a graph around {target}. This graph will later be used to trace reaction chains and measure event impacts.  

"""