---
name: fixtures
description: A fixture is for a constant the app owns; it re-imports with force on every migrate, commits after each file, and runs with in_import set so no field default is applied and no naming series advances.
triggers: ["sync_fixtures", "import_fixtures", "import_custom_scripts", "export_fixtures", "import_doc", "export_json", "import_file_by_path", "ignore_values", "_set_defaults", "queue_action", "check_if_locked", "unlock", "DOCUMENT_LOCK_EXPIRY", "set_new_name", "getseries", "FormMeta", "load_workflow", "Data Import", "Scheduler is inactive. Cannot import data.", "Error: Document has been modified after you have opened it", "Special Characters except", "ship data with an app", "fixtures export and import", "the settings i changed on the site went back to the old values after the last update", "why do my changes to that settings page keep getting overwritten every time we update", "furious that every deploy wipes the values the customer set by hand", "the sample records i deleted came back on their own", "i removed the demo data and it reappeared after the next update how do i stop it", "deleting those starter records does nothing they are back the next morning", "the setup data loaded only halfway and there is no way to roll it back", "half the records got created and then it crashed and the first half stayed", "why did an error in the middle of loading leave the earlier records saved", "records loaded from the app have empty fields that should have had a value", "the imported records are missing values i never filled in but expected to default", "i keep getting duplicate name errors on the first record i create by hand", "the numbering restarted at one and collided with records that were shipped with the app", "a form of that type refuses to open at all and fails the same way every single time", "the second run failed saying the document is locked and i cannot get past it"]
product: frappe
---

# Fixtures

## paths

frappe/utils/fixtures.py — sync_fixtures, import_fixtures, import_custom_scripts, export_fixtures
frappe/core/doctype/data_import/data_import.py — import_doc, export_json
frappe/modules/import_file.py — import_file_by_path, import_doc, ignore_values
frappe/model/document.py — _set_defaults, queue_action, check_if_locked, unlock, DOCUMENT_LOCK_EXPIRY
frappe/model/naming.py — set_new_name, getseries
frappe/desk/form/meta.py — FormMeta, load_workflow

## rules

MUST ship as a fixture only a value the APP owns and no site may change. Every fixture is imported with force=True, so the record returns to the file's contents on every migrate with no diff and no warning, and a Single holding operator-editable settings loses the operator's choices.
MUST seed a per-site value behind a frappe.db.exists check instead; frappe, erpnext and hrms declare no fixtures key at all and create their Roles and Single defaults imperatively.
NEVER ship demo data as a fixture; it re-imports on the next migrate, so the removal button refills its own screen.
MUST expect import_fixtures to iterate EVERY .json in the app's fixtures folder in sorted filename order. The fixtures list in hooks.py governs the EXPORT, so removing a file from that list does not stop its import.
MUST expect a mid-list failure to leave the site half-delivered. import_doc calls frappe.db.commit at the end of every FILE with no surrounding transaction, so a list that fails on its fifth file leaves the first four permanently committed and there is no rollback.
MUST expect a controller's validate to run during a fixture import; the call passes data_import=True and never sets ignore_validate, and a Workflow whose states do not resolve is the usual throw.
MUST state every field a fixture relies on. import_doc sets frappe.flags.in_import, _set_defaults returns immediately under that flag, and every unmentioned field carrying a default is stored NULL with nothing raised unless the field is also reqd.
MUST either drop the pinned name values from a fixture or seed the series past the pinned range at install. in_import short-circuits the name reset in set_new_name, so autoname never runs, and getseries reads and increments its own tabSeries row without consulting the target table — so the first ordinary autoname call on that site returns 0001 and collides with the fixture's own first record.
MUST resolve every Link value a fixture writes against what the same install creates. import_doc sets ignore_links on the document, so a Workflow shipped without its Workflow State rows imports cleanly and the damage appears at the first attempt to open a form of that doctype.
NEVER read that crash as transient. FormMeta fetches the Workflow and every Workflow State row during construction, and the cache write runs only after a successful construction, so there is no negative cache and every request repeats the identical failure.
NEVER ship Role Profile or Module Profile through fixtures. A doctype whose on_update calls queue_action takes a document lock before enqueueing, only a worker draining the queue clears it, and the second migrate inside the lock window throws DocumentLockedError.
NEVER read a green migrate as proof such a fixture is safe; DOCUMENT_LOCK_EXPIRY is three hours and a stale lock is ignored, so the pass may only prove three hours elapsed. Delete the stale zero-byte lock files under the site's locks folder and re-migrate to recover.

## values

order: sorted filename order within the app's fixtures folder
transaction: one commit per FILE
flags set: in_fixtures by sync_fixtures, in_import and ignore_links by the importer
force: always True for a fixture, so no skip condition applies
caught per file: ImportError and DoesNotExistError, printed as `Skipping fixture syncing from the file`
lock path: sites/<site>/locks, named for the sha224 of `<doctype>:<name>`
lock expiry: three hours

## how

The question is never whether a fixture CAN carry something. It is whether the thing is a constant the
app owns or a value that differs per site, and both directions of that mistake are silent. A variable
shipped as a fixture is clobbered on the next migrate, which is exactly what "the app owns this value"
means and is the proof it was never a constant. A constant not shipped as a fixture drifts to whatever
the site last happened to have, and nothing pulls it back. There is no middle setting.

Everything else follows from force plus in_import. Force removes the skip condition, so the file is the
truth on every run. in_import removes defaults and naming, so the file must be complete: a field the
file omits is NULL, and a name the file pins leaves the counter untouched for a collision later.

A fixture that writes a Link accepts a dangling reference without a word, so the check that finds the
problem is yours: resolve each Link value against what the same install creates, because the importer
will not.
