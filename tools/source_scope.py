# Copyright (c) 2026, iabodysa

from __future__ import annotations

from pathlib import Path

SKIP_DIRS: frozenset[str] = frozenset({
    ".git",
    ".venv",
    ".ctl",
    ".claude",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "public",
    "translations",
    "locale",
    "upstream",
    "_work",
})


def is_source_path(path: Path | str, skip: frozenset[str] | None = None) -> bool:
    parts = Path(path).parts
    return not (set(parts) & (skip or SKIP_DIRS))


def iter_source_files(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and (suffixes is None or path.suffix.lower() in suffixes)
        and is_source_path(path.relative_to(root))
    )
