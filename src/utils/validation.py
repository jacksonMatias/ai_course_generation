"""
Light-weight content-quality checks that can run **offline** (i.e.,
without calling the LLM again) after a course has been generated.

The goal is *not* to prove 100 % correctness of every Bitcoin SV fact
—that would require blockchain verification, consensus rules, etc.—but
rather to catch common formatting or structural issues early in the
CI/CD pipeline.

Features
--------
1. Heading hierarchy validation (no skipped levels, H1 appears once).
2. Presence of required sections (Overview, Objectives, Assessment …).
3. Quick Bitcoin-SV terminology sanity check (flag obvious typos).

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

# ---------------------------------------------------------------------- #
# Public API                                                             #
# ---------------------------------------------------------------------- #
def validate_markdown(markdown: str) -> List[str]:
    """
    Run all validations on the given Markdown text.

    Returns
    -------
    A list of *human-readable* error strings.
    Empty list ⇒ the file passed all checks.
    """
    errors: List[str] = []
    errors += _check_heading_levels(markdown)
    errors += _check_required_sections(markdown)
    errors += _check_bsv_terminology(markdown)
    return errors


def validate_file(path: Path | str) -> List[str]:
    """
    Convenience wrapper to validate a markdown file on disk.
    """
    path = Path(path)
    if not path.exists():
        return [f"File not found: {path}"]
    return validate_markdown(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------- #
# Individual validation rules                                            #
# ---------------------------------------------------------------------- #
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", flags=re.MULTILINE)


def _check_heading_levels(md: str) -> List[str]:
    """
    Ensure heading levels don’t jump (e.g., H2 → H4) and H1 appears once.
    """
    errors: List[str] = []
    last_level = 0
    h1_count = 0

    for match in _HEADING_RE.finditer(md):
        level = len(match.group(1))
        if level == 1:
            h1_count += 1
            if h1_count > 1:
                errors.append("Multiple H1 headings found.")
        if last_level and level > last_level + 1:
            errors.append(
                f"Heading level jumped from H{last_level} to H{level} at: '{match.group(2)}'"
            )
        last_level = level

    if h1_count == 0:
        errors.append("Document is missing a top-level H1 heading.")

    return errors


_REQUIRED_SECTIONS = {
    "## Course Overview",
    "## Module 1",
    "## Capstone Project",
    "## Assessment",
}


def _check_required_sections(md: str) -> List[str]:
    """
    Verify the presence of critical course sections.
    """
    errors: List[str] = []
    for section in _REQUIRED_SECTIONS:
        if section not in md:
            errors.append(f"Missing required section: '{section}'")
    return errors


# Very small list – extend as needed
_BSV_KEY_TERMS = {
    "bitcoin sv",
    "bsv",
    "satoshis",
    "utxo",
    "script",
    "op_return",
    "merchant api",
    "handcash",
    "nchain",
}


def _check_bsv_terminology(md: str) -> List[str]:
    """
    Flag headings that *should* mention Bitcoin SV but don’t.
    """
    errors: List[str] = []
    headings = [m.group(2).lower() for m in _HEADING_RE.finditer(md)]
    for h in headings:
        if "bitcoin" in h and "sv" not in h:
            errors.append(f"Heading may reference Bitcoin without 'SV': '{h}'")
    # Quick spell-check for key terms
    for term in _BSV_KEY_TERMS:
        if term not in md.lower():
            errors.append(f"Key BSV term not found anywhere: '{term}'")
            # Only flag each term once
    return errors
