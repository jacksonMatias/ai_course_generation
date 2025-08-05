"""
Configuration package for AI-Course-Generator.

Exposes:

* `settings` — runtime settings object backed by environment variables.
* YAML helper paths for prompts and knowledge-base sources.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from pathlib import Path

from .settings import settings  # re-export

# Useful absolute paths
PACKAGE_ROOT = Path(__file__).resolve().parent
PROMPTS_YAML = PACKAGE_ROOT / "prompts.yaml"
BSV_SOURCES_YAML = PACKAGE_ROOT / "bsv_sources.yaml"

__all__ = [
    "settings",
    "PACKAGE_ROOT",
    "PROMPTS_YAML",
    "BSV_SOURCES_YAML",
]
