"""Ascii icons for different file types."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Final


if TYPE_CHECKING:
    import os


class AsciiIcon(StrEnum):
    """ASCII icons for different file types."""

    # Default icons
    FOLDER = "📁"
    FILE = "📄"
    HIDDEN = "🔒"
    SYMLINK = "🔗"

    # Documents
    PDF = "📕"
    DOC = "📘"
    TXT = "📝"
    PRESENTATION = "📊"
    SPREADSHEET = "📈"
    EBOOK = "📚"

    # Code
    PYTHON = "🐍"
    JAVA = "☕"
    JS = "📜"
    HTML = "🌐"
    CSS = "🎨"
    CPP = "⚡"
    RUST = "🦀"
    GO = "🐹"
    RUBY = "💎"
    PHP = "🐘"
    SWIFT = "🎯"
    KOTLIN = "🎳"

    # Config & Data
    JSON = "📊"
    CSV = "📑"
    XML = "📐"
    YAML = "⚙️"
    INI = "🔧"
    ENV = "🔐"
    SQL = "🗄️"
    TOML = "⚡"

    # Media
    IMAGE = "🖼️"
    VIDEO = "🎥"
    AUDIO = "🎵"
    FONT = "🔤"
    MODEL_3D = "💠"

    # Design
    PSD = "🎨"
    AI = "🖌️"
    SKETCH = "✏️"
    FIGMA = "🎯"

    # Archives
    ARCHIVE = "📦"
    BACKUP = "💾"

    # Executables & Binaries
    EXECUTABLE = "⚙️"
    DLL = "🔌"
    BINARY = "👾"

    # Development
    GIT = "🌿"
    DOCKERFILE = "🐋"
    LOG = "📋"
    TEST = "🧪"

    # Special
    TEMP = "⌛"
    TRASH = "🗑️"
    LOCK = "🔒"


EXTENSION_MAP: Final[dict[str, AsciiIcon]] = {
    # Documents
    ".pdf": AsciiIcon.PDF,
    ".doc": AsciiIcon.DOC,
    ".docx": AsciiIcon.DOC,
    ".txt": AsciiIcon.TXT,
    ".md": AsciiIcon.TXT,
    ".rst": AsciiIcon.TXT,
    ".rtf": AsciiIcon.TXT,
    ".ppt": AsciiIcon.PRESENTATION,
    ".pptx": AsciiIcon.PRESENTATION,
    ".xls": AsciiIcon.SPREADSHEET,
    ".xlsx": AsciiIcon.SPREADSHEET,
    ".csv": AsciiIcon.CSV,
    ".epub": AsciiIcon.EBOOK,
    ".mobi": AsciiIcon.EBOOK,
    # Code
    ".py": AsciiIcon.PYTHON,
    ".pyi": AsciiIcon.PYTHON,
    ".ipynb": AsciiIcon.PYTHON,
    ".java": AsciiIcon.JAVA,
    ".class": AsciiIcon.JAVA,
    ".jar": AsciiIcon.JAVA,
    ".js": AsciiIcon.JS,
    ".jsx": AsciiIcon.JS,
    ".ts": AsciiIcon.JS,
    ".tsx": AsciiIcon.JS,
    ".html": AsciiIcon.HTML,
    ".htm": AsciiIcon.HTML,
    ".css": AsciiIcon.CSS,
    ".scss": AsciiIcon.CSS,
    ".sass": AsciiIcon.CSS,
    ".less": AsciiIcon.CSS,
    ".cpp": AsciiIcon.CPP,
    ".cc": AsciiIcon.CPP,
    ".c": AsciiIcon.CPP,
    ".hpp": AsciiIcon.CPP,
    ".h": AsciiIcon.CPP,
    ".rs": AsciiIcon.RUST,
    ".go": AsciiIcon.GO,
    ".rb": AsciiIcon.RUBY,
    ".php": AsciiIcon.PHP,
    ".swift": AsciiIcon.SWIFT,
    ".kt": AsciiIcon.KOTLIN,
    # Config & Data
    ".json": AsciiIcon.JSON,
    ".xml": AsciiIcon.XML,
    ".yaml": AsciiIcon.YAML,
    ".yml": AsciiIcon.YAML,
    ".ini": AsciiIcon.INI,
    ".env": AsciiIcon.ENV,
    ".sql": AsciiIcon.SQL,
    ".toml": AsciiIcon.TOML,
    ".db": AsciiIcon.SQL,
    ".sqlite": AsciiIcon.SQL,
    # Media
    ".jpg": AsciiIcon.IMAGE,
    ".jpeg": AsciiIcon.IMAGE,
    ".png": AsciiIcon.IMAGE,
    ".gif": AsciiIcon.IMAGE,
    ".svg": AsciiIcon.IMAGE,
    ".webp": AsciiIcon.IMAGE,
    ".ico": AsciiIcon.IMAGE,
    ".mp4": AsciiIcon.VIDEO,
    ".avi": AsciiIcon.VIDEO,
    ".mov": AsciiIcon.VIDEO,
    ".mkv": AsciiIcon.VIDEO,
    ".webm": AsciiIcon.VIDEO,
    ".mp3": AsciiIcon.AUDIO,
    ".wav": AsciiIcon.AUDIO,
    ".flac": AsciiIcon.AUDIO,
    ".m4a": AsciiIcon.AUDIO,
    ".ogg": AsciiIcon.AUDIO,
    ".ttf": AsciiIcon.FONT,
    ".otf": AsciiIcon.FONT,
    ".woff": AsciiIcon.FONT,
    ".woff2": AsciiIcon.FONT,
    ".obj": AsciiIcon.MODEL_3D,
    ".fbx": AsciiIcon.MODEL_3D,
    ".blend": AsciiIcon.MODEL_3D,
    # Design
    ".psd": AsciiIcon.PSD,
    ".ai": AsciiIcon.AI,
    ".sketch": AsciiIcon.SKETCH,
    ".fig": AsciiIcon.FIGMA,
    # Archives
    ".zip": AsciiIcon.ARCHIVE,
    ".tar": AsciiIcon.ARCHIVE,
    ".gz": AsciiIcon.ARCHIVE,
    ".7z": AsciiIcon.ARCHIVE,
    ".rar": AsciiIcon.ARCHIVE,
    ".bak": AsciiIcon.BACKUP,
    # Executables & Binaries
    ".exe": AsciiIcon.EXECUTABLE,
    ".msi": AsciiIcon.EXECUTABLE,
    ".app": AsciiIcon.EXECUTABLE,
    ".sh": AsciiIcon.EXECUTABLE,
    ".dll": AsciiIcon.DLL,
    ".so": AsciiIcon.DLL,
    ".dylib": AsciiIcon.DLL,
    ".bin": AsciiIcon.BINARY,
    # Development
    ".git": AsciiIcon.GIT,
    ".gitignore": AsciiIcon.GIT,
    ".dockerfile": AsciiIcon.DOCKERFILE,
    ".log": AsciiIcon.LOG,
    ".test": AsciiIcon.TEST,
    ".spec": AsciiIcon.TEST,
    # Temporary
    ".tmp": AsciiIcon.TEMP,
    ".temp": AsciiIcon.TEMP,
    ".swp": AsciiIcon.TEMP,
    ".lock": AsciiIcon.LOCK,
}


def get_path_ascii_icon(path: str | os.PathLike[str]) -> str:
    """Get an ASCII icon for a given file path based on its type.

    Args:
        path: File path as string or Path object

    Returns:
        ASCII icon representing the file type
    """
    import upath

    path_obj = upath.UPath(path)

    # Handle symbolic links
    if path_obj.is_symlink():
        return AsciiIcon.SYMLINK

    # Handle folders
    if path_obj.is_dir():
        return AsciiIcon.FOLDER

    # Handle hidden files (Unix-style)
    if path_obj.name.startswith("."):
        return AsciiIcon.HIDDEN

    # Get extension and return corresponding icon or default
    extension = path_obj.suffix.lower()
    name_lower = path_obj.name.lower()

    # Check full filename for special cases
    if name_lower in EXTENSION_MAP:
        return EXTENSION_MAP[name_lower]

    return EXTENSION_MAP.get(extension, AsciiIcon.FILE)
