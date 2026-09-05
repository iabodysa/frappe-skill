---
name: db-set
description: db_set skips validate, before_save and on_update but still loads the previous document and runs before_change and on_change, so a write chosen to avoid a handler still reaches it.
triggers: ["db_set", "load_doc_before_save", "get_doc_before_save", "run_method", "notify_update", "clear_cache", "set_value", "set_single_value", "get_value", "clear_document_cache", "get_cached_doc", "Error: Document has been modified after you have opened it", "`as_iterator` only works with `as_list=True` or `as_dict=True`", "Cannot make dict for single fieldname", "db_set vs save", "update a field without triggering hooks", "i updated one field without saving and the notification still went out", "skipping the save did not stop the other code from running", "why does my handler still fire when i only change a single field quietly", "i deliberately avoided a full save and the loop is still happening", "the value i just wrote is not what i read back a moment later", "the record keeps showing the old value after i updated the table directly", "why do i get stale data right after writing it in the same request", "a record is stuck in a status the approval steps will never let it leave", "the state changed to something the approval flow does not allow", "the last modified time did not change after i updated a field", "how do i change one field without running any of the checks"]
product: frappe
---

# db_set

## paths

frappe/model/document.py — db_set, load_doc_before_save, get_doc_before_save, run_method, notify_update, clear_cache
frappe/database/database.py — set_value, set_single_value, get_value
frappe/__init__.py — clear_document_cache, get_cached_doc

## rules

MUST expect `db_set` to run `before_change` before the write and `on_change` after it, and to load the previous document first when nothing loaded it already.
NEVER reach for `db_set` to escape a handler that fires on `on_change`; the handler still runs and the recursion it caused still recurses.
MUST use `frappe.db.set_value` where no controller method may run at all; it writes through the query builder and never constructs the Document.
NEVER put either on a status field or a workflow field; both skip `validate` and `validate_workflow`, so the row can hold a state no transition allows.
MUST keep both for derived, cached and counter fields, which is the case where skipping validation is the point.
MUST expect `db_set` to skip updating `modified` while the same document is being saved, because it checks `frappe.flags.currently_saving` first.
MUST expect `frappe.db.set_value` to clear the document cache before it writes — for the named row when the second argument is a string, and for the whole DocType when it is not.
MUST call `frappe.clear_document_cache` in the same transaction after any raw `frappe.db.sql` write, because that path never reaches the invalidation and `get_cached_doc` returns the cached object before reading the database.
NEVER claim `get_cached_doc` goes stale after `db.set_value`; that path already dropped the key, and the genuinely stale reader is one following raw SQL, a direct table write, or another process.
MUST read with `get_doc` rather than `get_cached_doc` where the value decides a write, because a cache miss is cheap and a stale branch is not.

## values

db_set skips: validate, before_validate, before_save, on_update, and every step inside _validate
db_set runs: before_change, the write, on_change, and notify_update when notify is true
frappe.db.set_value runs: the cache invalidation and the write, and no controller method
write target: set_single_value when the DocType is single, set_value otherwise
cache invalidation on set_value: the named row for a string name, the whole DocType for a filter
no invalidation: frappe.db.sql

## how

`db_set` is reached for as the write that runs nothing, and it is the write that runs less. The two methods it does run are the change pair, which is exactly where a notification, an audit row or a recalculation is usually registered — so the loop someone used `db_set` to break is still there. The question to ask about any write is not whether it is an ORM save but which of the three levels it sits on: the full save, `db_set` with the change pair, and the module function with nothing.

Those same three levels decide cache correctness, in the opposite direction. The two upper levels clear the document cache for you; the raw SQL level does not, and there is no warning — the next reader in this request or a later one simply gets the document as it was. So raw SQL is the level that has to carry its own invalidation, written next to it and inside the same transaction, and the reason to prefer `db.set_value` whenever the write can name its rows is that the invalidation then cannot be forgotten.

Neither shortcut belongs on a field the application reasons about. Skipping `validate` also skips `validate_workflow`, and a status written past the transition rules is a row the workflow can no longer move, with nothing recording how it got there.
