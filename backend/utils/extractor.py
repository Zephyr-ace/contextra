from openAi_llm import LLM_OA
from prompts import promptNodeExtractor, promptDeepresearch
from graph_components.Edge import Edge
from graph_components.Node import Node


class Extractor:

    def __init__(self, target: str, prompt:str, cache_path: str = backend/data/cache/apple_deepresearch.txt):
        self.target = target
        self.prompt = prompt
        self.cache_path = cache_path
        # Use config for model selection
        self.llm_oa = LLM_OA("gpt-4.1")

        self.promptNodeExtractor = promptNodeExtractor
    def extract(self):
        """main method"""
        return nodes, edges

    def _fetch_data(self):
        # check if there is cache first if -> return research_output

        # promptDeepresearch = replace {target} with target
        research_output = self.llm_oa.deepresearch(promptDeepresearch)
        #save as cache under path
        return research_output

    def _extract_nodes(self, research_output):
        prompt = promptNodeExtractor + research_output
        nodes = self.llm_oa.generate_structured(prompt)
        return nodes

    def _extract_edges(self, nodes, research_output):
        nodes_titles =
        prompt = promptEdgeExtractor + research_output
        return edges









