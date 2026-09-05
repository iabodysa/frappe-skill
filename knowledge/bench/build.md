---
name: build
description: bench build reads each app's public/build.json, writes bundles into sites/assets/<app>/dist with sites/assets/assets.json as the map from source name to hashed output, links every app's public folder into sites/assets, compiles that app's translations, and downloads frappe's prebuilt assets instead of building them unless --force, --apps or CI is set.
triggers: ["build", "bundle", "download_frappe_assets", "build_missing_files", "get_assets_link", "fetch_assets", "setup_assets", "generate_assets_map", "make_asset_dirs", "link_assets_dir", "clear_broken_symlinks", "symlink", "check_node_executable", "get_node_env", "get_safe_max_old_space_size", "compile_translations", "get_build_json", "get_build_json_path", "get_apps_list", "write_assets_json", "assets.json", "build.json", "hard-link", "save-metafiles", "bench build produces", "assets not updating", "sites/assets", "the page still shows the old file after i changed it", "my style change never appears in the browser no matter what i do", "why do my edits to the front end not show up on the site", "the new image i added returns not found", "a file i put in the public folder is not reachable from the browser", "why can the site not see a file i just added to the app", "the rebuild finished but nothing about the site changed", "it says done but the framework itself was never rebuilt", "why does rebuilding skip part of the system", "the second rebuild fails with a timeout while another one is running", "our app is ignored completely when everything is rebuilt", "the translated labels never refresh until i do something else", "the page shows the same old thing no matter what i change"]
product: frappe
---

# Build

## paths

frappe/commands/utils.py — build, watch
frappe/build.py — bundle, setup, download_frappe_assets, build_missing_files, get_assets_link, fetch_assets, setup_assets, generate_assets_map, make_asset_dirs, link_assets_dir, clear_broken_symlinks, symlink, check_node_executable, get_node_env, get_safe_max_old_space_size
frappe/gettext/translate.py — compile_translations
frappe/__init__.py — get_all_apps, get_app_source_path
frappe/utils/synchronization.py — filelock
esbuild/utils.js — get_build_json, get_build_json_path, get_apps_list, get_public_path
esbuild/esbuild.js — write_assets_json, get_rebuilt_assets

## rules

MUST declare every bundle an app ships in `<app>/<app>/public/build.json`; `get_build_json` returns nothing when the file is absent and the app is then built with no entry points and no error.
MUST read `sites/assets/assets.json` as the map a page resolves through; esbuild writes the source bundle name against the hashed output path there, and a template asking for a name that file does not carry gets nothing.
MUST pass `--force` to rebuild frappe itself; with no `--force`, no `--apps` and no `CI` in the environment, `download_frappe_assets` fetches a prebuilt archive keyed on the frappe checkout's `git rev-parse HEAD` and `bundle` is then told to skip frappe entirely.
MUST expect that download to be silent about failing; `download_frappe_assets` catches every exception, prints it in color and returns False, and the build continues as an ordinary build.
MUST read a build with no `--production` as a development build on any site whose `developer_mode` is on, because the mode is chosen from `developer_mode` or `dev_server` before `--production` is consulted.
MUST run `bench build` after adding a file to an app's public folder for the first time; `generate_assets_map` links `<app>/public` to `sites/assets/<app>`, `<app>/../node_modules` to `sites/assets/<app>/node_modules` and a docs folder to `sites/assets/<app>_docs`, and nothing else creates those links.
MUST pass `--hard-link` where the deployment cannot follow a symlink, and MUST expect a copy that then goes stale on the next source edit until the next build.
MUST add an app to `sites/apps.txt` before building it; `setup` and `compile_translations` both walk `get_all_apps(True)`, so an app absent from that file is neither bundled nor compiled.
MUST expect `bench build` to compile translations as its last step, one process pool of four, for the apps named by `--apps` or for every app when none is named.
NEVER run two builds on one bench at once; `filelock("bench_build", is_global=True, timeout=10)` is bench-wide, not per site, and the second waits ten seconds and then fails.
MUST re-run `bench build` after clearing `sites/assets`, and MUST expect the cache to be flushed at the end of a successful bundle, because `bundle` calls `frappe.cache.flushdb` under a suppressed exception.
MUST install yarn and node 18 or newer; `check_node_executable` prints a warning for an older node and for a missing yarn and then runs `yarn run` anyway, so the failure arrives from yarn rather than from the check.
NEVER pass `--app` and `--apps` together expecting both; `--app` is copied into `apps` only when `apps` is empty.

## values

command line: yarn run build or yarn run production, plus --apps, --skip_frappe, --files, --run-build-command, --save-metafiles
working directory of that command: the frappe app source path
node environment: NODE_OPTIONS with max_old_space_size at three quarters of total memory, floor 1024
read: sites/apps.txt, each app's public/build.json, sites/assets/assets.json
written: sites/assets/<app>/dist, sites/assets/assets.json and assets-rtl.json, the app symlinks under sites/assets, each app's compiled translations
mode: development when developer_mode or dev_server is set, otherwise production; --production overrides
download skipped when: --force, or --apps, or CI in the environment
lock: bench_build, bench-wide, timeout 10 seconds
--save-metafiles: esbuild metafiles beside the bundles, for bundle size analysis only

## how

Two different things happen under one command. `bundle` turns each app's declared entry points into
hashed files under `sites/assets/<app>/dist` and records the mapping in `assets.json`;
`generate_assets_map` makes `sites/assets/<app>` point at the app's public folder, so everything
already in that folder is served without being bundled at all. A file that is served but never rebuilt is usually reaching the browser
through the second path, not the first.

The most surprising default is that frappe is normally not built. On a bench where nothing forced it,
`bench build` downloads a prebuilt archive matching the current frappe commit and only fills in whatever
`assets.json` says is missing. That is why editing frappe's own JS and running `bench build` can appear
to do nothing: pass `--force`, or name apps, and the download is skipped.

Translations ride along at the end. `bench build` is the command that turns an app's translation
catalog into the compiled form the site loads, so a translation edit needs this command even when no
asset changed.
