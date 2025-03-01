"""Font-based icon providers."""

from __future__ import annotations

import asyncio

# Re-export the Icon class with absolute import
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pycons.models import Icon


async def get_icon(icon_name: str) -> Icon:
    """Get an icon character and font family.

    Args:
        icon_name: Name in format "prefix.name" (e.g. "fa.heart")

    Returns:
        Tuple of (unicode_character, font_family)
    """
    from pycons.registry import FontRegistry

    registry = FontRegistry()
    return await registry.get_icon(icon_name)


def get_icon_sync(icon_name: str) -> Icon:
    """Synchronous version of get_icon_async."""
    return asyncio.run(get_icon(icon_name))
