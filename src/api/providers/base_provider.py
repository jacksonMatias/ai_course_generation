"""
Base interface for all AI text-generation providers used by the
AI-Course-Generator project.

Every concrete provider ― OpenAI, Anthropic, Cohere, etc. ― **must**
derive from `BaseAIProvider` and fully implement the abstract methods
declared here.  This abstraction lets the rest of the code work with a
single, unified API no matter which vendor backs the model.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GenerationConfig:
    """
    Settings that control a single generation request.
    Extend this class as needed for additional parameters that are
    common to most providers.
    """
    max_tokens: int = 1_024
    temperature: float = 0.7
    top_p: float = 1.0
    stop: Optional[List[str]] = field(default_factory=list)
    stream: bool = False
    # Provider-specific extra parameters live here.
    extra: Dict[str, Any] = field(default_factory=dict)


class BaseAIProvider(ABC):
    """
    Abstract base class defining the contract for provider adapters.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        if not api_key:
            raise ValueError("API key must not be empty.")
        self.api_key = api_key
        self.base_url = base_url
        # Each provider may maintain a persistent system prompt.
        self._system_prompt: str | None = None

        # Fail fast if the key is invalid (network call is provider-specific).
        if api_key is not None and api_key != "local":
            self.validate_api_key()

    # --------------------------------------------------------------------- #
    # Public high-level API                                                #
    # --------------------------------------------------------------------- #
    def set_system_prompt(self, prompt: str) -> None:
        """
        Persist a *system* prompt that will be automatically prepended to
        every subsequent generation request.
        """
        self._system_prompt = prompt.strip()

    def generate_text(
        self,
        prompt: str,
        *,
        config: GenerationConfig | None = None,
    ) -> str:
        """
        Main entry point used by the rest of the application.
        Handles merging the system prompt (if any) with the user prompt and
        delegates to the provider-specific `_generate` method.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        full_prompt = (
            f"{self._system_prompt}\n\n{prompt}" if self._system_prompt else prompt
        )

        # Provider-specific generation
        return self._generate(full_prompt, config or GenerationConfig())

    # --------------------------------------------------------------------- #
    # Abstract ­– must be implemented by subclasses                         #
    # --------------------------------------------------------------------- #
    @abstractmethod
    def _generate(self, prompt: str, config: GenerationConfig) -> str:  # noqa: D401
        """
        Actually perform the remote call to the underlying model and
        return the generated text.

        Implementations should:
        * Map the generic `GenerationConfig` to the provider’s parameter
          set.
        * Handle errors gracefully and raise a provider-specific subclass
          of `ProviderError` (defined below) on failure.
        * Return **only** the model’s textual response.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_api_key(self) -> None:  # noqa: D401
        """
        Make a lightweight call (e.g., ‘GET /models’) to verify that the
        provided API key is valid and has sufficient quota.
        Should raise `InvalidAPIKeyError` on failure.
        """
        raise NotImplementedError

    # --------------------------------------------------------------------- #
    # Exception hierarchy                                                   #
    # --------------------------------------------------------------------- #
    class ProviderError(RuntimeError):
        """Generic wrapper for provider-specific errors."""

    class InvalidAPIKeyError(ProviderError):
        """Raised when the supplied API key is rejected by the provider."""
