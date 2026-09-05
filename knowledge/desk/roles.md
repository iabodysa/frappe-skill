---
name: roles
description: A Custom Role replaces a report's own role table instead of adding to it, and a report with rows on neither table is permitted to everyone.
triggers: ["is_permitted", "set_doctype_roles", "on_trash", "get_custom_allowed_roles", "run", "Report", "Custom Role", "Cannot edit a standard report. Please duplicate and create a new report", "You are not allowed to delete Standard Report", "Must specify a Query to run", "report role permission", "custom role for a report", "every single user can open this report and i never gave anyone access", "why is my report visible to people who should not see it", "i added a role restriction and now nobody can open the report at all", "adding one role silently threw away all the roles i had set before", "i emptied the role list and the old permissions came back on their own", "the roles i listed on the report are being completely ignored", "i made a second permission record for the same report and it does nothing", "how do i actually lock a report down to one group of people", "the role table filled itself in on some reports but stayed empty on mine", "the permission check passes but users still see rows they should not", "who is allowed to open a report when no roles are listed anywhere", "deleting the report left a stray permission record behind"]
product: frappe
---

# Report roles

## paths

frappe/core/doctype/report/report.py — is_permitted, set_doctype_roles, on_trash
frappe/core/doctype/custom_role/custom_role.py — get_custom_allowed_roles
frappe/desk/query_report.py — run

## rules

MUST read a Custom Role that names one role as removing every role the report's own Has Role table lists; those rows stay in the database and stop being read.
MUST keep rows in the Custom Role roles table, because an empty list is falsy and the report's own table answers again.
NEVER create a second Custom Role for the same report; get_custom_allowed_roles reads one record with no ordering and the other is never seen.
MUST list roles on a standard report, because set_doctype_roles fills the table on before_insert only, only when is_standard is No, and only for a ref_doctype that is not a child table.
NEVER read is_permitted as scoping rows; it compares frappe.get_roles for the session against the allowed list and returns true when the list is empty.
MUST close a report nobody should open at the ref_doctype's report permission, which run checks with frappe.has_permission before the report runs.

## values

order: Has Role rows, then Custom Role rows replace them entirely
empty Custom Role roles table: the report's own Has Role table answers
rows on neither table: permitted
auto-filled from: ref_doctype permissions at permlevel 0
compared against: frappe.get_roles() of the session, never the user argument
removed with the report: delete_custom_role("report", name) in on_trash

## how

Two tables answer one question and the second is an assignment, not an addition. Read the roles a
report actually enforces as the Custom Role's rows when it has any, and as the report's own rows
otherwise; a Custom Role whose child table is emptied silently restores the roles it replaced.

An empty result means permitted, so a report whose JSON lists no roles is open to every user
who holds the ref_doctype's report permission. Decide whether that right is the intended limit before
adding roles, because a role list narrows the access the DocType permission already granted.

is_permitted answers who may open the report and nothing about which rows come back; the rows are a
separate pass taking its own user.
