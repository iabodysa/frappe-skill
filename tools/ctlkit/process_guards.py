# Copyright (c) 2026, iabodysa

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path

from ctlkit.config import ProjectConfig

DOTTED = re.compile(r"^[A-Za-z_][\w.]*$")


@dataclass
class Verdict:

    name: str
    population: int
    failures: list[str]

    @property
    def ok(self) -> bool:
        return self.population > 0 and not self.failures

    def line(self) -> str:
        if self.population == 0:
            return f"{self.name}: REFUSED — the scan found nothing to grade, so a pass proves nothing"
        if self.failures:
            return f"{self.name}: FAILED — {len(self.failures)} of {self.population}"
        return f"{self.name}: clean — {self.population} graded"


def guard_paths(config: ProjectConfig, declared: dict | None = None) -> dict[str, Path]:
    package = config.root / config.app
    values = {
        "package": package,
        "modules_txt": package / "modules.txt",
        "patches_txt": package / "patches.txt",
        "www": package / "www",
    }
    for key, raw in (declared or {}).items():
        if key in values and isinstance(raw, str) and raw.strip():
            values[key] = (config.root / raw.strip()).resolve()
    return values


def modules_are_alive(paths: dict[str, Path]) -> Verdict:
    listing = paths["modules_txt"]
    if not listing.is_file():
        return Verdict("modules.txt is alive", 0, [])
    package = paths["package"]
    declared = [line.strip() for line in listing.read_text(encoding="utf-8").splitlines() if line.strip()]
    missing = [
        name for name in declared
        if not (package / name.lower().replace(" ", "_")).is_dir()
    ]
    return Verdict("modules.txt is alive", len(declared),
                   [f"{name} is declared and has no directory" for name in missing])


def patches_are_registered(paths: dict[str, Path]) -> Verdict:
    listing = paths["patches_txt"]
    if not listing.is_file():
        return Verdict("every patch resolves", 0, [])
    root = paths["package"].parent
    entries, failures = [], []
    for raw in listing.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("["):
            continue
        dotted = line.split()[0]
        if not DOTTED.match(dotted):
            continue
        entries.append(dotted)
        module = root / Path(*dotted.split(".")).with_suffix(".py")
        if not module.is_file():
            failures.append(f"{dotted} names no file at {module.relative_to(root)}")
        elif "def execute(" not in module.read_text(encoding="utf-8"):
            failures.append(f"{dotted} defines no execute()")
    return Verdict("every patch resolves", len(entries), failures)


def www_controllers_have_templates(paths: dict[str, Path]) -> Verdict:
    www = paths["www"]
    if not www.is_dir():
        return Verdict("every web page has its template", 0, [])
    controllers = [
        path for path in sorted(www.rglob("*.py"))
        if not path.name.startswith("__") and not path.name.startswith("test_")
    ]
    failures = [
        f"{path.relative_to(www)} has no template beside it"
        for path in controllers
        if not _template_for(path)
    ]
    return Verdict("every web page has its template", len(controllers), failures)


def _template_for(controller: Path) -> Path | None:
    names = {controller.stem, controller.stem.replace("_", "-")}
    for name in names:
        for suffix in (".html", ".md"):
            candidate = controller.with_name(name + suffix)
            if candidate.is_file():
                return candidate
    return None


FRAMEWORK_TEST_APIS = frozenset({"frappe.test_runner", "frappe.tests.utils"})


def _imports_a_test_module(dotted: str | None, package: str) -> bool:
    if not dotted or dotted in FRAMEWORK_TEST_APIS:
        return False
    if not dotted.startswith((f"{package}.", ".")):
        return False
    return dotted.rsplit(".", 1)[-1].startswith("test_")


def no_cross_test_imports(paths: dict[str, Path]) -> Verdict:
    package = paths["package"]
    if not package.is_dir():
        return Verdict("no module imports a test module", 0, [])
    name = package.name
    files = [p for p in sorted(package.rglob("*.py")) if "__pycache__" not in p.parts]
    failures = []
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = path.relative_to(package)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level and not node.module:
                    failures += [f"{rel} imports {'.' * node.level}{alias.name}"
                                 for alias in node.names if alias.name.startswith("test_")]
                elif node.level and node.module:
                    if node.module.rsplit(".", 1)[-1].startswith("test_"):
                        failures.append(f"{rel} imports {'.' * node.level}{node.module}")
                elif _imports_a_test_module(node.module, name):
                    failures.append(f"{rel} imports {'.' * node.level}{node.module}")
            elif isinstance(node, ast.Import):
                failures += [f"{rel} imports {alias.name}" for alias in node.names
                             if _imports_a_test_module(alias.name, name)]
    return Verdict("no module imports a test module", len(files), failures)


MIN_RANDOM_CHARACTERS = 12


def _hash_length(call: ast.Call) -> ast.AST | None:
    name = call.func.id if isinstance(call.func, ast.Name) else getattr(call.func, "attr", None)
    if name != "generate_hash":
        return None
    for keyword in call.keywords:
        if keyword.arg == "length":
            return keyword.value
    return call.args[0] if call.args else None


def fixture_identifiers_are_long_enough(paths: dict[str, Path]) -> Verdict:
    package = paths["package"]
    if not package.is_dir():
        return Verdict("fixture identifiers carry enough entropy", 0, [])
    files = [p for p in sorted(package.rglob("test_*.py")) if "__pycache__" not in p.parts]
    failures = []
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            length = _hash_length(node)
            if isinstance(length, ast.Constant) and isinstance(length.value, int) \
                    and length.value < MIN_RANDOM_CHARACTERS:
                failures.append(f"{path.relative_to(package)}:{node.lineno} "
                                f"generate_hash(length={length.value}) is under {MIN_RANDOM_CHARACTERS}")
    return Verdict("fixture identifiers carry enough entropy", len(files), failures)


def standard_records_match_their_folder(paths: dict[str, Path]) -> Verdict:
    package = paths["package"]
    if not package.is_dir():
        return Verdict("a shipped record matches its folder", 0, [])
    records, failures = [], []
    for path in sorted(package.rglob("*.json")):
        if "__pycache__" in path.parts or "node_modules" in path.parts:
            continue
        if len(path.relative_to(package).parts) < 4:
            continue
        declared = _declared_doctype(path)
        if declared is None or scrub(declared) != path.parent.parent.name:
            continue
        records.append(path)
        if path.stem != path.parent.name:
            failures.append(f"{path.relative_to(package)} sits in a folder named "
                            f"{path.parent.name!r}")
    return Verdict("a shipped record matches its folder", len(records), failures)


def scrub(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").lower()


def _declared_doctype(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError, OSError):
        return None
    doctype = payload.get("doctype") if isinstance(payload, dict) else None
    return doctype if isinstance(doctype, str) and doctype.strip() else None


CHECKS = (modules_are_alive, patches_are_registered, www_controllers_have_templates,
          no_cross_test_imports, fixture_identifiers_are_long_enough,
          standard_records_match_their_folder)


def run(config: ProjectConfig, declared: dict | None = None) -> tuple[int, list[Verdict]]:
    paths = guard_paths(config, declared)
    verdicts = [check(paths) for check in CHECKS]
    worst = 0 if all(v.ok for v in verdicts) else 1
    return worst, verdicts


def report(verdicts: list[Verdict]) -> None:
    for verdict in verdicts:
        print(verdict.line())
        for failure in verdict.failures[:10]:
            print(f"    {failure}")
        if len(verdict.failures) > 10:
            print(f"    ... {len(verdict.failures) - 10} more")
