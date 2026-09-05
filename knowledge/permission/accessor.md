---
name: accessor
description: Every read and every write has a checked call and an unchecked one, and the permission code sits only in DatabaseQuery and Document, never in frappe.db.
triggers: ["get_list", "get_all", "get_doc", "DatabaseQuery.execute", "_set_permission_map", "build_match_conditions", "add_user_permissions", "get_permission_query_conditions", "insert", "save", "submit", "cancel", "db_set", "check_permission", "sql", "get_value", "get_values", "set_value", "delete", "execute_query_report", "execute_script", "Report", "Workflow Action", "Cannot make dict for single fieldname", "Use of sub-query or function is restricted", "Illegal SQL Query", "checked vs unchecked read and write", "get_list vs get_all permission check", "why can everyone see everyone else's records in this list", "this list is leaking records from other users and i am furious", "the list page shows rows that should be filtered by user", "one salesman can see all the other salesmen's orders", "the report shows every row no matter who runs it", "my custom report ignores the user restrictions", "how do i make a list return only what the logged in user is allowed to see", "everything looked fine as admin but a normal user sees too much", "a field got written without any permission check", "setting a value directly skipped my validation", "the api let a user update a document they should not touch", "how do i tell whether a read is checked or unchecked"]
product: frappe
---

# Accessor

## paths

frappe/__init__.py — get_list, get_all, get_doc
frappe/model/db_query.py — DatabaseQuery.execute, _set_permission_map, build_match_conditions, add_user_permissions, get_permission_query_conditions
frappe/model/document.py — get_doc, insert, save, submit, cancel, db_set, check_permission
frappe/database/database.py — sql, get_value, get_values, set_value, delete
frappe/core/doctype/report/report.py — execute_query_report, execute_script
frappe/workflow/doctype/workflow_action/workflow_action.py — get_permission_query_conditions

## rules

MUST call get_list wherever the session user's rights bind, and MUST call get_all only where the answer must not depend on who is logged in.
MUST read get_all as two changes and not one: it sets ignore_permissions and it sets limit_page_length to 0, so it is also the unbounded read.
NEVER expect frappe.db.sql, frappe.db.get_value, frappe.db.get_values, frappe.db.set_value or frappe.db.delete to check anything; there is no permission code in frappe/database/database.py and no flag that adds it.
NEVER expect frappe.get_doc to check read; at the document layer only the unchecked form exists and the check belongs to the caller.
MUST read for_update=True as a locking read alone, since load_from_db carries it as a flag into the parent and child reads and nothing else.
MUST expect insert, save, submit and cancel to check the document they are called on and no other, so target.submit() says nothing about the document the caller read.
NEVER read db_set as a save; it writes the field with no check_permission and no validate, and it does run before_change and on_change.
NEVER call an explicit frappe.has_permission(..., throw=True) above a write redundant until three things hold — the later write lands on the SAME document, that path is reachable with no ignore_permissions and no db_set, and it asks the SAME permission.
MUST read the WHERE clause the author typed into a Query Report as the whole of its row scope, because execute_query_report calls frappe.db.sql and DatabaseQuery is never entered.
MUST ask which accessor a Script Report calls, because execute_script runs the report's own python through safe_exec: get_all returns every row and get_list runs the permission path.
MUST call get_list on a table the framework owns — Workflow Action, ToDo, File, Comment, Version, Email Queue, User Permission, Has Role — because hooks.py already declares the row scope for it.

## values

get_list: DatabaseQuery with permissions on
get_all: the same call with ignore_permissions=True and limit_page_length=0
DocPerm read: _set_permission_map, refuses the whole list before a condition is built
User Permission rows: build_match_conditions calling add_user_permissions
the app's condition: get_permission_query_conditions, from hooks.py and from Server Script
insert: check_permission("create")
save: check_permission("write", "save")
submit: check_permission("submit")
cancel: check_permission("cancel")
db_set: nothing
frappe.db.set_value: nothing

## how

get_list and get_all differ by one keyword argument and the name warns you of nothing, so choosing between them is not a style question — the unchecked one removes three layers at once: the DocPerm read that refuses the whole list, the User Permission rows that narrow it through every Link field, and the app's own condition.

One question decides it. Is the current session a user whose rights should bind, or the system? Anything reached from @frappe.whitelist, a portal route, a Web Form or a desk action is a user, and get_all there is the defect — invisible, because it behaves perfectly for whoever tests it as Administrator. A scheduler job, a patch, after_install or a computation whose answer must not move with the logged-in user is the system, and there the unchecked call is the correct one, chosen on purpose.

A count of unchecked calls is not a finding. The finding is an unchecked call reachable from an untrusted caller, and only a call graph answers that; a grep answers a different question.
