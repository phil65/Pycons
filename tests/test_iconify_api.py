from __future__ import annotations

import email.utils
import time
from typing import Any

import anyenv
import pytest

from pycons.iconify import api
from pycons.iconify.errors import IconifyError, IconifyRateLimitError, IconNotFoundError


class FakeResponse:
    def __init__(self, status_code: int, headers: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self.headers = headers or {}


def _raise_status(status_code: int, headers: dict[str, str] | None = None) -> Any:
    def fail(*args: Any, **kwargs: Any) -> Any:
        response: Any = FakeResponse(status_code, headers)
        msg = f"HTTP Error {status_code}"
        raise anyenv.ResponseError(msg, response)

    return fail


def test_rate_limit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(anyenv, "get_bytes_sync", _raise_status(429, {"Retry-After": "42"}))
    with pytest.raises(IconifyRateLimitError) as exc_info:
        api.svg("mdi:file")
    assert exc_info.value.retry_after == 42  # noqa: PLR2004
    assert exc_info.value.url == f"{api.DEFAULT_API_ROOT}/mdi/file.svg"


def test_not_found_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(anyenv, "get_bytes_sync", _raise_status(404))
    with pytest.raises(IconNotFoundError):
        api.svg("mdi:file")


def test_other_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(anyenv, "get_text_sync", _raise_status(500))
    with pytest.raises(IconifyError, match="HTTP 500"):
        api.iconify_version()


def test_retry_after_parsing() -> None:
    assert api._retry_after({"retry-after": "10"}) == 10  # noqa: PLR2004
    assert api._retry_after({}) is None
    assert api._retry_after({"retry-after": "garbage"}) is None
    date = email.utils.formatdate(time.time() + 120, usegmt=True)
    assert 100 < (api._retry_after({"Retry-After": date}) or 0) <= 120  # noqa: PLR2004


def test_roots_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(api.API_ROOT_ENV, "https://icons.example.com/")
    monkeypatch.setenv(api.CDN_ROOT_ENV, "https://a.example.com/, https://b.example.com")
    assert api.api_root() == "https://icons.example.com"
    assert api.cdn_roots() == ["https://a.example.com", "https://b.example.com"]
    monkeypatch.delenv(api.CDN_ROOT_ENV)
    assert api.cdn_roots() == list(api.DEFAULT_CDN_ROOTS)


@pytest.mark.network
def test_collections() -> None:
    assert len(api.collections()) > 100  # noqa: PLR2004
    assert set(api.collections("mdi", "fa6-")) == {"mdi", "fa6-solid", "fa6-regular", "fa6-brands"}


@pytest.mark.network
def test_collection() -> None:
    result = api.collection("mdi", info=True)
    assert result["prefix"] == "mdi"
    assert result["title"] == "Material Design Icons"
    assert result["info"]["name"] == "Material Design Icons"
    assert "file" in {name for names in result["categories"].values() for name in names}
    assert result["aliases"]
    assert result["total"] == len(
        set(result.get("uncategorized", [])).union(*result["categories"].values())
    )


@pytest.mark.network
def test_collection_not_found() -> None:
    with pytest.raises(IconNotFoundError):
        api.collection("this-set-does-not-exist")


@pytest.mark.network
def test_icon_set() -> None:
    data = api.icon_set("fa-brands")
    assert data["prefix"] == "fa-brands"
    assert "github" in data["icons"]
