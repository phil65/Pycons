"""Font providers."""

from __future__ import annotations

import re
from typing import ClassVar

from anyenv import load_json

from pycons.font_providers.base import FontProvider
from pycons.utils import extract_unicode_from_css, fetch_url


class FontAwesomeBase(FontProvider):
    """Base class for all FontAwesome providers."""

    GITHUB_API = "https://api.github.com/repos/FortAwesome/Font-Awesome/releases/latest"
    BASE_URL = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome"

    async def get_latest_version(self) -> str:
        # data = await fetch_url(self.GITHUB_API, use_cache=self.use_cache)
        # release_info = load_json(data, return_type=dict)
        # return release_info["tag_name"].lstrip("v")
        # Pinned to 6.7.2 - FA 7.x changed repo structure (no TTF files)
        return "6.7.2"


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
        data = load_json(mapping_data, return_type=dict)
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
        data = load_json(mapping_data, return_type=dict)
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
        data = load_json(mapping_data, return_type=dict)
        return {
            name: info["unicode"]
            for name, info in data.items()
            if "brands" in info["styles"]
        }


class CommunityMaterialDesignProvider(FontProvider):
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
        data = await fetch_url(self.VERSION_URL, use_cache=self.use_cache)
        tags = load_json(data, return_type=list)
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
        icons = {}

        # Parse the CSS using the correct double-colon syntax
        current_icon = None
        for line in content.splitlines():
            if ".mdi-" in line and "::before" in line:
                # Extract the icon name
                current_icon = line.split(".mdi-")[1].split("::before")[0]
            elif current_icon and "content:" in line:
                # Extract the Unicode value - format is: content: "\F01C9";
                if "\\F" in line.upper() or "\\f" in line:
                    unicode_value = (
                        line.split("content:")[1]
                        .split('"\\')[1]  # Get part after the backslash
                        .split('"')[0]  # Get part before the closing quote
                    )
                    icons[current_icon] = f"0x{unicode_value.lower()}"
                current_icon = None

        return icons


class CodiconsProvider(FontProvider):
    """Provider for Microsoft's Codicons."""

    NAME: ClassVar[str] = "codicons"
    PREFIX: ClassVar[str] = "msc"
    DISPLAY_NAME: ClassVar[str] = "VS Code Codicons"

    VERSION_URL = "https://api.github.com/repos/microsoft/vscode-codicons/releases/latest"

    async def get_latest_version(self) -> str:
        # data = await fetch_url(self.VERSION_URL, use_cache=self.use_cache)
        # release_info = load_json(data, return_type=dict)
        # return release_info["tag_name"].lstrip("v")
        # Pinned to 0.0.36 - later versions don't include TTF in releases
        return "0.0.36"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        return (
            f"https://github.com/microsoft/vscode-codicons/releases/download/{version}/codicon.ttf",
            f"https://raw.githubusercontent.com/microsoft/vscode-codicons/{version}/src/template/mapping.json",
        )

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        data = load_json(mapping_data, return_type=dict)
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
        # data = await fetch_url(self.VERSION_URL, use_cache=self.use_cache)
        # tags = load_json(data)
        # # Tags endpoint returns a list, first one is most recent
        # return tags[0]["name"].lstrip("v")
        return "master"

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        """Process the Phosphor.json mapping file."""
        data = load_json(mapping_data, return_type=dict)

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
        # data = await fetch_url(self.VERSION_URL, use_cache=self.use_cache)
        # tags = load_json(data)
        # # Tags endpoint returns a list, first one is most recent
        # return tags[0]["name"].lstrip("v")
        return "master"

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        return extract_unicode_from_css(mapping_data, self.CSS_PATTERN)


class ElusiveIconsProvider(FontProvider):
    """Provider for Elusive Icons."""

    NAME: ClassVar[str] = "elusive"
    PREFIX: ClassVar[str] = "el"
    DISPLAY_NAME: ClassVar[str] = "Elusive Icons"

    # No need for version URL as we're using a static version
    VERSION_URL = "https://api.github.com/repos/dovy/elusive-icons/tags"
    BASE_URL = "https://raw.githubusercontent.com/dovy/elusive-icons/master"
    CSS_PATTERN = r'\.el-([^:]+):before\s*{\s*content:\s*"\\([^"]+)"\s*;\s*}'

    async def get_latest_version(self) -> str:
        """Get latest version, or use 'master' if API fails."""
        try:
            data = await fetch_url(self.VERSION_URL, use_cache=self.use_cache)
            tags = load_json(data, return_type=list)
            return tags[0]["name"].lstrip("v")
        except Exception:  # noqa: BLE001
            # Fall back to master branch if API fails
            return "master"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        """Get URLs for font file and CSS."""
        return (
            "https://github.com/dovy/elusive-icons/raw/master/fonts/elusiveicons-webfont.ttf",
            f"{self.BASE_URL}/css/elusive-icons.css",
        )

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        """Process Elusive Icons CSS to extract icon names and unicode points."""
        content = mapping_data.decode("utf-8")
        icons = {}

        # Parse CSS looking for patterns like: .el-home:before { content: "\f189"; }
        for line in content.splitlines():
            if ".el-" in line and ":before" in line:
                # Extract icon name
                icon_name = line.split(".el-")[1].split(":before")[0]

                # Look for the content property in the same or next line
                content_search = line
                if "{" in line and "content:" not in line:
                    # Content might be on next line
                    idx = content.find(line) + len(line)
                    next_brace = content.find("}", idx)
                    if next_brace > idx:
                        content_search = content[idx:next_brace]

                # Extract unicode value if available
                if "content:" in content_search:
                    # Format is: content: "\f189";
                    match = re.search(r'content:\s*"\\([^"]+)"', content_search)
                    if match:
                        unicode_value = match.group(1)
                        icons[icon_name] = f"0x{unicode_value.lower()}"

        return icons


