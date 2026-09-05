---
name: defaults
description: Every Time field on an inserted document is stamped with nowtime regardless of its default, because that branch sits outside the block that reads the default at all.
triggers: ["_set_defaults", "insert", "save", "get_new_doc", "set_dynamic_default_values", "get_default_based_on_another_field", "validate_value_via_user_permissions", "update_if_missing", "Error: Document has been modified after you have opened it", "Please check the value of", "default value not applied on new document", "time field default", "the time field fills itself with the current clock time even though i left it empty", "why is there a time on a record where nobody entered one", "i never typed a time and every single row has one anyway", "checking whether the time is empty never works because it is always filled", "the duration between the two times is nonsense because both were filled automatically", "the field is marked required but it never asks me for a value", "rows i loaded from a file are blank where rows i create by hand have a value", "the default value is not applied when i save an existing record again", "how do i model a clock reading that is sometimes not taken", "two time columns on the same row hold the same second and i never entered either"]
product: frappe
---

# Defaults

## paths

frappe/model/document.py — _set_defaults, insert, save
frappe/model/create_new.py — get_new_doc, set_dynamic_default_values, get_default_based_on_another_field, validate_value_via_user_permissions
frappe/model/base_document.py — update_if_missing

## rules

MUST expect every `Time` field on an inserted document to hold the clock time of the insert, because `set_dynamic_default_values` assigns `nowtime()` to it outside the block that reads `df.default`.
NEVER model an optional clock reading as a `Time` field; an emptiness test on it is always false after insert.
MUST model an optional clock reading as `Datetime`, or MUST add a `Check` field recording whether the reading was taken and branch on that field before computing with the time.
NEVER mark a `Time` field `reqd`; the stamp lands before `_validate_mandatory`, so the requirement is satisfied by a value nobody entered and the person is never asked for it.
MUST read two `Time` fields on one row holding the same second with different microseconds as two stamps rather than two readings, because the loop calls `nowtime()` once per field.
MUST expect `get_doc({...}).insert()` to receive defaults; `_set_defaults` builds a new document and calls `update_if_missing`, so passing a full dict to the constructor does not turn defaults off.
MUST expect `frappe.flags.in_import` to skip `_set_defaults` entirely, which is why an imported row can hold a blank `Time` that no ordinary insert produces.
MUST expect an existing document being re-saved to receive no parent defaults, because `_set_defaults` fills the parent only when `is_new` is true; child rows are still filled where the row itself is new.
MUST write a Datetime default as the string that `set_dynamic_default_values` lowercases and compares against now, because that is the only fieldtype whose default is read as an expression there.

## values

read from df.default: a default starting with a colon, resolved against another field; a Datetime default equal to now
assigned without reading df.default: Time, always nowtime
skips _set_defaults entirely: frappe.flags.in_import
skips the parent only: is_new false
child rows: filled from a new child document, per row, only where the row is new
also set by set_dynamic_default_values: parent and parenttype when a parent document is passed

## how

Defaults are built by making a fresh document of the same DocType and copying across only the fields the target left empty, which is why a document assembled from a dict still gets them. The surprise is not that mechanism but one branch inside it: the `Time` fieldtype is assigned unconditionally, outside the `if` that every other fieldtype's default is read inside. Declaring no default does not turn it off, because nothing there reads a default.

The cost lands on modelling rather than on code. A `Time` field is the natural choice for an event that has a clock reading, and it is exactly wrong for an event that may not have happened, because the absence of the event is written as the moment the row was saved. A duration computed from two such fields is arithmetic over a timestamp nobody entered and reads as a genuine measurement. Ask first whether the reading is always taken; if it is not, the fieldtype is the defect.

`in_import` is the other thing to hold. It skips the whole step, so an imported row and an inserted row of the same DocType are not interchangeable as fixtures or as test data — the imported one can carry blanks the application never produces.
