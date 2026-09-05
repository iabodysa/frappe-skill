---
name: hiding-a-doctype
description: A DocType has no root hidden key, so hiding one is a DocPerm question, and read_only removes the DocType from can_search where no link restores it.
triggers: ["hide_toolbar", "read_only", "in_create", "show_name_in_global_search", "index_web_pages_for_search", "hidden", "UserPermissions.build_permissions", "UserPermissions.load_user", "can_search", "can_read", "can_write", "get_search_in_list", "get_doctypes", "meta.get(\"hidden\")", "Doctype", "Docfield", "Auto Email Report", "Invalid Output Format", "Please set filters value in Report Filter table.", "hide a doctype from the desk", "doctype not showing in search", "i set it to hidden but the form still shows up everywhere", "why did marking it hidden do absolutely nothing", "how do i hide a form from users without deleting it", "the flag i added changed nothing and there was no error", "i migrated and the hidden setting had no effect at all", "after making it read only nobody can find it in the search bar anymore", "the form vanished from the top search box and i cannot get it back", "why did locking a form also remove it from search", "how do i remove the new button but still let people edit records", "users can still create records even though i hid the new option", "i added a shortcut but the locked form still does not come up in search", "the log we hardened is now unreachable for the operators"]
product: frappe
---

# Hiding a DocType

## paths

frappe/core/doctype/doctype/doctype.json — hide_toolbar, read_only, in_create, show_name_in_global_search, index_web_pages_for_search
frappe/core/doctype/docfield/docfield.json — hidden
frappe/utils/user.py — UserPermissions.build_permissions, UserPermissions.load_user, can_search, can_read, can_write, in_create
frappe/public/js/frappe/ui/toolbar/search_utils.js — get_search_in_list, get_doctypes
frappe/public/js/frappe/form/toolbar.js — in_create
frappe/email/doctype/auto_email_report/auto_email_report.py — meta.get("hidden")

## rules

NEVER write `"hidden": 1` at the root of a DocType JSON; `hidden` is a DocField key and the DocType DocType declares no field of that name, so the JSON parses, migrates and stores while nothing reads it.
MUST conceal a DocType by giving the operational roles no read DocPerm and giving System Manager read and report only.
MUST read `read_only: 1` as removing the DocType from the awesome bar as well as locking the form; build_permissions appends to can_search only when the DocType is neither single nor read-only.
NEVER expect a Workspace link or a shortcut to restore search for a read-only DocType; the two lists are independent and search_utils reads can_search.
MUST set `in_create: 1` to remove the New menu item, and MUST read it as revoking nothing, because build_permissions adds in_create back into can_write.
MUST give a DocType that operational roles must read and write a different input route rather than a flag; no flag hides it.
NEVER harden a machine-written log to read_only without naming the route the operator will use to look at it, because the hardening removes his only one.

## values

hidden at DocType root: no field, read by nothing, no error
hidden on a DocField: real
read_only 1: form locked and the DocType dropped from can_search
in_create 1: New menu item hidden, create permission unchanged
hide_toolbar 1: the form toolbar
hidden by withdrawing: DocPerm read, DocPerm report

## how

The mistake this subject exists for is a valid key at the wrong level. `hidden` is a real DocField key, so writing it at the root of a DocType JSON produces a file that parses and a migration that succeeds, and the reader gets no signal that the line does nothing. Read a flag that changed nothing by asking whether the DocType that declares it has that field, not by trying it harder.

Hiding a DocType in the Desk is a permission question with a search side effect. Withdrawing the read DocPerm removes the DocType from every list the Desk builds, because those lists are built from the permission cache. `read_only` looks like a second way to do it and is really a third consequence: it locks the form and it also drops the DocType out of can_search, and that second effect is the one nobody predicts. A DocType made read-only as a hardening step and never linked from a Workspace has no route left at all.

So decide first what the operational roles must still do. If they must read and write, no flag will hide it and the answer is a narrower input route — a form on a different DocType, or a Report — not a flag on this one.
