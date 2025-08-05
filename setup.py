from __future__ import annotations

import pathlib

from setuptools import find_packages, setup

# ------------------------------------------------------------------ #
# Metadata                                                           #
# ------------------------------------------------------------------ #
NAME = "ai-course-generator"
DESCRIPTION = "Generate Bitcoin-SV courses (Markdown → DOCX/PDF) via a standardised AI API façade."
URL = "https://github.com/your-org/ai-course-generator"
EMAIL = "dev@your-org.com"
AUTHOR = "AI-Course-Generator Team"
LICENSE = "Apache-2.0"
PYTHON_REQUIRES = ">=3.9"

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
README = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

# Re-use the pinned runtime deps
REQUIREMENTS = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
REQUIREMENTS = [line.strip() for line in REQUIREMENTS if line.strip() and not line.startswith("#")]

# ------------------------------------------------------------------ #
# Setup                                                              #
# ------------------------------------------------------------------ #
setup(
    name=NAME,
    version="0.1.0",
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires=PYTHON_REQUIRES,
    packages=find_packages(where=".", exclude=("tests*", "generated_courses*", "examples*")),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "ai-course-generator=main:main",
        ]
    },
    license=LICENSE,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Education",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Environment :: Console",
    ],
)
