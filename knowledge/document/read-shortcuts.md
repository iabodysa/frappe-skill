---
name: read-shortcuts
description: get_value returns a bare value for one field and a row for two or more, orders by nothing at all unless order_by is passed, and count answers from a day-old cache only while it has no filters.
triggers: ["get_value", "get_values", "get_values_from_single", "get_single_value", "get_singles_value", "count", "get_last_doc", "get_cached_value", "value_cache", "DefaultOrderBy", "apply_order_by", "DoesNotExistError", "frappe.db.get_value with a list of fields", "frappe.db.count stale", "get_last_doc raises", "my code broke the moment i asked for a second column", "why do i get a plain value sometimes and a whole row other times", "asking for one column gives me the value but two columns give me something i cannot unpack", "the lookup hands me a different record every time i run it", "which record comes back when more than one matches the filter", "i keep getting the wrong record back and it changes between runs", "i cannot tell if the record is missing or the column is just empty", "the total on my page is a day behind and never refreshes", "records i deleted are still being counted in the total", "why is my count still wrong after i added rows", "asking for the newest record throws an error instead of coming back empty", "how do i get the most recently changed record instead of the most recently created one"]
product: frappe
---

# The single-row read shortcuts

## paths

frappe/database/database.py — get_value, get_values, get_values_from_single, get_single_value, get_singles_value, count, value_cache, cast_fieldtype
frappe/database/utils.py — DefaultOrderBy
frappe/database/query.py — apply_order_by
frappe/__init__.py — get_value, get_single_value, get_last_doc, get_cached_value, get_all, DoesNotExistError

## rules

MUST expect `get_value` to return the bare value when one field was asked for and a row when two or more were, and MUST expect a list carrying a single field name to return the bare value as well, because the branch tests how many columns came back rather than what was passed.
MUST unpack a multi-field read into as many names as fields, in the order the fields were given.
MUST pass `as_dict=True` where the field list is built at run time, since that is the only form whose shape does not change with the number of fields.
MUST expect `None` when no row matches, and NEVER read that `None` as a null column, because a matched row with a null column returns `None` too.
MUST pass `order_by` whenever the filters can match more than one row: the default is a sentinel that means keep the default ordering, and the query builder adds no `ORDER BY` clause for it, so the row returned is whichever the engine hands back first.
MUST pass `filters=None` for a Single DocType, which routes the read to the Singles table instead of a document table.
MUST expect `cache=True` on `get_value` to last for the current request or job only.
MUST expect `count` to cache only when it was given no filters, under a key naming the doctype, for one day, and MUST expect `cache=True` with filters to do nothing at all — neither read nor write.
NEVER show a cached `count` as a live total; it can be a day behind and nothing invalidates it on insert or delete.
MUST expect `count` to validate its filters and to count distinct rows unless `distinct=False` is passed.
MUST expect `frappe.db.get_single_value` to read the Singles table, to cast the stored string by the field's own fieldtype, and to hold the result for the request in the connection's value cache, which `cache=False` skips reading but not writing.
MUST expect it to raise rather than return `None` when the fieldname is not a field on that Single, since it reads the field from the meta before casting.
NEVER read `frappe.get_single_value` as an alias of the database method: the module-level function goes through the cached document, so it answers from the Single's cached document rather than from the Singles table.
MUST expect `get_last_doc` to run two queries — a name-only list read of one row, then a full document load — and MUST NEVER use it where the fields alone are wanted.
MUST expect `get_last_doc` to raise `DoesNotExistError` when nothing matches; it never returns `None`, so the caller needs the try or a prior existence check.
MUST expect `get_last_doc` to ignore permissions, because the list read behind it is the ignoring one.
MUST pass `order_by` to `get_last_doc` when last means most recently changed, because its default orders by creation.

## values

one field: the value; two or more: the row; `as_dict=True`: a dict
a one-name field list: still the bare value
no match: `None` from `get_value`, `DoesNotExistError` from `get_last_doc`
default order_by: the keep-default sentinel, which adds no `ORDER BY`
count cache: only with no filters, keyed on the doctype, one day, no invalidation
count distinct: on by default
get_single_value cache: the connection's value cache, per request
get_last_doc default order: `creation desc`
get_last_doc queries: a `name` pluck limited to one row, then a document load

## how

These four are shortcuts over the same query builder, and each one drops something to stay short. `get_value` drops the shape: its return type follows the number of columns, so code that starts with one field and grows to two breaks at the assignment rather than at the read. It also drops the ordering, which is invisible until a second row matches the filters and the answer starts changing between runs.

`count` and `get_single_value` drop freshness in exchange for a cache, at different scopes — one day across the site for the unfiltered count, one request for the single value. `get_last_doc` drops nothing but pays two queries and raises instead of answering empty, so it belongs where the caller already knows a document exists.
