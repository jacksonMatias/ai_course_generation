"""
High-level orchestration that turns a **course configuration** dictionary
(intended to come from YAML) into a *complete* Markdown document ready
for conversion to Word/PDF.

Process
-------
1. Build a course-outline prompt and ask the LLM to return a structured
   outline.
2. Parse the outline to extract *module / lesson* headings.
3. For every lesson, request detailed content from the LLM.
4. Optionally append assessments and a capstone project brief.

The class keeps *all* LLM interactions behind a single façade so the
rest of the program can simply call `CourseGenerator.generate_full_course`.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Sequence

import yaml

from ..api.standardized_api import StandardizedAI, GenerationConfig
from .prompt_generator import PromptGenerator
from .rule_engine import RuleEngine


# ---------------------------------------------------------------------- #
# Helper functions                                                       #
# ---------------------------------------------------------------------- #
_HEADING_RE = re.compile(r"^(#{2,6})\s+(.*)$")  # capture Markdown headings


def _is_lesson_heading(line: str) -> bool:
    """Lesson headings are usually `### Lesson` or deeper."""
    match = _HEADING_RE.match(line.strip())
    return bool(match and len(match.group(1)) >= 3)


def _is_module_heading(line: str) -> bool:
    """Module headings are usually `## Module`."""
    match = _HEADING_RE.match(line.strip())
    return bool(match and len(match.group(1)) == 2)


# ---------------------------------------------------------------------- #
# CourseGenerator                                                        #
# ---------------------------------------------------------------------- #
class CourseGenerator:
    """
    Orchestrates the multi-step generation of a full course.
    """

    def __init__(
        self,
        ai_api: StandardizedAI,
        *,
        prompt_gen: PromptGenerator | None = None,
        rule_engine: RuleEngine | None = None,
    ) -> None:
        self.ai = ai_api
        self.prompts = prompt_gen or PromptGenerator()
        self.rules = rule_engine or RuleEngine()

    # ------------------------------------------------------------------ #
    # Public entry point                                                 #
    # ------------------------------------------------------------------ #
    def generate_full_course(
        self,
        course_cfg: Dict,
        *,
        gen_cfg: GenerationConfig | None = None,
        with_assessments: bool = True,
    ) -> str:
        """
        Given a configuration dictionary (parsed from YAML) generate the
        entire course as a single Markdown string.
        """

        # 1 — Outline
        outline_prompt = self.prompts.build_course_outline(
            topic=course_cfg["topic"],
            duration=course_cfg.get("duration", "self-paced"),
            level=course_cfg.get("difficulty_level", "intermediate"),
        )
        outline_rules = self.rules.apply_rules("course", course_cfg.get("rules"))
        outline_md = self.ai.generate_course_content(
            outline_prompt, outline_rules, config=gen_cfg
        )

        # 2 — Parse outline to find lesson topics
        lesson_topics = self._parse_outline_for_lessons(outline_md)

        # 3 — Generate each lesson
        lessons_md: List[str] = []
        for topic in lesson_topics:
            lesson_prompt = self.prompts.build_lesson_content(
                lesson_topic=topic,
                include_code=bool(course_cfg.get("include_code_examples", True)),
            )
            lesson_rules = self.rules.apply_rules("lesson", course_cfg.get("rules"))
            lesson_md = self.ai.generate_course_content(
                lesson_prompt, lesson_rules, config=gen_cfg
            )
            lessons_md.append(lesson_md)

        # 4 — Assessments (optional)
        assessments_md: str = ""
        if with_assessments:
            assess_prompt = self.prompts.build_assessment(topic=course_cfg["topic"])
            assess_rules = self.rules.apply_rules("assessment", course_cfg.get("rules"))
            assessments_md = self.ai.generate_course_content(
                assess_prompt, assess_rules, config=gen_cfg
            )

        # 5 — Combine everything
        header = self._render_markdown_header(course_cfg)
        course_markdown = "\n\n".join(
            [header, outline_md, *lessons_md, assessments_md]
        ).strip()

        return course_markdown

    # ------------------------------------------------------------------ #
    # Internals                                                          #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _render_markdown_header(cfg: Dict) -> str:
        """
        Produce a brief front-matter-like section with metadata.
        """
        parts = [
            f"# {cfg.get('course_name', cfg['topic'])}",
            "",
            f"**Duration:** {cfg.get('duration', 'self-paced')}",
            f"**Difficulty:** {cfg.get('difficulty_level', 'intermediate').capitalize()}",
            f"**Target Audience:** {cfg.get('target_audience', 'Developers / Enthusiasts')}",
        ]
        return "\n".join(parts)

    @staticmethod
    def _parse_outline_for_lessons(outline_md: str) -> Sequence[str]:
        """
        Read the outline Markdown and return a list of lesson topics
        pulled from `###` headings.
        """
        lessons: List[str] = []
        for line in outline_md.splitlines():
            if _is_lesson_heading(line):
                # Remove leading hashes and whitespace
                topic = _HEADING_RE.sub(r"\2", line).strip()
                lessons.append(topic)
        # Fallback: if no lesson headings were found treat module headings
        if not lessons:
            for line in outline_md.splitlines():
                if _is_module_heading(line):
                    topic = _HEADING_RE.sub(r"\2", line).strip()
                    lessons.append(topic)
        return lessons


# ---------------------------------------------------------------------- #
# Convenience CLI (optional)                                             #
# ---------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    import argparse
    import sys

    def _load_cfg(path: Path) -> Dict:
        with path.open(encoding="utf-8") as fp:
            return yaml.safe_load(fp)

    parser = argparse.ArgumentParser(description="Generate a Bitcoin-SV course")
    parser.add_argument("config", type=Path, help="Path to course YAML config")
    parser.add_argument("--provider", default="openai", help="AI provider name")
    parser.add_argument("--api-key", required=True, help="API key for the provider")
    args = parser.parse_args()

    ai = StandardizedAI(args.provider, api_key=args.api_key)
    gen = CourseGenerator(ai)
    markdown = gen.generate_full_course(_load_cfg(args.config))
    sys.stdout.write(markdown)
