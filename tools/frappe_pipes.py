# Copyright (c) 2026, iabodysa

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import create_kit
import model_audit
import release_gate
import repo_guards
import schema_peek
import seed_kit
import translation_gate
from ctlkit.changelog import run_changelog
from ctlkit.config import TranslateResult, discover_config
from ctlkit.release import (changed_record_json, run_bump, run_bump_smart,
                            run_stamp, stamp_timestamp)
from ctlkit.translate import (_tr_extra_roots, _tr_pkg, _tr_verdict, print_translation_check,
                              run_translates, run_translation_check)


def parse_supplied_translations(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --translation value, expected source=translation: {value}")
        source, translation = value.rsplit("=", 1)
        parsed[source] = translation
    return parsed


def print_human(result: TranslateResult) -> None:
    print(f"app={result.config.app} lang={result.config.lang}")
    print(f"translation_file={result.config.translation_file}")
    print(
        "used={used} missing={missing} stale={stale} added={added} pruned={pruned}".format(
            used=len(result.used),
            missing=len(result.missing),
            stale=len(result.stale),
            added=result.added_count,
            pruned=result.pruned_count,
        )
    )
    if result.label_warnings:
        print(
            f"label_placeholder_warnings={len(result.label_warnings)} "
            f"(static labels must not contain a {{placeholder}})"
        )
        for rel, key, text in result.label_warnings:
            print(f"- {rel} [{key}]: {text}")
    if result.prompt_file:
        print(f"prompt_file={result.prompt_file}")
    print(f"todo={result.report_file}")
    if result.errors:
        print("errors:")
        for error in result.errors:
            print(f"- {error}")


def run_check_translations(
    root: str = ".",
    lang: str | None = None,
    max_missing: int = 0,
    max_stale: int = 0,
    as_json: bool = False,
) -> int:
    config = discover_config(root, lang)
    named = translation_gate.require_lang(lang or config.lang)
    script = repo_guards.script(config.root, "check_translations.py")
    if script is not None:
        argv = translation_gate.argv(_tr_pkg(config), named, max_missing,
                                     max_stale, _tr_extra_roots(config))
        return repo_guards.delegate(script, argv + ["--json"] if as_json else argv, config.root)
    verdict = _tr_verdict(root, named, max_missing, max_stale)
    missing, stale, passed = verdict["missing"], verdict["stale"], bool(verdict["ok"])
    if as_json:
        reason = ""
        if missing > max_missing:
            reason = f"{missing} missing translations exceed limit of {max_missing}"
        elif stale > max_stale:
            reason = f"{stale} stale translations exceed limit of {max_stale}"
        print(json.dumps(
            {"missing_count": missing, "stale_count": stale, "max_missing": max_missing,
             "max_stale": max_stale, "passed": passed, "reason": reason},
            ensure_ascii=False, separators=(",", ":"),
        ))
    else:
        print(
            f"translations: {missing} missing, {stale} stale"
            f" → {'PASS' if passed else 'FAIL'} (max allowed: {max_missing} missing, {max_stale} stale)"
        )
    return 0 if passed else 1


def run_seed(*, root: str | None = None, seed_file: str = "", dry_run: bool = False,
             no_site: bool = False, as_json: bool = False) -> int:
    return seed_kit.run(discover_config(root), Path(seed_file), dry_run=dry_run,
                        no_site=no_site, as_json=as_json)


class VerbRegistry:
    def __init__(self, sub) -> None:
        self._sub = sub
        self.verbs: dict[str, str] = {}

    def add_parser(self, name: str, **kwargs):
        self.verbs[name] = str(kwargs.get("help") or "")
        return self._sub.add_parser(name, **kwargs)

    def __getattr__(self, name: str):
        return getattr(self._sub, name)


def render_verbs(verbs: dict[str, str], width: int = 20) -> str:
    lines = [f"read={len(verbs)} verbs registered by frappe-pipes"]
    for name in sorted(verbs):
        summary = " ".join(verbs[name].split())
        if len(summary) > 62:
            summary = summary[:59].rstrip() + "..."
        lines.append(f"  {name.ljust(width)}{summary}")
    lines.append("  frappe-pipes <verb> --help  for one verb's own options")
    return "\n".join(lines)


def build_parser() -> tuple[argparse.ArgumentParser, dict[str, str]]:
    parser = argparse.ArgumentParser(
        prog="frappe-pipes",
        usage="frappe-pipes <command> [options]",
        description="The Frappe pipes carried out of the retired toolbox.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="frappe-pipes verbs  lists every verb this pipe registers\n",
    )
    sub = VerbRegistry(parser.add_subparsers(dest="command", required=True, metavar="<command>"))

    sub.add_parser("verbs", help="List every verb this pipe registers, and the count of them")

    translates = sub.add_parser("translates", help="Scan and maintain Frappe translation CSV files")
    translates.add_argument("--root", default=".", help="Frappe bench or project root")
    translates.add_argument("--lang", default=None, help="Target language code, e.g. ar or fr. No default: the runner names it")
    translates.add_argument("--apply", action="store_true", help="Write supplied translations to CSV")
    translates.add_argument("--prune", action="store_true", help="Remove stale rows from CSV; only works with --apply")
    translates.add_argument("--json", action="store_true", help="Print compact JSON summary")
    translates.add_argument("--emit-prompts", action="store_true", help="Write translation JSONL prompts without executing AI tools")
    translates.add_argument("--translation", action="append", default=[], help="Manual source=translation pair")
    translates.add_argument("--apply-file", default=None, help="JSONL file of {source,translation} rows to apply (implies --apply)")
    translates.add_argument("--check-file", default=None, dest="check_file", help="Grade a JSONL of {source,translation} rows against the shipped CSV; writes nothing")
    translates.add_argument("--model", default=None, help="AI model metadata override for generated prompts")
    translates.add_argument("--thinking", default=None, help="AI thinking-level metadata override for generated prompts")

    check_trans = sub.add_parser("check-translations", help="Gate commits when translations are missing or stale")
    check_trans.add_argument("--root", default=".", help="Frappe bench or project root")
    check_trans.add_argument("--lang", default=None, help="Target language code, e.g. ar or fr. No default: the runner names it")
    check_trans.add_argument("--max-missing", type=int, default=0, metavar="INT",
                             help="Fail if missing_count exceeds this (default 0)")
    check_trans.add_argument("--max-stale", type=int, default=0, metavar="INT",
                             help="Fail if stale_count exceeds this (default 0)")
    check_trans.add_argument("--json", action="store_true", help="Print compact JSON summary")

    changelog = sub.add_parser("changelog", help="Create the native Frappe changelog markdown for a version")
    changelog.add_argument("version", help="Semantic version X.Y.Z")
    changelog.add_argument("--root", default=".", help="Frappe bench or project root")
    changelog.add_argument("--title", default=None, help="App title override for the changelog heading")
    changelog.add_argument("--summary", default=None, help="One concise operator-facing summary line")
    changelog.add_argument("--bullet", action="append", default=[], help="A true shipped change; repeat once per change, no filler")
    changelog.add_argument("--draft", action="store_true", help="Create a draft with placeholder bullets")
    changelog.add_argument("--json", action="store_true", help="Print compact JSON summary")

    bump_parser = sub.add_parser("bump", help="Update app version declarations")
    bump_parser.add_argument("version", nargs="?", default=None, help="Semantic version X.Y.Z (omit with --smart)")
    bump_parser.add_argument("--root", default=".", help="Frappe bench or project root")
    bump_parser.add_argument("--json", action="store_true", help="Print compact JSON summary")
    bump_parser.add_argument("--smart", action="store_true", help="Analyse git diff and propose the correct semver bump")
    bump_parser.add_argument("--base", default="HEAD", help="Git ref to diff against (default: HEAD)")
    bump_parser.add_argument("--apply", action="store_true", help="Actually apply the proposed bump (only with --smart)")
    bump_parser.add_argument(
        "--allow-bookkeeping",
        default="",
        metavar="REASON",
        help="Release even though nothing but version files and the changelog has landed",
    )
    release_gate.add_arguments(bump_parser)

    bump_smart_parser = sub.add_parser("bump-smart", help="Analyse git diff and propose the correct semver bump")
    bump_smart_parser.add_argument("--root", default=".", help="Frappe bench or project root")
    bump_smart_parser.add_argument("--base", default="HEAD", help="Git ref to diff against (default: HEAD)")
    bump_smart_parser.add_argument("--json", action="store_true", help="Print compact JSON output")
    bump_smart_parser.add_argument("--apply", action="store_true", help="Apply the proposed version bump")
    release_gate.add_arguments(bump_smart_parser)

    stamp_parser = sub.add_parser("stamp", help="Update the modified field in JSON metadata files")
    stamp_parser.add_argument("paths", nargs="*", help="JSON metadata files to stamp")
    stamp_parser.add_argument(
        "--changed",
        action="store_true",
        help="Stamp the changed Workspace/Notification/Number Card/Dashboard Chart records git reports",
    )
    stamp_parser.add_argument("--root", default=".", help="Frappe bench or project root")
    stamp_parser.add_argument("--dry-run", action="store_true", help="List what --changed would stamp and exit")
    stamp_parser.add_argument("--json", action="store_true", help="Print compact JSON summary")


    sc_parser = sub.add_parser(
        "schema",
        help="A DocType's shape read from shipped JSON — mandatory fields, Select values, Link targets, child tables; no bench",
    )
    sc_parser.add_argument("doctype", nargs="?", help="DocType name, as titled in the JSON")
    sc_parser.add_argument("--root", default=None, help="Override project discovery")
    sc_parser.add_argument("--find", metavar="WORD", help="List DocTypes whose name contains WORD")
    sc_parser.add_argument("--config", action="store_true", help="Print the resolved project and bench paths and exit")
    sc_parser.add_argument("--json", action="store_true", help="Print machine JSON")

    ma_parser = sub.add_parser(
        "model-audit",
        help="Model-integrity findings read from shipped DocType JSON — dead fields, invalid Link targets, required-Link cycles, copy-forward; writes nothing to the app",
    )
    model_audit.add_arguments(ma_parser)

    seed_parser = sub.add_parser(
        "seed",
        help="Create a record set described in a seed file through Frappe's own document API",
    )
    seed_parser.add_argument("file", help="Seed file (.toml): DocTypes, field values, child rows")
    seed_parser.add_argument("--root", default=".", help="Frappe bench or project root")
    seed_parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                             help="Resolve every Link and Select against the shipped JSON, write nothing")
    seed_parser.add_argument("--no-site", action="store_true", dest="no_site",
                             help="With --dry-run, skip the read-only Link-exists pass against the site")
    seed_parser.add_argument("--json", action="store_true", help="Print machine JSON")

    create_kit.add_arguments(sub)

    return parser, sub.verbs


