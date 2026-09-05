#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa


from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _suite_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "SKILL.md").is_file():
            return candidate
    raise SystemExit(
        f"build-index: no SKILL.md above {start}, so the suite root is unknown and every "
        "index row would describe the wrong tree."
    )


SUITE_ROOT = _suite_root(Path(__file__).resolve().parent)
PRODUCTS = {"frappe", "erpnext", "hrms", "frappe-ui", "bench"}


INDEX_NAME = "INDEX.tsv"
INDEX_COLUMNS = ("triggers", "path", "source", "verified")

SHEET_QUESTIONS: dict[str, tuple[str, ...]] = {
    "a-desk-surface-is-filled-not-composed.md": (
        "how do i design a desk page",
        "what does a desk page look like",
        "should this be a page a list view or a report",
        "where does the primary action go on a desk screen",
        "what components does frappe give a desk page",
        "how does frappe design its own screens",
        "my desk page looks nothing like frappe",
        "which desk surface should i build",
        "design a frappe screen",
        "frappe design style",
    ),
    "knowing-your-answer-is-right.md": (
        "how do i know my answer about frappe is right",
        "the gate passed so is my leaf correct",
        "should i run it or read the source",
        "what does a passing check actually prove",
        "how do i verify what a model told me about frappe",
        "what would have to be true for my answer to be wrong",
        "verify a frappe answer",
        "how to check frappe behaviour",
    ),
    "the-checked-and-unchecked-spelling-of-a-read-and-a-write.md": (
        "get_list vs get_all which one checks permissions",
        "does frappe.db.sql ignore permissions",
        "which read applies user permissions",
        "my query returns rows the user should not see",
        "checked or unchecked spelling of a read",
        "permission checked query",
        "get_list vs get_all",
    ),
    "the-desk-what-is-metadata-and-what-must-be-code.md": (
        "what can i configure in the desk without writing code",
        "why is my column missing from the list view",
        "workspace link does not appear",
        "dashboard chart or number card which one",
        "desk configuration vs code",
        "what can be done without code in frappe",
    ),
    "the-records-that-carry-code-and-what-each-one-runs.md": (
        "is a print format a file or a record",
        "can a report run python",
        "what does a server script execute",
        "which desk records run code",
        "why did saving a report write a file into my app",
        "which desk record type can run code",
        "server script vs report vs print format",
    ),
    "when-a-background-job-runs-and-what-stops-it.md": (
        "my scheduled job never ran",
        "does a background job check permissions",
        "which user does a background job run as",
        "scheduler disabled on the site",
        "how do i queue work in frappe",
        "background job scheduling",
        "why is my scheduled job not running",
    ),
    "the-commands-that-run-code-and-who-they-run-as.md": (
        "does bench execute run as administrator",
        "why did my change in bench console disappear",
        "bench run-tests left the scheduler disabled on the site",
        "does a scheduled job check permissions",
        "which bench commands commit for me and which do not",
        "my migrate failed halfway and I do not know what is already committed",
        "does bench execute run on every site or just one",
        "which user does a background job run as",
        "bench execute ran my function twice",
        "bench execute vs console",
        "which user runs a bench command",
    ),
    "where-a-server-side-query-is-typed-and-what-it-carries.md": (
        "why does my query return different rows in the console than in the app",
        "bench console shows rows this user should not see",
        "my get_list works in bench execute but returns nothing over the api",
        "which user does a scheduled job run as",
        "does a background job run as the user who queued it",
        "does frappe.session.user work inside a server script",
        "the report shows rows the role should not be able to see",
        "what user does a controller method run as",
        "i tested the permission in the console and it passed but it fails in production",
        "server side query user context",
        "which user runs a server script query",
    ),
    "the-commands-that-create-an-app-a-site-and-an-install.md": (
        "what do i type to create a new frappe app from scratch",
        "i made an app with bench new-app but it does not show up on my site",
        "does bench new-app install the app on a site too",
        "what is the difference between get-app and install-app",
        "how do i completely remove an app from my bench",
        "does bench drop-site actually delete the site folder",
        "App myapp not in apps.txt when i install it",
        "in what order do i run new-app new-site and install-app",
        "what does uninstall-app leave behind on the site",
        "create a frappe app and site",
        "bench new-app new-site install-app",
    ),
    "the-files-an-app-is-made-of-and-what-each-one-declares.md": (
        "which file do I edit to add a field to a doctype",
        "what goes in hooks.py and what goes in the doctype python file",
        "difference between pre_model_sync and post_model_sync in patches.txt",
        "what is modules.txt for in a frappe app",
        "where does frappe load the client script for a doctype form",
        "do I need a fixtures folder or a patch to ship this record",
        "what are all the files in a frappe app and which ones matter",
        "is the config folder in an app still used or is it the workspace",
        "what is test_records.json and when does it run",
        "app structure",
        "directory layout",
    ),
    "choosing-a-naming-rule-and-keeping-the-tests-off-its-counter.md": (
        "my test suite is eating invoice numbers",
        "does running tests move the real naming series",
        "which naming rule should i pick for a doctype",
        "i set autoname but the numbers are not going up",
        "how do i reset a naming series counter safely",
        "my fixture pinned the names and now i get a duplicate entry error",
        "does renaming a document change the series number",
        "two naming series doctypes are sharing the same counter",
        "where does frappe store the naming counter",
        "naming series",
        "autoname pattern",
    ),
    "what-actually-sends-and-what-only-queues.md": (
        "notification is enabled but no email arrives",
        "emails stuck in Not Sent and no error anywhere",
        "does frappe.sendmail actually send the email",
        "why is nothing in the email queue after sendmail",
        "how do i stop all outgoing email on a site",
        "email queue row says Not Sent forever",
        "frappe notification not firing and nothing in error log",
        "does delayed=False send the email immediately",
        "who actually sends the email queue",
        "email sending pipeline",
        "frappe.sendmail vs email queue",
    ),
    "where-a-workflow-checks-a-permission-and-where-it-does-not.md": (
        "user approved his own document even though self approval is off",
        "how do i stop someone editing a document after it is approved",
        "workflow state changed but the document is still a draft",
        "can a user skip the workflow by editing the state field",
        "does ignore_permissions skip the workflow check",
        "submit button approved the document without the workflow",
        "allow_edit role is not being enforced",
        "who actually approved this document",
        "cancelled document still shows approved state",
        "workflow permission enforcement",
        "workflow bypass",
    ),
    "who-may-run-a-report-and-what-it-is-allowed-to-read.md": (
        "who can run a report in frappe",
        "query report vs script report permissions",
        "can a print format run a database query",
        "my report shows rows the user should not see",
        "how do i restrict a report to one role",
        "custom report roles are ignored",
        "which report type respects user permissions",
        "what does the report permission on a doctype do",
        "report print format jinja not working",
        "report permission types",
        "who can run this report",
    ),
    "delivering-to-a-site-that-is-already-running.md": (
        "what order does migrate actually run things in",
        "my migrate failed halfway what is on the site now",
        "does bench --site all really migrate every site",
        "which config key came back after i ran a bench command",
        "migrate finished but search returns nothing",
        "fixture or customization which one wins on migrate",
        "nginx.conf keeps getting regenerated over my edit",
        "can i roll back a failed migrate",
        "why did restart_supervisor_on_update change by itself",
        "bench migrate",
        "deploy an update to a live site",
    ),
    "the-four-public-routes-and-which-one-checks-a-permission.md": (
        "does a web page check permissions",
        "guest can open my portal page",
        "how do i make a public page in frappe",
        "web form or www page which one is safer",
        "why does my portal record give 404 instead of 403",
        "is whitelist enough to protect an endpoint",
        "which public route checks the doctype permission",
        "let a visitor submit a form without logging in",
        "allow_guest_to_view",
        "public website routes in frappe",
        "guest accessible pages",
    ),
    "the-frappe-ui-data-layer-and-which-call-refetches.md": (
        "frappe-ui createResource vs useDoc which one should I use",
        "createDocumentResource does not update when the route parameter changes",
        "createListResource or useList which one caches the rows",
        "why does my list change when I open a detail page in frappe-ui",
        "frappe-ui reload vs fetch which one actually refetches",
        "two components using useDoc on the same document share state",
        "does the frappe-ui cache survive a page reload",
        "second createResource with the same cache key ignored my options",
        "frappe-ui resource onError but it still throws",
        "frappe-ui data fetching",
        "which frappe-ui composable to use",
    ),
    "what-a-backup-carries-and-what-a-restore-cannot-bring-back.md": (
        "what does bench backup actually include",
        "does a frappe backup include the uploaded files",
        "restore lost all the passwords",
        "encryption key is invalid after restore",
        "what bench restore does not bring back",
        "do I need to run migrate after a restore",
        "does bench restore drop the existing database",
        "my backup files disappeared from private backups",
        "is the -enc backup file really encrypted",
        "bench backup contents",
        "restore a site backup",
    ),
    "fixtures-seed-migrate.md": (
        "fixture or patch or seed",
        "how do i ship data with an app",
        "my fixture did not install",
        "migrate did not update my records",
        "who owns the row after install",
        "fixtures vs seeds vs patches",
        "ship data with an app",
    ),
    "frappe-is-shorter-than-you-wrote-it.md": (
        "is there a shorter way to write this",
        "what does frappe already give me for this loop",
        "one line instead of a query",
        "frappe utility functions",
        "shorter frappe idiom",
    ),
    "frappe-translation-methodology.md": (
        "how do i translate my app",
        "my arabic string is not showing",
        "where does ar.csv go",
        "translation not applied",
        "translate a frappe app",
        "app translation workflow",
    ),
    "lifecycle-and-hooks.md": (
        "why is my hook not firing",
        "what order do validate and before_save run in",
        "on_submit did not run",
        "doc_events is ignored",
        "how do i scaffold a doctype",
        "doctype lifecycle hooks",
        "document event order",
    ),
    "page-layout-sketches.md": (
        "how should I lay out this page",
        "what layout suits a list heavy screen",
        "which page layout do I pick",
        "page layout template",
        "layout sketch",
        "how do I arrange the regions of a desk page",
        "what changes in my layout under right to left",
        "rtl layout",
    ),
    "page-layouts-command-console-dashboard-guided-batch.md": (
        "how do i build a command palette page",
        "what layout suits a dashboard summary screen",
        "how do i design a bulk action wizard",
        "command console layout",
        "dashboard first layout",
        "guided batch layout",
        "my sidebar markup is not showing up",
        "wizard stepper mirrors wrong under rtl",
    ),
    "permissions.md": (
        "why can this user not see the list",
        "permission denied but the role has read",
        "if_owner is not working",
        "how do i hide a doctype from a role",
        "portal user cannot open the record",
        "frappe permission system",
        "who can see this record",
    ),
    "talking-to-an-outside-service.md": (
        "how do i call an external api",
        "where do i keep an api key",
        "how do i retry a failed request",
        "how do i log an outgoing call",
        "call an external api",
        "integrate with a third party",
    ),
    "theming-what-survives-an-update.md": (
        "my css was overwritten by an update",
        "how do i customise the desk theme",
        "where do i put custom scss",
        "how do i change the logo",
        "customize the frappe desk theme",
        "css that survives an update",
    ),
    "writing-tests-the-frappe-way.md": (
        "how do i write a frappe test",
        "test_records is not loading",
        "how do i run one test",
        "my test passes against nothing",
        "frappe testing conventions",
        "how to write a frappe test",
    ),
}

