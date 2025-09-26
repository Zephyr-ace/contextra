"""
Simple test script for the vector database.
Run this from the backend directory with: python test_vector_db.py
"""

from vector_db.vector_store import VectorStore
from vector_db.embedding_service import EmbeddingService
from graph_components.Node import Node

def main():
    print("Initializing vector database and embedding service...")
    
    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStore(collection_name="test_nodes", persist_directory="./chroma_db")
    
    # Create a test node
    test_node = Node(
        name="Test Company",
        description="A test company for vector database demonstration",
        type="Company"
    )
    
    print(f"Created test node: {test_node.name} ({test_node.type})")
    print(f"Node title (from property): {test_node.title}")
    
    # Generate embedding
    print("Generating embedding for the node...")
    embedding = embedding_service.get_node_embedding(test_node)
    print(f"Embedding generated with {len(embedding)} dimensions")
    
    # Store in vector DB
    print("Storing node in vector database...")
    node_id = vector_store.add_node(test_node, embedding)
    print(f"Node stored with ID: {node_id}")
    
    # Search for the node
    print("\nSearching for 'test company'...")
    results = vector_store.search_by_text("test company")
    
    if results:
        print("Search results:")
        for i, result in enumerate(results):
            print(f"{i+1}. {result['metadata']['name']} ({result['metadata']['type']})")
            print(f"   {result['metadata']['description']}")
            if 'distance' in result and result['distance'] is not None:
                print(f"   Similarity: {1 - result['distance']:.4f}")
    else:
        print("No results found")
    
    print("\nVector database test completed successfully!")

if __name__ == "__main__":
    main()
