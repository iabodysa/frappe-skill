#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa


from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _suite_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "SKILL.md").is_file():
            return candidate
    raise SystemExit(
        f"publish: no SKILL.md above {start}, so the tree to publish is unknown and the "
        "remote would be filled with the wrong files."
    )


SUITE_ROOT = _suite_root(Path(__file__).resolve().parent)

DEFAULT_REMOTE = "https://github.com/iabodysa/frappe-skill"
DEFAULT_BRANCH = "main"

OK, FAILED, REFUSED = 0, 1, 2

# The scanner carries the digest of the owner's address, never the address, so the tool is not
# itself the leak it looks for.
SECRET_EMAIL_DIGESTS = ("a7e11fa4dd1eac71883b8cd4014b0af8e1cb0092153166d71e88c4c2782d247a",)

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
KEY = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")
CREDENTIAL = re.compile(
    r"(?i)(?:pass(?:word|wd)|secret|api[_-]?key|access[_-]?key|auth[_-]?token)\s*[:=]\s*"
    r"[\"']([^\"'\n]{4,})[\"']"
)

# Two lines in tools/benchx.py read as a credential and are not: the f-strings that WRITE a site
# config, whose quoted text is a placeholder the operator supplied. Held by the digest of each exact
# line — the tool carries no credential text of its own, a line is spared rather than a whole
# file, and a real secret on the next line is still caught.
WHITELIST_DIGESTS = (
    "fc6af3546da792d77f0329a512ae7640a15cf73e5428b6fde220568928bcad51",
    "820b2ae14dd13767f6a5775a1272ce7ab3f6db384556b7debde429f8acfa1328",
)

BINARY = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".woff", ".woff2", ".zip", ".whl"}


def git(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *argv], capture_output=True, text=True,
                          check=False)


def repo_of(source: Path) -> tuple[Path, str]:
    """The git root above the tree to publish, and that tree's path inside it."""
    found = git(source, "rev-parse", "--show-toplevel")
    if found.returncode != 0:
        raise SystemExit(f"publish: {source} is not inside a git repository.")
    root = Path(found.stdout.strip()).resolve()
    prefix = source.resolve().relative_to(root).as_posix()
    return root, prefix


def tracked(root: Path, prefix: str) -> list[str]:
    """Every file git tracks under the prefix, named as the remote will name it."""
    listed = git(root, "ls-files", "-z", "--", prefix).stdout.split("\0")
    return sorted(p[len(prefix) + 1:] for p in listed if p)


def untracked(root: Path, prefix: str) -> list[str]:
    listed = git(root, "ls-files", "-z", "--others", "--exclude-standard", "--", prefix)
    return sorted(p for p in listed.stdout.split("\0") if p)


def modified(root: Path, prefix: str) -> list[str]:
    listed = git(root, "status", "--porcelain", "-z", "--", prefix).stdout.split("\0")
    return sorted(entry[3:] for entry in listed if entry and not entry.startswith("??"))


def ignored(root: Path, prefix: str, files: list[str]) -> list[str]:
    """A tracked file can still match an ignore rule; publishing one leaks what was excluded."""
    if not files:
        return []
    asked = "\0".join(f"{prefix}/{name}" for name in files)
    # --no-index, because check-ignore reports nothing for a tracked file without it, and a
    # force-added file is exactly the one worth catching.
    answer = subprocess.run(["git", "-C", str(root), "check-ignore", "-z", "--no-index", "--stdin"],
                            input=asked, capture_output=True, text=True, check=False)
    return sorted(p[len(prefix) + 1:] for p in answer.stdout.split("\0") if p)


def line_digest(line: str) -> str:
    return hashlib.sha256(line.strip().encode()).hexdigest()


