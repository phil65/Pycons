from __future__ import annotations

from typing import Literal


IconProvider = Literal[
    "google",
    "duckduckgo",
    "iconhorse",
    "yandex",
    "favicon_io",
    "favicon_ninja",
]


def get_favicon(
    url: str,
    provider: IconProvider = "duckduckgo",
    size: int = 32,
):
    """Return a favicon URL for the given URL.

    Args:
        url: The URL to get the favicon for.
        provider: The provider to use for the favicon.
        size: Size of the favicon in pixels (not supported by all providers)
    """
    from urllib.parse import urlparse

    # Parse the URL to get the domain
    domain = urlparse(url).netloc or url

    match provider:
        case "google":
            return f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"
        case "duckduckgo":
            return f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        case "iconhorse":
            return f"https://icon.horse/icon/{domain}?size={size}"
        case "yandex":
            # Yandex supports sizes: 16, 32, 76, 120, 180, 192, 256
            valid_sizes = [16, 32, 76, 120, 180, 192, 256]
            closest_size = min(valid_sizes, key=lambda x: abs(x - size))
            return f"https://favicon.yandex.net/favicon/{domain}?size={closest_size}"
        case "favicon_io":
            return f"https://favicon.io/favicon/{domain}"
        case "favicon_ninja":
            return f"https://favicon.ninja/icon?url={domain}&size={size}"
        case _:
            msg = f"Invalid provider: {provider}"
            raise ValueError(msg)
