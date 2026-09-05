# Copyright (c) 2026, iabodysa


from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

RELEASE_KINDS = ("urgent", "batched")
BATCHED_MIN_HOURS = 6

NO_KIND = (
    "Refusing to bump: say what kind of release this is.\n"
    "  --kind urgent --reason '<why now>'   a user-visible or security fix; ships alone, now\n"
    "  --kind batched                       everything else; waits for a chunk boundary\n"
    "A version the operator cannot account for teaches him the number means nothing."
)

NO_REASON = (
    "Refusing to bump: --kind urgent needs --reason '<what breaks without it>'.\n"
    "An urgent release skips the cadence gate, so the reason is the record of why."
)


def add_arguments(parser) -> None:
    parser.add_argument(
        "--kind",
        choices=RELEASE_KINDS,
        default="",
        help="urgent = a user-visible or security fix, ships now and alone; batched = everything else",
    )
    parser.add_argument(
        "--reason",
        default="",
        metavar="TEXT",
        help="Why an urgent release cannot wait (required with --kind urgent)",
    )


def release_timestamp(root: Path, ref: str) -> str:
    if not ref:
        return ""
    result = subprocess.run(
        ["git", "-C", str(root), "log", "-n", "1", "--format=%cI", ref],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def hours_since(iso: str, now: datetime | None = None) -> float | None:
    if not iso:
        return None
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return None
    reference = now or (datetime.now(then.tzinfo) if then.tzinfo else datetime.now())
    return (reference - then).total_seconds() / 3600.0


def refusal(root: Path, base: str, kind: str, reason: str, now: datetime | None = None) -> str:
    if kind not in RELEASE_KINDS:
        return NO_KIND
    if kind == "urgent":
        return "" if reason.strip() else NO_REASON
    stamp = release_timestamp(root, base)
    elapsed = hours_since(stamp, now)
    if elapsed is None or elapsed >= BATCHED_MIN_HOURS:
        return ""
    return (
        f"Refusing to bump: the previous release {base} was cut {elapsed:.1f} hours ago\n"
        f"({stamp}), and a batched release waits {BATCHED_MIN_HOURS} hours.\n"
        "Collect the work and bump once, or say --kind urgent --reason '<why now>' if a\n"
        "user-visible or security fix cannot wait."
    )

def last_release(root: Path) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "-C", str(root), "log", "-n", "1", "--format=%H %s", "--grep=^Release "],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return "", ""
    sha, _, subject = result.stdout.strip().partition(" ")
    return sha, subject.split("Release ", 1)[-1].strip()


def untagged_release(root: Path) -> str:
    sha, version = last_release(root)
    if not version:
        return ""
    tag = "v" + version
    found = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "-q", "--verify", "refs/tags/" + tag],
        capture_output=True,
        text=True,
        check=False,
    )
    if found.returncode == 0:
        return ""
    return (
        f"Refusing to bump: the last release ({version}, {sha[:8]}) has no {tag} tag.\n"
        "A release that is only a branch commit cannot be deployed by tag, and anyone\n"
        "pulling the latest release gets an older one without being told.\n"
        f"    git tag -a {tag} {sha[:8]} -m '{version}' && git push origin {tag}"
    )
