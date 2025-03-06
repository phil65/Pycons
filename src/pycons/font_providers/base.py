"""Base class for font providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar


class FontProvider(ABC):
    """Base class for font providers."""

    # Override in subclasses
    NAME: ClassVar[str]
    PREFIX: ClassVar[str]
    DISPLAY_NAME: ClassVar[str]

    def __init__(self, use_cache: bool = True) -> None:
        super().__init__()
        self.use_cache = use_cache

    @abstractmethod
    async def get_latest_version(self) -> str:
        """Get the latest version from the source."""
        ...

    @abstractmethod
    def get_download_urls(self, version: str) -> tuple[str, str]:
        """Get URLs for the font file and mapping.

        Returns:
            Tuple of (ttf_url, mapping_url)
        """
        ...

    @abstractmethod
    def process_mapping(self, mapping_data: bytes) -> dict[str, str]:
        """Process the raw mapping data into a name->unicode dict.

        Different fonts provide their mappings in different formats (JSON, CSS, etc).
        This method handles the font-specific processing.

        Args:
            mapping_data: Raw bytes of the mapping file

        Returns:
            Dict mapping icon names to unicode points
        """
        ...
