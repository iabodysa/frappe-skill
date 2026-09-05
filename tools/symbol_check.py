# Copyright (c) 2026, iabodysa

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bench_source import DEFAULT_BENCH_ROOT, _source_root

SKILL_ROOT = Path(__file__).resolve().parent.parent
SOURCES = SKILL_ROOT / "SOURCES.json"
KNOWLEDGE_ROOT = SKILL_ROOT / "knowledge"
POINTER = re.compile(r"(?:knowledge|references|tasks)/[\w./-]+\.md")
PATHS_HEADING = re.compile(r"^##\s+paths\s*$", re.I)
NEXT_HEADING = re.compile(r"^##\s+")
PRODUCT = re.compile(r'^product:\s*"?([\w.-]+)"?\s*$', re.M)
VERSION = re.compile(r'^verified_version:\s*"?([\w.-]+)"?\s*$', re.M)
SEPARATOR = re.compile(r"\s+[—-]\s+")


class Finding:
    def __init__(self, leaf: str, verdict: str, detail: str) -> None:
        self.leaf, self.verdict, self.detail = leaf, verdict, detail

    def render(self) -> str:
        return f"  {self.verdict:<12} {self.leaf}\n    {self.detail}"


def path_lines(text: str) -> list[str]:
    lines, inside = [], False
    for line in text.split("\n"):
        if PATHS_HEADING.match(line):
            inside = True
            continue
        if inside and NEXT_HEADING.match(line):
            break
        if inside and line.strip():
            lines.append(line.strip())
    return lines


def named(line: str) -> tuple[str, list[str]]:
    parts = SEPARATOR.split(line.lstrip("- ").strip(), maxsplit=1)
    path = parts[0].strip().strip("`")
    if len(parts) == 1:
        return path, []
    return path, [s.strip().strip("`") for s in parts[1].split(",") if s.strip()]


def declared_version(product: str) -> str | None:
    if not SOURCES.is_file():
        return None
    entry = json.loads(SOURCES.read_text(encoding="utf-8"))["products"].get(product, {})
    return entry.get("version")


def products() -> list[str]:
    if not SOURCES.is_file():
        return ["frappe"]
    return list(json.loads(SOURCES.read_text(encoding="utf-8"))["products"])


def resolve(bench_root: Path, product: str, version: str | None, path: str) -> Path | None:
    tried = [(product, version)] + [(other, declared_version(other))
                                    for other in products() if other != product]
    for name, wanted in tried:
        try:
            target = _source_root(bench_root, name, wanted) / path
        except (ValueError, FileNotFoundError):
            continue
        if target.is_file():
            return target
    return None


def check(leaf: Path, bench_root: Path, root: Path) -> tuple[list[Finding], int]:
    text = leaf.read_text(encoding="utf-8")
    product = (PRODUCT.search(text).group(1) if PRODUCT.search(text) else "frappe")
    version = (VERSION.search(text).group(1) if VERSION.search(text)
               else declared_version(product))
    name = str(leaf.relative_to(root))
    found, seen = [], 0
    for line in path_lines(text):
        path, symbols = named(line)
        if not path or "/" not in path:
            continue
        seen += 1
        target = resolve(bench_root, product, version, path)
        if target is None:
            found.append(Finding(name, "FILE GONE",
                                 f"{path} names no file under any product this store declares"))
            continue
        body = target.read_text(encoding="utf-8", errors="replace")
        for symbol in symbols:
            if symbol.split(".")[-1] not in body:
                found.append(Finding(name, "SYMBOL GONE", f"{path} carries no {symbol}"))
    return found, seen


CONTROL_PRESENT = """---
name: control
product: "frappe"
---

## paths

frappe/model/naming.py — set_new_name
"""

CONTROL_ABSENT = CONTROL_PRESENT.replace("set_new_name", "no_such_symbol_at_all")

CONTROL_FILE_GONE = CONTROL_PRESENT.replace("frappe/model/naming.py", "frappe/model/no_such_file.py")


def controls(bench_root: Path, workspace: Path) -> tuple[int, int, list[str]]:
    cases = [("present", CONTROL_PRESENT, ""),
             ("absent", CONTROL_ABSENT, "SYMBOL GONE"),
             ("gone", CONTROL_FILE_GONE, "FILE GONE")]
    fired, lines = 0, []
    workspace.mkdir(parents=True, exist_ok=True)
    for label, text, expected in cases:
        leaf = workspace / f"control-{label}.md"
        leaf.write_text(text, encoding="utf-8")
        found, _ = check(leaf, bench_root, workspace)
        leaf.unlink()
        verdicts = {f.verdict for f in found}
        ok = (not verdicts) if not expected else (expected in verdicts)
        fired += 1 if ok else 0
        lines.append(f"  control {label:<8} expected {expected or 'no finding':<12} got "
                     f"{', '.join(sorted(verdicts)) or 'no finding':<12} {'ok' if ok else 'BROKEN'}")
    return fired, len(cases), lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="symbol-check")
    parser.add_argument("--bench-root", default=str(DEFAULT_BENCH_ROOT))
    parser.add_argument("--knowledge-root", default=str(KNOWLEDGE_ROOT))
    arguments = parser.parse_args(argv)
    bench_root = Path(arguments.bench_root).expanduser().resolve()
    root = Path(arguments.knowledge_root).expanduser().resolve()

    workspace = root.parent / ".symbol-check-controls"
    passed, total, control_lines = controls(bench_root, workspace)
    if workspace.exists():
        for leftover in workspace.iterdir():
            leftover.unlink()
        workspace.rmdir()
    print("POSITIVE CONTROLS")
    for line in control_lines:
        print(line)
    if passed != total:
        print(f"controls {passed} of {total} — a broken detector reads every leaf as clean")
        return 2

    findings, leaves, seen = [], 0, 0
    for leaf in sorted(p for p in root.rglob("*.md") if p.name != "README.md"):
        leaves += 1
        found, lines = check(leaf, bench_root, root)
        findings.extend(found)
        seen += lines
    pointers = 0
    for page in sorted(SKILL_ROOT.rglob("*.md")):
        if not page.is_relative_to(SKILL_ROOT / "tasks") and not page.is_relative_to(SKILL_ROOT / "references"):
            continue
        for match in POINTER.finditer(page.read_text(encoding="utf-8", errors="replace")):
            pointers += 1
            if not (SKILL_ROOT / match.group(0)).is_file():
                findings.append(Finding(str(page.relative_to(SKILL_ROOT)), "POINTER DEAD",
                                        f"{match.group(0)} names no page in this store"))
    print(f"CONSUMED {leaves} leaf file(s), {seen} path line(s) and {pointers} pointer(s)")
    for finding in findings:
        print(finding.render())
    print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