_HEADING = re.compile(r"^(#{1,3})\s+(.*\S)\s*$")
_HEADING_LEAD = re.compile(
    r"^(?:\u00a7\d+\s*[\u2014-]?\s*|part\s+\d+[a-z]?\s*[\u2014-]\s*|node\s*[\u2014-]\s*"
    r"|edge\s*[\u2014-]\s*|\d+(?:\.\d+)*\s*[.\u2014-]?\s*)",
    re.IGNORECASE,
)
_HEADING_TAIL = re.compile(r"\s*\(\u00a7?[^)]*\)\s*$")
_HEADING_TICK = re.compile(r"`([^`]+)`")
_HEADING_PART = re.compile(r"^part \d+[a-z]?$")
_HEADING_NOISE = frozenset({
    "node", "edge", "index", "rules", "options", "purpose", "the question",
    "the graph", "the file", "core rule",
})


TASK_QUESTIONS: dict[str, list[str]] = {
    "build-a-vue-front-end-on-frappe-ui.md": [
        "build a vue app on frappe",
        "frappe-ui data layer",
        "createresource or usedoc",
        "my list does not refresh",
        "save sends every field",
        "paging duplicates rows",
        "dark mode does not switch",
        "socket updates repeat",
        "frappe-ui frontend",
    ],
    "call-an-outside-service-or-be-called-by-one.md": [
        "call an external api from frappe",
        "expose an endpoint",
        "my webhook did not fire",
        "integrate with a third party service",
        "where do i put an api key",
        "oauth refresh token",
        "receive a callback",
        "verify an incoming request",
        "outbound and inbound integration",
    ],
    "change-a-doctype-without-breaking-its-lifecycle.md": [
        "add a field to a doctype",
        "rename a field",
        "change autoname",
        "my validate does not run",
        "what order do the hooks run in",
        "submit and cancel",
        "doctype schema change",
        "index not created",
        "modify a doctype safely",
    ],
    "decide-who-can-read-or-change-a-record.md": [
        "how do i restrict who sees this",
        "hide a record from a user",
        "limit a list to the user's own rows",
        "role permission not working",
        "user permission not filtering",
        "restrict one field",
        "permlevel",
        "who can open this report",
        "guest can see my page",
        "record level permissions",
    ],
    "plan-and-generate-a-new-frappe-app.md": [
        "create a new frappe app",
        "generate a doctype from a plan",
        "what to decide before bench new-app",
        "my doctype disappeared after migrate",
        "which decisions cannot be changed later",
        "modules.txt and the module folder",
        "ship permissions with an app",
        "naming series prefix already used",
        "plan and generate an app",
    ],
    "publish-a-public-page-or-a-portal-form.md": [
        "publish a public page",
        "web form",
        "portal page",
        "guest cannot open my page",
        "my route returns the wrong page",
        "let a visitor submit a form",
        "website route",
        "translate the portal",
        "public facing page in frappe",
    ],
    "ship-a-customisation-to-another-site.md": [
        "how do i ship this to another site",
        "deploy a customisation",
        "fixture or patch or custom field",
        "my custom field did not appear on the other site",
        "move a doctype change between sites",
        "ship data with an app",
        "install app on an existing site",
        "migrate did not bring my change",
        "uninstall did not remove it",
        "move a customisation between sites",
    ],
    "ship-the-first-run-an-app-puts-in-front-of-a-user.md": [
        "onboarding for a new app",
        "what the user sees on the first run",
        "module onboarding step not completing",
        "form tour does not start",
        "my toolbar buttons are duplicated",
        "ship a server script with an app",
        "print style restyles the whole desk",
        "web template renders the wrong file",
        "first run records an app ships",
    ],
    "write-and-run-tests-for-a-frappe-app.md": [
        "how do i test this",
        "bench run-tests",
        "test records",
        "my suite passed but nothing ran",
        "assert a validation error",
        "test rollback between tests",
        "before_tests",
        "frappe test suite",
    ],
}


