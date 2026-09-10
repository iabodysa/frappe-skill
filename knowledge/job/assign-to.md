---
name: assign-to
description: frappe.desk.form.assign_to carries the ToDo-queue assignment primitive — add, remove, close, clear and set_status — that Assignment Rule and manual assignment both wrap.
triggers: ["assign_to", "assign_to.add", "close_all_assignments", "ToDo assignment primitive", "document to user assignment queue", "assign a document to a role", "clear an assignment", "close an assignment"]
product: frappe
---

# Assign to

## paths

frappe/desk/form/assign_to.py — add, add_multiple, close_all_assignments, remove, remove_multiple, close, set_status, clear

## rules

MUST reach document-to-user or document-to-role assignment through `frappe.desk.form.assign_to.add`, never by inserting a ToDo row directly; `add` carries the lifecycle the rest of the module depends on.
MUST use `close_all_assignments(doctype, name)` to end every open assignment on one document at once.
MUST use `remove`, `close`, `clear` and `set_status` for the narrower single-assignment lifecycle operations they each name.

## how

Every document-to-user queue in the framework — manual Desk assignment, Assignment Rule's round robin — ends by calling into this module rather than writing a ToDo directly, so a custom assignment feature should call these functions instead of re-deriving ToDo creation and lifecycle.
