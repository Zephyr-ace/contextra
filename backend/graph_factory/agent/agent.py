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
        1. Connectivity in the network
        2. Significance of the entity type
        3. Potential impact or influence
        
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
        """Expand the graph by identifying important nodes and their connections.
        
        This function:
        1. Gets important nodes from the graph
        2. For each important node, uses LLM to identify related entities
        3. Uses the Extractor to extract nodes and edges
        4. Appends the new nodes and edges to the graph
        
        Returns:
            tuple: (List of new nodes added, List of new edges added)
        """
        from backend.utils.openAi_llm import LLM_OA
        from backend.utils.prompts import promptAgentExpandNode, promptNodeExtractor, promptEdgeExtractor
        from pydantic import BaseModel
        from typing import List, Dict, Any
        import json
        
        # Get important nodes from the graph
        important_nodes = self.get_important_nodes()
        
        if not important_nodes:
            print("No important nodes found to expand.")
            return [], []
            
        # Initialize LLM
        llm = LLM_OA(default_model="gpt-4")
        
        # Track all new nodes and edges
        all_new_nodes = []
        all_new_edges = []
        
        # Process each important node
        for node in important_nodes:
            print(f"Expanding node: {node.title}")
            
            try:
                # 1. Use promptAgentExpandNode to get related entities
                expand_prompt = promptAgentExpandNode.replace('{target}', node.title)
                research_output = llm.generate(expand_prompt)
                
                # 2. Create an Extractor for this node
                extractor = Extractor(target=node.title)
                
                # 3. Extract nodes and edges using the research output
                # Override the _fetch_data method to use our research output
                original_fetch_data = extractor._fetch_data
                extractor._fetch_data = lambda: research_output
                
                # Extract nodes and edges
                new_nodes, new_edges = extractor.extract()
                
                # Restore original method
                extractor._fetch_data = original_fetch_data
                
                # 4. Add to our collection of new nodes and edges
                all_new_nodes.extend(new_nodes)
                all_new_edges.extend(new_edges)
                
                print(f"Added {len(new_nodes)} nodes and {len(new_edges)} edges from {node.title}")
                
            except Exception as e:
                print(f"Expanded node {node.title}: {e}")
        
        # 5. Append all new nodes and edges to the graph
        if all_new_nodes or all_new_edges:
            self.append_to_graph(all_new_nodes, all_new_edges)
            
        return all_new_nodes, all_new_edges

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