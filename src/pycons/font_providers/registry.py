from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from anyenv import load_json

from pycons.font_providers.models import FontInfo, Icon
from pycons.font_providers.providers import PROVIDERS
from pycons.utils import _CACHE_DIR, fetch_url


if TYPE_CHECKING:
    from pathlib import Path

    from pycons.font_providers.base import FontProvider


class FontRegistry:
    """Manages font downloads and access."""

    def __init__(self) -> None:
        self.fonts_dir = _CACHE_DIR / "fonts"
        self.mappings_dir = _CACHE_DIR / "mappings"
        self.versions_file = _CACHE_DIR / "versions.json"
        # Create cache directories
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        self.mappings_dir.mkdir(parents=True, exist_ok=True)
        self._mapping_cache: dict[str, dict[str, str]] = {}

    async def get_fonts(self, names: list[str]) -> list[FontInfo]:
        """Get multiple fonts in parallel.

        Returns a list of FontInfo objects, with None for any fonts that failed to load.
        """
        results = await asyncio.gather(
            *(self.get_font(name) for name in names), return_exceptions=True
        )

        return [result for result in results if isinstance(result, FontInfo)]

    async def get_font(self, name: str) -> FontInfo:
        """Get font info, downloading if necessary."""
        provider = PROVIDERS[name]
        # Get latest version
        version = await provider.get_latest_version()
        # Get or download font files
        ttf_path = self.fonts_dir / f"{name}.ttf"
        mapping_path = self.mappings_dir / f"{name}.json"
        if not ttf_path.exists() or not mapping_path.exists():
            await self._download_font(name, version)
        return FontInfo(
            name=name,
            prefix=provider.PREFIX,
            display_name=provider.DISPLAY_NAME,
            current_version=version,
            ttf_path=ttf_path,
            mapping_path=mapping_path,
        )

    async def _download_font(self, name: str, version: str) -> None:
        """Download and save font files."""
        provider = PROVIDERS[name]
        ttf_url, mapping_url = provider.get_download_urls(version)
        # Download files in parallel
        ttf_data, mapping_data = await asyncio.gather(
            fetch_url(ttf_url), fetch_url(mapping_url)
        )
        # Process mapping while writing TTF
        await asyncio.gather(
            asyncio.to_thread(self._write_ttf, name, ttf_data),
            self._process_and_write_mapping(name, provider, mapping_data),
        )

    def _write_ttf(self, name: str, data: bytes) -> None:
        """Write TTF file to disk."""
        ttf_path = self.fonts_dir / f"{name}.ttf"
        ttf_path.write_bytes(data)

    async def _process_and_write_mapping(
        self, name: str, provider: FontProvider, data: bytes
    ) -> None:
        """Process and write mapping file."""
        mapping = provider.process_mapping(data)
        mapping_path = self.mappings_dir / f"{name}.json"
        await asyncio.to_thread(self._write_json, mapping_path, mapping)

    def _write_json(self, path: Path, data: dict) -> None:
        """Write JSON file to disk."""
        path.write_text(json.dumps(data, indent=2))

    async def get_icon(self, icon_spec: str) -> Icon:
        """Get an icon by its specification (e.g. 'fa.home')."""
        try:
            prefix, name = icon_spec.split(".")
        except ValueError as err:
            msg = f"Invalid icon spec {icon_spec!r}. Expected format: 'prefix.name'"
            raise ValueError(msg) from err

        # Find provider by prefix
        provider = next((p for p in PROVIDERS.values() if prefix == p.PREFIX), None)
        if not provider:
            msg = f"No provider found for prefix {prefix!r}"
            raise ValueError(msg)

        # Get font info which ensures font is downloaded
        font_info = await self.get_font(provider.NAME)
        text = font_info.mapping_path.read_text("utf-8")
        mapping = load_json(text, return_type=dict)

        if name not in mapping:
            msg = f"Icon '{name}' not found in {provider.DISPLAY_NAME}"
            raise ValueError(msg)
        return Icon(
            character=chr(int(mapping[name], 16)),
            provider=provider.NAME,
            prefix=prefix,
            name=name,
            ttf_path=font_info.ttf_path,
        )

    async def get_mapping(self, prefix: str) -> dict[str, str]:
        """Get character mapping for a font prefix."""
        if prefix not in self._mapping_cache:
            mapping_path = self.mappings_dir / f"{prefix}.json"
            with mapping_path.open("r") as f:
                self._mapping_cache[prefix] = load_json(f, return_type=dict)
        return self._mapping_cache[prefix]

    async def get_character(self, icon_name: str) -> str:
        """Get the Unicode character for an icon name."""
        prefix, name = icon_name.split(".", 1)
        mapping = await self.get_mapping(prefix)

        try:
            char_code = mapping[name]
            return chr(int(char_code, 16))
        except (KeyError, ValueError) as e:
            msg = f"Icon '{name}' not found in font {prefix}"
            raise ValueError(msg) from e


if __name__ == "__main__":

    async def main():
        registry = FontRegistry()

        font_infos = await registry.get_fonts([
            "fontawesome-regular",
            "material",
            "codicons",
            "remix",
            "phosphor",
        ])
        print(font_infos)
        icon = await registry.get_icon("fa.building")
        print(icon)

    asyncio.run(main())
