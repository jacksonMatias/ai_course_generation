"""
Ollama provider for Mistral:latest model running on localhost.

Integrates the Ollama Python client into the standardized AI provider interface.
Assumes Ollama is running locally with the mistral:latest model pulled.

Prerequisites:
- Install Ollama: https://ollama.com/download
- Pull Mistral model: `ollama pull mistral:latest`
- Start Ollama service: `ollama serve`

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import ollama
from ollama import ChatResponse

from .base_provider import BaseAIProvider, GenerationConfig


class OllamaProvider(BaseAIProvider):
    """
    Adapter for Ollama running locally with Mistral:latest model.
    """

    DEFAULT_MODEL: str = "mistral:latest"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:11434") -> None:
        # Ollama doesn't require API key for localhost
        super().__init__(api_key or "local", base_url)

        # Initialize Ollama client
        self.client = ollama.Client(host=base_url)

    def _generate(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text using Ollama's chat interface with Mistral model.
        """
        model = config.extra.get("model", self.DEFAULT_MODEL)

        try:
            if config.stream:
                # Streaming response
                response = self.client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                )

                # Collect streaming chunks
                collected_text: List[str] = []
                for chunk in response:
                    if hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                        collected_text.append(chunk.message.content)
                    elif isinstance(chunk, dict):
                        content = chunk.get('message', {}).get('content', '')
                        if content:
                            collected_text.append(content)

                return "".join(collected_text).strip()

            else:
                # Non-streaming response
                response: ChatResponse = self.client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False,
                )

                # Extract content from response
                if hasattr(response, 'message') and hasattr(response.message, 'content'):
                    return response.message.content.strip()
                elif isinstance(response, dict):
                    return response.get('message', {}).get('content', '').strip()
                else:
                    return str(response).strip()

        except Exception as exc:
            raise self.ProviderError(f"Ollama generation failed: {exc}") from exc

    def validate_api_key(self) -> None:
        """
        Test connection to Ollama by listing available models.
        """
        try:
            models = self.client.list()
            # Check if mistral:latest is available
            model_names = [model.get('name', '') for model in models.get('models', [])]
            if self.DEFAULT_MODEL not in model_names:
                raise self.ProviderError(
                    f"Model {self.DEFAULT_MODEL} not found. "
                    f"Please run: ollama pull {self.DEFAULT_MODEL}"
                )
        except Exception as exc:
            raise self.InvalidAPIKeyError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Ensure Ollama is running: ollama serve"
            ) from exc
