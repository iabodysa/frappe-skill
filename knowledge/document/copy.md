---
name: copy
description: copy_doc keeps no_copy fields unless it is asked not to, clears only name, owner, creation, modified, modified_by and docstatus on the parent and its children, and carries nothing that lives outside the document's own tables — no attachment, no comment, no tag and no assignment.
triggers: ["copy_doc", "ignore_no_copy", "remove_no_copy_fields", "fields_to_clear", "get_all_children", "set_parent_in_children", "create_attachment_copy", "make_new_document", "as_dict", "get_valid_dict", "get_valid_columns", "default_fields", "optional_fields", "child_table_fields", "amended_from", "amendment_date", "__islocal", "duplicate a document", "what does copy_doc copy", "copy loses attachments", "no_copy field still copied", "the duplicate is missing all the attached files", "why do the files not come across when i duplicate a record", "how do i carry attachments over to a copied record", "fields i marked as not to be copied are still filled in on the duplicate", "the copy keeps values that should have come out blank", "why is the reference number copied onto the duplicate", "the duplicate has none of the comments or assignments of the original", "the copied record is never saved and just disappears", "duplicating an approved document gives me another approved one in my tests", "the copy came out already submitted instead of a fresh draft"]
product: frappe
---

# Copy

## paths

frappe/__init__.py — copy_doc, get_doc
frappe/model/__init__.py — default_fields, optional_fields, child_table_fields
frappe/model/base_document.py — as_dict, get_valid_dict, get_valid_columns
frappe/model/document.py — get_all_children, set_parent_in_children
frappe/model/meta.py — Meta.get_valid_columns
frappe/api/v2.py — copy_doc
frappe/core/doctype/file/file.py — create_attachment_copy
frappe/automation/doctype/auto_repeat/auto_repeat.py — make_new_document

## rules

MUST pass `ignore_no_copy=False` to drop the fields marked no_copy; the parameter DEFAULTS TO TRUE, so a plain `frappe.copy_doc(doc)` carries every no_copy field on the parent and on every child row.
MUST read the copy as holding nothing outside the document's own table and child tables; `as_dict` is built from `get_valid_columns`, so attachments, comments, versions, tags, assignments and likes are not in it.
MUST re-attach files by hand after a copy, or copy each File row with `create_attachment_copy`, because the attachment is a File record pointing at the source document and no part of `copy_doc` touches it.
MUST expect `idx` to survive on the parent and on every child, because it is a default field and is absent from the list `copy_doc` clears.
MUST expect a child row to keep the SOURCE document's `parent`, `parentfield` and `parenttype` until the copy is inserted, because those three are child table columns and only `set_parent_in_children` rewrites them.
NEVER read a copy's `docstatus` as cleared inside a test run; `docstatus` is added to the cleared list only when `frappe.local.flags.in_test` is unset, so a test copying a submitted document gets a submitted copy.
MUST expect `amended_from` and `amendment_date` to be cleared on the PARENT ONLY; the child loop clears the shorter list.
MUST insert the returned document yourself; `copy_doc` sets `__islocal` on the parent and every child and returns without saving, so no validation, no naming and no hook has run on it.
MUST expect the returned object to be a fresh `Document` built by `get_doc` from a deepcopy, so mutating it cannot reach the source document.
MUST pass a dict rather than a Document where the source is already a plain dict; `copy_doc` skips `as_dict` in that case and deep-copies what it was handed, including any key the DocType does not define.
MUST read the v2 API `copy_doc` route as checking the `read` permission and applying field level read permissions before copying, and as passing `ignore_no_copy` true by default, so the copy it returns carries no_copy fields to the caller.

## values

cleared on the parent: name, owner, creation, modified, modified_by, docstatus, amended_from, amendment_date
cleared on each child: name, owner, creation, modified, modified_by, docstatus
docstatus exception: kept when frappe.local.flags.in_test is set
kept: idx, parent, parentfield, parenttype, and every no_copy field unless ignore_no_copy is False
set: __islocal on the parent and on every child
never carried: attachments, comments, versions, _user_tags, _comments, _assign, _liked_by, _seen
not done: insert, validation, naming, any doc_events handler
callers passing ignore_no_copy=False: make_new_document in Auto Repeat

## how

`copy_doc` is a field-level clone of one row and its child rows, not a duplicate of the record as a user
sees it. Everything a user reads on the form that lives in another table — the attachments, the comments,
the assignment, the tags — is outside the copy, and none of it announces its absence.

The parameter name is the trap. `ignore_no_copy` defaults to true, and true means the no_copy marks are
IGNORED, so the fields a designer marked as must-not-be-copied are exactly the fields a default call
copies. Where a copy is offered to a user, pass `ignore_no_copy=False` and let the DocType's own marks
decide.

The result is an unsaved document with the parent's identity stripped and the children still pointing at
the old parent. That is safe only because insert rewrites them; anything that reads the copy before
inserting it — a validation, a report, a hook you call yourself — sees the source document's name in
every child row.
