---
name: make-records
description: make_records inserts each record inside its own savepoint and on any exception other than a duplicate name it rolls back, logs and moves to the next record with no reordering and no second pass, so a record whose Link target comes later in the same list is lost silently.
triggers: ["make_records", "show_document_insert_error", "_validate_links", "Error: Document has been modified after you have opened it", "insert multiple records in a loop", "bulk insert rollback on error", "some of the starter records were never created and there was no error", "the setup finished green but half the records are missing", "why do my seeded records vanish with nothing shown in the output", "loading a list of records skips the ones that point at each other", "a record fails because the thing it links to does not exist yet", "the loader keeps going after a failure instead of stopping and telling me", "duplicates still blow up even though i told it to ignore duplicates", "the only sign of the failure was a line in the log nobody reads", "only the first few records were created and the rest failed quietly", "how do i work out the right order to create records in"]
product: frappe
---

# make_records

## paths

frappe/desk/page/setup_wizard/setup_wizard.py — make_records, show_document_insert_error
frappe/model/document.py — _validate_links, insert
frappe/model/base_document.py — db_insert

## rules

MUST expect `make_records` to insert each record under its own savepoint and, on any exception, roll back to that savepoint, log the error and continue to the next record with no retry and no reordering.
MUST expect `ignore_if_duplicate=True` to ignore a primary key collision on `name` alone, because `insert` forwards it to `db_insert` and nowhere else; a record whose unique field value duplicates an existing row still raises `UniqueValidationError`.
MUST derive record order from the Link graph before calling a seeder built on `make_records`, because every `Link` field declares its target in `options` and a topological sort places a DocType after everything it points at, including child-table rows, which `_validate_links` checks as strictly as the parent's own fields.
MUST give a `Dynamic Link` field and a Link cycle a retry pass of their own; neither is visible to a static read of the schema, and a cycle cannot be ordered at all.

## how

The seeder's own error handling is the failure mode: a record lost to a dependency-order problem produces no exception the caller sees, only a logged line inside an install nobody reads, so it looks identical to a record that was simply never declared. Deriving the write order from the schema's own Link graph removes the class of bug rather than adding a retry loop around it; only a Dynamic Link and a cycle stay outside what the graph can express.
