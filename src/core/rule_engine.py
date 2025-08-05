"""
Applies *content-generation rules* so every prompt fed to the LLM
conforms to pedagogical, stylistic, and Bitcoin-SV-specific guidelines.

Rules come from three layers, merged in ascending priority:

1.  **Built-ins** – universal defaults that rarely change.
2.  **YAML config** – project-wide rules editable in
    `config/prompts.yaml`.
3.  **Per-call overrides** – ad-hoc adjustments supplied by the caller.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

import yaml


class RuleEngine:
    # ------------------------------------------------------------------ #
    # Layer 1 – Hard-coded fallbacks                                     #
    # ------------------------------------------------------------------ #
    _DEFAULT_RULES: Dict[str, Any] = {
        "format": "markdown",
        "tone": "professional and engaging",
        "target_audience": "intermediate learners",
        "length": "comprehensive but concise",
        "include_examples": True,
        "include_exercises": True,
        # NEW: Markdown style enforcement
        "markdown_style_guide": """You are a professional technical writer. Produce **Markdown** that follows:
        1. # (module), ## (lesson), ### (sub-lesson), #### (sub-sub).
        2. Plain paragraphs only – no HTML.
        3. Bullet lists: *   —   Numbered lists: 1.
        4. Block quotes with >.
        5. Code blocks wrapped in ```
        6. Avoid Markdown tables unless strictly necessary.
        7. Never include HTML tags or Markdown comments.
        Any output that violates these rules is invalid."""
    }

    # Content-type-specific deltas (applied *after* `_DEFAULT_RULES`)
    _TYPE_RULES: Dict[str, Dict[str, Any]] = {
        "course": {"length": "detailed, multi-module"},
        "lesson": {"length": "single-lesson depth"},
        "assessment": {"include_exercises": False},
    }

    # ------------------------------------------------------------------ #
    # Layer 2 – YAML project config                                      #
    # ------------------------------------------------------------------ #
    _PROJECT_RULES: Mapping[str, Any] = {}
    _CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "prompts.yaml"

    try:
        if _CONFIG_PATH.exists():
            with _CONFIG_PATH.open(encoding="utf-8") as fp:
                _PROJECT_RULES = yaml.safe_load(fp) or {}
    except Exception as exc:  # pragma: no cover – never fatal
        print(f"[RuleEngine] Failed to load prompt rules: {exc}")

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    @classmethod
    def system_text(cls, content_type: str) -> tuple[str, str]:
        """
        Return (system_prompt, system_directive) for a given content_type.
        Falls back to '' if not present in YAML.
        """
        prompts = cls._PROJECT_RULES.get("prompts", {})
        section = prompts.get(content_type, {})
        return (
            section.get("system_prompt", "").strip(),
            section.get("system_directive", "").strip(),
        )
    @classmethod
    def apply_rules(
        cls,
        content_type: str,
        custom_rules: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Merge the rule layers and return the **effective** rule set for
        the given `content_type`.

        Precedence (lowest → highest):
        built-ins → YAML project rules → type-specific → `custom_rules`.
        """
        content_type = content_type.lower().strip()
        custom_rules = custom_rules or {}

        # Built-ins
        merged: Dict[str, Any] = dict(cls._DEFAULT_RULES)

        # YAML project rules – may include a global section or per-type
        project_global = cls._PROJECT_RULES.get("content_rules", {})
        merged.update(project_global)

        project_per_type = cls._PROJECT_RULES.get("content_rules_by_type", {}).get(
            content_type, {}
        )
        merged.update(project_per_type)

        # Type-specific hard-coded deltas
        merged.update(cls._TYPE_RULES.get(content_type, {}))

        # Caller overrides last
        merged.update(custom_rules)

        return merged
