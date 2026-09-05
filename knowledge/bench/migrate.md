---
name: migrate
description: Three phases each wrapped in a commit-or-rollback decorator run patches, then the schema, then a fixed sync order that ends with the after_migrate hooks, and none of it reaches a site being installed.
triggers: ["SiteMigration", "atomic", "pre_schema_updates", "run_schema_updates", "post_schema_updates", "run", "setUp", "tearDown", "required_services_running", "DBQueryProgressMonitor", "sync_all", "sync_for", "remove_orphan_doctypes", "run_all", "PatchType", "install_app", "add_module_defs", "set_all_patches_as_completed", "filelock", "bench migrate order of operations", "what does migrate actually run", "the setting is right on my machine but missing on the customer site", "brand new sites are missing a record that all the old sites have", "why does a fresh install skip the step that fixes this", "the feature is left switched on for every newly created site", "my fixture keeps getting overwritten by something else after an update", "the field change i shipped is reverted every time we update", "in what order do things actually happen when we update the site", "the update fails instantly when i run it twice at the same time", "running the update a second time says it cannot get a lock", "the code that seeds data never runs on new installs", "the update stops right at the start and exits with an error before doing anything"]
product: frappe
---

# Migrate

## paths

frappe/migrate.py — SiteMigration, atomic, pre_schema_updates, run_schema_updates, post_schema_updates, run, setUp, tearDown, required_services_running, DBQueryProgressMonitor
frappe/model/sync.py — sync_all, sync_for, remove_orphan_doctypes
frappe/modules/patch_handler.py — run_all, PatchType
frappe/installer.py — install_app, add_module_defs, set_all_patches_as_completed
frappe/utils/synchronization.py — filelock

## rules

MUST read the sync order as fixed: sync_jobs, sync_fixtures, sync_dashboards, sync_customizations, sync_languages, flush_deferred_inserts, remove_orphan_doctypes, Portal Settings sync_menu, Installed Applications update_versions, then the after_migrate hooks.
MUST expect a customization to win over a fixture carrying the same Custom Field or Property Setter, because sync_fixtures runs before sync_customizations and the later writer decides — not the file edited more recently.
MUST read an after_migrate hook as seeing a fully synced site; every fixture, dashboard, customization and language is in place before that loop runs.
MUST wire a seeder to BOTH runs when it has to reach new and existing sites. after_migrate is called from the migrate run and nowhere else; after_install, after_app_install and after_sync are called from the install run and nowhere else, and neither reports the gap.
NEVER put a step that closes, restricts, prunes or retires something on after_migrate alone. A fresh site is created in exactly the state that step exists to correct and stays there until somebody migrates, so the site ships with the thing open.
NEVER put a record every existing site needs on after_install alone; it reaches every new site and no existing one, forever, and the symptom is a customer site missing what the developer sees on their own.
MUST put a step acting on records that arrive as FIXTURES in after_sync, not after_install; within the install run the order is after_install, after_app_install, sync_jobs, sync_fixtures, sync_customizations, sync_dashboards, after_sync, so the rows do not exist yet at the earlier slot.
MUST add a Module Def for a module added to modules.txt in a later release through a patch; add_module_defs is called from the install run only.
NEVER make a patch the only place a fact is created; set_all_patches_as_completed stamps every patch on a fresh install, so its body never runs there.
MUST expect each of the three phases to commit on success and roll back on any exception; the atomic decorator wraps pre_schema_updates, run_schema_updates, post_schema_updates and run, and it suppresses a failure of the rollback itself to preserve the original exception.
MUST expect a second concurrent run on the same bench to fail rather than wait; run takes the bench_migrate filelock with a one-second timeout.
MUST expect SystemExit(1) before any phase when required_services_running answers false.

## values

phases: pre_schema_updates (before_migrate hooks), run_schema_updates (pre_model_sync patches, sync_all, post_model_sync patches), post_schema_updates (the sync order and after_migrate)
migrate run: after_migrate only
install run: before_install, before_app_install, after_install, after_app_install, after_sync
install order: add_module_defs, sync_for, add_to_installed_apps, Portal Settings sync_menu, set_all_patches_as_completed, after_install, after_app_install, sync_jobs, sync_fixtures, sync_customizations, sync_dashboards, after_sync
lock: bench_migrate, timeout 1

## how

Ask which run calls a step before asking whether it works. The install run and the migrate run share
no hook, so a function wired to one of them reaches new sites or existing ones and never both, and
nothing logs the half it misses. A step that must hold everywhere is wired to both and made
idempotent, so the double wiring costs nothing.

The sync order decides the value whenever two mechanisms ship the same row. Shipping one row through two
mechanisms is a defect either way, but knowing the order tells you which value a site actually has,
and neither file shows it.

Within the install run the hook chosen matters as much as the run does. Anything that reads rows a fixture
brings has exactly one correct slot, and the earlier one runs against nothing and says so in no way at
all.

The atomic decorator is the guarantee install does not give. A phase either lands whole or leaves
nothing, so a failed migrate is recoverable by fixing the cause and running again — which is why a
change that has to survive a mid-run failure belongs in a migrate hook rather than an install hook.
