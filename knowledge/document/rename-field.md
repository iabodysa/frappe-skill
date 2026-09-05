---
name: rename-field
description: rename_field copies the old column into the new one and never drops it, and when its validate block finds nothing to rename it prints one line to stdout and returns with no exception, so a stamped patch can silently move no data.
triggers: ["rename_field", "pre_model_sync", "post_model_sync", "rename a doctype field", "rename_field does not drop old column", "the old column is still sitting in the table after i renamed the field", "renaming the field did not move any of my data", "the upgrade said it finished but the new field is empty", "why is all my data still in the old column", "no error anywhere and yet zero rows were moved", "how do i check that a field rename actually did something", "should i worry about leftover columns piling up over releases", "my upgrade step ran too early and found nothing to change", "the rename step runs before the new field even exists", "a step that reads a field this release removes finds nothing at all"]
product: frappe
---

# rename_field

## paths

frappe/model/utils/rename_field.py — rename_field
frappe/migrate.py — pre_model_sync, post_model_sync

## rules

MUST expect both the old and the new column to exist in `tab<DocType>` after a field rename, because `rename_field` runs an UPDATE that copies the value and no DROP COLUMN follows it anywhere in migrate.
NEVER verify a field rename by checking that the old column is gone; MUST check that the new column carries the data and that the DocType JSON no longer lists the old fieldname.
MUST expect `rename_field` to print `"rename_field: <field> not found in ..."` and return with no exception when the new field is missing from the DocType or the old column is missing from the table, so a stamped patch can move zero rows and `bench migrate` still exits 0.
MUST register a `rename_field` patch as `post_model_sync`, because it needs `sync_all()` to have already created the new column, and the old column is still present at that point only because migrate never drops columns.
MUST register a `rename_doc` patch for a DocType as `pre_model_sync`, because the old name still has to resolve when it runs.
MUST register a patch that only READS a field this release removes as `pre_model_sync`; after `sync_all()` the read finds nothing and no-ops silently.

## how

Both checks sit inside `if validate:`, and `validate` defaults to True, so passing `validate=False` does not make a rename with nothing to rename work — it drops the print and lets the same silent no-op through without even a line on stdout. Only a field rename leaves an orphan column; `rename_doc` renames the whole table, so there is nothing left behind on that path. Orphan columns from field renames accumulate across releases and dropping them is cosmetic, never a blocker on a verification.
