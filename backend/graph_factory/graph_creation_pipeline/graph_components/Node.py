from typing import Optional

class Node:
    """
    Represents a node in a graph.
    
    Attributes:
        title (str): The title of the node.
        description (str): A description of the node.
        category (str): The category of the node.
    """
    
    def __init__(self, title: str, description: str = "", category: str = ""):
        """
        Initialize a Node object.
        
        Args:
            title (str): The title of the node.
            description (str, optional): A description of the node. Defaults to "".
            category (str, optional): The category of the node. Defaults to "".
        """
        self.title = title
        self.description = description
        self.category = category
    
    def __str__(self) -> str:
        """
        Return a string representation of the node.
        
        Returns:
            str: A string representation of the node.
        """
        return f"Node(title={self.title}, category={self.category})"
    
    def __repr__(self) -> str:
        """
        Return a string representation of the node for debugging.
        
        Returns:
            str: A string representation of the node.
        """
        return self.__str__()
