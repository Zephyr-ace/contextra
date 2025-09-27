"""
Script to directly load Apple data from JSON files into a Graph object and visualize it.
"""

import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
from collections import defaultdict

from graph_components.Graph import Graph
from graph_components.Node import Node
from graph_components.Edge import Edge

def load_json_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {file_path}: {e}")
        return []

def create_graph_from_json(nodes_json_path, edges_json_path):
    """Create a Graph object from JSON data."""
    # Create a new graph
    graph = Graph(bidirectional=False, use_vector_db=False)
    
    # Load nodes and edges from JSON
    nodes_data = load_json_data(nodes_json_path)
    edges_data = load_json_data(edges_json_path)
    
    print(f"Loaded {len(nodes_data)} nodes and {len(edges_data)} edges from JSON")
    
    # Create Node objects and add to graph
    for node_data in nodes_data:
        try:
            node = Node(**node_data)
            graph.appendNode(node)
        except Exception as e:
            print(f"Error creating node from {node_data}: {e}")
    
    # Create Edge objects and add to graph
    for edge_data in edges_data:
        try:
            edge = Edge(**edge_data)
            graph.appendEdge(edge)
        except Exception as e:
            print(f"Error creating edge from {edge_data}: {e}")
    
    print(f"Graph created with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    return graph

def create_networkx_graph(graph):
    """Convert our Graph object to a NetworkX graph for visualization."""
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for title, node in graph.nodes.items():
        G.add_node(node.name, 
                   title=title, 
                   type=node.type, 
                   description=node.description)
    
    # Add edges with attributes
    for edge in graph.edges:
        G.add_edge(edge.start.name, edge.end.name, 
                  title=edge.title, 
                  description=edge.description,
                  weight=edge.weight)
    
    return G

def visualize_graph(G, output_path="apple_graph.png"):
    """Visualize the NetworkX graph and save to a file."""
    plt.figure(figsize=(24, 18))
    
    # Group nodes by type
    node_types = defaultdict(list)
    for node, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'Unknown')
        node_types[node_type].append(node)
    
    # Create a color map for node types
    colors = list(mcolors.TABLEAU_COLORS.values())
    type_colors = {t: colors[i % len(colors)] for i, t in enumerate(node_types.keys())}
    
    # Set node colors based on type
    node_colors = [type_colors[G.nodes[n].get('type', 'Unknown')] for n in G.nodes()]
    
    # Set edge weights based on the weight attribute
    edge_weights = [G[u][v].get('weight', 0.5) * 2 + 0.5 for u, v in G.edges()]
    
    # Position nodes using a spring layout with adjusted parameters
    pos = nx.spring_layout(G, k=0.15, iterations=50, seed=42)
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.6, 
                          edge_color='gray', arrows=True, arrowsize=15)
    
    # Add labels with smaller font size for readability
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    
    # Create legend for node types
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
                             markersize=10, label=node_type) 
                      for node_type, color in type_colors.items()]
    plt.legend(handles=legend_elements, title="Node Types", loc="upper left", fontsize=12)
    
    # Add title
    plt.title("Apple Inc. Business Ecosystem", fontsize=20)
    
    # Remove axes
    plt.axis('off')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graph visualization saved to {output_path}")
    
    # Create a simplified version with fewer nodes for better readability
    create_simplified_visualization(G, pos, type_colors, "apple_graph_simplified.png")

def create_simplified_visualization(G, pos, type_colors, output_path):
    """Create a simplified visualization with only the most important nodes."""
    # Create a subgraph with only the most connected nodes
    top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:30]
    top_node_names = [n[0] for n in top_nodes]
    
    H = G.subgraph(top_node_names)
    
    plt.figure(figsize=(18, 14))
    
    # Draw the simplified graph
    node_colors = [type_colors[H.nodes[n].get('type', 'Unknown')] for n in H.nodes()]
    edge_weights = [H[u][v].get('weight', 0.5) * 2 + 0.5 for u, v in H.edges()]
    
    nx.draw_networkx_nodes(H, pos, nodelist=H.nodes(), node_size=900, 
                          node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(H, pos, edgelist=H.edges(), width=edge_weights, 
                          alpha=0.7, edge_color='gray', arrows=True, arrowsize=15)
    nx.draw_networkx_labels(H, pos, font_size=10, font_weight='bold')
    
    # Create legend for node types
    node_types_in_subgraph = set(H.nodes[n].get('type', 'Unknown') for n in H.nodes())
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=type_colors[t], 
                             markersize=10, label=t) 
                      for t in node_types_in_subgraph]
    plt.legend(handles=legend_elements, title="Node Types", loc="upper left", fontsize=12)
    
    # Add title
    plt.title("Apple Inc. Business Ecosystem (Simplified)", fontsize=20)
    
    # Remove axes
    plt.axis('off')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Simplified graph visualization saved to {output_path}")

def main():
    # Paths to JSON files
    nodes_json_path = "data/cache/apple_nodes.json"
    edges_json_path = "data/cache/apple_edges.json"
    
    # Check if files exist
    if not os.path.exists(nodes_json_path) or not os.path.exists(edges_json_path):
        print(f"Error: JSON files not found at {nodes_json_path} or {edges_json_path}")
        return
    
    # Create graph from JSON data
    graph = create_graph_from_json(nodes_json_path, edges_json_path)
    
    # Convert to NetworkX graph for visualization
    nx_graph = create_networkx_graph(graph)
    
    # Visualize the graph
    visualize_graph(nx_graph)
    
    print("Graph visualization completed!")

if __name__ == "__main__":
    main()
