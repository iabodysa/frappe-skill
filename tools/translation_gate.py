# Copyright (c) 2026, iabodysa

from __future__ import annotations

from pathlib import Path
from typing import Callable

import repo_guards


def require_lang(lang: str | None) -> str:
    named = (lang or "").strip()
    if not named:
        raise SystemExit(
            "No target language was named. Pass --lang <code>, for example --lang ar or "
            "--lang fr. The translation pipes carry no default language: the language "
            "belongs to whoever runs them, and guessing one scores the wrong CSV."
        )
    return named


def argv(package: str, lang: str, max_missing: int, max_stale: int,
         extra_roots: list[str] | None = None) -> list[str]:
    flags = [
        "--package", package,
        "--lang", require_lang(lang),
        "--max-missing", str(max_missing),
        "--max-stale", str(max_stale),
    ]
    for root in extra_roots or []:
        flags += ["--extra-root", root]
    return flags


def verdict(
    root: Path,
    package: str,
    lang: str,
    max_missing: int,
    max_stale: int,
    fallback: Callable[[], tuple[int, int]],
    extra_roots: list[str] | None = None,
) -> dict[str, object]:
    named = require_lang(lang)
    script = repo_guards.script(root, "check_translations.py")
    if script is not None:
        code, payload = repo_guards.capture(
            script,
            argv(package, named, max_missing, max_stale, extra_roots) + ["--json"],
            root,
        )
        return {
            "lang": named,
            "ok": bool(payload.get("passed")) and code == 0,
            "missing": payload.get("missing_count", -1),
            "stale": payload.get("stale_count", -1),
            "label_warnings": payload.get("label_warning_count", 0),
            "refused": bool(payload.get("refused")),
            "skipped": False,
            "delegated": True,
        }
    missing, stale = fallback()
    return {
        "lang": named,
        "ok": missing <= max_missing and stale <= max_stale,
        "missing": missing,
        "stale": stale,
        "label_warnings": 0,
        "refused": False,
        "skipped": False,
        "delegated": False,
    }
