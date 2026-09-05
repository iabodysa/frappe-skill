# Copyright (c) 2026, iabodysa

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import source_scope
import translation_gate

from ctlkit.config import ProjectConfig, SourceString, TranslateResult, discover_config

SKIP_DIRS = source_scope.SKIP_DIRS | {"private"}

HAND_WRITTEN_UNDER_PUBLIC = ("public", "js")

JSON_TEXT_KEYS = {
    "label",
    "title",
    "subtitle",
    "description",
    "message",
    "success_message",
    "subject",
    "options",
    "action_label",
    "action_name",
    "button_label",
    "card_name",
    "chart_name",
    "column",
}

LABEL_KEYS = {
    "label",
    "title",
    "subtitle",
    "options",
    "action_label",
    "button_label",
    "card_name",
    "chart_name",
    "column",
}

_CALL_START = re.compile(r"\bfrappe\._\(|(?<![\w.])_{1,2}\(")
_NEXT_LITERAL = re.compile(r"""\s*\+?\s*(['"])((?:\\.|(?!\1).)*?)\1""")


def clean_text(value: str) -> str:
    if "\\" not in value:
        return value.strip()
    try:
        return value.encode("latin-1", "backslashreplace").decode("unicode_escape").strip()
    except (UnicodeDecodeError, UnicodeEncodeError):
        return value.strip()


def is_candidate_text(value: str, allow_placeholders: bool = False, max_length: int = 180,
                      allow_markup: bool = False) -> bool:
    text = value.strip()
    if not text or len(text) > max_length:
        return False
    if not re.search(r"[A-Za-z]", text):
        return False
    if not allow_markup and re.search(r"[<>]", text):
        return False
    if allow_markup and re.search(r"<\s*(script|style|iframe)", text, re.IGNORECASE):
        return False
    if re.search(r"#{3,}", text):
        return False
    if not allow_placeholders and re.search(r"[{}]", text):
        return False
    if text.startswith(("http://", "https://", "/", "#")):
        return False
    return True


def is_auto_translatable(text: str) -> bool:
    return "&" not in text


PROSE_KEYS = {"description", "message", "subject", "success_message"}
PROSE_MAX_LENGTH = 600


def add_candidate(
    items: list[SourceString], text: str, source: str, kind: str, allow_placeholders: bool = False
) -> None:
    prose = kind.split(":")[-1] in PROSE_KEYS
    max_length = PROSE_MAX_LENGTH if prose else 180
    for part in text.splitlines():
        cleaned = part.strip()
        if is_candidate_text(cleaned, allow_placeholders=allow_placeholders,
                             max_length=max_length, allow_markup=prose):
            items.append(SourceString(cleaned, source, kind))


def is_maintainer_file(name: str) -> bool:
    lowered = name.lower()
    return lowered.startswith("test_") and lowered.endswith(".json")


def walk_files(package_path: Path) -> Iterable[Path]:
    for path in package_path.rglob("*"):
        if not path.is_file():
            continue
        parts = path.relative_to(package_path).parts[:-1]
        if set(parts) & SKIP_DIRS and parts[:2] != HAND_WRITTEN_UNDER_PUBLIC:
            continue
        if is_maintainer_file(path.name):
            continue
        if path.suffix.lower() in {".json", ".py", ".js", ".ts", ".vue", ".html"}:
            yield path


