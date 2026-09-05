# Copyright (c) 2026, iabodysa

from __future__ import annotations

import json
import re
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import seed_kit
from bench_source import DEFAULT_BENCH_ROOT

UNANSWERED = "ANSWER-ME"

FRAMEWORK_COLUMNS = frozenset({
    "doctype", "name", "owner", "creation", "modified", "modified_by", "docstatus", "idx",
    "parent", "parentfield", "parenttype",
    "_user_tags", "_comments", "_assign", "_liked_by", "_seen",
})

RESERVED_KEYWORDS = frozenset({
    "doctype", "meta", "flags", "parent_doc", "_table_fields", "_valid_columns",
    "_doc_before_save", "_table_fieldnames", "_reserved_keywords", "permitted_fieldnames",
    "dont_update_if_missing",
})

FIELDTYPES = frozenset({
    "Currency", "Int", "Long Int", "Float", "Percent", "Check", "Small Text", "Long Text",
    "Code", "Text Editor", "Markdown Editor", "HTML Editor", "Date", "Datetime", "Time",
    "Text", "Data", "Link", "Dynamic Link", "Password", "Select", "Rating", "Read Only",
    "Attach", "Attach Image", "Signature", "Color", "Barcode", "Geolocation", "Duration",
    "Icon", "Phone", "Autocomplete", "JSON",
    "Section Break", "Column Break", "Tab Break", "HTML", "Table", "Table MultiSelect",
    "Button", "Image", "Fold", "Heading",
})

LINK_FIELDTYPES = frozenset({"Link"})
TABLE_FIELDTYPES = frozenset({"Table", "Table MultiSelect"})
LAYOUT_FIELDTYPES = frozenset({
    "Section Break", "Column Break", "Tab Break", "HTML", "Button", "Image", "Fold", "Heading",
})

KINDS = frozenset({"ordinary", "single", "child"})
YES_NO = frozenset({"yes", "no"})
NAMING_ROUTES = ("field", "naming_series", "hash", "prompt", "format", "autoincrement")

MODULE_RECORD_DOCTYPES = frozenset({
    "Page", "Report", "Dashboard Chart Source", "Print Format", "Web Page", "Website Theme",
    "Web Form", "Web Template", "Notification", "Print Style", "Workspace", "Onboarding Step",
    "Module Onboarding", "Form Tour", "Client Script", "Server Script", "Custom Field",
    "Property Setter",
})

FIXTURE_ONLY_DOCTYPES = frozenset({
    "Workflow", "Dashboard Chart", "Number Card", "Kanban Board",
})

ONBOARDING_ACTIONS = frozenset({
    "Create Entry", "Update Settings", "Show Form Tour", "View Report", "Go to Page", "Watch Video",
})

LIST_FILTER_OPERATORS = frozenset({
    "=", "!=", ">", "<", ">=", "<=", "like", "not like", "in", "not in", "is", "between",
})

FIRST_RUN_RECORD_DOCTYPES = ("Workspace", "Onboarding Step", "Module Onboarding", "Form Tour")

DECLINED = "none"

APP_KEYS = frozenset({"name", "title", "publisher", "email", "description", "license", "modules"})
DOCTYPE_KEYS = frozenset({
    "name", "module", "kind", "submittable", "posts_ledger_entries", "naming",
    "naming_series_options", "title_field", "search_fields", "track_changes", "allow_rename",
    "is_tree", "field", "permission", "list_filter", "form_tour", "onboarding_step",
})
FIRST_RUN_KEYS = frozenset({
    "workspace", "module", "onboarding", "icon", "title", "subtitle", "success_message",
    "documentation_url", "allow_roles", "step",
})
FIRST_RUN_STEP_KEYS = frozenset({
    "name", "title", "action", "reference_document", "description", "form_tour",
})
LIST_FILTER_KEYS = frozenset({"fieldname", "operator", "value"})
FIELD_KEYS = frozenset({
    "fieldname", "fieldtype", "label", "options", "reqd", "unique", "in_list_view", "default",
    "read_only", "hidden",
})
PERMISSION_KEYS = frozenset({
    "role", "read", "write", "create", "delete", "submit", "cancel", "amend", "report",
    "export", "share", "print", "email", "permlevel",
})
RECORD_KEYS = frozenset({"doctype", "name", "module", "values"})

APP_IRREVERSIBLE = ("app.name", "app.modules")
FIRST_RUN_IRREVERSIBLE = ("first_run.workspace", "first_run.module", "first_run.onboarding")


def scrub(text: str) -> str:
    return text.replace(" ", "_").replace("-", "_").lower()


def classname(doctype: str) -> str:
    return doctype.replace(" ", "").replace("-", "")


def fresh_utc_stamp(now: datetime | None = None) -> str:
    base = now or datetime.now(timezone.utc)
    return base.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")


class PlanError(Exception):
    pass


@dataclass
class Refusal:
    key: str
    reason: str

    def line(self) -> str:
        return f"  REFUSED  {self.key:<44} {self.reason}"

    def compact(self) -> dict[str, str]:
        return {"key": self.key, "reason": self.reason}


@dataclass
class PlanField:
    fieldname: str
    fieldtype: str
    label: str = ""
    options: str = ""
    reqd: bool = False
    unique: bool = False
    in_list_view: bool = False
    default: str = ""
    read_only: bool = False
    hidden: bool = False


@dataclass
class PlanListFilter:
    fieldname: str
    operator: str
    value: str


