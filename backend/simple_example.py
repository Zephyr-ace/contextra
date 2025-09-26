"""
Simplified example of using the vector database.
Run this from the backend directory with: python simple_example.py
"""

import os
import sys
from graph_components.Node import Node
from vector_db.vector_store import VectorStore
from vector_db.embedding_service import EmbeddingService

def main():
    print("Starting simplified vector database example...")
    
    # Initialize services with dummy embeddings
    print("Initializing embedding service with dummy embeddings...")
    embedding_service = EmbeddingService(use_dummy=True)
    
    print("Initializing vector store...")
    vector_store = VectorStore(collection_name="simple_example", persist_directory="./chroma_db")
    
    # Create a few test nodes
    print("\nCreating test nodes...")
    nodes = [
        Node(
            name="Microsoft",
            description="A technology company that develops software and cloud services",
            type="Company"
        ),
        Node(
            name="Google",
            description="A technology company focusing on search, online advertising, and AI",
            type="Company"
        ),
        Node(
            name="Cloud Computing",
            description="The delivery of computing services over the internet",
            type="Concept"
        )
    ]
    
    # Add nodes to the vector store
    print("\nAdding nodes to vector store...")
    node_ids = []
    for node in nodes:
        print(f"Processing node: {node.name}")
        embedding = embedding_service.get_node_embedding(node)
        node_id = vector_store.add_node(node, embedding)
        node_ids.append(node_id)
        print(f"  Added with ID: {node_id}")
    
    # Search for nodes
    print("\nSearching for 'cloud technology'...")
    results = vector_store.search_by_text("cloud technology", n_results=2)
    
    # Print results
    if results:
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"{i+1}. {result['metadata']['name']} ({result['metadata']['type']})")
            print(f"   {result['metadata']['description']}")
    else:
        print("No results found")
    
    print("\nSimplified example completed!")

if __name__ == "__main__":
    main()
