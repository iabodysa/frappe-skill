---
name: bench-root
description: The bench root is derived from where the frappe package is imported from, three levels up, so a second checkout on disk is only source and the root that answers is the one whose sites directory holds a site_config.json.
triggers: ["get_bench_path", "FRAPPE_BENCH_ROOT", "get_bench_id", "get_sites", "get_site_path", "sites_path", "bench_id", "site_config.json", "common_site_config.json", "__version__", "apps", "sites", "env", "where is frappe installed", "which bench is live", "two frappe checkouts", "installed source path", "frappe source location", "which version am I reading", "i edited the file and nothing changed on the running site", "my change has no effect no matter how many times i restart", "am i editing the copy the site actually uses", "there are two copies of the same code on this machine", "which folder is the live one and which one is just a leftover", "how do i tell where the running code is actually installed", "the function i read about does not behave the way the file says", "the code i am reading does not match what the system does", "why does the version on disk differ from the version the site reports", "a script reads the wrong folder when i run it from somewhere else"]
product: frappe
---

# Bench Root

## paths

frappe/utils/__init__.py — get_bench_path, get_bench_id, get_sites, get_site_path, get_files_path
frappe/__init__.py — get_app_path, get_pymodule_path, get_module, __version__
frappe/installer.py — install_app, update_site_config

## rules

MUST derive the bench root from the imported frappe package rather than from a directory name, because get_bench_path returns FRAPPE_BENCH_ROOT when it is set and otherwise the realpath three levels above `frappe.__file__`, and no name on disk enters that answer.
MUST read a directory as a bench root only when it holds both `apps/frappe` and a `sites` directory, because get_sites lists the children of `sites` and get_site_path joins under it; a checkout carrying `apps` alone is source with no site to serve.
MUST read a child of `sites` as a site only when it holds `site_config.json`, because get_sites skips a directory without that file and skips a symlink outright.
MUST prove the version before citing a file from a checkout — read `apps/frappe/frappe/__init__.py` for `__version__` and match it against the version the running site reports — because two checkouts of different major versions carry the same file names and the same symbol names.
NEVER pick between two checkouts by path length, by directory name or by modification time; the name carries no claim about which one the site imports.
MUST set FRAPPE_BENCH_ROOT when a process must read one root while its working directory sits under another, because get_bench_path consults that variable first and every path helper built on it follows.
NEVER read a version claimed in a file header, a project instruction file or a page comment as the installed version; the only authority is `__version__` in the checkout the site imports.

## values

get_bench_path with FRAPPE_BENCH_ROOT set: that value, unresolved
get_bench_path with it unset: realpath of `frappe.__file__` + `../../..`
bench root shape: `apps/`, `sites/`, `env/`, `config/`, `logs/`
app source root: `<bench>/apps/<app>/<app>`
site directory test: is a directory, is not a symlink, holds `site_config.json`
sites_path default in get_sites: `frappe.local.sites_path`, else `.`
bench_id: the `bench_id` conf key, else the bench path with `/` replaced by `-`
version file: `<bench>/apps/<app>/<app>/__init__.py`, symbol `__version__`

## how

The framework never searches for its own installation. It imports `frappe`, takes the file that import resolved to, and walks up three directories — package, app repository, apps — to name the bench. So the question "where is the installed source" has one mechanical answer for any process that can import frappe, and it does not depend on a convention about where benches are kept.

That makes a second checkout on the same machine harmless and invisible at once. Nothing the framework does will ever look at it, so it cannot cause a wrong answer at runtime; but a reader who opens it by hand gets a different file with the same path inside the app and the same symbol names, and the difference between major versions is exactly where behaviour changed. The check that separates them is cheap and it is the version, not the location: read `__version__` out of the checkout, then compare it with what the site reports. A checkout that has no `sites` directory beside its `apps` has never served anything and cannot be the one the site imports.

The failure this prevents is a citation that is internally consistent and wrong. A symbol read from the wrong major version resolves, the surrounding code reads plausibly, and the rule derived from it is stated with a file and a symbol that both exist in the live tree too. Nothing in the reading announces the mismatch. Only the version comparison does, and it has to be made before the read, not after the conclusion.
