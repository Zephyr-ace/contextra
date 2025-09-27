"""
Enhanced Extractor that uses concise summary instead of raw research data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.openAi_llm import LLM_OA
from utils.prompts import promptNodeExtractor, promptEdgeExtractor
from graph_components.Node import Node
from graph_components.Edge import Edge
from pydantic import BaseModel
import json


class EnhancedExtractor:
    def __init__(self, target: str, summary_cache_path: str = None):
        self.target = target
        self.summary_cache_path = summary_cache_path or f"backend/demo_graph/{target.lower()}_summary_cache.txt"
        self.nodes_cache_path = f"backend/demo_graph/{target.lower()}_nodes.json"
        self.edges_cache_path = f"backend/demo_graph/{target.lower()}_edges.json"
        # Use structured generation model
        self.llm_oa = LLM_OA("gpt-4o")

    def extract_from_summary(self, summary_text: str):
        """Extract nodes and edges from the concise summary text"""
        print(f"Extracting from summary ({len(summary_text)} chars)...")

        # Check if both cached nodes and edges exist
        if os.path.exists(self.nodes_cache_path) and os.path.exists(self.edges_cache_path):
            nodes = self._load_nodes_from_cache()
            edges = self._load_edges_from_cache()
            print(f"Loaded {len(nodes)} nodes and {len(edges)} edges from cache")
            return nodes, edges

        # Extract nodes from summary
        if os.path.exists(self.nodes_cache_path):
            nodes = self._load_nodes_from_cache()
            print(f"Loaded {len(nodes)} nodes from cache")
        else:
            nodes = self._extract_nodes(summary_text)
            self._save_nodes_to_cache(nodes)
            print(f"Extracted {len(nodes)} nodes")

        # Extract edges using the nodes and summary
        edges = self._extract_edges(nodes, summary_text)
        self._save_edges_to_cache(edges)
        print(f"Extracted {len(edges)} edges")

        return nodes, edges

    def extract_from_summary_cache(self):
        """Load summary from cache and extract nodes/edges"""
        if not os.path.exists(self.summary_cache_path):
            raise FileNotFoundError(f"Summary cache not found at: {self.summary_cache_path}")

        with open(self.summary_cache_path, 'r', encoding='utf-8') as f:
            summary_text = f.read()

        return self.extract_from_summary(summary_text)

    def save_summary_cache(self, summary_text: str):
        """Save summary text to cache file"""
        os.makedirs(os.path.dirname(self.summary_cache_path), exist_ok=True)
        with open(self.summary_cache_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"Summary cache saved to: {self.summary_cache_path}")

    def _extract_nodes(self, summary_text: str):
        """Extract nodes from summary text"""
        prompt = promptNodeExtractor + f"\n\nText to analyze:\n{summary_text}"
        nodes = self.llm_oa.generate_structured(prompt, NodesExtractionFormat)
        return nodes.nodes if hasattr(nodes, 'nodes') else []

    def _extract_edges(self, nodes, summary_text: str):
        """Extract edges between nodes using summary text"""
        if len(nodes) < 2:
            print("Not enough nodes for edge extraction")
            return []

        node_titles = [node.title if hasattr(node, 'title') else str(node) for node in nodes]
        node_list_str = "\n".join([f"- {title}" for title in node_titles])

        prompt = promptEdgeExtractor.replace('{node_titles}', node_list_str) + f"\n\nText containing relationship evidence:\n{summary_text}"
        edges = self.llm_oa.generate_structured(prompt, EdgeExtractionFormat)
        return edges.edges if hasattr(edges, 'edges') else []

    def _save_nodes_to_cache(self, nodes):
        """Save nodes to cache file"""
        os.makedirs(os.path.dirname(self.nodes_cache_path), exist_ok=True)
        nodes_data = [node.model_dump() if hasattr(node, 'model_dump') else node.__dict__ for node in nodes]
        with open(self.nodes_cache_path, 'w') as f:
            json.dump(nodes_data, f, indent=2)

    def _save_edges_to_cache(self, edges):
        """Save edges to cache file"""
        os.makedirs(os.path.dirname(self.edges_cache_path), exist_ok=True)
        edges_data = [edge.model_dump() if hasattr(edge, 'model_dump') else edge.__dict__ for edge in edges]
        with open(self.edges_cache_path, 'w') as f:
            json.dump(edges_data, f, indent=2)

    def _load_nodes_from_cache(self):
        """Load nodes from cache file"""
        with open(self.nodes_cache_path, 'r') as f:
            nodes_data = json.load(f)
        return [Node(**node_data) for node_data in nodes_data]

    def _load_edges_from_cache(self):
        """Load edges from cache file"""
        with open(self.edges_cache_path, 'r') as f:
            edges_data = json.load(f)
        return [Edge(**edge_data) for edge_data in edges_data]


class NodesExtractionFormat(BaseModel):
    nodes: list[Node]


class EdgeExtractionFormat(BaseModel):
    edges: list[Edge]