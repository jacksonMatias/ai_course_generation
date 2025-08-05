"""
Unified façade that exposes a *single* API no matter which underlying
vendor (OpenAI, Anthropic, Cohere, …) is used.

Other layers of the application never import provider-specific classes
directly.  They depend only on `StandardizedAI`, which internally
instantiates the correct adapter.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from typing import Dict, Type

from .providers.base_provider import BaseAIProvider, GenerationConfig
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.ollama import OllamaProvider

class UnsupportedProviderError(ValueError):
    """Raised when an unknown provider name is supplied."""


class StandardizedAI:
    """
    Factory + facade that hides provider heterogeneity.

    Example
    -------
    >>> ai = StandardizedAI("openai", api_key="sk-…")
    >>> ai.set_system_prompt("You are a helpful assistant.")
    >>> ai.generate_text("Explain Bitcoin SV in one paragraph.")
    """

    _PROVIDER_MAP: Dict[str, Type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        # "cohere": CohereProvider,
        "ollama": OllamaProvider,

    }

    # ------------------------------------------------------------------ #
    # Construction                                                       #
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        provider: str,
        api_key: str,
        *,
        base_url: str | None = None,
    ) -> None:
        provider = provider.lower().strip()
        if provider not in self._PROVIDER_MAP:
            raise UnsupportedProviderError(
                f"Provider '{provider}' is not supported. "
                f"Choose from: {', '.join(self._PROVIDER_MAP)}"
            )

        provider_cls = self._PROVIDER_MAP[provider]
        self._adapter: BaseAIProvider = provider_cls(api_key=api_key, base_url=base_url)
        self.name: str = provider

    # ------------------------------------------------------------------ #
    # Public façade – simply delegate to the underlying adapter          #
    # ------------------------------------------------------------------ #
    def set_system_prompt(self, prompt: str) -> None:
        self._adapter.set_system_prompt(prompt)

    def generate_text(
        self,
        prompt: str,
        *,
        config: GenerationConfig | None = None,
    ) -> str:
        return self._adapter.generate_text(prompt, config=config)

    # ------------------------------------------------------------------ #
    # Helper tailored for course-content generation                      #
    # ------------------------------------------------------------------ #
    def generate_course_content(
        self,
        prompt: str,
        rules: Dict[str, str] | None = None,
        *,
        content_type: str = "course",
        config: GenerationConfig | None = None,
    ) -> str:
        from ..core.rule_engine import RuleEngine
        """
        Build the **full** prompt in five layers (top → bottom):

        1. system_prompt         (from prompts.yaml)
        2. markdown_style_guide  (from rules)
        3. system_directive      (from prompts.yaml)
        4. caller prompt         (argument)
        5. bullet-point meta-rules (everything left in `rules`)
        """
        # -------------------------------------------------- 1 & 3
        sys_prompt, sys_directive = RuleEngine.system_text(content_type)

        # -------------------------------------------------- 2
        style_guide = (rules or {}).get("markdown_style_guide", "").strip()

        # -------------------------------------------------- 5
        other_rules = {
            k: v for k, v in (rules or {}).items()
            if k != "markdown_style_guide"
        }
        bullets = (
            "\nPlease follow these rules:\n"
            + "\n".join(f"- **{k}**: {v}" for k, v in other_rules.items())
            if other_rules else ""
        )

        # ----------- compose final prompt ------------
        final_prompt = "\n\n".join(
            part for part in (
                style_guide,
                sys_directive,
                prompt.strip()
            ) if part                       # drop empty parts
        ) + bullets

        # Set/override the provider’s **system prompt**
        if sys_prompt:
            self._adapter.set_system_prompt(sys_prompt)

        # Fire the request
        return self.generate_text(final_prompt, config=config)
