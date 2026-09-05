#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

from __future__ import annotations

import json
import os
import tomllib
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

LAYOUT_FIELDS = {"Section Break", "Column Break", "Tab Break", "HTML", "Heading", "Fold"}
TABLE_FIELDS = {"Table", "Table MultiSelect"}
RECORD_KEYS = {"ref", "doctype", "match", "workflow", "submit", "as_user", "values", "rows"}
SEED_KEYS = {"title", "description"}
REFUSED_SEED_KEYS = {"site", "bench", "bench_path", "sites_path"}


class SeedError(Exception):
    pass


@dataclass
class RecordSpec:
    ref: str
    doctype: str
    values: dict[str, object]
    rows: dict[str, list[dict[str, object]]]
    match: list[str]
    workflow: list[str]
    submit: bool
    as_user: str | None
    index: int


@dataclass
class Finding:
    severity: str
    ref: str
    doctype: str
    fieldname: str
    message: str

    def line(self) -> str:
        where = f"{self.doctype}.{self.fieldname}" if self.fieldname else self.doctype
        return f"  {self.severity.upper():<8} {self.ref:<16} {where:<44} {self.message}"

    def compact(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "ref": self.ref,
            "doctype": self.doctype,
            "fieldname": self.fieldname,
            "message": self.message,
        }


@dataclass
class RecordOutcome:
    ref: str
    doctype: str
    status: str
    name: str = ""
    note: str = ""
    message: str = ""
    error_type: str = ""
    fieldname: str = ""
    workflow_from: str = ""
    workflow_to: str = ""

    def line(self) -> str:
        parts = [f"  {self.status:<10} {self.doctype:<30} {self.ref:<16} {self.name or '-'}"]
        if self.workflow_to:
            parts.append(f"workflow: {self.workflow_from or '-'} -> {self.workflow_to}")
        if self.note:
            parts.append(self.note)
        if self.message:
            where = f"{self.doctype}.{self.fieldname}" if self.fieldname else self.doctype
            parts.append(f"{self.error_type} on {where}: {self.message}")
        return "  ".join(parts)

    def compact(self) -> dict[str, str]:
        return {
            "ref": self.ref,
            "doctype": self.doctype,
            "status": self.status,
            "name": self.name,
            "note": self.note,
            "error_type": self.error_type,
            "fieldname": self.fieldname,
            "message": self.message,
            "workflow_from": self.workflow_from,
            "workflow_to": self.workflow_to,
        }


@dataclass
class SeedResult:
    seed_file: Path
    site: str
    bench_path: str
    schema_roots: list[str]
    mode: str
    title: str = ""
    findings: list[Finding] = field(default_factory=list)
    outcomes: list[RecordOutcome] = field(default_factory=list)
    site_checked: bool = False
    site_note: str = ""

    def blockers(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "blocker"]

    def counts(self) -> dict[str, int]:
        tally: dict[str, int] = {}
        for outcome in self.outcomes:
            tally[outcome.status] = tally.get(outcome.status, 0) + 1
        return tally

    def compact(self) -> dict[str, object]:
        return {
            "seed_file": str(self.seed_file),
            "site": self.site,
            "bench_path": self.bench_path,
            "schema_roots": self.schema_roots,
            "mode": self.mode,
            "title": self.title,
            "site_checked": self.site_checked,
            "site_note": self.site_note,
            "findings": [item.compact() for item in self.findings],
            "outcomes": [item.compact() for item in self.outcomes],
            "counts": self.counts(),
        }


