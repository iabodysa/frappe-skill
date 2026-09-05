---
name: scheduler
description: enqueue_events_for_site is the only call that reads maintenance_mode, pause_scheduler, disable_scheduler and System Settings enable_scheduler, so any path that calls enqueue_events directly runs the jobs of a paused site.
triggers: ["start_scheduler", "enqueue_events_for_all_sites", "enqueue_events_for_site", "enqueue_events", "is_scheduler_inactive", "is_scheduler_disabled", "toggle_scheduler", "enable_scheduler", "disable_scheduler", "activate_scheduler", "schedule_jobs_based_on_activity", "is_dormant", "get_scheduler_tick", "_get_scheduler_lock_file", "is_schduler_process_running", "FrappeWorker", "start_worker_pool", "set_niceness", "`job_id` paramater is required for deduplication.", "scheduler disabled site", "maintenance mode blocks scheduler", "none of my background jobs are running at all", "why did every scheduled task stop after i put the site in maintenance", "how do i turn the scheduler back on for a site", "a paused site is still running its jobs and i do not know what started them", "jobs fire on a site i deliberately stopped", "the tasks run once a day instead of every hour on a quiet site", "why are my jobs running so late on a site nobody uses much", "i started the scheduler twice and only one seems to do anything", "how can i tell whether the scheduler process is actually alive", "the order the jobs run in keeps changing between ticks", "one site throwing an error seems to be skipping the others"]
product: frappe
---

# Scheduler

## paths

frappe/utils/scheduler.py — start_scheduler, enqueue_events_for_all_sites, enqueue_events_for_site, enqueue_events, is_scheduler_inactive, is_scheduler_disabled, toggle_scheduler, enable_scheduler, disable_scheduler, activate_scheduler, schedule_jobs_based_on_activity, is_dormant, get_scheduler_tick, _get_scheduler_lock_file, is_schduler_process_running
frappe/utils/background_jobs.py — FrappeWorker, start_worker_pool, set_niceness

## rules

MUST call enqueue_events_for_site to run a site's due jobs, because enqueue_events reads no pause value and enqueues every Scheduled Job Type with stopped 0 whatever the site config says.
MUST set enable_scheduler in System Settings to run the scheduler, because is_scheduler_disabled reads that single value from the database and treats an unset one as disabled.
MUST clear maintenance_mode, pause_scheduler and disable_scheduler in site config, because is_scheduler_inactive returns True on the first of them that is set and never reaches the rest.
MUST call activate_scheduler as Administrator to clear pause_scheduler and set enable_scheduler in one step, and MUST expect it to throw while maintenance_mode is on.
MUST expect one scheduler per bench, because start_scheduler acquires a FileLock on config/scheduler_process without blocking and returns when another process holds it.
MUST ask is_schduler_process_running rather than counting processes, because the lock is held for the life of the process that took it.
MUST expect schedule_jobs_based_on_activity to be cached for an hour, so a site that has just been woken keeps the previous answer until the cache expires.
MUST expect a dormant site to run its jobs once a day rather than never, because schedule_jobs_based_on_activity returns True when the last Scheduled Job Log is a day old.
NEVER expect dormancy off frappecloud, because is_dormant returns False when developer_mode is set or the bench is not on frappecloud, and again when dormant_days in System Settings is zero.
MUST expect enqueue_events_for_all_sites to shuffle the site list and enqueue_events to shuffle the job list, so job order is not a thing to depend on.
MUST expect an exception in one site's tick to be logged and the loop to continue to the next site.

## values

pause reads, in order: site config maintenance_mode, site config pause_scheduler, site config disable_scheduler, System Settings enable_scheduler
tick: scheduler_tick_interval in common site config, else 60 seconds
bench lock file: config/scheduler_process
selection each tick: Scheduled Job Type rows with stopped 0
activity cache: one hour, on both schedule_jobs_based_on_activity and is_dormant
dormant threshold: dormant_days in System Settings, times 86400, against User last_active
dormant site still runs: once the last Scheduled Job Log is 86400 seconds old
worker pool: FrappeWorker starts a scheduler thread on work and on run_maintenance_tasks

## how

The scheduler is a loop that sleeps a tick and then, per site, decides twice: may this site run anything at all, and which of its jobs are due. The first decision lives entirely in one call frame — enqueue_events_for_site — and the second lives in enqueue_events and the Scheduled Job Type row. Nothing below the first frame re-checks the first decision, which is why a console script or a test helper that reaches for enqueue_events looks like it is doing the same thing and is not: it runs the jobs of a site somebody deliberately paused, under maintenance mode, with no message anywhere.

So when a site runs jobs it should not, ask which frame enqueued them before touching the pause values. And when a site runs none, read the four in their order, because the first one set ends the answer and the remaining three tell you nothing.

Dormancy is a separate refusal from pausing and it is not a switch anyone sets by hand. It is a cached judgement about whether people have been using the site, it only exists on frappecloud with dormant_days set, and it degrades to once a day rather than to nothing. Treat it as an explanation for jobs running late, never for jobs not running at all.
