"""
Concrete adapter for the Anthropic Claude API.

Translates the generic interface from `BaseAIProvider` into actual
calls to Anthropic's Messages API, handling parameter mapping,
error translation, and response processing.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import anthropic
from anthropic import Anthropic, APIError, AuthenticationError, RateLimitError

from .base_provider import BaseAIProvider, GenerationConfig


class AnthropicProvider(BaseAIProvider):
    """
    Adapter for Claude models (claude-3-5-sonnet-20241022, claude-3-haiku, etc.)
    using Anthropic's Messages API.
    """

    # Default model; can be overridden per-request via `GenerationConfig.extra`
    DEFAULT_MODEL: str = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        # Allow API key to come from env var for convenience
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        super().__init__(api_key, base_url)

        # Initialize the Anthropic client
        self.client = Anthropic(
            api_key=self.api_key,
            base_url=base_url
        )

    # ------------------------------------------------------------------ #
    # Abstract-method implementations                                    #
    # ------------------------------------------------------------------ #
    def _generate(self, prompt: str, config: GenerationConfig) -> str:  # noqa: D401
        """
        Perform a Messages API request and return the assistant's response.
        """

        model = config.extra.get("model", self.DEFAULT_MODEL)

        # Claude expects separate system and user messages
        messages = [{"role": "user", "content": prompt}]

        # Extract system prompt if it exists in the full prompt
        system_prompt = None
        if self._system_prompt:
            # Remove system prompt from user message since we'll send it separately
            user_content = prompt.replace(f"{self._system_prompt}\n\n", "")
            messages = [{"role": "user", "content": user_content}]
            system_prompt = self._system_prompt

        try:
            # Map stop sequences (Claude uses different parameter name)
            stop_sequences = config.stop if config.stop else None

            message = self.client.messages.create(
                model=model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                stop_sequences=stop_sequences,
                system=system_prompt,  # System prompt goes here
                messages=messages,
                stream=config.stream,
            )

        except RateLimitError as exc:  # Rate limit exceeded
            raise self.ProviderError(
                "Anthropic rate-limit reached; please retry later."
            ) from exc
        except AuthenticationError as exc:  # Invalid API key
            raise self.InvalidAPIKeyError("Invalid Anthropic API key.") from exc
        except APIError as exc:  # Any other Anthropic API error
            raise self.ProviderError(f"Anthropic API error: {exc}") from exc

        # Handle streaming response
        if config.stream:
            full_text: List[str] = []
            for chunk in message:
                if chunk.type == "content_block_delta":
                    if hasattr(chunk.delta, 'text'):
                        full_text.append(chunk.delta.text)
            return "".join(full_text).strip()

        # Non-streaming response - extract text content
        content_blocks = message.content
        if not content_blocks:
            return ""

        # Claude returns content as a list of blocks, usually text blocks
        text_content = []
        for block in content_blocks:
            if hasattr(block, 'text'):
                text_content.append(block.text)
            elif hasattr(block, 'content') and isinstance(block.content, str):
                text_content.append(block.content)

        return "".join(text_content).strip()

    def validate_api_key(self) -> None:  # noqa: D401
        """
        Lightweight validation by making a minimal API call.
        Raises `InvalidAPIKeyError` on failure.
        """
        try:
            # Make a minimal request to validate the key
            self.client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
        except AuthenticationError as exc:
            raise self.InvalidAPIKeyError("Anthropic API key rejected.") from exc
        except APIError:
            # For other errors (network, quota, etc.) we skip hard failure here;
            # they will surface during actual generation.
            pass
        except Exception:
            # Catch any other unexpected errors during validation
            pass

    def set_system_prompt(self, prompt: str) -> None:
        """
        Override to handle Claude's system prompt format properly.
        """
        super().set_system_prompt(prompt)