def parse_seed_file(path: Path) -> tuple[str, list[RecordSpec]]:
    if not path.is_file():
        raise SeedError(f"no seed file at {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise SeedError(f"{path}: {exc}") from exc

    header = data.get("seed", {})
    if not isinstance(header, dict):
        raise SeedError(f"{path}: [seed] must be a table")
    named_here = sorted(REFUSED_SEED_KEYS & set(header))
    if named_here:
        raise SeedError(
            f"{path}: [seed] names {', '.join(named_here)}. The bench and the site come from "
            ".ctl.toml so there is one source of truth; remove the key."
        )
    unknown_header = sorted(set(header) - SEED_KEYS)
    if unknown_header:
        raise SeedError(f"{path}: [seed] has unknown key(s): {', '.join(unknown_header)}")

    raw_records = data.get("record", [])
    if not isinstance(raw_records, list) or not raw_records:
        raise SeedError(f"{path}: no [[record]] entries")

    specs: list[RecordSpec] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_records):
        if not isinstance(raw, dict):
            raise SeedError(f"{path}: [[record]] #{index + 1} is not a table")
        unknown = sorted(set(raw) - RECORD_KEYS)
        if unknown:
            raise SeedError(
                f"{path}: [[record]] #{index + 1} has unknown key(s): {', '.join(unknown)}. "
                f"Known keys are {', '.join(sorted(RECORD_KEYS))}."
            )
        doctype = str(raw.get("doctype") or "").strip()
        if not doctype:
            raise SeedError(f"{path}: [[record]] #{index + 1} has no doctype")
        ref = str(raw.get("ref") or "").strip()
        if not ref:
            raise SeedError(f"{path}: [[record]] #{index + 1} ({doctype}) has no ref")
        if ref in seen:
            raise SeedError(f"{path}: ref {ref!r} is used twice")
        seen.add(ref)
        values = raw.get("values", {})
        if not isinstance(values, dict):
            raise SeedError(f"{path}: [record.values] for {ref!r} must be a table")
        rows_raw = raw.get("rows", {})
        if not isinstance(rows_raw, dict):
            raise SeedError(f"{path}: [record.rows] for {ref!r} must be a table of arrays")
        rows: dict[str, list[dict[str, object]]] = {}
        for table, entries in rows_raw.items():
            if not isinstance(entries, list) or not all(isinstance(one, dict) for one in entries):
                raise SeedError(f"{path}: rows.{table} for {ref!r} must be an array of tables")
            rows[table] = list(entries)
        match = raw.get("match", [])
        if isinstance(match, str):
            match = [match]
        if not isinstance(match, list) or not all(isinstance(one, str) for one in match):
            raise SeedError(f"{path}: match for {ref!r} must be a list of fieldnames")
        workflow = raw.get("workflow", [])
        if isinstance(workflow, str):
            workflow = [workflow]
        if not isinstance(workflow, list) or not all(isinstance(one, str) for one in workflow):
            raise SeedError(f"{path}: workflow for {ref!r} must be a list of action names")
        submit = raw.get("submit", False)
        if not isinstance(submit, bool):
            raise SeedError(f"{path}: submit for {ref!r} must be true or false")
        if submit and workflow:
            raise SeedError(
                f"{path}: {ref!r} sets both submit and workflow. A governed document is advanced "
                "by its workflow actions; submit would bypass the transition."
            )
        as_user = raw.get("as_user")
        specs.append(
            RecordSpec(
                ref=ref,
                doctype=doctype,
                values=dict(values),
                rows=rows,
                match=list(match),
                workflow=list(workflow),
                submit=submit,
                as_user=str(as_user) if as_user else None,
                index=index,
            )
        )
    return str(header.get("title") or path.stem), specs


def _schema_roots(config) -> list[Path]:
    roots = [Path(config.package_path)]
    bench = getattr(config, "bench_path", None)
    apps = Path(bench) / "apps" if bench else None
    if apps and apps.is_dir():
        roots.append(apps)
    return roots


