#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

from __future__ import annotations

import argparse
import csv
import json
import re
import tomllib
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", ".ctl", ".claude", "__pycache__", "node_modules", "translations",
             "locale", "private", "dist", "vendor", "assets"}
SCAN_EXTS = {".json", ".py", ".js", ".ts", ".vue", ".html"}


def is_maintainer_file(name: str) -> bool:
    lowered = name.lower()
    return lowered.startswith("test_") and lowered.endswith(".json")

JSON_TEXT_KEYS = {"label", "title", "subtitle", "description", "message",
                  "success_message", "subject", "options", "action_label",
                  "action_name", "action", "state", "button_label", "card_name",
                  "chart_name", "column"}
LABEL_KEYS = {"label", "title", "subtitle", "options", "action_label", "action", "state",
              "button_label", "card_name", "chart_name", "column"}
DECLARED_KEYS = {"description"}

_CALL_START = re.compile(r"(?<![A-Za-z0-9_])(?:(?:frappe\.)?_(?:lt)?|__)\(")
_NEXT_LITERAL = re.compile(r"""\s*\+?\s*(['"])((?:\\.|(?!\1).)*?)\1""")
_CONST_ASSIGN = re.compile(r"^(?:(?:const|let|var)\s+)?([A-Za-z_$][\w$]*)\s*=\s*\(?", re.M)
_IDENT_ARG = re.compile(r"\s*([A-Za-z_$][\w$]*)\s*[,)]")
_HTML_TAG = re.compile(r"<[^>]+>")

def project_config(package: Path) -> tuple[Path | None, dict]:
    for base in (package, package.parent, *package.parents):
        config = base / ".ctl.toml"
        if not config.is_file():
            continue
        with config.open("rb") as handle:
            return base, tomllib.load(handle)
    return None, {}


def retired_names(loaded: dict) -> dict[str, str | None]:
    table = loaded.get("translations", {}).get("retired", {})
    if not isinstance(table, dict):
        return {}
    return {name: (value or None) for name, value in table.items()}


def scan_roots(package: Path, base: Path | None, loaded: dict,
               extra: list[str]) -> list[Path]:
    declared = loaded.get("translations", {}).get("scan_roots")
    if declared is not None and not isinstance(declared, list):
        raise SystemExit("REFUSED: [translations].scan_roots must be a list of directories "
                         "relative to the .ctl.toml that declares it.")
    named: list[Path] = []
    for entry in (declared or []) if base is not None else []:
        root = (base / str(entry)).resolve()
        if not root.is_dir():
            raise SystemExit(f"REFUSED: [translations].scan_roots names {entry!r}, which is "
                             f"not a directory at {root}. A root that does not exist scans "
                             "nothing and reports a clean run.")
        named.append(root)
    for entry in extra:
        root = Path(entry).resolve()
        if not root.is_dir():
            raise SystemExit(f"REFUSED: --extra-root {entry!r} is not a directory at {root}.")
        named.append(root)
    ordered = [package] if not named else named
    seen, roots = set(), []
    for root in ordered:
        if root not in seen:
            seen.add(root)
            roots.append(root)
    return roots


def framework_locale_dirs(package: Path) -> list[Path]:
    for ancestor in [package.parent, *package.parent.parents]:
        for apps in (ancestor / "frappe-bench" / "apps", ancestor / "apps"):
            if (apps / "frappe" / "frappe" / "locale").is_dir():
                return [apps / app / app / "locale" for app in ("frappe", "erpnext", "hrms")
                        if (apps / app / app / "locale").is_dir()]
    return []


def read_po_msgids(po_path: Path) -> set:
    translated, msgid, msgstr, state = set(), [], [], None
    try:
        lines = po_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return translated

    def flush() -> None:
        if msgid and any(part for part in msgstr):
            translated.add("".join(msgid))

    for raw in lines:
        line = raw.strip()
        if line.startswith("msgid "):
            flush()
            msgid, msgstr, state = [_po_literal(line[6:])], [], "id"
        elif line.startswith("msgstr "):
            msgstr, state = [_po_literal(line[7:])], "str"
        elif line.startswith('"') and state == "id":
            msgid.append(_po_literal(line))
        elif line.startswith('"') and state == "str":
            msgstr.append(_po_literal(line))
        elif not line:
            flush()
            msgid, msgstr, state = [], [], None
    flush()
    return translated


