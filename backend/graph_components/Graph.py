from typing import List, Dict, Optional, Union, Any
import os
from .Node import Node
from .Edge import Edge

# Import vector database components with fallback
try:
    from ..vector_db.vector_store import VectorStore
    from ..vector_db.embedding_service import EmbeddingService
    VECTOR_DB_AVAILABLE = True
except ImportError:
    # Handle the case where vector_db module is not available
    VECTOR_DB_AVAILABLE = False


class Graph:
    """
    Represents a graph data structure with nodes and edges.

    Attributes:
        nodes (Dict[str, Node]): Dictionary of nodes in the graph, keyed by node title.
        edges (List[Edge]): List of edges in the graph.
        bidirectional (bool): If True, edges are treated as bidirectional (adding or deleting an edge affects both directions).
    """

    def __init__(self, bidirectional: bool = False, use_vector_db: bool = True, collection_name: str = "graph_nodes", persist_directory: str = "./chroma_db", reset_db: bool = True):
        """
        Initialize a Graph object with empty nodes and edges collections.

        Args:
            bidirectional (bool, optional): If True, edges are treated as bidirectional. Defaults to False.
            use_vector_db (bool, optional): If True, use vector database for node storage and similarity search. Defaults to True.
            collection_name (str, optional): Name of the collection in the vector database. Defaults to "graph_nodes".
            persist_directory (str, optional): Directory to persist the vector database. Defaults to "./chroma_db".
            reset_db (bool, optional): If True, reset the vector database collection on initialization. Defaults to True.
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.bidirectional = bidirectional
        self.use_vector_db = use_vector_db and VECTOR_DB_AVAILABLE
        
        # Initialize vector database components if available and requested
        if self.use_vector_db:
            try:
                print(f"Initializing vector database for graph with collection '{collection_name}'...")
                self.embedding_service = EmbeddingService(use_dummy=False)
                self.vector_store = VectorStore(collection_name=collection_name, persist_directory=persist_directory)
                
                # Reset the collection if requested
                if reset_db:
                    try:
                        print("Resetting vector database collection...")
                        self.vector_store.client.delete_collection(name=collection_name)
                        self.vector_store = VectorStore(collection_name=collection_name, persist_directory=persist_directory)
                        print("Vector database collection reset successfully.")
                    except Exception as e:
                        print(f"Warning: Could not reset vector database collection: {e}")
                        # Continue with existing collection
                
                print("Vector database initialized successfully.")
            except Exception as e:
                print(f"Warning: Could not initialize vector database: {e}")
                self.use_vector_db = False
                self.embedding_service = None
                self.vector_store = None

    def appendNode(self, node: Node) -> None:
        """
        Append a node to the graph and add it to the vector database if enabled.

        Args:
            node (Node): The node to append.
        """
        # Add to the nodes dictionary
        self.nodes[node.title] = node
        
        # Add to vector database if enabled
        if self.use_vector_db and hasattr(self, 'vector_store') and self.vector_store is not None:
            try:
                # Generate embedding for the node
                embedding = self.embedding_service.get_node_embedding(node)
                
                # Add to vector store
                node_id = self.vector_store.add_node(node, embedding)
                
                # Store the vector database ID with the node for future reference
                if not hasattr(node, 'vector_db_id'):
                    setattr(node, 'vector_db_id', node_id)
                    
            except Exception as e:
                print(f"Warning: Could not add node to vector database: {e}")
                # Continue without vector database entry

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
        Delete a node from the graph, all edges connected to it, and remove it from the vector database.

        Args:
            node_title (str): The title of the node to delete.

        Returns:
            bool: True if the node was found and deleted, False otherwise.
        """
        if node_title not in self.nodes:
            return False
            
        # Get the node before deleting it
        node = self.nodes[node_title]
        
        # Remove from vector database if enabled
        if self.use_vector_db and hasattr(self, 'vector_store') and self.vector_store is not None:
            try:
                # If the node has a vector_db_id, use it for deletion
                if hasattr(node, 'vector_db_id'):
                    self.vector_store.delete_node(node.vector_db_id)
                else:
                    # Otherwise, try to find it by name in the vector store
                    # This is a fallback and might not be reliable
                    print(f"Warning: Node {node_title} has no vector_db_id, attempting to find by name")
            except Exception as e:
                print(f"Warning: Could not remove node from vector database: {e}")
        
        # Remove the node from the nodes dictionary
        del self.nodes[node_title]

        # Remove all edges connected to this node
        self.edges = [edge for edge in self.edges if edge.start.title != node_title and edge.end.title != node_title]

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
            self.edges = [
                edge
                for edge in self.edges
                if not (
                    (edge.start.title == start_title and edge.end.title == end_title)
                    or (edge.start.title == end_title and edge.end.title == start_title)
                )
            ]
        else:
            # Remove edges only in the specified direction
            self.edges = [
                edge for edge in self.edges if not (edge.start.title == start_title and edge.end.title == end_title)
            ]

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
                        dfs(edge.end.title, target_title, path, visited, total_weight * edge.weight)

            # Backtrack: remove the current node from path and mark it as unvisited
            path.pop()
            visited.remove(current_title)

        # Start DFS from the start node
        dfs(start_title, target_title, [], set(), 0)

        # Sort paths by their weights in descending order
        sorted_paths = [path for _, path in sorted(zip(path_weights, all_paths), reverse=True)]

        # Return the specified number of paths (or all if fewer are found)
        return sorted_paths[: min(amount, len(sorted_paths))]

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
        
    def find_similar_nodes(self, query_node: Node, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find nodes similar to the given query node using vector similarity search.
        
        Args:
            query_node (Node): The node to find similar nodes for.
            top_k (int, optional): The number of similar nodes to return. Defaults to 5.
            
        Returns:
            List[Dict[str, Any]]: A list of similar nodes with metadata and similarity scores.
        """
        if not self.use_vector_db or not hasattr(self, 'vector_store') or self.vector_store is None:
            print("Warning: Vector database not available for similarity search")
            return []
            
        try:
            # Generate embedding for the query node
            query_embedding = self.embedding_service.get_node_embedding(query_node)
            
            # Search for similar nodes
            similar_nodes = self.vector_store.search_by_embedding(query_embedding, n_results=top_k)
            return similar_nodes
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []
    
    def find_similar_by_text(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find nodes similar to the given text query using vector similarity search.
        
        Args:
            query_text (str): The text query to find similar nodes for.
            top_k (int, optional): The number of similar nodes to return. Defaults to 5.
            
        Returns:
            List[Dict[str, Any]]: A list of similar nodes with metadata and similarity scores.
        """
        if not self.use_vector_db or not hasattr(self, 'vector_store') or self.vector_store is None:
            print("Warning: Vector database not available for text search")
            return []
            
        try:
            # Search for similar nodes by text
            similar_nodes = self.vector_store.search_by_text(query_text, n_results=top_k)
            return similar_nodes
        except Exception as e:
            print(f"Error during text search: {e}")
            return []
