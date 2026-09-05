---
name: custom-docperm
description: One Custom DocPerm row for a DocType replaces the entire shipped permissions block for every role on it, the first row is a copy of the native DocPerm rather than a blank one, and a single Reset click deletes them all.
triggers: ["set_custom_permissions", "add_permission", "setup_custom_perms", "copy_perms", "reset_perms", "update_permission_property", "add", "reset", "update", "sync_customizations_for_doctype", "remove_app", "Cannot set", "There must be atleast one permission rule.", "Only allowed to export customizations in developer mode", "customize doctype permissions without a patch", "after i gave one role access everyone else lost theirs", "granting a permission to a single role removed permissions from other roles", "why did other roles lose access when i only added one role", "roles that used to open this document cannot open it anymore and i changed nothing for them", "i clicked reset on the permissions screen and everything we set up is gone", "my permission setup disappears every time the site is updated", "the access rules i seeded keep being added again after every update", "how do i change who can see a document type without editing the original app", "my code never deletes a permission but permissions keep vanishing", "after removing the app its old access rules are still there", "why does the permission screen show a much shorter list than before"]
product: frappe
---

# Custom DocPerm

## paths

frappe/model/meta.py — set_custom_permissions
frappe/permissions.py — add_permission, setup_custom_perms, copy_perms, reset_perms, update_permission_property
frappe/core/page/permission_manager/permission_manager.py — add, reset, update
frappe/modules/utils.py — sync_customizations_for_doctype
frappe/installer.py — remove_app

## rules

MUST read Custom DocPerm as all-or-nothing per DocType. set_custom_permissions queries the table for the DocType and REPLACES the whole permissions block when it finds any row, so one custom row for one role silently discards every native row for every other role, and no row at all leaves the shipped DocPerm untouched.
NEVER write rows for the roles an app cares about on a DocType that had none before without accounting for the rest; that call has replaced the base apps' permission table with a short list.
MUST read removing the custom_perms key from a customization file as restoring the owning app's shipped permissions, not as stripping the site's; the fallback is usually the correct state.
MUST read the first Custom DocPerm row for a doctype as a COPY of the native DocPerm. add_permission calls setup_custom_perms, which calls copy_perms to copy every standard DocPerm on that doctype, and add_permission then finds its row already present and returns without touching it — so granting a permission to a role that already holds a native DocPerm CONVERTS that native row rather than adding one.
NEVER loop update_permission_property over "every ptype I did not name" after add_permission; that zeroes ptypes the framework granted natively, and the author sees no delete anywhere in their own code.
MUST expect add_permission called with no ptype to default to read 1, so an operator who added a row by hand before the seeder first ran pre-empts the sequence and the seeder's existence check skips that row forever.
NEVER treat frappe.db.exists on parent, role and permlevel as an idempotency guarantee; it is a skip. reset_perms runs one unfiltered delete of every Custom DocPerm row for the doctype, is reachable from the Permission Manager by a single click permitted only to System Manager, and after_migrate re-runs with no completion state — so Reset-then-migrate repeats the seed without limit.
MUST use a doc_events handler on Custom DocPerm where the seeded state has to actually hold.
NEVER export permissions into a customization file for a shared doctype. The custom_perms branch of the sync deletes every row whose parent is the doctype and reinserts the file's rows, Custom DocPerm carries no module field, and the framework has no way to spare a row an operator created or another app installed.
MUST use a check-then-add seed instead; it grants what the app needs and leaves everything else standing.
MUST read a with_permissions export as unable to tell a row the app deliberately seeded from a row copy_perms manufactured out of the native DocPerm; it exports both, and the file then wipes and reinserts both on every run.
MUST delete an app's own Custom DocPerm rows in before_uninstall; remove_app's Module Def scan never reaches them.
MUST expect set_custom_permissions to return early under frappe.flags.in_patch and frappe.flags.in_install, and to skip a child table and the DocType, DocField, DocPerm and Custom DocPerm metas.

## values

replacement rule: any Custom DocPerm row for the DocType replaces the whole permissions block
copy trigger: setup_custom_perms fires when no Custom DocPerm row exists for the parent
add_permission default: read 1
add_permission existence check: parent, role, permlevel, if_owner 0
reset_perms: one unfiltered delete on parent, plus delete_notification_count_for
module field: none

## how

Ask what a permission row REPLACES before asking what it grants. The table is not a set of additions to
the shipped block; it is an alternative block that wins entirely the moment it is non-empty. That is why
a seeder written to grant one role its access can remove access from roles it never named, and why the
symptom shows up on a doctype the app does not own.

Custom DocPerm carries no module field, so no mechanism can tell an app's row from an operator's. Every
consequence follows: the customization sync must wipe the table to write it, a Reset click cannot spare
anything, and an existence check cannot distinguish "already seeded" from "an operator got there
first". Where the seeded state must hold, the only thing that holds it is a doc_events handler on
Custom DocPerm — a check on the write, not a check on the seed.

Prefer leaving the shipped block alone. A doctype with no custom rows is in the state its owning app
intends, and the cheapest correct delivery is the one that never creates the first row.
