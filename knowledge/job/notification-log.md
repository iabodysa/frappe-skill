---
name: notification-log
description: enqueue_create_notification takes a list of users and drops every user who is disabled or who switched notifications off, and its failure never reaches the caller.
triggers: ["enqueue_create_notification", "make_notification_logs", "_get_user_ids", "send_notification_email", "type", "for_user", "from_user", "document_type", "document_name", "link", "is_notifications_enabled", "Notification Settings", "notification not sent to disabled user", "some people never get the bell notification and nobody knows why", "notification did not reach one of the users", "why do only some of my users see the alert in the bell menu", "no error anywhere but the notification never showed up", "the notification silently disappears and nothing is logged", "how do i find out why a person was not notified", "the user turned off notifications long ago and still nothing shows", "no notifications at all right after a fresh install", "i do not get a notification when i am the one who did the action", "notifying myself does not work but notifying others does", "why does the alert not appear for the person who triggered it", "i passed an email and the notification went nowhere"]
product: frappe
---

# Notification Log

## paths

frappe/desk/doctype/notification_log/notification_log.py — enqueue_create_notification, make_notification_logs, _get_user_ids, send_notification_email
frappe/desk/doctype/notification_log/notification_log.json — type, for_user, from_user, document_type, document_name, link
frappe/desk/doctype/notification_settings/notification_settings.py — is_notifications_enabled

## rules

MUST call `enqueue_create_notification` with the whole list of users; a per-user loop at the call site rebuilds the loop it already runs.
NEVER insert a Notification Log row by hand; `enqueue_create_notification` dispatches through `frappe.enqueue`, and a savepoint, try, rollback and `log_error` block around a hand-rolled insert rebuilds what the queue already provides.
MUST read `_get_user_ids` as filtering on two conditions — User `enabled` is 1 AND `is_notifications_enabled` — so a hand-rolled insert that checks only `enabled` writes to users who switched notifications off.
MUST read `is_notifications_enabled` as returning true when the user has no Notification Settings row, so the filter only ever removes an explicit opt-out.
MUST pass a `type` of Alert or Energy Point when the recipient is also the sender; `make_notification_logs` inserts a row for `for_user` equal to `from_user` only for those two types.
MUST read a failure as unreachable from the caller, because the insert happens in a background job.
MUST expect no row at all during a fresh install; `enqueue_create_notification` returns early on `frappe.flags.in_install`.
MUST pass user emails, not user names; `_get_user_ids` matches the User `email` field and returns the User name it found.

## values

types: Mention, Energy Point, Assignment, Share, Alert
recipient filter: User `enabled` is 1, then `is_notifications_enabled(user)`
self-notification: inserted only for type Energy Point or Alert
default when no Notification Settings row exists: enabled
dispatch: `frappe.enqueue` of `make_notification_logs`

## how

A notification is a queued write with two opt-outs in front of it, and both live on the recipient rather than on the sender. Hand the native writer the list and let it subtract; anything you filter yourself will be a subset of one condition and will miss the other.

Because the insert runs in a background job, the writer is not a place to learn whether a person was notified. A row's absence means one of three things — the user is disabled, the user turned notifications off, or the sender is the recipient on a type that does not self-notify — and none of them raise. Decide which by reading the User and the Notification Settings row, not by rerunning the send.
