---
name: lock
description: Frappe has three locks that are not interchangeable — for_update on the read, filelock for a critical section, and the document lock file, which is weak by its own docstring and exists for queue_action.
triggers: ["filelock", "LOCKS_DIR", "create_lock", "lock_exists", "lock_age", "check_lock", "delete_lock", "get_lock_path", "release_document_locks", "LockTimeoutError", "unlock", "is_locked", "check_if_locked", "queue_action", "get_signature", "DOCUMENT_LOCK_EXPIRY", "DOCUMENT_LOCK_SOFT_EXPIRY", "get_value", "get_values", "get_singles_dict", "start_scheduler", "_get_scheduler_lock_file", "after_job", "Error: Document has been modified after you have opened it", "`as_iterator` only works with `as_list=True` or `as_dict=True`", "frappe locking mechanisms", "document lock file vs for_update", "i keep getting told the record is locked and cannot save", "a record stays locked forever after a background job crashed", "why does my job say the document is being worked on when nothing is running", "two background jobs are writing the same record at the same time", "how do i stop a scheduled task from running twice at once", "my process waits forever instead of failing when something else holds the record", "how do i make sure only one process talks to the outside system at a time", "i see a timeout error about waiting for a lock", "how long until a stuck lock clears by itself", "is there a way to force unlock a record that is stuck", "two users saving at the same time overwrite each other"]
product: frappe
---

# Lock

## paths

frappe/utils/synchronization.py — filelock, LOCKS_DIR
frappe/utils/file_lock.py — create_lock, lock_exists, lock_age, check_lock, delete_lock, get_lock_path, release_document_locks, LockTimeoutError
frappe/model/document.py — lock, unlock, is_locked, check_if_locked, queue_action, get_signature, DOCUMENT_LOCK_EXPIRY, DOCUMENT_LOCK_SOFT_EXPIRY
frappe/database/database.py — get_value, get_values, get_singles_dict
frappe/utils/scheduler.py — start_scheduler, _get_scheduler_lock_file
frappe/hooks.py — after_job

## rules

MUST read a row with for_update=True when the same transaction writes it after reading, because the database holds that lock and releases it with the transaction.
MUST pass skip_locked=True to step over rows another transaction holds, and wait=False to fail rather than queue behind one.
MUST use frappe.utils.synchronization.filelock for a section that is not a row — a file, an outbound call, a scheduled method that must not overlap itself.
MUST expect filelock to raise LockTimeoutError after its timeout and to write an Error Log row before raising.
MUST pass is_global=True to filelock only for a bench-wide section, because the default lock file lives under the site's locks directory and a global one under the bench config directory.
NEVER use frappe.utils.file_lock for synchronisation; its own module docstring calls it weak and prone to race conditions, and it exists for document locking around queue_action.
MUST expect doc.lock to raise frappe.DocumentLockedError when a lock file for the document's signature exists and is younger than three hours.
MUST expect doc.lock to delete a lock older than three hours and take it, so an abandoned lock does not need a person.
MUST call doc.unlock or let after_job run release_document_locks, because that hook unlocks only what frappe.local.locked_documents holds in the process that took the lock.
NEVER read is_locked as proof another process is working; it tests for a file, and check_if_locked offers a force unlock after thirty minutes.
MUST expect the scheduler's own bench-wide lock to be a non-blocking FileLock on config/scheduler_process, not a document lock.

## values

for_update: SELECT FOR UPDATE, held to the end of the transaction, on get_value, get_values and get_singles_dict
skip_locked: skips rows another transaction holds
wait=False: fails instead of waiting for the lock
filelock default timeout: 30 seconds
filelock site path: the site's locks directory, the name plus .lock
filelock global path: the bench config directory, the name plus .lock
document lock file name: sha224 of doctype, a colon and name, lowercased, plus .lock, under the site's locks directory
document lock hard expiry: three hours, after which lock deletes it and takes it
document lock soft expiry: thirty minutes, after which check_if_locked offers Force Unlock
file_lock.check_lock timeout: 600 seconds, raises LockTimeoutError

## how

Pick the lock by what two writers can reach at once, not by how long the section is. When that thing is a row and the work is inside one transaction, for_update is the whole answer: the database owns it, it releases when the transaction ends, and there is nothing to clean up if the process dies. Reach past it only when the thing two writers reach is not a row — a file on disk, a call to somebody else's system, a scheduled method whose runs must not overlap — and then filelock is the tool, with is_global saying whether the section is per site or per bench.

The third lock is not a weaker version of the second; it answers a different question. The document lock is a marker that a document is being worked on in the background, readable by the desk, expiring on its own, and offering a person a force unlock. It is advisory by construction — its own module says so — so treating it as mutual exclusion around a short section gives you neither exclusion nor an error.

An app that uses for_update heavily and filelock nowhere is not missing anything. Before adding a lock, name the two writers that can be inside the section at once; if you cannot name the second, the lock is protecting nothing and will only produce timeouts.
