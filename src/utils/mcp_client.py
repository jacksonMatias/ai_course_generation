"""
Very thin wrapper around the **Model-Context-Protocol (MCP)** used by
this project to exchange *knowledge objects* (documents, embeddings,
metadata) with external services.

Why so small?
-------------
Most applications only need to:

1. `publish()` a freshly-scraped document to a remote knowledge base.
2. `query()` existing content for retrieval-augmented generation (RAG).
3. `health_check()` that a given MCP endpoint is alive.

Anything more complex (streaming embeddings, delta updates, etc.) should
live in `src/mcp_integration/`.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

LOGGER = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 20


class MCPClient:
    """
    Minimal client for JSON-over-HTTP MCP endpoints.
    """

    def __init__(self, endpoint: str, *, auth_token: Optional[str] = None) -> None:
        if not endpoint.startswith(("http://", "https://", "mcp://")):
            raise ValueError("Endpoint must start with http(s):// or mcp://")
        # Normalise mcp:// to https:// for transport
        self.base_url = endpoint.replace("mcp://", "https://")
        self.session = requests.Session()
        if auth_token:
            self.session.headers.update({"Authorization": f"Bearer {auth_token}"})
        self.session.headers.update({"User-Agent": "AI-Course-Generator/1.0"})

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def publish(
        self,
        *,
        title: str,
        text: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Publish a document (text) so that downstream LLM calls can
        retrieve it via MCP.

        Returns
        -------
        document_id (str)
        """
        payload = {
            "title": title,
            "text": text,
            "tags": tags or [],
            "metadata": metadata or {},
        }
        rsp = self._post("/v1/documents", payload)
        doc_id = rsp.get("id") or str(uuid.uuid4())
        LOGGER.info("Published document %s (%s chars)", doc_id, len(text))
        return doc_id

    def query(
        self,
        query: str,
        *,
        top_k: int = 5,
        filter_tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve **top_k** relevant snippets for the query.

        Returns
        -------
        List of {id, title, snippet, score}
        """
        payload = {"query": query, "top_k": top_k, "tags": filter_tags or []}
        rsp = self._post("/v1/query", payload)
        results = rsp.get("results", [])
        LOGGER.debug("MCP query returned %s hits", len(results))
        return results

    def health_check(self) -> bool:
        """
        Verify that the remote MCP endpoint is reachable.
        """
        try:
            self._get("/health")
            return True
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("MCP health-check failed: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        rsp = self.session.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        if not rsp.ok:
            raise RuntimeError(f"MCP POST {url} failed: HTTP {rsp.status_code}")
        return rsp.json()

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        rsp = self.session.get(url, timeout=DEFAULT_TIMEOUT)
        if not rsp.ok:
            raise RuntimeError(f"MCP GET {url} failed: HTTP {rsp.status_code}")
        return rsp.json()