def scan_text(name: str, text: str,
              spared_digests: tuple[str, ...] = WHITELIST_DIGESTS) -> tuple[list[str], int]:
    """Every line of one file that reads as a live credential, and how many were spared."""
    found, spared = [], 0
    for number, line in enumerate(text.split("\n"), start=1):
        if line.strip() and line_digest(line) in spared_digests:
            spared += 1
            continue
        for match in EMAIL.finditer(line):
            if hashlib.sha256(match.group(0).lower().encode()).hexdigest() in SECRET_EMAIL_DIGESTS:
                found.append(f"{name}:{number} carries the owner's own address")
        if KEY.search(line):
            found.append(f"{name}:{number} carries what reads as an API or access key")
        if CREDENTIAL.search(line):
            found.append(f"{name}:{number} assigns a literal password or secret")
    return found, spared


def scan(source: Path, files: list[str]) -> tuple[list[str], int, int]:
    """Findings, files read, whitelisted lines spared — a zero is only worth as much as those."""
    findings, read, spared = [], 0, 0
    for name in files:
        path = source / name
        if path.suffix.lower() in BINARY or not path.is_file():
            continue
        read += 1
        found, held = scan_text(name, path.read_text(encoding="utf-8", errors="replace"))
        findings.extend(found)
        spared += held
    return findings, read, spared


# The controls are assembled from parts so the scanner does not report its own fixtures.
CONTROL_CLEAN = "a plain line of prose with nothing to hide in it at all\n"
CONTROL_KEY = "TOKEN = 'sk-" + "A" * 24 + "'\n"
CONTROL_CREDENTIAL = "admin_password" + " = " + '"hunter2hunter2"' + "\n"


def controls() -> tuple[int, int, list[str]]:
    """A broken scanner reads every file as clean, so prove it fires before believing a zero."""
    spare = (line_digest(CONTROL_CREDENTIAL),)
    cases = [("clean", CONTROL_CLEAN, WHITELIST_DIGESTS, False),
             ("key", CONTROL_KEY, WHITELIST_DIGESTS, True),
             ("credential", CONTROL_CREDENTIAL, WHITELIST_DIGESTS, True),
             ("whitelist", CONTROL_CREDENTIAL, spare, False)]
    passed, lines = 0, []
    for label, text, spared_digests, expected in cases:
        found, _ = scan_text(f"control-{label}", text, spared_digests)
        fired = bool(found)
        passed += 1 if fired == expected else 0
        lines.append(f"  control {label:<11} expected {'a finding' if expected else 'no finding':<10} "
                     f"got {'a finding' if fired else 'no finding':<10} "
                     f"{'ok' if fired == expected else 'BROKEN'}")
    return passed, len(cases), lines


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Delta:
    """What the publish would do to the remote, named the way git names it."""

    def __init__(self, source: Path, files: list[str], clone: Path, remote_files: list[str]) -> None:
        here = {name: digest(source / name) for name in files}
        there = {name: digest(clone / name) for name in remote_files}
        added = sorted(set(here) - set(there))
        deleted = sorted(set(there) - set(here))
        self.modified = sorted(n for n in set(here) & set(there) if here[n] != there[n])
        gone = {there[name]: name for name in deleted}
        self.renamed = sorted((gone[here[name]], name) for name in added if here[name] in gone)
        moved_from = {old for old, _ in self.renamed}
        moved_to = {new for _, new in self.renamed}
        self.added = [n for n in added if n not in moved_to]
        self.deleted = [n for n in deleted if n not in moved_from]

    def empty(self) -> bool:
        return not (self.added or self.deleted or self.modified or self.renamed)

    def counts(self) -> str:
        return (f"added {len(self.added)} | deleted {len(self.deleted)} | "
                f"modified {len(self.modified)} | renamed {len(self.renamed)}")

    def render(self) -> list[str]:
        lines = [f"  A  {n}" for n in self.added]
        lines += [f"  D  {n}" for n in self.deleted]
        lines += [f"  M  {n}" for n in self.modified]
        lines += [f"  R  {old} -> {new}" for old, new in self.renamed]
        return lines


