---
name: validation
description: Only some DocField properties are checked on the server, so replacing a controller check with mandatory_depends_on or read_only_depends_on moves the rule into the browser and every API, patch, job and import then skips it.
triggers: ["_validate", "_validate_non_negative", "validate_set_only_once", "_validate_links", "get_invalid_links", "validate_workflow", "_get_missing_mandatory_fields", "_validate_selects", "_validate_data_fields", "_validate_length", "_sync_autoname_field", "set_fetch_from_value", "get_set_only_once_fields", "get_fields_to_fetch", "_field_autoname", "refresh_dependency", "set_dependant_property", "is_docfield_mandatory", "DEPENDENCY_PROPERTIES", "NonNegativeError", "CannotChangeConstantError", "LinkValidationError", "Error: Document has been modified after you have opened it", "Please check the value of", "Special Characters except", "mandatory field not enforced", "server side field validation", "a field that is supposed to be required got saved empty by a script", "the conditional required field is ignored when records come in from the importer", "why is my required-when rule skipped by the api but enforced on the screen", "a field nobody is allowed to edit got changed by a background job", "the read only rule holds on the form and holds nowhere else", "saving without changing anything complains that a value cannot be modified", "it says the field can only be set once even though i did not touch it", "why do i get a cannot change error on a save that changed nothing", "negative numbers still get saved even though i ticked the no negative box", "the record saved with a link pointing at something that does not exist", "the bad link is accepted on some fields and refused on others", "spaces keep getting trimmed off the field the record name is built from"]
product: frappe
---

# Validation

## paths

frappe/model/document.py — _validate, _validate_non_negative, validate_set_only_once, _validate_links, get_invalid_links, validate_workflow
frappe/model/base_document.py — _get_missing_mandatory_fields, _validate_selects, _validate_data_fields, _validate_length, _sync_autoname_field, get_invalid_links, set_fetch_from_value
frappe/model/meta.py — get_set_only_once_fields, get_fields_to_fetch
frappe/model/naming.py — _field_autoname
frappe/public/js/frappe/form/layout.js — refresh_dependency, set_dependant_property
frappe/public/js/frappe/form/save.js — is_docfield_mandatory
frappe/public/js/frappe/form/grid_row.js — DEPENDENCY_PROPERTIES
frappe/exceptions.py — NonNegativeError, CannotChangeConstantError, LinkValidationError

## rules

MUST read `_get_missing_mandatory_fields` as filtering on `reqd` alone, so `mandatory_depends_on` never reaches a server check.
MUST keep the controller check for `mandatory_depends_on` and `read_only_depends_on`, because their only evaluation sites are `layout.js`, `save.js` and `grid_row.js`, and a document written by `get_doc(...).insert()`, a whitelisted method, a patch, a background job, a fixture or a data import passes through none of them.
MUST expect `non_negative` to be read only for Int, Float and Currency, because `_validate_non_negative` filters on fieldtype; the property is inert on any other fieldtype.
MUST expect `set_only_once` to compare the raw stored value against the raw new value, so an empty string against `None` throws `CannotChangeConstantError` where a hand-written check that normalised blanks did not.
MUST expect `validate_set_only_once` to run only when the document is not new and `_doc_before_save` was loaded.
MUST delete a controller `.strip()` on the field a `field:` autoname reads; `_field_autoname` strips the value and `_sync_autoname_field` copies the stripped `name` back onto that field on every save.
MUST expect an invalid Link to insert without error when at least one `fetch_from` reads from that field, because the multi-column lookup returns `None`, the enclosing block is skipped, and nothing is appended to `invalid_links`.
NEVER write a test asserting that a bad Link raises `LinkValidationError` without recording that adding a `fetch_from` on that field later makes the assertion pass while testing nothing.
MUST read a DocField property the model layer never reads as a browser behaviour the DocType editor offers, never as a rule that refuses a document written any other way.

## values

checked on the server: reqd, non_negative, set_only_once, unique, Select options, fetch_from, default, docstatus, workflow state, Link target existence, field length, ignore_user_permissions
checked in the browser only: mandatory_depends_on, read_only_depends_on, depends_on, collapsible_depends_on
non_negative fieldtypes: Int, Float, Currency
set_only_once comparison: str() for Date, Datetime and Time; child tables by row comparison; every other fieldtype by equality
exceptions thrown: NonNegativeError, CannotChangeConstantError, LinkValidationError
link lookup with no fetch_from consumer: one cached column, a miss is caught
link lookup with a fetch_from consumer: several columns as a dict, a miss returns None and is not caught

## how

The DocType editor puts server rules and browser rules in the same panel, and the framework gives no sign of which is which. That makes the native-first move — delete the Python, set the key — correct for one set of properties and destructive for another, with the same appearance either way. The split is mechanical: the model layer either reads the property or it does not, and the DocType editor's panel is not evidence either way.

`mandatory_depends_on` and `read_only_depends_on` are the two that matter, because they read as rules and are enforced only where a person is typing. A document created by any other route is not refused, it is accepted with the field empty or with the field changed. So a controller check that duplicates one of them is not a duplicate at all; it is the only copy that holds where the rule needs to hold.

Inside the server-checked set the traps are about what the framework compares rather than whether it compares. `set_only_once` compares raw values, so a column that has held both an empty string and NULL over its life will throw on a save that changed nothing a person can see. `non_negative` compares nothing at all outside three fieldtypes. And `_validate_links` reads its target by two different routes depending on whether anything fetches from the field, and only the single-column route reports a missing row — which makes Link validation a property of the schema around the field rather than of the field.
