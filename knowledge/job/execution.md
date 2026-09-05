---
name: execution
description: execute_job commits on return and rolls back on any exception, and it retries the whole job up to five times only for a deadlock, a lock wait timeout or an explicit RetryBackgroundJobError.
triggers: ["execute_job", "RQ_JOB_FAILURE_TTL", "RQ_RESULTS_TTL", "before_job", "after_job", "RetryBackgroundJobError", "CallbackManager", "release_document_locks", "`job_id` paramater is required for deduplication.", "background job retry on deadlock", "execute_job commit rollback", "my background task half wrote the data and stopped", "the task failed and left the record in a broken half state", "why does the same work run five times before it gives up", "the task keeps retrying whenever two things write at once", "how do i make a failed background task try again", "the task left a record locked and nobody can edit it", "a document stays locked after the work is over", "there is no log for the task so i assumed it worked", "the background work ran as the wrong user", "why did my changes disappear when the task threw an error", "how do i run cleanup after the task whether it fails or not"]
product: frappe
---

# Execution

## paths

frappe/utils/background_jobs.py — execute_job, RQ_JOB_FAILURE_TTL, RQ_RESULTS_TTL
frappe/hooks.py — before_job, after_job
frappe/exceptions.py — RetryBackgroundJobError
frappe/utils/__init__.py — CallbackManager
frappe/utils/file_lock.py — release_document_locks

## rules

NEVER call frappe.db.commit inside a background method for the ordinary path; execute_job commits after the method returns.
MUST raise frappe.RetryBackgroundJobError to ask for a retry, because execute_job retries on it, on a deadlock and on a lock wait timeout, and on nothing else.
MUST expect at most five retries, each preceded by a sleep of the attempt number plus one second, after which execute_job calls frappe.log_error and re-raises.
MUST expect frappe.db.rollback before every retry and before every logged failure, so a partially written document does not survive the attempt that wrote it.
MUST expect an Error Log row titled with the method name for a failed job, and NEVER treat the absence of a job log row as the absence of a failure.
MUST register work that has to run whichever way the job ends on frappe.local.job.after_job, because execute_job runs that CallbackManager in its finally block.
MUST read frappe.local.job for the site, method, job_name, kwargs and user of the running job rather than passing them again in kwargs.
MUST expect the job to run as the user recorded at enqueue time, because execute_job calls frappe.set_user with it before the method runs.
MUST hook before_job and after_job for work that wraps every job on the site, and MUST expect after_job to run even when the method raised.
NEVER leave a document locked at the end of a job; release_document_locks is registered on after_job and unlocks only what frappe.local.locked_documents holds.
MUST expect execute_job to call frappe.destroy after an async run, so nothing may hold a database handle past the method's return.

## values

retry limit: five
retry triggers: frappe.RetryBackgroundJobError, database deadlock, lock wait timeout
sleep before retry: attempt number plus one, in seconds
on return: frappe.db.commit, the method's return value is the job result
on any other exception: rollback, frappe.log_error titled with the method name, commit, traceback printed, exception re-raised
before_job shipped by frappe: frappe.recorder.record, frappe.monitor.start
after_job shipped by frappe: frappe.recorder.dump, frappe.monitor.stop, frappe.utils.file_lock.release_document_locks
result kept in redis: 600 seconds unless rq_results_ttl is set
failure kept in redis: seven days unless rq_job_failure_ttl is set

## how

A background method is a transaction whose boundaries someone else owns. Write it to do its work and return; the commit on the way out and the rollback on the way to the Error Log are already there. A method that commits in the middle has split itself into pieces the retry cannot undo, which is exactly the case where a retry makes the data worse rather than better.

That is what decides whether a method may ask for a retry at all. The retry re-runs the whole method from the top, so it is safe only when running twice produces the same state as running once. Check that before raising RetryBackgroundJobError, and where it is not true, fix the second run — a deduplicating job id, an existence check, a row lock — rather than accepting the duplicate.

Failure is quiet at the call site by construction: the caller has already returned. The two places it shows are the Error Log row named for the method and the rq failed registry, and the second is trimmed. So a job whose failure must be acted on needs an on_failure of its own or a record it writes itself; watching for its absence is not a way of learning it failed.
