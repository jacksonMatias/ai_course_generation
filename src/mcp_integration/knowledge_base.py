"""
High-level wrapper that combines the **web-scraper**, **MCP client** and
local caching to keep an *up-to-date* Bitcoin-SV knowledge corpus.

Typical flow
------------
from src.mcp_integration.knowledge_base import KnowledgeBase

kb = KnowledgeBase("mcp://bsv-knowledge")
kb.sync_url("https://bitcoinsv.academy/learn/overview")
snippets = kb.search("merchant api fee structure", top_k=3)

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import List

from ..utils import web_scraper
from ..utils.file_handler import read_text, write_text
from ..utils.mcp_client import MCPClient

LOGGER = logging.getLogger(__name__)

# Where scraped originals are cached locally
_CACHE_DIR = Path(__file__).resolve().parents[2] / "src" / "data" / "bsv_sources"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class KnowledgeBase:
    """
    Glue layer that hides all persistence & network details behind
    three intuitive methods: `sync_url`, `sync_file`, and `search`.
    """

    def __init__(self, mcp_endpoint: str):
        self.client = MCPClient(mcp_endpoint)

    # ------------------------------------------------------------------ #
    # Ingestion                                                           #
    # ------------------------------------------------------------------ #
    def sync_url(self, url: str, *, force: bool = False) -> str:
        """
        Download the web page (respecting robots.txt) *once*, cache it,
        and publish to MCP (idempotent).  Returns MCP document id.
        """
        cache_file = _CACHE_DIR / (self._slugify(url) + ".txt")
        if cache_file.exists() and not force:
            LOGGER.debug("Using cached copy for %s", url)
            text = read_text(cache_file)
        else:
            text = web_scraper.fetch_clean_text(url)
            write_text(text, cache_file)

        doc_id = self.client.publish(title=url, text=text, tags=["bsv", "web"])
        return doc_id

    def sync_file(self, path: str | Path, *, tags: List[str] | None = None) -> str:
        """
        Push a *local* document (Markdown, PDF-text, etc.) into MCP.
        """
        path = Path(path)
        text = read_text(path)
        doc_id = self.client.publish(
            title=path.name, text=text, tags=(tags or ["bsv", "file"])
        )
        return doc_id

    # ------------------------------------------------------------------ #
    # Retrieval                                                           #
    # ------------------------------------------------------------------ #
    def search(self, query: str, *, top_k: int = 5) -> List[str]:
        """
        Return plain-text snippets from the MCP knowledge base.
        """
        results = self.client.query(query, top_k=top_k, filter_tags=["bsv"])
        return [r.get("snippet", "") for r in results]

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _slugify(url: str) -> str:
        """
        Convert URL into filesystem-safe slug.
        """
        return uuid.uuid5(uuid.NAMESPACE_URL, url).hex
