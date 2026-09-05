---
name: hooks
description: The three permission hooks run on different paths and disagree on what a falsy return means — one denies, one shows every row, and one is never reached by an API call.
triggers: ["permission_query_conditions", "has_permission", "has_website_permission", "get_permission_query_conditions", "has_controller_permissions", "get_newargs", "insert", "_validate_links", "get_invalid_links", "set_fetch_from_value", "search_in_doctypes_with_web_view", "has_web_form_permission", "validate_print_permission", "Web Form", "Use of sub-query or function is restricted", "Illegal SQL Query", "has_permission vs permission_query_conditions", "permission hook falsy return", "my filter is supposed to hide all rows but the user sees everything", "returning false from my row filter shows every record instead of none", "how do i block every single row from a list for a certain user", "my custom check never runs when the request comes from the app", "the portal check works on the website page but not on the other calls", "my function blows up with an unexpected keyword argument", "the function never receives the record type it is supposed to scope", "my check can only take access away and never give it", "i wrote a rule to give a role extra access and it does nothing", "the field i read in my check is empty while creating a new record", "my check passes on save but fails on the very first insert", "why is my permission function ignored on some pages and not others"]
product: frappe
---

# Permission hooks

## paths

frappe/hooks.py — permission_query_conditions, has_permission, has_website_permission
frappe/model/db_query.py — get_permission_query_conditions
frappe/permissions.py — has_controller_permissions
frappe/__init__.py — has_website_permission, get_newargs
frappe/model/document.py — insert, _validate_links
frappe/model/base_document.py — get_invalid_links, set_fetch_from_value
frappe/website/page_renderers/document_page.py — search_in_doctypes_with_web_view
frappe/website/doctype/web_form/web_form.py — has_web_form_permission
frappe/www/printview.py — validate_print_permission

## rules

MUST return the SQL string "1=0" from a permission_query_conditions hook to deny every row, because get_permission_query_conditions appends a condition only when it is truthy and a skipped condition leaves the list unrestricted.
NEVER return False, None, "" or 0 from a permission_query_conditions hook meaning to deny; that is the value that shows the caller every row.
MUST declare doctype=None on a permission_query_conditions hook to receive the DocType it is scoping, because frappe.call passes doctype= and get_newargs drops a keyword the signature does not name.
MUST expect a has_permission hook to be able to deny only; has_controller_permissions returns True when every hook returned None, and a controller never grants a permission the DocPerm withheld.
MUST return None from a has_permission hook that has no opinion, because the first non-None return decides the answer.
NEVER read a fetched field inside a has_permission hook on create: insert calls check_permission("create") before _validate_links, and _validate_links is what applies fetch_from through get_invalid_links.
MUST resolve the value a create-time hook needs from a field the caller actually set, following the links by hand from the child link to its parent.
NEVER declare has_website_permission in hooks.py and rely on it for an API call; it is consulted only by the Web View renderer, the Web Form, and the print view, and frappe/permissions.py does not mention it.
MUST put a portal's per-record check inside the whitelisted method or in a has_permission hook, because /api/method reaches frappe.has_permission and stops there.

## values

permission_query_conditions: returns a SQL fragment, joined with " and ", falsy is dropped
has_permission: returns True, False or None, first non-None wins, denies only
has_website_permission: website rendering path only, never the RPC path
"1=0": the deny
frappe/permissions.py mentions of has_website_permission: none

## how

The three hooks share a word and nothing else. Read each one by asking what its return value means and which request reaches it.

permission_query_conditions returns text, not a verdict, so a boolean return is a category error the truth test silently forgives in the wrong direction: the natural-looking deny is the exact value that removes the filter. Write the deny as SQL.

has_permission returns a verdict, and the framework treats None as silence. It sits below the DocPerm, so it can narrow an already-granted permission and can never widen one — a design that expects a hook to hand a role a right it does not hold is designed backwards. Its position in insert also matters more than its body: the document it sees at create time holds only what the caller set.

has_website_permission reads like the portal's answer to has_permission and belongs to a different path entirely. A portal that declares it has declared a check that refuses nothing while reading in review as though the records were scoped.
