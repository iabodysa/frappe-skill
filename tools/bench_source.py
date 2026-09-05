#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa


from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


def _declared_bench() -> Path | None:
    declared = os.environ.get("FRAPPE_BENCH_ROOT")
    if declared:
        return Path(declared).expanduser()
    files = [Path(directory) / ".benchx.toml"
             for directory in [Path.cwd(), *Path.cwd().parents]]
    files.append(Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
                 / "benchx" / "config.toml")
    for candidate in files:
        if not candidate.is_file():
            continue
        try:
            with candidate.open("rb") as handle:
                config = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError):
            continue
        target = config.get("target", {})
        bench = target.get("bench") if isinstance(target, dict) else None
        if bench:
            return Path(bench).expanduser()
    return None


SEARCH_ROOTS = ("~", "~/Developer")


def _is_bench(path: Path) -> bool:
    return (path / "apps" / "frappe").is_dir() and (path / "sites").is_dir()


def bench_roots(search_roots: tuple[str, ...] | None = None) -> list[Path]:
    found: list[Path] = []
    for entry in search_roots or SEARCH_ROOTS:
        parent = Path(entry).expanduser()
        if not parent.is_dir():
            continue
        for child in sorted(parent.iterdir()):
            if not child.is_dir() or not _is_bench(child):
                continue
            resolved = child.resolve()
            if resolved not in found:
                found.append(resolved)
    return sorted(found)


def _default_bench_root(search_roots: tuple[str, ...] | None = None) -> Path:
    declared = _declared_bench()
    if declared is not None:
        return declared
    for directory in [Path.cwd(), *Path.cwd().parents]:
        if _is_bench(directory):
            return directory
    found = bench_roots(search_roots)
    if len(found) == 1:
        return found[0]
    searched = ", ".join(search_roots or SEARCH_ROOTS)
    if not found:
        raise ValueError(
            f"no bench under {searched}; set FRAPPE_BENCH_ROOT or [target].bench in .benchx.toml"
        )
    listed = ", ".join(str(item) for item in found)
    raise ValueError(
        f"the bench root is ambiguous between {listed}; "
        "set FRAPPE_BENCH_ROOT or [target].bench in .benchx.toml"
    )


def bench_root_for_site(site: str, search_roots: tuple[str, ...] | None = None) -> Path:
    found = bench_roots(search_roots)
    matches = [
        root for root in found if (root / "sites" / site / "site_config.json").is_file()
    ]
    listed = ", ".join(str(item) for item in found) or "none"
    if not matches:
        raise ValueError(f"no bench serves site {site}; searched {listed}")
    if len(matches) > 1:
        served = ", ".join(str(item) for item in matches)
        raise ValueError(f"site {site} is served by more than one bench: {served}")
    return matches[0]


def __getattr__(name: str) -> Path:
    if name == "DEFAULT_BENCH_ROOT":
        return _default_bench_root()
    raise AttributeError(name)

