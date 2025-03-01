from __future__ import annotations

from io import TextIOWrapper
from pathlib import Path
import re
from typing import Any

from appdirs import user_cache_dir
import hishel
import httpx


_CACHE_TIMEOUT = 30 * 24 * 60 * 60
_CACHE_DIR = Path(user_cache_dir("textual_icons", "Textualize"))


async def fetch_url(url: str) -> bytes:
    """Fetch data from URL using httpx with hishel caching."""
    storage = hishel.AsyncFileStorage(
        base_path=_CACHE_DIR,
        ttl=_CACHE_TIMEOUT,
    )
    controller = hishel.Controller(
        cacheable_methods=["GET"],
        cacheable_status_codes=[200],
        allow_stale=True,
    )
    transport = hishel.AsyncCacheTransport(
        transport=httpx.AsyncHTTPTransport(),
        storage=storage,
        controller=controller,
    )
    async with httpx.AsyncClient(transport=transport) as client:  # type: ignore[arg-type]
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.content


def extract_unicode_from_css(css_data: bytes, pattern: str) -> dict[str, str]:
    """Extract unicode points from CSS content."""
    content = css_data.decode("utf-8")
    matches = re.findall(pattern, content, re.MULTILINE)

    charmap = {}
    for name, key in matches:
        # Convert CSS unicode escapes to hex
        key = key.replace("\\F", "0xf").lower()
        key = key.replace("\\", "0x")
        name = name.rstrip(":").lower()
        charmap[name] = key

    return charmap


try:
    import orjson as _orjson

    def load_json(data: str | bytes | TextIOWrapper) -> Any:
        """Load JSON data using orjson if available."""
        if isinstance(data, TextIOWrapper):
            data = data.read()
        if isinstance(data, str):
            data = data.encode()
        return _orjson.loads(data)

except ImportError:
    import json as _stdlib_json

    def load_json(data: str | bytes | TextIOWrapper) -> Any:
        """Load JSON data using stdlib json."""
        if isinstance(data, TextIOWrapper):
            data = data.read()
        if isinstance(data, bytes):
            data = data.decode()
        return _stdlib_json.loads(data)
