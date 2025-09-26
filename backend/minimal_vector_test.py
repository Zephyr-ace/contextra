"""
Minimal test for vector database functionality.
Run this from the backend directory with: python minimal_vector_test.py
"""

import os
import sys
from graph_components.Node import Node

def main():
    print("Starting minimal vector database test...")
    
    # Create a test node
    test_node = Node(
        name="Test Company",
        description="A test company for vector database demonstration",
        type="Company"
    )
    
    print(f"Created test node: {test_node.name}")
    print(f"Node title (via property): {test_node.title}")
    print(f"Node description: {test_node.description}")
    print(f"Node type: {test_node.type}")
    
    # Test ChromaDB basic functionality
    print("\nTesting ChromaDB basic functionality...")
    try:
        import chromadb
        print("✓ Successfully imported chromadb")
        
        # Create in-memory client
        client = chromadb.Client()
        print("✓ Successfully created ChromaDB client")
        
        # Create a collection
        collection = client.create_collection(name="test_collection")
        print("✓ Successfully created collection")
        
        # Add a simple embedding
        collection.add(
            ids=["test1"],
            embeddings=[[1.0, 2.0, 3.0]],
            metadatas=[{"name": test_node.name, "description": test_node.description}],
            documents=[f"{test_node.name}: {test_node.description}"]
        )
        print("✓ Successfully added data to collection")
        
        # Query the collection
        results = collection.query(
            query_embeddings=[[1.0, 2.0, 3.0]],
            n_results=1
        )
        print("✓ Successfully queried collection")
        print(f"Query results: {results}")
        
        print("\nBasic ChromaDB test passed!")
    except Exception as e:
        print(f"Error testing ChromaDB: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nMinimal vector database test completed!")

if __name__ == "__main__":
    main()
