---
name: rest-routes
description: v1 answers at both /api and /api/v1 while v2 names the path segment document instead of resource, so /api/v2/resource matches no url rule and raises DoesNotExistError.
triggers: ["API_URL_MAP", "ApiVersion", "get_api_version", "handle", "url_rules", "document_list", "create_doc", "read_doc", "update_doc", "delete_doc", "execute_doc_method", "handle_rpc_call", "get_request_form_data", "copy_doc", "run_doc_method", "get_meta", "count", "PERMISSION_MAP", "get_list", "Not permitted", "Cannot edit standard fields", "frappe rest api endpoints", "api v1 vs api v2", "the api says the document does not exist but i can see it in the list", "why do i get a not found for a record that is definitely there", "the new api version returns nothing for a url that worked before", "our integration only ever gets twenty rows back", "the list endpoint stops at twenty records no matter what i ask for", "how do i get more than the first page from the api", "deleting a child row over the api leaves the parent wrong", "removing a table line through the api does not update the parent total", "the api rejects my update because i used the wrong request type", "updating a record over the api fails but creating one works", "how do i copy a record or get its field list over the api", "the api lets someone read a record they should not see"]
product: frappe
---

# REST routes

## paths

frappe/api/__init__.py — API_URL_MAP, ApiVersion, get_api_version, handle
frappe/api/v1.py — url_rules, document_list, create_doc, read_doc, update_doc, delete_doc, execute_doc_method, handle_rpc_call, get_request_form_data
frappe/api/v2.py — url_rules, document_list, create_doc, read_doc, copy_doc, update_doc, delete_doc, execute_doc_method, run_doc_method, get_meta, count, PERMISSION_MAP
frappe/client.py — get_list, delete_doc

## rules

MUST read an unversioned `/api/resource/...` call as v1; `get_api_version` returns V2 only for a path that starts `/api/v2`, and `API_URL_MAP` mounts the same v1 rules under `/api` and `/api/v1`.
NEVER call `/api/v2/resource/<doctype>`; v2 names that path segment `document`, and a segment `API_URL_MAP` does not carry converts a werkzeug 404 into `frappe.DoesNotExistError`.
MUST use v2 for the four things v1 has no rule for — `copy_doc` at `/document/<dt>/<name>/copy`, `get_meta` at `/doctype/<dt>/meta`, `count` at `/doctype/<dt>/count`, and `run_doc_method` at `/method/run_doc_method`.
MUST send `PUT` on v1, and `PATCH` or `PUT` on v2, to update a document.
MUST delete a child row through v2; its `delete_doc` routes to `frappe.client.delete_doc`, which removes the row through the parent's `save`, while v1 calls `frappe.delete_doc` and runs no parent update.
NEVER depend on a trailing slash on either version; `API_URL_MAP` is built with `strict_slashes=False` and `merge_slashes=False`.
MUST set `limit_page_length` on a list call yourself; both versions default it to 20 and a caller raises it with one query parameter.
MUST read `read_doc` as the place the read permission is checked — v1 calls `doc.has_permission("read")` and raises `frappe.PermissionError`, v2 calls `doc.check_permission("read")` — and both then call `apply_fieldlevel_read_permissions`.
MUST read `create_doc`, `update_doc` and `delete_doc` as enforcing nothing of their own; `insert`, `save` and `frappe.delete_doc` are where the permission is decided.
MUST read the request verb as choosing the permission on a v2 document method; `PERMISSION_MAP` maps GET to `read` and POST to `write`, and `execute_doc_method` calls `doc.check_permission` with it.
MUST call `doc.is_whitelisted(method)` before a document method on either version — both `execute_doc_method` bodies do it first, so an unwhitelisted controller method is unreachable through the route.
MUST expect v2's `update_doc` to strip fields the caller's permlevel cannot read on the way out; v1's does not.
MUST read a v1 `POST` to `/resource/<dt>/<name>/` as a document-method call, not a create; that rule binds `execute_doc_method`.

## values

v1 mounts: `/api`, `/api/v1`
v2 mount: `/api/v2`
v1 path segments: `/method`, `/resource`
v2 path segments: `/method`, `/document`, `/doctype`
update verb: v1 `PUT`; v2 `PATCH` or `PUT`
delete response: HTTP 202 with body `ok`, both versions
list page length default: 20
meta route permission: `frappe.only_for("All")`
v2 create keeps a supplied name: `flags.name_set`
v1 read extra: `expand_links`, `run_method`

## how

Two versions run side by side and share one Werkzeug map, so the version is decided by the path prefix and nothing else. A call with no version segment is v1 — that is the compatibility mount, not a default that will follow the newest code.

The difference that breaks a client is one path segment. v1 says `resource`, v2 says `document`, and the wrong segment does not 404 in a readable way; the router turns the miss into `DoesNotExistError`, which reads like a missing record rather than a missing route. When a v2 call reports that a document does not exist, ask first whether that segment is right.

No route enforces a permission by being a route. Read and copy check for themselves because `frappe.get_doc` does not; create, update and delete enforce nothing at the route and rely entirely on `insert`, `save` and `frappe.delete_doc`; the list route hands the whole request to `frappe.client.get_list` and inherits every layer `DatabaseQuery` carries. So the question about a REST call is never what the route allows, it is which call underneath it is doing the checking.
