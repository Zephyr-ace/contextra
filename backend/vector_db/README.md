# Vector Database for Contextra

This module provides a vector database implementation for the Contextra application using ChromaDB.

## Overview

The vector database is used to store and retrieve Node embeddings for semantic search capabilities. It allows finding contextually similar nodes based on their name and description.

## Components

- `VectorStore`: Main class for interacting with the vector database
- `EmbeddingService`: Service for generating embeddings for nodes

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Import and use in your application:

```python
from vector_db import VectorStore
from vector_db.embedding_service import EmbeddingService
from graph_components.Node import Node

# Initialize services
embedding_service = EmbeddingService()
vector_store = VectorStore(collection_name="nodes", persist_directory="./chroma_db")

# Create a node
node = Node(
    name="Example Company",
    description="A technology company specializing in AI",
    type="Company"
)

# Generate embedding and store in vector DB
embedding = embedding_service.get_node_embedding(node)
node_id = vector_store.add_node(node, embedding)

# Search for similar nodes
results = vector_store.search_by_text("AI technology companies")
```

## Why ChromaDB?

ChromaDB was chosen for the following reasons:

1. **Ease of use**: Simple Python API that integrates well with our existing codebase
2. **Local deployment**: Can run embedded in the application without external services
3. **Hybrid search**: Supports both text and vector-based search
4. **Persistence**: Provides options for in-memory or disk-based storage
5. **Active development**: Regularly updated with new features and improvements

## Alternative Options

Other options that were considered:
- FAISS: Great performance but lacks metadata storage
- PostgreSQL + pgvector: More complex setup but provides full SQL capabilities
- Milvus: More suitable for larger-scale deployments
- Qdrant: Good option but ChromaDB's Python-native approach fits better with our stack
