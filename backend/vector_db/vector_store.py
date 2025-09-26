from typing import List, Dict, Any, Optional, Union
import chromadb
from chromadb.config import Settings
import os
import uuid

# Use absolute imports instead of relative imports
try:
    from graph_components.Node import Node
except ImportError:
    # For when running from within the vector_db directory
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from graph_components.Node import Node

class VectorStore:
    """
    A vector database implementation using ChromaDB for storing and retrieving Node embeddings.
    
    This class provides methods to:
    - Add nodes with their embeddings to the database
    - Search for similar nodes based on text or embeddings
    - Retrieve nodes by ID
    - Delete nodes from the database
    """
    
    def __init__(self, collection_name: str = "nodes", persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store with ChromaDB.
        
        Args:
            collection_name (str): Name of the collection to use
            persist_directory (str): Directory to persist the database
        """
        # Ensure the persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with a simpler configuration
        try:
            # Try the persistent client first
            self.client = chromadb.PersistentClient(path=persist_directory)
        except Exception as e:
            print(f"Warning: Could not create persistent client: {e}")
            print("Falling back to in-memory client...")
            # Fall back to in-memory client
            self.client = chromadb.Client()
        
        # Get or create collection
        try:
            # Try to get the collection if it exists
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Using existing collection: {collection_name}")
        except Exception as e:
            # Collection doesn't exist yet or there was another error
            print(f"Collection not found or error: {e}")
            print(f"Creating new collection: {collection_name}")
            try:
                self.collection = self.client.create_collection(name=collection_name)
                print(f"Successfully created collection: {collection_name}")
            except Exception as create_error:
                print(f"Error creating collection: {create_error}")
                raise
    
    def add_node(self, node: Node, embedding: List[float]) -> str:
        """
        Add a node with its embedding to the vector database.
        
        Args:
            node (Node): The node to add
            embedding (List[float]): The embedding vector for the node
            
        Returns:
            str: The ID of the added node
        """
        node_id = str(uuid.uuid4()) if not hasattr(node, 'id') else str(node.id)
        
        # Prepare metadata
        metadata = {
            "name": node.name,
            "description": node.description,
            "type": node.type
        }
        
        # Add aliases if available
        if hasattr(node, 'aliases') and node.aliases:
            metadata["aliases"] = ", ".join(node.aliases)
        
        # Add to collection
        self.collection.add(
            ids=[node_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[f"{node.name}: {node.description}"]  # For hybrid search
        )
        
        return node_id
    
    def add_nodes(self, nodes: List[Node], embeddings: List[List[float]]) -> List[str]:
        """
        Add multiple nodes with their embeddings to the vector database.
        
        Args:
            nodes (List[Node]): The nodes to add
            embeddings (List[List[float]]): The embedding vectors for the nodes
            
        Returns:
            List[str]: The IDs of the added nodes
        """
        if len(nodes) != len(embeddings):
            raise ValueError("Number of nodes must match number of embeddings")
        
        node_ids = []
        metadatas = []
        documents = []
        
        for node in nodes:
            node_id = str(uuid.uuid4()) if not hasattr(node, 'id') else str(node.id)
            node_ids.append(node_id)
            
            metadata = {
                "name": node.name,
                "description": node.description,
                "type": node.type
            }
            
            if hasattr(node, 'aliases') and node.aliases:
                metadata["aliases"] = ", ".join(node.aliases)
                
            metadatas.append(metadata)
            documents.append(f"{node.name}: {node.description}")
        
        # Add to collection
        self.collection.add(
            ids=node_ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        return node_ids
    
    def search_by_text(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar nodes based on text query.
        
        Args:
            query (str): The text query
            n_results (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of matching nodes with their metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def search_by_embedding(self, embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar nodes based on embedding vector.
        
        Args:
            embedding (List[float]): The embedding vector to search with
            n_results (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of matching nodes with their metadata
        """
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by its ID.
        
        Args:
            node_id (str): The ID of the node to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The node data if found, None otherwise
        """
        try:
            result = self.collection.get(ids=[node_id])
            if result['ids'] and len(result['ids']) > 0:
                return {
                    'id': result['ids'][0],
                    'metadata': result['metadatas'][0],
                    'document': result['documents'][0],
                    'embedding': result['embeddings'][0] if 'embeddings' in result else None
                }
            return None
        except Exception:
            return None
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node by its ID.
        
        Args:
            node_id (str): The ID of the node to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            self.collection.delete(ids=[node_id])
            return True
        except Exception:
            return False
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format query results into a more usable structure.
        
        Args:
            results (Dict[str, Any]): The raw results from ChromaDB
            
        Returns:
            List[Dict[str, Any]]: Formatted results
        """
        formatted_results = []
        
        if not results['ids'] or len(results['ids'][0]) == 0:
            return formatted_results
        
        for i, node_id in enumerate(results['ids'][0]):
            formatted_results.append({
                'id': node_id,
                'metadata': results['metadatas'][0][i],
                'document': results['documents'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
