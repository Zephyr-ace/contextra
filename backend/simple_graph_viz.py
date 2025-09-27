"""
Simple script to load Apple data from JSON files and create a basic visualization.
This script has minimal dependencies and focuses on clarity.
"""

import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def load_json_data(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Paths to JSON files
    nodes_json_path = "data/cache/apple_nodes.json"
    edges_json_path = "data/cache/apple_edges.json"
    
    # Check if files exist
    if not os.path.exists(nodes_json_path) or not os.path.exists(edges_json_path):
        print(f"Error: JSON files not found at {nodes_json_path} or {edges_json_path}")
        return
    
    # Load data from JSON files
    nodes_data = load_json_data(nodes_json_path)
    edges_data = load_json_data(edges_json_path)
    
    print(f"Loaded {len(nodes_data)} nodes and {len(edges_data)} edges from JSON")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Create a mapping of node names to their data
    node_map = {node['name']: node for node in nodes_data}
    
    # Add nodes to the graph
    for node in nodes_data:
        G.add_node(node['name'], **node)
    
    # Add edges to the graph
    for edge in edges_data:
        start_name = edge['start']['name']
        end_name = edge['end']['name']
        
        # Only add the edge if both nodes exist
        if start_name in G.nodes and end_name in G.nodes:
            G.add_edge(start_name, end_name, **edge)
    
    print(f"Graph created with {len(G.nodes)} nodes and {len(G.edges)} edges")
    
    # Group nodes by type
    node_types = defaultdict(list)
    for node in nodes_data:
        node_type = node.get('type', 'Unknown')
        node_types[node_type].append(node['name'])
    
    # Print node type distribution
    print("\nNode type distribution:")
    for node_type, nodes in node_types.items():
        print(f"- {node_type}: {len(nodes)} nodes")
    
    # Create a basic visualization
    plt.figure(figsize=(20, 16))
    
    # Use a spring layout for node positioning
    pos = nx.spring_layout(G, k=0.15, iterations=50, seed=42)
    
    # Draw nodes with different colors based on type
    for i, (node_type, nodes) in enumerate(node_types.items()):
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_size=100, 
                              label=node_type, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5, arrows=True, arrowsize=10)
    
    # Draw labels for important nodes only (to avoid clutter)
    # Find the most connected nodes
    top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:20]
    top_node_names = [n[0] for n in top_nodes]
    labels = {node: node for node in top_node_names}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    
    plt.title("Apple Inc. Business Ecosystem", fontsize=16)
    plt.legend(scatterpoints=1, title="Node Types")
    plt.axis('off')
    
    # Save the figure
    output_path = "apple_graph_simple.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nGraph visualization saved to {output_path}")
    
    # Create a focused visualization showing only Apple and its direct connections
    create_apple_focused_visualization(G, pos, "apple_focused_graph.png")

def create_apple_focused_visualization(G, pos, output_path):
    """Create a visualization focused on Apple and its direct connections."""
    # Find the Apple node
    apple_node = "Apple Inc."
    
    if apple_node not in G.nodes:
        print(f"Error: {apple_node} not found in the graph")
        return
    
    # Get Apple's neighbors (1-hop)
    neighbors = list(G.predecessors(apple_node)) + list(G.successors(apple_node))
    neighbors.append(apple_node)
    
    # Create a subgraph
    H = G.subgraph(neighbors)
    
    plt.figure(figsize=(16, 12))
    
    # Draw the subgraph
    nx.draw_networkx_nodes(H, pos, nodelist=[apple_node], node_size=1500, 
                          node_color='red', alpha=0.8)
    nx.draw_networkx_nodes(H, pos, nodelist=[n for n in H.nodes if n != apple_node], 
                          node_size=700, node_color='skyblue', alpha=0.6)
    
    # Draw edges
    nx.draw_networkx_edges(H, pos, width=1.0, alpha=0.7, arrows=True, arrowsize=15)
    
    # Draw labels
    labels = {node: node for node in H.nodes}
    nx.draw_networkx_labels(H, pos, labels=labels, font_size=8)
    
    plt.title("Apple Inc. and Direct Connections", fontsize=16)
    plt.axis('off')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Apple-focused visualization saved to {output_path}")

if __name__ == "__main__":
    main()
