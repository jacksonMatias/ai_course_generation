# src/templates/style_map.py
# -*- coding: utf-8 -*-
"""
Mapa Markdown → estilos Word ajustado a *course_template.docx*.
Incluye NBSP (U+00A0) tras la barra vertical en varios estilos.
"""

NBSP = "\u00A0"          # atajo para que se vea claro

STYLE_MAP: dict[str, str] = {
    # Títulos
    "h1": f"BSVA | Numbered list heading level 1",
    "h2": f"BSVA |{NBSP}Numbered list heading level 2",
    "h3": f"BSVA |{NBSP}Numbered list heading level 3",
    "h4": f"BSVA |{NBSP}Numbered list heading level 4",

    # Texto normal
    "p":  "Normal",           
    "intro": "BSVA | Introduction",

    # Listas
    "ul": "BSVA | ABC List",
    "ol": f"BSVA |{NBSP}Numbered list heading level 2",
    "ul_boxed": "BSVA | Boxed List Bullet 1",

    # Citas y bloques especiales
    "blockquote": "BSVA | Quote",
    "boxed_quote": "BSVA | Boxed Text Quote",
    "boxed_quote_name": "BSVA | Boxed Text Quote – Name",

    # Código
    "code": "HTML Preformatted",

    # Tabla de contenidos
    "toc_heading": "TOC Heading",
    "toc_lvl1": "toc 1",
    "toc_lvl2": "toc 2",
    "toc_lvl3": "toc 3",

    # Header / footer (solo si tu conversor los usa)
    "header": "BSVA | HEADER",
    "footer": "BSVA | FOOTER",

    # Portada
    "cover_title": "BSVA | Cover Title",
}
