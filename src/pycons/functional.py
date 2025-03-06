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
    from pycons.font_providers.registry import FontRegistry

    registry = FontRegistry()
    return await registry.get_icon(icon_name)


def get_icon_sync(icon_name: str) -> Icon:
    """Synchronous version of get_icon_async."""
    return asyncio.run(get_icon(icon_name))


async def get_icon_from_iconify_id(iconify_id: str) -> Icon:
    """Get an icon using an Iconify identifier format.

    Args:
        iconify_id: Icon identifier in Iconify format (e.g., "mdi:home" or
                   "material-symbols:home-outline")

    Returns:
        Icon object

    Raises:
        ValueError: If the icon identifier is invalid or the icon is not found
    """
    from pycons.font_providers.registry import FontRegistry

    # Parse the Iconify identifier
    if ":" not in iconify_id:
        msg = f"Invalid Iconify identifier: {iconify_id}. Expected format: 'prefix:name'"
        raise ValueError(msg)

    namespace, icon_name = iconify_id.split(":", 1)

    # Map Iconify namespaces to our provider prefixes
    namespace_map = {
        "mdi": "mdi",  # Community Material Design
        "fa6-regular": "fa",  # Font Awesome Regular
        "fa6-solid": "fas",  # Font Awesome Solid
        "fa6-brands": "fab",  # Font Awesome Brands
        "codicon": "msc",  # VS Code Codicons
        "ph": "ph",  # Phosphor
        "ri": "ri",  # Remix
        "el": "el",  # Elusive
    }

    # Special handling for material-symbols
    if namespace == "material-symbols":
        if icon_name.endswith("-outline"):
            prefix = "mso"  # Material Symbols Outlined
            name = icon_name[:-8]  # Remove "-outline" suffix
        elif icon_name.endswith("-rounded"):
            prefix = "msr"  # Material Symbols Rounded
            name = icon_name[:-8]  # Remove "-rounded" suffix
        elif icon_name.endswith("-sharp"):
            prefix = "mss"  # Material Symbols Sharp
            name = icon_name[:-6]  # Remove "-sharp" suffix
        else:
            # Default to outlined if no style suffix
            prefix = "mso"
            name = icon_name
    else:
        # For other namespaces, look up the mapping
        prefix = namespace_map.get(namespace)  # type: ignore[assignment]
        if not prefix:
            msg = f"Unsupported Iconify namespace: {namespace}"
            raise ValueError(msg)
        name = icon_name

    # Use our standard get_icon method with the mapped prefix and name
    registry = FontRegistry()
    return await registry.get_icon(f"{prefix}.{name}")
