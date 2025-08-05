#!/usr/bin/env python3
"""
Command-line entry-point for the **AI-Course-Generator** suite.

Given a course configuration YAML, this tool will:

1. Generate the course content via the chosen LLM provider.
2. Post-process the Markdown (cleaning + table-of-contents).
3. Validate the output for basic structural issues.
4. Persist Markdown, DOCX (and PDF if Pandoc present) into an output dir.

Example
-------
$ python main.py my_course.yaml \
    --provider openai \
    --api-key $OPENAI_API_KEY \
    --docx-template src/templates/word_templates/course_template.docx
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import yaml

# Local imports
from src.api.standardized_api import StandardizedAI
from src.config.settings import settings
from src.core.course_generator import CourseGenerator
from src.core.markdown_processor import MarkdownProcessor
from src.converters.document_formatter import DocumentFormatter
from src.utils.validation import validate_markdown

_LOG_FORMAT = "[%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)
LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------- #
# CLI                                                                     #
# ---------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ai-course-generator",
        description="Generate Bitcoin-SV courses with a single command.",
    )
    p.add_argument(
        "config",
        type=Path,
        help="YAML file describing the course (see examples in /config)",
    )
    p.add_argument(
        "-p",
        "--provider",
        default=settings.DEFAULT_PROVIDER,
        choices=["openai", "anthropic", "cohere", "ollama"],
        help=f"Which AI provider to use (default: {settings.DEFAULT_PROVIDER})",
    )
    p.add_argument(
        "--api-key",
        help="API key for the provider (falls back to environment or .env file).",
    )
    p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=settings.COURSE_OUTPUT_DIR,
        help="Directory to store generated files.",
    )
    p.add_argument(
        "--docx-template",
        type=Path,
        help="Optional .docx template providing styles & branding.",
    )
    p.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF export even if Pandoc is available.",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose logging.",
    )
    return p


def main(argv: Optional[list[str]] = None) -> None:  # noqa: D401
    args = build_parser().parse_args(argv)

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    # ------------------------------------------------------------------ #
    # Load course YAML                                                   #
    # ------------------------------------------------------------------ #
    if not args.config.exists():
        LOGGER.error("Config file not found: %s", args.config)
        sys.exit(1)

    course_cfg = _load_yaml(args.config)
    LOGGER.info("Loaded course config: %s", course_cfg.get("course_name", "<unnamed>"))

    # ------------------------------------------------------------------ #
    # Instantiate AI provider façade                                     #
    # ------------------------------------------------------------------ #
    api_key = args.api_key or _lookup_api_key(args.provider)
    if not api_key and args.provider != "ollama":
        LOGGER.error("API key not provided and not found in environment/.env")
        sys.exit(1)

    ai = StandardizedAI(args.provider, api_key=api_key)

    # ------------------------------------------------------------------ #
    # Generate course                                                    #
    # ------------------------------------------------------------------ #
    generator = CourseGenerator(ai)
    markdown_raw = generator.generate_full_course(course_cfg)
    LOGGER.info("Course generation completed (raw length: %s chars)", len(markdown_raw))

    # ------------------------------------------------------------------ #
    # Post-processing                                                    #
    # ------------------------------------------------------------------ #
    processor = MarkdownProcessor()
    markdown_clean = processor.process(markdown_raw, toc=True)

    # Validation warnings
    warnings = validate_markdown(markdown_clean)
    if warnings:
        LOGGER.warning("Validation produced %s warning(s):", len(warnings))
        for w in warnings:
            LOGGER.warning("  • %s", w)

    # ------------------------------------------------------------------ #
    # Persist files                                                      #
    # ------------------------------------------------------------------ #
    output_dir: Path = args.output_dir
    file_stem = _slugify(course_cfg.get("course_name") or course_cfg["topic"])
    md_path = output_dir / f"{file_stem}.md"
    processor.save(markdown_clean, md_path)
    LOGGER.info("Markdown saved → %s", md_path)

    formatter = DocumentFormatter()
    docx_path, pdf_path = formatter.render_all(
        markdown_clean,
        file_stem=file_stem,
        output_dir=output_dir,
        word_template=args.docx_template,
    )
    LOGGER.info("DOCX saved → %s", docx_path)
    if pdf_path:
        LOGGER.info("PDF saved  → %s", pdf_path)
    elif not args.no_pdf:
        LOGGER.info("PDF export skipped (Pandoc missing or disabled).")

    LOGGER.info("✓ All done — happy teaching! 📚")


# ---------------------------------------------------------------------- #
# Utilities                                                              #
# ---------------------------------------------------------------------- #
def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def _lookup_api_key(provider: str) -> str | None:
    provider = provider.lower()
    if provider == "openai":
        return settings.OPENAI_API_KEY
    if provider == "anthropic":
        return settings.ANTHROPIC_API_KEY
    if provider == "cohere":
        return settings.COHERE_API_KEY
    if provider == "ollama":
        return None
    return None


def _slugify(text: str) -> str:
    import re

    slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    return slug


# ---------------------------------------------------------------------- #
# Entry-point                                                            #
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
