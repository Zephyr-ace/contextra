from typing import List, Dict, Any, Union, Optional
import numpy as np

# Use absolute imports instead of relative imports
try:
    from graph_components.Node import Node
except ImportError:
    # For when running from within the vector_db directory
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from graph_components.Node import Node

class EmbeddingService:
    """
    Service for generating embeddings for nodes.
    
    This class provides methods to generate embeddings for nodes based on their name and description.
    It can use different embedding models depending on the configuration.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", use_dummy: bool = False):
        """
        Initialize the embedding service with a specified model.
        
        Args:
            model_name (str): Name of the embedding model to use
            use_dummy (bool): If True, use a dummy embedding generator instead of loading a model
        """
        self.embedding_dim = 384  # Default dimension for all-MiniLM-L6-v2
        self.use_dummy = use_dummy
        
        if use_dummy:
            print("Using dummy embedding generator for testing")
            self.model = None
        else:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"Loading embedding model: {model_name}")
                self.model = SentenceTransformer(model_name)
                print("Model loaded successfully")
            except ImportError as e:
                print(f"Error importing sentence-transformers: {e}")
                print("Please install sentence-transformers: pip install sentence-transformers")
                print("Falling back to dummy embedding generator")
                self.use_dummy = True
                self.model = None
            except Exception as e:
                print(f"Error loading model: {e}")
                print("Falling back to dummy embedding generator")
                self.use_dummy = True
                self.model = None
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text.
        
        Args:
            text (str): The text to embed
            
        Returns:
            List[float]: The embedding vector
        """
        if self.use_dummy:
            # Generate a deterministic dummy embedding based on the hash of the text
            import hashlib
            import numpy as np
            
            # Create a hash of the text
            text_hash = hashlib.md5(text.encode()).hexdigest()
            # Use the hash to seed a random number generator
            np.random.seed(int(text_hash, 16) % 2**32)
            # Generate a random embedding vector
            embedding = np.random.uniform(-1, 1, self.embedding_dim)
            # Normalize the vector
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        else:
            # Use the actual model
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
