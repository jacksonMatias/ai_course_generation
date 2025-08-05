#!/usr/bin/env python3
"""
Convierte **un Markdown ya existente** a DOCX (y PDF si Pandoc está disponible).

Uso básico
----------
$ python scripts/convert_md.py my_notes.md \
    --docx-template src/templates/word_templates/course_template.docx \
    --output-dir dist/
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Dependencias internas del proyecto
from src.core.markdown_processor import MarkdownProcessor
from src.converters.document_formatter import DocumentFormatter

_LOG_FORMAT = "[%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)
LOGGER = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="convert-md",
        description="Convierte un Markdown premontado a DOCX/PDF usando la plantilla corporativa.",
    )
    p.add_argument(
        "markdown",
        type=Path,
        help="Archivo .md a convertir.",
    )
    p.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("dist"),
        help="Directorio destino (default: ./dist).",
    )
    p.add_argument(
        "--docx-template",
        type=Path,
        help="Plantilla .docx con estilos y branding.",
        required=True,
    )
    p.add_argument(
        "--no-toc",
        action="store_true",
        help="No generar tabla de contenidos automática.",
    )
    p.add_argument(
        "--no-pdf",
        action="store_true",
        help="Saltar exportación a PDF (aunque haya Pandoc).",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="Verbose logging.",
    )
    return p


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #
def main(argv: Optional[list[str]] = None) -> None:
    args = build_parser().parse_args(argv)

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    # -------- Leer Markdown ------------------------------------------------- #
    if not args.markdown.exists():
        LOGGER.error("Markdown no encontrado: %s", args.markdown)
        sys.exit(1)

    raw_md = args.markdown.read_text(encoding="utf-8")
    LOGGER.info("Leído Markdown (%s caracteres)", len(raw_md))

    # -------- Post-proceso (limpieza + TOC) --------------------------------- #
    processor = MarkdownProcessor()
    clean_md = processor.process(raw_md, toc=not args.no_toc)

    # -------- Persistir Markdown limpio ------------------------------------ #
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    file_stem = args.markdown.stem
    md_path = output_dir / f"{file_stem}.md"
    processor.save(clean_md, md_path)
    LOGGER.info("Markdown limpio → %s", md_path)

    # -------- DOCX / PDF ---------------------------------------------------- #
    formatter = DocumentFormatter()
    docx_path, pdf_path = formatter.render_all(
        markdown_text=clean_md,
        file_stem=file_stem,
        output_dir=output_dir,
        word_template=args.docx_template,
    )
    LOGGER.info("DOCX → %s", docx_path)

    if pdf_path:
        LOGGER.info("PDF  → %s", pdf_path)
    elif not args.no_pdf:
        LOGGER.info("PDF omitido (Pandoc ausente o --no-pdf).")

    LOGGER.info("✓ Conversión finalizada.")


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
