"""
General utility functions for file handling, scraping, and MCP.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from .file_handler import read_yaml, write_yaml, read_json, write_json, read_text, write_text, download
from .validation import validate_markdown, validate_file
from .web_scraper import fetch_clean_text, save_to_file
from .mcp_client import MCPClient

__all__ = [
    "read_yaml", "write_yaml", "read_json", "write_json",
    "read_text", "write_text", "download",
    "validate_markdown", "validate_file",
    "fetch_clean_text", "save_to_file",
    "MCPClient"
]
