---
name: rollback
description: FrappeTestCase.setUpClass queues _rollback_db with addClassCleanup, so the rollback runs after the last test in the class and every row one test writes is still visible to the tests that follow it.
triggers: ["FrappeTestCase.setUpClass", "_rollback_db", "_restore_thread_locals", "_commit_watcher", "FrappeTestCase.SHOW_TRANSACTION_COMMIT_WARNINGS", "Database.rollback", "Database.commit", "Database.before_commit", "LogSettings.clear_logs", "LogSettings.register_doctype", "Log Settings", "`as_iterator` only works with `as_list=True` or `as_dict=True`", "test rollback after class", "frappe test transaction rollback", "rows from one test are still there when the next test runs", "why is my test failing on a duplicate that another test created", "the second test in the file blows up on an existing record", "i expected an empty table at the start of each test and it is not empty", "test data is leaking between tests in the same file", "my test left rows behind in the real database", "how do i find what is saving data in the middle of my test", "cleanup only seems to happen at the very end instead of after each test", "calling that cleanup routine wipes out my test rows too", "the error names a duplicate but my test is about something else entirely", "running the tests polluted a shared environment with junk rows", "how do i know if something under test is writing permanently"]
product: frappe
---

# Rollback

## paths

frappe/tests/utils.py — FrappeTestCase.setUpClass, _rollback_db, _restore_thread_locals, _commit_watcher, FrappeTestCase.SHOW_TRANSACTION_COMMIT_WARNINGS
frappe/database/database.py — Database.rollback, Database.commit, Database.before_commit
frappe/core/doctype/log_settings/log_settings.py — LogSettings.clear_logs, LogSettings.register_doctype

## rules

MUST give each test in a class its own distinct key — a different name, a different date — rather than assuming an empty table; `addClassCleanup` runs after the last test, not after each one.
MUST expect a test that proves a UNIQUE index to leave its row behind for the next test in the same class, which then fails on a duplicate error that has nothing to do with what it is testing.
MUST expect the class cleanups to run in LIFO order: `_rollback_db` first, then `_restore_thread_locals` with the flags copied at `setUpClass`.
MUST expect `setUpClass` to commit before it queues anything, so rows written before the class began are outside the rollback.
NEVER call a method that commits from inside a test. The commit ends the ambient transaction, the class rollback afterwards has nothing to undo, and on a shared site it lands every row another suite was holding.
MUST test a `clear_old_logs` implementation by calling that controller method directly with the rows it should delete; `LogSettings.clear_logs` calls `frappe.db.commit()` after every entry in `logs_to_clear`.
NEVER reach a retention rule through the scheduler entry that wraps it either; MUST state the gap where a path cannot be reached without committing.
MUST set `SHOW_TRANSACTION_COMMIT_WARNINGS` on the class to make a commit during the class announce itself; `_commit_watcher` is registered on `frappe.db.before_commit` and prints a warning with a stack.

## values

rollback scope: one test class
queued by: addClassCleanup, in setUpClass
cleanup order: _rollback_db, then _restore_thread_locals
_rollback_db: clears frappe.db.value_cache, then frappe.db.rollback()
_restore_thread_locals: flags, error_log, message_log, debug_log, conf, cache, lang, preload_assets, and deletes frappe.local.request
before the queue: frappe.db.commit() in setUpClass
commit warning: SHOW_TRANSACTION_COMMIT_WARNINGS, default False

## how

The isolation a Frappe test gets is real but its unit is the class, not the method. `setUpClass` flushes what came before with a commit, then queues the rollback as a class cleanup, and `unittest` runs a class cleanup once — after the last test in that class. Everything between those two points is one transaction shared by every method in the class.

So the question a test has to answer about itself is not "is the table clean" but "does any earlier method in this class write the key I am about to write". A test that writes a row and a later test that writes the same natural key collide, and the error names a duplicate rather than the behaviour, which sends the reader to the wrong file. Distinct keys per method cost nothing and remove the whole class of failure.

The other way to lose the boundary is a commit, and the dangerous ones are not in the test — they are inside framework code the test calls. Log retention is the clean example: the entry point loops over the registered log types and commits after each one, which is correct for a scheduled job and fatal for a test, because the commit takes the test's own rows with it and leaves the rollback nothing to undo. The rule that follows is general. When the code under test commits, do not call it; call the piece below the commit, and say plainly which path is left uncovered rather than letting the suite imply it covered it.
