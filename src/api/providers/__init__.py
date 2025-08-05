"""
Provider-specific implementations live in this sub-package.

Each module corresponds to a single AI provider,
implementing the BaseAIProvider interface.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from .base_provider import BaseAIProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
# from .cohere import CohereProvider

__all__ = [
    "BaseAIProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    # "CohereProvider",
    "OllamaProvider",
]
