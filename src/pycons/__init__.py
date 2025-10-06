"""Pycons: main package.

Icon utilities (Material Design icons & similar).
"""

from __future__ import annotations

from importlib.metadata import version

__version__ = version("pycons")
__title__ = "Pycons"

__author__ = "Philipp Temminghoff"
__author_email__ = "philipptemminghoff@googlemail.com"
__copyright__ = "Copyright (c) 2025 Philipp Temminghoff"
__license__ = "MIT"
__url__ = "https://github.com/phil65/pycons"

from pycons.functional import get_icon_sync, get_icon

__all__ = [
    "__version__",
    "get_icon",
    "get_icon_sync",
]
