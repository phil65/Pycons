"""Exceptions raised by the Iconify wrappers."""


class IconifyError(Exception):
    """Base class for errors when fetching Iconify data."""

    def __init__(self, message: str, url: str) -> None:
        super().__init__(message)
        self.url = url


class IconNotFoundError(IconifyError):
    """Icon or icon set does not exist."""

    def __init__(self, url: str) -> None:
        super().__init__(f"Not found: {url}", url)


class IconifyRateLimitError(IconifyError):
    """Request was rejected by the rate limiter (HTTP 429).

    The public Iconify API is meant for loading icons on demand. Bulk data
    (whole icon sets) should come from the CDN or a self-hosted API instance.
    See https://iconify.design/docs/api/ ("Limits").
    """

    def __init__(self, url: str, retry_after: int | None) -> None:
        wait = f"retry after {retry_after}s" if retry_after is not None else "retry later"
        msg = (
            f"Rate limited by Iconify ({wait}): {url}. "
            "Use the CDN for bulk data or point PYCONS_ICONIFY_API to a self-hosted instance."
        )
        super().__init__(msg, url)
        self.retry_after = retry_after
