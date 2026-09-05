---
name: rename-doc
description: A rename_doc patch renames only the stored row, and import_file deletes and re-inserts whatever row matches a shipped record's JSON name, so a rename patch and the JSON name that still names the old key together re-create the record under both names.
triggers: ["import_file", "delete_old_doc", "IMPORTABLE_DOCTYPES", "sync_dashboards", "autoname", "Number Card", "Document Type and Function are required to create a number card", "Aggregate Field is required to create a number card", "Parent Document Type is required to create a number card", "rename a document across sites", "rename_doc patch", "the old record came back by itself after i renamed it", "i renamed it it worked and then the next deploy undid it", "why does a renamed record reappear under its old name", "we now have two copies one with the old name and one with the new", "renaming across all our sites keeps reverting", "the rename holds on one site and reverts on another", "how do i rename a record that ships with the app so it stays renamed", "the dashboard tile was recreated under its old name after the upgrade", "does renaming an approval flow behave the same way", "the rename broke the translated label on the card"]
product: frappe
---

# rename_doc and its shipped JSON

## paths

frappe/modules/import_file.py — import_file, delete_old_doc
frappe/model/sync.py — IMPORTABLE_DOCTYPES
frappe/utils/dashboard.py — sync_dashboards
frappe/desk/doctype/number_card/number_card.py — autoname

## rules

MUST land a `frappe.rename_doc` patch and the JSON rename — directory, file name, `name` field, and every dependent that points at the old key — as one indivisible change, because `import_file` deletes whatever row matches the JSON's `name` and re-inserts it, so a JSON still carrying the old key re-creates the retired record on the next migrate.
MUST land the patch and every JSON that still names the old key in the same release even when they live in different modules, because a migrate that runs between the two halves re-creates the retired record.
MUST expect `import_file` to cover Print Format and Onboarding Step, and `sync_dashboards` to cover Number Card and Dashboard Chart; MUST check `IMPORTABLE_DOCTYPES` and `sync_dashboards` before assuming a record kind is covered.
NEVER assume a Workflow rename is covered by a patch-versus-JSON race; Workflow is absent from `IMPORTABLE_DOCTYPES` and from `make_records_in_module`, migrate never reads a Workflow file from the module tree, and a seeder is its only writer.
MUST update the translation file alongside a Number Card rename when its name derives from `label`, because `autoname` sets `self.name = self.label` and the stored key is then tied to the translation source string.

## how

The renamed row and the shipped JSON are two halves of one fact, and `import_file` enforces that by identity rather than by diffing: it matches on `name`, deletes what it finds, and inserts fresh from the JSON on every migrate that reimports the file. A patch that renames the row without touching the JSON does not fail — it succeeds once, and the very next migrate reverses it by re-creating the old name from the JSON that never moved.
