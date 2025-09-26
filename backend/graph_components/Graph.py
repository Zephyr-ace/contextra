from typing import List, Dict, Optional
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
