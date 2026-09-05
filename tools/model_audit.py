# Copyright (c) 2026, iabodysa

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from source_scope import SKIP_DIRS
except ImportError:  # invoked as a path from outside the tools directory
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from source_scope import SKIP_DIRS

LINKISH = {"Link", "Dynamic Link"}
STRUCTURAL = {"Tab Break", "Section Break", "Column Break", "Fold", "Heading", "Button", "HTML", "Image", "Table", "Table MultiSelect"}
GENERIC_FIELDS = {"name", "title", "status", "company", "naming_series", "amended_from", "disabled", "description", "notes", "remarks", "idx", "owner", "creation", "modified", "date", "amount", "remark", "reason", "type", "category"}
COPY_FWD_EXCLUDE = {
    "Company", "Cost Center", "Project", "User", "Employee", "Account", "Currency", "DocType",
    "Mode of Payment", "Supplier", "Customer", "Item", "Warehouse", "Department", "Branch",
    "Address", "Contact", "party_type", "reference_doctype",
}
NEVER_FETCH = {"amended_from"}
_PRIOR_PREFIXES = ("previous_", "prev_", "old_", "original_", "source_")
_PRIOR_SUFFIXES = ("_previous", "_prev", "_old", "_from")


def _is_prior(fieldname: str | None) -> bool:
    if not fieldname:
        return False
    return fieldname.startswith(_PRIOR_PREFIXES) or fieldname.endswith(_PRIOR_SUFFIXES)
FRAMEWORK_DOCTYPES = {
    "User", "Role", "Company", "Cost Center", "Account", "Item", "Customer", "Supplier",
    "Employee", "Department", "Designation", "Project", "Task", "Address", "Contact", "Currency",
    "UOM", "Warehouse", "Workflow", "Workflow State", "Workflow Action Master", "DocType", "File",
    "Print Format", "Letter Head", "Territory", "Brand", "Item Group", "Customer Group",
    "Supplier Group", "Mode of Payment", "Holiday List", "Fiscal Year", "Payment Term",
    "Terms and Conditions", "Email Template", "Notification", "Report", "Bank Account", "Branch",
    "Country", "Purchase Invoice", "Sales Invoice", "Purchase Order", "Sales Order", "Journal Entry",
    "Payment Entry", "GL Entry", "Asset", "Serial No", "Batch", "Stock Entry", "Delivery Note",
    "Material Request", "Expense Claim", "Leave Application", "Attendance", "Salary Slip", "Shift Type",
    "Employee Advance", "Vehicle", "Driver", "Location", "Activity Type", "Operation", "Workstation",
    "Quotation", "Lead", "Opportunity", "Tax Category", "Finance Book", "Accounting Dimension",
    "Asset Movement", "Additional Salary", "Salary Component", "Salary Structure", "Leave Type",
    "Vehicle Log", "Timesheet", "Salary Structure Assignment", "Payroll Entry", "Asset Category",
}


def _walk(package_path: Path):
    for p in package_path.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def load_doctypes(package_path: Path) -> dict:
    out: dict = {}
    for p in package_path.glob("**/doctype/*/*.json"):
        if p.stem != p.parent.name or any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if data.get("doctype") != "DocType":
            continue
        name = data.get("name") or p.stem
        fields = data.get("fields", []) or []
        links = [
            (f.get("fieldname"), f.get("options"), bool(f.get("reqd")), bool(f.get("fetch_from")))
            for f in fields if f.get("fieldtype") in LINKISH
        ]
        out[name] = {"name": name, "module": data.get("module"), "path": p, "fields": fields, "links": links}
    return out