def extract_json_strings(path: Path, package_path: Path) -> list[SourceString]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    found: list[SourceString] = []
    rel = str(path.relative_to(package_path))

    def visit(obj: object, key: str | None = None) -> None:
        if isinstance(obj, dict):
            skip_options = obj.get("fieldtype") == "Dynamic Link"
            if obj.get("parenttype") == "Workflow":
                for workflow_key in ("state", "next_state", "action"):
                    if isinstance(obj.get(workflow_key), str):
                        add_candidate(found, obj[workflow_key], rel, f"json:workflow-{workflow_key}")
            for child_key, child_value in obj.items():
                if child_key == "options" and skip_options:
                    continue
                visit(child_value, child_key)
        elif isinstance(obj, list):
            for item in obj:
                visit(item, key)
        elif isinstance(obj, str) and key in JSON_TEXT_KEYS:
            _scan_calls(obj, found, rel, f"json:{key}")
            add_candidate(found, obj, rel, f"json:{key}")

    if isinstance(payload, dict) and payload.get("doctype") == "DocType" and payload.get("name"):
        add_candidate(found, str(payload["name"]), rel, "json:doctype-name")
    if isinstance(payload, dict) and payload.get("doctype") == "Workspace":
        _extract_workspace_content(payload.get("content", ""), rel, found)
    visit(payload)
    return found


def find_label_placeholder_warnings(config: ProjectConfig) -> list[tuple[str, str, str]]:
    warnings: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for root in config.scan_roots:
        for path in walk_files(root):
            if path.suffix.lower() != ".json":
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            rel = str(path.relative_to(root))

            def visit(obj: object, key: str | None = None) -> None:
                if isinstance(obj, dict):
                    for child_key, child_value in obj.items():
                        visit(child_value, child_key)
                elif isinstance(obj, list):
                    for item in obj:
                        visit(item, key)
                elif isinstance(obj, str) and key in LABEL_KEYS:
                    if re.search(r"[{}]", obj) and re.search(r"[A-Za-z]", obj):
                        entry = (rel, key, obj.strip())
                        if entry not in seen:
                            seen.add(entry)
                            warnings.append(entry)

            visit(payload)
    return warnings


_HTML_TAG = re.compile(r"<[^>]+>")


def _extract_workspace_content(content_str: str, rel: str, found: list[SourceString]) -> None:
    if not content_str:
        return
    try:
        blocks = json.loads(content_str)
    except Exception:
        return
    if not isinstance(blocks, list):
        return
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type", "")
        if block_type not in {"header", "paragraph", "markdown"}:
            continue
        text = (block.get("data") or {}).get("text", "")
        if not isinstance(text, str):
            continue
        plain = _HTML_TAG.sub("", text).strip()
        if plain:
            add_candidate(found, plain, rel, "json:workspace-content")


def _scan_calls(content: str, found: list[SourceString], rel: str, kind: str) -> None:
    for call in _CALL_START.finditer(content):
        pos = call.end()
        parts: list[str] = []
        while (lit := _NEXT_LITERAL.match(content, pos)) is not None:
            parts.append(lit.group(2))
            pos = lit.end()
        if parts:
            add_candidate(found, clean_text("".join(parts)), rel, kind, allow_placeholders=True)


def extract_code_strings(path: Path, package_path: Path) -> list[SourceString]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    found: list[SourceString] = []
    rel = str(path.relative_to(package_path))
    _scan_calls(content, found, rel, "code:translate-call")
    return found


def extract_source_strings(config: ProjectConfig) -> list[SourceString]:
    found: list[SourceString] = []
    for root in config.scan_roots:
        for path in walk_files(root):
            if path.suffix.lower() == ".json":
                found.extend(extract_json_strings(path, root))
            else:
                found.extend(extract_code_strings(path, root))
    return found


def unique_texts(items: Iterable[SourceString]) -> list[str]:
    return sorted({item.text for item in items})


