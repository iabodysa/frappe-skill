---
name: read
description: frappe.qb.get_query skips every permission check by default, the same as before, but it now takes ignore_permissions and a caller that passes ignore_permissions=False gets the same role, share, user-permission and permlevel checks get_list runs.
triggers: ["Engine.get_query", "apply_filters", "apply_list_filters", "apply_dict_filters", "parse_fields", "SQLFunctionParser", "is_function_dict", "parse_function", "check_select_permission", "add_permission_conditions", "apply_field_permissions", "ChildQuery", "DynamicTableField", "exists", "get_value", "get_values", "get_all", "get_list", "count", "DatabaseQuery", "or_filters", "get_cached_doc", "can_cache_doc", "get_doc", "`as_iterator` only works with `as_list=True` or `as_dict=True`", "Use of sub-query or function is restricted", "Illegal SQL Query", "frappe.qb permission check", "query builder bypasses permissions", "users can see records they are not supposed to see", "my query ignores the access rules i set up", "why does one way of reading data respect roles and another way does not", "restricted people are getting everyone's rows in the list", "the query comes back with nothing but there is definitely matching data", "no error and no rows either i cannot tell what went wrong", "how do i write an either-or condition when reading rows", "my either or condition quietly returns zero results", "i get an attribute error deep inside the reading code with no useful message", "adding a sum or a count to my read blows up before it even runs", "the existence check says yes for a record that is not actually there", "SQL functions are not allowed as strings in SELECT", "my aggregate string now throws asking for dict syntax", "does passing ignore_permissions to get_query actually turn on a check"]
product: frappe
---

# Reading rows

## paths

frappe/database/query.py — Engine.get_query, Engine.check_select_permission, Engine.add_permission_conditions, Engine.apply_field_permissions, apply_filters, apply_list_filters, apply_dict_filters, parse_fields, SQLFunctionParser, ChildQuery, DynamicTableField
frappe/database/database.py — exists, get_value, get_values, get_all, get_list, count
frappe/model/db_query.py — DatabaseQuery, or_filters
frappe/__init__.py — get_list, get_all, get_cached_doc, can_cache_doc, get_doc

## rules

MUST read `frappe.qb.get_query` as checking no permission by default; `ignore_permissions` defaults to `True`, so a bare call still returns every row and every field with no role, share, user-permission or permlevel check.
MUST pass `ignore_permissions=False` to turn that check on; `Engine.get_query` now accepts it as one of its keyword-only names, and doing so runs `check_select_permission`, `add_permission_conditions` and `apply_field_permissions` — the same role, share, user-permission and permlevel checks `get_list` runs.
MUST use `get_list`, or `get_query` called with `ignore_permissions=False`, where a permission, a User Permission or a `permission_query_conditions` hook has to apply; a bare `get_query` or `get_all` still skips every one of them.
MUST write an aggregate in `get_query(fields=...)` as a dict whose one key besides `as` is an upper-case name in `FUNCTION_MAPPING` — `COUNT`, `SUM`, `AVG`, `MAX`, `MIN`, `ABS`, `EXTRACT`, `LOCATE`, `TIMESTAMP`, `IFNULL`, `CONCAT`, `NOW`, `NULLIF`, `MONTHNAME`, `QUARTER`, `MONTH`, `YEAR` — because `SQLFunctionParser.is_function_dict` reads exactly that shape before `_parse_single_field_item` ever tries the child-table path.
NEVER write an aggregate as a string carrying a parenthesis in `get_query(fields=...)`; `_validate_select_field` matches it with `FUNCTION_CALL_PATTERN` and throws `frappe.ValidationError`, naming the dict syntax to use instead.
MUST expect a dict naming a field that exists but is not a table field to fail later and elsewhere, because `ChildQuery.__init__` returns without setting its attributes and the half-built object is appended anyway.
NEVER put the string `"or"` in a `get_query` filter list; a string entry is rewritten as a filter on `name`, so the query compiles with an extra equality and returns nothing, raising nothing.
MUST express OR in `get_query` as a PyPika `Criterion`, which `apply_filters` passes to the where clause intact.
MUST expect `or_filters` to work the same way moving a call between `frappe.db.get_all` and `get_query`; `Engine.get_query` now takes `or_filters` directly, the same keyword `DatabaseQuery` takes.
MUST expect `frappe.db.exists` to return its second argument without querying whenever the doctype is not DocType and the two arguments are equal.
MUST read with `get_doc` rather than `get_cached_doc` where the value decides a write.

## values

no permission check by default: frappe.qb.get_query (ignore_permissions=True default), frappe.db.get_all, frappe.db.get_value, frappe.db.sql
permission checked: frappe.get_list and frappe.db.get_list, through DatabaseQuery with ignore_permissions false; frappe.qb.get_query too, once called with ignore_permissions=False
frappe.get_all: the same DatabaseQuery with ignore_permissions set to true
get_query keyword-only parameters: validate_filters, skip_locked, wait, ignore_permissions, ignore_user_permissions, user, parent_doctype, reference_doctype, or_filters, db_query_compat
a str or int filter: rewritten as a filter on name
a list of only strings or ints: rewritten as name in that list
a dict in fields whose one non-"as" key is upper-case and in FUNCTION_MAPPING (COUNT, SUM, AVG, MAX, MIN, ABS, EXTRACT, LOCATE, TIMESTAMP, IFNULL, CONCAT, NOW, NULLIF, MONTHNAME, QUARTER, MONTH, YEAR): an aggregate function call
a dict in fields whose one non-"as" key is upper-case and in OPERATOR_MAPPING (ADD, SUB, MUL, DIV): an arithmetic expression over exactly two arguments
any other dict in fields: one child-table query per key, filtered on parenttype, parentfield and parent, ordered by idx
a string in fields carrying a parenthesis: rejected by _validate_select_field with frappe.ValidationError; use the dict form instead
a Criterion in filters or fields: passed through unchanged
exists shortcut: dt is not DocType and dt equals dn, returns dn
row lock: for_update on get_value, get_values and get_singles_dict

## how

The three reads are not three styles of the same thing; they sit at different levels of checking, and the difference is a default rather than a wall. `get_list` runs the permission check. `get_all` always skips it. `get_query` skips it too unless the caller passes `ignore_permissions=False`, in which case it runs the same `check_select_permission`, `add_permission_conditions` and `apply_field_permissions` machinery `get_list` runs. `get_query` still buys joins, child-table sub-queries, aggregation, row locking and unbuffered iteration the checked path cannot express, and a call site that reads data for a person still has to choose the flag on purpose — the default leaves every permission, User Permission and query-condition hook behind.

Inside `get_query` the argument types are the grammar, and a parenthesis moved sides in this version. A dict in `fields` means an aggregate or an arithmetic expression when its one non-`as` key is an upper-case name `FUNCTION_MAPPING` or `OPERATOR_MAPPING` knows, and a child table otherwise; a string with a parenthesis is now rejected outright, with the error naming the dict form to use. A string in `filters` means a name, a `Criterion` means raw boolean logic. Nothing validates that a child-table dict meant what its shape says, so the failure to expect there is still an AttributeError from deep inside the parser rather than a message naming the argument.

`exists` has the same shape of surprise at the other end: it answers from the arguments rather than the database when the doctype and the name are equal, which is correct for a Single and wrong for anything else that happens to be named after its DocType.
