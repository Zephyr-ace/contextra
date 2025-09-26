from openAi_llm import LLM_OA
from prompts import promptNodeExtractor


class Extractor:

    def __init__(self, target: str, prompt:str, cache_path: str):
        self.target = target
        self.prompt = prompt
        self.cache_path = cache_path
        # Use config for model selection
        self.llm_oa = LLM_OA("gpt-4.1")

        self.promptNodeExtractor = promptNodeExtractor

    def extract_nodes(self, ):









