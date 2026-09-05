---
name: doctype-update-hook
description: on_doctype_update fires from DocType.on_update when the DocType record is saved, and import_file only reimports a DocType JSON when migration_hash no longer matches the file's calculated hash, so editing the hook alone leaves it inert until any byte of the sibling JSON changes.
triggers: ["on_update", "import_file", "Doctype", "Fieldname", "Not in Developer Mode! Set in site_config.json or make", "Not allowed to create custom Virtual DocType.", "on_doctype_update hook", "doctype json not reimporting", "i edited the code but nothing happens after i run the upgrade", "the upgrade finished with no errors and my change did nothing", "why is my index never created on the table", "i have upgraded ten times and the code i added still does not run", "how do i force it to reload the record type definition", "the change only took effect after i touched something unrelated", "nothing tells me whether the definition file was actually picked up", "my setup code for this record type runs on one machine and not the other", "does a clean upgrade mean my change was applied", "the definition file on disk is newer but it is being skipped"]
product: frappe
---

# on_doctype_update

## paths

frappe/core/doctype/doctype/doctype.py — on_update
frappe/modules/import_file.py — import_file

## rules

MUST expect `on_doctype_update` and `after_doctype_insert` to run only when the DocType record itself is saved, from `DocType.on_update`, never because a controller file on disk changed.
MUST expect `bench migrate` to reimport a DocType's JSON, and so run `on_update`, only when `migration_hash` no longer equals the file's calculated hash; a DocType is skipped on this hash regardless of its `modified` timestamp.
NEVER read a clean `bench migrate` exit code as proof `on_doctype_update` ran; exit 0 with the JSON unchanged means the file was not reimported at all.
MUST verify an index added inside `on_doctype_update` with `SHOW INDEX` after migrating, not with migrate's exit code.
MUST ship an `on_doctype_update` edit and a byte change to the sibling `.json` as one change, because editing any field of the JSON changes its calculated hash and activates a hook edit that was otherwise inert.

## how

The hash decides, not the timestamp: `import_file` excludes DocType by name from the timestamp-only skip, so only `migration_hash` decides whether a DocType is reimported. That makes the mechanism insensitive to which field changed — bumping `modified` works because it changes the file's bytes, and so does any other edit, including one made for an unrelated reason on a JSON that has been sitting next to a hook edit for weeks.
