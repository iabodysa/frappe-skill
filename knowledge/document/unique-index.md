---
name: unique-index
description: DbColumn.get_definition writes not null default only for Check, Int, Currency, Float and Percent, so every other fieldtype in a composite unique index is nullable and two rows that both leave that member empty do not collide because two NULLs are never equal.
triggers: ["DbColumn.get_definition", "default_fields", "unique constraint on multiple fields", "composite unique index", "duplicate rows still get saved when one of the fields is left blank", "i set two fields to be unique together and duplicates keep appearing", "why does it let me save the same record twice when one field is empty", "the duplicate check only works when every field is filled in", "the database shows the uniqueness rule but it never blocks anything", "my test proves the constraint exists yet duplicates still go through", "the no duplicate rule looks correct and does nothing in real data", "how do i stop duplicates only among drafts and still allow cancelled ones", "i want the duplicate check to ignore cancelled and submitted records", "there is no tick box to make the rule depend on whether the record is cancelled"]
product: frappe
---

# Composite unique index

## paths

frappe/database/schema.py — DbColumn.get_definition
frappe/model/__init__.py — default_fields

## rules

MUST expect a Data, Link, Select, Date or Datetime column to be created NULLABLE with no default, because `get_definition` gives `not null default` only to Check, Int, Currency, Float and Percent.
MUST expect two rows that agree on every other member of a composite unique index but leave a nullable member empty to NOT collide, because the index admits multiple NULLs there.
NEVER accept `information_schema` reporting the index, or a test that only asserts the index's column list, as proof the index refuses a duplicate; it refuses one only between rows that both carry a value on every member.
MUST make every member of a composite unique index NOT NULL — `reqd` where a value is always written, or a Check field, which is already `not null default 0` — or MUST keep the optional column out of the index and express the distinction some other way.
NEVER expect a composite unique constraint that must key on `docstatus` to be declarable through DocField properties; `get_definition` writes `unique` and `search_index` onto one column each, and `docstatus` is not a DocField — it is a member of `default_fields` in `frappe/model/__init__.py`, with no `unique` or `search_index` checkbox to set.

## how

The gap is not in the index; it is upstream of it, in which fieldtypes the schema builder ever gives a NOT NULL default. A duplicate the index was built to refuse walks in whenever both colliding rows leave the same optional member unset, and the index itself looks intact throughout — present, correctly defined, passing any check that only inspects its column list.

A constraint that must include `docstatus` — refusing a duplicate only among draft rows, say, while a cancelled or submitted row is exempt — cannot be reached by checking `unique` or `search_index` boxes at all, composite or not: those properties apply one DocField column at a time, and `docstatus` carries no DocField to check them on. That constraint has to be written as a custom index outside the DocField json.
