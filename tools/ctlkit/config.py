# Copyright (c) 2026, iabodysa

from __future__ import annotations

import os
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class AgentCommand:
    name: str
    bench_args: tuple[str, ...]
    safety: str
    derived_from: str
    description: str
    required_args: tuple[str, ...] = ()


AGENT_COMMANDS = {
    "migrate": AgentCommand(
        name="migrate",
        bench_args=("migrate",),
        safety="bench_write",
        derived_from="agent/site.py:migrate",
        description="Run bench migrate for the configured site.",
    ),
    "clear-cache": AgentCommand(
        name="clear-cache",
        bench_args=("clear-cache",),
        safety="bench_write",
        derived_from="agent/site.py:clear_cache",
        description="Clear Frappe site cache.",
    ),
    "clear-website-cache": AgentCommand(
        name="clear-website-cache",
        bench_args=("clear-website-cache",),
        safety="bench_write",
        derived_from="agent/site.py:clear_website_cache",
        description="Clear Frappe website cache.",
    ),
    "backup": AgentCommand(
        name="backup",
        bench_args=("backup", "--verbose"),
        safety="bench_write",
        derived_from="agent/site.py:backup",
        description="Create a site backup.",
    ),
    "install-app": AgentCommand(
        name="install-app",
        bench_args=("install-app", "{app}", "--force"),
        safety="bench_write",
        derived_from="agent/site.py:install_app",
        description="Install an app on the configured site, retrying without --force on older benches.",
        required_args=("app",),
    ),
    "console": AgentCommand(
        name="console",
        bench_args=("console",),
        safety="bench_write",
        derived_from="agent/site.py:run_app_scripts",
        description="Run a script through bench console stdin for the configured site.",
    ),
    "maintenance-on": AgentCommand(
        name="maintenance-on",
        bench_args=("set-maintenance-mode", "on"),
        safety="bench_write",
        derived_from="agent/site.py:enable_maintenance_mode",
        description="Enable site maintenance mode.",
    ),
    "maintenance-off": AgentCommand(
        name="maintenance-off",
        bench_args=("set-maintenance-mode", "off"),
        safety="bench_write",
        derived_from="agent/site.py:disable_maintenance_mode",
        description="Disable site maintenance mode.",
    ),
}

@dataclass(frozen=True)
class SourceString:
    text: str
    source: str
    kind: str


@dataclass
class ProjectConfig:
    root: Path
    app: str
    app_path: Path
    package_path: Path
    scan_roots: list[Path]
    lang: str
    translation_file: Path
    state_dir: Path
    todo_file: Path
    state_file: Path
    claude_command: str = "claude"
    claude_model: str = "claude-sonnet-4-5"
    claude_thinking: str = "high"
    bench_path: Path | None = None
    site: str | None = None
    agent_bench_command: str = "bench"
    agent_allow_bench_write: bool = False
    agent_allow_destructive: bool = False
    agent_state_file: Path | None = None
    agent_report_file: Path | None = None
    plans: dict = field(default_factory=dict)


@dataclass
class AgentRunResult:
    command_name: str
    command: list[str]
    status: str
    returncode: int | None
    duration_seconds: float
    output: str
    derived_from: str
    safety: str
    state_file: Path
    log_file: Path | None = None
    error: str | None = None

    def compact(self) -> dict[str, object]:
        return {
            "command_name": self.command_name,
            "status": self.status,
            "returncode": self.returncode,
            "duration_seconds": round(self.duration_seconds, 3),
            "command": self.command,
            "derived_from": self.derived_from,
            "safety": self.safety,
            "state_file": str(self.state_file),
            "log_file": str(self.log_file) if self.log_file else None,
            "error": self.error,
        }


@dataclass
class TranslateResult:
    config: ProjectConfig
    used: list[str]
    missing: list[str]
    stale: list[str]
    skipped_count: int = 0
    added_count: int = 0
    pruned_count: int = 0
    report_file: Path | None = None
    prompt_file: Path | None = None
    errors: list[str] = field(default_factory=list)
    label_warnings: list[tuple[str, str, str]] = field(default_factory=list)

    def compact(self) -> dict[str, object]:
        return {
            "app": self.config.app,
            "lang": self.config.lang,
            "translation_file": str(self.config.translation_file),
            "used_count": len(self.used),
            "missing_count": len(self.missing),
            "skipped_count": self.skipped_count,
            "stale_count": len(self.stale),
            "added_count": self.added_count,
            "pruned_count": self.pruned_count,
            "label_warning_count": len(self.label_warnings),
            "report_file": str(self.report_file) if self.report_file else None,
            "prompt_file": str(self.prompt_file) if self.prompt_file else None,
            "errors": self.errors,
        }


