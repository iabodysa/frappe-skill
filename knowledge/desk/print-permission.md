---
name: print-permission
description: The print permission is consulted only after read passes, so it refuses nobody who can already read the document, and Print Settings is what refuses a print by docstatus.
triggers: ["validate_print_permission", "validate_key", "get_rendered_template", "false_if_not_shared", "Not allowed to print draft documents", "Not allowed to print cancelled documents", "print permission vs read permission", "print settings restrict print", "i unchecked print on every role and people can still print", "removing print rights changed absolutely nothing", "how do i actually stop someone from printing a document they can open", "why is my print restriction ignored while the read restriction works", "someone printed a document without logging in how", "a person opened a printout from a link even though they have no access", "i want to block printing of drafts until they are approved", "how do i prevent printing a cancelled document", "a shared document can be printed by whoever it was shared with is that normal", "the print rule i wrote looks correct but has no effect in practice", "printing works for a user who should not be able to print at all"]
product: frappe
---

# Print permission

## paths

frappe/www/printview.py — validate_print_permission, validate_key, get_rendered_template
frappe/permissions.py — false_if_not_shared

## rules

MUST close a print at the read permission; validate_print_permission returns on the first of read and print that passes, and read is tried first.
NEVER write a role permission on print expecting it to refuse a user who can read the document.
MUST expect a shared document to answer a print check with read, because false_if_not_shared rewrites email and print to read before asking frappe.share.get_shared.
MUST expect a Document Share Key passed as key in the query string to pass the check with no role on the session, and to raise LinkExpired only once expires_on has passed.
MUST expect frappe.has_website_permission to pass the check on its own.
MUST expect frappe.flags.ignore_print_permissions to skip validate_print_permission entirely in get_rendered_template.
MUST use Print Settings allow_print_for_draft and allow_print_for_cancelled to refuse a print, which is the check that refuses by docstatus on a submittable DocType.

## values

tried in order: read, then print
passes without a role: frappe.has_website_permission, a valid Document Share Key
legacy key: doc.get_signature() while System Settings allow_older_web_view_links is on
refusals that hold: allow_print_for_draft, allow_print_for_cancelled
failure call: doc._handle_permission_failure("print")
shareable permissions: read, write, share, submit, email, print — with email and print asked as read

## how

Clearing the print checkbox on every role a user holds reads as the way to stop him printing and
changes no behaviour: the loop passes on read before it ever asks about print, so print is
only consulted for someone who already failed read, which is nobody who reached the page. The rule
you wrote stays in the tree and the next maintainer reads it as if it worked.

Decide what you are actually refusing. If the user should not see the document, take read. If the
document is fine to see but not to print at a given stage, that is docstatus and the switches live
in Print Settings. Anything else — the portal permission, a share key in a link — is a separate route
into the same function and no role narrows it.
