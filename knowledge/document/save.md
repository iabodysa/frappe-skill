---
name: save
description: The controller's validate runs after the framework has already set defaults, resolved every fetch_from and checked permissions, and before the framework validates its own field properties, so where a hand-written check sits decides whether it never fires or throws first.
triggers: ["insert", "run_before_save_methods", "run_post_save_methods", "_validate", "_validate_links", "_set_defaults", "set_docstatus", "check_if_latest", "check_if_locked", "validate_higher_perm_levels", "set_new_name", "set_title_field", "update_children", "clear_cache", "notify_update", "save_version", "load_doc_before_save", "Error: Document has been modified after you have opened it", "order of hooks on save", "validate runs before or after defaults", "my validation check never runs no matter what i put in it", "why does my check in the code never fire when i save the record", "the custom error i wrote never shows up on save", "i get my own error message instead of the required field message", "the wrong error text comes up when a mandatory field is empty", "why does my error hide the built in required field warning", "it keeps telling me the document has been modified after i opened it", "saving fails saying someone else changed the record but nobody did", "why do i get a modified after you opened it error on every save", "the value i read right after saving is not the one that got stored", "the child table rows end up with a different status than the parent", "which of my code hooks runs first when a record is saved"]
product: frappe
---

# Save

## paths

frappe/model/document.py — insert, save, run_before_save_methods, run_post_save_methods, _validate, _validate_links, _set_defaults, set_docstatus, check_if_latest, check_if_locked, validate_higher_perm_levels, set_new_name, set_title_field, update_children, clear_cache, notify_update, save_version, load_doc_before_save

## rules

MUST expect `_set_defaults`, `check_permission`, `check_if_latest` and `_validate_links` to have run before `validate`, because both `insert` and `save` call `run_before_save_methods` after them.
NEVER re-read a `fetch_from` source inside `validate`; `_validate_links` wrote that value already, on insert and on save alike.
MUST expect a `frappe.throw` in `validate` to pre-empt `_validate_mandatory`, `_validate_non_negative` and `validate_set_only_once`, because `run_before_save_methods` returns before `_validate` is called.
MUST re-read the tests before deleting a controller check that the framework repeats later, because the framework's message, its field and its exception class are what the user then sees instead.
MUST expect `before_validate` on save and on submit only; `run_before_save_methods` does not call it for cancel or for update_after_submit.
MUST expect `flags.ignore_validate` to skip `validate`, `before_save`, `before_submit`, `before_cancel` and `before_update_after_submit` in one step, because `run_before_save_methods` returns before all of them.
MUST expect `on_change` after `on_update`, `notify_update`, `update_global_search` and `save_version`, so a document read inside `on_change` is already written and already versioned.
NEVER put a write meant to survive inside `run_post_save_methods` without deciding what a later exception does to it; every method there runs inside the caller's transaction.
MUST expect `set_docstatus` to copy the parent's docstatus onto every child row, twice on insert and twice on save.

## values

insert order: _set_defaults, set_user_and_timestamp, set_docstatus, check_permission create, check_if_latest, _validate_links, before_insert, set_new_name, set_parent_in_children, validate_higher_perm_levels, run_before_save_methods, _validate, set_docstatus, db_insert, update_children, run_post_save_methods
save order: check_if_locked, _set_defaults, check_permission write, set_user_and_timestamp, set_docstatus, check_if_latest, set_parent_in_children, set_name_in_children, validate_higher_perm_levels, _validate_links, run_before_save_methods, _validate, validate_update_after_submit, set_docstatus, db_update, update_children, run_post_save_methods
run_before_save_methods: reset_seen, before_validate for save and submit, return on flags.ignore_validate, then the action's own methods, then set_title_field
action methods before the write: save — validate, before_save; submit — validate, before_submit; cancel — before_cancel; update_after_submit — before_update_after_submit
_validate on the parent: _validate_mandatory, _validate_data_fields, _validate_selects, _validate_non_negative, _validate_length, _fix_rating_value, _validate_code_fields, _sync_autoname_field, _extract_images_from_text_editor, _sanitize_content, _save_passwords, validate_workflow
_validate on each child row: the same list without _validate_mandatory and validate_workflow
_validate last step: optional fields cleared when the document is new, validate_set_only_once when it is not
_validate skipped entirely: _action cancel
run_post_save_methods: the action's own methods, clear_cache, notify_update unless flags.notify_update is false, update_global_search, save_version, on_change
action methods after the write: save — on_update; submit — on_update, on_submit; cancel — on_cancel, check_no_back_links_exist; update_after_submit — on_update_after_submit

## how

One list of methods runs before the write and one after it, and the controller's own methods are entries inside those lists rather than a layer around them. Everything the framework does to prepare the document — defaults, timestamps, docstatus, the permission check, the stale-copy check, link resolution and `fetch_from` — happens before `run_before_save_methods`; everything the framework does to check its own declared field properties happens after it, in `_validate`. So the useful question about any hand-written rule is not whether it duplicates a DocField property, it is which side of `run_before_save_methods` its counterpart lives on.

That gives two different deletions with two different proofs. A controller line that re-does preparation the framework already finished never fired, so removing it changes nothing anyone can observe and the proof is that the value still arrives. A controller `frappe.throw` that re-does a check `_validate` would make always fired first, so removing it changes the wording, the exception class and the field the error attaches to, and any test asserting the old text fails for a correct reason.

Read `_action` as the thing that selects both lists. It is set from the docstatus transition, not from the method name, so `save()` on a submitted document runs the update_after_submit pair and neither `validate` nor `on_update` reaches it. When behaviour appears to be missing on one kind of write, name the action first and read the two lists for it.
