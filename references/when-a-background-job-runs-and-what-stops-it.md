# When a background job runs, and what stops it

`frappe.enqueue` hands the job to a worker BEFORE the enqueueing transaction commits unless
`enqueue_after_commit` is set, so a worker can read a row that does not exist yet and the same work
is queued twice unless `deduplicate` is set with a `job_id`. Only `enqueue_events_for_site` reads
the four pause settings, so any path calling `enqueue_events` directly runs the jobs of a site that
was deliberately paused.

| Route into a worker | When the work becomes visible | What can stop it |
|---|---|---|
| `frappe.enqueue` | at once, before the caller's commit | `enqueue_after_commit`, `deduplicate` with a `job_id` |
| `frappe.enqueue_doc` | the same | the same |
| a `scheduler_events` bucket in `hooks.py` | on the tick for that frequency | `pause_scheduler`, `maintenance_mode`, `disable_scheduler`, System Settings |
| a Scheduled Job Type row | on its own cron | the row's own switch, and nothing else |
| `enqueue_events` called directly | on the tick | nothing — every pause setting is above it |
| the job body, once running | when `execute_job` returns | an exception rolls the job back; five retries for a deadlock, a lock wait timeout or `RetryBackgroundJobError` |

The queue name is a timeout, not a priority: `short`, `default` and `long`, each namespaced by bench
id, so two benches on one redis never dequeue each other's work.

## Settled by

| what it settles | leaf |
|---|---|
| the commit ordering and the duplicate | `knowledge/job/enqueue.md` |
| the commit on return, the rollback, and the five retries | `knowledge/job/execution.md` |
| the three names, the timeouts, and the bench-id namespace | `knowledge/job/queue.md` |
| the one call that reads every pause setting | `knowledge/job/scheduler.md` |
| the row `sync_jobs` keeps and the log it fails into | `knowledge/job/scheduled-type.md` |
| the three locks, and which one the document lock file is for | `knowledge/job/lock.md` |
