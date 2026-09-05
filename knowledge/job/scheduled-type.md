---
name: scheduled-type
description: sync_jobs deletes a Scheduled Job Type only when its method string is absent from hooks, so a method that stops resolving while its hooks line stays keeps its row and fails into its own log on every tick forever.
triggers: ["ScheduledJobType", "autoname", "validate", "enqueue", "is_event_due", "is_job_in_queue", "rq_job_id", "get_next_execution", "execute", "log_status", "update_scheduler_log", "get_queue_name", "on_trash", "execute_event", "run_scheduled_job", "sync_jobs", "insert_events", "insert_cron_jobs", "insert_event_jobs", "insert_single_event", "clear_events", "scheduler_events", "Scheduled Job Type", "Cron format is required for job types with Cron frequency.", "scheduled job type deleted", "sync_jobs removes stale job", "i removed the job from the code but it still runs every hour", "why does a job i deleted keep firing after a migrate", "the background job fails every time and nobody ever sees an error", "how do i actually stop a recurring job from running", "renaming the function broke the nightly task and nothing warned me", "the scheduled task never shows any log so i cannot tell if it ran", "how do i make something run every night at a specific minute", "two different jobs ended up with the same name and one overwrote the other", "i want a schedule the fixed options cannot express", "the site was down all weekend and the missed runs never caught up", "how do i trigger a scheduled task by hand to test it", "all the history of a job vanished after i cleaned up the code", "the scheduled job never runs and no error ever appears"]
product: frappe
---

# Scheduled Job Type

## paths

frappe/core/doctype/scheduled_job_type/scheduled_job_type.py — ScheduledJobType, autoname, validate, enqueue, is_event_due, is_job_in_queue, rq_job_id, get_next_execution, execute, log_status, update_scheduler_log, get_queue_name, on_trash, execute_event, run_scheduled_job, sync_jobs, insert_events, insert_cron_jobs, insert_event_jobs, insert_single_event, clear_events
frappe/hooks.py — scheduler_events

## rules

MUST remove the line from scheduler_events in hooks.py to remove a job, because clear_events deletes a row only when its method string is missing from the hooks it just read.
MUST expect insert_single_event to print a yellow "is not a valid method" line and return without touching an existing row when frappe.get_attr fails, so a renamed or deleted method leaves its row behind and bench migrate still succeeds.
MUST delete the Scheduled Job Type row by hand when the hooks line is already gone and the row remains.
MUST expect clear_events to skip any row carrying a scheduler_event and any row carrying a server_script, so those are never removed by a migrate.
MUST declare a cron string under the cron key of scheduler_events for anything the named frequencies cannot express, and MUST expect insert_single_event to update only frequency and cron_format on an existing row.
MUST expect Scheduled Job Type to be named from the last two dotted segments of its method, so two methods sharing a module name and a function name collide.
MUST set create_log to see a run, and MUST expect validate to force it to 1 for every frequency other than All.
MUST expect execute to catch every exception, roll back and write status Failed to the Scheduled Job Log, so a broken scheduled method never raises anywhere a person is watching.
MUST expect enqueue to skip a job whose rq_job_id is already QUEUED or STARTED and to log that skip through the scheduler logger only.
NEVER call a scheduled method directly to test it and read the result as a scheduler run; call execute_event, which is whitelisted for System Manager and enqueues with force.
MUST expect run_scheduled_job to raise frappe.InReadOnlyMode when maintenance_mode is set.
NEVER rely on Hourly Maintenance or Daily Maintenance to spread load across sites, because get_next_execution computes the per-site offset and then returns a value computed without it.

## values

frequency options: All, Hourly, Hourly Long, Hourly Maintenance, Daily, Daily Long, Daily Maintenance, Weekly, Weekly Long, Monthly, Monthly Long, Cron, Yearly, Annual
All: every scheduler_interval seconds expressed as minutes, default 240 seconds
Hourly, Hourly Long, Hourly Maintenance: minute zero
Daily, Daily Long, Daily Maintenance: midnight
Weekly, Weekly Long: midnight Sunday
Monthly, Monthly Long: midnight on the first
Yearly, Annual: midnight on the first of January
queue: long when the frequency contains Long or Maintenance, else default
name: the last two dotted segments of method
rq job id: scheduled_job, two colons, the method
due test: next execution from last_execution, falling back to creation, at or before now
create_log: forced to 1 unless frequency is All
statuses written: Start, Complete, Failed
last_execution written: on status Start when create_log is 1, on every status write when it is 0
on_trash: deletes every Scheduled Job Log for the row

## how

The row is a cache of a hooks line, and the two can disagree in one direction only. A migrate adds and updates rows from hooks, and it deletes a row whose method string no longer appears in hooks — the string, not the callable. A method that stops importing keeps its string, so it keeps its row, so the scheduler keeps enqueueing it, and the only trace is a Failed row in its own log. Ask whether the string is still in hooks before asking why the job still runs; nothing about the failure will lead you there.

The reverse direction is where the loud failure is: delete the hooks line and the row goes with it, taking every Scheduled Job Log row for it through on_trash. So the log is not a place to keep history you need after the job is retired.

Choose a frequency by what the job may not miss. The named frequencies are fixed cron strings anchored at midnight or the hour, and the row's own last_execution is what "due" is measured from, so a site that was down does not replay missed runs — it runs once when it comes back. Where the exact minute matters, write the cron string; where it must not overlap itself, the rq_job_id already refuses a second copy while the first is queued or running.
