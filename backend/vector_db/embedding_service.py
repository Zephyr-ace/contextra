from typing import List, Dict, Any, Union, Optional
import numpy as np
from ..graph_components.Node import Node

class EmbeddingService:
    """
    Service for generating embeddings for nodes.
    
    This class provides methods to generate embeddings for nodes based on their name and description.
    It can use different embedding models depending on the configuration.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service with a specified model.
        
        Args:
            model_name (str): Name of the embedding model to use
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "Please install sentence-transformers: pip install sentence-transformers"
            )
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text.
        
        Args:
            text (str): The text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def get_node_embedding(self, node: Node) -> List[float]:
        """
        Generate an embedding for a node based on its name and description.
        
        Args:
            node (Node): The node to embed
            
        Returns:
            List[float]: The embedding vector
        """
        # Combine name and description for a more comprehensive embedding
        text = f"{node.name}: {node.description}"
        
        # Add aliases if available
        if hasattr(node, 'aliases') and node.aliases:
            text += f" (Also known as: {', '.join(node.aliases)})"
            
        return self.get_embedding(text)
    
    def get_nodes_embeddings(self, nodes: List[Node]) -> List[List[float]]:
        """
        Generate embeddings for multiple nodes.
        
        Args:
            nodes (List[Node]): The nodes to embed
            
        Returns:
            List[List[float]]: The embedding vectors
        """
        texts = []
        for node in nodes:
            text = f"{node.name}: {node.description}"
            if hasattr(node, 'aliases') and node.aliases:
                text += f" (Also known as: {', '.join(node.aliases)})"
            texts.append(text)
            
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
