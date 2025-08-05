# """
# Concrete adapter for the Cohere Chat / Generate API.

# This class turns the generic `BaseAIProvider` interface into actual
# calls to Cohere’s SDK, handling parameter mapping, error translation,
# and streaming aggregation.

# Author : AI-Course-Generator
# Created: 2025-08-04
# """

# from __future__ import annotations

# import os
# from typing import List

# import cohere
# from cohere import CohereAPIError, CohereConnectionError, CohereAPIKeyError

# from .base_provider import BaseAIProvider, GenerationConfig


# class CohereProvider(BaseAIProvider):
#     """
#     Adapter targeting Cohere’s Command family (`command-r`, `command-r-plus`)
#     using the Chat endpoint (preferred) or fallback to `generate`.
#     """

#     DEFAULT_MODEL: str = "command-r-plus"

#     def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
#         # Allow API key via env var
#         api_key = api_key or os.getenv("COHERE_API_KEY", "")
#         super().__init__(api_key, base_url)

#         # Initialise the client
#         self.client = cohere.Client(api_key=self.api_key, base_url=base_url)

#     # ------------------------------------------------------------------ #
#     # Abstract-method implementations                                    #
#     # ------------------------------------------------------------------ #
#     def _generate(self, prompt: str, config: GenerationConfig) -> str:  # noqa: D401
#         """
#         Uses Cohere’s *chat* endpoint when available (streaming supported);
#         otherwise falls back to *generate*.
#         """

#         model = config.extra.get("model", self.DEFAULT_MODEL)

#         try:
#             # Chat endpoint supports streaming natively
#             if config.stream:
#                 stream = self.client.chat_stream(
#                     model=model,
#                     message=prompt,
#                     temperature=config.temperature,
#                     max_tokens=config.max_tokens,
#                     p=config.top_p,
#                     stop_sequences=config.stop or None,
#                 )
#                 chunks: List[str] = []
#                 for chunk in stream:
#                     if chunk.event_type == "text-generation":
#                         chunks.append(chunk.text)
#                 return "".join(chunks).strip()

#             # Non-streaming chat
#             response = self.client.chat(
#                 model=model,
#                 message=prompt,
#                 temperature=config.temperature,
#                 max_tokens=config.max_tokens,
#                 p=config.top_p,
#                 stop_sequences=config.stop or None,
#             )
#             return response.text.strip()

#         except CohereAPIKeyError as exc:
#             raise self.InvalidAPIKeyError("Invalid Cohere API key.") from exc
#         except CohereConnectionError as exc:
#             raise self.ProviderError("Network error talking to Cohere.") from exc
#         except CohereAPIError as exc:
#             raise self.ProviderError(f"Cohere API error: {exc}") from exc

#     def validate_api_key(self) -> None:  # noqa: D401
#         """
#         Validates the API key with a lightweight request (`tokenize`).
#         """
#         try:
#             self.client.tokenize("ping")
#         except CohereAPIKeyError as exc:
#             raise self.InvalidAPIKeyError("Cohere API key rejected.") from exc
#         except CohereAPIError:
#             # Other errors (quota, etc.) will surface at generation time
#             pass