def _sheet_headings(text: str) -> list[str]:
    found: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = _HEADING.match(line)
        if match:
            found.append(match.group(2))
    return found


def _sheet_triggers(sheet: Path) -> list[str]:
    questions = SHEET_QUESTIONS.get(sheet.name)
    if questions is None:
        raise ValueError(
            f"{sheet.name} has no reader questions in SHEET_QUESTIONS, so the index would carry a "
            "sheet no reader word can reach"
        )
    words = [*questions, sheet.stem.replace("-", " ")]
    for heading in _sheet_headings(sheet.read_text(encoding="utf-8")):
        for part in _HEADING_TAIL.sub("", heading).split(" \u2014 "):
            part = _HEADING_LEAD.sub("", part).strip().strip(".,;:")
            for candidate in [_HEADING_TICK.sub(r"\1", part), *_HEADING_TICK.findall(part)]:
                candidate = re.sub(r"\s+", " ", candidate).strip().lower()
                if len(candidate) < 3 or not re.search(r"[a-z]{3}", candidate):
                    continue
                if candidate in _HEADING_NOISE or _HEADING_PART.match(candidate):
                    continue
                words.append(candidate)
    cleaned = [re.sub(r"\s+", " ", w.replace(",", " ").replace("\t", " ")).strip()
               for w in words]
    return list(dict.fromkeys(w for w in cleaned if w))


