"""Wrapper for the Iconify API and the Iconify icon set packages.

Per-icon calls (`svg`, `css`, `icon_data`, `search`, ...) go to the Iconify API.
Collection-level calls (`collections`, `collection`, `icon_set`) load the
`@iconify/collections` and `@iconify-json/<prefix>` npm packages from a CDN,
as the public API is rate-limited for bulk usage.

Environment variables:

| Variable | Default |
|---|---|
| `PYCONS_ICONIFY_API` | `https://api.iconify.design` |
| `PYCONS_ICONIFY_CDN` | `https://cdn.jsdelivr.net/npm,https://unpkg.com` |

CDN roots are tried in order. jsDelivr refuses files above 50 MB (e.g. `fluent-emoji`),
unpkg serves those.
"""

from __future__ import annotations

import contextlib
import email.utils
import functools
import os
import re
import time
from typing import TYPE_CHECKING, Any, Literal, cast, overload
from urllib.parse import urljoin
import warnings

import anyenv

from pycons.iconify.errors import IconifyError, IconifyRateLimitError, IconNotFoundError
from pycons.iconify.iconify_types import (
    APIv2CollectionResponse,
    APIv2SearchResponse,
    APIv3KeywordsResponse,
    IconifyInfo,
    IconifyJSON,
    IconifyMetadata,
)


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Mapping

    from anyenv.download.http_types import ParamsType

    from pycons.iconify.iconify_types import Flip, Rotation

StylesheetFormat = Literal["expanded", "compact", "compressed"]


API_ROOT_ENV = "PYCONS_ICONIFY_API"
CDN_ROOT_ENV = "PYCONS_ICONIFY_CDN"
DEFAULT_API_ROOT = "https://api.iconify.design"
DEFAULT_CDN_ROOTS = ("https://cdn.jsdelivr.net/npm", "https://unpkg.com")

API_TIMEOUT = 10
CDN_TIMEOUT = 60
METADATA_TTL = "1d"
DATA_TTL = "7d"
MAX_REDIRECTS = 5


def api_root() -> str:
    """Return the Iconify API root URL."""
    return os.environ.get(API_ROOT_ENV, DEFAULT_API_ROOT).rstrip("/")


def cdn_roots() -> list[str]:
    """Return the root URLs of the npm CDNs serving the Iconify packages, in order."""
    value = os.environ.get(CDN_ROOT_ENV, "")
    roots = [root.strip().rstrip("/") for root in value.split(",") if root.strip()]
    return roots or list(DEFAULT_CDN_ROOTS)


def _retry_after(headers: Mapping[str, str]) -> int | None:
    value = next((v for k, v in headers.items() if k.lower() == "retry-after"), None)
    if value is None:
        return None
    if value.isdigit():
        return int(value)
    try:
        date = email.utils.parsedate_to_datetime(value)
    except TypeError, ValueError:
        return None
    return max(0, int(date.timestamp() - time.time()))


@contextlib.contextmanager
def _translate_errors(url: str) -> Generator[None]:
    try:
        yield
    except anyenv.ResponseError as e:
        match e.status_code:
            case 404:
                raise IconNotFoundError(url) from e
            case 429:
                headers = e.response.headers if e.response else {}
                raise IconifyRateLimitError(url, _retry_after(headers)) from e
            case code:
                msg = f"HTTP {code}: {url}"
                raise IconifyError(msg, url) from e


def _get_json[T](
    url: str,
    return_type: type[T],
    *,
    ttl: str,
    params: ParamsType | None = None,
    timeout: float = API_TIMEOUT,
) -> T:
    # return_type is only used for typing: anyenv validates via isinstance without
    # pydantic (fails for TypedDicts), and validating whole icon sets would be slow.
    with _translate_errors(url):
        data: Any = anyenv.get_json_sync(
            url, params=params, timeout=timeout, cache=True, cache_ttl=ttl
        )
    return cast("T", data)


def _get_text(url: str, *, ttl: str, params: ParamsType | None = None) -> str:
    with _translate_errors(url):
        return anyenv.get_text_sync(
            url, params=params, timeout=API_TIMEOUT, cache=True, cache_ttl=ttl
        )