def _po_literal(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    return text.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")


def framework_translated(package: Path, lang: str) -> set:
    covered: set = set()
    for locale_dir in framework_locale_dirs(package):
        covered |= read_po_msgids(locale_dir / f"{lang}.po")
    return covered


def clean_text(value: str) -> str:
    if "\\" not in value:
        return value.strip()
    try:
        return value.encode("latin-1", "backslashreplace").decode("unicode_escape").strip()
    except (UnicodeDecodeError, UnicodeEncodeError):
        return value.strip()


def is_candidate_text(value: str, declared: bool = False) -> bool:
    text = value.strip()
    if not text:
        return False
    if not re.search(r"[A-Za-z]", text):
        return False
    if not declared:
        if len(text) > 180:
            return False
        if re.search(r"[<>]", text):
            return False
        if "#" in text:
            return False
        if re.search(r"[{}]", text):
            return False
    return not text.startswith(("http://", "https://", "/", "#"))


def is_auto_translatable(text: str) -> bool:
    return "&" not in text


def add_candidate(found: set, text: str, declared: bool = False) -> None:
    for part in text.splitlines():
        cleaned = part.strip()
        if is_candidate_text(cleaned, declared=declared):
            found.add(cleaned)


def string_constants(content: str) -> dict:
    constants: dict = {}
    for assign in _CONST_ASSIGN.finditer(content):
        pos = assign.end()
        parts: list[str] = []
        while True:
            literal = _NEXT_LITERAL.match(content, pos)
            if literal is None:
                break
            parts.append(literal.group(2))
            pos = literal.end()
        if parts:
            constants[assign.group(1)] = clean_text("".join(parts))
    return constants


def scan_calls(content: str, found: set, constants: dict | None = None,
               calls: set | None = None, origin: str = "") -> None:
    for call in _CALL_START.finditer(content):
        pos = call.end()
        parts: list[str] = []
        while True:
            literal = _NEXT_LITERAL.match(content, pos)
            if literal is None:
                break
            parts.append(literal.group(2))
            pos = literal.end()
        if parts:
            msgid = clean_text("".join(parts))
            add_candidate(found, msgid, declared=True)
            if calls is not None:
                calls.add((origin, msgid))
            continue
        if not constants:
            continue
        ident = _IDENT_ARG.match(content, pos)
        if ident is not None and ident.group(1) in constants:
            add_candidate(found, constants[ident.group(1)], declared=True)
            if calls is not None:
                calls.add((origin, constants[ident.group(1)]))


def extract_workspace_content(content_str: str, found: set) -> None:
    if not content_str:
        return
    try:
        blocks = json.loads(content_str)
    except ValueError:
        return
    if not isinstance(blocks, list):
        return
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") not in {"header", "paragraph", "markdown"}:
            continue
        text = (block.get("data") or {}).get("text", "")
        if isinstance(text, str):
            plain = _HTML_TAG.sub("", text).strip()
            if plain:
                add_candidate(found, plain)


def git_files(package: Path) -> list[Path] | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(package), "ls-files", "-z",
             "--cached", "--others", "--exclude-standard"],
            capture_output=True, check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    names = proc.stdout.decode("utf-8", "surrogateescape").split("\0")
    return [package / name for name in names if name]


def walk_files(root: Path):
    candidates = git_files(root)
    if candidates is None:
        candidates = root.rglob("*")
    for path in candidates:
        if not path.is_file() or path.suffix.lower() not in SCAN_EXTS:
            continue
        if set(path.relative_to(root).parts[:-1]) & SKIP_DIRS:
            continue
        if is_maintainer_file(path.name):
            continue
        yield path


