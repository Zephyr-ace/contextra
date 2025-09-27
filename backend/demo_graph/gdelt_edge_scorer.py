"""
GDELT Edge Scorer for Apple Knowledge Graph
Integrates hybrid co-occurrence and causal weight scoring from GDELT analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import GDELT functions
gdelt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gdelt-analysis-main")
sys.path.append(gdelt_path)

# Import specific functions from the GDELT main.py
import importlib.util
spec = importlib.util.spec_from_file_location("gdelt_main", os.path.join(gdelt_path, "main.py"))
gdelt_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gdelt_main)

# Access functions from the loaded module
hybrid_cooccurrence = gdelt_main.hybrid_cooccurrence
get_causal_weight_score = gdelt_main.get_causal_weight_score

import json
import time
from typing import Dict, Any, List, Optional
import logging


class GDELTEdgeScorer:
    def __init__(self, date_range: Optional[Dict[str, str]] = None):
        """
        Initialize GDELT edge scorer

        Args:
            date_range: Dict with 'start_date' and 'end_date' in YYYY-MM-DD format
                       If None, uses default range (last 12 months)
        """
        self.date_range = date_range or {
            'start_date': '2023-10-01',  # About 12 months ago
            'end_date': '2024-09-30'     # Recent data
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_entity_names(self, graph_data: Dict[str, Any]) -> Dict[int, str]:
        """Extract clean entity names for GDELT queries"""
        entity_names = {}

        for node in graph_data['nodes']:
            node_id = node['id']
            name = node['name']

            # Clean entity names for better GDELT matching
            clean_name = self._clean_entity_name(name)
            entity_names[node_id] = clean_name

        return entity_names

    def _clean_entity_name(self, name: str) -> str:
        """Clean entity names for better GDELT matching"""
        # Remove common corporate suffixes
        name = name.replace(" Inc.", "").replace(" Corporation", "").replace(" Corp.", "")
        name = name.replace(" Company", "").replace(" Ltd.", "").replace(" LLC", "")

        # Handle specific cases
        name_mapping = {
            "Taiwan Semiconductor Manufacturing Co.": "TSMC",
            "People's Republic of China": "China",
            "India (Government & Manufacturing/Consumer Market)": "India",
            "U.S. & EU Antitrust Regulators": "antitrust regulators",
            "Global Smartphone Market Demand": "smartphone market",
            "App Developer Ecosystem": "app developers",
            "US DOJ Antitrust Case 2024": "DOJ Apple lawsuit",
            "EU DMA Compliance": "EU Digital Markets Act"
        }

        return name_mapping.get(name, name)

    def score_edge_cooccurrence(self, entity_a: str, entity_b: str) -> Dict[str, Any]:
        """
        Calculate hybrid co-occurrence score for an edge

        Args:
            entity_a: Source entity name
            entity_b: Target entity name

        Returns:
            Dict with co-occurrence metrics
        """
        try:
            self.logger.info(f"Scoring co-occurrence: {entity_a} -> {entity_b}")

            result = hybrid_cooccurrence(
                entity_a,
                entity_b,
                start_date=self.date_range['start_date'],
                end_date=self.date_range['end_date']
            )

            return {
                'cooccurrence_count': result['cooccurrence'],
                'entity_a_count': result['entity_a_count'],
                'entity_b_count': result['entity_b_count'],
                'jaccard_similarity': result['normalized_cooccurrence'],
                'total_documents': result['total_documents']
            }

        except Exception as e:
            self.logger.warning(f"Co-occurrence scoring failed for {entity_a} -> {entity_b}: {e}")
            return {
                'cooccurrence_count': 0,
                'entity_a_count': 0,
                'entity_b_count': 0,
                'jaccard_similarity': 0.0,
                'total_documents': 0,
                'error': str(e)
            }

    def score_edge_causal_weight(self, entity_a: str, entity_b: str) -> Dict[str, Any]:
        """
        Calculate causal weight scores for an edge (both directions)

        Args:
            entity_a: Source entity name
            entity_b: Target entity name

        Returns:
            Dict with causal weight metrics
        """
        try:
            self.logger.info(f"Scoring causal weights: {entity_a} <-> {entity_b}")

            result = get_causal_weight_score(
                entity_a,
                entity_b,
                start_date=self.date_range['start_date'],
                end_date=self.date_range['end_date']
            )

            # Normalize the weights (they are very small values)
            # Apply log transformation and scaling to make them more interpretable
            weight_a_to_b = result['weight_a_to_b']
            weight_b_to_a = result['weight_b_to_a']

            # Normalize weights to 0-1 scale with log transformation
            normalized_weight_a_to_b = self._normalize_causal_weight(weight_a_to_b)
            normalized_weight_b_to_a = self._normalize_causal_weight(weight_b_to_a)

            return {
                'raw_weight_a_to_b': weight_a_to_b,
                'raw_weight_b_to_a': weight_b_to_a,
                'normalized_weight_a_to_b': normalized_weight_a_to_b,
                'normalized_weight_b_to_a': normalized_weight_b_to_a,
                'jaccard_similarity': result['jaccard'],
                'avg_causal_strength': result['avg_strength'],
                'p_a_to_b': result['p_a_to_b'],
                'p_b_to_a': result['p_b_to_a'],
                'p_bidirectional': result['p_bidirectional'],
                'p_no_causal': result['p_no_causal'],
                'snippets_scored': result['n_scored']
            }

        except Exception as e:
            self.logger.warning(f"Causal weight scoring failed for {entity_a} <-> {entity_b}: {e}")
            return {
                'raw_weight_a_to_b': 0.0,
                'raw_weight_b_to_a': 0.0,
                'normalized_weight_a_to_b': 0.0,
                'normalized_weight_b_to_a': 0.0,
                'jaccard_similarity': 0.0,
                'avg_causal_strength': 0.0,
                'p_a_to_b': 0.0,
                'p_b_to_a': 0.0,
                'p_bidirectional': 0.0,
                'p_no_causal': 1.0,
                'snippets_scored': 0,
                'error': str(e)
            }

    def _normalize_causal_weight(self, weight: float, min_threshold: float = 1e-6) -> float:
        """
        Normalize very small causal weights to 0-1 scale

        Args:
            weight: Raw causal weight (very small number)
            min_threshold: Minimum threshold for normalization

        Returns:
            Normalized weight between 0-1
        """
        if weight <= 0:
            return 0.0

        # Apply log transformation for very small values
        import math
        if weight < min_threshold:
            return 0.0

        # Log scale normalization (adjust these parameters based on typical weight ranges)
        # Assuming typical weights are in range 1e-6 to 1e-2
        log_weight = math.log10(weight)
        log_min = math.log10(min_threshold)  # -6
        log_max = math.log10(1e-2)           # -2

        normalized = (log_weight - log_min) / (log_max - log_min)
        return max(0.0, min(1.0, normalized))

    def score_all_edges(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score all edges in the graph with GDELT metrics

        Args:
            graph_data: Apple knowledge graph data

        Returns:
            Updated graph data with GDELT scores
        """
        self.logger.info("Starting GDELT scoring for all edges...")

        # Extract entity names
        entity_names = self.extract_entity_names(graph_data)

        # Create a copy of the graph data
        updated_graph = json.loads(json.dumps(graph_data))

        total_edges = len(updated_graph['edges'])
        self.logger.info(f"Scoring {total_edges} edges...")

        for i, edge in enumerate(updated_graph['edges']):
            self.logger.info(f"Processing edge {i+1}/{total_edges}")

            source_id = edge['source']
            target_id = edge['target']

            source_name = entity_names.get(source_id, f"Node_{source_id}")
            target_name = entity_names.get(target_id, f"Node_{target_id}")

            # Score co-occurrence
            cooccur_scores = self.score_edge_cooccurrence(source_name, target_name)

            # Score causal weights
            causal_scores = self.score_edge_causal_weight(source_name, target_name)

            # Add GDELT scores to edge
            edge['gdelt_scores'] = {
                'cooccurrence': cooccur_scores,
                'causal_weights': causal_scores,
                'date_range': self.date_range,
                'source_entity': source_name,
                'target_entity': target_name
            }

            # Add a brief delay to avoid overwhelming GDELT
            time.sleep(0.5)

        # Update metadata
        updated_graph['metadata']['gdelt_scoring'] = {
            'date_range': self.date_range,
            'scorer_version': '1.0',
            'total_edges_scored': total_edges
        }

        self.logger.info("GDELT scoring complete!")
        return updated_graph

    def save_scored_graph(self, scored_graph: Dict[str, Any], output_path: str):
        """Save the scored graph to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scored_graph, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Scored graph saved to: {output_path}")

    def create_scoring_summary(self, scored_graph: Dict[str, Any]) -> str:
        """Create a summary of GDELT scoring results"""
        edges = scored_graph['edges']

        # Calculate summary statistics
        cooccurrence_scores = []
        causal_weights = []
        jaccard_scores = []

        for edge in edges:
            gdelt = edge.get('gdelt_scores', {})

            if 'cooccurrence' in gdelt:
                cooccur = gdelt['cooccurrence']
                cooccurrence_scores.append(cooccur.get('cooccurrence_count', 0))
                jaccard_scores.append(cooccur.get('jaccard_similarity', 0))

            if 'causal_weights' in gdelt:
                causal = gdelt['causal_weights']
                causal_weights.append(causal.get('normalized_weight_a_to_b', 0))
                causal_weights.append(causal.get('normalized_weight_b_to_a', 0))

        # Calculate statistics
        avg_cooccurrence = sum(cooccurrence_scores) / len(cooccurrence_scores) if cooccurrence_scores else 0
        avg_jaccard = sum(jaccard_scores) / len(jaccard_scores) if jaccard_scores else 0
        avg_causal_weight = sum(causal_weights) / len(causal_weights) if causal_weights else 0

        max_cooccurrence = max(cooccurrence_scores) if cooccurrence_scores else 0
        max_jaccard = max(jaccard_scores) if jaccard_scores else 0
        max_causal_weight = max(causal_weights) if causal_weights else 0

        summary = f"""
