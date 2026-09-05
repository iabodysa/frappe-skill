---
name: cancel
description: Cancel sets docstatus to 2 in memory and calls save, and that save skips _validate entirely, so every framework field rule and the workflow check are not run on the write that cancels.
triggers: ["_cancel", "save", "_validate", "run_before_save_methods", "run_post_save_methods", "check_no_back_links_exist", "DocStatus", "check_if_doc_is_linked", "check_if_doc_is_dynamically_linked", "Error: Document has been modified after you have opened it", "Standard DocType can not be deleted.", "This document can not be deleted right now as it", "what happens when a document is cancelled", "cancel skips validate", "my validation rules do not run when a document is cancelled", "cancelling lets through values that saving would have blocked", "why are my checks skipped only when i cancel", "it refuses to cancel because another document is linked to it", "i get a message that this document cannot be cancelled right now", "how do i block a cancellation when a condition is not met", "my reversal entries disappear after a cancellation fails", "the code that runs on cancel executed but the changes are gone afterwards", "i cannot edit or save a document after it has been cancelled", "the approval step is not checked at all when the document is cancelled"]
product: frappe
---

# Cancel

## paths

frappe/model/document.py — cancel, _cancel, save, _validate, run_before_save_methods, run_post_save_methods, check_no_back_links_exist, DocStatus
frappe/model/delete_doc.py — check_if_doc_is_linked, check_if_doc_is_dynamically_linked

## rules

MUST read cancel as setting `docstatus` to 2 in memory and calling `save`; `_cancel` does nothing else.
MUST expect `_validate` to be skipped on cancel, so `_validate_mandatory`, `_validate_non_negative`, `validate_set_only_once` and `validate_workflow` do not run on that write.
NEVER put a rule that must hold at cancellation in `validate`; `run_before_save_methods` calls `before_cancel` alone for that action.
MUST expect `before_cancel` before `db_update` and `on_cancel` after `db_update` and `update_children`, because `run_before_save_methods` selects the first and `run_post_save_methods` the second.
MUST expect `check_no_back_links_exist` immediately after `on_cancel`, so a document another submitted document still links to refuses the cancel after `on_cancel` already ran.
MUST read `flags.ignore_links` as turning both back-link checks off, so a cancel run with it set leaves another submitted document pointing at a cancelled row.
MUST write a reversal in `on_cancel` as something that survives being run against a row already written, because the write happened before it.
NEVER expect a cancelled document to be saved again; `check_docstatus_transition` raises for every target once the stored docstatus is 2.

## values

hook order on cancel: before_cancel, db_update, update_children, on_cancel, check_no_back_links_exist, clear_cache, notify_update, update_global_search, save_version, on_change
methods not run on cancel: validate, before_validate, before_save, on_update, and every step inside _validate

## how

Cancel reuses `save` and differs from it in two places only: which methods `run_before_save_methods` and `run_post_save_methods` select, and the fact that `_validate` is skipped. Everything else — the permission check, the stale-copy check, link resolution, the child updates — happens exactly as on any other save.

The skipped `_validate` is the part that decides design. A rule expressed as a DocField property is not enforced on the write that cancels, so a document can be cancelled while holding a value the same document could not have been saved with. Put a cancellation rule in `before_cancel`, which is the only method the framework runs for this action before the write.

`on_cancel` runs after the row is written, and `check_no_back_links_exist` runs after `on_cancel`. That order means a reversal posted in `on_cancel` can execute and then be undone by the exception the back-link check raises, so the reversal must be something the transaction rollback fully removes rather than something with an effect outside the database.
