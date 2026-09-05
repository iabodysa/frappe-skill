# Copyright (c) 2026, iabodysa

from __future__ import annotations

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
