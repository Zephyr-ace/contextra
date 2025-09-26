"""
Example demonstrating the enhanced duplicate checking with vector similarity.
"""

from graph_components.Graph import Graph
from graph_components.Node import Node
from graph_creation_pipeline.integrityCheck import IntegrityCheck

def main():
    print("Initializing graph with vector database...")
    graph = Graph(bidirectional=False, use_vector_db=True, collection_name="duplicate_check_example", reset_db=True)
    
    # Create integrity checker
    integrity_checker = IntegrityCheck(similarity_threshold=0.8)
    
    # Create some initial nodes
    print("\nAdding initial nodes to the graph...")
    nodes = [
        Node(
            name="Microsoft Corporation",
            description="A multinational technology company that develops and sells computer software, consumer electronics, and personal computers.",
            type="Company"
        ),
        Node(
            name="Google",
            description="A technology company specializing in Internet-related services and products, including search, cloud computing, and advertising technologies.",
            type="Company"
        ),
        Node(
            name="Cloud Computing",
            description="The delivery of computing services over the internet to offer faster innovation, flexible resources, and economies of scale.",
            type="Concept"
        )
    ]
    
    # Add nodes to graph
    for node in nodes:
        print(f"Adding node: {node.name}")
        graph.appendNode(node)
    
    print(f"\nGraph now has {len(graph.nodes)} nodes")
    
    # Now try to add some potential duplicates
    print("\nChecking potential duplicate nodes...")
    
    test_nodes = [
        # Exact duplicate
        Node(
            name="Microsoft Corporation",
            description="A multinational technology company that develops and sells computer software, consumer electronics, and personal computers.",
            type="Company"
        ),
        # Similar name but different description
        Node(
            name="Microsoft",
            description="An American multinational technology company headquartered in Redmond, Washington.",
            type="Organization"
        ),
        # Different name but similar description
        Node(
            name="Alphabet Inc.",
            description="A technology company specializing in Internet services, including search, cloud computing, and online advertising.",
            type="Company"
        ),
        # Completely different node
        Node(
            name="Tesla",
            description="An American electric vehicle and clean energy company.",
            type="Company"
        )
    ]
    
    # Check each node for duplicates
    for i, test_node in enumerate(test_nodes):
        print(f"\nChecking node {i+1}: {test_node.name}")
        is_duplicate, info = integrity_checker.checkDuplicates(test_node, graph)
        
        if is_duplicate:
            print(f"✗ DUPLICATE DETECTED: {info['reason']}")
            print(f"  Similarity: {info['similarity']:.2f}")
            print(f"  Similar to: {info['node'].name} - {info['node'].description}")
        else:
            print(f"✓ Not a duplicate - adding to graph")
            graph.appendNode(test_node)
    
    print(f"\nFinal graph has {len(graph.nodes)} nodes")
    
    # Demonstrate text-based similarity search
    print("\nDemonstrating text-based similarity search...")
    search_query = "technology company software"
    print(f"Searching for: '{search_query}'")
    
    similar_nodes = graph.find_similar_by_text(search_query, top_k=3)
    
    if similar_nodes:
        print(f"Found {len(similar_nodes)} similar nodes:")
        for i, result in enumerate(similar_nodes):
            print(f"{i+1}. {result['metadata']['name']} ({result['metadata']['type']})")
            print(f"   {result['metadata']['description']}")
            if 'distance' in result and result['distance'] is not None:
                similarity = 1.0 - result['distance']
                print(f"   Similarity: {similarity:.2f}")
    else:
        print("No similar nodes found")
    
    print("\nExample completed!")

if __name__ == "__main__":
    main()
