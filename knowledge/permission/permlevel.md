---
name: permlevel
description: A permlevel violation puts the old value back and saves successfully, and Administrator returns before the check runs at all.
triggers: ["validate_higher_perm_levels", "reset_values_if_no_permlevel_access", "get_permlevel_access", "get_high_permlevel_fields", "get_role_permissions", "Error: Document has been modified after you have opened it", "Please check the value of", "permlevel violation on save", "administrator bypasses permlevel", "the field goes back to its old value after i save and there is no error", "my change is silently discarded when i save", "why does saving succeed but the value never actually changes", "the user edits the field and it reverts with no warning at all", "i restricted a field but the user can still set it while creating the record", "the restricted field inside the child table is still editable", "i want one role to edit only one field and read the rest", "how do i let a role change just the approval field and nothing else", "it works when i test as admin but not for the other user", "i expected an error but the save came back successful", "my test waits for an exception that never happens", "the restriction does not apply to some fields at all", "saving silently loses the field's new value"]
product: frappe
---

# Permlevel

## paths

frappe/model/document.py — validate_higher_perm_levels
frappe/model/base_document.py — reset_values_if_no_permlevel_access
frappe/model/meta.py — get_permlevel_access, get_high_permlevel_fields
frappe/permissions.py — get_role_permissions

## rules

MUST expect a write to a field above permlevel 0 by a role without access to be reset to its previous or default value and saved, never refused.
NEVER assert an exception in a permlevel test; MUST assert the field's value after the save.
NEVER rehearse a permlevel design from an Administrator session, because validate_higher_perm_levels returns before any check when frappe.session.user is Administrator.
MUST expect ignore_permissions and frappe.flags.in_install to skip every field restriction as well as the DocPerm.
MUST expect a NEW document to skip the child-table pass, so a restricted child field can be set at creation time.
MUST raise the permlevel of every OTHER field and leave the writable one at 0 to let a role write one field of a document it may not otherwise change; raising the field's own permlevel restricts it and never grants it.
MUST expect a field whose fieldtype is in display_fieldtypes, or whose fieldname is listed in the ignore_permlevel_for_fields flag, to be excluded from the reset without that being visible on the DocType.
MUST grant a permlevel by adding a DocPerm row carrying that permlevel and that right for the role, because get_permlevel_access collects the permlevel of every matching row.
MUST edit the PARENT DocType's DocPerm rows to change permlevel access on a child table, because get_permissions substitutes the parent's rows for a child table.

## values

level 0: governed by the ordinary DocPerm
level above 0: restricted, granted by a DocPerm row at that level
violation: value reset, document saved, response successful
Administrator: exempt, returns before the check
ignore_permissions: exempt
frappe.flags.in_install: exempt
new document: child rows not reset
excluded: display_fieldtypes, ignore_permlevel_for_fields

## how

Every other refusal in the permission model raises. This one does not: it resets and reports success, so nothing in the UI or the API says a value was discarded, and the only observable is the stored value after the save. Design the test around that observable.

The direction is the usual mistake. A permlevel restricts; it never grants. So the shape of "this role may edit only the approval field" is not a high permlevel on that field — it is a high permlevel on all the others. Getting it backwards produces a design that reads correct in review and enforces nothing.

Two exemptions are worth carrying in the head while reading any code path: Administrator, and anything that already set ignore_permissions. Both mean a permlevel design that was demonstrated working was demonstrated on a path where it never ran.
