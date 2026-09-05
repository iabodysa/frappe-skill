---
name: patches
description: The handler wraps the patch body and its Patch Log row in one transaction, and it stamps the patch on any normal return, so a patch that swallowed every row failure is recorded as done and never runs again.
triggers: ["run_all", "run_single", "execute_patch", "update_patch_log", "executed", "PatchType", "delete_doc", "check_if_doc_is_linked", "check_if_doc_is_dynamically_linked", "check_permission_and_not_submitted", "add_to_deleted_document", "Standard DocType can not be deleted.", "This document can not be deleted right now as it", "patches.txt format", "write a data migration patch", "the data fix says it completed but nothing actually changed", "my one time data script is marked done and refuses to run again", "why does it think the migration step already ran when the old rows are still there", "half the records were converted and the rest were left behind", "the data script ran twice and made a mess of the records", "the same one time script keeps running on every update", "it will not let me delete the record because something still links to it", "deleting a document fails saying it cannot be deleted right now", "how do i safely remove a record that other records point at", "i forced the delete and now there are broken references everywhere", "the deleted record is gone for good and there is no way to restore it"]
product: frappe
---

# Patches

## paths

frappe/modules/patch_handler.py — run_all, run_single, execute_patch, update_patch_log, executed, PatchType
frappe/model/delete_doc.py — delete_doc, check_if_doc_is_linked, check_if_doc_is_dynamically_linked, check_permission_and_not_submitted, add_to_deleted_document

## rules

MUST read the Patch Log row as recording that a patch RAN, never that it worked. update_patch_log is called immediately after the body returns and the only thing that keeps a patch out of the log is an exception escaping it, so a loop that catches per-row failures, logs them and continues returns normally, the patch is stamped, and the legacy data stays where it is permanently.
MUST end a data patch with the comparison that proves it: count what the patch set out to move against what it moved and raise when the shortfall means the data is still there.
MUST keep per-row savepoints so one bad row does not strand the whole run, and MUST state the rule on the patch beside the number it checks. NEVER raise on any failure and NEVER swallow every failure.
MUST say what re-creates the data when a patch deliberately swallows everything; without that sentence it is indistinguishable from a patch that silently did nothing.
NEVER call frappe.db.commit inside a patch body. run_single commits before the body so it starts clean, runs the body, writes the Patch Log row, rolls the whole thing back and re-raises on any exception, and commits once on success — so the data change and the stamp are one unit.
MUST expect an inner commit to produce a patch that RUNS TWICE against different inputs, not a lost patch: the rows written so far persist, a later failure rolls back only what followed and leaves no Patch Log row, and the next run starts from a state its own code never expected.
MUST publish a written idempotency rule with a deliberately resumable patch that checkpoints, because it has taken the handler's guarantee away and owes the replacement.
MUST assert in a patch's own test both that the expected work ran AND that frappe.db.commit was called zero times; the first assertion alone passes on a patch that commits.
MUST read executed as matching only a Patch Log row with skipped 0, so a patch recorded with skipped 1 and its traceback runs again on the next attempt.
MUST prefix a patch with `finally:` in patches.txt to defer it to the end of the run; run_single appends it to frappe.flags.final_patches instead of executing it, and the log row is written without that prefix.
NEVER reach for force=True on delete_doc to get past a LinkExistsError. It skips check_if_doc_is_linked, check_if_doc_is_dynamically_linked and check_permission_and_not_submitted outright, so a row still referenced is deleted anyway, a submitted document is deleted without being cancelled, and every reference is left dangling with no error and no log line.
MUST delete or repoint the dependent rows first, then delete without the flag.
MUST give a cleanup pass a filter that actually identifies the app's own rows — an owner, a module or a creation timestamp; force is not a filter, and delete_permanently skips add_to_deleted_document so there is no Deleted Document row and no restore path.

## values

one transaction: commit before the body, body, Patch Log row, commit on success or rollback and re-raise
stamp condition: the body returned without raising
skip set: Patch Log rows with skipped 0
patch types: pre_model_sync, post_model_sync
deferred: a patchmodule beginning `finally:`

## how

The handler gives one guarantee and takes it back the moment a patch commits inside itself: the data
change and the record that it happened land together or not at all. Everything a patch author has to
decide follows from protecting that pairing. Do not commit; let the handler do it.

What the handler cannot decide is whether the work succeeded, because a normal return is all it sees.
That judgement belongs in the patch: it knows what it set out to move, so it can count what it moved
and raise when the two disagree. A patch without that comparison converts a data problem into a green
migrate and a stamped log row that guarantees nobody looks again.

A patch that deletes is where the framework's refusals matter most. A LinkExistsError is the site
protecting itself, and the flag that gets past it does not narrow the check — it removes three of them,
including the one that stops a submitted document being deleted uncancelled.
