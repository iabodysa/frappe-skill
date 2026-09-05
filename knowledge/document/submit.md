---
name: submit
description: The action is chosen by comparing the docstatus already read from the database with the one now set on the object, so a second submit becomes update_after_submit and two requests that both read a draft both submit.
triggers: ["_submit", "set_docstatus", "check_docstatus_transition", "validate_update_after_submit", "run_before_save_methods", "run_post_save_methods", "DocStatus", "is_draft", "is_submitted", "is_cancelled", "get_value", "get_values", "get_singles_dict", "DocstatusTransitionError", "Error: Document has been modified after you have opened it", "`as_iterator` only works with `as_list=True` or `as_dict=True`", "submit action docstatus", "how does frappe decide submit vs update", "two people clicked submit at the same time and the entry posted twice", "duplicate postings when the same request is sent twice quickly", "why did the same document create two sets of entries", "the value i change on a submitted record is silently ignored", "editing a field after submitting does nothing and no error appears", "why can i not change this field once the record is submitted", "i cannot put a submitted record back to draft", "how do i reopen a submitted document as a draft again", "my checks run a second time when i submit and i did not expect that", "the code that should run once on submit did not run the second time", "clicking submit again asks for a different permission than before", "the document was submitted and now cannot be changed or edited without first cancelling and amending it"]
product: frappe
---

# Submit

## paths

frappe/model/document.py — submit, _submit, set_docstatus, check_docstatus_transition, validate_update_after_submit, run_before_save_methods, run_post_save_methods, DocStatus
frappe/model/docstatus.py — DocStatus, is_draft, is_submitted, is_cancelled
frappe/database/database.py — get_value, get_values, get_singles_dict
frappe/exceptions.py — DocstatusTransitionError

## rules

MUST read submit as setting `docstatus` to 1 in memory and calling `save`; `_submit` does nothing else.
MUST expect a second submit of an already-submitted document to take `_action` update_after_submit, so `on_submit` does not run again and `check_permission` asks for submit rather than write.
NEVER treat that as protection against two concurrent requests; `check_docstatus_transition` compares a docstatus already read into the object and takes no lock.
MUST take the row lock before the read that decides, with `for_update=True` on `frappe.db.get_value`, and MUST use the value that locking read returned, because a later plain read answers from the snapshot the transaction opened before the lock.
MUST expect `validate` to run again on submit, because `run_before_save_methods` calls `validate` and then `before_submit`.
MUST expect `on_update` before `on_submit`; `run_post_save_methods` runs both for the submit action.
MUST expect a field changed after submit to need `allow_on_submit`, because `validate_update_after_submit` runs on that action and checks every field and every new child row against it.
NEVER expect a draft to be reachable again from a submitted document; the 1 to 0 transition raises `DocstatusTransitionError`.

## values

docstatus values: 0 draft, 1 submitted, 2 cancelled
action from stored 0: 0 gives save, 1 gives submit, 2 raises DocstatusTransitionError
action from stored 1: 1 gives update_after_submit, 2 gives cancel, 0 raises DocstatusTransitionError
action from stored 2: any target raises ValidationError
permission asked: submit for the submit action, submit for update_after_submit, cancel for the cancel action
lock: for_update on get_value, get_values and get_singles_dict

## how

Submit is not a separate write path. It sets a number on the object and calls `save`, and every ordering question about it is answered by the save order. What submit adds is the transition table: the action is chosen by pairing the docstatus the object was loaded with against the docstatus it now carries, and that pairing decides which methods run and which permission is asked for.

The consequence people get backwards is what the table protects. It refuses a repeated transition, so clicking submit twice on a document that is already submitted posts nothing twice, and that is real. It says nothing about two requests that each loaded a draft: both see 0, both take the submit branch, both run `on_submit`. The check is a comparison of two values already in memory, so the only thing that makes a submit-time effect happen once is a row lock taken before the read that decides, and the locking read's own return value being what the decision uses.

After submit the document is not frozen but narrowed. The update_after_submit action skips `validate` and `on_update`, runs its own pair of methods, and lets through only the fields and the new child rows the DocType marked `allow_on_submit`. When a change appears to be silently ignored on a submitted document, read `allow_on_submit` before reading the controller.
