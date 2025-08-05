"""
Centralised runtime configuration.

The module supports two complementary mechanisms:

1. **Environment variables** – quick overrides, great for CI / secrets.
2. **`.env` file** (optional) – convenient for local development.

Any setting can be accessed via the `settings` singleton:

from src.config.settings import settings

print(settings.OPENAI_API_KEY)
print(settings.COURSE_OUTPUT_DIR)

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, validator

# ---------------------------------------------------------------------- #
# Load `.env` if present                                                #
# ---------------------------------------------------------------------- #
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DOTENV_PATH = _PROJECT_ROOT / ".env"
if _DOTENV_PATH.exists():
    load_dotenv(dotenv_path=_DOTENV_PATH)


# ---------------------------------------------------------------------- #
# Settings model                                                        #
# ---------------------------------------------------------------------- #
class _Settings(BaseSettings):
    # ------------------------------------------------------------------ #
    # AI provider keys                                                   #
    # ------------------------------------------------------------------ #
    OPENAI_API_KEY: str = Field("", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field("", env="ANTHROPIC_API_KEY")
    COHERE_API_KEY: str = Field("", env="COHERE_API_KEY")

    # ------------------------------------------------------------------ #
    # Default provider & model                                           #
    # ------------------------------------------------------------------ #
    DEFAULT_PROVIDER: str = Field("openai", env="DEFAULT_PROVIDER")

    # ------------------------------------------------------------------ #
    # Paths                                                              #
    # ------------------------------------------------------------------ #
    COURSE_OUTPUT_DIR: Path = Field(
        _PROJECT_ROOT / "generated_courses", env="COURSE_OUTPUT_DIR"
    )

    # ------------------------------------------------------------------ #
    # Validation                                                         #
    # ------------------------------------------------------------------ #
    @validator("DEFAULT_PROVIDER")
    def _validate_provider(cls, v: str) -> str:  # noqa: D401,N805
        allowed = {"openai", "anthropic", "cohere"}
        if v.lower() not in allowed:
            raise ValueError(f"DEFAULT_PROVIDER must be one of {', '.join(allowed)}")
        return v.lower()

    class Config:
        # Allow reading from environment variables by default
        env_file = ".env"
        case_sensitive = False


# Singleton instance – importable as `settings`
settings = _Settings()  # type: ignore[var-annotated]

# Create output directory on first import
settings.COURSE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Quick sanity log (optional)
if os.getenv("DEBUG_SETTINGS") == "1":  # pragma: no cover
    for k, v in settings.dict().items():
        print(f"[settings] {k} = {v}")

