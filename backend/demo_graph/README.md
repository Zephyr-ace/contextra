# Apple Knowledge Graph Demo - Enhanced Pipeline

This demo creates a knowledge graph from Apple deep research data using an enhanced pipeline with O3 reasoning model.

## Overview

The enhanced demo performs these steps:
1. **O3 Concise Summarization**: Uses O3 reasoning model to create a focused summary of the most important entities and their causal impact on Apple (includes goal repetition)
2. **Summary Caching**: Saves the concise summary as cache in demo_graph directory
3. **Enhanced Entity Extraction**: Extracts nodes and edges from the summary (not raw research) using existing modules
4. **JSON Export**: Outputs the complete graph in JSON format
5. **Visualization**: Creates NetworkX + Matplotlib visualizations

## Files

- `main.py` - Main orchestration script
- `summarizer.py` - O3 concise summarization with goal repetition
- `enhanced_extractor.py` - Enhanced extractor that works with summary cache
- `graph_generator.py` - Enhanced graph creation using new pipeline
- `visualizer.py` - NetworkX + Matplotlib visualization
- `requirements.txt` - Python dependencies

## Cache Files Generated

- `apple_summary_cache.txt` - Concise O3 summary cache
- `apple_nodes.json` - Extracted nodes cache
- `apple_edges.json` - Extracted edges cache

## Usage

1. Ensure OpenAI API key is set:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the complete demo:
   ```bash
   python main.py
   ```

   Or run individual components:
   ```bash
   python summarizer.py      # Just summarization
   python graph_generator.py # Just graph generation
   python visualizer.py      # Just visualization
   ```

## Output

- `apple_summary.json` - Research data summary
- `apple_graph.json` - Complete graph in JSON format
- `graph_summary.txt` - Human-readable summary
- `visualizations/` - NetworkX + Matplotlib plots
  - `apple_full_graph.png` - Complete network visualization
  - `apple_companies_subgraph.png` - Company entities focus
  - `apple_graph_statistics.png` - Statistics charts

## Graph Structure

The JSON graph follows this structure:
```json
{
  "target": "Apple",
  "metadata": {
    "generated_by": "AppleGraphGenerator",
    "data_source": "apple_deepresearch.txt",
    "statistics": { ... }
  },
  "nodes": [
    {
      "id": 0,
      "name": "Node Name",
      "type": "Company|Person|Product|etc",
      "description": "Description",
      "aliases": [...]
    }
  ],
  "edges": [
    {
      "source": 0,
      "target": 1,
      "title": "Relationship Title",
      "description": "Relationship Description",
      "importance_score": 0.75
    }
  ]
}
```