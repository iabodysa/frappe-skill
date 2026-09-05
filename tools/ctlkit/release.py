# Copyright (c) 2026, iabodysa

from __future__ import annotations

import re
import subprocess

import release_gate
from pathlib import Path

from ctlkit.changelog import validate_version
from ctlkit.config import discover_config

BOOKKEEPING_NAMES: set[str] = {"pyproject.toml", "setup.py", "__init__.py", "changelog.py"}
BOOKKEEPING_DIRS: set[str] = {"change_log"}

def _git_lines(root: Path, *args: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def replace_once(path: Path, pattern: str, replacement: str) -> bool:
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
    if count:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def previous_release_ref(root: Path) -> str:
    tags = _git_lines(root, "describe", "--tags", "--abbrev=0")
    commits = _git_lines(root, "log", "--grep=^Release [0-9]", "-n", "1", "--format=%H")
    tag = tags[0] if tags else ""
    commit = commits[0] if commits else ""
    if not tag or not commit:
        return tag or commit
    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", tag, commit],
        capture_output=True,
        text=True,
        check=False,
    )
    return commit if ancestor.returncode == 0 else tag


def _is_bookkeeping(path: str) -> bool:
    parts = Path(path).parts
    if set(parts) & BOOKKEEPING_DIRS:
        return True
    return Path(path).name in BOOKKEEPING_NAMES


def release_range(root: Path) -> dict[str, object]:
    base = previous_release_ref(root)
    if not base:
        return {"resolved": False, "base": "", "commits": [], "files": [], "content_files": []}
    commits = _git_lines(root, "log", "--format=%h %s", f"{base}..HEAD")
    files = _git_lines(root, "diff", "--name-only", f"{base}..HEAD")
    return {
        "resolved": True,
        "base": base,
        "commits": commits,
        "files": files,
        "content_files": [f for f in files if not _is_bookkeeping(f)],
    }


def run_bump(
    root: Path | str | None = None,
    version: str = "",
    allow_bookkeeping: str = "",
    kind: str = "",
    reason: str = "",
) -> dict[str, object]:
    validate_version(version)
    config = discover_config(root)
    release = release_range(config.root)
    unearned = minor_refusal(config.root, version, release, allow_bookkeeping)
    if unearned:
        raise SystemExit(unearned)
    denial = release_gate.refusal(config.root, str(release.get('base') or ''), kind, reason)
    if denial:
        raise SystemExit(denial)
    untagged = release_gate.untagged_release(config.root)
    if untagged:
        raise SystemExit(untagged)
    if release["resolved"] and not release["content_files"] and not allow_bookkeeping:
        counted = "\n".join("  " + line for line in release["commits"]) or "  (none)"
        raise SystemExit(
            "Refusing to bump: nothing outside the version files and the changelog has\n"
            f"landed since {release['base']}. A version is one deliverable the operator can\n"
            "name — collect the work and bump once.\n"
            f"Commits counted since {release['base']}:\n{counted}\n"
            "Pass --allow-bookkeeping '<reason>' to release anyway."
        )
    candidates = [
        (
            config.package_path / "__init__.py",
            r'__version__\s*=\s*"[0-9][0-9.]*"',
            f'__version__ = "{version}"',
        ),
        (
            config.root / "pyproject.toml",
            r'^version\s*=\s*"[0-9][0-9.]*"',
            f'version = "{version}"',
        ),
        (
            config.root / "setup.py",
            r'version="[0-9][0-9.]*"',
            f'version="{version}"',
        ),
    ]
    updated: list[str] = []
    missing: list[str] = []
    for path, pattern, replacement in candidates:
        if replace_once(path, pattern, replacement):
            updated.append(str(path))
        else:
            missing.append(str(path))
    if not updated:
        raise SystemExit("No version declarations updated.")
    return {
        "app": config.app,
        "version": version,
        "updated": updated,
        "missing": missing,
        "release_base": release["base"],
        "content_commits": len(release["commits"]),
        "content_files": len(release["content_files"]),
        "bookkeeping_override": allow_bookkeeping,
        "kind": kind,
        "kind_reason": reason,
        "previous_release_at": release_gate.release_timestamp(config.root, str(release.get("base") or "")),
    }


MINOR_SURFACE_FLOOR = 5
MINOR_RELEASE_FLOOR = 10

BREAKING_FILES: set[str] = {".ctl.toml"}
NEW_SURFACE_PARTS: set[str] = {
    "workspace", "number_card", "dashboard", "report", "web_form", "print_format"
}


