from typing import List, Dict, Optional, Union
from .Node import Node
from .Edge import Edge

class Graph:
    """
    Represents a graph data structure with nodes and edges.
    
    Attributes:
        nodes (Dict[str, Node]): Dictionary of nodes in the graph, keyed by node title.
        edges (List[Edge]): List of edges in the graph.
        bidirectional (bool): If True, edges are treated as bidirectional (adding or deleting an edge affects both directions).
    """
    
    def __init__(self, bidirectional: bool = False):
        """
        Initialize a Graph object with empty nodes and edges collections.
        
        Args:
            bidirectional (bool, optional): If True, edges are treated as bidirectional. Defaults to False.
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.bidirectional = bidirectional

    def appendNode(self, node: Node) -> None:
        """
        Append a node to the graph.
        
        Args:
            node (Node): The node to append.
        """
        self.nodes[node.title] = node
    
    def appendEdge(self, edge: Edge) -> None:
        """
        Append an edge to the graph. If the graph is bidirectional, also append the reverse edge.
        
        Args:
            edge (Edge): The edge to append.
        """
        self.edges.append(edge)
        
        # If bidirectional, create and append the reverse edge
        if self.bidirectional:
            from copy import deepcopy
            # Create a new edge with reversed start and end nodes
            reverse_edge = deepcopy(edge)
            reverse_edge.start, reverse_edge.end = edge.end, edge.start
            self.edges.append(reverse_edge)
    
    def deleteNode(self, node_title: str) -> bool:
        """
        Delete a node from the graph and all edges connected to it.
        
        Args:
            node_title (str): The title of the node to delete.
            
        Returns:
            bool: True if the node was found and deleted, False otherwise.
        """
        if node_title not in self.nodes:
            return False
        
        # Remove the node from the nodes dictionary
        del self.nodes[node_title]
        
        # Remove all edges connected to this node
        self.edges = [edge for edge in self.edges 
                     if edge.start.title != node_title and edge.end.title != node_title]
        
        return True
    
    def deleteEdge(self, start_title: str, end_title: str) -> bool:
        """
        Delete an edge between two nodes. If the graph is bidirectional, also delete the reverse edge.
        
        Args:
            start_title (str): The title of the start node of the edge.
            end_title (str): The title of the end node of the edge.
            
        Returns:
            bool: True if the edge was found and deleted, False otherwise.
        """
        initial_length = len(self.edges)
        
        if self.bidirectional:
            # Remove edges in both directions
            self.edges = [edge for edge in self.edges 
                         if not ((edge.start.title == start_title and edge.end.title == end_title) or
                                 (edge.start.title == end_title and edge.end.title == start_title))]
        else:
            # Remove edges only in the specified direction
            self.edges = [edge for edge in self.edges 
                         if not (edge.start.title == start_title and edge.end.title == end_title)]
        
        # Return True if any edges were removed
        return len(self.edges) < initial_length
    
    def find_paths(self, start_title: str, target_title: str, amount: int = 1) -> list:
        """
        Find the paths with the most weight between a starting node and a target node.
        
        Args:
            start_title (str): The title of the starting node.
            target_title (str): The title of the target node.
            amount (int, optional): The number of paths to return. Defaults to 1.
            
        Returns:
            list: A list of lists, where each inner list represents a path (sequence of nodes)
                 from start to target, sorted by total path weight in descending order.
                 Each path is represented as a list of node titles.
                 Returns an empty list if no paths are found.
        """
        if start_title not in self.nodes or target_title not in self.nodes:
            return []
        
        # Use a modified depth-first search to find all paths
        all_paths = []
        path_weights = []
        
        def dfs(current_title, target_title, path, visited, total_weight):
            # Mark the current node as visited
            visited.add(current_title)
            path.append(current_title)
            
            # If we've reached the target, add the path to our collection
            if current_title == target_title:
                all_paths.append(path.copy())
                path_weights.append(total_weight)
            else:
                # Explore all adjacent nodes
                for edge in self.edges:
                    if edge.start.title == current_title and edge.end.title not in visited:
                        dfs(edge.end.title, target_title, path, visited, total_weight + edge.weight)
            
            # Backtrack: remove the current node from path and mark it as unvisited
            path.pop()
            visited.remove(current_title)
        
        # Start DFS from the start node
        dfs(start_title, target_title, [], set(), 0)
        
        # Sort paths by their weights in descending order
        sorted_paths = [path for _, path in sorted(zip(path_weights, all_paths), reverse=True)]
        
        # Return the specified number of paths (or all if fewer are found)
        return sorted_paths[:min(amount, len(sorted_paths))]
    
    def __str__(self) -> str:
        """
        Return a string representation of the graph.
        
        Returns:
            str: A string representation of the graph.
        """
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.edges)})"
    
    def __repr__(self) -> str:
        """
        Return a string representation of the graph for debugging.
        
        Returns:
            str: A string representation of the graph.
        """
        return self.__str__()
