---
name: queue
description: A queue name is a timeout, the three built-in names are short, default and long, and every queue is namespaced by bench id so two benches on one redis never dequeue each other's jobs.
triggers: ["get_queues_timeout", "get_queue", "get_queues", "get_queue_list", "validate_queue", "generate_qname", "is_queue_accessible", "get_workers", "get_running_jobs_in_queue", "get_redis_conn", "start_worker", "start_worker_pool", "FrappeWorker", "set_niceness", "truncate_failed_registry", "_check_queue_size", "RedisQueue", "QueueOverloaded", "`job_id` paramater is required for deduplication.", "queue name and timeout", "short default long queue", "the background job never runs and just sits there", "my job is stuck forever and nothing happens", "why is my queued task never picked up", "the long task dies after five minutes every time", "the job gets killed halfway and looks like the code broke", "how long can a background task run before it is cut off", "which queue should i send a slow task to", "two sites on the same server are stealing each other's jobs", "jobs from one bench show up on another bench", "the queue fills up and requests start failing", "how do i stop the queue from growing without limit", "i added a new queue and nothing runs on it"]
product: frappe
---

# Queue

## paths

frappe/utils/background_jobs.py — get_queues_timeout, get_queue, get_queues, get_queue_list, validate_queue, generate_qname, is_queue_accessible, get_workers, get_running_jobs_in_queue, get_redis_conn, start_worker, start_worker_pool, FrappeWorker, set_niceness, truncate_failed_registry, _check_queue_size
frappe/utils/redis_queue.py — RedisQueue
frappe/exceptions.py — QueueOverloaded

## rules

MUST pass a queue name that get_queues_timeout knows, because validate_queue throws for anything else and a name added to the workers block of common_site_config.json only exists after that file is edited.
MUST choose the queue by how long the method runs, because the queue name is where the timeout comes from and passing no timeout takes the queue's.
MUST set max_queued_jobs in site config to make the limit exist, because _check_queue_size returns without checking when it is unset and MAX_QUEUED_JOBS is not read there.
MUST expect frappe.QueueOverloaded rather than a silent drop once max_queued_jobs is reached.
MUST define a new queue under the workers key of common_site_config.json with its own timeout, and MUST start a worker for it, because get_queues_timeout builds the list from that key and nothing dequeues a queue no worker watches.
MUST expect a job enqueued for an unwatched queue to sit in redis forever with no error at the call site.
NEVER share one redis_queue between benches without distinct bench ids, because generate_qname prefixes the bench id and is_queue_accessible filters on it.
MUST set redis_queue in common_site_config.json, because get_redis_conn raises without it.
MUST expect get_redis_conn to retry a BusyLoadingError or a ConnectionError five times one second apart and then re-raise.
NEVER count on set_niceness twice in one process; it increments the niceness and is written to be called once per process lifetime.

## values

short: 300 seconds
default: 300 seconds
long: 1500 seconds
custom queues: the workers key of common_site_config.json, timeout key per worker, default 300
queue name in redis: bench id, a colon, the queue type
dequeue order when a worker watches several: the order get_queues_timeout lists them — short, default, long, then custom
failed job retention: rq_job_failure_ttl in site config, else seven days
failed jobs kept: rq_failed_jobs_limit in site config, else 1000, trimmed by truncate_failed_registry
result retention: rq_results_ttl in site config, else 600 seconds
niceness increment: background_process_niceness in site config, else 10
worker pool: start_worker_pool uses FrappeWorker, which starts a scheduler thread of its own

## how

The queue name is not a priority label, it is a contract about duration. A method that runs for four minutes on the default queue is killed at 300 seconds and the failure looks like the method broke. Ask how long the slowest realistic run takes, then pick the name whose timeout covers it, and pass an explicit timeout only when the method's own bound differs from every queue's.

The bench id prefix is the reason a job can look lost. Queues are per bench, not per site, while job ids are per site; so a job enqueued on one bench is invisible to a worker started on another even against the same redis, and nothing on the enqueueing side reports it. When a job never runs, ask which queues the running workers watch before looking at the method.

Adding a queue is two edits, never one. The workers key makes the name valid and gives it a timeout; a worker process started against that name is what empties it. Doing only the first produces an accepted enqueue and a queue that grows.
