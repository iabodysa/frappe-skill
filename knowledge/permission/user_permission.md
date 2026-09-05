---
name: user_permission
description: A User Permission carries four fields, and the row condition it generates also admits a row whose scoped field is empty unless apply_strict_user_permissions is on.
triggers: ["has_permission", "get_user_permissions", "has_user_permission", "add_user_permission", "remove_user_permission", "clear_user_permissions_for_doctype", "user_permission_exists", "get_applicable_for_doctype_list", "build_match_conditions", "add_user_permissions", "apply_strict_user_permissions", "User Permission", "System Settings", "User permission already exists", "Use of sub-query or function is restricted", "Illegal SQL Query", "user permission not filtering", "user permission empty value applies_to_all", "i restricted the user to one company and he still sees records from all of them", "the restriction lets through records where the field is blank", "why do rows with an empty company still appear for a restricted user?", "restricting a user to one branch also filtered lists i never wanted filtered", "my restriction leaks records that have nothing filled in that field", "the check passes before the record exists even though the user is restricted", "a user can create a document for a value he is not allowed to see", "the restriction works on the list but not when creating", "restricting to a parent value does not include the ones under it", "should restricting a top level value cover everything beneath it?", "i wrote my own filter and it disagrees with what the system shows"]
product: frappe
---

# User Permission

## paths

frappe/permissions.py — has_permission, get_user_permissions, has_user_permission, add_user_permission, remove_user_permission, clear_user_permissions_for_doctype
frappe/core/doctype/user_permission/user_permission.py — get_user_permissions, user_permission_exists, get_applicable_for_doctype_list
frappe/model/db_query.py — build_match_conditions, add_user_permissions
frappe/core/doctype/system_settings/system_settings.json — apply_strict_user_permissions

## rules

MUST read a user's permitted values through frappe.permissions.get_user_permissions, which returns a dict keyed by the allow DocType.
NEVER pluck for_value out of tabUser Permission by hand; the pluck drops applicable_for, drops hide_descendants, and drops the Redis tier that get_user_permissions reads.
MUST apply applicable_for, because a User Permission may bind one DocType only and a plucked list applies every row to every DocType in that scope.
MUST apply hide_descendants, because get_user_permissions expands a nested-set value to its descendants when the flag is off and returns the named node alone when it is on.
NEVER cache the result again in frappe.local_cache; get_user_permissions caches per user in Redis and the cache is cleared when a User Permission changes, while a local cache lives for one request.
MUST expect {} for Administrator and for Guest, returned before the database is touched.
MUST read apply_strict_user_permissions in System Settings before stating what a scoped list returns, because the generated condition carries an ifnull(...)='' leg only while that setting is off.
NEVER write the row filter by hand as field in (allowed); that is a second implementation which disagrees with the framework on exactly the empty row.
MUST close an empty scoped field at the source by making the field required, never with a filter repeated at every read site.
MUST set ignore_user_permissions on a Link field that should not narrow the list, because add_user_permissions walks EVERY Link field pointing at the scoped DocType.
NEVER read frappe.has_permission(doctype, ptype) with no doc as scoped by User Permission; has_user_permission is called only from the doc branch, so a role-only check such as a "create" permission test before a doc exists passes for any Company or Supplier the role is allowed at all.

## values

returned per row: doc, applicable_for, is_default, hide_descendants
key: the allow DocType
cache: frappe.cache.hget("user_permissions", user)
short circuit: Administrator, Guest
has_permission with no doc: role_permissions only, has_user_permission not called
loose condition: ifnull(`tab<DocType>`.`<field>`, '')='' or `<field>` in (...)
strict condition: `<field>` in (...)
switch: apply_strict_user_permissions in System Settings

## how

A User Permission is metadata, so the enforcement is already written: DatabaseQuery turns the rows into a WHERE fragment on every read through add_user_permissions, and a scope declared here binds every endpoint at once instead of every endpoint remembering to apply it.

The temptation is to read the table directly, because for_value is the value you want and the other three fields look like bookkeeping. They are not: applicable_for narrows which DocType the rule binds, hide_descendants decides whether a tree value means one node or a subtree, and both are silently discarded by a pluck, so the scope comes out wrong in whichever direction the data happens to fall.

The empty-value leg is the part that surprises a reviewer. The same data answers two ways depending on one checkbox, so a hand-written filter that looks stricter than the framework is not enforcing a permission — it is hiding a data-entry defect. Fix the record, then read the setting before claiming what the framework returns.
