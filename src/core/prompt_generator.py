"""
Centralised helper that builds *well-formed* prompts for the underlying
LLM, sourcing reusable prompt text from **YAML configuration** as well
as lightweight f-strings.

By funnelling all prompt construction through this module we ensure that
every course, lesson, or assessment request follows a consistent
structure and that future prompt-engineering tweaks are strictly
DRY (defined once in `config/prompts.yaml`).

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any, Dict, Mapping

import yaml

# ---------------------------------------------------------------------- #
# Configuration loading                                                  #
# ---------------------------------------------------------------------- #
_CONFIG_PATH = (
    Path(__file__).resolve().parents[1] / "config" / "prompts.yaml"
)  # …/src/core → up 2 → config/prompts.yaml


def _load_yaml(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Prompt configuration file not found: {path}")
    with path.open(encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


_PROMPT_CFG: Mapping[str, Any] = _load_yaml(_CONFIG_PATH)


# ---------------------------------------------------------------------- #
# Prompt-building class                                                  #
# ---------------------------------------------------------------------- #
class PromptGenerator:
    """
    High-level façade providing *semantic* methods such as
    `build_course_outline()` or `build_lesson_content()` instead of
    scattering raw f-strings throughout the codebase.
    """

    # ------------------------------------------------------------------ #
    # Course-level prompts                                               #
    # ------------------------------------------------------------------ #
    def build_course_outline(self, *, topic: str, duration: str, level: str) -> str:
        """
        Returns a prompt that asks the model to craft a full course outline
        (modules, lessons, assessments) for the given **Bitcoin SV** topic.
        """

        base = textwrap.dedent(
            """
            Create a comprehensive course outline about **{topic}** on the
            Bitcoin SV blockchain.

            Guidelines:
            - Audience level: {level}
            - Total course duration: {duration}
            - Structure the outline into clear *Modules* and *Lessons*.
            - Provide learning objectives for each module.
            - Conclude with a capstone project idea and assessment types.

            Use Markdown headings (## Module, ### Lesson) so the output can be
            rendered as a document directly.
            """
        ).strip()

        # Enrich with any additional instruction snippets from YAML
        extras = _PROMPT_CFG.get("bsv_prompts", {}) \
                            .get("course_generation", {}) \
                            .get("extra_guidelines", "")

        return base.format(topic=topic, level=level, duration=duration) + (
            f"\n\n{extras.strip()}" if extras else ""
        )

    # ------------------------------------------------------------------ #
    # Section / lesson prompts                                           #
    # ------------------------------------------------------------------ #
    def build_lesson_content(self, *, lesson_topic: str, include_code: bool = True) -> str:
        """
        Prompt the model to generate the *detailed* content for a single
        lesson of the Bitcoin SV course.
        """

        base = textwrap.dedent(
            """
            Write the full lesson content for **{lesson_topic}** within a Bitcoin SV
            course.

            Requirements:
            - Begin with a concise lesson overview and 3–5 learning outcomes.
            - Explain each concept clearly, followed by a real-world BSV example.
            - {code_clause}
            - End with 3 discussion questions and 2 hands-on exercises.
            - Output strictly in **Markdown** (use code fences for code).
            """
        ).strip()

        code_clause = (
            "Provide working Python or JavaScript code samples when demonstrating transactions"
            if include_code
            else "Do NOT include any code samples"
        )

        return base.format(lesson_topic=lesson_topic, code_clause=code_clause)

    # ------------------------------------------------------------------ #
    # Assessment prompts                                                 #
    # ------------------------------------------------------------------ #
    def build_assessment(
        self,
        *,
        topic: str,
        mcq: int = 3,
        coding: int = 1,
        short_answer: int = 2,
    ) -> str:
        """
        Prompt to generate a balanced assessment for the specified topic.
        """

        return textwrap.dedent(
            f"""
            Create an assessment for the Bitcoin SV topic **{topic}** containing:
            - {mcq} multiple-choice questions (clearly mark the correct answer).
            - {short_answer} short-answer / definition questions.
            - {coding} practical coding exercise (include starter code).

            Format the output in *Markdown* with clear sub-headings.
            """
        ).strip()
