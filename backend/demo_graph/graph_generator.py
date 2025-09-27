"""
Graph Generation System for Apple Deep Research
Uses existing extractor and OpenAI modules to create knowledge graph
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_extractor import EnhancedExtractor
from summarizer import DataSummarizer
from graph_components.Node import Node
from graph_components.Edge import Edge
import json
from typing import List, Dict, Any


class AppleGraphGenerator:
    def __init__(self):
        """Initialize the graph generator"""
        self.target = "Apple"
        self.summarizer = DataSummarizer()
        self.extractor = EnhancedExtractor(target=self.target)
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

    def generate_graph(self) -> Dict[str, Any]:
        """
        Generate the complete knowledge graph from Apple research data
        Uses the new pipeline: O3 Summary -> Entity Extraction -> Graph

        Returns:
            dict: Complete graph structure with nodes and edges
        """
        print("Starting enhanced graph generation for Apple...")

        # Step 1: Create concise summary using O3
        print("Step 1: Creating concise summary with O3...")
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache", "apple_deepresearch.txt")

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Research data not found at: {data_path}")

        summary_result = self.summarizer.summarize_research_data(data_path, self.target)

        if "error" in summary_result:
            raise Exception(f"Summarization failed: {summary_result['error']}")

        summary_text = summary_result["summary_text"]
        print(f"Created summary ({len(summary_text)} characters)")

        # Step 2: Save summary to cache
        print("Step 2: Saving summary to cache...")
        self.extractor.save_summary_cache(summary_text)

        # Step 3: Extract nodes and edges from summary
        print("Step 3: Extracting nodes and edges from summary...")
        nodes, edges = self.extractor.extract_from_summary(summary_text)

        self.nodes = nodes
        self.edges = edges

        print(f"Extracted {len(nodes)} nodes and {len(edges)} edges")

        # Step 4: Convert to JSON-serializable format
        graph_data = self._create_graph_structure()

        # Add summary info to metadata
        graph_data["metadata"]["summary_info"] = {
            "model_used": summary_result["model_used"],
            "summary_length": len(summary_text),
            "summary_type": summary_result.get("summary_type", "enhanced")
        }

        return graph_data

    def _create_graph_structure(self) -> Dict[str, Any]:
        """Create a structured graph representation"""

        # Convert nodes to dictionary format
        nodes_data = []
        for i, node in enumerate(self.nodes):
            node_dict = {
                "id": i,
                "name": node.name,
                "type": node.type,
                "description": node.description,
                "aliases": node.aliases if hasattr(node, 'aliases') else []
            }
            nodes_data.append(node_dict)

        # Convert edges to dictionary format with node IDs
        edges_data = []
        for edge in self.edges:
            # Find source and target node IDs
            source_id = self._find_node_id(edge.start.name)
            target_id = self._find_node_id(edge.end.name)

            if source_id is not None and target_id is not None:
                edge_dict = {
                    "source": source_id,
                    "target": target_id,
                    "title": edge.title,
                    "description": edge.description,
                    "importance_score": edge.importance_score
                }
                edges_data.append(edge_dict)

        # Create graph statistics
        stats = {
            "total_nodes": len(nodes_data),
            "total_edges": len(edges_data),
            "node_types": self._get_node_type_distribution(),
            "avg_importance_score": self._calculate_avg_importance()
        }

        # Complete graph structure
        graph_structure = {
            "target": self.target,
            "metadata": {
                "generated_by": "AppleGraphGenerator",
                "data_source": "apple_deepresearch.txt",
                "statistics": stats
            },
            "nodes": nodes_data,
            "edges": edges_data,
            "graph_format": "json"
        }

        return graph_structure

    def _find_node_id(self, node_name: str) -> int:
        """Find the ID of a node by its name"""
        for i, node in enumerate(self.nodes):
            if node.name.lower() == node_name.lower():
                return i
            # Check aliases too
            if hasattr(node, 'aliases') and node.aliases:
                for alias in node.aliases:
                    if alias.lower() == node_name.lower():
                        return i
        return None

    def _get_node_type_distribution(self) -> Dict[str, int]:
        """Get distribution of node types"""
        type_counts = {}
        for node in self.nodes:
            node_type = node.type
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        return type_counts

    def _calculate_avg_importance(self) -> float:
        """Calculate average importance score of edges"""
        if not self.edges:
            return 0.0
        total_score = sum(edge.importance_score for edge in self.edges)
        return round(total_score / len(self.edges), 3)

    def save_graph_json(self, graph_data: Dict[str, Any], output_path: str):
        """Save graph to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        print(f"Graph saved to: {output_path}")

    def get_graph_summary(self, graph_data: Dict[str, Any]) -> str:
        """Generate a text summary of the graph"""
        stats = graph_data["metadata"]["statistics"]

        summary = f"""
Apple Knowledge Graph Summary:
=============================
- Target Entity: {graph_data['target']}
- Total Nodes: {stats['total_nodes']}
- Total Edges: {stats['total_edges']}
- Average Edge Importance: {stats['avg_importance_score']}

Node Type Distribution:
{chr(10).join(f"  - {type_name}: {count}" for type_name, count in stats['node_types'].items())}

Key Entities (First 10 nodes):
{chr(10).join(f"  - {node['name']} ({node['type']})" for node in graph_data['nodes'][:10])}
        """

        return summary


def main():
    """Main function to generate the Apple knowledge graph"""
    print("=== Apple Knowledge Graph Generator ===")

    # Initialize generator
    generator = AppleGraphGenerator()

    # Generate the graph
    try:
        graph_data = generator.generate_graph()

        # Save to JSON file
        output_path = "backend/demo_graph/apple_graph.json"
        generator.save_graph_json(graph_data, output_path)

        # Print summary
        summary = generator.get_graph_summary(graph_data)
        print(summary)

        # Also save summary to file
        summary_path = "backend/demo_graph/graph_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        print(f"\nGraph generation complete!")
        print(f"JSON graph: {output_path}")
        print(f"Summary: {summary_path}")

    except Exception as e:
        print(f"Error during graph generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()