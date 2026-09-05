---
name: records
description: add_to_test_record_log writes the DocType into sites/<site>/.test_log on every branch and make_test_records_for_doctype returns early on anything already listed there, so test records are built once per site and an edited test_records.json is never read again, and make_test_objects forces the _T- test naming series onto any DocType that merely carries a naming_series field, so a test record name is site counter state and an explicit name key in test_records.json only answers the duplicate check.
triggers: ["make_test_records", "make_test_records_for_doctype", "make_test_objects", "get_dependencies", "get_modules", "add_to_test_record_log", "get_test_record_log", "print_mandatory_fields", "get_test_records", "Document.insert", "Document.set_new_name", "get_all_children", "BaseDocument.db_insert", "BaseDocument._validate_selects", "set_new_name", "NamingSeries", "revert_series_if_last", "get_default_naming_series", "delete_doc", "check_permission_and_not_submitted", "check_if_doc_is_linked", "app_group", "Cannot make dict for single fieldname", "Error: Document has been modified after you have opened it", "Please check the value of", "test records not loading", "test record name", "_T- prefix", "test record ignores my autoname", "explicit name in test_records.json", "d.meta.get_field", "flags.name_set", "set_name_from_naming_options", "frappe.db.exists", "i edited the sample data file and the tests still use the old values", "why are my test rows not rebuilt after i changed them", "the test data file is being ignored completely", "the created rows have a weird underscore prefix in their names instead of my numbering", "i set the name myself in the sample data and it came out totally different", "how do i rebuild the sample rows for just one form without redoing everything", "deleting the sample rows fails saying it is linked somewhere", "the run says it finished fine but no sample rows were actually created", "my test asserts a fixed row name and it breaks on a different machine", "child rows are duplicated every time the sample data loads", "the whole batch of sample data dies on one bad link value", "why does the numbering keep jumping after i delete rows and rebuild"]
product: frappe
---

# Test records

## paths

frappe/test_runner.py — make_test_records, make_test_records_for_doctype, make_test_objects, get_dependencies, get_modules, add_to_test_record_log, get_test_record_log, print_mandatory_fields
frappe/__init__.py — get_test_records
frappe/model/document.py — Document.insert, Document.set_new_name, get_all_children
frappe/model/base_document.py — BaseDocument.db_insert, BaseDocument._validate_selects
frappe/model/naming.py — set_new_name, set_name_from_naming_options, NamingSeries, revert_series_if_last, get_default_naming_series
frappe/model/delete_doc.py — delete_doc, check_permission_and_not_submitted, check_if_doc_is_linked
frappe/utils/bench_helper.py — app_group

## rules

MUST write test records as `test_records.json` beside the DocType; `get_test_records` reads that path and the runner inserts them for the whole suite.
NEVER write an app's own factory module for the same job; it rebuilds what `make_test_objects` already built and pays for every rebuild.
MUST expect a DocType with no records to produce none. `make_test_records_for_doctype` tries `_make_test_records`, then a `test_records` attribute in the test module, then `test_records.json`, and the last branch only calls `print_mandatory_fields` when `verbose` is set — there is no fourth branch and no synthesis from meta.
NEVER supply records by two of those three mechanisms; they are `elif` branches, so a `test_records` attribute in `test_<slug>.py` silences the `test_records.json` beside it.
NEVER read an unchanged result after editing `test_records.json` as the edit failing. MUST remove that DocType's line from `sites/<site>/.test_log`, or delete the file, so the DocType is built again. That file is site state and never belongs in a commit.
NEVER pass `--force` to rebuild one DocType. `run_tests_for_doctype` deletes every row of the named DocType and then passes `force` down through `make_test_records`, which recurses over the whole dependency set.
MUST rebuild one DocType in this order: delete its rows with `frappe.delete_doc(dt, name, force=True)`, delete its line from `sites/<site>/.test_log`, then run the suite for it with `CI` set.
MUST pass `force=True` to that delete; `delete_doc` runs `check_if_doc_is_linked` only when `force` is unset, and a `_T-` row is linked by other `_T-` rows by construction. Where the DocType has an `enabled` or `disabled` field the refusal reads `You can disable this {0} instead of deleting it.` and names no link.
MUST cancel a submitted record before deleting it; `check_permission_and_not_submitted` runs outside the `force` branch, and `make_test_objects` submits any record carrying `"docstatus": 1`.
MUST leave `naming_series` out of a record. `make_test_objects` sets `d.naming_series = "_T-" + d.doctype + "-"` only when the field is empty; a record that carries one names itself from the site's prefix and advances the shared `tabSeries` row.
MUST read that assignment as keyed on the FIELD and never on the DocType's naming rule; `make_test_objects` tests `d.meta.get_field("naming_series")`, so a DocType autonamed `field:` or `format:` that merely carries the field is still given `_T-<DocType>-` and stores it, where `set_name_from_naming_options` dispatches on the autoname string and never reads it — inert there, and a full replacement of the shipped prefix on a `naming_series:` DocType.
MUST expect `_T-<DocType>-#####` even though nothing writes the digits; `NamingSeries.__init__` appends `.#####` to a series with no `#` in it.
NEVER expect an explicit `"name"` key to reach the row. `make_test_objects` assigns `d.name` without setting `flags.name_set`, so `insert` calls `Document.set_new_name`, which calls `set_new_name`, which sets `doc.name = None` and derives the name again unless the autoname is `prompt` or `frappe.flags.in_import` is set; a `field:` DocType keeps the key only because its own naming rule rebuilds the same value.
MUST read an explicit `"name"` key as the duplicate check instead. `make_test_objects` passes it to `frappe.db.exists` before the insert and skips the record when a row already carries that name, so on a `naming_series:` DocType the key decides whether the record is built and not what it is called.
NEVER assert a `naming_series:` test record's name as a literal. The forced `_T-<DocType>-` prefix resolves to one `tabSeries` row per site, so the digits are that site's counter state; reach the row through a Link value or a filter on a field the record sets.
NEVER expect a `_T-` series to fail Select validation; `_validate_selects` skips the field named `naming_series` before it compares against `options`.
MUST land the removal of `naming_series` from one DocType's records and the rewriting of every Link value naming its old rows in the same commit; `make_test_objects` inserts with link validation on and a `LinkValidationError` takes the whole DocType's load down.
MUST re-read the rebuilt names and compare them against every record and assertion that names one. `revert_series_if_last` decrements `tabSeries` only when the deleted name is the current value, so deleting three rows rewinds at most one and the rebuild mints upward from where it stopped.
MUST confirm the rows landed rather than reading exit 0 as proof; `add_to_test_record_log` writes the line on every branch, including the one that made nothing, so a second attempt returns early.
NEVER call `frappe.test_runner.make_test_objects` from application code or from an app's own test; the runner is what makes the records.
MUST expect an insert of a record whose row already exists to double its child rows. `make_test_objects` passes `ignore_if_duplicate=True`, `db_insert` swallows the parent's duplicate-name error without raising, and `insert` then loops `get_all_children()` and inserts every child unconditionally.

