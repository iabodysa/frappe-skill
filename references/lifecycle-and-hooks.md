# Where a controller check runs, and what runs around it

A controller's `validate` runs AFTER the framework has set defaults, resolved every `fetch_from` and
checked permissions, and BEFORE the framework validates its own field properties. That position is
the whole design question: a check placed above it never fires, and a check placed below it throws
first and hides the framework's own message. A hooked method runs the controller body, then the
handlers registered for the DocType by name, then the wildcard handlers.

| Entry | What the framework runs first | What your code can still refuse |
|---|---|---|
| `doc.insert()` | defaults, `fetch_from`, the `create` right, then autoname | anything in `validate` and `before_insert` |
| `doc.save()` on an existing row | the `write` right, then defaults and `fetch_from` | anything in `validate` and `before_save` |
| `doc.submit()` | the action chosen by comparing the stored docstatus with the one now set | `before_submit`, and nothing about concurrency |
| `doc.cancel()` | the `cancel` right | nothing — the save beneath it skips `_validate` |
| `doc.db_set` | the previous document is loaded | `before_change` and `on_change` only |
| a `doc_events` handler by DocType name | the controller body first | its own body |
| a `doc_events` wildcard handler | every by-name handler first | its own body, and it overwrites the return |

A Time field is stamped with `nowtime` on insert whatever its default, because that branch sits
outside the block that reads a default at all.

## Settled by

| what it settles | leaf |
|---|---|
| where `validate` sits, and what a hand check above or below it costs | `knowledge/document/save.md` |
| the three-step order and the shared return value | `knowledge/document/hooks.md` |
| the docstatus comparison, and two requests submitting one draft | `knowledge/document/submit.md` |
| the cancel save that skips `_validate` | `knowledge/document/cancel.md` |
| what it skips and what it still reaches | `knowledge/document/db-set.md` |
| the Time field stamped past its own default | `knowledge/document/defaults.md` |
| which DocField properties the server enforces | `knowledge/document/validation.md` |
| the rollback that empties the commit queues | `knowledge/document/transaction.md` |
| the wildcard doc_event that adds a validate handler no controller declares | `knowledge/document/service-level-agreement.md` |
