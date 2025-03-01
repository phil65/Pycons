"""Font providers."""

from __future__ import annotations

from typing import ClassVar

from pycons.base import FontProvider
from pycons.utils import (
    extract_unicode_from_css,
    fetch_url,
    load_json,
)


class FontAwesomeBase(FontProvider):
    """Base class for all FontAwesome providers."""

    GITHUB_API = "https://api.github.com/repos/FortAwesome/Font-Awesome/releases/latest"
    BASE_URL = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome"

    async def get_latest_version(self) -> str:
        data = await fetch_url(self.GITHUB_API)
        release_info = load_json(data)
        return release_info["tag_name"].lstrip("v")


class FontAwesomeRegularProvider(FontAwesomeBase):
    NAME: ClassVar[str] = "fontawesome-regular"
    PREFIX: ClassVar[str] = "fa"
    DISPLAY_NAME: ClassVar[str] = "Font Awesome 6 Free Regular"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        return (
            f"{self.BASE_URL}/{version}/webfonts/fa-regular-400.ttf",
            f"{self.BASE_URL}/{version}/metadata/icons.json",
        )

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        data = load_json(mapping_data)
        return {
            name: info["unicode"]
            for name, info in data.items()
            if "regular" in info["styles"]
        }


class FontAwesomeSolidProvider(FontAwesomeBase):
    NAME: ClassVar[str] = "fontawesome-solid"
    PREFIX: ClassVar[str] = "fas"
    DISPLAY_NAME: ClassVar[str] = "Font Awesome 6 Free Solid"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        return (
            f"{self.BASE_URL}/{version}/webfonts/fa-solid-900.ttf",
            f"{self.BASE_URL}/{version}/metadata/icons.json",
        )

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        data = load_json(mapping_data)
        return {
            name: info["unicode"]
            for name, info in data.items()
            if "solid" in info["styles"]
        }


class FontAwesomeBrandsProvider(FontAwesomeBase):
    NAME: ClassVar[str] = "fontawesome-brands"
    PREFIX: ClassVar[str] = "fab"
    DISPLAY_NAME: ClassVar[str] = "Font Awesome 6 Brands"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        return (
            f"{self.BASE_URL}/{version}/webfonts/fa-brands-400.ttf",
            f"{self.BASE_URL}/{version}/metadata/icons.json",
        )

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        data = load_json(mapping_data)
        return {
            name: info["unicode"]
            for name, info in data.items()
            if "brands" in info["styles"]
        }


class MaterialDesignProvider(FontProvider):
    """Provider for Material Design icons."""

    NAME: ClassVar[str] = "material"
    PREFIX: ClassVar[str] = "mdi"
    DISPLAY_NAME: ClassVar[str] = "Material Design Icons"

    VERSION_URL = "https://api.github.com/repos/Templarian/MaterialDesign-Webfont/tags"
    BASE_URL = (
        "https://raw.githubusercontent.com/Templarian/MaterialDesign-Webfont/master"
    )
    CSS_PATTERN = r'\.mdi-([^:]+):before\s*{\s*content:\s*"(.+)"\s*}'

    async def get_latest_version(self) -> str:
        """Get latest version from GitHub tags."""
        data = await fetch_url(self.VERSION_URL)
        tags = load_json(data)
        # Tags API returns list of tags, first one is most recent
        return tags[0]["name"].lstrip("v")

    def get_download_urls(self, version: str) -> tuple[str, str]:
        return (
            f"{self.BASE_URL}/fonts/materialdesignicons-webfont.ttf",
            f"{self.BASE_URL}/css/materialdesignicons.css",
        )

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        """Process Material Design Icons CSS with a custom parser."""
        content = mapping_data.decode("utf-8")

        # Print a sample to understand the format
        print(f"CSS sample: {content[:500]}")

        # Custom parser for Material Design Icons CSS
        icons = {}

        # Look for patterns like: .mdi-access-point:before { content: "\F0003"; }
        for line in content.splitlines():
            # First find the selector line
            if ".mdi-" in line and ":before" in line:
                # Extract the icon name
                icon_name = line.split(".mdi-")[1].split(":before")[0]

                # Look ahead for the content line with Unicode value
                for i in range(3):  # Check next few lines
                    if i + 1 >= len(content.splitlines()):
                        break
                    content_line = content.splitlines()[
                        content.splitlines().index(line) + i + 1
                    ]
                    if "content:" in content_line and "\\F" in content_line.upper():
                        # Extract the Unicode value
                        unicode_value = (
                            content_line.split("content:")[1]
                            .split('"\\')[1]
                            .split('"')[0]
                        )
                        icons[icon_name] = f"0x{unicode_value.lower()}"
                        break

        print(f"Extracted {len(icons)} icons")
        if icons:
            print(f"First 3 icons: {list(icons.items())[:3]}")

        return icons