def fill(clone: Path, source: Path, files: list[str]) -> None:
    """The remote holds exactly the tracked tree — so empty it first, then lay the files down."""
    for entry in clone.iterdir():
        if entry.name == ".git":
            continue
        shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    for name in files:
        target = clone / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="publish",
        description="Republish the skill tree to its public remote. Reads by default; "
                    "writes only with --push.")
    parser.add_argument("--source", type=Path, default=SUITE_ROOT,
                        help="the tree to publish (default: this skill's root)")
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--message", default="", metavar="TEXT",
                        help="the commit subject; required by --push")
    parser.add_argument("--push", action="store_true",
                        help="write the delta to the remote instead of only printing it")
    arguments = parser.parse_args(argv)

    source = arguments.source.expanduser().resolve()
    if arguments.push and not arguments.message.strip():
        print("Refusing to push: --message '<subject>' says what this publish changed.\n"
              "A commit nobody can account for teaches the reader the log means nothing.")
        return REFUSED

    root, prefix = repo_of(source)
    files = tracked(root, prefix)
    if not files:
        print(f"Refusing to publish: git tracks no file under {prefix}.")
        return REFUSED

    loose = untracked(root, prefix)
    if loose:
        print(f"Refusing to publish: {len(loose)} untracked file(s) under {prefix}; "
              "commit or remove them first.")
        for name in loose[:10]:
            print(f"  {name}")
        return REFUSED

    dirty = modified(root, prefix)
    if dirty:
        print(f"Refusing to publish: {len(dirty)} uncommitted change(s) under {prefix}; "
              "the remote would not match any commit here.")
        for name in dirty[:10]:
            print(f"  {name}")
        return REFUSED

    hidden = ignored(root, prefix, files)
    if hidden:
        print(f"Refusing to publish: {len(hidden)} tracked file(s) match an ignore rule.")
        for name in hidden[:10]:
            print(f"  {name}")
        return REFUSED

    passed, total, control_lines = controls()
    print("POSITIVE CONTROLS")
    for line in control_lines:
        print(line)
    if passed != total:
        print(f"controls {passed} of {total} — a broken scan reads every file as clean")
        return REFUSED

    findings, read, spared = scan(source, files)
    print(f"CONSUMED {len(files)} tracked file(s), {read} read for secrets, "
          f"{spared} whitelisted line(s)")
    if findings:
        print(f"Refusing to publish: the secret scan found {len(findings)} line(s).")
        for line in findings[:10]:
            print(f"  {line}")
        return REFUSED

    workspace = Path(tempfile.mkdtemp(prefix="frappe-publish-"))
    clone = workspace / "remote"
    try:
        got = subprocess.run(
            ["git", "clone", "--quiet", "--branch", arguments.branch, "--single-branch",
             arguments.remote, str(clone)],
            capture_output=True, text=True, check=False)
        if got.returncode != 0:
            print(f"Failed to clone {arguments.remote} at {arguments.branch}: "
                  f"{got.stderr.strip().splitlines()[-1] if got.stderr.strip() else 'no reason given'}")
            return FAILED

        head = git(clone, "rev-parse", "HEAD").stdout.strip()
        there = sorted(p for p in git(clone, "ls-files", "-z").stdout.split("\0") if p)
        delta = Delta(source, files, clone, there)
        print(f"PUBLISH {prefix} -> {arguments.remote} {arguments.branch}")
        for line in delta.render():
            print(line)
        print(f"  {delta.counts()}")

        if not arguments.push:
            print(f"DRY RUN — remote head {head[:7]} was read, never written. "
                  "Add --push --message '<subject>' to publish.")
            return OK

        if delta.empty():
            print(f"Nothing to publish — the remote at {head[:7]} already carries this tree.")
            return OK

        fill(clone, source, files)
        git(clone, "add", "-A")
        made = git(clone, "commit", "-m", arguments.message.strip())
        if made.returncode != 0:
            print(f"Failed to commit: {made.stderr.strip() or made.stdout.strip()}")
            return FAILED
        sent = git(clone, "push", "origin", f"HEAD:{arguments.branch}")
        if sent.returncode != 0:
            print(f"Failed to push: {sent.stderr.strip() or sent.stdout.strip()}")
            return FAILED
        new = git(clone, "rev-parse", "HEAD").stdout.strip()
        print(f"old head   {head}")
        print(f"new commit {new}")
        print(f"  {delta.counts()}")
        return OK
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