VERSION_PATTERN = re.compile(r'__version__\s*=\s*["\']([^"\']+)["\']')
BENCH_VERSION_PATTERN = re.compile(r'^VERSION\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
BENCH_PACKAGE_MARKER = Path("bench") / "config" / "common_site_config.py"


@dataclass(frozen=True)
class InstalledPackage:
    product: str
    consumer: str
    path: str
    version: str
    root: Path


def _frappe_ui_installs(bench_root: Path) -> list[InstalledPackage]:
    bench_root = bench_root.expanduser().resolve()
    apps_root = bench_root / "apps"
    installs: list[InstalledPackage] = []
    if not apps_root.is_dir():
        return installs

    for app_path in sorted(apps_root.iterdir(), key=lambda path: path.name):
        if not app_path.is_dir():
            continue
        app_root = app_path.resolve()
        for directory, child_dirs, _files in os.walk(app_root):
            current = Path(directory)
            child_dirs[:] = sorted(
                name
                for name in child_dirs
                if name != "node_modules" and not name.startswith(".")
            )
            if not (current / "package.json").is_file():
                continue
            package_path = current / "node_modules" / "frappe-ui" / "package.json"
            if not package_path.is_file():
                continue
            try:
                version = json.loads(package_path.read_text(encoding="utf-8")).get(
                    "version"
                )
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid frappe-ui package: {package_path}: {exc}") from exc
            if not version:
                raise ValueError(f"frappe-ui version missing: {package_path}")
            relative_root = package_path.parent.relative_to(app_root)
            installs.append(
                InstalledPackage(
                    product="frappe-ui",
                    consumer=app_path.name,
                    path=(Path("apps") / app_path.name / relative_root).as_posix(),
                    version=str(version),
                    root=package_path.parent,
                )
            )
    return sorted(installs, key=lambda install: install.path)


def _frappe_ui_root(bench_root: Path, expected_version: str | None = None) -> Path:
    candidates = _frappe_ui_installs(bench_root)
    if expected_version:
        matches = [item.root for item in candidates if item.version == expected_version]
        if matches:
            return matches[0]
        installed = ", ".join(sorted({item.version for item in candidates})) or "none"
        raise ValueError(f"frappe-ui {expected_version} not installed; found {installed}")
    if len(candidates) == 1:
        return candidates[0].root
    installed = ", ".join(sorted({item.version for item in candidates})) or "none"
    raise ValueError(f"frappe-ui {expected_version or ''} not uniquely installed; found {installed}")


def _bench_package_root(bench_root: Path) -> Path:
    candidates: list[Path] = []
    env_lib = bench_root.expanduser().resolve() / "env" / "lib"
    if env_lib.is_dir():
        candidates.extend(sorted(env_lib.glob("python*/site-packages")))
    try:
        spec = importlib.util.find_spec("bench")
    except (ImportError, ValueError):
        spec = None
    if spec and spec.origin:
        candidates.append(Path(spec.origin).resolve().parent.parent)
    for candidate in candidates:
        if (candidate / BENCH_PACKAGE_MARKER).is_file():
            return candidate
    raise ValueError(
        f"the bench package is installed neither under {bench_root}/env nor on sys.path"
    )


def _installed_version(
    bench_root: Path, product: str, expected_version: str | None = None
) -> str:
    if product == "frappe-ui":
        package_path = _frappe_ui_root(bench_root, expected_version) / "package.json"
        return json.loads(package_path.read_text(encoding="utf-8"))["version"]
    if product == "bench":
        init_path = _bench_package_root(bench_root) / "bench" / "__init__.py"
        pattern = BENCH_VERSION_PATTERN
    else:
        init_path = (
            bench_root.expanduser().resolve()
            / "apps"
            / product
            / product
            / "__init__.py"
        )
        pattern = VERSION_PATTERN
    if not init_path.is_file():
        raise FileNotFoundError(init_path)
    match = pattern.search(init_path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"version not found: {init_path}")
    return match.group(1)


def _source_root(
    bench_root: Path, product: str, expected_version: str | None = None
) -> Path:
    if product == "frappe-ui":
        return _frappe_ui_root(bench_root, expected_version)
    if product == "bench":
        return _bench_package_root(bench_root)
    return bench_root.expanduser().resolve() / "apps" / product


def resolve(
    product: str = "frappe",
    site: str | None = None,
    expected_version: str | None = None,
    search_roots: tuple[str, ...] | None = None,
) -> dict[str, str]:
    root = (
        bench_root_for_site(site, search_roots)
        if site
        else _default_bench_root(search_roots)
    )
    version = _installed_version(root, product)
    if expected_version and version != expected_version:
        raise ValueError(
            f"{product} {expected_version} is not the installed version; "
            f"{root} carries {version}"
        )
    return {
        "bench": str(root),
        "product": product,
        "version": version,
        "source_root": str(_source_root(root, product)),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="bench_source")
    parser.add_argument("--product", default="frappe")
    parser.add_argument("--site")
    parser.add_argument("--expect")
    args = parser.parse_args(argv)
    try:
        answer = resolve(args.product, args.site, args.expect)
    except (ValueError, FileNotFoundError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print("|".join(f"{key}={value}" for key, value in answer.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
