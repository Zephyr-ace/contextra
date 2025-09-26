"""
Minimal test script for ChromaDB functionality.
"""

import chromadb
import os

def main():
    print("Testing basic ChromaDB functionality...")
    
    # Create a directory for the database
    persist_dir = "./simple_chroma_test"
    os.makedirs(persist_dir, exist_ok=True)
    
    try:
        # Try to create a persistent client
        print("Attempting to create a persistent client...")
        client = chromadb.PersistentClient(path=persist_dir)
        print("✓ Successfully created persistent client")
    except Exception as e:
        print(f"✗ Failed to create persistent client: {e}")
        print("Falling back to in-memory client...")
        client = chromadb.Client()
        print("✓ Successfully created in-memory client")
    
    # Create a collection
    print("\nCreating a test collection...")
    try:
        collection = client.create_collection(name="test_collection")
        print("✓ Successfully created collection")
    except Exception as e:
        print(f"✗ Failed to create collection: {e}")
        return
    
    # Add some data
    print("\nAdding test data...")
    try:
        collection.add(
            ids=["id1", "id2"],
            embeddings=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            metadatas=[{"name": "Item 1"}, {"name": "Item 2"}],
            documents=["This is item 1", "This is item 2"]
        )
        print("✓ Successfully added data")
    except Exception as e:
        print(f"✗ Failed to add data: {e}")
        return
    
    # Query the data
    print("\nQuerying data...")
    try:
        results = collection.query(
            query_embeddings=[[1.0, 2.0, 3.0]],
            n_results=2
        )
        print("✓ Successfully queried data")
        print(f"Results: {results}")
    except Exception as e:
        print(f"✗ Failed to query data: {e}")
        return
    
    print("\nBasic ChromaDB test completed successfully!")

if __name__ == "__main__":
    main()
