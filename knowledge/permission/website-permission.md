---
name: website-permission
description: frappe.has_website_permission returns the controller's own has_website_permission when the doc defines one and never reads the hooks in that case, and it returns False when neither exists.
triggers: ["has_website_permission", "frappe.has_website_permission", "ignore_permissions", "get_hooks", "doc.has_website_permission", "User.has_website_permission", "Address", "has_common_link", "search_in_doctypes_with_web_view", "validate_print_permission", "check_webform_perm", "allow_guest_to_view", "website permission hook not called", "portal record 403", "who can open my portal document", "my portal permission function is never called", "the check i registered for this record type gets skipped completely", "why is my custom portal rule ignored on this document?", "a signed in customer gets permission denied opening his own record on the site", "the portal says access denied for a record that belongs to the visitor", "how do i let a customer open only his own document on the website?", "the rule works on the web page but the api returns everything anyway", "my website check does not protect the rest api", "the print view refuses to open the document for a portal user", "the web form says no permission for the record the user owns", "adding a second check made it stricter instead of allowing more"]
product: frappe
---

# Website permission

## paths

frappe/__init__.py — has_website_permission, get_hooks, call
frappe/hooks.py — has_website_permission
frappe/core/doctype/user/user.py — has_website_permission
frappe/contacts/doctype/address/address.py — has_website_permission, has_common_link
frappe/website/page_renderers/document_page.py — search_in_doctypes_with_web_view
frappe/website/doctype/web_form/web_form.py — check_webform_perm
frappe/www/printview.py — validate_print_permission

## rules

MUST expect a controller method named `has_website_permission` to END the check; frappe.has_website_permission returns its value directly and the hooks registered for that DocType are never read.
MUST register the check as a hook when other apps must be able to add their own condition, and as a controller method when the DocType must own the answer alone.
MUST expect EVERY hook registered for a DocType to have to return truthy: the loop returns False on the first falsy result and returns True only after all of them passed.
MUST read a missing answer as a refusal; with no controller method and no hook for the DocType, the function returns False rather than deferring to the role permissions.
MUST expect `doc.flags.ignore_permissions` to short-circuit to True before either the controller method or the hooks are consulted.
MUST pass `doctype` when calling with a document NAME rather than a document, because the function loads the document with get_doc(doctype, doc) and reads the doctype off the loaded document only after that.
NEVER call it with neither a doc nor a doctype expecting the hooks to run; the hook lookup is keyed on the doctype, and an unset key yields an empty list and a False.
MUST write the hook target with the keyword parameters `doc`, `ptype`, `user` and `verbose`, because the call passes all four by name.
MUST expect the answer to be consulted on three paths only — the web view renderer, the Web Form's per-record check, and the print view — and NEVER on `/api/method` or `/api/resource`.
MUST expect the web view renderer to try `allow_guest_to_view` and the ordinary document permission FIRST, so a website permission function is reached only for a record that is neither public nor already readable.

## values

order: ignore_permissions, then the controller's has_website_permission, then the hooks for that doctype
controller method wins: the hooks are skipped entirely
hook combination: AND, first falsy denies, empty list denies
default with nothing registered: False
hook shape: {"<DocType>": "<dotted path>"}, called with doc, ptype, user, verbose
registrations in frappe: Address through the hook, User through a controller method
User's answer: the document's name equals the session user
Address's answer: a Contact carrying the session user's email shares a link with the address
callers: document_page, web_form, printview

## how

Two registration points answer the same question and they are not additive. A controller method on the document takes the whole decision: the moment it exists, the hook entry for that DocType is dead code. That is the shape to reach for when a DocType owns its own portal rule, and the shape to avoid when a second app is expected to tighten the rule later, since the app cannot get in front of the method.

Hooks compose the other way. Every registered function has to agree, so adding one can only narrow the answer and never widen it — and because an empty list is False, the function's own default is refusal. Nothing here grants; has_website_permission is a way of saying yes to a record the ordinary permission already said no to, on the three rendering paths that ask.

The two implementations frappe registers show the intended shape: an answer derived from the session's identity, not from a role. User compares the record's name to the session user. Address walks from the session's email to a Contact and asks whether that Contact links to the address. Both are per-record and neither needs a Role Permission row, which is what makes has_website_permission useful for a portal where every visitor holds the same role.