GDELT Edge Scoring Summary:
==========================
Date Range: {self.date_range['start_date']} to {self.date_range['end_date']}
Total Edges Scored: {len(edges)}

Co-occurrence Statistics:
- Average co-occurrence count: {avg_cooccurrence:.1f}
- Maximum co-occurrence count: {max_cooccurrence}
- Average Jaccard similarity: {avg_jaccard:.4f}
- Maximum Jaccard similarity: {max_jaccard:.4f}

Causal Weight Statistics:
- Average normalized causal weight: {avg_causal_weight:.4f}
- Maximum normalized causal weight: {max_causal_weight:.4f}

Top Co-occurring Pairs:
"""

        # Find top co-occurring pairs
        edge_cooccur = [(edge['title'], edge.get('gdelt_scores', {}).get('cooccurrence', {}).get('cooccurrence_count', 0)) for edge in edges]
        edge_cooccur.sort(key=lambda x: x[1], reverse=True)

        for title, count in edge_cooccur[:5]:
            summary += f"- {title}: {count} documents\n"

        return summary


def main():
    """Main function to score Apple graph edges with GDELT"""
    print("=== GDELT Edge Scorer for Apple Knowledge Graph ===")

    # Initialize scorer with recent date range
    scorer = GDELTEdgeScorer(date_range={
        'start_date': '2023-10-01',
        'end_date': '2024-09-30'
    })

    # Load Apple graph
    graph_path = "apple_graph.json"
    if not os.path.exists(graph_path):
        print(f"Error: Apple graph not found at {graph_path}")
        return

    with open(graph_path, 'r', encoding='utf-8') as f:
        graph_data = json.load(f)

    print(f"Loaded graph with {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")

    # Score all edges
    print("Starting GDELT scoring...")
    scored_graph = scorer.score_all_edges(graph_data)

    # Save scored graph
    output_path = "apple_graph_gdelt_scored.json"
    scorer.save_scored_graph(scored_graph, output_path)

    # Create and save summary
    summary = scorer.create_scoring_summary(scored_graph)
    print(summary)

    with open("gdelt_scoring_summary.txt", 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"✅ GDELT scoring complete!")
    print(f"   Scored graph: {output_path}")
    print(f"   Summary: gdelt_scoring_summary.txt")


if __name__ == "__main__":
    main()