def _classify_files(paths: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {"docs_i18n": 0, "new_surface": 0, "behavior": 0, "breaking": 0,
                              "new_module": 0}
    for p in paths:
        path = Path(p)
        if path.name == "modules.txt":
            counts["new_module"] += 1
        elif path.name in BREAKING_FILES:
            counts["breaking"] += 1
        elif any(part in NEW_SURFACE_PARTS for part in path.parts) and path.suffix == ".json":
            counts["new_surface"] += 1
        elif path.suffix in {".md", ".txt"} or "translations" in path.parts or "change_log" in path.parts:
            counts["docs_i18n"] += 1
        elif path.suffix == ".py":
            counts["behavior"] += 1
        elif path.suffix == ".json" and "doctype" in path.parts:
            counts["behavior"] += 1
        else:
            counts["docs_i18n"] += 1
    return counts


def releases_since_minor(root: Path) -> int:
    notes = sorted(root.glob("*/change_log/v*/v*_*_*.md"))
    versions = []
    for note in notes:
        parts = note.stem.lstrip("v").split("_")
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            versions.append(tuple(int(part) for part in parts))
    if not versions:
        return 0
    versions.sort()
    newest_minor = max((major, minor) for major, minor, _ in versions)
    return sum(1 for major, minor, _ in versions if (major, minor) == newest_minor)


def minor_refusal(root: Path, version: str, release: dict, override: str = "") -> str:
    if override:
        return ""
    current = _read_current_version(root)
    try:
        was = tuple(int(part) for part in current.split(".")[:3])
        now = tuple(int(part) for part in version.split(".")[:3])
    except ValueError:
        return ""
    if now[0] != was[0] or now[1] <= was[1]:
        return ""
    classification = _classify_files(list(release.get("content_files") or []))
    if classification.get("new_module"):
        return ""
    since_minor = releases_since_minor(root)
    surface = classification["new_surface"]
    if surface >= MINOR_SURFACE_FLOOR and since_minor >= MINOR_RELEASE_FLOOR:
        return ""
    short = []
    if surface < MINOR_SURFACE_FLOOR:
        short.append(f"{surface} new surface file(s), floor is {MINOR_SURFACE_FLOOR}")
    if since_minor < MINOR_RELEASE_FLOOR:
        short.append(f"{since_minor} release(s) since the last minor, floor is {MINOR_RELEASE_FLOOR}")
    return (
        f"Refusing to bump {current} to {version}: the middle digit is a milestone, and this\n"
        f"wave has not earned one — {'; '.join(short)}.\n"
        "A new module clears it at any size. Otherwise collect the work and take a patch.\n"
        "Pass --allow-bookkeeping '<reason>' to release anyway."
    )


def _decide_bump(classification: dict[str, int], since_minor: int = 0) -> tuple[str, str]:
    if classification["breaking"] > 0:
        return "major", "breaking changes detected — confirm with owner"
    if classification.get("new_module"):
        return "minor", "modules.txt changed — a whole new module is a milestone at any size"
    surface = classification["new_surface"]
    if surface >= MINOR_SURFACE_FLOOR and since_minor >= MINOR_RELEASE_FLOOR:
        return "minor", (f"{surface} new surface files and {since_minor} releases since the last "
                         f"minor — both floors cleared")
    if surface:
        short = []
        if surface < MINOR_SURFACE_FLOOR:
            short.append(f"{surface} new surface file(s), floor is {MINOR_SURFACE_FLOOR}")
        if since_minor < MINOR_RELEASE_FLOOR:
            short.append(f"{since_minor} release(s) since the last minor, floor is "
                         f"{MINOR_RELEASE_FLOOR}")
        return "patch", ("new surface fitting the existing model — " + "; ".join(short))
    if classification["behavior"] > 0:
        return "patch", "controller or schema behavior changes"
    return "patch", "docs and i18n only"


def _increment_version(version: str, bump_type: str) -> str:
    major, minor, patch = validate_version(version)
    if bump_type == "major":
        return f"{major + 1}.0.0"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def _read_current_version(root: Path) -> str:
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"([0-9][0-9.]*)"', content, re.MULTILINE)
        if match:
            return match.group(1)
    init_candidates = list(root.glob("*/*/  __init__.py")) + list(root.glob("*/__init__.py"))
    for init in init_candidates:
        content = init.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*"([0-9][0-9.]*)"', content)
        if match:
            return match.group(1)
    raise SystemExit("Cannot determine current version from pyproject.toml or __init__.py")


def run_bump_smart(
    root: Path | str | None = None,
    base: str = "HEAD",
    apply: bool = False,
    as_json: bool = False,
    kind: str = "",
    reason: str = "",
) -> dict[str, object]:
    config = discover_config(root)
    repo = config.app_path

    result = subprocess.run(
        ["git", "diff", "--name-only", base],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--name-only", base],
            cwd=str(config.root),
            capture_output=True,
            text=True,
        )
    changed_files = [line for line in result.stdout.strip().splitlines() if line.strip()]

    classification = _classify_files(changed_files)
    since_minor = releases_since_minor(config.root)
    bump_type, reason = _decide_bump(classification, since_minor)

    current_version = _read_current_version(config.root)
    proposed_version = _increment_version(current_version, bump_type)

    applied = False
    if apply:
        run_bump(config.root, proposed_version, kind=kind, reason=reason)
        applied = True

    return {
        "current_version": current_version,
        "proposed_version": proposed_version,
        "bump_type": bump_type,
        "reason": reason,
        "changed_files": len(changed_files),
        "classification": classification,
        "releases_since_minor": since_minor,
        "applied": applied,
    }


from stamp import changed_record_json, run_stamp, stamp_timestamp
