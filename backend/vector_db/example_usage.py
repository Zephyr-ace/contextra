"""
Example usage of the vector database for Contextra.
"""

import os
import sys

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from vector_db module
from vector_db.vector_store import VectorStore
from vector_db.embedding_service import EmbeddingService

# Import from graph_components module
from graph_components.Node import Node
from graph_components.Graph import Graph

def main():
    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStore(collection_name="nodes", persist_directory="./chroma_db")
    
    # Create some example nodes
    nodes = [
        Node(
            name="Microsoft",
            description="A multinational technology company that develops and sells computer software, consumer electronics, and personal computers.",
            type="Company"
        ),
        Node(
            name="Google",
            description="A technology company specializing in Internet-related services and products, including search, cloud computing, and advertising technologies.",
            type="Company"
        ),
        Node(
            name="Satya Nadella",
            description="CEO of Microsoft Corporation since 2014, known for transforming Microsoft's business model to focus on cloud computing.",
            type="Person"
        ),
        Node(
            name="Sundar Pichai",
            description="CEO of Google LLC and its parent company Alphabet Inc., known for his work on Google Chrome and Android.",
            type="Person"
        ),
        Node(
            name="Azure",
            description="Microsoft's cloud computing service for building, testing, deploying, and managing applications and services.",
            type="Product"
        ),
        Node(
            name="Google Cloud",
            description="Google's suite of cloud computing services that runs on the same infrastructure that Google uses internally.",
            type="Product"
        )
    ]
    
    # Generate embeddings and add to vector store
    print("Generating embeddings and adding nodes to vector store...")
    embeddings = embedding_service.get_nodes_embeddings(nodes)
    node_ids = vector_store.add_nodes(nodes, embeddings)
    
    # Map node titles to IDs for reference
    node_id_map = {nodes[i].name: node_ids[i] for i in range(len(nodes))}
    print(f"Added {len(node_ids)} nodes to vector store")
    
    # Perform some example searches
    print("\nSearching for 'cloud computing'...")
    results = vector_store.search_by_text("cloud computing", n_results=3)
    print_results(results)
    
    print("\nSearching for 'tech company CEO'...")
    results = vector_store.search_by_text("tech company CEO", n_results=3)
    print_results(results)
    
    # Get a specific node
    print("\nRetrieving Microsoft node...")
    microsoft_node = vector_store.get_node(node_id_map["Microsoft"])
    if microsoft_node:
        print(f"Found: {microsoft_node['metadata']['name']} - {microsoft_node['metadata']['description']}")
    else:
        print("Node not found")
    
    # Example of using embeddings for similarity check
    print("\nChecking similarity between nodes...")
    azure_embedding = embedding_service.get_node_embedding(nodes[4])  # Azure
    similar_to_azure = vector_store.search_by_embedding(azure_embedding, n_results=3)
    print("Nodes similar to Azure:")
    print_results(similar_to_azure)

def print_results(results):
    """Print search results in a readable format."""
    if not results:
        print("No results found")
        return
    
    for i, result in enumerate(results):
        print(f"{i+1}. {result['metadata']['name']} ({result['metadata']['type']})")
        print(f"   {result['metadata']['description']}")
        if 'distance' in result and result['distance'] is not None:
            print(f"   Similarity: {1 - result['distance']:.4f}")
        print()

if __name__ == "__main__":
    main()
