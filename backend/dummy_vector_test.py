"""
Test script for vector database using dummy embeddings.
Run this from the backend directory with: python dummy_vector_test.py
"""

import os
import sys
from graph_components.Node import Node
from vector_db.vector_store import VectorStore
from vector_db.embedding_service import EmbeddingService

def main():
    print("Testing vector database with dummy embeddings...")
    
    # Initialize services with dummy embeddings
    embedding_service = EmbeddingService(use_dummy=True)
    
    # Use in-memory ChromaDB for testing
    vector_store = VectorStore(collection_name="test_nodes")
    
    # Create some test nodes
    test_nodes = [
        Node(
            name="Company A",
            description="A technology company focused on AI",
            type="Company"
        ),
        Node(
            name="Company B",
            description="A software development company",
            type="Company"
        ),
        Node(
            name="Person X",
            description="CEO of Company A",
            type="Person"
        )
    ]
    
    print(f"Created {len(test_nodes)} test nodes")
    
    # Generate embeddings and add to vector store
    for node in test_nodes:
        print(f"Processing node: {node.name}")
        embedding = embedding_service.get_node_embedding(node)
        node_id = vector_store.add_node(node, embedding)
        print(f"Added node with ID: {node_id}")
    
    # Test search functionality
    print("\nTesting search functionality...")
    
    search_terms = ["AI company", "software development", "CEO"]
    
    for term in search_terms:
        print(f"\nSearching for: '{term}'")
        results = vector_store.search_by_text(term)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results):
                print(f"{i+1}. {result['metadata']['name']} ({result['metadata']['type']})")
                print(f"   {result['metadata']['description']}")
        else:
            print("No results found")
    
    print("\nVector database test completed!")

if __name__ == "__main__":
    main()
