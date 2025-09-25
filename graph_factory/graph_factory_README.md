# Graph Factory

The `graph_factory` builds and maintains the **Investment Graph** for a given stock or sector.  
It turns broad, unstructured input (deep research, filings, news) into a structured, expandable graph of **entities** and **relationships**. This graph forms the **foundation** for monitoring, impact tracing, and decisioning.

---

## Workflow

### 0. Input
- Broad information basis around the stock/sector (deep research, filings, news).
- Input is chunked into fragments for parallel analysis.

### 1. Initial Graph Construction (Fundament)
Goal: create a **small, focused graph** around the target stock/sector.

i. **Entity Extraction (per fragment)**  
- Extract entities (Pydantic models).  
- Node categories:  
  - `Company`  
  - `Product`  
  - `Person`  
  - `Event`  
  - `Regulation`  

ii. **Edge Creation (per fragment)**  
- For each pair of entities, a reasoning model proposes:  
  - `edge_type: str` (free-form, unconstrained)  
  - `connection_strength: {0.1=weak, 0.5=neutral, 0.9=strong}`  

iii. **Merge into Global Graph**  
- Local fragment-graphs are merged.  
- For each edge:  
  - Maintain `connection_strength` (aggregated)  
  - Track `edge_count` (number of fragment-level occurrences)

iv. **(Optional) Filter**  
- Prune irrelevant or low-signal nodes/edges.

---

### 2. Iterative Agentic Refinement
A crew of AI agents expands the graph in multiple iterations (parameterized, default = 2).

1. **Node Prioritization**  
   - Select nodes most relevant to the portfolio component (reasoning model).  

2. **Targeted Expansion (per node, parallel)**  
   - Perform multiple searches for new information.  
   - Extract entities and edges from new data.  
   - Integrate into the global graph.  
   - (Optional) Filter again for quality.  

3. **Repeat** until the iteration budget is reached.

---

## Edge Weight Calculation

After the global graph is constructed:

1. Fetch **co-occurrence statistics** from GDELT for each node pair.  
2. For each edge, compute final weight:

