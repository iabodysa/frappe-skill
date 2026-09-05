---
name: form-settings
description: The Web Form Check fields act at four different places and only two of them reach the write, while depends_on hides a Check field on the form without clearing its stored value.
triggers: ["accept", "WebForm.get_context", "WebForm.validate_mandatory", "published", "login_required", "anonymous", "allow_edit", "allow_multiple", "allow_delete", "allow_incomplete", "apply_document_permissions", "show_list", "condition_json", "Web Form", "You need to be in developer mode to edit a Standard Web Form", "Following fields are missing:", "Mandatory Information missing:", "web form check field visibility", "depends_on web form field", "people are sending the same form twice and i limited it to one", "why did a second entry get created for the same person", "how do i stop duplicate submissions from one user", "a required field came through empty in the saved record", "the form let them skip a mandatory question", "i ticked the option but nothing changed on the actual save", "the checkbox disappeared from the settings screen but it is still taking effect", "after turning on anonymous every submission is refused", "someone bypassed the form by posting straight to the endpoint", "which of these switches actually blocks a submission and which is just navigation"]
product: frappe
---

# Web Form settings

## paths

frappe/website/doctype/web_form/web_form.py — accept, WebForm.get_context, WebForm.validate_mandatory
frappe/website/doctype/web_form/web_form.json — published, login_required, anonymous, allow_edit, allow_multiple, allow_delete, allow_incomplete, apply_document_permissions, show_list, condition_json

## rules

NEVER read an unchecked `allow_multiple` as a one-record-per-user rule. It is a redirect in get_context and accept never reads it, so a second POST to the accept endpoint inserts a second record.
MUST add a `validate` on the target DocType when one record per user is a real requirement.
MUST expect the `allow_multiple` redirect to be skipped for a Guest, for a form with `login_required` unchecked, and for any request already carrying a name or is_list, and to filter on `condition_json` plus an owner condition.
MUST read `allow_edit` and `login_required` as holding against a direct POST; both throw inside accept.
MUST read the Web Form's own validate_mandatory as dead code; it has no caller in frappe, erpnext or hrms, so with `allow_incomplete` checked nothing on the server enforces a field marked reqd.
MUST expect ignore_mandatory to be set whenever the payload carries a base64 attachment, with no setting involved.
MUST read the stored value of every Check field with frappe.db.get_value rather than the Web Form as the Desk renders it. depends_on hides a field and never clears it, so a value set before its parent changed is still stored and still runs.
MUST unset `login_required` in the same save that sets `anonymous`, since `anonymous` hides `login_required` and the hidden value still refuses every submission.

## values

published: routing only — get_published_web_forms builds the route rules from it
login_required: accept, insert branch — throws for a Guest session
allow_edit: accept, before the branch — throws when the payload carries a name
allow_multiple: get_context only — redirects a returning user to their first record
allow_incomplete: accept, before the write — sets ignore_mandatory on the document
allow_delete: the delete endpoint — with an owner match, permits the delete
anonymous: accept — rewrites the session to Guest for the whole call
apply_document_permissions: has_web_form_permission — replaces the owner match with the document's own permission
show_list: get_context — routes /<route> to /<route>/list instead of /<route>/new
depends_on login_required: allow_edit, allow_multiple, allow_comments, show_list
depends_on allow_multiple and login_required: allow_delete
depends_on not anonymous: login_required

## how

Each Check field acts in exactly one place, and the places are not the same layer. Two throw inside
the write endpoint and hold against a script posting directly. Two only steer the page builder and
are invisible to a POST. So before relying on a setting, ask which of the two it is: a setting that
lives in get_context is a routing convenience and never a rule.

`allow_incomplete` is the sharpest case. It turns the DocType's own mandatory check off and the Web
Form's replacement never runs, so a form that looks stricter than the DocType is in fact looser than
it. Anything that must be present belongs in `validate`.

The Web Form's own form view lies by omission. depends_on controls display and nothing else, so any field
hidden by a parent keeps whatever it held when it was last visible, and that stored value is what
runs. When a form behaves as though a setting is on that the form view does not show, read the row from
the database.
