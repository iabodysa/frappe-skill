---
name: portal_identity
description: generate_keys overwrites api_secret on the single User row, so api_key/api_secret is one credential per user and rotating one device signs out every other device that user owns.
triggers: ["User.has_desk_access", "User.set_system_user", "User.set_roles_and_modules_based_on_user_type", "generate_keys", "apply_permissions_for_non_standard_user_type", "user_linked_with_permission_on_doctype", "doc_events", "\"*\"", "on_update", "get_sessions_to_clear", "clear_sessions", "delete_session", "operation", "status", "user", "ip_address", "reference_doctype", "reference_name", "export_from", "file_type", "report_name", "page", "User Type", "Activity Log", "Access Log", "Not a valid User Image.", "Welcome email sent", "Please setup default outgoing Email Account from Settings > Email Account", "website user vs user", "api_key api_secret portal user", "i changed the api secret on my phone and now the tablet is signed out too", "rotating the key for one device kicked out every other device", "why does resetting one device's key sign the user out everywhere?", "the portal user has no desk access but can still call our backend methods", "a customer login with no seat still reaches our internal endpoints", "should a portal account be able to hit our api at all?", "users stay signed in on unlimited devices and i cannot cap it", "how do i limit how many devices one account can be signed in on", "i opened the log to check sign ins and only found exports and prints", "where do i see who logged in and from which ip address?", "the audit log i checked has no login rows at all"]
product: frappe
---

# Portal identity

## paths

frappe/core/doctype/user/user.py — User.has_desk_access, User.set_system_user, User.set_roles_and_modules_based_on_user_type, generate_keys
frappe/core/doctype/user_type/user_type.py — apply_permissions_for_non_standard_user_type, user_linked_with_permission_on_doctype
frappe/hooks.py — doc_events, "*", on_update
frappe/sessions.py — get_sessions_to_clear, clear_sessions, delete_session
frappe/core/doctype/activity_log/activity_log.json — operation, status, user, ip_address, reference_doctype, reference_name
frappe/core/doctype/access_log/access_log.json — export_from, file_type, report_name, page

## rules

MUST expect User.set_system_user to assign user_type = "Website User" whenever has_desk_access is false, giving an identity with no seat that still authenticates and still calls a whitelisted method.
MUST read apply_permissions_for_non_standard_user_type as a global on_update hook on every DocType, not as code inside User Type's own controller, because hooks.py wires it under doc_events["*"]["on_update"].
MUST expect that hook to create the matching User Permission only when the edited record's own link field names a user, so "this holder may see only his own record" becomes declared metadata db_query enforces on every read, instead of a scope parameter each endpoint must remember.
MUST bound devices with User.simultaneous_sessions; get_sessions_to_clear reads it at login and clear_sessions deletes every session past that count through delete_session.
NEVER assign api_key/api_secret as a per-device portal credential; generate_keys overwrites api_secret on the single User row, so rotating one device logs out every device that user owns.
MUST read generate_keys as restricted to System Manager by frappe.only_for, and read the secret it returns as carrying no expiry.
MUST read Activity Log, not Access Log, as the login audit; Access Log's fields are export_from, file_type, report_name and page and record exports, prints and report views, never a login.

## how

Website User, User Type, simultaneous_sessions and Activity Log already cover most of a portal identity before any custom credential DocType is worth writing, and the one that looks closest — api_key/api_secret — is the one that does not fit, because it is scoped to the user and not the device.

set_system_user decides Website User purely from desk access, so the identity carries no seat and still reaches every @frappe.whitelist method a session may call. Reading "who may see only their own record" out of User Type means following the on_update hook to user_type.py rather than the DocType's own validate or on_update — the creation happens generically, from whichever record carries the link field back to the user, not from a special path User Type itself defines.

simultaneous_sessions and clear_sessions give device-count enforcement and per-device revocation without a bespoke session table: the login path evicts the oldest sessions past the configured count, and delete_session removes one row on demand.

Two names run the same direction: each looks like the answer and is not. api_key/api_secret reads like per-device auth and is one shared secret per user, restricted to System Manager, with no expiry. Access Log reads like the login audit and is instead the export/print/report record; Activity Log is the one that answers a login-audit question.