## values

file: <app>/<module>/doctype/<scrubbed doctype>/test_records.json
mechanisms, in order: _make_test_records, a test_records attribute in test_<slug>.py, test_records.json
record log: sites/<site>/.test_log, one DocType per line, written on every branch
dependency set: every Link field of the DocType, every Link field of every child table, the DocType itself, plus test_dependencies, minus test_ignore
private series: _T-<DocType>-, expanded to _T-<DocType>-.#####
_T- forced when: d.meta.get_field("naming_series") is truthy and the record leaves the field empty — the DocType's autoname is not read
explicit "name" key: the argument to frappe.db.exists, then discarded by set_new_name unless the autoname is prompt or frappe.flags.in_import is set
name a naming_series: record gets: _T-<DocType>-0000N off the tabSeries row keyed _T-<DocType>-
insert flags: ignore_if_duplicate=True, link validation on, no ignore_links
caught on insert: frappe.NameError, and any class in d.flags.ignore_these_exceptions_in_test
hook run before each insert: before_test_insert
skip switches: frappe.flags.skip_test_records, test_ignore
--force: bench's global option in app_group, written bench --site <site> --force run-tests

## how

Frappe already has the thing an app keeps rebuilding, and it is a JSON file beside the DocType. Reach for it before writing anything that builds documents, because everything an app's own factory does — dependency order, naming, submission, reuse across the suite — this already does, and the runner hands the result to any test that asks.

The thing that surprises everyone is that it builds once per SITE and not once per run. The record of what was built is a plain text file in the site directory, so it outlives the process, the branch and the checkout. An edit to `test_records.json` therefore reads as ignored: the old rows are still committed, the early return fires, and a record pointing at something the edit added dies with a link error. The fix is never in the repository — remove the line, or the file.

Names are the second trap and they compound with the first. A DocType with a `naming_series` field gets a private `_T-` series only when the record leaves that field empty; fill it in and the test rows are minted from the same counter the site's real documents use, interleaved with them, advancing it every run. So leave it out. But leaving it out renames that DocType's rows, and every other `test_records.json` that named an old row by its production name now names a row that will never exist. That is one change, not two, and it must ship as one.

What triggers the forcing is the field and not the rule, so a DocType named from one of its own fields still carries `_T-` in the stored `naming_series` of every test row, doing nothing; only a series DocType has its shipped prefix replaced. And writing a `"name"` into the record does not pin the name back down. That key is read once, to ask whether the row is already there, and the naming inside `insert` then throws it away. So on a series DocType the name of a test record is a fact about the site's counter and not about the record, which is why an assertion should reach the row through a Link value or a filter and never through the literal name.

Rebuilding one DocType is the operation people get wrong, because the obvious flag is the wrong tool. `--force` is bench's global option and it recurses across the whole dependency set, re-inserting ancestors that still exist; the parent write is discarded and the child writes are not, so a record carrying a child table quietly doubles its rows and throws on some later save in an unrelated test. Do it by hand instead: delete the rows forcibly, cancelling anything submitted, remove the one line from the log, run the DocType. Then read the names back, because deleting rows does not rewind the counter and the rebuilt rows are almost never the numbers that were there before.
