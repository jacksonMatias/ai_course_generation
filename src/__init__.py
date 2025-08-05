"""
Public package root for **ai-course-generator**.

Exports the most frequently-used façade classes so that user-code can
write terse imports such as:

from ai_course_generator import StandardizedAI, CourseGeneral


The canonical distribution name on PyPI is *ai-course-generator* while
the import-path is **ai_course_generator** (PEP-8 compliant).

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:
    __version__: str = _pkg_version("ai-course-generator")
except PackageNotFoundError:  # local dev / editable install
    __version__ = "0.0.0.dev0"

# ---------------------------------------------------------------------- #
# Re-export high-level API                                              #
# ---------------------------------------------------------------------- #
from .api.standardized_api import StandardizedAI  # noqa: E402,F401
from .core.course_generator import CourseGenerator  # noqa: E402,F401
from .converters.document_formatter import DocumentFormatter  # noqa: E402,F401

__all__ = [
    "StandardizedAI",
    "CourseGenerator",
    "DocumentFormatter",
    "__version__",
]
