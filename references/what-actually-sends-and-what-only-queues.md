# What actually sends, and what only queues

Neither a Notification record nor a `frappe.sendmail` call sends anything: both stop at an Email
Queue row. The one thing that opens an SMTP session is the scheduler's queue flush, registered in
the `all` bucket, and one Default Value — `suspend_email_queue` — returns that flush before it reads
a single row, with no log, no message and no mark on any row.

| Layer | What it hands back | Where the mail can end here |
|---|---|---|
| a Notification record on a document event | one call per channel, nothing to the caller | a channel failure, which writes an Error Log and lets the save commit |
| `frappe.sendmail` | an Email Queue row, an empty list, or nothing | one malformed address cancels it for every recipient and writes no row |
| the same call past a hundred recipients | nothing at all | the split, whose failures are suppressed |
| the queue row at the next flush | a per-recipient status on the row | mute, `suspend_email_queue`, `send_after`, a dead SMTP session |
| `enqueue_create_notification` | nothing to the caller | a disabled user, a user with notifications off, or its own failure |

A row refused by mute or by suspension keeps status `Not Sent` and is picked up by every later
flush, so mail stops with nothing written anywhere and resumes the moment the setting is cleared.

## Settled by

| what it settles | leaf |
|---|---|
| mute, suspension, and the row every later flush picks up | `knowledge/job/email-queue.md` |
| the malformed address and the hundred-recipient threshold | `knowledge/job/recipients.md` |
| the swallowed channel failure, and the lines either side of it | `knowledge/job/notification.md` |
| who `enqueue_create_notification` drops | `knowledge/job/notification-log.md` |
| the tick the flush runs on, and what pauses it | `knowledge/job/scheduler.md` |
| the commit ordering behind a queued send | `knowledge/job/enqueue.md` |