@dataclass
class ChangelogResult:
    config: ProjectConfig
    version: str
    file: Path
    index_file: Path
    created: bool
    index_updated: bool
    feed_file: Path | None = None
    feed_updated: bool = False

    def compact(self) -> dict[str, object]:
        return {
            "app": self.config.app,
            "version": self.version,
            "file": str(self.file),
            "index_file": str(self.index_file),
            "created": self.created,
            "index_updated": self.index_updated,
            "feed_file": str(self.feed_file) if self.feed_file else None,
            "feed_updated": self.feed_updated,
        }


def load_toml_config(root: Path, quiet: bool = False) -> dict[str, object]:
    config_file = root / ".ctl.toml"
    if not config_file.exists():
        return {}
    try:
        with config_file.open("rb") as handle:
            return tomllib.load(handle)
    except Exception:
        if quiet:
            return {}
        raise


def as_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


_GIT_TOPLEVEL_CACHE: dict[Path, Path | None] = {}


def git_toplevel(path: Path) -> Path | None:
    if path in _GIT_TOPLEVEL_CACHE:
        return _GIT_TOPLEVEL_CACHE[path]
    result: Path | None = None
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            result = Path(completed.stdout.strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        result = None
    _GIT_TOPLEVEL_CACHE[path] = result
    return result


def assert_same_checkout(start: Path, resolved: Path) -> None:
    if start == resolved:
        return
    start_top = git_toplevel(start)
    resolved_top = git_toplevel(resolved)
    if start_top is None or resolved_top is None or start_top == resolved_top:
        return
    raise SystemExit(
        "frappe-pipes: refusing to grade a different checkout than the one you named.\n"
        f"  asked for: {start}\n"
        f"             git checkout {start_top}\n"
        f"  resolved:  {resolved}/.ctl.toml\n"
        f"             git checkout {resolved_top}\n"
        "That config belongs to another checkout, so every verdict would describe it and not the "
        f"tree you asked about. Put a .ctl.toml in {start_top} to make it its own project."
    )


def find_root(start: Path, explicit: bool = False) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    global_cfg = Path.home() / ".ctl.toml"
    for candidate in [current, *current.parents]:
        toml = candidate / ".ctl.toml"
        if toml.exists() and toml != global_cfg:
            assert_same_checkout(current, candidate)
            return candidate
    for candidate in [current, *current.parents]:
        if (candidate / "sites" / "apps.txt").exists() and (candidate / "apps").exists():
            return candidate
        if (candidate / "modules.txt").exists() and (candidate / "translations").exists():
            return candidate.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".ctl").is_dir() or (candidate / ".git").exists():
            return candidate
    if explicit and current.is_dir():
        for child in sorted(path for path in current.iterdir() if path.is_dir()):
            if (child / "modules.txt").exists() and (child / "translations").exists():
                return current
        raise SystemExit(
            f"frappe-pipes: --root {current} holds no Frappe app — no .ctl.toml, no bench layout, and no "
            "<app>/modules.txt beside a translations/ dir. Refusing to fall back to the default project."
        )
    if global_cfg.exists():
        data = load_toml_config(global_cfg.parent, quiet=True)
        default = data.get("global", {}).get("default_project")
        if default:
            return Path(default).expanduser().resolve()
    return current


def registered_projects() -> dict[str, str]:
    global_cfg = Path.home() / ".ctl.toml"
    if not global_cfg.exists():
        return {}
    table = load_toml_config(global_cfg.parent, quiet=True).get("projects", {})
    if not isinstance(table, dict):
        return {}
    return {str(name): str(path) for name, path in table.items()}


def resolve_project(root: Path | str | None) -> Path | str | None:
    if root is None:
        return root
    text = str(root)
    if not text or text in (".", "..") or os.sep in text or text.startswith("~"):
        return root
    if Path(text).exists():
        return root

    known = registered_projects()
    if text in known:
        return Path(known[text]).expanduser().resolve()
    if known:
        names = ", ".join(sorted(known))
        raise SystemExit(f"frappe-pipes: no project named '{text}'. Registered: {names}")
    raise SystemExit(
        f"frappe-pipes: no project named '{text}', and ~/.ctl.toml declares no [projects] table. "
        "Add one mapping short names to paths, or pass a path."
    )


