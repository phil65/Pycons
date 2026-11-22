# Pycons

[![PyPI License](https://img.shields.io/pypi/l/pycons.svg)](https://pypi.org/project/pycons/)
[![Package status](https://img.shields.io/pypi/status/pycons.svg)](https://pypi.org/project/pycons/)
[![Monthly downloads](https://img.shields.io/pypi/dm/pycons.svg)](https://pypi.org/project/pycons/)
[![Distribution format](https://img.shields.io/pypi/format/pycons.svg)](https://pypi.org/project/pycons/)
[![Wheel availability](https://img.shields.io/pypi/wheel/pycons.svg)](https://pypi.org/project/pycons/)
[![Python version](https://img.shields.io/pypi/pyversions/pycons.svg)](https://pypi.org/project/pycons/)
[![Implementation](https://img.shields.io/pypi/implementation/pycons.svg)](https://pypi.org/project/pycons/)
[![Releases](https://img.shields.io/github/downloads/phil65/Pycons/total.svg)](https://github.com/phil65/Pycons/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/Pycons)](https://github.com/phil65/Pycons/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/Pycons)](https://github.com/phil65/Pycons/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/Pycons)](https://github.com/phil65/Pycons/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/Pycons)](https://github.com/phil65/Pycons/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/Pycons)](https://github.com/phil65/Pycons/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/Pycons)](https://github.com/phil65/Pycons/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/Pycons)](https://github.com/phil65/Pycons/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/Pycons)](https://github.com/phil65/Pycons)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/Pycons)](https://github.com/phil65/Pycons/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/Pycons)](https://github.com/phil65/Pycons/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/Pycons)](https://github.com/phil65/Pycons)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/Pycons)](https://github.com/phil65/Pycons)
[![Package status](https://codecov.io/gh/phil65/Pycons/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/Pycons/)
[![PyUp](https://pyup.io/repos/github/phil65/Pycons/shield.svg)](https://pyup.io/repos/github/phil65/Pycons/)

[Read the documentation!](https://phil65.github.io/Pycons/)

Icon utilities for Python: resolve icon names from popular icon fonts to Unicode characters
and font files, fetch SVGs and icon sets from [Iconify](https://iconify.design), build favicon
URLs and pick emoji icons for file paths.

## Installation

```bash
pip install pycons
```

Requires Python 3.13+.

## Quickstart

### Icon fonts

Icons are addressed as `prefix.name`. The font and its codepoint mapping are downloaded on
first use and cached in the user cache directory.

```python
import asyncio

from pycons import get_icon, get_icon_sync

icon = get_icon_sync("fa.heart")
print(icon.character, icon.ttf_path)  # Unicode character + path to the TTF file

icon = asyncio.run(get_icon("mdi.home"))
```

Iconify-style identifiers are supported for the bundled fonts as well:

```python
import asyncio

from pycons.functional import get_icon_from_iconify_id

icon = asyncio.run(get_icon_from_iconify_id("material-symbols:home-rounded"))
```

| Prefix | Font | Iconify prefix |
| --- | --- | --- |
| `fa` / `fas` / `fab` | Font Awesome 6 Regular / Solid / Brands | `fa6-regular` / `fa6-solid` / `fa6-brands` |
| `mdi` | Community Material Design Icons | `mdi` |
| `mso` / `msr` / `mss` | Google Material Symbols Outlined / Rounded / Sharp | `material-symbols` (`-outline`, `-rounded`, `-sharp` suffix) |
| `msc` | VS Code Codicons | `codicon` |
| `ph` | Phosphor | `ph` |
| `ri` | Remix Icon | `ri` |
| `el` | Elusive Icons | `el` |

### Iconify

`pycons.iconify.api` wraps the [Iconify API](https://iconify.design/docs/api/) for per-icon
requests and loads whole icon sets from the `@iconify-json/*` npm packages via CDN
(jsDelivr, falling back to unpkg), since the public API is rate-limited for bulk use.

```python
from pycons.iconify import api

svg = api.svg("mdi:home", color="red", height=24)  # bytes
result = api.search("arrow", limit=32)
mdi = api.icon_set("mdi")  # full IconifyJSON data
sets = api.collections("mdi", "fa6-")  # metadata of matching icon sets
```

Errors are raised as `IconNotFoundError`, `IconifyRateLimitError` or `IconifyError`
(`pycons.iconify.errors`). The endpoints can be overridden with the `PYCONS_ICONIFY_API` and
`PYCONS_ICONIFY_CDN` (comma-separated) environment variables.

### Favicons and file icons

```python
from pycons.asciicons import get_path_ascii_icon
from pycons.favicon import get_favicon

get_favicon("https://github.com", provider="google", size=64)  # favicon URL
get_path_ascii_icon("script.py")  # "🐍"
```

## Features

- 11 icon fonts behind one `prefix.name` lookup, with async and sync APIs
- Cached downloads; set `GITHUB_TOKEN` to avoid GitHub rate limits when fetching fonts
- Typed Iconify wrapper: SVG, CSS, search, keywords, icon data and full icon sets
- Favicon URL builder for Google, DuckDuckGo, Icon Horse, Yandex, favicon.io and favicon.ninja
- Emoji icons for files and folders by extension (works with `upath` paths)

## Documentation

See the [documentation](https://phil65.github.io/Pycons/) for the API reference.
