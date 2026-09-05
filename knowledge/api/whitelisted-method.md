---
name: whitelisted-method
description: /api/method checks membership in the whitelist and the request verb and nothing else, and an _api Server Script returns above even those two checks.
triggers: ["handle", "execute_cmd", "run_server_script", "is_valid_http_method", "upload_file", "handle_rpc_call", "run_doc_method", "whitelist", "is_whitelisted", "override_whitelisted_method", "allowed_http_methods_for_whitelisted_func", "only_for", "get_server_script_map", "get", "getpage", "is_permitted", "Server Script", "Page", "Not permitted", "expose a python method to the api", "whitelist decorator", "anyone who is logged in can call our custom endpoint", "why can a normal user run a function that only managers should run", "how do i limit who is allowed to call a custom endpoint", "the endpoint returns data the user has no permission to see", "our custom function skips the record permission checks", "the code that answers the url is not the code i am looking at", "i edited the function but the api still returns the old behaviour", "a method marked for post only is being reached with a get", "why does the request type restriction not apply from a background job", "an anonymous visitor can open a page that should require login", "someone not signed in can pull our page definition", "how do i expose a python function safely to outside callers"]
product: frappe
---

# Whitelisted method

## paths

frappe/handler.py — handle, execute_cmd, run_server_script, is_valid_http_method, upload_file
frappe/api/v1.py — handle_rpc_call
frappe/api/v2.py — handle_rpc_call, run_doc_method
frappe/__init__.py — whitelist, is_whitelisted, override_whitelisted_method, allowed_http_methods_for_whitelisted_func, only_for
frappe/core/doctype/server_script/server_script_utils.py — get_server_script_map
frappe/desk/desk_page.py — get, getpage
frappe/core/doctype/page/page.py — is_permitted

## rules

MUST write the DocType permission check inside the whitelisted function; `is_whitelisted` decides whether the function may be called and never whether the calling user may touch this record.
MUST call `frappe.has_permission(doctype, ptype, doc=...)` in the body of every `_api` Server Script — `execute_cmd` and the v2 dispatcher both resolve the Server Script and `return` above `is_whitelisted` and `is_valid_http_method`, so neither check runs for it.
MUST read an `_api` Server Script as reachable by any authenticated session whatever roles its DocType declares.
MUST read `override_whitelisted_methods` in every installed app's `hooks.py` before trusting that a dotted path runs the function you opened; `frappe.override_whitelisted_method` rewrites the name first on both versions.
NEVER read `@frappe.whitelist(methods=["POST"])` as a check that always holds; `is_valid_http_method` returns without comparing when `frappe.flags.in_safe_exec` is set or when `frappe.local.job` exists, so a Server Script and a background job reach the function whatever verb it declared.
MUST declare `allow_guest=True` on an endpoint a signed-out caller must reach, and MUST then write every check the function needs itself.
MUST call `frappe.only_for(roles)` inside the function body to restrict who may call a whitelisted method by role; it is not a parameter of `frappe.whitelist`, and it passes any Administrator session and any session where `frappe.flags.in_test` is set without checking roles at all.
MUST read `Page.is_permitted` as returning `True` whenever the Page's Has Role child table is empty, so `frappe.desk.desk_page.getpage` — declared `allow_guest=True`, with `is_permitted` as its only check — hands the page definition and its assets to an anonymous caller for any Page that has no role configured.
MUST read `run_doc_method` as the one command `execute_cmd` exempts from both checks; it does its own `is_whitelisted` and `is_valid_http_method` on the bound method after `check_permission`.
MUST expect v1 to truncate the method at the first slash — `handle_rpc_call` splits on `/` and keeps the first segment — so a path with a slash silently calls a shorter name.
MUST reach a controller method by DocType on v2 at `/method/<doctype>/<method>`, which loads the DocType module and prefixes the dotted path before the checks run.

## values

v1 RPC route: `/api/method/<path:method>`
v2 RPC routes: `/method/<method>`, `/method/<doctype>/<method>`
checks on `/api/method`: `is_whitelisted`, `is_valid_http_method`
checks skipped for an `_api` Server Script: both
verb check skipped when: `frappe.flags.in_safe_exec`, or `frappe.local.job` exists
Server Script map key: `_api`
named v2 rules ahead of the generic one: login, logout, ping, upload_file, run_doc_method
only_for exempts: Administrator session, frappe.flags.in_test
Page.is_permitted on empty Has Role: True

## how

The whitelist is a registry of callable names, not a permission table. `@frappe.whitelist` records the function and the verbs it accepts; the dispatcher proves the name is registered and the verb is allowed, then calls it with the whole form dict. Nothing between the request and the function knows which DocType the function will open, so a whitelisted function that reads or writes a record is the only place that check can live.

Read the order of `execute_cmd` as the shape of the risk. The name is rewritten by every app's overrides, then a Server Script matching that name answers and returns, and only after those two does the function get looked up and checked. So the function you read in the app is not necessarily the code that answers, and a Server Script named after an endpoint runs with no check at all.

Two conditions turn the verb check off entirely — safe-exec and a background job. That means the verb is a check on browser traffic and nothing more. Where the verb is the only thing standing between a read and a write, the function needs its own test.

The test a function writes for itself is only as strict as its default. `getpage` writes one — `page.is_permitted()` — and that check itself returns `True` the moment nobody bothered to add a role to the Page, so `allow_guest=True` plus a self-written check still hands out every unrestricted Page to a caller who never logged in.
