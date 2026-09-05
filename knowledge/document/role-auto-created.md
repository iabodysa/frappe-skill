---
name: role-auto-created
description: Every role a DocType names in its own permissions block is auto-created with desk_access = 1 on sync, before sync_fixtures runs, so a seeder that sets desk_access off loses the race on any run its hook entry is missing from and only a fixture wins every time.
triggers: ["on_update", "make_module_and_roles", "AUTOMATIC_ROLES", "sync_all", "sync_fixtures", "Doctype", "Fieldname", "Not in Developer Mode! Set in site_config.json or make", "Not allowed to create custom Virtual DocType.", "role auto created from doctype permissions", "new role appears automatically", "a role i never created showed up on its own", "new roles keep appearing after every upgrade", "why does the system add roles i did not ask for", "the role i set to have no back office access keeps getting it back", "my setting on the role is reset every time we upgrade", "how do i stop a role from being able to open the back office", "the script that fixes the role works some runs and not others", "roles are being created with the wrong defaults", "which roles are always added to everything no matter what", "my change to the role is overwritten during the upgrade"]
product: frappe
---

# Role auto-creation

## paths

frappe/core/doctype/doctype/doctype.py — on_update, make_module_and_roles
frappe/permissions.py — AUTOMATIC_ROLES
frappe/migrate.py — sync_all, sync_fixtures

## rules

MUST expect a Role named in a DocType's `permissions` block to exist with `desk_access = 1` the moment that DocType is synced, because `on_update` calls `make_module_and_roles`, which inserts every missing role from `permissions` plus `AUTOMATIC_ROLES` with `desk_access = 1` and no other value set.
MUST use a Role fixture, not a `frappe.db.set_value` seeder, to hold a role's `desk_access` at 0, because `sync_all()` runs before `sync_fixtures()` on install and on every migrate, so the fixture is always applied after the framework's default and a seeder is only applied on the runs its hook entry survived into.
MUST read `AUTOMATIC_ROLES` as Guest, All, System User and Administrator; these are added to every DocType's role set regardless of what its own `permissions` block names.

## how

The order is fixed, not incidental: `migrate.py` runs `sync_all()` before `sync_fixtures()` on both install and migrate, so the auto-created default and any fixture correction always land in that sequence. A seeder reaches the same end state only on the runs it happens to be wired into; a fixture is declarative and cannot be dropped from a run by a missing hook entry.
