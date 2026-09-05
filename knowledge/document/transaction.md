---
name: transaction
description: A rollback called with no save_point discards every row written since the transaction began and resets the before_commit and after_commit queues, so work an earlier successful part of the request had queued never runs and nothing announces either loss.
triggers: ["Database.commit", "Database.rollback", "Database.savepoint", "Database.release_savepoint", "Database.begin", "before_commit", "after_commit", "before_rollback", "after_rollback", "savepoint", "add_unique", "sync_database", "application", "SAFE_HTTP_METHODS", "UNSAFE_HTTP_METHODS", "execute_job", "`as_iterator` only works with `as_list=True` or `as_dict=True`", "Invalid request arguments", "Invalid Request", "frappe.db.rollback savepoint", "before_commit and after_commit queues", "everything i saved earlier in the run disappeared and nothing raised an error", "half my records vanished after one bad row in the loop", "why did all my earlier saved rows get thrown away silently", "the background job i queued after saving never ran", "queued follow up work is never picked up after an error in the same run", "why does my after save task get dropped instead of just delayed", "the record i create in a read only endpoint is never actually saved", "data written by a get request disappears right after the response", "why does calling my endpoint from the browser url not save anything", "i get an error saying the save point does not exist", "rolling back after changing a table structure blows up", "my error log entry is gone whenever the operation fails"]
product: frappe
---

# Transaction

## paths

frappe/database/database.py — Database.commit, Database.rollback, Database.savepoint, Database.release_savepoint, Database.begin, before_commit, after_commit, before_rollback, after_rollback, savepoint
frappe/database/__init__.py — savepoint
frappe/database/mariadb/database.py — add_unique
frappe/app.py — sync_database, application
frappe/auth.py — SAFE_HTTP_METHODS, UNSAFE_HTTP_METHODS
frappe/utils/background_jobs.py — execute_job

## rules

NEVER call `frappe.db.rollback()` with no `save_point` inside a loop that continues; it issues an unscoped rollback, opens a fresh transaction and continues, so every row written earlier in the request is gone and nothing raises.
MUST expect a bare rollback to reset `before_commit` and `after_commit`, so an effect registered through `enqueue_after_commit` is discarded rather than deferred.
MUST expect the `save_point` branch to leave those queues intact; it rolls back to the named point only.
MUST wrap each row of a batch in `savepoint`, imported from `frappe.database`, which names a random save point, rolls back to it on the caught exception and releases it on success.
NEVER call `frappe.db.savepoint(catch=...)`; the method on the Database object takes a save point NAME, and the context manager is the module-level function.
NEVER wrap DDL in a save point; MariaDB commits around `ALTER TABLE` whether it succeeds or fails, so the rollback in the handler raises that the save point does not exist — `add_unique` commits before its own DDL for the same reason.
MUST let a statement in a DDL path stand or fail on its own with no rollback at all.
MUST raise and let the request boundary own the rollback where the whole request is meant to be atomic.
NEVER call `frappe.db.commit()` inside a controller method; it splits the document's atomicity and can persist half an operation.
MUST expect a request whose method is GET, HEAD or OPTIONS to end in a rollback, not in nothing, so a whitelisted method reached over GET that inserts a row loses the write while returning a payload built from what it just wrote.
MUST set `frappe.local.flags.commit` where a safe-method endpoint has to record something durable; `sync_database` reads it before it reads the request method, and it is the framework's own replacement for a hand-written commit.
MUST record a failure that has to survive its own transaction through an independent mechanism, never as an ordinary insert in the transaction that is about to roll back.

## values

commit on: POST, PUT, DELETE, PATCH, or frappe.local.flags.commit
rollback on: GET, HEAD, OPTIONS, and any other method not in the unsafe set
bare rollback: before_commit reset, after_commit reset, before_rollback run, ROLLBACK, begin, value cache cleared, after_rollback run
save_point rollback: ROLLBACK TO SAVEPOINT, value cache cleared, hook queues untouched
savepoint context manager: a ten-letter random name, rollback to it on the caught exception, release on success; usable as a decorator over a whole function
default catch: Exception

## how

There are two rollbacks and they differ by more than scope. The scoped one undoes statements. The bare one undoes statements, throws away the queued commit-time effects, and then opens a new transaction so execution simply carries on — which is why the damage is invisible: no exception, no log line, and the loop that called it keeps producing rows that look fine. Whenever a bare rollback appears inside a handler or a loop, the question is what else was already written in that request, and the answer is usually everything.

Choose the shape from what independence the work has. One atomic request raises and lets the boundary decide. Independent rows each take a save point, which is the framework's own primitive for exactly that and is why hand-written transaction handling is not needed. An effect that must happen only after success is queued for after the commit, and must be understood as cancellable by any later bare rollback in the same request.

DDL is the exception that breaks the pattern rather than an instance of it. The database ends the transaction around a schema change, so the save point taken before it is gone by the time the handler runs, and the code written to survive the failure is the code that raises. The framework makes the same admission by committing before its own schema change.

The request boundary is where all of this is finally settled, and it is settled by the HTTP method rather than by anything the code did. A safe method rolls back actively, which turns a write inside a GET endpoint into a success response over a database that kept nothing.