def extract(roots: list[Path]) -> tuple[set, list[tuple[str, str, str]], set, set, list[dict]]:
    found: set = set()
    warnings: list[tuple[str, str, str]] = []
    calls: set = set()
    doctypes: set = set()
    consumed: list[dict] = []

    for root in roots:
        files = chars = 0
        for path in walk_files(root):
            rel = f"{root.name}/{path.relative_to(root)}"
            if path.suffix.lower() != ".json":
                try:
                    content = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                files, chars = files + 1, chars + len(content)
                scan_calls(content, found, string_constants(content), calls, rel)
                continue
            try:
                raw = path.read_text(encoding="utf-8")
                payload = json.loads(raw)
            except (OSError, ValueError, UnicodeDecodeError):
                continue
            files, chars = files + 1, chars + len(raw)

            def visit(obj, key=None):
                if isinstance(obj, dict):
                    skip_options = obj.get("fieldtype") == "Dynamic Link"
                    for child_key, child in obj.items():
                        if child_key == "options" and skip_options:
                            continue
                        visit(child, child_key)
                elif isinstance(obj, list):
                    for item in obj:
                        visit(item, key)
                elif isinstance(obj, str):
                    if key in JSON_TEXT_KEYS:
                        scan_calls(obj, found, None, calls, rel)
                        add_candidate(found, obj, declared=key in DECLARED_KEYS)
                    if key in LABEL_KEYS and re.search(r"[{}]", obj) and re.search(r"[A-Za-z]", obj):
                        entry = (rel, key, obj.strip())
                        if entry not in warnings:
                            warnings.append(entry)

            if isinstance(payload, dict):
                if payload.get("doctype") == "DocType" and payload.get("name"):
                    add_candidate(found, str(payload["name"]))
                    doctypes.add(str(payload["name"]))
                if payload.get("doctype") == "Workspace":
                    extract_workspace_content(payload.get("content", ""), found)
            visit(payload)
        consumed.append({"root": root.name, "files": files, "chars": chars})
    return found, warnings, calls, doctypes, consumed


def retired_name_hits(calls: set, doctypes: set, retired: dict) -> tuple[list, list]:
    violations = []
    for origin, text in sorted(calls):
        for name, replacement in retired.items():
            if name in text:
                violations.append((origin, name, replacement, text))

    errors = []
    if doctypes:
        for name, replacement in sorted(retired.items()):
            if name in doctypes:
                errors.append((name, "ships as a DocType again, so it is not retired"))
            if replacement is not None and replacement not in doctypes:
                errors.append((name, f"replacement {replacement!r} ships no DocType"))
    return violations, errors


def read_csv_keys(path: Path) -> set:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as handle:
        return {row[0] for row in csv.reader(handle) if len(row) >= 2 and row[0].strip()}


def stale_baseline_path(package: Path, lang: str) -> Path:
    return package / "translations" / f"{lang}.stale-baseline.txt"


def read_stale_baseline(path: Path) -> set:
    if not path.exists():
        return set()
    lines = path.read_text(encoding="utf-8").splitlines()
    return {line for line in lines if line.strip() and not line.startswith("#")}


