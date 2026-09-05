# Copyright (c) 2026, iabodysa

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from ctlkit import process_guards
from ctlkit.config import discover_config, load_toml_config

_DEFAULTS: dict[str, object] = {"package": "", "lang": "", "max_missing": 0, "max_stale": 0}


def script(base: Path, name: str) -> Path | None:
    for relative in (Path("scripts"), Path(".claude") / "tools" / "scripts"):
        candidate = base / relative / name
        if candidate.is_file():
            return candidate
    return None


def delegate(target: Path, argv: list[str], cwd: Path) -> int:
    return subprocess.run([sys.executable, str(target), *argv], cwd=cwd).returncode


def capture(target: Path, argv: list[str], cwd: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(target), *argv], cwd=cwd,
        capture_output=True, text=True, check=False,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode or 1, {}


DELEGATED_GUARDS: tuple[tuple[str, list[str]], ...] = (
    ("check_doctype_dates.py", []),
    ("check_dangling_roles.py", []),
    ("check_lock_ordering.py", ["--baseline", "0"]),
    ("check_role_alert_reach.py", []),
)


def _process_guards(base: Path) -> tuple[int, list]:
    try:
        config = discover_config(base)
    except SystemExit:
        return 0, []
    declared = load_toml_config(base, quiet=True).get("guards", {})
    return process_guards.run(config, declared if isinstance(declared, dict) else {})


def forked_guards(base: Path, toolbox: Path | None = None) -> list[tuple[str, str, str]]:
    home = toolbox or Path(__file__).resolve().parent
    forked: list[tuple[str, str, str]] = []
    for candidate in sorted(home.glob("check_*.py")):
        shipped = script(base, candidate.name)
        if shipped is None:
            continue
        theirs = hashlib.sha256(shipped.read_bytes()).hexdigest()[:12]
        ours = hashlib.sha256(candidate.read_bytes()).hexdigest()[:12]
        if theirs != ours:
            forked.append((candidate.name, str(shipped), f"project {theirs} vs toolbox {ours}"))
    return forked


def unwired_hooks(base: Path) -> list[str]:
    hooks = base / ".githooks"
    if not hooks.is_dir():
        return []
    listed = subprocess.run(["git", "-C", str(base), "ls-files", ".githooks"],
                            capture_output=True, text=True)
    if listed.returncode != 0 or not listed.stdout.strip():
        return []
    tracked = sorted(Path(name).name for name in listed.stdout.split()
                     if Path(name).name in ("pre-commit", "pre-push", "commit-msg"))
    if not tracked:
        return []
    wired = subprocess.run(["git", "-C", str(base), "config", "--get", "core.hooksPath"],
                           capture_output=True, text=True)
    named = wired.stdout.strip()
    if named and (base / named).resolve() == hooks.resolve():
        return []
    return tracked


def wire_hooks(base: Path) -> list[str]:
    unwired = unwired_hooks(base)
    if not unwired:
        return []
    done = subprocess.run(["git", "-C", str(base), "config", "core.hooksPath", ".githooks"],
                          capture_output=True, text=True)
    if done.returncode != 0:
        return []
    for name in unwired:
        hook = base / ".githooks" / name
        if hook.is_file():
            hook.chmod(hook.stat().st_mode | 0o111)
    return [] if unwired_hooks(base) else unwired


def run_all(base: Path, package: str, as_json: bool = False) -> int:
    built_in, verdicts = _process_guards(base)
    unwired = unwired_hooks(base)
    wired = wire_hooks(base)
    if not as_json:
        process_guards.report(verdicts)
        if wired:
            print(f"guards: WIRED {', '.join(wired)} — {base} tracked them and core.hooksPath did "
                  "not reach them, so a clone carried these gates and fired none of them. They run "
                  "from the next commit. Undo with `git config --unset core.hooksPath`")
        elif unwired:
            print(f"guards: {base} TRACKS {', '.join(unwired)} and core.hooksPath does not reach "
                  "them — a clone carries these gates and fires none of them, and this run could "
                  "not repair it. Wire with `git config core.hooksPath .githooks`")
    forked = forked_guards(base)
    if forked and not as_json:
        for name, path, digests in forked:
            print(f"guards: {name} is FORKED — {path} differs from this toolbox ({digests}); "
                  "the project copy is what gates the push")
    results: dict[str, int] = {}
    for name, extra in DELEGATED_GUARDS:
        target = script(base, name)
        if target is None:
            continue
        results[name] = delegate(target, [package, *extra], base)
    worst = max([*results.values(), built_in], default=built_in)
    if as_json:
        print(json.dumps({"guards": results, "ok": worst == 0,
                          "unwired_hooks": unwired, "wired_hooks": wired,
                          "forked": [name for name, _, _ in forked],
                          "process": {v.name: {"population": v.population, "failures": v.failures}
                                      for v in verdicts}},
                         ensure_ascii=False, separators=(",", ":")))
    elif not results:
        print("guards: the project ships no delegated guard")
    return worst


def thresholds(base: Path) -> dict[str, object]:
    runner = base / "scripts" / "run_guards.sh"
    values = dict(_DEFAULTS)
    values["package"] = discover_config(base).app
    if not runner.is_file():
        return values
    proc = subprocess.run(
        ["sh", str(runner), "thresholds"], cwd=base,
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        return values
    try:
        loaded = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return values
    values.update({key: loaded[key] for key in values if key in loaded})
    return values