def _joined(words: list[str], where: str) -> str:
    for word in words:
        if "," in word or "\t" in word:
            raise ValueError(
                f"{where} carries a trigger with a comma or a tab — {word!r} — and the index joins "
                "triggers with a comma inside a tab-separated row, so the phrase would split"
            )
    return ", ".join(words)


TREE_ROOTS = ("knowledge", "references", "tasks")

_CLAUSE = re.compile(r"[,;\u2014]")
_CLAUSE_LEAD = re.compile(r"^(?:and|or|but|so|then|because|which|that)\s+", re.IGNORECASE)


def _tree_files(suite_root: Path) -> list[str]:
    root = suite_root.expanduser().resolve()
    found: list[str] = []
    for branch in TREE_ROOTS:
        for path in (root / branch).rglob("*.md"):
            if path.name == "README.md":
                continue
            found.append(path.relative_to(root).as_posix())
    return sorted(found)


def _tree_front(leaf: Path) -> dict[str, Any]:
    text = leaf.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(
            f"{leaf} carries no frontmatter, so the tree states no name, description or product "
            "for it and the index cannot build its row"
        )
    front: dict[str, Any] = {}
    for line in text.split("---\n", 2)[1].splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(": ")
        if not separator:
            raise ValueError(f"{leaf}: frontmatter line is not `key: value` \u2014 {line!r}")
        value = value.strip()
        front[key] = json.loads(value) if value[:1] in "[{\"" else value
    if front.get("product") not in PRODUCTS:
        raise ValueError(
            f"{leaf}: frontmatter names product {front.get('product')!r}, and the index only "
            f"carries a leaf whose product is one of {sorted(PRODUCTS)}"
        )
    return front


