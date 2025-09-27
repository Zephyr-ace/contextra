from typing import Dict, List, Optional, Union, Set, Tuple
import numpy as np
from backend.graph_components.Graph import Graph
from backend.graph_components.Node import Node
from backend.graph_components.Edge import Edge
from backend.vector_db.embedding_service import EmbeddingService


class IntegrityCheck:
    """
    A class for performing integrity checks on graph components.
    
    This class provides methods to check for duplicates, inconsistencies,
    and other integrity issues in a graph.
    """
    
    def __init__(self, similarity_threshold: float = 0.85, top_k: int = 3):
        """
        Initialize the IntegrityCheck object.
        
        Args:
            similarity_threshold (float): Threshold for considering nodes as duplicates (0.0 to 1.0).
                Higher values mean more similarity is required to flag as duplicate.
            top_k (int): Number of most similar nodes to retrieve for comparison.
        """
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.embedding_service = EmbeddingService(use_dummy=False)
    
    def checkDuplicates(self, node: Node, graph: Graph) -> Tuple[bool, Optional[Dict]]:
        """
        Check if a node is a duplicate of any existing node in the graph using vector similarity.
        
        Args:
            node (Node): The node to check for duplicates.
            graph (Graph): The graph to check against.
            
        Returns:
            Tuple[bool, Optional[Dict]]: A tuple containing:
                - bool: True if the node is a duplicate, False otherwise.
                - Optional[Dict]: Information about the most similar node if a duplicate is found, None otherwise.
        """
        # First, check for exact title match (fast check)
        if node.title in graph.nodes:
            return True, {
                "node": graph.nodes[node.title],
                "similarity": 1.0,
                "reason": "Exact title match"
            }
        
        # If no vector store in graph, we can't do semantic similarity checks
        if not hasattr(graph, 'vector_store') or graph.vector_store is None:
            return False, None
        
        # Generate embedding for the node
        try:
            node_embedding = self.embedding_service.get_node_embedding(node)
            
            # Search for similar nodes in the vector store
            similar_nodes = graph.vector_store.search_by_embedding(node_embedding, n_results=self.top_k)
            
            # If we found any similar nodes
            if similar_nodes:
                most_similar = similar_nodes[0]  # The most similar node
                similarity = 1.0 - (most_similar.get('distance', 0) if most_similar.get('distance') is not None else 0)
                
                # Check if similarity exceeds our threshold
                if similarity >= self.similarity_threshold:
                    # Find the actual node object
                    node_title = most_similar['metadata']['name']
                    duplicate_node = next((n for n in graph.nodes.values() if n.name == node_title), None)
                    
                    return True, {
                        "node": duplicate_node,
                        "similarity": similarity,
                        "reason": "Semantic similarity"
                    }
        except Exception as e:
            print(f"Warning: Error during vector similarity check: {e}")
            # Fall back to basic checks if vector search fails
        
        # Check for name similarity as fallback
        for existing_node in graph.nodes.values():
            if node.name.lower() == existing_node.name.lower():
                return True, {
                    "node": existing_node,
                    "similarity": 0.9,
                    "reason": "Case-insensitive name match"
                }
            
            # Check for name in aliases
            if hasattr(existing_node, 'aliases') and existing_node.aliases:
                if node.name.lower() in [alias.lower() for alias in existing_node.aliases]:
                    return True, {
                        "node": existing_node,
                        "similarity": 0.8,
                        "reason": "Name matches alias"
                    }
        
        # No duplicates found
        return False, None
    
    def checkGraphIntegrity(self, graph: Graph) -> Dict[str, List[str]]:
        """
        Check the overall integrity of a graph.
        
        Args:
            graph (Graph): The graph to check.
            
        Returns:
            Dict[str, List[str]]: A dictionary of issues found, where keys are issue types
                                 and values are lists of descriptions of the issues.
        """
        issues = {
            "duplicate_nodes": [],
            "orphaned_nodes": [],
            "invalid_edges": []
        }
        
        # Placeholder logic - to be implemented
        # This could check for various integrity issues in the graph
        
        return issues
