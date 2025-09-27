"""
Data Summarization Module for Apple Deep Research
Uses OpenAI reasoning model to summarize and structure the research data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.openAi_llm import LLM_OA
import json


class DataSummarizer:
    def __init__(self, reasoning_model="o3"):
        """Initialize with OpenAI reasoning model"""
        self.llm = LLM_OA(reasoning_model)

    def summarize_research_data(self, data_path: str, target: str = "Apple") -> dict:
        """
        Create concise summary focusing on most important entities and their impact

        Args:
            data_path: Path to the research data file
            target: Target entity (default: Apple)

        Returns:
            dict: Concise summary with key entities and impacts
        """
        # Read the research data
        with open(data_path, 'r', encoding='utf-8') as f:
            research_content = f.read()

        # Goal from the prompts - building context graph for reaction chains and impact measurement
        summarization_prompt = f"""
        GOAL: Create a concise summary to identify the most important entities that have a **direct and strong causal impact** on {target}. This summary will be used to build a context graph around {target} that can later trace reaction chains and measure event impacts.

        Your task is to analyze the research data and create a focused, concise summary that highlights:

        1. The 8-12 MOST CRITICAL entities that directly impact {target}
        2. HOW each entity impacts {target} (causal relationships)
        3. The STRENGTH of each impact (high/medium influence)

        Focus on entities in these categories:
        - Companies (suppliers, competitors, partners, contractors)
        - Sectors/Industries
        - Products or Services
        - Regulators / Institutions
        - Countries / Regions
        - Key People (executives, regulators, founders, political figures)

        RULES:
        • Focus ONLY on entities with clear, significant causal influence on {target}
        • Prioritize the biggest impact drivers first
        • Be concise but specific about HOW each entity affects {target}
        • Skip weak correlations or mere mentions

        IMPORTANT: Start your response by clearly stating the goal: "GOAL: To identify the most important entities with direct and strong causal impact on {target} for building a context graph that traces reaction chains and measures event impacts."

        Research Data:
        {research_content[:10000]}

        Provide a concise, focused summary that will serve as the foundation for entity extraction and graph building.
        """

        try:
            summary = self.llm.generate(summarization_prompt)

            # Structure the summary
            structured_summary = {
                "target": target,
                "summary_text": summary,
                "data_source": data_path,
                "model_used": self.llm.default_model,
                "summary_type": "concise_entities_impact"
            }

            return structured_summary

        except Exception as e:
            print(f"Error during summarization: {e}")
            return {
                "target": target,
                "error": str(e),
                "data_source": data_path
            }

    def save_summary(self, summary: dict, output_path: str):
        """Save summary to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Summary saved to: {output_path}")


def main():
    """Main function to run the summarizer"""
    # Initialize summarizer
    summarizer = DataSummarizer()

    # Path to Apple deep research data
    data_path = "backend/data/cache/apple_deepresearch.txt"

    # Check if data file exists
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    print(f"Summarizing data from: {data_path}")
    print("Using reasoning model for analysis...")

    # Generate summary
    summary = summarizer.summarize_research_data(data_path, "Apple")

    # Save summary
    output_path = "backend/demo_graph/apple_summary.json"
    summarizer.save_summary(summary, output_path)

    print("Summarization complete!")
    if "error" not in summary:
        print(f"Summary contains {len(summary['summary_text'])} characters")
    else:
        print(f"Error occurred: {summary['error']}")


if __name__ == "__main__":
    main()