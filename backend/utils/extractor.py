from openAi_llm import LLM_OA
from prompts import promptNodeExtractor, promptDeepresearch


class Extractor:

    def __init__(self, target: str, prompt:str, cache_path: str = backend/data/cache/apple_deepresearch.txt):
        self.target = target
        self.prompt = prompt
        self.cache_path = cache_path
        # Use config for model selection
        self.llm_oa = LLM_OA("gpt-4.1")

        self.promptNodeExtractor = promptNodeExtractor

    def fetch_data(self):
        # check if there is cache first

        # promptDeepresearch = replace {target} with target
        research_output self.llm_oa.deepresearch(promptDeepresearch)
        return research_output
    def extract_nodes(self, ):









