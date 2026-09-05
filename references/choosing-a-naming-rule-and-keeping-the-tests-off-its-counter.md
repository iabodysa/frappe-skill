# Choosing a naming rule, and keeping the tests off its counter

Declare ONE `autoname` route per DocType: naming runs a fixed sequence and the first step that sets
a name ends it, so a second declaration is dead rather than combined. Only the series routes keep a
number, and that number lives in one `tabSeries` row held under `FOR UPDATE` until the inserting
transaction commits, so every insert resolving the same prefix is serialised for the whole of that
transaction. A test record, a fixture import and a rename each reach that row by a different path.

| `autoname` route | where the name comes from | what it costs the counter |
|---|---|---|
| `naming_series:` | the `tabSeries` row for the prefix the field resolved to | one lock per prefix, held to commit |
| a literal carrying `#` — `PRE-.#####` | the same `tabSeries` row scheme | the same lock, on a prefix nothing can vary |
| `format:` | a template that MAY contain `#` | a shared row only when the template carries `#` |
| `field:` | the value of the named field, trimmed and written back | none |
| `hash` | a random hash | none |
| `prompt` | the value the user typed | none |
| `autoincrement` | the database column | none — the database owns it |
| Document Naming Rule | the rule's own prefix and counter | its own row, ahead of every route above |

An `autoname` string matching no route leaves the name empty and the document is given a random hash
with no error, so the absence of a failure is not proof the route you declared is the route that ran.

## Settled by

| what it settles | leaf |
|---|---|
| the sequence, and the silent hash for an unmatched string | `knowledge/document/autoname.md` |
| the `tabSeries` row, the lock, and how long it is held | `knowledge/document/naming-series.md` |
| a fixture import runs with `in_import`, so no series advances | `knowledge/bench/fixtures.md` |
| test records are built once per site and never re-read | `knowledge/bench/records.md` |
| the exit code a failing suite reports | `knowledge/bench/runner.md` |
