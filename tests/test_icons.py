"""Test the icon providers."""

import pytest

from pycons.functional import get_icon_from_iconify_id
from pycons.registry import FontRegistry


@pytest.mark.asyncio
async def test_all_providers():
    """Test fetching one icon from each provider."""
    registry = FontRegistry()

    # Test standard provider format
    test_cases = [
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
    ]

    for icon_id, provider_name in test_cases:
        print(f"Testing {provider_name} ({icon_id})...")
        try:
            icon = await registry.get_icon(icon_id)
            print(f"  ✓ Success: {icon.character} ({hex(ord(icon.character))})")

            # Verify font file exists
            assert icon.ttf_path.exists(), f"Font file does not exist: {icon.ttf_path}"

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            raise

    # Test Iconify format
    iconify_test_cases = [
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
    ]

    for iconify_id, provider_name in iconify_test_cases:
        print(f"Testing Iconify format for {provider_name} ({iconify_id})...")
        try:
            icon = await get_icon_from_iconify_id(iconify_id)
            print(f"  ✓ Success: {icon.character} ({hex(ord(icon.character))})")

            # Verify font file exists
            assert icon.ttf_path.exists(), f"Font file does not exist: {icon.ttf_path}"

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            raise


if __name__ == "__main__":
    pytest.main([__file__])
