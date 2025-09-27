from backend.graph_components.Graph import Graph
from backend.utils.extractor import Extractor

class Agent:
    def __init__(self, graph: Graph):
        self.graph = graph

    def get_important_nodes(self):
        """Identify the 10 most important nodes in the graph using OpenAI LLM.
        
        Returns:
            List[Node]: List of the 10 most important nodes from the graph
        """
        import json
        from backend.utils.openAi_llm import LLM_OA
        from pydantic import BaseModel
        from typing import List
        
        # Create a class to define the expected response format
        class ImportantNodesResponse(BaseModel):
            important_node_titles: List[str]
            reasoning: str
        
        # Convert nodes to a serializable format
        nodes_data = {}
        for title, node in self.graph.nodes.items():
            nodes_data[title] = {
                "name": node.name,
                "type": node.type,
                "description": node.description,
                "aliases": node.aliases
            }
        
        # Create the prompt for the LLM
        prompt = f"""Analyze the following graph nodes and identify the 10 most important ones.
        Consider factors such as:
        1. Centrality in the network
        2. Significance of the entity type
        3. Richness of description
        4. Potential impact or influence
        
        Here are all the nodes in the graph:
        {json.dumps(nodes_data, indent=2)}
        
        Return the 10 most important node titles in a list, along with your reasoning.
        """
        
        # Initialize the LLM with GPT-4
        llm = LLM_OA(default_model="gpt-4")
        
        try:
            # Get structured response from LLM
            response = llm.generate_structured(prompt, ImportantNodesResponse)
            
            # Get the nodes corresponding to the important node titles
            important_nodes = []
            for title in response.important_node_titles:
                if title in self.graph.nodes:
                    important_nodes.append(self.graph.nodes[title])
            
            print(f"Selected {len(important_nodes)} important nodes. Reasoning: {response.reasoning}")
            return important_nodes
            
        except Exception as e:
            print(f"Error identifying important nodes: {e}")
            # Fallback: return a subset of nodes if available
            node_list = list(self.graph.nodes.values())
            return node_list[:min(10, len(node_list))]

    def expand_node(self):
        # formulate_query
        # scrape_information
        # extract
        pass

    def append_to_graph(self, nodes, edges):
        """Append nodes and edges to the graph.
        
        Args:
            nodes (List[Node]): List of nodes to append
            edges (List[Edge]): List of edges to append
        """
        # Append each node individually
        for node in nodes:
            self.graph.appendNode(node)
            
        # Append each edge individually
        for edge in edges:
            self.graph.appendEdge(edge)