@dataclass
class PlanDocType:
    name: str
    module: str
    kind: str
    submittable: str
    posts_ledger_entries: str
    naming: str
    naming_series_options: list[str] = field(default_factory=list)
    title_field: str = ""
    search_fields: str = ""
    track_changes: bool = True
    allow_rename: bool = True
    is_tree: bool = False
    form_tour: str = ""
    onboarding_step: str = ""
    fields: list[PlanField] = field(default_factory=list)
    permissions: list[dict[str, object]] = field(default_factory=list)
    list_filters: list[PlanListFilter] = field(default_factory=list)

    def tour_steps(self) -> list[PlanField]:
        return [one for one in self.fields
                if one.reqd and one.fieldname and one.fieldtype not in LAYOUT_FIELDTYPES]

    def targets(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for one in self.fields:
            if one.fieldtype in LINK_FIELDTYPES | TABLE_FIELDTYPES:
                out.append((one.fieldname, one.options))
        return out


@dataclass
class PlanRecord:
    doctype: str
    name: str
    module: str
    values: dict[str, object]


@dataclass
class PlanStep:
    name: str
    title: str
    action: str
    reference_document: str = ""
    description: str = ""
    form_tour: str = ""


@dataclass
class PlanFirstRun:
    declared: bool = False
    workspace: str = ""
    module: str = ""
    onboarding: str = ""
    icon: str = ""
    title: str = ""
    subtitle: str = ""
    success_message: str = ""
    documentation_url: str = ""
    allow_roles: list[str] = field(default_factory=list)
    steps: list[PlanStep] = field(default_factory=list)

    @property
    def wants_onboarding(self) -> bool:
        return bool(self.onboarding) and self.onboarding != DECLINED \
            and UNANSWERED not in self.onboarding


@dataclass
class Plan:
    path: Path
    app: dict[str, object]
    doctypes: list[PlanDocType]
    records: list[PlanRecord]
    hooks: dict[str, object]
    roles: list[str]
    first_run: PlanFirstRun = field(default_factory=PlanFirstRun)

    def step_names(self) -> list[tuple[str, str]]:
        out = [(f"first_run.step[{index}].name", step.name)
               for index, step in enumerate(self.first_run.steps)]
        out.extend((f"doctype[{doc.name}].onboarding_step", doc.onboarding_step)
                   for doc in self.doctypes if doc.onboarding_step)
        return out

    def tour_names(self) -> set[str]:
        return {doc.form_tour for doc in self.doctypes if doc.form_tour}

    @property
    def app_name(self) -> str:
        return str(self.app.get("name") or "")

    @property
    def modules(self) -> list[str]:
        raw = self.app.get("modules") or []
        return [str(one) for one in raw] if isinstance(raw, list) else []


def _as_bool(value: object, key: str, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise PlanError(f"{key} must be true or false")
    return value


def _as_str(value: object, key: str, default: str = "") -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise PlanError(f"{key} must be a string")
    return value


def _unknown(seen: Iterable[str], known: frozenset[str], key: str) -> None:
    extra = sorted(set(seen) - known)
    if extra:
        raise PlanError(f"{key} has unknown key(s): {', '.join(extra)}")


def parse_plan(path: Path) -> Plan:
    if not path.is_file():
        raise PlanError(f"no plan file at {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise PlanError(f"{path}: {exc}") from exc

    app = data.get("app")
    if not isinstance(app, dict):
        raise PlanError(f"{path}: no [app] table")
    _unknown(app, APP_KEYS, "[app]")

    raw_doctypes = data.get("doctype", [])
    if not isinstance(raw_doctypes, list):
        raise PlanError(f"{path}: [[doctype]] must be an array of tables")

    doctypes: list[PlanDocType] = []
    for index, raw in enumerate(raw_doctypes):
        if not isinstance(raw, dict):
            raise PlanError(f"{path}: [[doctype]] #{index + 1} is not a table")
        _unknown(raw, DOCTYPE_KEYS, f"[[doctype]] #{index + 1}")
        name = _as_str(raw.get("name"), f"doctype[{index}].name")
        if not name:
            raise PlanError(f"{path}: [[doctype]] #{index + 1} has no name")
        raw_fields = raw.get("field", [])
        if not isinstance(raw_fields, list):
            raise PlanError(f"{path}: [[doctype.field]] for {name!r} must be an array of tables")
        fields: list[PlanField] = []
        for position, one in enumerate(raw_fields):
            if not isinstance(one, dict):
                raise PlanError(f"{path}: [[doctype.field]] #{position + 1} of {name!r} is not a table")
            _unknown(one, FIELD_KEYS, f"[[doctype.field]] #{position + 1} of {name!r}")
            fields.append(PlanField(
                fieldname=_as_str(one.get("fieldname"), "fieldname"),
                fieldtype=_as_str(one.get("fieldtype"), "fieldtype"),
                label=_as_str(one.get("label"), "label"),
                options=_as_str(one.get("options"), "options"),
                reqd=_as_bool(one.get("reqd"), "reqd", False),
                unique=_as_bool(one.get("unique"), "unique", False),
                in_list_view=_as_bool(one.get("in_list_view"), "in_list_view", False),
                default=_as_str(one.get("default"), "default"),
                read_only=_as_bool(one.get("read_only"), "read_only", False),
                hidden=_as_bool(one.get("hidden"), "hidden", False),
            ))
        raw_perms = raw.get("permission", [])
        if not isinstance(raw_perms, list):
            raise PlanError(f"{path}: [[doctype.permission]] for {name!r} must be an array of tables")
        permissions: list[dict[str, object]] = []
        for position, one in enumerate(raw_perms):
            if not isinstance(one, dict):
                raise PlanError(f"{path}: [[doctype.permission]] #{position + 1} of {name!r} is not a table")
            _unknown(one, PERMISSION_KEYS, f"[[doctype.permission]] #{position + 1} of {name!r}")
            permissions.append(dict(one))
        raw_filters = raw.get("list_filter", [])
        if not isinstance(raw_filters, list):
            raise PlanError(f"{path}: [[doctype.list_filter]] for {name!r} must be an array of tables")
        list_filters: list[PlanListFilter] = []
        for position, one in enumerate(raw_filters):
            if not isinstance(one, dict):
                raise PlanError(f"{path}: [[doctype.list_filter]] #{position + 1} of {name!r} "
                                "is not a table")
            _unknown(one, LIST_FILTER_KEYS, f"[[doctype.list_filter]] #{position + 1} of {name!r}")
            list_filters.append(PlanListFilter(
                fieldname=_as_str(one.get("fieldname"), "list_filter.fieldname"),
                operator=_as_str(one.get("operator"), "list_filter.operator", "="),
                value=_as_str(one.get("value"), "list_filter.value"),
            ))
        options = raw.get("naming_series_options", [])
        if not isinstance(options, list):
            raise PlanError(f"{path}: naming_series_options for {name!r} must be a list")
        doctypes.append(PlanDocType(
            name=name,
            module=_as_str(raw.get("module"), "module"),
            kind=_as_str(raw.get("kind"), "kind"),
            submittable=_as_str(raw.get("submittable"), "submittable"),
            posts_ledger_entries=_as_str(raw.get("posts_ledger_entries"), "posts_ledger_entries"),
            naming=_as_str(raw.get("naming"), "naming"),
            naming_series_options=[str(one) for one in options],
            title_field=_as_str(raw.get("title_field"), "title_field"),
            search_fields=_as_str(raw.get("search_fields"), "search_fields"),
            track_changes=_as_bool(raw.get("track_changes"), "track_changes", True),
            allow_rename=_as_bool(raw.get("allow_rename"), "allow_rename", True),
            is_tree=_as_bool(raw.get("is_tree"), "is_tree", False),
            form_tour=_as_str(raw.get("form_tour"), "form_tour"),
            onboarding_step=_as_str(raw.get("onboarding_step"), "onboarding_step"),
            fields=fields,
            permissions=permissions,
            list_filters=list_filters,
        ))

    raw_records = data.get("record", [])
    if not isinstance(raw_records, list):
        raise PlanError(f"{path}: [[record]] must be an array of tables")
    records: list[PlanRecord] = []
    for index, raw in enumerate(raw_records):
        if not isinstance(raw, dict):
            raise PlanError(f"{path}: [[record]] #{index + 1} is not a table")
        _unknown(raw, RECORD_KEYS, f"[[record]] #{index + 1}")
        values = raw.get("values", {})
        if not isinstance(values, dict):
            raise PlanError(f"{path}: [record.values] #{index + 1} must be a table")
        records.append(PlanRecord(
            doctype=_as_str(raw.get("doctype"), "record.doctype"),
            name=_as_str(raw.get("name"), "record.name"),
            module=_as_str(raw.get("module"), "record.module"),
            values=dict(values),
        ))

    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        raise PlanError(f"{path}: [hooks] must be a table")
    raw_roles = data.get("roles", [])
    if not isinstance(raw_roles, list):
        raise PlanError(f"{path}: roles must be a list of role names")

    return Plan(path=path, app=dict(app), doctypes=doctypes, records=records,
                hooks=dict(hooks), roles=[str(one) for one in raw_roles],
                first_run=_parse_first_run(path, data.get("first_run")))


def _parse_first_run(path: Path, raw: object) -> PlanFirstRun:
    if raw is None:
        return PlanFirstRun()
    if not isinstance(raw, dict):
        raise PlanError(f"{path}: [first_run] must be a table")
    _unknown(raw, FIRST_RUN_KEYS, "[first_run]")
    raw_steps = raw.get("step", [])
    if not isinstance(raw_steps, list):
        raise PlanError(f"{path}: [[first_run.step]] must be an array of tables")
    steps: list[PlanStep] = []
    for index, one in enumerate(raw_steps):
        if not isinstance(one, dict):
            raise PlanError(f"{path}: [[first_run.step]] #{index + 1} is not a table")
        _unknown(one, FIRST_RUN_STEP_KEYS, f"[[first_run.step]] #{index + 1}")
        steps.append(PlanStep(
            name=_as_str(one.get("name"), "first_run.step.name"),
            title=_as_str(one.get("title"), "first_run.step.title"),
            action=_as_str(one.get("action"), "first_run.step.action"),
            reference_document=_as_str(one.get("reference_document"),
                                       "first_run.step.reference_document"),
            description=_as_str(one.get("description"), "first_run.step.description"),
            form_tour=_as_str(one.get("form_tour"), "first_run.step.form_tour"),
        ))
    allow_roles = raw.get("allow_roles", [])
    if not isinstance(allow_roles, list):
        raise PlanError(f"{path}: first_run.allow_roles must be a list of role names")
    return PlanFirstRun(
        declared=True,
        workspace=_as_str(raw.get("workspace"), "first_run.workspace"),
        module=_as_str(raw.get("module"), "first_run.module"),
        onboarding=_as_str(raw.get("onboarding"), "first_run.onboarding"),
        icon=_as_str(raw.get("icon"), "first_run.icon"),
        title=_as_str(raw.get("title"), "first_run.title"),
        subtitle=_as_str(raw.get("subtitle"), "first_run.subtitle"),
        success_message=_as_str(raw.get("success_message"), "first_run.success_message"),
        documentation_url=_as_str(raw.get("documentation_url"), "first_run.documentation_url"),
        allow_roles=[str(one) for one in allow_roles],
        steps=steps,
    )


def app_roots(bench_root: Path) -> list[Path]:
    apps = bench_root / "apps"
    if not apps.is_dir():
        return []
    return sorted(one for one in apps.iterdir() if one.is_dir())


def installed_hook_keys(bench_root: Path) -> set[str]:
    reader = re.compile(r"(?:get_hooks|hooks\.get)\(\s*[\"']([a-z_0-9]+)[\"']")
    declared = re.compile(r"^#?\s*([a-z_][a-z_0-9]*)\s*=", re.M)
    keys: set[str] = set()
    for app in app_roots(bench_root):
        for source in app.rglob("*.py"):
            if "node_modules" in source.parts:
                continue
            body = source.read_text(encoding="utf-8", errors="replace")
            keys.update(reader.findall(body))
            if source.name == "hooks.py":
                keys.update(declared.findall(body))
    return keys


def installed_roles(bench_root: Path, doctype_files: dict[str, Path]) -> set[str]:
    roles: set[str] = set()
    for app in app_roots(bench_root):
        for record in app.rglob("*/role/*/*.json"):
            if record.stem != record.parent.name:
                continue
            try:
                data = json.loads(record.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if data.get("doctype") == "Role" and data.get("name"):
                roles.add(str(data["name"]))
    for path in doctype_files.values():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for row in data.get("permissions", []) or []:
            if isinstance(row, dict) and row.get("role"):
                roles.add(str(row["role"]))
    return roles


def installed_module_records(bench_root: Path) -> dict[tuple[str, str], str]:
    found: dict[tuple[str, str], str] = {}
    for app in app_roots(bench_root):
        for doctype in FIRST_RUN_RECORD_DOCTYPES:
            for record in app.rglob(f"*/{scrub(doctype)}/*/*.json"):
                if record.stem != record.parent.name:
                    continue
                try:
                    data = json.loads(record.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                if data.get("doctype") == doctype and data.get("name"):
                    found.setdefault((doctype, str(data["name"])), app.name)
    return found


def series_prefix(value: str) -> str:
    return value.split(".", 1)[0].strip()


def claimed_series_prefixes(doctype_files: dict[str, Path]) -> dict[str, str]:
    claimed: dict[str, str] = {}
    for name, path in doctype_files.items():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        candidates: list[str] = []
        autoname = str(data.get("autoname") or "")
        if autoname.startswith("format:"):
            candidates.append(autoname[len("format:"):])
        elif autoname and not autoname.startswith(("field:", "naming_series", "hash", "Prompt",
                                                   "prompt", "autoincrement", "expression")):
            candidates.append(autoname)
        for one in data.get("fields", []) or []:
            if isinstance(one, dict) and one.get("fieldname") == "naming_series":
                candidates.extend(str(one.get("options") or "").split("\n"))
        for candidate in candidates:
            prefix = series_prefix(candidate)
            if prefix:
                claimed.setdefault(prefix, name)
    return claimed


@dataclass
class CheckResult:
    plan: Path
    bench_root: Path
    doctypes_installed: int
    hook_keys_read: int
    roles_known: int
    module_records_known: int = 0
    refusals: list[Refusal] = field(default_factory=list)
    order: list[str] = field(default_factory=list)

    def compact(self) -> dict[str, object]:
        return {
            "plan": str(self.plan),
            "bench_root": str(self.bench_root),
            "consumed": {
                "installed_doctypes": self.doctypes_installed,
                "hook_keys_read": self.hook_keys_read,
                "roles_known": self.roles_known,
                "module_records_known": self.module_records_known,
            },
            "order": self.order,
            "refusals": [one.compact() for one in self.refusals],
            "refusal_count": len(self.refusals),
        }


def _is_unanswered(value: object) -> bool:
    if isinstance(value, str):
        return not value.strip() or UNANSWERED in value
    if isinstance(value, list):
        return not value or any(_is_unanswered(one) for one in value)
    return value is None


def check_irreversible(plan: Plan) -> list[Refusal]:
    found: list[Refusal] = []
    for key in APP_IRREVERSIBLE:
        value = plan.app.get(key.split(".", 1)[1])
        if _is_unanswered(value):
            found.append(Refusal(key, f"irreversible and still at {UNANSWERED}"))
    for index, doc in enumerate(plan.doctypes):
        label = doc.name if not _is_unanswered(doc.name) else str(index)
        for name, value, allowed in (
            ("name", doc.name, None),
            ("module", doc.module, None),
            ("kind", doc.kind, KINDS),
            ("submittable", doc.submittable, YES_NO),
            ("posts_ledger_entries", doc.posts_ledger_entries, YES_NO),
            ("naming", doc.naming, None),
        ):
            key = f"doctype[{label}].{name}"
            if _is_unanswered(value):
                found.append(Refusal(key, f"irreversible and still at {UNANSWERED}"))
                continue
            if allowed and value not in allowed:
                found.append(Refusal(key, f"{value!r} is not one of {', '.join(sorted(allowed))}"))
        if not _is_unanswered(doc.naming) and doc.naming.split(":", 1)[0] not in NAMING_ROUTES:
            found.append(Refusal(f"doctype[{label}].naming",
                                 f"{doc.naming!r} names no route; the routes are "
                                 f"{', '.join(NAMING_ROUTES)}"))
        if doc.posts_ledger_entries == "yes" and doc.submittable != "yes":
            found.append(Refusal(f"doctype[{label}].submittable",
                                 "a ledger posting forces submittable from the first day"))
        if doc.naming == "autoincrement" and doc.allow_rename:
            found.append(Refusal(f"doctype[{label}].allow_rename",
                                 "autoincrement forces allow_rename off"))
        for position, one in enumerate(doc.fields):
            base = f"doctype[{label}].field[{position}]"
            if _is_unanswered(one.fieldname):
                found.append(Refusal(f"{base}.fieldname", f"irreversible and still at {UNANSWERED}"))
            if _is_unanswered(one.fieldtype):
                found.append(Refusal(f"{base}.fieldtype", f"irreversible and still at {UNANSWERED}"))
            elif one.fieldtype not in FIELDTYPES:
                found.append(Refusal(f"{base}.fieldtype", f"{one.fieldtype!r} is not a fieldtype"))
    return found


def check_fieldnames(plan: Plan) -> list[Refusal]:
    found: list[Refusal] = []
    for doc in plan.doctypes:
        seen: set[str] = set()
        for position, one in enumerate(doc.fields):
            key = f"doctype[{doc.name}].field[{position}].fieldname"
            name = one.fieldname
            if not name or UNANSWERED in name:
                continue
            if one.fieldtype in LAYOUT_FIELDTYPES:
                continue
            if name in FRAMEWORK_COLUMNS:
                found.append(Refusal(key, f"{name!r} is a framework column; the schema pass drops "
                                          "the field and raises nothing"))
            elif name in RESERVED_KEYWORDS:
                found.append(Refusal(key, f"{name!r} is a reserved keyword on the document object"))
            if name in seen:
                found.append(Refusal(key, f"{name!r} is used twice on this DocType"))
            seen.add(name)
    return found


def check_targets(plan: Plan, installed: set[str]) -> list[Refusal]:
    found: list[Refusal] = []
    in_plan = {doc.name for doc in plan.doctypes}
    for doc in plan.doctypes:
        for fieldname, target in doc.targets():
            key = f"doctype[{doc.name}].field[{fieldname}].options"
            if not target or UNANSWERED in target:
                found.append(Refusal(key, "a Link or Table field carries its target in options"))
                continue
            if target in in_plan or target in installed:
                continue
            found.append(Refusal(key, f"{target!r} is neither in this plan nor installed"))
    return found


def check_series(plan: Plan, claimed: dict[str, str]) -> list[Refusal]:
    found: list[Refusal] = []
    for doc in plan.doctypes:
        candidates = list(doc.naming_series_options)
        if doc.naming.startswith("format:"):
            candidates.append(doc.naming[len("format:"):])
        for candidate in candidates:
            prefix = series_prefix(candidate)
            if not prefix or UNANSWERED in prefix:
                continue
            owner = claimed.get(prefix)
            if owner:
                found.append(Refusal(
                    f"doctype[{doc.name}].naming_series_options",
                    f"prefix {prefix!r} is already claimed by {owner}; the counter row is shared",
                ))
    return found


def check_hooks(plan: Plan, readable: set[str]) -> list[Refusal]:
    if not readable:
        return [Refusal("hooks", "no installed app source under the bench root, so no hook key "
                                 "set could be measured; pass --bench")]
    found: list[Refusal] = []
    for key in sorted(plan.hooks):
        if key not in readable:
            found.append(Refusal(f"hooks.{key}", "no reader in the installed source spells this key"))
            continue
        value = plan.hooks[key]
        for dotted in _dotted_values(value):
            if "." not in dotted:
                found.append(Refusal(f"hooks.{key}",
                                     f"{dotted!r} is not a dotted path; the reader imports it"))
    return found


def _dotted_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for one in value:
            out.extend(_dotted_values(one))
        return out
    if isinstance(value, dict):
        out = []
        for one in value.values():
            out.extend(_dotted_values(one))
        return out
    return []


def check_roles(plan: Plan, known: set[str]) -> list[Refusal]:
    found: list[Refusal] = []
    declared = set(plan.roles)
    for doc in plan.doctypes:
        for position, row in enumerate(doc.permissions):
            role = str(row.get("role") or "")
            key = f"doctype[{doc.name}].permission[{position}].role"
            if not role or UNANSWERED in role:
                found.append(Refusal(key, "a permission row carries a role name"))
                continue
            if role in declared or role in known:
                continue
            found.append(Refusal(key, f"{role!r} exists on no site and this plan does not declare "
                                      "it; sync would create it with desk access"))
    return found


def check_records(plan: Plan) -> list[Refusal]:
    found: list[Refusal] = []
    modules = set(plan.modules)
    for index, record in enumerate(plan.records):
        key = f"record[{index}]"
        if not record.doctype or UNANSWERED in record.doctype:
            found.append(Refusal(f"{key}.doctype", f"still at {UNANSWERED}"))
            continue
        if record.doctype in FIXTURE_ONLY_DOCTYPES:
            continue
        if record.doctype not in MODULE_RECORD_DOCTYPES:
            found.append(Refusal(f"{key}.doctype",
                                 f"{record.doctype!r} is neither imported from a module directory "
                                 "nor shipped as a fixture"))
            continue
        if record.module and record.module not in modules:
            found.append(Refusal(f"{key}.module", f"{record.module!r} is not in app.modules"))
    return found


def check_modules(plan: Plan) -> list[Refusal]:
    found: list[Refusal] = []
    modules = set(plan.modules)
    for doc in plan.doctypes:
        if _is_unanswered(doc.module):
            continue
        if doc.module not in modules:
            found.append(Refusal(f"doctype[{doc.name}].module",
                                 f"{doc.module!r} is not in app.modules, so the sync walk never "
                                 "opens its directory"))
    return found


def check_list_filters(plan: Plan) -> list[Refusal]:
    found: list[Refusal] = []
    for doc in plan.doctypes:
        names = {one.fieldname for one in doc.fields if one.fieldname}
        for position, one in enumerate(doc.list_filters):
            key = f"doctype[{doc.name}].list_filter[{position}]"
            if doc.kind and doc.kind != "ordinary":
                found.append(Refusal(key, f"a {doc.kind} DocType opens no list view, so "
                                          "frappe.listview_settings is read by nothing"))
                continue
            if _is_unanswered(one.fieldname):
                found.append(Refusal(f"{key}.fieldname", f"still at {UNANSWERED}"))
                continue
            if one.fieldname not in names and one.fieldname not in FRAMEWORK_COLUMNS:
                found.append(Refusal(f"{key}.fieldname",
                                     f"{one.fieldname!r} is on no field of this DocType"))
            if one.operator not in LIST_FILTER_OPERATORS:
                found.append(Refusal(f"{key}.operator",
                                     f"{one.operator!r} is not a list filter operator"))
    return found


def _claimed(found: list[Refusal], key: str, doctype: str, name: str,
             claimed: dict[tuple[str, str], str]) -> None:
    owner = claimed.get((doctype, name))
    if owner:
        found.append(Refusal(key, f"{doctype} {name!r} is already shipped by {owner}; the import "
                                  "overwrites that record and nothing hands it back"))


def check_first_run(plan: Plan, installed: set[str], claimed: dict[tuple[str, str], str],
                    roles_known: set[str]) -> list[Refusal]:
    first = plan.first_run
    if not first.declared:
        return [Refusal("first_run", "the plan declares no [first_run] table, so no Workspace "
                                     "carries a link to any DocType and the app opens on nothing")]
    found: list[Refusal] = []
    in_plan = {doc.name for doc in plan.doctypes}
    modules = set(plan.modules)
    declared_records = {(record.doctype, record.name) for record in plan.records}

    for key in FIRST_RUN_IRREVERSIBLE:
        value = getattr(first, key.split(".", 1)[1])
        if _is_unanswered(value):
            found.append(Refusal(key, f"irreversible and still at {UNANSWERED}"))

    if first.module and UNANSWERED not in first.module and first.module not in modules:
        found.append(Refusal("first_run.module",
                             f"{first.module!r} is not in app.modules, so the sync walk never "
                             "opens its directory"))

    if first.workspace and UNANSWERED not in first.workspace:
        _claimed(found, "first_run.workspace", "Workspace", first.workspace, claimed)
        if ("Workspace", first.workspace) in declared_records:
            found.append(Refusal("first_run.workspace",
                                 f"{first.workspace!r} is also declared as a [[record]]; two "
                                 "writers would race for one file"))

    if first.wants_onboarding:
        _claimed(found, "first_run.onboarding", "Module Onboarding", first.onboarding, claimed)
        if not plan.step_names():
            found.append(Refusal("first_run.step",
                                 "Module Onboarding.steps is required, so an onboarding with no "
                                 "step fails validation on the site"))

    seen_steps: set[str] = set()
    for key, name in plan.step_names():
        if _is_unanswered(name):
            found.append(Refusal(key, f"irreversible and still at {UNANSWERED}"))
            continue
        if not first.wants_onboarding:
            found.append(Refusal(key, "first_run.onboarding is declined, so Module Onboarding.steps "
                                      "cites this step from nowhere"))
            continue
        _claimed(found, key, "Onboarding Step", name, claimed)
        if name in seen_steps:
            found.append(Refusal(key, f"{name!r} names two onboarding steps; the second import "
                                      "overwrites the first"))
        seen_steps.add(name)

    tours = plan.tour_names()
    for index, step in enumerate(first.steps):
        base = f"first_run.step[{index}]"
        if _is_unanswered(step.title):
            found.append(Refusal(f"{base}.title", "Module Onboarding renders a step by its title"))
        if _is_unanswered(step.action):
            found.append(Refusal(f"{base}.action", f"still at {UNANSWERED}"))
        elif step.action not in ONBOARDING_ACTIONS:
            found.append(Refusal(f"{base}.action", f"{step.action!r} is not one of "
                                                   f"{', '.join(sorted(ONBOARDING_ACTIONS))}"))
        elif step.action == "Create Entry" and not step.reference_document:
            found.append(Refusal(f"{base}.reference_document",
                                 "a Create Entry step opens the form of its reference document"))
        elif step.action == "Show Form Tour" and not step.form_tour:
            found.append(Refusal(f"{base}.form_tour",
                                 "a Show Form Tour step names the tour it runs"))
        target = step.reference_document
        if target and UNANSWERED not in target and target not in in_plan and target not in installed:
            found.append(Refusal(f"{base}.reference_document",
                                 f"{target!r} is neither in this plan nor installed"))
        if step.form_tour and UNANSWERED not in step.form_tour and step.form_tour not in tours:
            found.append(Refusal(f"{base}.form_tour",
                                 f"{step.form_tour!r} is asked for by no DocType in this plan"))

    seen_tours: set[str] = set()
    for doc in plan.doctypes:
        for name, key in ((doc.form_tour, f"doctype[{doc.name}].form_tour"),
                          (doc.onboarding_step, f"doctype[{doc.name}].onboarding_step")):
            if name and UNANSWERED in name:
                found.append(Refusal(key, f"irreversible and still at {UNANSWERED}"))
            elif name and doc.kind == "child":
                found.append(Refusal(key, "a child table opens no form of its own, so the record "
                                          "would point at a document nobody can reach"))
        if not doc.form_tour or UNANSWERED in doc.form_tour or doc.kind == "child":
            continue
        key = f"doctype[{doc.name}].form_tour"
        _claimed(found, key, "Form Tour", doc.form_tour, claimed)
        if doc.form_tour in seen_tours:
            found.append(Refusal(key, f"{doc.form_tour!r} names two form tours; Form Tour is named "
                                      "by its title, so the second import overwrites the first"))
        seen_tours.add(doc.form_tour)
        if not doc.tour_steps():
            found.append(Refusal(key, "Form Tour.steps is required and this DocType declares no "
                                      "required field to step through"))

    declared = set(plan.roles)
    for index, role in enumerate(first.allow_roles):
        key = f"first_run.allow_roles[{index}]"
        if _is_unanswered(role):
            found.append(Refusal(key, "a role row carries a role name"))
        elif role not in declared and role not in roles_known:
            found.append(Refusal(key, f"{role!r} exists on no site and this plan does not declare "
                                      "it; sync would create it with desk access"))
    return found


def dependency_order(plan: Plan) -> tuple[list[str], list[Refusal]]:
    names = [doc.name for doc in plan.doctypes]
    in_plan = set(names)
    needs: dict[str, set[str]] = {name: set() for name in names}
    for doc in plan.doctypes:
        for _fieldname, target in doc.targets():
            if target in in_plan and target != doc.name:
                needs[doc.name].add(target)
    ordered: list[str] = []
    pending = dict(needs)
    while pending:
        ready = sorted(name for name, wants in pending.items() if not wants)
        if not ready:
            cycle = " -> ".join(sorted(pending))
            return [], [Refusal("doctype", f"a link cycle leaves no DocType writable first: {cycle}")]
        for name in ready:
            ordered.append(name)
            pending.pop(name)
        for wants in pending.values():
            wants.difference_update(ready)
    return ordered, []


def run_check(plan_path: Path, bench_root: Path) -> CheckResult:
    plan = parse_plan(plan_path)
    doctype_files = seed_kit.doctype_index(app_roots(bench_root))
    installed = set(doctype_files)
    readable = installed_hook_keys(bench_root)
    roles = installed_roles(bench_root, doctype_files)
    module_records = installed_module_records(bench_root)
    order, cycle = dependency_order(plan)
    result = CheckResult(
        plan=plan_path,
        bench_root=bench_root,
        doctypes_installed=len(installed),
        hook_keys_read=len(readable),
        roles_known=len(roles),
        module_records_known=len(module_records),
        order=order,
    )
    result.refusals = (
        check_irreversible(plan)
        + check_modules(plan)
        + check_fieldnames(plan)
        + check_targets(plan, installed)
        + check_series(plan, claimed_series_prefixes(doctype_files))
        + check_hooks(plan, readable)
        + check_roles(plan, roles)
        + check_records(plan)
        + check_list_filters(plan)
        + check_first_run(plan, installed, module_records, roles)
        + cycle
    )
    return result


def render_check(result: CheckResult) -> str:
    lines = [
        f"plan   {result.plan}",
        f"bench  {result.bench_root}",
        f"CONSUMED {result.doctypes_installed} installed DocType(s), "
        f"{result.hook_keys_read} hook key(s) the source reads, {result.roles_known} role name(s), "
        f"{result.module_records_known} first-run record name(s)",
        "",
    ]
    if result.order:
        lines.append("write order: " + " -> ".join(result.order))
        lines.append("")
    if not result.refusals:
        lines.append("  every irreversible decision is answered and every reference resolves.")
    for refusal in result.refusals:
        lines.append(refusal.line())
    lines.append("")
    lines.append(f"refusals={len(result.refusals)}")
    return "\n".join(lines)


PLAN_TEMPLATE = """# A Frappe app plan. `frappe-pipes create check` refuses to pass while any value
# below still reads ANSWER-ME, because every one of those decisions is irreversible
# once the app holds data. Run `frappe-pipes create ask` for the questions in order.

roles = []

[app]
name = "ANSWER-ME"
title = "ANSWER-ME"
publisher = "ANSWER-ME"
email = "ANSWER-ME"
description = "One line an operator reads in the apps screen."
license = "mit"
modules = ["ANSWER-ME"]

[hooks]

[[doctype]]
name = "ANSWER-ME"
module = "ANSWER-ME"
kind = "ANSWER-ME"
submittable = "ANSWER-ME"
posts_ledger_entries = "ANSWER-ME"
naming = "ANSWER-ME"
naming_series_options = []
title_field = ""
search_fields = ""
track_changes = true
allow_rename = true
is_tree = false
form_tour = ""
onboarding_step = ""

[[doctype.field]]
fieldname = "ANSWER-ME"
fieldtype = "ANSWER-ME"
label = ""
options = ""
reqd = false
unique = false
in_list_view = false

[[doctype.permission]]
role = "System Manager"
read = true
write = true
create = true
delete = true
report = true
export = true
share = true
print = true
email = true
permlevel = 0

[[doctype.list_filter]]
fieldname = "docstatus"
operator = "="
value = "0"

[first_run]
workspace = "ANSWER-ME"
module = "ANSWER-ME"
onboarding = "ANSWER-ME"
icon = ""
title = ""
subtitle = ""
success_message = ""
documentation_url = ""
allow_roles = []

[[first_run.step]]
name = "ANSWER-ME"
title = "ANSWER-ME"
action = "ANSWER-ME"
reference_document = ""
description = ""
form_tour = ""
"""


QUESTIONS = [
    ("app.name", "What is the app name, and which modules does it carry? A controller is loaded "
                 "from its module value and patches.txt carries import paths forever."),
    ("doctype.kind", "Is each DocType ordinary, a single, or a child table? The table sync is "
                     "skipped for a single and a child table's permissions are wiped, and neither "
                     "carries data across afterwards."),
    ("doctype.submittable", "Is it submittable, and does it post ledger entries? A submitted "
                            "document never returns to draft and a cancel writes reversal rows."),
    ("doctype.naming", "Which naming route, and is it autoincrement? The autoincrement decision is "
                       "refused once the table holds a row, and it forces allow_rename off."),
    ("doctype.field.fieldname", "What is the fieldname of every field? A rename in the JSON alone "
                                "adds an empty column and orphans the old one while the migration "
                                "exits clean."),
    ("doctype.field.fieldtype", "What is the fieldtype of every field? A change is permitted only "
                                "inside a small group, and editing the JSON bypasses that guard."),
    ("doctype.permission.role", "Which roles hold which permissions? The rows ship in the DocType "
                                "JSON and a role that does not exist is created with desk access."),
    ("first_run.workspace", "Which Workspace does the app open on, which module carries it, and is "
                            "there a Module Onboarding or is that answer 'none'? The workspace "
                            "content cites the onboarding by name and nothing removes an orphaned "
                            "record on the next migration."),
    ("first_run.step.name", "What does the first run walk an operator through, step by step? A step "
                            "is reached only through Module Onboarding.steps, which cites it by "
                            "name, and the step name is typed once and never derived."),
    ("doctype.form_tour", "Which DocTypes ship a Form Tour, and what is each tour called? A Form "
                          "Tour is named by its title, so a retitled tour imports as a second "
                          "record and the first one stays live."),
    ("doctype.onboarding_step", "Which DocTypes ship an Onboarding Step of their own, and what is "
                                "each step called? Leave it empty for a DocType the first run "
                                "does not walk through."),
    ("doctype.title_field", "What are the labels, the title field, the list-view flags, the unique "
                            "flag, track_changes and the naming_series option list?"),
    ("doctype.list_filter", "Which filter does each list view open on? The filter rows and the "
                            "title field decide what the generated list-view settings carry."),
]


def run_ask() -> int:
    for key, question in QUESTIONS:
        print(f"{key:<28} {question}")
    return 0


def run_plan(out: Path, force: bool) -> int:
    if out.exists() and not force:
        print(f"REFUSED {out} already exists; pass --force to overwrite it")
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(PLAN_TEMPLATE, encoding="utf-8")
    print(f"plan={out}")
    return 0


CONTROLLER_TEMPLATE = """{base_import}


class {classname}({base_class}):
\tpass
"""

TEST_TEMPLATE = """from frappe.tests.utils import FrappeTestCase


class Test{classname}(FrappeTestCase):
\tpass
"""


def doctype_json(doc: PlanDocType, stamp: str, owner: str) -> dict[str, object]:
    fields = []
    for one in doc.fields:
        entry: dict[str, object] = {
            "fieldname": one.fieldname,
            "fieldtype": one.fieldtype,
            "label": one.label or one.fieldname.replace("_", " ").title(),
        }
        if one.options:
            entry["options"] = one.options
        for flag, value in (("reqd", one.reqd), ("unique", one.unique),
                            ("in_list_view", one.in_list_view), ("read_only", one.read_only),
                            ("hidden", one.hidden)):
            if value:
                entry[flag] = 1
        if one.default:
            entry["default"] = one.default
        fields.append(entry)

    permissions = []
    for row in doc.permissions:
        entry = {"role": str(row.get("role") or "")}
        for flag in sorted(PERMISSION_KEYS - {"role", "permlevel"}):
            if row.get(flag):
                entry[flag] = 1
        entry["permlevel"] = int(row.get("permlevel") or 0)
        permissions.append(entry)

    data: dict[str, object] = {
        "actions": [],
        "creation": stamp,
        "doctype": "DocType",
        "editable_grid": 1,
        "engine": "InnoDB",
        "field_order": [one.fieldname for one in doc.fields],
        "fields": fields,
        "index_web_pages_for_search": 1,
        "links": [],
        "modified": stamp,
        "modified_by": owner,
        "module": doc.module,
        "name": doc.name,
        "owner": owner,
        "permissions": permissions,
        "sort_field": "modified",
        "sort_order": "DESC",
        "states": [],
    }
    if doc.kind == "child":
        data["istable"] = 1
    if doc.kind == "single":
        data["issingle"] = 1
    if doc.submittable == "yes":
        data["is_submittable"] = 1
    if doc.is_tree:
        data["is_tree"] = 1
    if doc.track_changes:
        data["track_changes"] = 1
    if doc.allow_rename:
        data["allow_rename"] = 1
    if doc.title_field:
        data["title_field"] = doc.title_field
    if doc.search_fields:
        data["search_fields"] = doc.search_fields
    route = doc.naming.split(":", 1)[0]
    if route == "naming_series":
        data["autoname"] = "naming_series:"
    elif route in ("field", "format"):
        data["autoname"] = doc.naming
    elif route == "prompt":
        data["autoname"] = "Prompt"
    elif route in ("hash", "autoincrement"):
        data["autoname"] = route
    return data


@dataclass
class Emission:
    path: Path
    kind: str
    body: str

    def compact(self) -> dict[str, str]:
        return {"path": str(self.path), "kind": self.kind}


def list_view_settings(doc: PlanDocType) -> dict[str, object]:
    settings: dict[str, object] = {}
    if doc.title_field:
        settings["hide_name_column"] = True
    if doc.list_filters:
        settings["filters"] = [[one.fieldname, one.operator, one.value] for one in doc.list_filters]
    return settings


def workspace_json(plan: Plan, order: list[str], stamp: str, owner: str) -> dict[str, object]:
    first = plan.first_run
    by_name = {doc.name: doc for doc in plan.doctypes}
    links: list[dict[str, object]] = []
    content: list[dict[str, object]] = []
    if first.wants_onboarding:
        content.append({"type": "onboarding",
                        "data": {"onboarding_name": first.onboarding, "col": 12}})
    for module in plan.modules:
        listed = [by_name[name] for name in order
                  if by_name[name].module == module and by_name[name].kind != "child"]
        if not listed:
            continue
        links.append({"hidden": 0, "is_query_report": 0, "label": module,
                      "link_count": len(listed), "onboard": 0, "type": "Card Break"})
        for doc in listed:
            links.append({"dependencies": "", "hidden": 0, "is_query_report": 0, "label": doc.name,
                          "link_count": 0, "link_to": doc.name, "link_type": "DocType",
                          "onboard": 0, "type": "Link"})
        content.append({"type": "card", "data": {"card_name": module, "col": 4}})
    return {
        "charts": [], "content": json.dumps(content, ensure_ascii=False), "creation": stamp,
        "custom_blocks": [], "docstatus": 0, "doctype": "Workspace", "for_user": "",
        "hide_custom": 0, "icon": first.icon or "folder", "idx": 0, "is_hidden": 0,
        "label": first.workspace, "links": links, "modified": stamp, "modified_by": owner,
        "module": first.module, "name": first.workspace, "number_cards": [], "owner": owner,
        "parent_page": "", "public": 1, "quick_lists": [], "restrict_to_domain": "", "roles": [],
        "sequence_id": 1.0, "shortcuts": [], "title": first.workspace,
    }


def onboarding_step_json(step: PlanStep, stamp: str, owner: str,
                         is_single: bool = False) -> dict[str, object]:
    data: dict[str, object] = {
        "action": step.action, "creation": stamp, "docstatus": 0, "doctype": "Onboarding Step",
        "idx": 0, "is_complete": 0, "is_single": 1 if is_single else 0, "is_skipped": 0,
        "modified": stamp, "modified_by": owner, "name": step.name, "owner": owner,
        "show_full_form": 0, "title": step.title or step.name, "validate_action": 0,
    }
    if step.reference_document:
        data["reference_document"] = step.reference_document
    if step.description:
        data["description"] = step.description
    if step.form_tour:
        data["form_tour"] = step.form_tour
        data["show_form_tour"] = 1
    return data


def module_onboarding_json(plan: Plan, order: list[str], stamp: str,
                           owner: str) -> dict[str, object]:
    first = plan.first_run
    by_name = {doc.name: doc for doc in plan.doctypes}
    steps = [{"step": step.name} for step in first.steps]
    steps.extend({"step": by_name[name].onboarding_step} for name in order
                 if by_name[name].onboarding_step)
    return {
        "allow_roles": [{"role": role} for role in first.allow_roles],
        "creation": stamp, "docstatus": 0, "doctype": "Module Onboarding",
        "documentation_url": first.documentation_url, "idx": 0, "is_complete": 0,
        "modified": stamp, "modified_by": owner, "module": first.module, "name": first.onboarding,
        "owner": owner, "steps": steps, "subtitle": first.subtitle,
        "success_message": first.success_message, "title": first.title or first.onboarding,
    }


def form_tour_json(doc: PlanDocType, stamp: str, owner: str) -> dict[str, object]:
    steps = []
    for one in doc.tour_steps():
        label = one.label or one.fieldname.replace("_", " ").title()
        steps.append({
            "description": label, "field": "", "fieldname": one.fieldname,
            "fieldtype": one.fieldtype, "has_next_condition": 0, "is_table_field": 0,
            "label": label, "parent_field": "", "position": "Right", "title": label,
        })
    return {
        "creation": stamp, "docstatus": 0, "doctype": "Form Tour", "idx": 0, "is_standard": 1,
        "modified": stamp, "modified_by": owner, "module": doc.module, "name": doc.form_tour,
        "owner": owner, "reference_doctype": doc.name, "save_on_complete": 1, "steps": steps,
        "title": doc.form_tour,
    }


def _record_text(body: dict[str, object]) -> str:
    return json.dumps(body, indent=1, ensure_ascii=False, sort_keys=True) + "\n"


def first_run_emissions(plan: Plan, package: Path, order: list[str], stamp: str,
                        owner: str) -> list[Emission]:
    first = plan.first_run
    if not first.declared:
        return []
    by_name = {doc.name: doc for doc in plan.doctypes}
    home = package / scrub(first.module)
    out = [Emission(home / "workspace" / scrub(first.workspace)
                    / f"{scrub(first.workspace)}.json", "workspace",
                    _record_text(workspace_json(plan, order, stamp, owner)))]
    if first.wants_onboarding:
        for step in first.steps:
            out.append(Emission(home / "onboarding_step" / scrub(step.name)
                                / f"{scrub(step.name)}.json", "onboarding step",
                                _record_text(onboarding_step_json(step, stamp, owner))))
        for name in order:
            doc = by_name[name]
            if not doc.onboarding_step:
                continue
            derived = PlanStep(name=doc.onboarding_step, title=doc.onboarding_step,
                               action="Update Settings" if doc.kind == "single" else "Create Entry",
                               reference_document=doc.name)
            out.append(Emission(package / scrub(doc.module) / "onboarding_step"
                                / scrub(derived.name) / f"{scrub(derived.name)}.json",
                                "onboarding step",
                                _record_text(onboarding_step_json(derived, stamp, owner,
                                                                  is_single=doc.kind == "single"))))
        out.append(Emission(home / "module_onboarding" / scrub(first.onboarding)
                            / f"{scrub(first.onboarding)}.json", "module onboarding",
                            _record_text(module_onboarding_json(plan, order, stamp, owner))))
    for name in order:
        doc = by_name[name]
        if not doc.form_tour:
            continue
        out.append(Emission(package / scrub(doc.module) / "form_tour" / scrub(doc.form_tour)
                            / f"{scrub(doc.form_tour)}.json", "form tour",
                            _record_text(form_tour_json(doc, stamp, owner))))
    return out


def plan_emissions(plan: Plan, package: Path, order: list[str], stamp: str) -> list[Emission]:
    owner = "Administrator"
    by_name = {doc.name: doc for doc in plan.doctypes}
    out: list[Emission] = []

    out.append(Emission(package / "modules.txt", "modules.txt",
                        "\n".join(plan.modules) + "\n"))
    for module in plan.modules:
        out.append(Emission(package / scrub(module) / "__init__.py", "module package", ""))
        out.append(Emission(package / scrub(module) / "doctype" / "__init__.py",
                            "module package", ""))

    for name in order:
        doc = by_name[name]
        folder = package / scrub(doc.module) / "doctype" / scrub(doc.name)
        out.append(Emission(folder / "__init__.py", "doctype package", ""))
        out.append(Emission(folder / f"{scrub(doc.name)}.json", "doctype json",
                            json.dumps(doctype_json(doc, stamp, owner), indent=1,
                                       ensure_ascii=False) + "\n"))
        base_import = ("from frappe.utils.nestedset import NestedSet" if doc.is_tree
                       else "from frappe.model.document import Document")
        base_class = "NestedSet" if doc.is_tree else "Document"
        out.append(Emission(folder / f"{scrub(doc.name)}.py", "controller",
                            CONTROLLER_TEMPLATE.format(base_import=base_import,
                                                       base_class=base_class,
                                                       classname=classname(doc.name))))
        out.append(Emission(folder / f"test_{scrub(doc.name)}.py", "test",
                            TEST_TEMPLATE.format(classname=classname(doc.name))))
        settings = list_view_settings(doc)
        if settings and doc.kind == "ordinary":
            out.append(Emission(
                folder / f"{scrub(doc.name)}_list.js", "list view settings",
                f"frappe.listview_settings[{json.dumps(doc.name, ensure_ascii=False)}] = "
                f"{json.dumps(settings, indent=1, ensure_ascii=False, sort_keys=True)};\n"))

    for record in plan.records:
        body = dict(record.values)
        body["doctype"] = record.doctype
        body["name"] = record.name
        body["modified"] = stamp
        text = json.dumps(body, indent=1, ensure_ascii=False) + "\n"
        if record.doctype in FIXTURE_ONLY_DOCTYPES:
            out.append(Emission(package / "fixtures" / f"{scrub(record.doctype)}.json",
                                "fixture", text))
            continue
        folder = (package / scrub(record.module or plan.modules[0])
                  / scrub(record.doctype) / scrub(record.name))
        out.append(Emission(folder / f"{scrub(record.name)}.json", "module record", text))

    lines = []
    for key in sorted(plan.hooks):
        lines.append(f"{key} = {json.dumps(plan.hooks[key], ensure_ascii=False)}")
    fixture_types = sorted({record.doctype for record in plan.records
                            if record.doctype in FIXTURE_ONLY_DOCTYPES})
    if fixture_types:
        lines.append(f"fixtures = {json.dumps(fixture_types, ensure_ascii=False)}")
    if lines:
        scaffold = package / "hooks.py"
        body = scaffold.read_text(encoding="utf-8") if scaffold.is_file() else ""
        out.append(Emission(scaffold, "hooks", body.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n"))

    out.extend(first_run_emissions(plan, package, order, stamp, owner))
    return out


@dataclass
class GenerateResult:
    plan: Path
    dest: Path
    package: Path
    mode: str
    stamp: str
    emissions: list[Emission] = field(default_factory=list)
    refusals: list[Refusal] = field(default_factory=list)

    def compact(self) -> dict[str, object]:
        return {
            "plan": str(self.plan),
            "dest": str(self.dest),
            "package": str(self.package),
            "mode": self.mode,
            "stamp": self.stamp,
            "emitted": [one.compact() for one in self.emissions],
            "refusals": [one.compact() for one in self.refusals],
            "refusal_count": len(self.refusals),
        }


def render_generate(result: GenerateResult) -> str:
    lines = [
        f"plan    {result.plan}",
        f"package {result.package}",
        f"mode    {result.mode}",
        f"stamp   {result.stamp}",
        "",
    ]
    for refusal in result.refusals:
        lines.append(refusal.line())
    if result.refusals:
        lines.append("")
        lines.append(f"refusals={len(result.refusals)}  wrote=0")
        return "\n".join(lines)
    verb = "would write" if result.mode == "dry-run" else "wrote"
    for emission in result.emissions:
        lines.append(f"  {verb:<11} {emission.kind:<16} {emission.path}")
    lines.append("")
    lines.append(f"refusals=0  files={len(result.emissions)}")
    return "\n".join(lines)


def run_generate(plan_path: Path, dest: Path, bench_root: Path, write: bool) -> GenerateResult:
    checked = run_check(plan_path, bench_root)
    plan = parse_plan(plan_path)
    package = dest / plan.app_name / plan.app_name
    result = GenerateResult(plan=plan_path, dest=dest, package=package,
                            mode="write" if write else "dry-run", stamp=fresh_utc_stamp())
    if checked.refusals:
        result.refusals = list(checked.refusals)
        result.refusals.append(Refusal("check", "the plan is red, so nothing is written"))
        return result
    if not (package / "hooks.py").is_file():
        result.refusals.append(Refusal(
            "scaffold",
            f"no app package at {package}; create the scaffold first with "
            f"`python3 tools/benchx.py new-app {plan.app_name}`",
        ))
        return result
    result.emissions = plan_emissions(plan, package, checked.order, result.stamp)
    if not write:
        return result
    for emission in result.emissions:
        emission.path.parent.mkdir(parents=True, exist_ok=True)
        emission.path.write_text(emission.body, encoding="utf-8")
    return result


def resolve_bench(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else Path(DEFAULT_BENCH_ROOT)


def run(args) -> int:
    if args.create_command == "ask":
        return run_ask()
    if args.create_command == "plan":
        return run_plan(Path(args.out).expanduser(), args.force)
    if args.create_command == "check":
        try:
            result = run_check(Path(args.plan).expanduser(), resolve_bench(args.bench))
        except PlanError as exc:
            raise SystemExit(f"frappe-pipes create check: {exc}") from exc
        if args.json:
            print(json.dumps(result.compact(), ensure_ascii=False, separators=(",", ":")))
        else:
            print(render_check(result))
        return 1 if result.refusals else 0
    if args.create_command == "app":
        try:
            result = run_generate(Path(args.plan).expanduser(), Path(args.dest).expanduser(),
                                  resolve_bench(args.bench), args.write)
        except PlanError as exc:
            raise SystemExit(f"frappe-pipes create app: {exc}") from exc
        if args.json:
            print(json.dumps(result.compact(), ensure_ascii=False, separators=(",", ":")))
        else:
            print(render_generate(result))
        return 1 if result.refusals else 0
    return 2


def add_arguments(sub) -> None:
    create = sub.add_parser(
        "create",
        help="Plan a new Frappe app, grade the plan, and generate what bench new-app does not write",
    )
    inner = create.add_subparsers(dest="create_command", required=True, metavar="<step>")

    plan_parser = inner.add_parser("plan", help="Write the plan template")
    plan_parser.add_argument("--out", default="app-plan.toml", help="Where to write the template")
    plan_parser.add_argument("--force", action="store_true", help="Overwrite an existing plan file")

    inner.add_parser("ask", help="Print the plan's questions, the hardest to reverse first")

    check_parser = inner.add_parser("check", help="Grade a filled plan; non-zero on any refusal")
    check_parser.add_argument("plan", help="Plan file (.toml)")
    check_parser.add_argument("--bench", default=None, help="Bench root holding the installed apps")
    check_parser.add_argument("--json", action="store_true", help="Print machine JSON")

    app_parser = inner.add_parser("app", help="Generate the app files; a dry run unless --write")
    app_parser.add_argument("plan", help="Plan file (.toml)")
    app_parser.add_argument("--dest", required=True, help="Directory holding the app package root")
    app_parser.add_argument("--bench", default=None, help="Bench root holding the installed apps")
    app_parser.add_argument("--write", action="store_true",
                            help="Write the files; without it nothing is written")
    app_parser.add_argument("--json", action="store_true", help="Print machine JSON")
