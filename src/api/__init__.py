"""
AI provider abstraction layer.

This module provides a unified interface for working with different
AI text-generation providers (OpenAI, Anthropic, Cohere) through
the `StandardizedAI` façade.

Example
-------
from src. appeal import StandardizedAI

ai = StandardizedAI("openai", api_key="sk-...")
ai.set_system_prompt("You are a Bitcoin SV expert educator.")
response = ai.generate_text("Explain UTXOs in simple terms.")

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from .standardized_api import StandardizedAI

__all__ = [
    "StandardizedAI",
]