def _described(sentence: str) -> list[str]:
    words = []
    for part in _CLAUSE.split(sentence):
        candidate = re.sub(r"\s+", " ", part.replace("\t", " ")).strip().strip(".,;:")
        candidate = _CLAUSE_LEAD.sub("", _HEADING_LEAD.sub("", candidate)).strip()
        if len(candidate) < 3 or not re.search(r"[A-Za-z]{3}", candidate):
            continue
        words.append(candidate.lower())
    return words


def _leaf_triggers(relative: str, front: dict[str, Any]) -> list[str]:
    words: list[str] = []
    if front.get("name"):
        words.append(str(front["name"]))
    if front.get("description"):
        words.extend(_described(str(front["description"])))
    words.extend(str(one) for one in front.get("triggers", []))
    words.append(Path(relative).stem.replace("-", " "))
    cleaned = (re.sub(r"\s+", " ", word).strip() for word in words)
    return list(dict.fromkeys(word for word in cleaned if word))


def _index_rows(suite_root: Path) -> list[tuple[str, str, str, str]]:
    suite_root = suite_root.expanduser().resolve()
    rows: list[tuple[str, str, str, str]] = []
    for relative in _tree_files(suite_root):
        if not relative.startswith("knowledge/"):
            continue
        front = _tree_front(suite_root / relative)
        source = front.get("source") or {}
        rows.append((
            _joined(_leaf_triggers(relative, front), relative),
            relative,
            f"{source.get('path', '-')}:{source.get('lines', '-')}" if source else "-",
            str(front.get("verified_version", "-")),
        ))
    for sheet in sorted((suite_root / "references").glob("*.md")):
        rows.append((
            _joined(_sheet_triggers(sheet), sheet.name),
            f"references/{sheet.name}",
            "-",
            "-",
        ))
    for page in sorted((suite_root / "tasks").glob("*.md")):
        questions = TASK_QUESTIONS.get(page.name)
        if questions is None:
            raise ValueError(
                f"{page.name} has no reader questions in TASK_QUESTIONS, so the index would carry a "
                "task page no reader word can reach"
            )
        rows.append((_joined(list(questions), page.name), f"tasks/{page.name}", "-", "-"))
    return rows


def index_text(suite_root: Path) -> str:
    lines = ["\t".join(INDEX_COLUMNS)]
    lines.extend("\t".join(row) for row in _index_rows(suite_root))
    return "\n".join(lines) + "\n"