class BaseGoogleMaterialSymbolsProvider(FontProvider):
    """Base provider for Google's official Material Symbols."""

    VERSION_URL = (
        "https://api.github.com/repos/google/material-design-icons/releases/latest"
    )
    BASE_URL = "https://github.com/google/material-design-icons/raw"

    async def get_latest_version(self) -> str:
        """Get latest version from GitHub releases."""
        return "master"

    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        """Process the .codepoints file format."""
        content = mapping_data.decode("utf-8")
        icons = {}

        # Parse the codepoints file - format is name[space]codepoint
        for line in content.splitlines():
            if line.strip() and " " in line:
                name, codepoint = line.strip().split(" ", 1)
                # Convert name to kebab-case if it contains underscores
                name = name.replace("_", "-").lower()
                # Convert codepoint to 0xXXXX format
                icons[name] = f"0x{codepoint}"

        return icons


class GoogleMaterialSymbolsOutlinedProvider(BaseGoogleMaterialSymbolsProvider):
    """Provider for Google Material Symbols Outlined style."""

    NAME: ClassVar[str] = "material-symbols-outlined"
    PREFIX: ClassVar[str] = "mso"
    DISPLAY_NAME: ClassVar[str] = "Google Material Symbols Outlined"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        base_url = "https://raw.githubusercontent.com/google/material-design-icons/master/variablefont"
        return (
            f"{base_url}/MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].ttf",
            f"{base_url}/MaterialSymbolsOutlined[FILL,GRAD,opsz,wght].codepoints",
        )


class GoogleMaterialSymbolsRoundedProvider(BaseGoogleMaterialSymbolsProvider):
    """Provider for Google Material Symbols Rounded style."""

    NAME: ClassVar[str] = "material-symbols-rounded"
    PREFIX: ClassVar[str] = "msr"
    DISPLAY_NAME: ClassVar[str] = "Google Material Symbols Rounded"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        base_url = "https://raw.githubusercontent.com/google/material-design-icons/master/variablefont"
        return (
            f"{base_url}/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].ttf",
            f"{base_url}/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].codepoints",
        )


class GoogleMaterialSymbolsSharpProvider(BaseGoogleMaterialSymbolsProvider):
    """Provider for Google Material Symbols Sharp style."""

    NAME: ClassVar[str] = "material-symbols-sharp"
    PREFIX: ClassVar[str] = "mss"
    DISPLAY_NAME: ClassVar[str] = "Google Material Symbols Sharp"

    def get_download_urls(self, version: str) -> tuple[str, str]:
        base_url = "https://raw.githubusercontent.com/google/material-design-icons/master/variablefont"
        return (
            f"{base_url}/MaterialSymbolsSharp[FILL,GRAD,opsz,wght].ttf",
            f"{base_url}/MaterialSymbolsSharp[FILL,GRAD,opsz,wght].codepoints",
        )


PROVIDERS = {
    FontAwesomeRegularProvider.NAME: FontAwesomeRegularProvider(),
    FontAwesomeSolidProvider.NAME: FontAwesomeSolidProvider(),
    FontAwesomeBrandsProvider.NAME: FontAwesomeBrandsProvider(),
    CommunityMaterialDesignProvider.NAME: CommunityMaterialDesignProvider(),
    GoogleMaterialSymbolsOutlinedProvider.NAME: GoogleMaterialSymbolsOutlinedProvider(),
    GoogleMaterialSymbolsRoundedProvider.NAME: GoogleMaterialSymbolsRoundedProvider(),
    GoogleMaterialSymbolsSharpProvider.NAME: GoogleMaterialSymbolsSharpProvider(),
    CodiconsProvider.NAME: CodiconsProvider(),
    PhosphorProvider.NAME: PhosphorProvider(),
    RemixProvider.NAME: RemixProvider(),
    ElusiveIconsProvider.NAME: ElusiveIconsProvider(),
}
