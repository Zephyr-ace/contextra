from typing import List, Dict, Optional, Tuple
from ...graph_components.Graph import Graph
from ...graph_components.Node import Node
from ...graph_components.Edge import Edge


def format_path_as_string(graph: Graph, path: List[str]) -> str:
    """
    Format a path as a string representation showing the relationships between nodes.
    
    The format is:
    node1.name + node1.description <- (reason: edge1.description) -> node2.name + node2.description...
    
    For unidirectional edges: - (reason) ->
    For bidirectional edges: <- (reason) ->
    
    Args:
        graph (Graph): The graph containing the nodes and edges
        path (List[str]): A list of node titles representing a path
        
    Returns:
        str: A formatted string representation of the path
    """
    if not path or len(path) < 2:
        return "" if not path else f"{graph.nodes[path[0]].name}: {graph.nodes[path[0]].description}"
    
    result = []
    
    for i in range(len(path) - 1):
        current_node_title = path[i]
        next_node_title = path[i + 1]
        
        current_node = graph.nodes[current_node_title]
        next_node = graph.nodes[next_node_title]
        
        # Find the edge between current_node and next_node
        edge = None
        reverse_edge = None
        
        for e in graph.edges:
            if e.start.title == current_node_title and e.end.title == next_node_title:
                edge = e
            elif e.start.title == next_node_title and e.end.title == current_node_title:
                reverse_edge = e
        
        # Format the current node
        if i == 0:
            result.append(f"{current_node.name}: {current_node.description}")
        
        # Format the edge
        if edge:
            if reverse_edge:  # Bidirectional
                result.append(f"<- ({edge.description}) ->")
            else:  # Unidirectional
                result.append(f"- ({edge.description}) ->")
        else:
            # If no direct edge found but reverse edge exists (unusual case)
            if reverse_edge:
                result.append(f"<- ({reverse_edge.description}) -")
            else:
                # No edge found, use a generic connector
                result.append("- (unknown relation) ->")
        
        # Format the next node
        result.append(f"{next_node.name}: {next_node.description}")
    
    return " ".join(result)


def format_paths_as_strings(graph: Graph, paths: List[List[str]]) -> List[str]:
    """
    Format multiple paths as string representations.
    
    Args:
        graph (Graph): The graph containing the nodes and edges
        paths (List[List[str]]): A list of paths, where each path is a list of node titles
        
    Returns:
        List[str]: A list of formatted string representations of the paths
    """
    return [format_path_as_string(graph, path) for path in paths]


def get_path_with_most_weight(graph: Graph, start_title: str, target_title: str) -> List[str]:
    """
    Get the path with the highest total weight between two nodes.
    
    Args:
        graph (Graph): The graph containing the nodes and edges
        start_title (str): The title of the starting node
        target_title (str): The title of the target node
        
    Returns:
        List[str]: The path with the highest total weight as a list of node titles
    """
    paths = graph.find_paths(start_title, target_title, amount=1)
    if not paths:
        return []
    return paths[0]


def validateProximity(node1: Node, node2: Node, edge: Edge) -> bool:
    """
    Validate if two nodes should be connected by a specific edge based on their proximity or relationship.
    
    Args:
        node1 (Node): The first node
        node2 (Node): The second node
        edge (Edge): The edge connecting the nodes
        
    Returns:
        bool: True if the edge is valid for connecting these nodes, False otherwise
    """
    # Placeholder logic - to be implemented
    # This could check for semantic similarity, contextual relevance, or other factors
    # that determine if the nodes should be connected by this edge
    
    # For now, always return True as a placeholder
    return True