def _get_bytes(url: str, *, ttl: str, params: ParamsType | None = None) -> bytes:
    with _translate_errors(url):
        return anyenv.get_bytes_sync(
            url, params=params, timeout=API_TIMEOUT, cache=True, cache_ttl=ttl
        )


@functools.cache
def _resolve_redirects(url: str) -> str:
    """Return the final URL after redirects (e.g. unpkg's version redirect).

    anyenv does not follow redirects. On network errors the URL is returned unchanged,
    so cached responses stay usable offline.
    """
    for _ in range(MAX_REDIRECTS):
        try:
            with _translate_errors(url):
                response = anyenv.request_sync("HEAD", url, timeout=API_TIMEOUT)
        except anyenv.RequestError:
            return url
        if not 300 <= response.status_code < 400 or not (  # noqa: PLR2004
            location := response.headers.get("location")
        ):
            return url
        url = urljoin(url, location)
    return url


def _package_json[T](package: str, file: str, return_type: type[T]) -> T:
    """Fetch a file of an npm package, trying the CDN roots in order.

    A 404 is final, other HTTP and network errors fall through to the next root.
    """
    *fallbacks, last = cdn_roots()
    for root in fallbacks:
        try:
            url = _resolve_redirects(f"{root}/{package}/{file}")
            return _get_json(url, return_type, ttl=DATA_TTL, timeout=CDN_TIMEOUT)
        except IconNotFoundError:
            raise
        except IconifyError, anyenv.RequestError:
            continue
    url = _resolve_redirects(f"{last}/{package}/{file}")
    return _get_json(url, return_type, ttl=DATA_TTL, timeout=CDN_TIMEOUT)


def _optional_package_json[T](package: str, file: str, return_type: type[T]) -> T | None:
    try:
        return _package_json(package, file, return_type)
    except IconNotFoundError:
        return None


def collections(*prefixes: str) -> dict[str, IconifyInfo]:
    """Return collections where key is icon set prefix, value is IconifyInfo object.

    https://iconify.design/docs/api/collections.html

    Loaded from the `@iconify/collections` package instead of the API.

    Args:
        prefixes: Icon set prefixes to filter by. Partial prefixes ending with "-"
            match all sets starting with them (e.g. "mdi-" matches "mdi-light").
            If none are given, all collections are returned.
    """
    data = _package_json("@iconify/collections", "collections.json", dict[str, IconifyInfo])
    if not prefixes:
        return data
    return {
        key: info
        for key, info in data.items()
        if any(key == p or (p.endswith("-") and key.startswith(p)) for p in prefixes)
    }


def icon_set(prefix: str) -> IconifyJSON:
    """Return the complete data of an icon set, including all icons and aliases.

    Loaded from the `@iconify-json/<prefix>` package.

    Args:
        prefix: Icon set prefix.
    """
    return _package_json(f"@iconify-json/{prefix}", "icons.json", IconifyJSON)


def collection(
    prefix: str,
    info: bool = False,
    chars: bool = False,
) -> APIv2CollectionResponse:
    """Return a list of icons in an icon set.

    https://iconify.design/docs/api/collection.html

    Built from the `@iconify-json/<prefix>` package in the same shape as the API
    response.

    Parameters
    ----------
    prefix : str
        Icon set prefix.
    info : bool, optional
        If enabled, the response will include icon set information.
    chars : bool, optional
        If enabled, the response will include the character map. The character map
        exists only in icon sets that were imported from icon fonts.
    """
    package = f"@iconify-json/{prefix}"
    data = icon_set(prefix)
    set_info = _package_json(package, "info.json", IconifyInfo)
    metadata = _optional_package_json(package, "metadata.json", IconifyMetadata) or {}
    icons = data["icons"]
    aliases = data.get("aliases", {})

    visible = [name for name, icon in icons.items() if not icon.get("hidden")]
    visible_set = set(visible)
    categories = {
        title: [name for name in names if name in visible_set]
        for title, names in metadata.get("categories", {}).items()
    }
    categorized = {name for names in categories.values() for name in names}
    hidden = [name for name, icon in icons.items() if icon.get("hidden")]
    hidden += [name for name, alias in aliases.items() if alias.get("hidden")]

    response: APIv2CollectionResponse = {
        "prefix": prefix,
        "total": len(visible),
        "title": set_info["name"],
    }
    if uncategorized := [name for name in visible if name not in categorized]:
        response["uncategorized"] = uncategorized
    if categories:
        response["categories"] = categories
    if hidden:
        response["hidden"] = hidden
    if visible_aliases := {
        name: alias["parent"] for name, alias in aliases.items() if not alias.get("hidden")
    }:
        response["aliases"] = visible_aliases
    if "prefixes" in metadata:
        response["prefixes"] = metadata["prefixes"]
    if "suffixes" in metadata:
        response["suffixes"] = metadata["suffixes"]
    if info:
        response["info"] = set_info
    if chars and (char_map := _optional_package_json(package, "chars.json", dict[str, str])):
        response["chars"] = char_map
    return response


