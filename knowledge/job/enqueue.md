---
name: enqueue
description: enqueue hands the job to a worker before the enqueueing transaction commits unless enqueue_after_commit is set, and it re-queues the same work unless deduplicate is set with a job_id.
triggers: ["enqueue_doc", "run_doc_method", "create_job_id", "get_job", "get_job_status", "is_job_enqueued", "get_jobs", "_check_queue_size", "task", "queue_action", "execute_action", "after_commit", "before_commit", "after_rollback", "CallbackManager", "`job_id` paramater is required for deduplication.", "Cannot make dict for single fieldname", "Error: Document has been modified after you have opened it", "background job enqueue after commit", "job re-queued after worker restart", "the background task cannot find the record i just created", "my queued work starts before the save is finished", "why does the worker say the document does not exist yet", "the same task got queued twice", "the work ran again after i restarted the workers", "how do i stop duplicate tasks from piling up", "the call gave me nothing back instead of a task handle", "i cannot check the status of the work i just queued", "the worker crashes with an error about something not being sendable", "passing an object into the background task breaks it", "how do i run this straight away instead of in the background"]
product: frappe
---

# Enqueue

## paths

frappe/utils/background_jobs.py — enqueue, enqueue_doc, run_doc_method, create_job_id, get_job, get_job_status, is_job_enqueued, get_jobs, _check_queue_size
frappe/__init__.py — enqueue, enqueue_doc, task
frappe/model/document.py — queue_action, execute_action
frappe/database/database.py — after_commit, before_commit, after_rollback
frappe/utils/__init__.py — CallbackManager

## rules

MUST pass enqueue_after_commit=True when the job reads a row the same request is writing, because enqueue calls q.enqueue_call immediately and a worker can dequeue it before the caller commits.
MUST pass deduplicate=True together with job_id, because enqueue throws when deduplicate is set without one.
MUST expect enqueue to return None when deduplicate finds the job QUEUED or STARTED, and to return None when enqueue_after_commit is set, so NEVER read the return value as a Job in either case.
NEVER prefix a job_id with the site name, because create_job_id already prefixes it to every job_id.
MUST pass on_failure only when the failure needs an action, because enqueue installs truncate_failed_registry as on_failure when the caller passes none, and replacing it stops the failed-job registry being trimmed.
NEVER pass job_name; enqueue calls deprecation_warning for it and job_id is what is_job_enqueued reads.
NEVER pass is_async=False outside a test; enqueue calls deprecation_warning for it and now=True is the documented way to run inline.
MUST expect enqueue to run the method inline through frappe.call when now=True, and also when redis is unreachable while frappe.local.flags.in_migrate is set.
MUST call enqueue_doc rather than enqueue on a bound method, because enqueue_doc queues run_doc_method with the doctype and name and the worker loads the document itself.
MUST call doc.queue_action for a background submit or cancel, because it takes the document lock, prefers the underscore-prefixed inner method when one exists, and defaults enqueue_after_commit to True.
NEVER pass a Document, a datetime or any non-serialisable object in kwargs; the worker receives what redis stored.

## values

enqueue_after_commit: adds the enqueue call to frappe.db.after_commit and returns None
deduplicate: requires job_id, refuses on QUEUED or STARTED, deletes a job in any other state before re-queueing
job id stored: site name, two colons, the caller's job_id, or a uuid4 when none is given
is_job_enqueued: True for QUEUED or STARTED only
get_job: None when the job id is unknown
timeout when unset: the queue's own timeout, else 300
on_failure default: truncate_failed_registry
queue size limit: only when max_queued_jobs is set in site config, throws frappe.QueueOverloaded
frappe.task: decorator that attaches an .enqueue method carrying the decorator's own keywords

## how

Two keyword arguments carry the whole subject. Ask first whether the job reads anything the caller is writing; if it does, the job is racing the commit and enqueue_after_commit is the answer, not a sleep and not a retry. Ask second whether the same logical work can be asked for twice — a button, a hook that fires per row, a scheduled method that overlaps itself; if it can, the pair deduplicate and job_id refuses the second, and without a job_id there is nothing for it to compare.

Everything the worker gets it gets through redis, so kwargs must be plain values. That is why enqueue_doc exists: it passes the doctype and the name and lets the worker load a fresh document, which is also the only version that reflects the commit.

The return value is not something to test. It is a Job on the plain path, and None both when the call is deferred to after-commit and when deduplication refused it. Code that branches on the return is reading three different situations through one value; ask the state with is_job_enqueued instead.
