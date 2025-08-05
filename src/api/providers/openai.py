"""
Concrete adapter for the OpenAI Chat Completions API.

It translates the generic interface defined in `BaseAIProvider`
into actual calls to `openai.ChatCompletion.create`, handling
parameter mapping, error translation, and response post-processing.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import openai
from openai import AuthenticationError, OpenAIError, RateLimitError

from .base_provider import BaseAIProvider, GenerationConfig


class OpenAIProvider(BaseAIProvider):
    """
    Adapter for `gpt-4o`, `gpt-4-turbo`, or any other ChatCompletion-capable
    OpenAI model.
    """

    # Default chat model; can be overridden per-request via `GenerationConfig.extra`
    DEFAULT_MODEL: str = "gpt-4o-mini"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        # Allow API key to come from env var for convenience
        api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        super().__init__(api_key, base_url)

        openai.api_key = self.api_key
        if base_url:
            openai.api_base = base_url

    # ------------------------------------------------------------------ #
    # Abstract-method implementations                                    #
    # ------------------------------------------------------------------ #
    def _generate(self, prompt: str, config: GenerationConfig) -> str:  # noqa: D401
        """
        Perform a ChatCompletion request and return **only** the assistant
        message content.
        """

        model = config.extra.get("model", self.DEFAULT_MODEL)

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                stop=config.stop or None,
                stream=config.stream,
            )
        except RateLimitError as exc:  # Transient – propagate as ProviderError
            raise self.ProviderError(
                "OpenAI rate-limit reached; please retry later."
            ) from exc
        except AuthenticationError as exc:  # Invalid / expired key
            raise self.InvalidAPIKeyError("Invalid OpenAI API key.") from exc
        except OpenAIError as exc:  # Any other SDK-level failure
            raise self.ProviderError(f"OpenAI error: {exc}") from exc

        # Non-streaming → we have the whole payload
        if not config.stream:
            # `choices[0].message.content` holds the assistant text
            return response.choices[0].message.content.strip()

        # Streaming → accumulate chunks
        full_text: List[str] = []
        for chunk in response:
            delta = chunk.choices[0].delta  # type: ignore[attr-defined]
            if "content" in delta:
                full_text.append(delta.content)
        return "".join(full_text).strip()

    def validate_api_key(self) -> None:  # noqa: D401
        """
        Lightweight validation by hitting `/models`.
        Raises `InvalidAPIKeyError` on failure.
        """
        try:
            # Ask for one model and immediately stop reading
            next(openai.Model.list()["data"])
        except AuthenticationError as exc:
            raise self.InvalidAPIKeyError("OpenAI API key rejected.") from exc
        except OpenAIError:
            # For other errors (network, etc.) we skip hard failure here;
            # they will surface during generation.
            pass
