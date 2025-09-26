from typing import Optional
from .Node import Node

class Edge:
    """
    Represents an edge in a graph connecting two nodes.
    
    Attributes:
        weight (float): The weight of the edge.
        start (Node): The starting node of the edge.
        end (Node): The ending node of the edge.
        description (str): A description of the edge.
        title (str): A title for the edge.
    """
    
    def __init__(self, start: Node, end: Node, weight: float = 1.0, 
                 description: str = "", title: str = ""):
        """
        Initialize an Edge object.
        
        Args:
            start (Node): The starting node of the edge.
            end (Node): The ending node of the edge.
            weight (float, optional): The weight of the edge. Defaults to 1.0.
            description (str, optional): A description of the edge. Defaults to "".
            title (str, optional): A title for the edge. Defaults to "".
        """
        self.start = start
        self.end = end
        self.weight = weight
        self.description = description
        self.title = title
    
    def __str__(self) -> str:
        """
        Return a string representation of the edge.
        
        Returns:
            str: A string representation of the edge.
        """
        return f"Edge(title={self.title}, start={self.start}, end={self.end}, weight={self.weight})"
    
    def __repr__(self) -> str:
        """
        Return a string representation of the edge for debugging.
        
        Returns:
            str: A string representation of the edge.
        """
        return self.__str__()