def main(argv: list[str] | None = None) -> int:
    parser, verbs = build_parser()
    args = parser.parse_args(argv)

    if args.command == "verbs":
        print(render_verbs(verbs))
        return 0

    if args.command == "translates" and getattr(args, "check_file", None):
        checked = run_translation_check(root=args.root, lang=args.lang, rows_file=args.check_file)
        if args.json:
            print(json.dumps(checked, ensure_ascii=False, separators=(",", ":")))
        else:
            print_translation_check(checked)
        return 1 if checked["collisions"] else 0

    if args.command == "translates":
        supplied = parse_supplied_translations(args.translation)
        apply_flag = args.apply
        apply_file = getattr(args, "apply_file", None)
        if apply_file:
            apply_flag = True
            for line in Path(apply_file).read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                src = obj.get("source")
                tr = obj.get("translation", "")
                if not src or not str(tr).strip():
                    raise SystemExit(f"Invalid JSONL row (need non-empty source+translation): {line}")
                supplied[src] = str(tr)
        result = run_translates(
            root=args.root,
            lang=args.lang,
            apply=apply_flag,
            prune=args.prune,
            supplied_translations=supplied,
            translate_with_ai=False,
            emit_prompts=args.emit_prompts,
            model=args.model,
            thinking=args.thinking,
        )
        if args.json:
            print(json.dumps(result.compact(), ensure_ascii=False, separators=(",", ":")))
        else:
            print_human(result)
        return 1 if result.errors else 0

    if args.command == "check-translations":
        return run_check_translations(
            root=args.root,
            lang=args.lang,
            max_missing=args.max_missing,
            max_stale=args.max_stale,
            as_json=args.json,
        )

    if args.command == "changelog":
        result = run_changelog(
            root=args.root,
            version=args.version,
            summary=args.summary,
            bullets=args.bullet,
            title=args.title,
            draft=args.draft,
        )
        if args.json:
            print(json.dumps(result.compact(), ensure_ascii=False, separators=(",", ":")))
        else:
            print(f"changelog={result.file}")
            print(f"index={result.index_file}")
            if result.feed_file:
                state = "updated" if result.feed_updated else "already carried this version"
                print(f"feed={result.feed_file} ({state})")
            else:
                print("feed=none found — check the app's in-app release list by hand")
        return 0

    if args.command in {"bump", "bump-smart"}:
        if args.command == "bump-smart" or getattr(args, "smart", False):
            result = run_bump_smart(
                root=args.root,
                base=getattr(args, "base", "HEAD"),
                apply=getattr(args, "apply", False),
                as_json=args.json,
                kind=getattr(args, "kind", "") or "",
                reason=getattr(args, "reason", "") or "",
            )
            if args.json:
                print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
            else:
                print(f"current_version={result['current_version']}")
                print(f"proposed_version={result['proposed_version']}")
                print(f"bump_type={result['bump_type']}")
                print(f"reason={result['reason']}")
                print(f"changed_files={result['changed_files']}")
                print(f"applied={result['applied']}")
            return 0
        if not args.version:
            raise SystemExit("bump requires a version argument (X.Y.Z) or --smart flag")
        result = run_bump(
            root=args.root,
            version=args.version,
            allow_bookkeeping=getattr(args, "allow_bookkeeping", "") or "",
            kind=getattr(args, "kind", "") or "",
            reason=getattr(args, "reason", "") or "",
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        else:
            print(f"version={result['version']}")
            print(
                f"since={result['release_base'] or '(no previous release)'}"
                f" commits={result['content_commits']} content_files={result['content_files']}"
            )
            for path in result["updated"]:
                print(f"updated={path}")
        return 0

    if args.command == "stamp":
        paths = list(args.paths)
        if args.changed:
            paths += [str(p) for p in changed_record_json(discover_config(args.root).root)]
        if not paths:
            print("stamp: nothing to stamp — pass paths, or --changed with an edited record")
            return 0
        if args.dry_run:
            print(f"would_stamp={len(paths)} at {stamp_timestamp()}")
            for path in paths:
                print(path)
            return 0
        result = run_stamp(paths)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        else:
            print(f"stamped={result['stamped_count']}")
            for path in result["stamped"]:
                print(path)
        return 1 if result["failed"] else 0


    if args.command == "schema":
        argv_out = [args.doctype] if args.doctype else []
        for flag, value in (("--root", args.root), ("--find", args.find)):
            if value:
                argv_out += [flag, value]
        for flag, on in (("--config", args.config), ("--json", args.json)):
            if on:
                argv_out.append(flag)
        return schema_peek.main(argv_out)

    if args.command == "model-audit":
        return model_audit.run(root=args.root, package=args.package, only=args.only,
                               as_json=args.json, out=args.out)

    if args.command == "seed":
        return run_seed(root=args.root, seed_file=args.file, dry_run=args.dry_run,
                        no_site=args.no_site, as_json=args.json)

    if args.command == "create":
        return create_kit.run(args)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