def write_stale_baseline(path: Path, stale: list, lang: str, regen: str) -> None:
    header = (
        f"# {lang}.csv rows whose English source string was already gone when this set\n"
        "# was recorded. The gate fails only on stale rows NOT listed here, so its\n"
        "# output names the row a change just stranded instead of all of them.\n"
        f"# Regenerate after deleting drained rows, with the translation gate:\n#   {regen}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "".join(f"{text}\n" for text in stale), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Coverage gate for one target language: every user-facing English string "
                    "the app ships must carry a row in that language's CSV.")
    parser.add_argument("--package", required=True, help="App package directory")
    parser.add_argument("--lang", required=True,
                        help="Target language code to score, e.g. ar or fr. No default: the "
                             "language belongs to whoever runs the scan")
    parser.add_argument("--max-missing", type=int, default=0)
    parser.add_argument("--max-stale", type=int, default=0,
                        help="Stale rows allowed BEYOND the recorded set, not in total")
    parser.add_argument("--update-stale-baseline", action="store_true",
                        help="Re-record the stale set, then report against it")
    parser.add_argument("--extra-root", action="append", default=[],
                        help="Another source tree that renders this catalogue, added to "
                             "the [translations].scan_roots declared in .ctl.toml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    package = Path(args.package).resolve()
    csv_path = package / "translations" / f"{args.lang}.csv"
    if not csv_path.exists():
        if args.json:
            print(json.dumps({"refused": True, "reason": "missing-csv",
                              "lang": args.lang, "csv_path": str(csv_path), "passed": False},
                             ensure_ascii=False, separators=(",", ":")))
        else:
            print(f"REFUSED: {csv_path} does not exist, so there is no {args.lang} "
                  "population to score. Point --package at an app root that ships "
                  f"translations/{args.lang}.csv, or create the file first.",
                  file=sys.stderr)
        return 2
    baseline_path = stale_baseline_path(package, args.lang)
    regen = (f"--package {args.package} --lang {args.lang} --update-stale-baseline")
    base, loaded = project_config(package)
    roots = scan_roots(package, base, loaded, args.extra_root)
    used, warnings, calls, doctypes, consumed = extract(roots)
    existing = read_csv_keys(csv_path)
    retired, retired_entry_errors = retired_name_hits(calls, doctypes,
                                                     retired_names(loaded))

    candidates = {t for t in used if is_auto_translatable(t)} - existing
    framework = framework_translated(package, args.lang)
    excused = sorted(candidates & framework)
    missing = sorted(candidates - framework)
    stale = sorted(existing - used)
    recorded = read_stale_baseline(baseline_path)
    new_stale = sorted(set(stale) - recorded)
    drained = sorted(recorded - set(stale))

    if args.update_stale_baseline:
        write_stale_baseline(baseline_path, stale, args.lang, regen)
        recorded, new_stale, drained = set(stale), [], []

    passed = (len(missing) <= args.max_missing
              and len(new_stale) <= args.max_stale
              and not warnings
              and not retired
              and not retired_entry_errors)

    if args.json:
        print(json.dumps({"lang": args.lang,
                          "missing_count": len(missing), "stale_count": len(stale),
                          "new_stale_count": len(new_stale),
                          "label_warning_count": len(warnings),
                          "retired_name_count": len(retired),
                          "retired_entry_error_count": len(retired_entry_errors),
                          "framework_excused_count": len(excused),
                          "scan_roots": [str(root) for root in roots],
                          "consumed": consumed,
                          "max_missing": args.max_missing, "max_stale": args.max_stale,
                          "passed": passed}, ensure_ascii=False, separators=(",", ":")))
        return 0 if passed else 1

    if args.update_stale_baseline:
        print(f"recorded {len(stale)} stale rows in {baseline_path.name}")
    for entry in consumed:
        print(f"consumed {entry['root']}: {entry['files']} source files, "
              f"{entry['chars']} characters")
    print(f"translations ({args.lang}): {len(missing)} missing, {len(stale)} stale "
          f"({len(new_stale)} newly stale), "
          f"{len(warnings)} label placeholder warnings, "
          f"{len(retired)} retired names in translate calls "
          f"(allowed: {args.max_missing} missing, {args.max_stale} newly stale, 0 warnings, "
          "0 retired)")
    if missing:
        print(f"\nMISSING — add a row in {args.lang} to {csv_path.name} for each:")
        for text in missing:
            print(f"  {text}")
    if excused:
        print(f"\nFRAMEWORK-TRANSLATED ({len(excused)}) — the installed frappe/erpnext/hrms "
              f"already ship {args.lang} for these, so a row of your own would duplicate and "
              "override the framework's wording:")
        for text in excused:
            print(f"  {text}")
    if len(new_stale) > args.max_stale:
        print(f"\nNEWLY STALE ({len(new_stale)}) — these {csv_path.name} rows lost their "
              f"English source since {baseline_path.name} was recorded. Deleting or "
              "renaming a source string is what strands a row, so the fix belongs with "
              "that change: re-key the row to the new source string, or delete the row "
              "if the string is gone for good, then re-record the set with\n"
              f"    {regen}")
        for text in new_stale:
            print(f"  {text}")
    if drained:
        noun = "row is" if len(drained) == 1 else "rows are"
        print(f"\n{len(drained)} recorded stale {noun} no longer stale. Not a failure — "
              "a spent entry excuses only itself — but re-record to keep the set honest:\n"
              f"    {regen}")
    for rel, key, text in warnings:
        print(f"\nLABEL PLACEHOLDER — {rel} ({key}): {text}")
        print("  A static label renders verbatim; move the placeholder into a code _() call.")
    if retired:
        print(f"\nRETIRED NAME ({len(retired)}) — a translate call still names a record "
              "the rename retired, so the user reads a record that no longer exists. "
              f"Reword the message, then re-key its {csv_path.name} row to the new "
              "English source in the SAME change — the row is keyed on that string and "
              f"editing it alone strands the {args.lang} translation:")
        for rel, name, replacement, text in retired:
            became = repr(replacement) if replacement else "nothing — the record was folded away"
            print(f"  {rel}: {name!r} -> {became}\n      {text}")
    for name, problem in retired_entry_errors:
        print(f"\nRETIRED ENTRY — {name!r}: {problem}")
        print("  Fix or drop the entry under [translations.retired] in .ctl.toml.")
    print("\n" + ("PASS" if passed else "FAIL"))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
