#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

LAYOUT = {"Section Break", "Column Break", "Tab Break", "HTML", "Heading"}


def _read_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def resolve_config(root: str | None) -> dict:
    cfg: dict = {}
    home_toml = Path.home() / ".ctl.toml"
    if home_toml.is_file():
        cfg.update(_read_toml(home_toml).get("global", {}))

    project = Path(root).expanduser() if root else None
    if project is None and cfg.get("default_project"):
        project = Path(cfg["default_project"]).expanduser()
    if project is None:
        project = Path.cwd()

    local = project / ".ctl.toml"
    if local.is_file():
        data = _read_toml(local)
        cfg.update(data.get("global", {}))
        scoped = data.get("project", {})
        if scoped.get("site"):
            cfg["site"] = scoped["site"]
        if scoped.get("bench_path"):
            cfg["bench"] = str((project / str(scoped["bench_path"])).resolve())

    cfg["project"] = str(project)
    cfg.setdefault("bench", str(Path(cfg.get("bench", "~/Developer/frappe-bench")).expanduser()))
    return cfg


def doctype_files(project: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in project.rglob("*/doctype/*/*.json"):
        if path.stem != path.parent.name or "node_modules" in path.parts:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("doctype") == "DocType" or "fields" in data:
            out[data.get("name", path.stem)] = path
    return out


def describe(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    fields = data.get("fields", [])

    def entry(f: dict) -> dict:
        item = {"fieldname": f.get("fieldname"), "type": f.get("fieldtype"),
                "label": f.get("label")}
        if f.get("fieldtype") in ("Select",) and f.get("options"):
            item["values"] = [o for o in str(f["options"]).split("\n") if o != ""]
        if f.get("fieldtype") in ("Link", "Table", "Table MultiSelect"):
            item["target"] = f.get("options")
        if f.get("default"):
            item["default"] = f.get("default")
        return item

    return {
        "name": data.get("name", path.stem),
        "module": data.get("module"),
        "path": str(path),
        "submittable": bool(data.get("is_submittable")),
        "istable": bool(data.get("istable")),
        "autoname": data.get("autoname"),
        "required": [entry(f) for f in fields if f.get("reqd")],
        "children": [entry(f) for f in fields
                     if f.get("fieldtype") in ("Table", "Table MultiSelect")],
        "selects": [entry(f) for f in fields
                    if f.get("fieldtype") == "Select" and not f.get("hidden")],
        "links": [entry(f) for f in fields
                  if f.get("fieldtype") == "Link" and not f.get("hidden")],
        "field_count": len([f for f in fields if f.get("fieldtype") not in LAYOUT]),
    }


def render(spec: dict, files: dict[str, Path]) -> str:
    lines = [f"{spec['name']}   module={spec['module']}   fields={spec['field_count']}"
             + ("   SUBMITTABLE" if spec["submittable"] else "")
             + ("   CHILD TABLE" if spec["istable"] else "")]
    if spec.get("autoname"):
        lines.append(f"  autoname: {spec['autoname']}")

    lines.append("\nMUST be set:")
    if not spec["required"]:
        lines.append("  (nothing mandatory)")
    for f in spec["required"]:
        extra = ""
        if f.get("values"):
            extra = "  one of: " + " | ".join(f["values"])
        elif f.get("target"):
            extra = f"  -> {f['target']}"
        lines.append(f"  {f['fieldname']:<24} {f['type']:<16}{extra}")

    if spec["children"]:
        lines.append("\nCHILD ROWS — the parent will refuse an empty table:")
        for f in spec["children"]:
            child = files.get(f.get("target") or "")
            need = ""
            if child:
                sub = describe(child)
                need = "  row needs: " + ", ".join(
                    r["fieldname"] for r in sub["required"]) if sub["required"] else "  row needs: (nothing)"
            lines.append(f"  {f['fieldname']:<24} -> {f.get('target')}{need}")

    other = [f for f in spec["selects"] if f["fieldname"] not in
             {r["fieldname"] for r in spec["required"]}]
    if other:
        lines.append("\nOTHER SELECT VALUES — the stored value is English, not the label:")
        for f in other[:12]:
            lines.append(f"  {f['fieldname']:<24} {' | '.join(f.get('values') or [])}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read a DocType's shape from shipped JSON.")
    ap.add_argument("doctype", nargs="?")
    ap.add_argument("--root", help="project root; else .ctl.toml, else ~/.ctl.toml")
    ap.add_argument("--find", metavar="WORD", help="list DocTypes whose name contains WORD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--config", action="store_true", help="print the resolved paths and exit")
    args = ap.parse_args(argv)

    cfg = resolve_config(args.root)
    project = Path(cfg["project"])

    if args.config:
        print(json.dumps(cfg, ensure_ascii=False, indent=1))
        return 0

    if not project.is_dir():
        print(f"project root not found: {project}", file=sys.stderr)
        return 2

    files = doctype_files(project)
    print(f"read={len(files)} DocType JSON files under {project}", file=sys.stderr)
    if not files:
        print(f"no DocType JSON found under {project} — a zero here is an empty scan, "
              "not a clean one; pass --root at the app that ships the JSON", file=sys.stderr)
        return 2

    if args.find:
        needle = args.find.lower()
        hits = sorted(n for n in files if needle in n.lower())
        for name in hits:
            print(name)
        if not hits:
            print(f"no DocType matching {args.find!r} under {project}", file=sys.stderr)
        return 0 if hits else 1

    if not args.doctype:
        ap.error("give a DocType name, or --find WORD")

    match = files.get(args.doctype)
    if match is None:
        near = sorted(n for n in files if args.doctype.lower() in n.lower())
        print(f"no DocType named {args.doctype!r} under {project}", file=sys.stderr)
        if near:
            print("did you mean: " + ", ".join(near[:8]), file=sys.stderr)
        return 1

    spec = describe(match)
    print(json.dumps(spec, ensure_ascii=False, indent=1) if args.json else render(spec, files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
