from typing import Optional
from backend.graph_components.Graph import Graph
from backend.utils.extractor import Extractor

class GraphConstructor:
    """
    A class for constructing and modifying graphs based on prompts and targets.
    
{{ ... }}
        prompt (str): The prompt used to guide graph construction.
        target (str): The target output or goal for the graph construction.
        graph (Graph): The graph object to be constructed or modified.
    """
    
    def __init__(self, prompt: str, target: str, graph: Graph):
        """
        Initialize a GraphConstructor object.
        
        Args:
            prompt (str): The prompt used to guide graph construction.
            target (str): The target output or goal for the graph construction.
            graph (Graph): The graph object to be constructed or modified.
        """
        self.prompt = prompt
        self.target = target
        self.graph = graph
    
    def construct_graph(self) -> Graph:
        """
        Construct or modify the graph based on the prompt and target.
        
        Returns:
            Graph: The constructed or modified graph.
        """
        extractor = Extractor(target=self.target, prompt=self.prompt, cache_path="./cache")
        # TODO: Implement proper extraction method once Extractor class is fully implemented
        # For now, we'll use empty collections
        Nodes = {}
        Edges = []
        self.graph.nodes = Nodes
        self.graph.edges = Edges
        return self.graph
    
 
    
    def __str__(self) -> str:
        """
        Return a string representation of the GraphConstructor.
        
        Returns:
            str: A string representation of the GraphConstructor.
        """
        return f"GraphConstructor(prompt='{self.prompt[:20]}...', target='{self.target[:20]}...', graph={self.graph})"