# Copyright (c) 2026, iabodysa

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from ctlkit.config import ChangelogResult, ProjectConfig, discover_config

def validate_version(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        raise SystemExit(f"Invalid version, expected X.Y.Z: {version}")
    return tuple(int(part) for part in match.groups())


def app_title(app: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[_\-\s]+", app) if part)


def changelog_filename(version: str) -> tuple[str, str]:
    major, minor, patch = validate_version(version)
    return f"v{major}", f"v{major}_{minor}_{patch}.md"


def render_changelog(title: str, version: str, summary: str, bullets: list[str],
                     released_at: str = "") -> str:
    cleaned_bullets = [bullet.strip() for bullet in bullets if bullet.strip()]
    lines = [
        *([f"<!-- released: {released_at} -->"] if released_at else []),
        f"# {title} {version}",
        "",
        summary.strip(),
        "",
        *[f"- {bullet}" for bullet in cleaned_bullets],
        "",
    ]
    return "\n".join(lines)


def update_changelog_index(index_file: Path, version: str, rel_path: str) -> bool:
    index_file.parent.mkdir(parents=True, exist_ok=True)
    entry = f"- [{version}]({rel_path})"
    if index_file.exists():
        existing = index_file.read_text(encoding="utf-8")
    else:
        existing = "# Change Log\n\n## Latest\n\n"
    if entry in existing:
        return False
    lines = existing.splitlines()
    try:
        latest_idx = lines.index("## Latest")
        insert_at = latest_idx + 1
        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
        lines.insert(insert_at, entry)
        content = "\n".join(lines).rstrip() + "\n"
    except ValueError:
        content = "# Change Log\n\n## Latest\n\n" + entry + "\n\n" + existing.rstrip() + "\n"
    index_file.write_text(content, encoding="utf-8")
    return True


def find_release_feed(config: "ProjectConfig") -> Path | None:
    for path in sorted(config.package_path.rglob("changelog.py")):
        if "_RELEASES = [" in path.read_text(encoding="utf-8"):
            return path
    return None


def update_release_feed(feed_file: Path, version: str, title: str, app: str) -> bool:
    existing = feed_file.read_text(encoding="utf-8")
    if f"{title.split()[0] if title else ''} {version} " in existing or f" {version} —" in existing:
        return False
    marker = "_RELEASES = [\n"
    if marker not in existing:
        return False
    entry = (
        "    {\n"
        f'        "title": "{title}",\n'
        f'        "app_name": "{app}",\n'
        '        "link": "/app",\n'
        f'        "creation": "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",\n'
        "    },\n"
    )
    feed_file.write_text(existing.replace(marker, marker + entry, 1), encoding="utf-8")
    return True


VAGUE_HEADLINES: tuple[str, ...] = (
    "documentation update",
    "docs update",
    "documentation updates",
    "internal improvements",
    "internal safeguards",
    "various fixes",
    "minor fixes",
    "bug fixes",
    "maintenance release",
    "housekeeping",
    "chore",
    "misc",
)


def headline_is_checkable(summary: str) -> bool:
    cleaned = summary.strip().rstrip(".").strip().lower()
    if not cleaned:
        return False
    if cleaned in VAGUE_HEADLINES:
        return False
    return len(cleaned.split()) >= 4


def run_changelog(
    root: Path | str | None = None,
    version: str = "",
    summary: str | None = None,
    bullets: list[str] | None = None,
    title: str | None = None,
    draft: bool = False,
) -> ChangelogResult:
    config = discover_config(root)
    series_dir, file_name = changelog_filename(version)
    cleaned_bullets = [bullet.strip() for bullet in (bullets or []) if bullet.strip()]
    if not summary and not draft:
        raise SystemExit("Changelog requires --summary unless --draft is set.")
    if summary and not draft and not headline_is_checkable(summary):
        raise SystemExit(
            f"Refusing this headline: {summary!r} names nothing the operator can check.\n"
            "Say what changed and where — 'Documentation update.' is the recorded example\n"
            "of a headline that fails; 'The upgrade runbook states the cutover is deferred'\n"
            "is one that passes."
        )
    if draft:
        summary = summary or "Write a concise operator-facing summary for this release."

    change_log_dir = config.package_path / "change_log"
    output_file = change_log_dir / series_dir / file_name
    index_file = change_log_dir / "README.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    was_existing = output_file.exists()
    output_file.write_text(
        render_changelog(
            title or app_title(config.app),
            version,
            summary or "",
            cleaned_bullets,
            released_at="" if draft else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
        encoding="utf-8",
    )
    index_updated = update_changelog_index(index_file, version, f"{series_dir}/{file_name}")
    feed_file = find_release_feed(config)
    feed_updated = False
    if feed_file and not draft:
        feed_title = f"{title or app_title(config.app)} {version} — {summary or ''}".rstrip(" —")
        feed_updated = update_release_feed(feed_file, version, feed_title, config.app)
    return ChangelogResult(
        config=config,
        version=version,
        file=output_file,
        index_file=index_file,
        created=not was_existing,
        index_updated=index_updated,
        feed_file=feed_file,
        feed_updated=feed_updated,
    )