def discover_config(root: Path | str | None = None, lang: str | None = None) -> ProjectConfig:
    root = resolve_project(root)
    named = root is not None and str(root) not in ("", ".")
    base = find_root(Path(root or "."), explicit=named)
    raw = load_toml_config(base)
    project = raw.get("project", {}) if isinstance(raw.get("project", {}), dict) else {}
    translations = raw.get("translations", {}) if isinstance(raw.get("translations", {}), dict) else {}
    claude = raw.get("claude", {}) if isinstance(raw.get("claude", {}), dict) else {}
    agent = raw.get("agent", {}) if isinstance(raw.get("agent", {}), dict) else {}
    plans = raw.get("plans", {}) if isinstance(raw.get("plans", {}), dict) else {}

    app = str(project.get("app") or "")
    if not app:
        apps_txt = base / "sites" / "apps.txt"
        if apps_txt.exists():
            app_names = [
                line.strip()
                for line in apps_txt.read_text(encoding="utf-8").splitlines()
                if line.strip() and line.strip() not in {"frappe", "erpnext"}
            ]
            if app_names:
                app = app_names[0]
    if not app:
        direct_modules = list(base.glob("*/modules.txt"))
        if direct_modules:
            app = direct_modules[0].parent.name
    if not app:
        raise SystemExit("Unable to discover Frappe app. Add .ctl.toml with [project].app.")

    selected_lang = lang or str(project.get("language") or "")
    configured_app_path = project.get("app_path")
    configured_package_path = project.get("package_path")
    app_path = (base / str(configured_app_path)).resolve() if configured_app_path else base / "apps" / app
    package_path = (
        (base / str(configured_package_path)).resolve()
        if configured_package_path
        else app_path / app
    )
    if not configured_package_path and not package_path.exists() and (base / app).exists():
        app_path = base
        package_path = base / app
    if not package_path.exists():
        raise SystemExit(f"Unable to find app package for {app}: {package_path}")

    declared_roots = translations.get("scan_roots")
    if declared_roots and not isinstance(declared_roots, list):
        raise SystemExit("[translations].scan_roots must be a list of directories "
                         "relative to .ctl.toml.")
    scan_roots = [package_path]
    if declared_roots:
        scan_roots = []
        for entry in declared_roots:
            root = (base / str(entry)).resolve()
            if not root.is_dir():
                raise SystemExit(f"[translations].scan_roots names {entry!r}, which is not "
                                 f"a directory at {root}. A root that does not exist scans "
                                 "nothing and reports a clean run.")
            scan_roots.append(root)

    configured_file = project.get("translation_file")
    translation_file = (
        (base / str(configured_file)).resolve()
        if configured_file
        else package_path / "translations" / f"{selected_lang or 'unnamed-language'}.csv"
    )
    configured_tasks_dir = project.get("tasks_dir")
    state_dir = Path(str(configured_tasks_dir)).expanduser().resolve() if configured_tasks_dir else base / ".ctl"
    todo_file = base / str(translations.get("todo_file") or ".ctl/translates-todo.md")
    state_file = base / str(translations.get("state_file") or ".ctl/translates-state.json")
    configured_bench_path = project.get("bench_path") or agent.get("bench_path")
    bench_path = (base / str(configured_bench_path)).resolve() if configured_bench_path else base
    configured_site = project.get("site") or agent.get("site") or agent.get("default_site")
    agent_state_file = base / str(agent.get("state_file") or ".ctl/agent-state.json")
    agent_report_file = base / str(agent.get("report_file") or ".ctl/agent-runs.md")
    return ProjectConfig(
        root=base,
        app=app,
        app_path=app_path,
        package_path=package_path,
        scan_roots=scan_roots,
        lang=selected_lang,
        translation_file=translation_file,
        state_dir=state_dir,
        todo_file=todo_file,
        state_file=state_file,
        claude_command=str(claude.get("command") or "claude"),
        claude_model=str(claude.get("model") or "claude-sonnet-4-5"),
        claude_thinking=str(claude.get("thinking") or "high"),
        bench_path=bench_path,
        site=str(configured_site) if configured_site else None,
        agent_bench_command=str(agent.get("bench_command") or "bench"),
        agent_allow_bench_write=as_bool(agent.get("allow_bench_write"), False),
        agent_allow_destructive=as_bool(agent.get("allow_destructive"), False),
        plans=dict(plans),
        agent_state_file=agent_state_file,
        agent_report_file=agent_report_file,
    )
