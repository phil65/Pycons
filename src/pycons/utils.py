from __future__ import annotations

import os
from pathlib import Path
import re

import anyenv
from appdirs import user_cache_dir


_CACHE_TIMEOUT = 30 * 24 * 60 * 60
_CACHE_DIR = Path(user_cache_dir("Pycons", False))
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


async def fetch_url(url: str, use_cache: bool = True) -> bytes:
    """Fetch data from URL using httpx with optional hishel caching (on by default)."""
    headers = {}
    if TOKEN and ("github.com" in url or "githubusercontent.com" in url):
        headers["Authorization"] = f"token {TOKEN}"
    return await anyenv.get_bytes(url, headers=headers, cache=use_cache, cache_ttl="1w")


def extract_unicode_from_css(css_data: bytes, pattern: str) -> dict[str, str]:
    """Extract unicode points from CSS content."""
    content = css_data.decode("utf-8")
    matches = re.findall(pattern, content, re.MULTILINE)

    charmap: dict[str, str] = {}
    for name, key in matches:
        # Convert CSS unicode escapes to hex
        key = key.replace("\\F", "0xf").lower()
        key = key.replace("\\", "0x")
        name = name.rstrip(":").lower()
        charmap[name] = key

    return charmap
