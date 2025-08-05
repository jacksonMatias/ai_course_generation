"""
High-level façade that *wraps* the low-level `MarkdownToWordConverter`
and, when Pandoc is available, also provides **PDF** export.

Typical usage
-------------
from pathlib import Path
from src.converters.document_formatter import DocumentFormatter

formatter = DocumentFormatter()
docx_path, pdf_path = formatter.render_all(
markdown_text=my_md,
file_stem="bitcoin_sv_fundamentals",
output_dir=Path("dist/"),
word_template=Path("src/templates/word_templates/course_template.docx"),
)

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from .markdown_to_word import MarkdownToWordConverter

LOGGER = logging.getLogger(__name__)


class DocumentFormatter:
    """
    Produce nicely-formatted course handouts in DOCX (always) and
    PDF (when the system has Pandoc + a LaTeX engine).
    """

    def __init__(self) -> None:
        self._md2docx = MarkdownToWordConverter()
        self._pandoc_available: bool | None = None  # lazy-checked

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def render_all(
        self,
        markdown_text: str,
        *,
        file_stem: str,
        output_dir: Path,
        word_template: Optional[Path] = None,
    ) -> Tuple[Path, Optional[Path]]:
        """
        Convert Markdown to DOCX (always) and PDF (if possible).

        Returns
        -------
        (docx_path, pdf_path_or_None)
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        docx_path = output_dir / f"{file_stem}.docx"
        pdf_path: Optional[Path] = output_dir / f"{file_stem}.pdf"

        # 1 — DOCX
        self._md2docx.convert(
            markdown_text,
            output_path=docx_path,
            template_path=word_template,
        )

        # 2 — PDF (optional)
        if self._has_pandoc():
            try:
                self._markdown_to_pdf(markdown_text, pdf_path)
            except Exception as exc:  # pragma: no cover
                LOGGER.warning("PDF export failed: %s", exc)
                pdf_path = None
        else:
            pdf_path = None

        return docx_path, pdf_path

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _markdown_to_pdf(markdown_text: str, pdf_path: Path) -> None:
        """
        Use Pandoc (must be on $PATH) to turn Markdown into a PDF.
        Assumes a LaTeX engine such as `xelatex` is available.
        """
        cmd = ["pandoc", "-", "-o", str(pdf_path), "--pdf-engine=xelatex"]
        subprocess.run(cmd, input=markdown_text.encode("utf-8"), check=True)

    # ------------------------------------------------------------------ #
    # Availability checks                                                #
    # ------------------------------------------------------------------ #
    def _has_pandoc(self) -> bool:
        """
        Cheap memoised check for Pandoc availability.
        """
        if self._pandoc_available is None:
            self._pandoc_available = shutil.which("pandoc") is not None
            if not self._pandoc_available:
                LOGGER.info("Pandoc not found – PDF export disabled.")
        return self._pandoc_available