def read_translation_rows(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = csv.reader(handle)
        return {row[0]: row for row in rows if len(row) >= 2 and row[0].strip()}


def read_translation_csv(path: Path) -> dict[str, str]:
    return {source: row[1] for source, row in read_translation_rows(path).items()}


def check_against_csv(existing: dict[str, str], proposed: dict[str, str]) -> dict[str, object]:
    matches, collisions, additions = [], [], []
    for source in sorted(proposed):
        wanted = proposed[source].strip()
        current = existing.get(source)
        if current is None:
            additions.append({"source": source, "proposed": wanted})
        elif current.strip() == wanted:
            matches.append({"source": source, "translation": wanted})
        else:
            collisions.append({"source": source, "existing": current, "proposed": wanted})
    return {"matches": matches, "collisions": collisions, "additions": additions}


def run_translation_check(*, lang: str, root: Path | str | None = None,
                          rows_file: str = "") -> dict[str, object]:
    named = translation_gate.require_lang(lang)
    proposed: dict[str, str] = {}
    for number, line in enumerate(Path(rows_file).read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise SystemExit(f"{rows_file}:{number} is not JSON ({exc}).") from exc
        source, translation = row.get("source"), str(row.get("translation") or "")
        if not source or not translation.strip():
            raise SystemExit(f"{rows_file}:{number} needs a non-empty source and translation.")
        proposed[source] = translation
    config = discover_config(root, named)
    result = check_against_csv(read_translation_csv(config.translation_file), proposed)
    result["lang"] = named
    result["translation_file"] = str(config.translation_file)
    return result


def print_translation_check(result: dict[str, object]) -> None:
    collisions = result["collisions"]
    print(f"{len(result['matches'])} already identical · {len(collisions)} COLLIDE · "
          f"{len(result['additions'])} new  ({result['translation_file']})")
    for row in collisions:
        print(f"  {row['source']}\n      shipped: {row['existing']}\n      proposed: {row['proposed']}")


def write_translation_csv(path: Path, rows: dict[str, list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for source in sorted(rows):
            writer.writerow(rows[source])


def build_prompt(source: SourceString, config: ProjectConfig, module: str | None = None) -> str:
    context = {
        "task": "Translate one Frappe UI source string into the language named under "
                "\"language\" below.",
        "rules": [
            "Return JSON only.",
            "Keep English product names if they are brands.",
            "Write concise professional prose in that language, suitable for ERP navigation.",
            "Do not add explanations outside JSON.",
        ],
        "app": config.app,
        "language": config.lang,
        "module": module or infer_module(source.source),
        "source_file": source.source,
        "source_kind": source.kind,
        "source_text": source.text,
        "expected_json": {"source": source.text, "translation": "...", "confidence": "high|medium|low"},
    }
    return json.dumps(context, ensure_ascii=False, separators=(",", ":"))


def infer_module(source: str) -> str:
    parts = Path(source).parts
    if "doctype" in parts:
        idx = parts.index("doctype")
        if idx > 0:
            return parts[idx - 1]
    return "unknown"


def write_prompt_jsonl(config: ProjectConfig, sources: list[SourceString], missing: list[str]) -> Path:
    by_text = {item.text: item for item in sources}
    prompt_file = config.state_dir / "translation-prompts.jsonl"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    with prompt_file.open("w", encoding="utf-8") as handle:
        for text in missing:
            source = by_text[text]
            payload = {
                "model": config.claude_model,
                "thinking": config.claude_thinking,
                "prompt": build_prompt(source, config),
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    return prompt_file


def write_reports(result: TranslateResult, sources: list[SourceString]) -> None:
    cfg = result.config
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    state = {
        "last_run": now,
        **result.compact(),
        "missing": result.missing,
        "stale": result.stale,
    }
    cfg.state_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.report_file = cfg.todo_file
    lines = [
        "# frappe-pipes translates TODO",
        "",
        f"- Last run: `{now}`",
        f"- App: `{cfg.app}`",
        f"- Language: `{cfg.lang}`",
        f"- Used strings: `{len(result.used)}`",
        f"- Missing translations: `{len(result.missing)}`",
        f"- Stale CSV rows: `{len(result.stale)}`",
        f"- Added this run: `{result.added_count}`",
        f"- Pruned this run: `{result.pruned_count}`",
    ]
    if result.prompt_file:
        lines.append(f"- Prompt file: `{result.prompt_file}`")
    lines.extend(
        [
            "",
            "## Claude/Codex TODO",
            "",
            "- [ ] Add `frappe-pipes translates` to `build` as the preferred token-light translation audit workflow.",
            "- [ ] Document default scan mode, automatic prompt-file generation, `--json`, `--apply`, `--prune`, `--model`, and `--thinking`.",
            "- [ ] Keep the rule: `frappe-pipes translates` never calls Claude or Codex directly; workers run the generated prompts externally.",
            "- [ ] Keep the rule: never prune stale translation rows unless `--prune` is explicitly set.",
            "",
            "## Missing",
        ]
    )
    if result.missing:
        for text in result.missing:
            source = next((item for item in sources if item.text == text), None)
            where = f" ({source.source})" if source else ""
            lines.append(f"- [ ] `{text}`{where}")
    else:
        lines.append("- None")
    lines.extend(["", "## Stale Candidates"])
    if result.stale:
        for text in result.stale:
            lines.append(f"- [ ] `{text}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Label Placeholder Warnings",
            "",
            "_Static schema labels must not contain a `{placeholder}` — placeholders "
            "belong only to code `_()`/`__()` format-strings._",
            "",
        ]
    )
    if result.label_warnings:
        for rel, key, text in result.label_warnings:
            lines.append(f"- [ ] `{text}` — {rel} (`{key}`)")
    else:
        lines.append("- None")
    cfg.todo_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.todo_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_translates(
    *,
    lang: str,
    root: Path | str | None = None,
    apply: bool = False,
    prune: bool = False,
    supplied_translations: dict[str, str] | None = None,
    translate_with_ai: bool = False,
    emit_prompts: bool = False,
    model: str | None = None,
    thinking: str | None = None,
) -> TranslateResult:
    if translate_with_ai:
        raise SystemExit(
            "frappe-pipes translates does not call Claude or Codex directly. "
            "Run without --translate-with-claude and use the generated prompt_file externally."
        )
    config = discover_config(root, translation_gate.require_lang(lang))
    if model:
        config.claude_model = model
    if thinking:
        config.claude_thinking = thinking
    sources = extract_source_strings(config)
    used = unique_texts(sources)
    existing = read_translation_csv(config.translation_file)
    auto_translatable = {t for t in used if is_auto_translatable(t)}
    skipped = {t for t in used if not is_auto_translatable(t)}
    missing = sorted(auto_translatable - set(existing))
    stale = sorted(set(existing) - set(used))
    result = TranslateResult(
        config=config, used=used, missing=missing, stale=stale,
        skipped_count=len(skipped),
    )
    result.label_warnings = find_label_placeholder_warnings(config)

    if emit_prompts or missing:
        result.prompt_file = write_prompt_jsonl(config, sources, missing)

    translations = dict(supplied_translations or {})

    if apply:
        rows = read_translation_rows(config.translation_file)
        for source, translated in translations.items():
            if source in missing and translated.strip():
                rows[source] = [source, translated.strip()]
                result.added_count += 1
        if prune:
            for source in stale:
                rows.pop(source, None)
                result.pruned_count += 1
        write_translation_csv(config.translation_file, rows)

    write_reports(result, sources)
    return result


def _tr_pkg(config: ProjectConfig) -> str:
    return str(config.package_path.relative_to(config.root))


def _tr_extra_roots(config: ProjectConfig) -> list[str]:
    return [str(root.relative_to(config.root)) for root in config.scan_roots
            if root != config.package_path]


def _tr_verdict(root: str, lang: str, max_missing: int, max_stale: int) -> dict[str, object]:
    named = translation_gate.require_lang(lang)
    config = discover_config(root, named)

    def fallback() -> tuple[int, int]:
        result = run_translates(root=root, lang=named)
        return len(result.missing), len(result.stale)

    return translation_gate.verdict(
        config.root, _tr_pkg(config), named, max_missing, max_stale, fallback,
        _tr_extra_roots(config),
    )
