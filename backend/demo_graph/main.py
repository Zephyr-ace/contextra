"""
Main Demo Graph Generation Script
Orchestrates the entire process: summarization -> graph generation -> visualization
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(backend_dir))

from graph_generator import AppleGraphGenerator
from visualizer import GraphVisualizer
import time


def main():
    """Main orchestration function"""
    print("=" * 60)
    print("APPLE KNOWLEDGE GRAPH DEMO")
    print("=" * 60)
    print("This demo will:")
    print("1. Create concise summary using O3 reasoning model (with goal repetition)")
    print("2. Cache the summary and extract entities/relationships from it")
    print("3. Generate knowledge graph using enhanced extraction pipeline")
    print("4. Create JSON output of the complete graph")
    print("5. Generate NetworkX + Matplotlib visualizations")
    print("=" * 60)

    start_time = time.time()

    try:
        # Enhanced Graph Generation (includes O3 summarization internally)
        print("\n🌐 Step 1: Enhanced Graph Generation...")
        generator = AppleGraphGenerator()
        graph_data = generator.generate_graph()

        # Save graph JSON
        graph_json_path = os.path.join(backend_dir, "apple_graph.json")
        generator.save_graph_json(graph_data, graph_json_path)

        # Save graph summary
        summary_text = generator.get_graph_summary(graph_data)
        summary_path = os.path.join(backend_dir, "graph_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)

        print(f"✅ Graph generated with {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
        print(f"   JSON saved to: {graph_json_path}")

        # Step 2: Visualization
        print("\n📊 Step 2: Creating visualizations...")
        visualizer = GraphVisualizer()
        viz_output_dir = os.path.join(backend_dir, "visualizations")
        visualizer.generate_all_visualizations(graph_json_path, viz_output_dir)
        print(f"✅ Visualizations saved to: {viz_output_dir}")

        # Final Summary
        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"📁 Output directory: backend/demo_graph/")
        print("\nGenerated files:")
        print(f"   📄 apple_summary.json - Research data summary")
        print(f"   📄 apple_graph.json - Complete graph in JSON format")
        print(f"   📄 graph_summary.txt - Human-readable graph summary")
        print(f"   📊 visualizations/ - NetworkX + Matplotlib plots")
        print(f"      ├── apple_full_graph.png")
        print(f"      ├── apple_companies_subgraph.png")
        print(f"      └── apple_graph_statistics.png")

        # Print key statistics
        stats = graph_data['metadata']['statistics']
        print(f"\n📈 Graph Statistics:")
        print(f"   • Nodes: {stats['total_nodes']}")
        print(f"   • Edges: {stats['total_edges']}")
        print(f"   • Average importance: {stats['avg_importance_score']}")
        print(f"   • Node types: {len(stats['node_types'])}")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check the error above and ensure:")
        print("1. OpenAI API key is set in environment")
        print("2. Required Python packages are installed (networkx, matplotlib)")
        print("3. All file paths are accessible")


if __name__ == "__main__":
    main()