def doctype_index(roots: Iterable[Path]) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*/doctype/*/*.json"):
            if path.stem != path.parent.name or "node_modules" in path.parts:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if data.get("doctype") != "DocType" and "fields" not in data:
                continue
            index.setdefault(str(data.get("name") or path.stem), path)
    return index


def _reached_by(transitions: list[dict]) -> dict[str, list[str]]:
    landings: dict[str, list[str]] = {}
    for one in transitions:
        action = str(one.get("action") or "")
        target = str(one.get("next_state") or "")
        if action and target and target not in landings.setdefault(action, []):
            landings[action].append(target)
    return landings


def workflow_index(roots: Iterable[Path]) -> dict[str, dict[str, object]]:
    index: dict[str, dict[str, object]] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*/workflow/*/*.json"):
            if path.stem != path.parent.name or "node_modules" in path.parts:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if data.get("doctype") != "Workflow" or not data.get("is_active"):
                continue
            doctype = str(data.get("document_type") or "")
            if not doctype:
                continue
            index.setdefault(doctype, {
                "name": data.get("name"),
                "state_field": data.get("workflow_state_field"),
                "actions": sorted({str(one.get("action")) for one in data.get("transitions", [])}),
                "states": [str(one.get("state")) for one in data.get("states", [])],
                "reached_by": _reached_by(data.get("transitions", [])),
            })
    return index


_META_CACHE: dict[str, dict[str, object]] = {}


def read_doctype(index: dict[str, Path], doctype: str) -> dict[str, object] | None:
    if doctype in _META_CACHE:
        return _META_CACHE[doctype]
    path = index.get(doctype)
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    fields = {}
    for one in data.get("fields", []):
        if one.get("fieldtype") in LAYOUT_FIELDS:
            continue
        fields[str(one.get("fieldname"))] = one
    meta = {
        "name": data.get("name", doctype),
        "autoname": data.get("autoname") or "",
        "istable": bool(data.get("istable")),
        "is_submittable": bool(data.get("is_submittable")),
        "fields": fields,
    }
    _META_CACHE[doctype] = meta
    return meta


def select_options(spec: dict) -> list[str]:
    return [one.strip() for one in str(spec.get("options") or "").split("\n")]


def is_reference(value: object) -> bool:
    return isinstance(value, str) and value.startswith("@") and not value.startswith("@@")


def reference_name(value: str) -> str:
    return value[1:]


def literal(value: object) -> object:
    if isinstance(value, str) and value.startswith("@@"):
        return value[1:]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def resolve_value(value: object, refs: dict[str, str], ref: str, fieldname: str) -> object:
    if is_reference(value):
        target = reference_name(str(value))
        if target not in refs:
            raise SeedError(f"{ref}.{fieldname} refers to @{target}, which no earlier record defines")
        return refs[target]
    return literal(value)


def match_fields(spec: RecordSpec, meta: dict[str, object] | None) -> list[str]:
    if spec.match:
        return spec.match
    if "name" in spec.values:
        return ["name"]
    autoname = str((meta or {}).get("autoname") or "")
    if autoname.startswith("field:"):
        derived = autoname.split(":", 1)[1].strip()
        if derived in spec.values:
            return [derived]
    return []


def check_static(specs: list[RecordSpec], index: dict[str, Path],
                 workflows: dict[str, dict[str, object]] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    known_refs: dict[str, str] = {}
    workflows = workflows or {}

    def add(severity: str, spec: RecordSpec, fieldname: str, message: str) -> None:
        findings.append(Finding(severity, spec.ref, spec.doctype, fieldname, message))

    for spec in specs:
        meta = read_doctype(index, spec.doctype)
        if meta is None:
            add("blocker", spec, "", f"no DocType named {spec.doctype!r} in any shipped JSON")
            known_refs[spec.ref] = spec.doctype
            continue
        fields = meta["fields"]
        governing = workflows.get(spec.doctype)
        if spec.submit and not meta["is_submittable"]:
            add("blocker", spec, "", f"{spec.doctype} is not submittable, so submit does nothing")
        if spec.submit and governing:
            add("blocker", spec, "",
                f"{governing['name']} governs {spec.doctype}: advance it with "
                f"workflow = [...] rather than submit")
        if spec.workflow and not governing:
            add("blocker", spec, "", f"no shipped active Workflow governs {spec.doctype}")
        for action in spec.workflow:
            if governing and action not in governing["actions"]:
                add("blocker", spec, "",
                    f"{governing['name']} has no action {action!r}; it offers "
                    + " | ".join(str(one) for one in governing["actions"]))
        state_field = str((governing or {}).get("state_field") or "")
        if state_field and state_field in spec.values:
            add("blocker", spec, state_field,
                f"is the workflow state field of {governing['name']}; set it with "
                "workflow = [...] instead of writing the state")
        keys = match_fields(spec, meta)
        if not keys:
            add(
                "blocker", spec, "",
                "no match keys: declare match = [...] or set the autoname field, otherwise a "
                "re-run cannot tell whether this record already exists",
            )
        for key in keys:
            if key != "name" and key not in spec.values:
                add("blocker", spec, key, "named in match but never set")

        for fieldname, value in spec.values.items():
            if fieldname == "name":
                continue
            spec_field = fields.get(fieldname)
            if spec_field is None:
                add("blocker", spec, fieldname, f"{spec.doctype} has no such field")
                continue
            fieldtype = str(spec_field.get("fieldtype") or "")
            if fieldtype in TABLE_FIELDS:
                add(
                    "blocker", spec, fieldname,
                    f"{fieldtype} field set in [record.values]; child rows belong in "
                    f"[[record.rows.{fieldname}]]",
                )
                continue
            findings.extend(_check_scalar(spec, fieldname, value, spec_field, index, known_refs))

        for table, entries in spec.rows.items():
            table_field = fields.get(table)
            if table_field is None:
                add("blocker", spec, table, f"{spec.doctype} has no such field")
                continue
            if str(table_field.get("fieldtype")) not in TABLE_FIELDS:
                add("blocker", spec, table, f"is a {table_field.get('fieldtype')}, not a child table")
                continue
            child_name = str(table_field.get("options") or "")
            child_meta = read_doctype(index, child_name)
            if child_meta is None:
                add("blocker", spec, table, f"child table {child_name!r} is not in any shipped JSON")
                continue
            for position, row in enumerate(entries, start=1):
                for fieldname, value in row.items():
                    child_field = child_meta["fields"].get(fieldname)
                    if child_field is None:
                        add("blocker", spec, f"{table}[{position}].{fieldname}",
                            f"{child_name} has no such field")
                        continue
                    findings.extend(
                        _check_scalar(spec, f"{table}[{position}].{fieldname}", value,
                                      child_field, index, known_refs)
                    )
                for fieldname, child_field in child_meta["fields"].items():
                    if child_field.get("reqd") and fieldname not in row and not child_field.get("default"):
                        add("warning", spec, f"{table}[{position}].{fieldname}",
                            "mandatory on the child row and not set")

        for fieldname, spec_field in fields.items():
            if not spec_field.get("reqd") or fieldname in spec.values:
                continue
            if spec_field.get("default") or str(spec_field.get("fieldtype")) in TABLE_FIELDS:
                continue
            add("warning", spec, fieldname,
                "mandatory and not set — the controller must fill it or the insert will be refused")

        known_refs[spec.ref] = spec.doctype
    return findings


def _check_scalar(spec: RecordSpec, fieldname: str, value: object, spec_field: dict,
                  index: dict[str, Path], known_refs: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    fieldtype = str(spec_field.get("fieldtype") or "")

    if is_reference(value):
        target = reference_name(str(value))
        if target not in known_refs:
            findings.append(Finding("blocker", spec.ref, spec.doctype, fieldname,
                                    f"refers to @{target}, which no earlier record defines"))
            return findings
        if fieldtype == "Link":
            wanted = str(spec_field.get("options") or "")
            if known_refs[target] != wanted:
                findings.append(Finding(
                    "blocker", spec.ref, spec.doctype, fieldname,
                    f"links to {wanted} but @{target} is a {known_refs[target]}"))
        elif fieldtype not in {"Dynamic Link", "Data", "Small Text", "Text"}:
            findings.append(Finding("warning", spec.ref, spec.doctype, fieldname,
                                    f"is a {fieldtype}; a @ref resolves to a record name"))
        return findings

    plain = literal(value)
    if fieldtype == "Select":
        allowed = select_options(spec_field)
        if allowed and str(plain) not in allowed:
            findings.append(Finding(
                "blocker", spec.ref, spec.doctype, fieldname,
                f"{plain!r} is not one of: " + " | ".join(one for one in allowed if one)))
    elif fieldtype == "Link":
        target = str(spec_field.get("options") or "")
        if not target:
            findings.append(Finding("blocker", spec.ref, spec.doctype, fieldname,
                                    "is a Link with no target DocType in its JSON"))
        elif read_doctype(index, target) is None:
            findings.append(Finding("blocker", spec.ref, spec.doctype, fieldname,
                                    f"links to {target!r}, which is not in any shipped JSON"))
    elif fieldtype == "Dynamic Link":
        holder = str(spec_field.get("options") or "")
        named = spec.values.get(holder)
        if isinstance(named, str) and named and read_doctype(index, named) is None:
            findings.append(Finding("blocker", spec.ref, spec.doctype, fieldname,
                                    f"{holder} names {named!r}, which is not in any shipped JSON"))
    return findings


def _link_targets(specs: list[RecordSpec], index: dict[str, Path]) -> list[tuple[RecordSpec, str, str, str]]:
    wanted: list[tuple[RecordSpec, str, str, str]] = []
    for spec in specs:
        meta = read_doctype(index, spec.doctype)
        if meta is None:
            continue
        for fieldname, value in spec.values.items():
            spec_field = meta["fields"].get(fieldname)
            if not spec_field or is_reference(value):
                continue
            if str(spec_field.get("fieldtype")) == "Link" and spec_field.get("options"):
                wanted.append((spec, fieldname, str(spec_field["options"]), str(literal(value))))
        for table, entries in spec.rows.items():
            table_field = meta["fields"].get(table)
            if not table_field:
                continue
            child_meta = read_doctype(index, str(table_field.get("options") or ""))
            if child_meta is None:
                continue
            for position, row in enumerate(entries, start=1):
                for fieldname, value in row.items():
                    child_field = child_meta["fields"].get(fieldname)
                    if not child_field or is_reference(value):
                        continue
                    if str(child_field.get("fieldtype")) == "Link" and child_field.get("options"):
                        wanted.append((spec, f"{table}[{position}].{fieldname}",
                                       str(child_field["options"]), str(literal(value))))
    return wanted


def _connect(config, site: str) -> tuple[object, bool]:
    import frappe

    if getattr(frappe.local, "initialised", False):
        current = getattr(frappe.local, "site", "")
        if current and current != site:
            raise SeedError(
                f"already connected to {current}, but .ctl.toml names {site}. "
                "One site per run."
            )
        return frappe, False

    sites = Path(config.bench_path) / "sites"
    os.chdir(sites)
    frappe.init(site=site, sites_path=str(sites))
    frappe.connect()
    frappe.set_user("Administrator")
    return frappe, True


def check_links_on_site(config, site: str, specs: list[RecordSpec],
                        index: dict[str, Path]) -> tuple[list[Finding], str]:
    wanted = _link_targets(specs, index)
    if not wanted:
        return [], "no literal Link values to resolve"
    try:
        frappe, owned = _connect(config, site)
    except Exception as exc:
        return [], f"site not reachable ({type(exc).__name__}: {exc}); shipped-JSON pass only"
    findings: list[Finding] = []
    try:
        for spec, fieldname, target, value in wanted:
            if not value:
                continue
            if not frappe.db.exists(target, value):
                findings.append(Finding("blocker", spec.ref, spec.doctype, fieldname,
                                        f"no {target} named {value!r} on {site}"))
    finally:
        if owned:
            frappe.db.rollback()
            frappe.destroy()
    return findings, f"resolved {len(wanted)} literal Link value(s) against {site}"


def _payload(spec: RecordSpec, refs: dict[str, str]) -> dict[str, object]:
    payload: dict[str, object] = {"doctype": spec.doctype}
    for fieldname, value in spec.values.items():
        payload[fieldname] = resolve_value(value, refs, spec.ref, fieldname)
    for table, entries in spec.rows.items():
        payload[table] = [
            {key: resolve_value(value, refs, spec.ref, f"{table}.{key}") for key, value in row.items()}
            for row in entries
        ]
    return payload


def _existing_name(frappe, spec: RecordSpec, payload: dict[str, object], keys: list[str]) -> str:
    if keys == ["name"]:
        return frappe.db.exists(spec.doctype, str(payload.get("name") or "")) or ""
    filters = {key: payload.get(key) for key in keys}
    return frappe.db.exists(spec.doctype, filters) or ""


def _workflow_state(frappe, doctype: str, name: str) -> tuple[str, str]:
    from frappe.model.workflow import get_workflow_name

    workflow = get_workflow_name(doctype)
    if not workflow:
        return "", ""
    stateful = frappe.get_cached_value("Workflow", workflow, "workflow_state_field")
    if not stateful:
        return "", ""
    return stateful, str(frappe.db.get_value(doctype, name, stateful) or "")


def _framework_message(frappe, exc: Exception) -> tuple[str, str]:
    spoken = [str(one.get("message") or "") for one in frappe.get_message_log()]
    text = str(exc).strip()
    for one in spoken:
        cleaned = frappe.utils.strip_html(one).strip()
        if cleaned and cleaned not in text:
            text = f"{text} | {cleaned}" if text else cleaned
    fieldname = ""
    if isinstance(exc, frappe.MandatoryError) and "]:" in str(exc):
        fieldname = str(exc).split("]:", 1)[1].strip()
    return text or type(exc).__name__, fieldname


def _expected_states(spec: RecordSpec, workflows: dict[str, dict[str, object]]) -> list[str]:
    if not spec.workflow:
        return []
    governing = workflows.get(spec.doctype) or {}
    return list(governing.get("reached_by", {}).get(spec.workflow[-1], []))


def apply_seed(config, site: str, specs: list[RecordSpec], index: dict[str, Path],
               workflows: dict[str, dict[str, object]] | None = None) -> list[RecordOutcome]:
    from frappe.model.workflow import apply_workflow

    workflows = workflows or {}

    frappe, owned = _connect(config, site)
    outcomes: list[RecordOutcome] = []
    refs: dict[str, str] = {}
    try:
        for spec in specs:
            savepoint = f"ctl_seed_{spec.index}"
            frappe.db.savepoint(savepoint)
            frappe.clear_messages()
            if spec.as_user:
                frappe.set_user(spec.as_user)
            try:
                payload = _payload(spec, refs)
                keys = match_fields(spec, read_doctype(index, spec.doctype))
                if not keys:
                    raise SeedError("no match keys, so a re-run could not recognise this record")
                found = _existing_name(frappe, spec, payload, keys)
                if found:
                    refs[spec.ref] = found
                    stateful, state = _workflow_state(frappe, spec.doctype, found)
                    note = f"matched on {', '.join(keys)}"
                    if stateful:
                        note += f"; {stateful}={state}"
                        expected = _expected_states(spec, workflows)
                        if expected and state and state not in expected:
                            note += f" (this file ends at {' or '.join(expected)})"
                    outcomes.append(RecordOutcome(spec.ref, spec.doctype, "unchanged", found, note))
                    continue

                doc = frappe.get_doc(payload)
                doc.insert()
                _, before = _workflow_state(frappe, spec.doctype, doc.name)
                after = before
                for action in spec.workflow:
                    doc = apply_workflow(doc, action)
                    _, after = _workflow_state(frappe, spec.doctype, doc.name)
                if spec.submit:
                    doc.submit()
                refs[spec.ref] = doc.name
                frappe.db.commit()
                outcomes.append(RecordOutcome(
                    spec.ref, spec.doctype, "created", doc.name,
                    note=f"docstatus={doc.docstatus}" if spec.submit else "",
                    workflow_from=before if spec.workflow else "",
                    workflow_to=after if spec.workflow else "",
                ))
            except SeedError as exc:
                frappe.db.rollback(save_point=savepoint)
                outcomes.append(RecordOutcome(spec.ref, spec.doctype, "failed",
                                              error_type="SeedError", message=str(exc)))
            except Exception as exc:
                frappe.db.rollback(save_point=savepoint)
                message, fieldname = _framework_message(frappe, exc)
                outcomes.append(RecordOutcome(spec.ref, spec.doctype, "failed",
                                              error_type=type(exc).__name__,
                                              fieldname=fieldname, message=message))
            finally:
                if spec.as_user:
                    frappe.set_user("Administrator")
    finally:
        if owned:
            frappe.destroy()
    return outcomes


def render(result: SeedResult) -> str:
    lines = [
        f"seed   {result.seed_file}",
        f"title  {result.title}",
        f"site   {result.site}",
        f"bench  {result.bench_path}",
        f"schema {' + '.join(result.schema_roots)}",
        f"mode   {result.mode}",
        "",
    ]
    if result.mode == "dry-run":
        lines.append(f"shipped-JSON pass: {len(result.findings)} finding(s)")
        if result.site_note:
            lines.append(f"site pass: {result.site_note}")
        lines.append("")
        if not result.findings:
            lines.append("  every field, Select value and Link target resolves.")
        for finding in result.findings:
            lines.append(finding.line())
        lines.append("")
        blockers = len(result.blockers())
        warnings = len(result.findings) - blockers
        lines.append(f"blockers={blockers}  warnings={warnings}  records={len(result.outcomes) or 'n/a'}")
        return "\n".join(lines)

    for outcome in result.outcomes:
        lines.append(outcome.line())
    lines.append("")
    tally = result.counts()
    lines.append("  ".join(f"{key}={value}" for key, value in sorted(tally.items())) or "nothing to do")
    return "\n".join(lines)


def run(config, seed_file: Path, *, dry_run: bool = False, no_site: bool = False,
        as_json: bool = False) -> int:
    site = getattr(config, "site", None)
    if not site:
        raise SystemExit(
            "frappe-pipes seed: no site in .ctl.toml. Add [project].site so the bench and the site "
            "have one source of truth."
        )
    path = Path(seed_file).expanduser().resolve()
    try:
        title, specs = parse_seed_file(path)
    except SeedError as exc:
        raise SystemExit(f"frappe-pipes seed: {exc}") from exc

    roots = _schema_roots(config)
    index = doctype_index(roots)
    workflows = workflow_index(roots)
    result = SeedResult(
        seed_file=path,
        site=str(site),
        bench_path=str(config.bench_path),
        schema_roots=[str(one) for one in roots],
        mode="dry-run" if dry_run else "apply",
        title=title,
    )

    if dry_run:
        result.findings = check_static(specs, index, workflows)
        if no_site:
            result.site_note = "skipped (--no-site)"
        else:
            site_findings, note = check_links_on_site(config, str(site), specs, index)
            result.findings.extend(site_findings)
            result.site_checked = bool(site_findings) or note.startswith("resolved")
            result.site_note = note
        _emit(result, as_json)
        return 1 if result.blockers() else 0

    try:
        result.outcomes = apply_seed(config, str(site), specs, index, workflows)
    except SeedError as exc:
        raise SystemExit(f"frappe-pipes seed: {exc}") from exc
    _emit(result, as_json)
    return 1 if any(one.status == "failed" for one in result.outcomes) else 0


def _emit(result: SeedResult, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.compact(), ensure_ascii=False, separators=(",", ":")))
    else:
        print(render(result))
