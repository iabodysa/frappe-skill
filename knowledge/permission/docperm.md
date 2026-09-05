---
name: docperm
description: The DocPerm row is the only thing that refuses a write; in_create and read_only change which list a DocType appears in and stop nothing.
triggers: ["has_permission", "get_role_permissions", "get_valid_perms", "get_all_perms", "add_permission", "update_permission_property", "reset_perms", "setup_custom_perms", "UserPermissions.build_permissions", "build_doctype_map", "can_create", "in_create", "can_write", "can_search", "role", "permlevel", "if_owner", "read", "write", "create", "delete", "submit", "cancel", "amend", "report", "export", "import", "share", "print", "email", "PermissionEngine", "execute", "get_columns_and_fields", "Custom Docperm", "docperm row permission", "in_create and read_only doctype flags", "i marked the doctype so it cannot be created but records still get inserted", "i locked the form yet writes still save new records", "why does the setting that hides the new button not stop writes", "the role has no rights but the user can still edit", "a user cannot open a record even though i gave the role access", "how do i see exactly what one named user is allowed to open", "i changed the permissions and nothing changed for the user", "my permission edits keep getting lost after an update", "everything works when i log in as admin and breaks for real users", "where do i actually edit who can do what", "a background job wrote to a locked record and i cannot explain it", "the nightly task bypassed all my permission rules", "a user in that role still sees a record he should not be allowed to open even though the read column for the role looks off"]
product: frappe
---

# DocPerm

## paths

frappe/permissions.py — has_permission, get_role_permissions, get_valid_perms, get_all_perms, add_permission, update_permission_property, reset_perms, setup_custom_perms
frappe/utils/user.py — UserPermissions.build_permissions, build_doctype_map, can_create, in_create, can_write, can_search
frappe/core/doctype/docperm/docperm.json — role, permlevel, if_owner, read, write, create, delete, submit, cancel, amend, report, export, import, share, print, email
frappe/core/doctype/custom_docperm/custom_docperm.json — role, permlevel
frappe/core/page/permission_manager/permission_manager.js — PermissionEngine
frappe/core/report/permitted_documents_for_user/permitted_documents_for_user.py — execute, get_columns_and_fields

## rules

MUST read the DocPerm rows in the DocType JSON as the only refusal; everything else on the DocType names where it appears.
NEVER read in_create: 1 as a lock. build_permissions sorts the DocType into in_create instead of can_create and then folds in_create back into can_write, so insert() still succeeds.
NEVER read read_only: 1 as a lock either; it removes the DocType from search.
MUST audit an immutable DocType in three passes and MUST NOT stop at the first — the DocPerm rows, then in_create and read_only, then the calling code, because a scheduler or submit-time write runs with no session user and no role to grant.
MUST make read the only right every role holds when code is meant to be the sole writer, and MUST set ignore_permissions at the writing call site.
MUST open the Role Permissions Manager at /app/permission-manager to read or edit the rules, and MUST run the Permitted Documents For User report to answer what one named user can open.
NEVER generate a markdown table or a stored copy of DocPerm rows; it is a rebuild of both, it is stale the moment it is written, and it keeps naming DocTypes the app no longer installs.
MUST edit rights through add_permission and update_permission_property rather than by writing tabDocPerm, because a customized DocType's rights move to Custom DocPerm.
NEVER rehearse a DocPerm design against a session logged in as Administrator; has_permission returns True for that user before any DocPerm row is read.

## values

refuses: the DocPerm row
has_permission for Administrator: True, returned before the DocPerm rows are read
in_create: not offered in create, still writable
read_only: not offered in search
customized rights: Custom DocPerm, written by setup_custom_perms
live editor: Role Permissions Manager, /app/permission-manager
live answer for one user: Permitted Documents For User

## how

Read a DocType's permission story from the rows outward. The rights columns are the decision; in_create and read_only are list membership, and an absence there is a missing button rather than a hole. Confusing the two costs a day, because the audit that found no New button reports a locked DocType while the API accepts writes.

The reverse ordering is what makes a DocType genuinely code-only: give every role read alone, and let the one path that must write it say ignore_permissions at the call site where the reason is visible. Then the refusal holds for the desk, the API and the portal at once, and the exemption is one grep away.

Two live places already answer "who can do what", and both are permission-aware and current. A generated snapshot answers the same question worse and rots in a specific way — it keeps rows for roles the JSON grants nothing, because nothing recomputes it. When the question is about one named user rather than the rules, the report is the right instrument; the rules alone cannot answer it, since User Permissions narrow what a granted right actually reaches.
