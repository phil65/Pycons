"""Models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class FontInfo:
    """Information about a font package."""

    name: str  # e.g. "fontawesome"
    prefix: str  # e.g. "fa"
    display_name: str  # e.g. "Font Awesome 6 Free Regular"
    current_version: str  # e.g. "6.7.2"
    ttf_path: Path  # Path to the downloaded TTF file
    mapping_path: Path  # Path to the downloaded mapping file


@dataclass
class Icon:
    """Represents a font icon with all its context."""

    character: str  # The actual Unicode character
    provider: str  # The provider name (e.g. "fontawesome-regular")
    prefix: str  # The provider prefix (e.g. "fa")
    name: str  # The icon name (e.g. "home")
    ttf_path: Path  # Path to the font file

    @property
    def css_class(self) -> str:
        """CSS class to use for this icon."""
        return f"icon-{self.prefix}"

    @property
    def font_family(self) -> str:
        """Font family name for CSS."""
        # This might need to be mapped from provider to actual font family name
        return self.provider