def last_modified(*prefixes: str) -> dict[str, int]:
    """Return last modified date for icon sets.

    https://iconify.design/docs/api/last-modified.html

    Example:
    https://api.iconify.design/last-modified?prefixes=mdi,mdi-light,tabler

    Parameters
    ----------
    prefixes : Sequence[str], optional
        Comma separated list of icon set prefixes. You can use partial prefixes that
        end with "-", such as "mdi-" matches "mdi-light".  If None, return all
        collections.

    Returns
    -------
    dict[str, int]
        Dictionary where key is icon set prefix, value is last modified date as
        UTC integer timestamp.
    """
    query_params = {"prefixes": ",".join(prefixes)}
    content = _get_json(f"{api_root()}/last-modified", dict, ttl=METADATA_TTL, params=query_params)
    if "lastModified" not in content:  # pragma: no cover
        msg = f"Unexpected response from API: {content}. Expected 'lastModified'."
        raise ValueError(msg)
    return content["lastModified"]


def svg(
    *key: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> bytes:
    """Generate SVG for icon.

    https://iconify.design/docs/api/svg.html

    Returns a bytes object containing the SVG data: `b'<svg>...</svg>'`

    Example:
    https://api.iconify.design/fluent-emoji-flat/alarm-clock.svg?height=48&width=48

    Parameters
    ----------
    key: str
        Icon set prefix and name. May be passed as a single string in the format
        `"prefix:name"` or as two separate strings: `'prefix', 'name'`.
    color : str, optional
        Icon color. Replaces currentColor with specific color, resulting in icon with
        hardcoded palette.
    height : str | int, optional
        Icon height. If only one dimension is specified, such as height, other
        dimension will be automatically set to match it.
    width : str | int, optional
        Icon width. If only one dimension is specified, such as height, other
        dimension will be automatically set to match it.
    flip : str, optional
        Flip icon.
    rotate : str | int, optional
        Rotate icon. If an integer is provided, it is assumed to be in degrees.
    box : bool, optional
        Adds an empty rectangle to SVG that matches the icon's viewBox. It is needed
        when importing SVG to various UI design tools that ignore viewBox. Those tools,
        such as Sketch, create layer groups that automatically resize to fit content.
        Icons usually have empty pixels around icon, so such software crops those empty
        pixels and icon's group ends up being smaller than actual icon, making it harder
        to align it in design.
    """
    prefix, name = _split_prefix_name(key)

    if rotate not in (None, 1, 2, 3):
        rotate = str(rotate).replace("deg", "") + "deg"  # ty: ignore[invalid-assignment]

    query_params = {
        "color": color,
        "height": height,
        "width": width,
        "flip": flip,
        "rotate": rotate,
    }

    # Remove None values
    query_params = {k: v for k, v in query_params.items() if v is not None}

    if box:
        query_params["box"] = 1

    return _get_bytes(f"{api_root()}/{prefix}/{name}.svg", ttl=DATA_TTL, params=query_params)


def css(
    *keys: str,
    selector: str | None = None,
    common: str | None = None,
    override: str | None = None,
    pseudo: bool | None = None,
    var: str | None = None,
    square: bool | None = None,
    color: str | None = None,
    mode: Literal["mask", "background"] | None = None,
    format: StylesheetFormat | None = None,  # noqa: A002
) -> str:
    """Return CSS for `icons` in `prefix`.

    https://iconify.design/docs/api/css.html

    Iconify API can dynamically generate CSS for icons, where icons are used as
    background or mask image.

    Example:
    https://api.iconify.design/mdi.css?icons=account-box,account-cash,account,home

    Parameters
    ----------
    keys : str
        Icon set prefix and name(s). May be passed as a single string in the format
        `"prefix:name"` or as multiple strings: `'prefix', 'name1', 'name2'`.
        To generate CSS for icons from multiple icon sets, send separate queries for
        each icon set.
    selector : str, optional
        CSS selector for icons. If not set, defaults to ".icon--{prefix}--{name}"
        Variable "{prefix}" is replaced with icon set prefix, "{name}" with icon name.
    common : str, optional
        Common selector for icons, defaults to ".icon--{prefix}". Set it to empty to
        disable common code. Variable "{prefix}" is replaced with icon set prefix.
    override : str, optional
        Selector that mixes `selector` and `common` to generate icon specific
        style that overrides common style. Default value is
        `".icon--{prefix}.icon--{prefix}--{name}"`.
    pseudo : bool, optional
         Set it to `True` if selector for icon is a pseudo-selector, such as
         ".icon--{prefix}--{name}::after".
    var : str, optional
        Name for variable to use for icon, defaults to `"svg"` for monotone icons,
        `None` for icons with palette. Set to null to disable.
    square : bool, optional
        Forces icons to have width of 1em.
    color : str, optional
        Sets color for monotone icons. Also renders icons as background images.
    mode : Literal["mask", "background"], optional
        Forces icon to render as mask image or background image. If not set, mode will
        be detected from icon content: icons that contain currentColor will be rendered
        as mask image, other icons as background image.
    format : Literal["expanded", "compact", "compressed"], optional
        Stylesheet formatting option. Matches options used in Sass. Supported values
        are "expanded", "compact" and "compressed".
    """
    prefix, icons = _split_prefix_name(keys, allow_many=True)
    params: dict = {"icons": ",".join(icons)}

    for k in ("selector", "common", "override", "var", "color", "mode", "format"):
        if (val := locals()[k]) is not None:
            params[k] = val
    if pseudo:
        params["pseudo"] = 1
    if square:
        params["square"] = 1

    resp = _get_text(f"{api_root()}/{prefix}.css", ttl=DATA_TTL, params=params)
    if missing := set(re.findall(r"Could not find icon: ([^\s]*) ", resp)):
        warnings.warn(
            f"Icon(s) {sorted(missing)} not found. "
            "Search for icons at https://icon-sets.iconify.design",
            stacklevel=2,
        )
    return resp


def icon_data(*keys: str) -> IconifyJSON:
    """Return icon data for the given icons of one icon set.

    https://iconify.design/docs/api/icon-data.html

    Example:
    https://api.iconify.design/mdi.json?icons=acount-box,account-cash,account,home

    Missing icons are added to `not_found` property of response.

    Parameters
    ----------
    keys : str
        Icon set prefix and name(s). May be passed as a single string in the format
        `"prefix:icon"` or as multiple strings: `'prefix', 'icon1', 'icon2'`.
    """
    prefix, names = _split_prefix_name(keys, allow_many=True)
    return _get_json(
        f"{api_root()}/{prefix}.json?icons={','.join(names)}", IconifyJSON, ttl=DATA_TTL
    )


def search(
    query: str,
    limit: int | None = None,
    start: int | None = None,
    prefixes: Iterable[str] | None = None,
    category: str | None = None,
) -> APIv2SearchResponse:
    """Search icons.

    https://iconify.design/docs/api/search.html

    Example:
    https://api.iconify.design/search?query=arrows-horizontal&limit=999

    The Search query can include special keywords.

    For most keywords, the keyword and value can be separated by ":" or "=". It is
    recommended to use "=" because the colon can also be treated as icon set prefix.

    Keywords with boolean values can have the following values:

    "true" or "1" = true. "false" or "0" = false. Supported keywords:

    - `palette` (bool). Filter icon sets by palette.
      Example queries: "home palette=false", "cat palette=true".
    - `style` ("fill" | "stroke"). Filter icons by code.
      Example queries: "home style=fill", "cat style=stroke".
    - `fill` and `stroke` (bool). Same as above, but as boolean. Only one of keywords
      can be set: "home fill=true".
    - `prefix` (str). Same as prefix property from search query parameters, but in
      keyword. Overrides parameter.
    - `prefixes` (string). Same as prefixes property from
      search query parameters, but in keyword. Overrides parameter.

    Parameters
    ----------
    query : str
        Search string. Case insensitive.
    limit : int, optional
        Maximum number of items in response, default is 64. Min 32, max 999.
        If numer of icons in result matches limit, it means there are more icons to
        show.
    start : int, optional
        Start index for results, default is 0.
    prefixes : str | Iterable[str], optional
        List of icon set prefixes. You can use partial prefixes that
        end with "-", such as "mdi-" matches "mdi-light".
    category : str, optional
        Filter icon sets by category.
    """
    params: dict = {"query": query}
    if limit is not None:
        params["limit"] = limit
    if start is not None:
        params["start"] = start
    if prefixes is not None:
        if isinstance(prefixes, str):
            params["prefix"] = prefixes
        else:
            params["prefixes"] = ",".join(prefixes)
    if category is not None:
        params["category"] = category
    return _get_json(
        f"{api_root()}/search",
        APIv2SearchResponse,
        ttl=METADATA_TTL,
        params=params,
    )


def keywords(prefix: str | None = None, keyword: str | None = None) -> APIv3KeywordsResponse:
    """Intended for use in suggesting search queries.

    https://iconify.design/docs/api/keywords.html

    One of `prefix` or `keyword` MUST be specified.

    Keyword can only contain letters numbers and dash.
    If it contains "-", only the last part after "-" is used.
    Must be at least 2 characters long.

    Parameters
    ----------
    prefix : str, optional
        Keyword Prefix.  API returns all keywords that start with `prefix`.
    keyword : str, optional
        Partial keyword. API returns all keywords that start or
        end with `keyword`.  (Ignored if `prefix` is specified).
    """
    if prefix:
        if keyword:
            warnings.warn(
                "Cannot specify both prefix and keyword. Ignoring keyword.",
                stacklevel=2,
            )
        params = {"prefix": prefix}
    elif keyword:
        params = {"keyword": keyword}
    else:
        params = {}
    return _get_json(
        f"{api_root()}/keywords", APIv3KeywordsResponse, ttl=METADATA_TTL, params=params
    )


def iconify_version() -> str:
    """Return version of iconify API.

    https://iconify.design/docs/api/version.html

    The purpose of this query is to be able to tell which server you are connected to,
    but without exposing actual location of server, which can help debug error.
    This is used in networks when many servers are running.

    Examples
    --------
    >>> iconify_version()
    'Iconify API version 3.0.0-beta.1'
    """
    return _get_text(f"{api_root()}/version", ttl=METADATA_TTL)


@overload
def _split_prefix_name(
    key: tuple[str, ...], allow_many: Literal[False] = ...
) -> tuple[str, str]: ...


@overload
def _split_prefix_name(
    key: tuple[str, ...], allow_many: Literal[True]
) -> tuple[str, tuple[str, ...]]: ...


def _split_prefix_name(
    key: tuple[str, ...], allow_many: bool = False
) -> tuple[str, str] | tuple[str, tuple[str, ...]]:
    """Convenience function to split prefix and name from key.

    Examples
    --------
    >>> _split_prefix_name(("mdi", "account"))
    ("mdi", "account")
    >>> _split_prefix_name(("mdi:account",))
    ("mdi", "account")
    """
    if not key:
        msg = "icon key must be at least one string."
        raise ValueError(msg)
    if len(key) == 1:
        if ":" not in key[0]:
            msg = f"Single-argument icon names must be in the format 'prefix:name'. Got {key[0]!r}"
            raise ValueError(msg)
        prefix, name = key[0].split(":", maxsplit=1)
        return (prefix, (name,)) if allow_many else (prefix, name)
    prefix, *rest = key
    if not allow_many:
        if len(rest) > 1:
            msg = "icon key must be either 1 or 2 arguments."
            raise ValueError(msg)
        return prefix, rest[0]
    return prefix, tuple(rest)


if __name__ == "__main__":
    data = svg("mdi:account")
    print(data)
