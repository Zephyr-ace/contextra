promptNodeExtractor = """"""
promptEdgeExtractor =
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