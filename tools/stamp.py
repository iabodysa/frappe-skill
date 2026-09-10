# Copyright (c) 2026, iabodysa

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path

TIMESTAMP_SKIPPING_RECORDS = ("workspace", "notification", "number_card", "dashboard_chart")


def stamp_timestamp(now: datetime | None = None) -> str:
    base = now or datetime.now()
    return (base.replace(second=0, microsecond=0) + timedelta(minutes=1)).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )


def changed_record_json(root: Path) -> list[Path]:
    proc = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "-z", "-uall"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode:
        return []
    out: list[Path] = []
    for entry in proc.stdout.split("\0"):
        name = entry[3:] if len(entry) > 3 else ""
        if not name.endswith(".json"):
            continue
        path = root / name
        if path.is_file() and path.parent.parent.name in TIMESTAMP_SKIPPING_RECORDS:
            out.append(path)
    return sorted(out)


def _record_json_paths(root: Path) -> list[Path]:
    out: list[Path] = []
    for module_dir in root.glob("*"):
        if not module_dir.is_dir():
            continue
        for record_type in TIMESTAMP_SKIPPING_RECORDS:
            record_dir = module_dir / record_type
            if not record_dir.is_dir():
                continue
            for rec in record_dir.iterdir():
                jf = rec / f"{rec.name}.json"
                if jf.is_file():
                    out.append(jf)
    return sorted(out)


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False,
    )
    return proc.stdout if proc.returncode == 0 else ""


def _file_history(root: Path, relpath: Path) -> list[tuple[str, str]]:
    """oldest -> newest [(sha, isodate), ...] of commits touching relpath on HEAD."""
    log = _git(root, "log", "--reverse", "--format=%H\t%ad", "--date=short", "--", str(relpath))
    out: list[tuple[str, str]] = []
    for line in log.splitlines():
        if not line.strip():
            continue
        sha, date = line.split("\t")
        out.append((sha, date))
    return out


def _content_at(root: Path, sha: str, relpath: Path) -> tuple[dict, str | None] | None:
    text = _git(root, "show", f"{sha}:{relpath}")
    if not text:
        return None
    try:
        data = json.loads(text)
    except Exception:
        return None
    modified = data.pop("modified", None)
    return data, modified


def record_freshness(root: Path) -> dict[str, object]:
    """Whether each shipped Workspace/Notification/Number Card/Dashboard Chart record
    is behind its own source.

    A record is stale exactly when some commit changed its non-`modified` content
    without bumping `modified` in that same commit, and no later commit re-stamped
    it since. That is the only condition that leaves a target site's already-imported
    copy un-refreshed, because Frappe's fixture importer decides whether to reimport
    these four record types purely by comparing `modified` timestamps, never by
    diffing content (DocType JSON always reimports by content hash and is excluded).

    A record's first commit can never be flagged: there is no prior state to diff
    against, so a repository-wide history rewrite (a squashed baseline commit that
    republishes the whole tree at once) produces no false staleness here, unlike a
    measure based on "how long since the last commit touching this path."
    """
    toplevel = _git(root, "rev-parse", "--show-toplevel").strip()
    git_root = Path(toplevel) if toplevel else root

    stale: list[dict[str, str]] = []
    fresh: list[str] = []
    no_history: list[str] = []
    for jf in _record_json_paths(root):
        rel = jf.relative_to(root)  # cwd-relative, for `git log -- <path>`
        git_rel = jf.relative_to(git_root)  # repo-root-relative, for `git show sha:<path>`
        history = _file_history(root, rel)
        if not history:
            no_history.append(str(rel))
            continue
        prev_content: dict | None = None
        prev_modified: str | None = None
        violation: tuple[str, str] | None = None
        for sha, date in history:
            got = _content_at(root, sha, git_rel)
            if got is None:
                continue
            content, modified = got
            if prev_content is not None:
                if content != prev_content and modified == prev_modified:
                    violation = (sha, date)
                elif modified != prev_modified:
                    violation = None
            prev_content, prev_modified = content, modified
        if violation is None:
            fresh.append(str(rel))
        else:
            stale.append({
                "path": str(rel), "current_modified": prev_modified or "",
                "content_changed_at": violation[0], "date": violation[1],
            })
    return {
        "checked": len(fresh) + len(stale) + len(no_history),
        "fresh": len(fresh), "stale": stale, "no_history": no_history,
        "state": "STALE" if stale else "fresh",
    }


def run_stamp(paths: Iterable[Path | str]) -> dict[str, object]:
    stamped: list[str] = []
    failed: list[str] = []
    now = stamp_timestamp()
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            failed.append(str(path))
            continue
        content = path.read_text(encoding="utf-8")
        updated, count = re.subn(
            r'("modified":\s*")[^"]*(")',
            lambda match: match.group(1) + now + match.group(2),
            content,
            count=1,
        )
        if count:
            path.write_text(updated, encoding="utf-8")
            stamped.append(str(path))
        else:
            failed.append(str(path))
    return {"timestamp": now, "stamped": stamped, "failed": failed, "stamped_count": len(stamped)}
