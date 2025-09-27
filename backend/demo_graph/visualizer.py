"""
Graph Visualization Module
Uses NetworkX and Matplotlib to create visual representations of the Apple knowledge graph
"""

import json
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import numpy as np
from typing import Dict, Any, List
import os


class GraphVisualizer:
    def __init__(self):
        """Initialize the graph visualizer"""
        self.graph = nx.DiGraph()
        self.node_colors = {
            'Company': '#FF6B6B',      # Red
            'Person': '#4ECDC4',       # Teal
            'Product/Service': '#45B7D1',  # Blue
            'Sector': '#96CEB4',       # Green
            'Regulator/Authority': '#FFEAA7',   # Yellow
            'Country': '#DDA0DD',      # Plum
            'Ecosystem': '#FFB347',    # Orange
            'Technology': '#87CEEB',   # Sky Blue
            'Legal Case': '#FF69B4',   # Hot Pink
            'Policy': '#32CD32',       # Lime Green
            'Default': '#D3D3D3'       # Light Gray
        }

    def load_graph_from_json(self, json_path: str) -> Dict[str, Any]:
        """Load graph data from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        return graph_data

    def create_networkx_graph(self, graph_data: Dict[str, Any]):
        """Create NetworkX graph from JSON data"""
        self.graph.clear()

        # Add nodes
        for node in graph_data['nodes']:
            self.graph.add_node(
                node['id'],
                name=node['name'],
                type=node['type'],
                description=node['description'][:50] + "..." if len(node['description']) > 50 else node['description'],
                full_description=node['description']
            )

        # Add edges
        for edge in graph_data['edges']:
            self.graph.add_edge(
                edge['source'],
                edge['target'],
                title=edge['title'],
                description=edge['description'],
                importance=edge['importance_score'],
                weight=edge['importance_score']
            )

        print(f"Created NetworkX graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

    def visualize_full_graph(self, output_path: str, figsize=(16, 12)):
        """Create a comprehensive visualization of the full graph"""
        fig, ax = plt.subplots(figsize=figsize)

        # Use spring layout for better node distribution
        pos = nx.spring_layout(self.graph, k=3, iterations=50, seed=42)

        # Get node colors based on type
        node_colors = [self.node_colors.get(
            self.graph.nodes[node]['type'],
            self.node_colors['Default']
        ) for node in self.graph.nodes()]

        # Get edge weights for thickness
        edge_weights = [self.graph.edges[edge]['weight'] * 3 for edge in self.graph.edges()]

        # Draw edges first (so they appear behind nodes)
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color='gray',
            width=edge_weights,
            alpha=0.6,
            arrows=True,
            arrowsize=10,
            ax=ax
        )

        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color=node_colors,
            node_size=800,
            alpha=0.9,
            ax=ax
        )

        # Add node labels
        labels = {node: self.graph.nodes[node]['name'][:15] + "..."
                 if len(self.graph.nodes[node]['name']) > 15
                 else self.graph.nodes[node]['name']
                 for node in self.graph.nodes()}

        nx.draw_networkx_labels(
            self.graph, pos, labels,
            font_size=8, font_weight='bold',
            ax=ax
        )

        # Create legend
        self._create_legend(ax)

        ax.set_title("Apple Knowledge Graph - Full Network", fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Full graph visualization saved to: {output_path}")
        plt.close()

    def visualize_subgraph_by_type(self, node_type: str, output_path: str, figsize=(12, 8)):
        """Create a focused visualization showing nodes of a specific type and their connections"""
        # Find nodes of the specified type
        type_nodes = [node for node in self.graph.nodes()
                     if self.graph.nodes[node]['type'] == node_type]

        if not type_nodes:
            print(f"No nodes found of type: {node_type}")
            return

        # Create subgraph including the type nodes and their immediate neighbors
        subgraph_nodes = set(type_nodes)
        for node in type_nodes:
            subgraph_nodes.update(self.graph.neighbors(node))
            subgraph_nodes.update(self.graph.predecessors(node))

        subgraph = self.graph.subgraph(subgraph_nodes)

        fig, ax = plt.subplots(figsize=figsize)
        pos = nx.spring_layout(subgraph, k=2, iterations=50, seed=42)

        # Color nodes: target type in main color, others in light gray
        node_colors = []
        for node in subgraph.nodes():
            if node in type_nodes:
                node_colors.append(self.node_colors.get(node_type, self.node_colors['Default']))
            else:
                node_colors.append('#E0E0E0')  # Light gray for connected nodes

        # Draw the subgraph
        nx.draw_networkx_edges(subgraph, pos, edge_color='gray', alpha=0.6, arrows=True, arrowsize=8, ax=ax)
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=600, alpha=0.9, ax=ax)

        # Labels
        labels = {node: subgraph.nodes[node]['name'][:12] + "..."
                 if len(subgraph.nodes[node]['name']) > 12
                 else subgraph.nodes[node]['name']
                 for node in subgraph.nodes()}
        nx.draw_networkx_labels(subgraph, pos, labels, font_size=9, font_weight='bold', ax=ax)

        ax.set_title(f"Apple Knowledge Graph - {node_type} Entities and Connections",
                    fontsize=14, fontweight='bold', pad=15)
        ax.axis('off')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Subgraph visualization for {node_type} saved to: {output_path}")
        plt.close()

    def create_statistics_plot(self, graph_data: Dict[str, Any], output_path: str):
        """Create a statistics visualization showing node types and edge importance"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Node type distribution
        stats = graph_data['metadata']['statistics']
        types = list(stats['node_types'].keys())
        counts = list(stats['node_types'].values())
        colors = [self.node_colors.get(t, self.node_colors['Default']) for t in types]

        ax1.pie(counts, labels=types, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Node Type Distribution', fontsize=14, fontweight='bold')

        # Plot 2: Edge importance distribution
        edge_importance = [edge['importance_score'] for edge in graph_data['edges']]
        ax2.hist(edge_importance, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Importance Score')
        ax2.set_ylabel('Number of Edges')
        ax2.set_title('Edge Importance Score Distribution', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Statistics visualization saved to: {output_path}")
        plt.close()

    def _create_legend(self, ax):
        """Create a legend for node types"""
        legend_elements = []
        for node_type, color in self.node_colors.items():
            if node_type != 'Default':
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                                markerfacecolor=color, markersize=10, label=node_type))

        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))

    def generate_all_visualizations(self, json_path: str, output_dir: str):
        """Generate all visualizations and save to output directory"""
        # Load graph data
        graph_data = self.load_graph_from_json(json_path)

        # Create NetworkX graph
        self.create_networkx_graph(graph_data)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate visualizations
        print("Generating visualizations...")

        # 1. Full graph
        self.visualize_full_graph(os.path.join(output_dir, "apple_full_graph.png"))

        # 2. Company subgraph (most important type)
        self.visualize_subgraph_by_type("Company", os.path.join(output_dir, "apple_companies_subgraph.png"))

        # 3. Statistics
        self.create_statistics_plot(graph_data, os.path.join(output_dir, "apple_graph_statistics.png"))

        print(f"All visualizations saved to: {output_dir}")


def main():
    """Main function to create visualizations"""
    print("=== Apple Knowledge Graph Visualizer ===")

    # Paths
    json_path = "apple_graph.json"
    output_dir = "visualizations"

    # Check if graph JSON exists
    if not os.path.exists(json_path):
        print(f"Error: Graph JSON file not found at {json_path}")
        print("Please run graph_generator.py first to create the graph.")
        return

    # Create visualizer and generate all plots
    visualizer = GraphVisualizer()
    try:
        visualizer.generate_all_visualizations(json_path, output_dir)
        print("Visualization generation complete!")
    except Exception as e:
        print(f"Error during visualization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()