def reindex(suite_root: Path, write: bool) -> tuple[bool, str]:
    suite_root = suite_root.expanduser().resolve()
    path = suite_root / INDEX_NAME
    wanted = index_text(suite_root)
    found = path.read_text(encoding="utf-8") if path.is_file() else ""
    if found == wanted:
        return True, f"{INDEX_NAME} agrees with the tree"
    if not write:
        return False, (
            f"{INDEX_NAME} disagrees with the tree \u00b7 regenerate it with "
            "python3 tools/build_index.py index"
        )
    path.write_text(wanted, encoding="utf-8")
    return True, f"{path} \u00b7 {len(wanted.encode('utf-8'))} bytes \u00b7 {wanted.count(chr(10)) - 1} rows"


RELATIONS_NAME = "RELATIONS.tsv"
RELATIONS_COLUMNS = ("hops", "file", "leaf")

_POINTER = re.compile(r"(?:knowledge|references|tasks)/[A-Za-z0-9/._-]+\.md")
_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")


def _pointers(suite_root: Path) -> dict[str, list[str]]:
    root = suite_root.expanduser().resolve()
    files = _tree_files(root)
    known = set(files)
    by_stem: dict[str, list[str]] = {}
    for relative in files:
        by_stem.setdefault(Path(relative).stem, []).append(relative)
    stated: dict[str, list[str]] = {}
    for relative in files:
        text = (root / relative).read_text(encoding="utf-8")
        found: set[str] = set()
        for target in _POINTER.findall(text):
            if target in known and target != relative:
                found.add(target)
        for link in _WIKILINK.findall(text):
            stem = Path(link).stem if "/" in link else link.rsplit(".", 1)[-1]
            candidates = by_stem.get(stem, [])
            if len(candidates) == 1 and candidates[0] != relative:
                found.add(candidates[0])
        stated[relative] = sorted(found)
    return stated


def _relation_rows(suite_root: Path) -> list[tuple[str, ...]]:
    stated = _pointers(suite_root)
    rows: list[tuple[str, ...]] = []
    for entry in sorted(one for one in stated if one.startswith("tasks/")):
        routes: dict[str, tuple[str, ...]] = {entry: (entry,)}
        frontier = [entry]
        while frontier:
            reached: list[str] = []
            for here in frontier:
                for target in stated[here]:
                    if target in routes:
                        continue
                    routes[target] = routes[here] + (target,)
                    reached.append(target)
            frontier = sorted(reached)
        rows.extend(route for target, route in sorted(routes.items())
                    if target.startswith("knowledge/"))
    return rows


def relations_text(suite_root: Path) -> str:
    lines = ["\t".join(RELATIONS_COLUMNS)]
    lines.extend("\t".join(row) for row in _relation_rows(suite_root))
    return "\n".join(lines) + "\n"


def rerelate(suite_root: Path, write: bool) -> tuple[bool, str]:
    suite_root = suite_root.expanduser().resolve()
    path = suite_root / RELATIONS_NAME
    wanted = relations_text(suite_root)
    found = path.read_text(encoding="utf-8") if path.is_file() else ""
    if found == wanted:
        return True, f"{RELATIONS_NAME} agrees with the tree"
    if not write:
        return False, (
            f"{RELATIONS_NAME} disagrees with the tree \u00b7 regenerate it with "
            "python3 tools/build_index.py relations"
        )
    path.write_text(wanted, encoding="utf-8")
    return True, (f"{path} \u00b7 {len(wanted.encode('utf-8'))} bytes \u00b7 "
                  f"{wanted.count(chr(10)) - 1} routes")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild INDEX.tsv and RELATIONS.tsv from the tree."
    )
    parser.add_argument("--root", type=Path, default=SUITE_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("index", "relations"):
        one = sub.add_parser(name)
        one.add_argument("--check", action="store_true",
                         help="Report disagreement and exit 1 without writing")
    args = parser.parse_args(argv)
    build = reindex if args.command == "index" else rerelate
    agreed, message = build(args.root, write=not args.check)
    print(message)
    return 0 if agreed else 1


if __name__ == "__main__":
    raise SystemExit(main())
