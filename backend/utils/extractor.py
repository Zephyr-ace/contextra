from openAi_llm import LLM_OA
from prompts import promptNodeExtractor, promptDeepresearch, promptEdgeExtractor
from backend.graph_components.Edge import Edge
from backend.graph_components.Node import Node
from pydantic import BaseModel
import os
import json


class Extractor:

    def __init__(self, target: str, cache_path: str = "backend/data/cache/apple_deepresearch.txt"):
        self.target = target
        self.cache_path = cache_path
        self.nodes_cache_path = f"backend/data/cache/{target.lower()}_nodes.json"
        self.edges_cache_path = f"backend/data/cache/{target.lower()}_edges.json"
        # Use config for model selection
        self.llm_oa = LLM_OA("gpt-4.1")

        self.promptNodeExtractor = promptNodeExtractor
    def extract(self):
        """main method"""
        # Check if cached nodes and edges exist
        if os.path.exists(self.nodes_cache_path) and os.path.exists(self.edges_cache_path):
            nodes = self._load_nodes_from_cache()
            edges = self._load_edges_from_cache()
            print(f"Loaded {len(nodes)} nodes and {len(edges)} edges from cache")
            return nodes, edges

        research_output = self._fetch_data()
        nodes = self._extract_nodes(research_output)
        edges = self._extract_edges(nodes, research_output)

        # Cache the results
        self._save_nodes_to_cache(nodes)
        self._save_edges_to_cache(edges)

        return nodes, edges

    def _fetch_data(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as f:
                return f.read()

        prompt = promptDeepresearch.replace('{target}', self.target)
        research_output = self.llm_oa.deepresearch(prompt)

        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w') as f:
            f.write(research_output)

        return research_output

    def _extract_nodes(self, research_output):
        prompt = promptNodeExtractor + research_output
        nodes = self.llm_oa.generate_structured(prompt, NodesExtractionFormat)
        return nodes.nodes if hasattr(nodes, 'nodes') else []

    def _extract_edges(self, nodes, research_output):
        if len(nodes) < 2:
            print("Not enough nodes for edge extraction")
            return []

        node_titles = [node.title if hasattr(node, 'title') else str(node) for node in nodes]
        node_list_str = "\n".join([f"- {title}" for title in node_titles])

        prompt = promptEdgeExtractor.replace('{node_titles}', node_list_str) + f"\n\nResearch data:\n{research_output}"
        edges = self.llm_oa.generate_structured(prompt, EdgeExtractionFormat)
        return edges.edges if hasattr(edges, 'edges') else []

    def _save_nodes_to_cache(self, nodes):
        os.makedirs(os.path.dirname(self.nodes_cache_path), exist_ok=True)
        nodes_data = [node.model_dump() if hasattr(node, 'model_dump') else node.__dict__ for node in nodes]
        with open(self.nodes_cache_path, 'w') as f:
            json.dump(nodes_data, f, indent=2)

    def _save_edges_to_cache(self, edges):
        os.makedirs(os.path.dirname(self.edges_cache_path), exist_ok=True)
        edges_data = [edge.model_dump() if hasattr(edge, 'model_dump') else edge.__dict__ for edge in edges]
        with open(self.edges_cache_path, 'w') as f:
            json.dump(edges_data, f, indent=2)

    def _load_nodes_from_cache(self):
        with open(self.nodes_cache_path, 'r') as f:
            nodes_data = json.load(f)
        return [Node(**node_data) for node_data in nodes_data]

    def _load_edges_from_cache(self):
        with open(self.edges_cache_path, 'r') as f:
            edges_data = json.load(f)
        return [Edge(**edge_data) for edge_data in edges_data]

class NodesExtractionFormat(BaseModel):
    nodes: list[Node]

class EdgeExtractionFormat(BaseModel):
    edges: list[Edge]





