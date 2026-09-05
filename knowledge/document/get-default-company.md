---
name: get-default-company
description: erpnext.get_default_company resolves get_user_default_as_list("company", user) then falls back to the Global Defaults single field default_company, and a custom resolver that skips either step reads a different value on a site where only one was set.
triggers: ["get_default_company", "get_user_default_as_list", "get_user_default", "is_a_user_permission_key", "get_global_default", "default company lookup", "erpnext default company resolution", "how do i get the company that should be filled in by default", "which company does the system pick when the field is left empty", "my own code picks a different company than the rest of the system does", "the default company is right for one user and wrong for another", "i set the default company in settings but my script still gets nothing back", "why does one report show a different default company than the form", "how do i find the default company for the user who is logged in", "the company field fills itself in for some users only", "does it matter if i write the key with a capital letter or not", "what order does it check when it decides which company to use"]
product: erpnext
---

# get_default_company

## paths

erpnext/__init__.py — get_default_company
frappe/defaults.py — get_user_default_as_list, get_user_default, is_a_user_permission_key, get_global_default

## rules

MUST import erpnext.get_default_company rather than re-deriving the chain, because it already resolves frappe.defaults.get_user_default_as_list("company", user) and falls back to the Global Defaults single field default_company.
NEVER treat a lookup key's case as broken input; is_a_user_permission_key marks "Company" as a user-permission key (it differs from its own scrub) and re-reads the scrubbed "company" when the first lookup is empty, so both forms resolve.
NEVER read frappe.defaults.get_global_default("company") as the same read as the Global Defaults default_company field; get_global_default reads the DefaultValue table under the __default parent, while erpnext.get_default_company reads the Global Defaults single field directly — two stores normally kept in step but not guaranteed to agree.
MUST end a custom per-module company resolver by delegating to erpnext.get_default_company for its tail, since ERPNext declares no module concept and any legitimate remainder is a module-scoped read consulted before the user default.

## values

resolution order: get_user_default_as_list("company", user) first item, else Global Defaults single field default_company
user-permission key test: is_a_user_permission_key(key) — true when key contains no ":" and key differs from frappe.scrub(key)
global stores read: DefaultValue table under parent __default (get_global_default), Global Defaults single doctype field default_company (get_default_company) — two separate reads

## how

The function is short enough that re-deriving it is never cheaper than importing it, but the two details that make a hand-rolled version wrong are both easy to miss. The case of the lookup key is not one of them: get_user_default_as_list treats a key that differs from its own scrubbed form as a user-permission key and re-reads the scrubbed form when the first lookup misses, so a chain built on "Company" and one built on "company" both resolve.

The real divergence is the global fallback. erpnext.get_default_company reads the Global Defaults single field default_company directly. frappe.defaults.get_global_default("company") reads the DefaultValue table instead. The two are normally kept in step by the same UI, but they are two stores, and a custom chain that mixes one chain's user step with the other's global step can disagree with ERPNext on a site where only one was set directly.

A legitimate reason to write a custom chain still exists — a per-module settings field consulted before the user default, since ERPNext itself has no module concept. That remainder should end by delegating to erpnext.get_default_company for its tail rather than re-implementing the two fallback reads.
