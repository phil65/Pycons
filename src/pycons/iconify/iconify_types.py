"""Type definitions for iconify response objects.

Credits to pyconify library.
https://github.com/pyapp-kit/pyconify/blob/main/src/pyconify/iconify_types.py
"""

from __future__ import annotations  # pragma: no cover

from typing import Literal, NotRequired, Required, TypedDict


Rotation = Literal["90", "180", "270", 90, 180, 270, "-90", 1, 2, 3]
Flip = Literal["horizontal", "vertical", "horizontal,vertical"]


class Author(TypedDict, total=False):
    """Author information."""

    name: Required[str]
    """Author name."""
    url: NotRequired[str]
    """Author website."""


class License(TypedDict, total=False):
    """License information."""

    title: Required[str]
    """License title."""
    spdx: str
    """SPDX license ID."""
    url: str
    """License URL."""


class IconifyInfo(TypedDict, total=False):
    """Icon set information block."""

    name: Required[str]
    """Icon set name."""
    author: Required[Author]
    """Author info."""
    license: Required[License]
    """License info."""
    total: int
    """Total number of icons."""
    version: str
    """Version string."""
    height: int | list[int]
    """Icon grid: number or array of numbers."""
    displayHeight: int
    """Display height for samples: 16 - 24."""
    category: str
    """Category on Iconify collections list."""
    tags: list[str]
    """List of tags to group similar icon sets."""
    palette: bool
    """Palette status. True -> predefined color scheme, False -> use currentColor."""
    hidden: bool
    """If true, icon set should not appear in icon sets list."""


class APIv2CollectionResponse(TypedDict, total=False):
    """Object returned from collection(prefix)."""

    prefix: Required[str]
    """Icon set prefix."""
    total: Required[int]
    """Number of icons (duplicate of info?.total)."""
    title: str
    """Icon set title, if available (duplicate of info?.name)."""
    info: IconifyInfo
    """Icon set info."""
    uncategorized: list[str]
    """List of icons without categories."""
    categories: dict[str, list[str]]
    """List of icons, sorted by category."""
    hidden: list[str]
    """List of hidden icons."""
    aliases: dict[str, str]
    """List of aliases, key = alias, value = parent icon."""
    chars: dict[str, str]
    """Characters, key = character, value = icon name."""
    prefixes: dict[str, str]
    """Prefix mappings per https://iconify.design/docs/types/iconify-json-metadata.html#themes."""
    suffixes: dict[str, str]
    """Suffix mappings."""


class APIv3LastModifiedResponse(TypedDict):
    """key is icon set prefix, value is lastModified property from that icon set."""

    lastModified: dict[str, int]
    """Dictionary mapping icon set prefixes to their lastModified timestamps."""


class IconifyOptional(TypedDict, total=False):
    """Optional properties that contain icon dimensions and transformations."""

    left: int
    """Left position of the ViewBox, default = 0."""
    top: int
    """Top position of the ViewBox, default = 0."""
    width: int
    """Width of the ViewBox, default = 16."""
    height: int
    """Height of the ViewBox, default = 16."""
    rotate: int
    """Number of 90-degree rotations (1=90deg, etc...), default = 0."""
    hFlip: bool
    """Horizontal flip, default = false."""
    vFlip: bool
    """Vertical flip, default = false."""


class IconifyIcon(IconifyOptional, total=False):
    """Iconify icon object."""

    body: Required[str]
    """Icon's SVG data."""


class IconifyJSON(IconifyOptional, total=False):
    """Return value of icon_data(prefix, *names)."""

    prefix: Required[str]
    """Icon set prefix."""
    icons: Required[dict[str, IconifyIcon]]
    """Dictionary of icon names to icon data."""
    lastModified: int
    """Timestamp of last modification."""
    aliases: dict[str, str]
    """Dictionary mapping aliases to their parent icon names."""
    not_found: list[str]
    """List of icon names that were not found."""


class APIv2SearchResponse(TypedDict, total=False):
    """Return value of search(query)."""

    icons: list[str]
    """List of prefix:name."""
    total: int
    """Number of results. If same as `limit`, more results are available."""
    limit: int
    """Number of results shown."""
    start: int
    """Index of first result."""
    collections: dict[str, IconifyInfo]
    """List of icon sets that match query."""
    request: APIv2SearchParams
    """Copy of request parameters."""


class APIv2SearchParams(TypedDict, total=False):
    """Request parameters for search(query)."""

    query: Required[str]
    """Search string."""
    limit: int
    """Maximum number of items in response."""
    start: int
    """Start index for results."""
    prefix: str
    """Filter icon sets by one prefix."""
    prefixes: str
    """Filter icon sets by multiple prefixes or partial."""
    category: str
    """Filter icon sets by category."""
    similar: bool
    """Include partial matches for words (default = True)."""


class APIv3KeywordsResponse(TypedDict, total=False):
    """Return value of keywords()."""

    keyword: str
    """Keyword (one of keyword or prefix will be present)."""
    prefix: str
    """Prefix (one of keyword or prefix will be present)."""
    exists: Required[bool]
    """Whether the keyword exists."""
    matches: Required[list[str]]
    """Matching results."""
    invalid: Literal[True]
    """Indicates if the query was invalid."""
