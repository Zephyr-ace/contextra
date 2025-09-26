from __future__ import annotations

# OpenAI LLMs - kept for potential future use but not used by extractor
from openai import OpenAI, AsyncOpenAI
import asyncio
from pydantic import BaseModel

from typing import List, Dict, Optional, TypeVar, Type

T = TypeVar('T', bound=BaseModel)


class LLM_OA:
    def __init__(self, default_model: str):
        self.default_model = default_model
        self.model_name = default_model  # Add model_name attribute for caching
        self.client = OpenAI()  # nutzt automatisch environment variable "OPENAI_API_KEY"
        self.async_client = AsyncOpenAI()  # für parallele Verarbeitung

    async def __aenter__(self) -> "LLM_OA":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.async_client.close()

    def generate(self, prompt: str, model: str = None) -> str:
        model = model or self.default_model
        response = self.client.responses.create(
            model=model,
            input=[
                {"role": "user",
                 "content": prompt}
            ]
        )
        return response.output_text

    def generate_structured(self, prompt: str, desired_output_format: Type[T], model: str = None) -> T:
        model = model or self.default_model

        response = self.client.responses.parse(
            model=model,
            input=[{"role": "user", "content": prompt}],
            text_format=desired_output_format,
        )
        return response.output_parsed

    async def generate_structured_async(self, prompt: str, desired_output_format: Type[T],
                                        model: str = None, temperature: float = None) -> T:
        model = model or self.default_model

        # Create request parameters
        request_params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": desired_output_format
        }

        # Only add temperature if it's specified and supported
        if temperature is not None:
            request_params["temperature"] = temperature

        response = await self.async_client.beta.chat.completions.parse(**request_params)
        return response.choices[0].message.parsed

    async def generate_structured_parallel(self, prompts: list[str], desired_output_format: Type[T]) -> list[T]:
        async def generate_with_client(prompt: str) -> T:
            response = await self.async_client.responses.parse(
                model=self.default_model,
                input=[{"role": "user", "content": prompt}],
                text_format=desired_output_format,
            )
            return response.output_parsed

        tasks = [generate_with_client(prompt) for prompt in prompts]
        async_tasks = await asyncio.gather(*tasks)
        return async_tasks

    async def generate_async(self, prompt: str, model: str = None) -> str:
        model = model or self.default_model
        response = await self.async_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def generate_parallel(self, prompts: List[str], model: str = None) -> List[str]:
        """Generate responses for multiple prompts in parallel."""
        model = model or self.default_model

        async def generate_single(prompt: str) -> str:
            response = await self.async_client.responses.create(
                model=model,
                input=[{"role": "user", "content": prompt}]
            )
            return response.output_text

        tasks = [generate_single(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)

    def generate_structured_parallel_sync(self, prompts: list[str], desired_output_format: Type[T]) -> list[T]:
        async def run_with_new_client():
            async_client = AsyncOpenAI()
            try:
                async def generate_with_client(prompt: str) -> T:
                    response = await async_client.responses.parse(
                        model=self.default_model,
                        input=[{"role": "user", "content": prompt}],
                        text_format=desired_output_format,
                    )
                    return response.output_parsed

                tasks = [generate_with_client(prompt) for prompt in prompts]
                return await asyncio.gather(*tasks)
            finally:
                await async_client.close()

        return asyncio.run(run_with_new_client())





# FinBERT functionality has been moved to core/llm_finbert.py
# This file now contains only OpenAI LLM functionality for potential future use