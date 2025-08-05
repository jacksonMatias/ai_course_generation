"""
Small, dependency-light helpers for common filesystem operations that
crop up across the code-base:

* Reading / writing **YAML**, **JSON**, and plain-text.
* Handy `atomic_write()` to avoid partially-written files.
* Convenience wrappers to download remote files into `data/input/`.

These helpers deliberately keep a *tiny* surface area so they can be
imported anywhere without causing circular-import headaches.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

import requests
import yaml

# Project root is two levels up from this file
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DATA_INPUT_DIR = _PROJECT_ROOT / "src" / "data" / "input"
_DATA_INPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------- #
# YAML / JSON helpers                                                   #
# --------------------------------------------------------------------- #
def read_yaml(path: Path | str) -> Mapping[str, Any]:
    """Return the YAML file as dict (empty dict if file missing)."""
    path = Path(path)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


def write_yaml(data: Mapping[str, Any], path: Path | str) -> None:
    """Write mapping to YAML (UTF-8, indent=2)."""
    path = Path(path)
    _atomic_write(path, yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def read_json(path: Path | str) -> Any:
    path = Path(path)
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fp:
        return json.load(fp)


def write_json(obj: Any, path: Path | str, *, indent: int = 2) -> None:
    path = Path(path)
    _atomic_write(path, json.dumps(obj, indent=indent, ensure_ascii=False))


def read_text(path: Path | str) -> str:
    path = Path(path)
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(text: str, path: Path | str) -> None:
    path = Path(path)
    _atomic_write(path, text)


# --------------------------------------------------------------------- #
# Download helper                                                      #
# --------------------------------------------------------------------- #
def download(url: str, *, filename: Optional[str] = None) -> Path:
    """
    Fetch a remote file (GET) and save it into `data/input/`.
    Returns the local path.  Uses streaming download for large files.
    """
    filename = filename or url.split("/")[-1] or "download.bin"
    dest_path = _DATA_INPUT_DIR / filename

    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    with dest_path.open("wb") as fh:
        shutil.copyfileobj(response.raw, fh)

    return dest_path


# --------------------------------------------------------------------- #
# Atomic-write utility                                                 #
# --------------------------------------------------------------------- #
def _atomic_write(path: Path, data: str | bytes) -> None:
    """
    Write *text* or *bytes* to `path` atomically:
    1. Write into a temp-file in the same dir.
    2. `rename()` (atomic on POSIX) to the final name.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    mode: str
    if isinstance(data, str):
        mode = "w"
        encode = lambda x: x  # noqa: E731
    else:
        mode = "wb"
        encode = lambda x: x  # type: ignore  # noqa: E731

    with tempfile.NamedTemporaryFile(delete=False, dir=path.parent) as tmp:
        with open(tmp.name, mode, encoding="utf-8" if mode == "w" else None) as fh:
            fh.write(encode(data))  # type: ignore[arg-type]
    Path(tmp.name).replace(path)
