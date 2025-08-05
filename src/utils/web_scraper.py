"""
Tiny, self-contained utility to fetch **publicly-available** web pages
and return a *clean* block of text that can be fed into the LLM or saved
into `data/bsv_sources/`.

Design goals
------------
* **Zero headless browser**: pure `requests + BeautifulSoup`.
* **Respect robots.txt** via `urllib.robotparser`.
* **Auto-throttle** repeated requests to the same host (simple in-memory).
* **Very small** surface so it remains portable and test-friendly.

Author : AI-Course-Generator
Created: 2025-08-04
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)
USER_AGENT = "AI-Course-Generator/1.0 (+https://github.com/your-org/ai-course-generator)"

# Simple per-host throttle (seconds between requests)
_THROTTLE_SECONDS = 2.0
_last_request_time: Dict[str, float] = {}

# Tiny robots.txt cache
_robots_cache: Dict[str, RobotFileParser] = {}


# ---------------------------------------------------------------------- #
# Public API                                                             #
# ---------------------------------------------------------------------- #
def fetch_clean_text(url: str, *, timeout: int = 15) -> str:
    """
    Download URL **if allowed** and return visible text with scripts,
    style, nav etc. stripped out.

    Raises
    ------
    RuntimeError
        On network error, robots disallow, or non-HTML response.
    """
    _check_robots(url)
    _throttle(url)

    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout)
    if not resp.ok:
        raise RuntimeError(f"Failed to fetch {url}: HTTP {resp.status_code}")

    ctype = resp.headers.get("Content-Type", "")
    if "html" not in ctype:
        raise RuntimeError(f"Unsupported content-type for scraping: {ctype}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script/style/nav/aside tags
    for tag in soup(["script", "style", "nav", "aside", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Collapse multiple blank lines
    lines = [ln.strip() for ln in text.splitlines()]
    cleaned = "\n".join([ln for ln in lines if ln])

    LOGGER.info("Scraped %s (%.1f KB)", url, len(resp.content) / 1024)
    return cleaned


def save_to_file(text: str, dest: Path | str) -> Path:
    """
    Persist scraped text so the LLM can ingest it later offline.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return dest


# ---------------------------------------------------------------------- #
# Internal helpers                                                       #
# ---------------------------------------------------------------------- #
def _check_robots(url: str) -> None:
    """
    Quick robots.txt check; raises if disallowed.
    """
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    robot = _robots_cache.get(base)
    if robot is None:
        robot = RobotFileParser()
        robot.set_url(f"{base}/robots.txt")
        try:
            robot.read()
        except Exception:
            # If robots.txt is unreachable fall back to allow (common)
            pass
        _robots_cache[base] = robot

    if robot.disallow_all or not robot.can_fetch(USER_AGENT, url):
        raise RuntimeError(f"Robots.txt disallows scraping {url}")


def _throttle(url: str) -> None:
    """
    Delay if the same host was hit less than `_THROTTLE_SECONDS` ago.
    """
    host = urlparse(url).netloc
    now = time.time()
    last = _last_request_time.get(host, 0)
    delta = now - last
    if delta < _THROTTLE_SECONDS:
        time.sleep(_THROTTLE_SECONDS - delta)
    _last_request_time[host] = time.time()