def code_tokens(package_path: Path) -> set:
    toks: set = set()
    word = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    for p in _walk(package_path):
        if not p.is_file() or p.suffix.lower() not in {".py", ".js", ".json", ".html", ".vue", ".md"}:
            continue
        is_doctype_def = (p.suffix.lower() == ".json" and p.stem == p.parent.name and p.parent.parent.name == "doctype")
        if is_doctype_def:
            continue
        try:
            toks.update(word.findall(p.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return toks


def _find_cycles(edges: dict) -> list:
    cycles, WHITE, GREY, BLACK = [], 0, 1, 2
    color = {n: WHITE for n in edges}
    stack: list = []
    seen = set()

    def dfs(n):
        color[n] = GREY
        stack.append(n)
        for m in edges.get(n, []):
            if color.get(m, BLACK) == GREY:
                cyc = stack[stack.index(m):]
                key = tuple(sorted(cyc))
                if key not in seen:
                    seen.add(key)
                    cycles.append(cyc + [m])
            elif color.get(m, WHITE) == WHITE:
                dfs(m)
        stack.pop()
        color[n] = BLACK

    for n in list(edges):
        if color[n] == WHITE:
            dfs(n)
    return cycles


def detect_loops(dts: dict, tokens: set) -> list:
    out = []
    req_edges = {n: [t for (_f, t, reqd, _ff) in d["links"] if reqd and t in dts] for n, d in dts.items()}
    for cyc in _find_cycles(req_edges):
        out.append({"kind": "reqd-link-cycle", "severity": "high", "cycle": cyc,
                    "why": "each link is required, so none of these doctypes can be created first"})
    seen_pairs = set()
    for n, d in dts.items():
        for (f, t, _reqd, _ff) in d["links"]:
            if t not in dts:
                continue
            back = [bf for (bf, bt, _r, _x) in dts[t]["links"] if bt == n]
            if not back:
                continue
            pair = tuple(sorted((f"{n}.{f}", f"{t}.{back[0]}")))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            unread = [side for side in ((n, f), (t, back[0])) if side[1] not in tokens]
            if not unread:
                continue
            out.append({"kind": "mutual-link-ring", "severity": "medium",
                        "a": f"{n}.{f}", "b": f"{t}.{back[0]}",
                        "unread_backlink": [f"{s[0]}.{s[1]}" for s in unread],
                        "why": "two doctypes Link each other and a back-link is read by NOTHING — a stamp no one consumes (a ring, not a tree)"})
    return out


def _fetch_roots(d: dict) -> set:
    roots = set()
    for f in d["fields"]:
        ff = f.get("fetch_from")
        if ff and "." in ff:
            roots.add(ff.split(".", 1)[0])
    return roots


def _backlink_roots(src: dict, target_doctype: str) -> set:
    roots = set()
    for f in src["fields"]:
        if f.get("fieldtype") in LINKISH and f.get("options") == target_doctype:
            ff = f.get("fetch_from")
            if ff and "." in ff:
                roots.add(ff.split(".", 1)[0])
    return roots


def detect_fetch_from(dts: dict) -> list:
    out = []
    seen_cf: set = set()
    for n, d in dts.items():
        links = d["links"]
        n_roots = _fetch_roots(d)
        for (lf, a, _r, _ff) in links:
            if a not in dts or a == n:
                continue
            a_pref: dict = {}
            for (af, t, ar, _x2) in dts[a]["links"]:
                if not t:
                    continue
                cand = (af, ar)
                cur = a_pref.get(t)
                if cur is None or (
                    (not _is_prior(af), bool(ar)) > (not _is_prior(cur[0]), bool(cur[1]))
                ):
                    a_pref[t] = cand
            for (mf, x, mf_reqd, ffm) in links:
                if mf == lf or ffm or not x or x in COPY_FWD_EXCLUDE or x not in a_pref:
                    continue
                if (n, mf) in seen_cf:
                    continue
                src_field, src_reqd = a_pref[x]
                if mf in NEVER_FETCH or src_field in NEVER_FETCH:
                    continue
                if _is_prior(mf):
                    continue
                if _is_prior(src_field):
                    continue
                if mf_reqd and not src_reqd:
                    continue
                if mf in n_roots:
                    continue
                if mf in _backlink_roots(dts[a], n):
                    continue
                seen_cf.add((n, mf))
                out.append({"kind": "copy-forward", "severity": "high", "doctype": n, "field": mf,
                            "target": x, "via": lf, "source": a,
                            "fetch": f"{lf}.{src_field}", "fetch_from": f"{lf}.{src_field}",
                            "fetch_if_empty": 1,
                            "why": f"{n}.{mf} re-selects {x}, which its own {lf} ({a}) already holds"})
    fetched, manual = {}, {}
    for n, d in dts.items():
        for f in d["fields"]:
            fn = f.get("fieldname")
            if not fn or fn in GENERIC_FIELDS:
                continue
            (fetched if f.get("fetch_from") else manual).setdefault(fn, []).append(n)
    for fn in sorted(set(fetched) & set(manual)):
        out.append({"kind": "late-normalization", "severity": "medium", "field": fn,
                    "fetched_on": fetched[fn][:4], "manual_on": manual[fn][:4],
                    "why": "derives via fetch_from on some doctypes but is hand-entered on others — the manual ones are the un-normalized layer"})
    return out


def detect_dead_and_invalid(dts: dict, tokens: set) -> list:
    out = []
    for n, d in dts.items():
        for f in d["fields"]:
            ft, fn = f.get("fieldtype"), f.get("fieldname")
            if not fn or ft in STRUCTURAL:
                continue
            if ft == "Link":
                t = f.get("options")
                if t and t not in dts and t not in FRAMEWORK_DOCTYPES and str(t).strip() == str(t) and "\n" not in str(t):
                    out.append({"kind": "invalid-link-target", "severity": "medium",
                                "doctype": n, "field": fn, "target": t,
                                "why": f"Link options '{t}' is not a DocType in this app or the known framework set — verify it exists in an installed app"})
            if (f.get("hidden") or f.get("read_only")) and fn not in tokens and not f.get("fetch_from"):
                out.append({"kind": "dead-field", "severity": "low", "doctype": n, "field": fn, "fieldtype": ft,
                            "why": "hidden/read-only and read by nothing — a field with no consumer"})
    return out


def audit(package_path: Path) -> dict:
    dts = load_doctypes(package_path)
    tokens = code_tokens(package_path)
    findings = detect_loops(dts, tokens) + detect_fetch_from(dts) + detect_dead_and_invalid(dts, tokens)
    return {"doctypes": len(dts), "findings": findings}


_ORDER = {"high": 0, "medium": 1, "low": 2}


def render(result: dict, only: str | None = None) -> str:
    findings = result["findings"]
    if only:
        findings = [f for f in findings if f["kind"] == only or only in f["kind"]]
    findings = sorted(findings, key=lambda f: (_ORDER.get(f.get("severity"), 9), f["kind"]))
    by_kind: dict = {}
    for f in findings:
        by_kind.setdefault(f["kind"], []).append(f)
    head = f"model-audit: {result['doctypes']} DocTypes · {len(findings)} finding(s)"
    counts = " · ".join(f"{k}={len(v)}" for k, v in sorted(by_kind.items()))
    lines = [head, counts, ""]
    labels = {
        "reqd-link-cycle": "CREATION DEADLOCK — required-Link cycle (can't create any of these first)",
        "mutual-link-ring": "RING — two doctypes Link each other (unread back-link = a stamp nobody reads)",
        "copy-forward": "COPY-FORWARD — one fact re-typed manually on 3+ records (needs fetch_from)",
        "late-normalization": "LATE NORMALIZATION — field fetched on some doctypes, manual on others",
        "invalid-link-target": "INVALID LINK TARGET — options points at no real DocType",
        "dead-field": "DEAD FIELD — defined but read by nothing",
    }
    for kind in sorted(by_kind, key=lambda k: _ORDER.get(by_kind[k][0].get("severity"), 9)):
        lines.append(f"▌{labels.get(kind, kind)}")
        for f in by_kind[kind]:
            if kind == "reqd-link-cycle":
                lines.append("  - " + " → ".join(f["cycle"]))
            elif kind == "mutual-link-ring":
                tag = f"  (unread: {', '.join(f['unread_backlink'])})" if f["unread_backlink"] else ""
                lines.append(f"  - {f['a']}  ⇄  {f['b']}{tag}")
            elif kind == "copy-forward":
                lines.append(f"  - {f['doctype']}.{f['field']} (→{f['target']})  ⇐ fetch_from {f['fetch']} + fetch_if_empty:1  [its own {f['via']} already holds it]")
            elif kind == "late-normalization":
                lines.append(f"  - {f['field']}: fetched on {f['fetched_on']} · manual on {f['manual_on']}")
            elif kind == "invalid-link-target":
                lines.append(f"  - {f['doctype']}.{f['field']} → '{f['target']}' (no such DocType)")
            elif kind == "dead-field":
                lines.append(f"  - {f['doctype']}.{f['field']} [{f['fieldtype']}]")
        lines.append("")
    if not findings:
        lines.append("clean — no model-integrity findings.")
    return "\n".join(lines).rstrip()


def resolve_package(root: str | None, package: str | None) -> Path:
    """The app package directory whose DocType JSON is read."""
    if package:
        path = Path(package).expanduser().resolve()
        if not path.is_dir():
            raise SystemExit(f"--package is not a directory: {path}")
        return path
    try:
        from ctlkit.config import discover_config
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from ctlkit.config import discover_config
    return discover_config(root or ".").package_path


def _refuse_writing_into_the_audited_app(out: Path, package: Path) -> None:
    audited = package.parent if package.parent != package else package
    if out == audited or audited in out.parents or package in out.parents:
        raise SystemExit(
            f"--out would write the report into the audited app at {audited}; "
            "model-audit reports on a repository and never writes one."
        )


def run(root: str | None = None, package: str | None = None, only: str | None = None,
        as_json: bool = False, out: str | None = None) -> int:
    package_path = resolve_package(root, package)
    result = audit(package_path)
    result["package"] = str(package_path)
    if as_json:
        if only:
            result = dict(result, findings=[f for f in result["findings"]
                                            if f["kind"] == only or only in f["kind"]])
        text = json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
    else:
        text = render(result, only=only)
    if out:
        target = Path(out).expanduser().resolve()
        _refuse_writing_into_the_audited_app(target, package_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
        print(f"report={target}")
    else:
        print(text)
    return 0


def add_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--root", default=".", help="Frappe bench or project root")
    parser.add_argument("--package", default=None,
                        help="Audit this app package directory instead of discovering it")
    parser.add_argument("--only", default=None, metavar="KIND",
                        help="Report one finding kind: dead-field, invalid-link-target, "
                             "reqd-link-cycle, mutual-link-ring, copy-forward, late-normalization")
    parser.add_argument("--json", action="store_true", help="Print machine JSON")
    parser.add_argument("--out", default=None, metavar="FILE",
                        help="Write the report to FILE; refused inside the audited app")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = add_arguments(argparse.ArgumentParser(
        prog="model-audit",
        description="Read an app's shipped DocType JSON and report model-integrity findings; "
                    "writes nothing to the app and needs no bench.",
    ))
    args = parser.parse_args(argv)
    return run(root=args.root, package=args.package, only=args.only,
               as_json=args.json, out=args.out)


if __name__ == "__main__":
    raise SystemExit(main())