class CodiconsProvider(FontProvider):
    """Provider for Microsoft's Codicons."""

    NAME: ClassVar[str] = "codicons"
    PREFIX: ClassVar[str] = "msc"
    DISPLAY_NAME: ClassVar[str] = "VS Code Codicons"

    VERSION_URL = "https://api.github.com/repos/microsoft/vscode-codicons/releases/latest"

    async def get_latest_version(self) -> str:
        data = await fetch_url(self.VERSION_URL)
        release_info = load_json(data)
        return release_info["tag_name"].lstrip("v")

    def get_download_urls(self, version: str) -> tuple[str, str]:
        return (
            f"https://github.com/microsoft/vscode-codicons/releases/download/{version}/codicon.ttf",
            f"https://raw.githubusercontent.com/microsoft/vscode-codicons/{version}/src/template/mapping.json",
        )

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        data = load_json(mapping_data)
        return {name.lower(): hex(code) for name, code in data.items()}


class PhosphorProvider(FontProvider):
    """Provider for Phosphor icons."""

    NAME: ClassVar[str] = "phosphor"
    PREFIX: ClassVar[str] = "ph"
    DISPLAY_NAME: ClassVar[str] = "Phosphor Icons"

    VERSION_URL = "https://api.github.com/repos/phosphor-icons/web/tags"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        base = f"https://raw.githubusercontent.com/phosphor-icons/web/{version}"
        return (f"{base}/src/regular/Phosphor.ttf", f"{base}/src/Phosphor.json")

    async def get_latest_version(self) -> str:
        # data = await fetch_url(self.VERSION_URL)
        # tags = load_json(data)
        # # Tags endpoint returns a list, first one is most recent
        # return tags[0]["name"].lstrip("v")
        return "master"

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        """Process the Phosphor.json mapping file."""
        data = load_json(mapping_data)

        # Get the regular icon set's icons (first set in iconSets array)
        icons = data["iconSets"][0]["icons"]

        # Create mapping from tag to unicode point
        return {
            tag: hex(icon["grid"])  # Convert grid number to hex string
            for icon in icons
            for tag in icon["tags"]  # Each icon can have multiple tags
        }


class RemixProvider(FontProvider):
    """Provider for Remix icons."""

    NAME: ClassVar[str] = "remix"
    PREFIX: ClassVar[str] = "ri"
    DISPLAY_NAME: ClassVar[str] = "Remix Icon"

    # VERSION_URL = "https://api.github.com/repos/Remix-Design/RemixIcon/tags"
    CSS_PATTERN = r'^\.ri-(.+):before {\s*content: "(.+)";\s*}$'

    def get_download_urls(self, version: str) -> tuple[str, str]:
        base = "https://raw.githubusercontent.com/Remix-Design/RemixIcon/master"
        return (f"{base}/fonts/remixicon.ttf", f"{base}/fonts/remixicon.css")

    async def get_latest_version(self) -> str:
        # data = await fetch_url(self.VERSION_URL)
        # tags = load_json(data)
        # # Tags endpoint returns a list, first one is most recent
        # return tags[0]["name"].lstrip("v")
        return "master"

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        return extract_unicode_from_css(mapping_data, self.CSS_PATTERN)


PROVIDERS = {
    FontAwesomeRegularProvider.NAME: FontAwesomeRegularProvider(),
    FontAwesomeSolidProvider.NAME: FontAwesomeSolidProvider(),
    FontAwesomeBrandsProvider.NAME: FontAwesomeBrandsProvider(),
    MaterialDesignProvider.NAME: MaterialDesignProvider(),
    CodiconsProvider.NAME: CodiconsProvider(),
    PhosphorProvider.NAME: PhosphorProvider(),
    RemixProvider.NAME: RemixProvider(),
}
