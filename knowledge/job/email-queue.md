---
name: queue
description: A row refused by mute or by suspend_email_queue keeps status Not Sent and is picked up by every later flush, so mail stops with nothing written anywhere.
triggers: ["flush", "get_queue", "retry_sending_emails", "EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_PERCENT", "EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_COUNT", "EmailQueue.can_send_now", "EmailQueue.send", "SendMailContext.__exit__", "notify_failed_email", "get_email_retry_limit", "toggle_sending", "send_now", "clear_old_logs", "show_toggle_sending_button", "Send Now", "are_emails_muted", "execute", "LogDoctype.clear_old_logs", "Email Queue", "Log Settings", "Emails are muted", "Email Queue flushing aborted due to too many failures.", "Only Administrator can delete Email Queue", "email stuck in queue not sent", "email queue status", "emails are not going out and there is no error anywhere", "mail stopped sending and nothing was written to any log", "why did outgoing mail suddenly stop with no warning", "the same message keeps trying to send again and again", "one message has been stuck sending for hours", "a pile of messages is queued and never leaves", "how do i force one message to go out right now", "how do i turn outgoing mail off for a while", "the failure count looks far too low during an outage", "nobody was told that the message failed to send", "old queued messages vanished before i could look at them", "why was only one person notified about the failure"]
product: frappe
---

# Email Queue

## paths

frappe/email/queue.py — flush, get_queue, retry_sending_emails, EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_PERCENT, EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_COUNT
frappe/email/doctype/email_queue/email_queue.py — EmailQueue.can_send_now, EmailQueue.send, SendMailContext.__exit__, notify_failed_email, get_email_retry_limit, toggle_sending, send_now, clear_old_logs
frappe/email/doctype/email_queue/email_queue_list.js — show_toggle_sending_button
frappe/email/doctype/email_queue/email_queue.js — Send Now
frappe/__init__.py — are_emails_muted
frappe/patches/v14_0/set_suspend_email_queue_default.py — execute
frappe/core/doctype/log_settings/log_settings.py — LogDoctype.clear_old_logs

## rules

MUST read `suspend_email_queue` from DefaultValue when mail stops with no error; it sits on no DocType and `toggle_sending` is its only writer.
MUST set it through the Suspend Sending button on the Email Queue list view, shown only to Administrator and System Manager.
MUST set `mute_emails` in site config or `frappe.flags.mute_emails` to silence an app, because `can_send_now` reads it below every send and a call site cannot skip it.
NEVER write an app-level `email_enabled()` that each `frappe.sendmail` call site must call; that design holds only while every call site keeps calling it.
MUST make an app-visible toggle write the native switch rather than be read at each call site.
NEVER read the `Emails are muted` msgprint in `flush` as the stop; it has no return and the flush continues to the batch.
MUST read a row refused by `can_send_now` as untouched — status stays Not Sent, retry unchanged, and every later flush retries it until `clear_old_logs` deletes it.
MUST read `force_send` as skipping `can_send_now` entirely, and MUST read the desk Send Now button as passing it on every click.
MUST read `send_now` as checking a read permission on the row alone before it force-sends.
MUST read status Error with `retry` at the limit as tried and abandoned, and Not Sent with a non-zero retry as still in flight.
NEVER count Error rows as the failure total during an outage; the aborted batch leaves untried rows at Not Sent.
MUST read `notify_failed_email` as reaching one person, the row's owner, and only at the last failure.
MUST read that Notification Log count as a floor; the writer sits under `savepoint(catch=Exception)` and its own failure is rolled back.
MUST read a row stuck in Sending as the work of a killed worker, rescued by `retry_sending_emails` after fifteen minutes at the cost of one retry.
MUST read the batch abort as needing BOTH thresholds, so a batch of ten rows that all fail never trips it.

## values

mute: `frappe.flags.mute_emails` or site config `mute_emails`
suspend: DefaultValue key `suspend_email_queue`, value 1
suspend predecessor: `hold_queue`, carried over by a v14 patch
statuses: Not Sent, Sending, Sent, Partially Sent, Error, Expired
retry limit: System Settings `email_retry_limit`, falling back to 3
batch abort: failures over 0.33 of the batch AND over 10
batch size: site config `email_queue_batch_size`, falling back to 500
stuck rescue: status Sending, unmodified for 15 minutes, error text `Retry Limit Exceeded`
bulk split batch: 1000 recipients per background job, queue `long`
deletion: `clear_old_logs`, retention set by Log Settings, defaulting to 30 days

## how

Three things stop a queue row, and only one of them says so. A raise from the SMTP session becomes a status and a traceback on the row. Mute and suspend become nothing at all: `can_send_now` returns false, `send` returns, and the row is exactly as it was. So the first question about mail that stopped is never which account broke — an account problem raises — it is whether the switch is on.

The status machine is the whole record of an attempt. Below the retry limit a failure writes Not Sent, or Partially Sent when a recipient already succeeded, and adds one to `retry`; at the limit it writes Error and tells the owner once. Read a status with its `retry` together: the pair distinguishes a row still being tried from a row given up on, and neither reads as failure on its own.

`force_send` is the one parameter that reaches `send` past the check, and the desk passes it whenever an operator opens a row and pushes Send Now. Plan for a suspended site to still emit whatever a person clicks.
