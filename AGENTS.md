# AGENTS.md

## Overview

`pycons` is a small icon utility library. It downloads icon fonts (Font Awesome,
Material Design, Material Symbols, Codicons, Phosphor, Remix, Elusive) and resolves
icon names to Unicode characters plus the matching TTF file. It also wraps the
Iconify API / icon-set packages, builds favicon URLs for domains and maps file paths
to emoji "ASCII" icons. Python >= 3.14, HTTP via `anyenv`.

## Architecture

- `src/pycons/__init__.py`: public entry points `get_icon` (async) and `get_icon_sync`.
- `src/pycons/functional.py`: `get_icon("prefix.name")`, `get_icon_sync`, and
  `get_icon_from_iconify_id("mdi:home")`, which maps Iconify prefixes to font provider prefixes.
- `src/pycons/font_providers/`:
  - `base.py`: `FontProvider` ABC (`NAME`, `PREFIX`, `DISPLAY_NAME`, `get_latest_version`,
    `get_download_urls`, `process_mapping`).
  - `providers.py`: concrete providers plus the `PROVIDERS` dict (keyed by `NAME`).
    Font Awesome is pinned to 6.7.2 (7.x ships no TTFs).
  - `registry.py`: `FontRegistry` downloads TTF + mapping files into the user cache dir,
    writes a `name -> hex codepoint` JSON per font and returns `Icon` objects.
  - `models.py`: `FontInfo` and `Icon` dataclasses.
- `src/pycons/utils.py`: `fetch_url` (anyenv, cached 1 week, adds `GITHUB_TOKEN`/`GH_TOKEN`
  for GitHub URLs), `_CACHE_DIR` (appdirs `user_cache_dir("Pycons")`), CSS codepoint parser.
- `src/pycons/iconify/`: synchronous Iconify wrapper.
  - `api.py`: per-icon calls (`svg`, `css`, `icon_data`, `search`, `keywords`,
    `last_modified`, `iconify_version`) hit the Iconify API; collection-level calls
    (`collections`, `collection`, `icon_set`) load `@iconify/collections` /
    `@iconify-json/<prefix>` from npm CDNs (jsDelivr, then unpkg).
  - `errors.py`: `IconifyError`, `IconNotFoundError` (404), `IconifyRateLimitError` (429).
  - `iconify_types.py`: TypedDicts for API responses / IconifyJSON.
- `src/pycons/favicon.py`: `get_favicon(url, provider, size)` returns a favicon URL (no I/O).
- `src/pycons/asciicons.py`: `AsciiIcon` StrEnum, `EXTENSION_MAP`, `get_path_ascii_icon(path)`
  (uses `upath`, so remote paths work too).
- `src/pycons/log.py`: `get_logger`.

Control flow for font icons: `get_icon("fa.heart")` -> `FontRegistry.get_icon` -> find provider
by prefix -> `get_font` (download if missing) -> read mapping JSON -> `Icon(character, ttf_path, ...)`.

## Where to look

| Task | Location |
| --- | --- |
| Add / fix an icon font | `src/pycons/font_providers/providers.py` (+ register in `PROVIDERS`) |
| Iconify prefix mapping | `src/pycons/functional.py` (`get_icon_from_iconify_id`) |
| Download / cache behaviour | `src/pycons/font_providers/registry.py`, `src/pycons/utils.py` |
| Iconify API / CDN calls | `src/pycons/iconify/api.py` |
| File-type emoji | `src/pycons/asciicons.py` |
| Tests | `tests/test_icons.py`, `tests/test_iconify_api.py` |
| CI | `.github/workflows/build.yml`, `.github/workflows/documentation.yml` |

## Commands

```bash
uv sync --all-extras                 # setup (default groups: dev, lint, docs)
uv run pytest                        # tests (duty: `uv run duty test`)
uv run pytest -m "not network"       # offline subset
uv run ruff check . && uv run ruff format --check .
uv run ty check                      # type check (src only, warnings fail)
uv run deptry src                    # dependency check
uv run mkdocs-mknodes build          # docs (duty: `uv run duty build`, `serve`)
uv build
```

`duties.py` also has `update` (`uv lock --upgrade` + sync), `lint`, `lint_check`, `clean`
(`git clean -dfX`) and `version` (bumps version, commits, tags).
Pre-commit hooks (prek) run ruff, tombi, `ty check` and pytest on commit.

## Conventions

- Google-style docstrings without types in `Args` (see `.github/copilot-instructions.md`).
  Some Iconify functions still use NumPy-style sections.
- No `from __future__ import annotations` (PEP 649; banned via ruff TID251); typing-only imports under `TYPE_CHECKING`.
- ruff with preview rules, line length 100. ty is the type checker: use targeted
  `# ty: ignore[rule]`, not mypy-style ignores.
- Tests are plain functions (no classes); async tests run via `asyncio_mode = "auto"`.

## Pitfalls

- Copier-managed project (`.copier-answers.yml`, template `copier-phil65`). Don't hand-edit
  template-owned files (workflows, `duties.py`, `.pre-commit-config.yaml`, most of
  `pyproject.toml`); add dependencies below the `# Only add below (Copier)` markers.
- Most tests need network (font downloads from GitHub/CDNs, Iconify API/CDN) and are marked
  `@pytest.mark.network`. Set `GITHUB_TOKEN` to avoid GitHub API rate limits.
- Env vars: `PYCONS_ICONIFY_API` (API root), `PYCONS_ICONIFY_CDN` (comma-separated CDN roots),
  `GITHUB_TOKEN` / `GH_TOKEN`.
- Downloaded fonts are cached in the user cache dir and not re-downloaded; delete it to refresh.
- The public Iconify API is rate-limited; bulk data must come from the CDN path.
- Docs are the mkdocs-mknodes default site: `README.md` is the index page, API pages are
  generated; `docs/` is empty.
