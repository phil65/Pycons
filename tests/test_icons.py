"""Test the icon providers."""

import pytest

from pycons.font_providers.registry import FontRegistry
from pycons.functional import get_icon_from_iconify_id


@pytest.mark.parametrize(
    ("icon_id", "provider_name"),
    [
        ("fa.heart", "Font Awesome Regular"),
        ("fas.heart", "Font Awesome Solid"),
        ("fab.github", "Font Awesome Brands"),
        ("mdi.home", "Community Material Design"),
        ("mso.home", "Google Material Symbols Outlined"),
        ("msr.home", "Google Material Symbols Rounded"),
        ("mss.home", "Google Material Symbols Sharp"),
        ("msc.home", "VS Code Codicons"),
        ("ph.house", "Phosphor"),
        ("ri.home-line", "Remix"),
        ("el.home", "Elusive"),
    ],
)
async def test_standard_provider_format(icon_id, provider_name):
    """Test fetching icons using standard provider format."""
    registry = FontRegistry()
    icon = await registry.get_icon(icon_id)
    assert icon.character, f"{provider_name} icon has no character"
    assert icon.ttf_path.exists(), f"{provider_name} font file does not exist"


@pytest.mark.parametrize(
    ("iconify_id", "provider_name"),
    [
        ("mdi:home", "Community Material Design"),
        ("fa6-regular:heart", "Font Awesome Regular"),
        ("fa6-solid:heart", "Font Awesome Solid"),
        ("fa6-brands:github", "Font Awesome Brands"),
        ("material-symbols:home-outline", "Google Material Symbols Outlined"),
        ("material-symbols:home-rounded", "Google Material Symbols Rounded"),
        ("material-symbols:home-sharp", "Google Material Symbols Sharp"),
        ("codicon:home", "VS Code Codicons"),
        ("ph:house", "Phosphor"),
        ("ri:home-line", "Remix"),
        ("el:home", "Elusive"),
    ],
)
async def test_iconify_format(iconify_id, provider_name):
    """Test fetching icons using Iconify format."""
    icon = await get_icon_from_iconify_id(iconify_id)
    assert icon.character, f"{provider_name} icon has no character"
    assert icon.ttf_path.exists(), f"{provider_name} font file does not exist"


if __name__ == "__main__":
    pytest.main([__file__])
