---
name: read
description: frappe.qb.get_query runs no permission check and has no parameter to ask for one, because the class that would check reads the tables back out of the compiled SQL and nothing in the tree calls it.
triggers: ["Engine.get_query", "apply_filters", "apply_list_filters", "apply_dict_filters", "parse_fields", "get_function_object", "ChildQuery", "DynamicTableField", "Permission.check_permissions", "exists", "get_value", "get_values", "get_all", "get_list", "count", "DatabaseQuery", "or_filters", "get_cached_doc", "can_cache_doc", "get_doc", "`as_iterator` only works with `as_list=True` or `as_dict=True`", "Use of sub-query or function is restricted", "Illegal SQL Query", "frappe.qb permission check", "query builder bypasses permissions", "users can see records they are not supposed to see", "my query ignores the access rules i set up", "why does one way of reading data respect roles and another way does not", "restricted people are getting everyone's rows in the list", "the query comes back with nothing but there is definitely matching data", "no error and no rows either i cannot tell what went wrong", "how do i write an either-or condition when reading rows", "my either or condition quietly returns zero results", "i get an attribute error deep inside the reading code with no useful message", "adding a sum or a count to my read blows up before it even runs", "the existence check says yes for a record that is not actually there"]
product: frappe
---

# Reading rows

## paths

frappe/database/query.py — Engine.get_query, apply_filters, apply_list_filters, apply_dict_filters, parse_fields, get_function_object, ChildQuery, DynamicTableField, Permission.check_permissions
frappe/database/database.py — exists, get_value, get_values, get_all, get_list, count
frappe/model/db_query.py — DatabaseQuery, or_filters
frappe/__init__.py — get_list, get_all, get_cached_doc, can_cache_doc, get_doc

## rules

MUST read `frappe.qb.get_query` as checking no permission at all; `Permission.check_permissions` is defined and called by nothing, and `Engine.get_query` accepts no `ignore_permissions`, keyword-only or otherwise.
NEVER pass `ignore_permissions` to `get_query`; it raises `TypeError`, because the only keyword-only names are `validate_filters`, `skip_locked` and `wait`.
MUST use `get_list` where a permission, a User Permission or a `permission_query_conditions` hook has to apply, and NEVER use `get_query` or `get_all` there, because neither reaches the permission check.
MUST write an aggregate in `get_query(fields=...)` as a string carrying a parenthesis, because `get_function_object` splits on the parenthesis and on the word as.
NEVER write an aggregate as a dict in `get_query(fields=...)`; a dict entry means a child table request, so each key is read as a child-table fieldname and `get_meta().get_field()` returning None raises an AttributeError before any SQL exists.
MUST expect a dict naming a field that exists but is not a table field to fail later and elsewhere, because `ChildQuery.__init__` returns without setting its attributes and the half-built object is appended anyway.
NEVER put the string `"or"` in a `get_query` filter list; a string entry is rewritten as a filter on `name`, so the query compiles with an extra equality and returns nothing, raising nothing.
MUST express OR in `get_query` as a PyPika `Criterion`, which `apply_filters` passes to the where clause intact.
MUST rewrite a call moved between `frappe.db.get_all` and `get_query` by hand, because `or_filters` is a separate argument on `DatabaseQuery` and `Engine.get_query` does not accept it.
MUST expect `frappe.db.exists` to return its second argument without querying whenever the doctype is not DocType and the two arguments are equal.
MUST read with `get_doc` rather than `get_cached_doc` where the value decides a write.

## values

no permission check: frappe.qb.get_query, frappe.db.get_all, frappe.db.get_value, frappe.db.sql
permission checked: frappe.get_list and frappe.db.get_list, through DatabaseQuery with ignore_permissions false
frappe.get_all: the same DatabaseQuery with ignore_permissions set to true
get_query keyword-only parameters: validate_filters, skip_locked, wait
a str or int filter: rewritten as a filter on name
a list of only strings or ints: rewritten as name in that list
a dict in fields: one child-table query per key, filtered on parenttype, parentfield and parent, ordered by idx
a string in fields carrying a parenthesis: an aggregate
a Criterion in filters or fields: passed through unchanged
exists shortcut: dt is not DocType and dt equals dn, returns dn
row lock: for_update on get_value, get_values and get_singles_dict

## how

The three reads are not three styles of the same thing; they sit at different levels of checking, and the differences are silent. `get_list` runs the permission check. `get_all` and `get_query` do not. `get_query` buys joins, child-table sub-queries, aggregation, row locking and unbuffered iteration that the checked path cannot express, and it pays for them by leaving every permission, User Permission and query-condition hook behind. So the question at a call site reading data for a person is which of the three, and the answer is never decided by convenience.

Inside `get_query` the argument types are the grammar. A dict in `fields` means a child table, a string with a parenthesis means an aggregate, a string in `filters` means a name, a `Criterion` means raw boolean logic. Nothing validates that you meant what the type says, so the two failures to expect are an AttributeError from deep inside the parser and an empty result set from a query that compiled fine. Neither error names the argument that caused it, which is why the symptom to search for here is emptiness rather than an exception.

`exists` has the same shape of surprise at the other end: it answers from the arguments rather than the database when the doctype and the name are equal, which is correct for a Single and wrong for anything else that happens to be named after its DocType.
