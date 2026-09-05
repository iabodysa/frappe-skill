---
name: recipients
description: One malformed address cancels the mail for every other recipient and writes no queue row, and past a hundred recipients the send returns nothing at all.
triggers: ["EMail.validate", "EMail.as_string", "QueueBuilder.process", "QueueBuilder.as_dict", "QueueBuilder.send_emails", "final_recipients", "final_cc", "final_bcc", "EmailQueue.set_recipients", "EmailQueue.send", "sendmail", "STANDARD_USERS", "Email Queue", "Headers must be a dictionary", "Only Administrator can delete Email Queue", "Updating Email Queue Statuses. The emails will be picked up in the next scheduled run.", "one bad email address blocks the whole email", "email queue recipient limit", "nobody got the email and there is nothing in the queue to show for it", "one wrong address in the list and the whole send died", "why does a single typo in one recipient stop everyone else from getting the mail", "the send just returns empty and i cannot tell if it worked", "how do i know a mail actually went out when the call gives me nothing back", "sending to a big list quietly reports failure even though the mails go", "the person on copy is getting the same message over and over", "why does the cc address receive one email per person on the list", "the queue row lists the right person but the to line is blank", "mail works for normal users but never for the admin account i test with", "i sent to a hundred people and half of them never received anything", "how can i count who actually received a bulk mail instead of guessing"]
product: frappe
---

# Recipients

## paths

frappe/email/email_body.py — EMail.validate, EMail.as_string
frappe/email/doctype/email_queue/email_queue.py — QueueBuilder.process, QueueBuilder.as_dict, QueueBuilder.send_emails, final_recipients, final_cc, final_bcc, EmailQueue.set_recipients, EmailQueue.send
frappe/__init__.py — sendmail, STANDARD_USERS

## rules

MUST resolve a user id to that User's `email` field before putting it in `recipients`, because `EMail.validate` drops Guest and Administrator from recipients, cc and bcc before it validates anything.
MUST read a queue row that lists Administrator as a recipient over a message with an empty To as that drop; the strip runs on the message only, while `as_dict` writes the unfiltered recipient list to the child rows and `send` hands each child row value to `sendmail` as the address.
MUST validate an address list before passing it to `frappe.sendmail` whenever it is assembled from user data — a Contact field, a child table, an imported column.
MUST read address validation as all or nothing: `as_string` raises on the first malformed address, `as_dict` catches it, writes an Error Log titled `Invalid email address`, and returns nothing, so no Email Queue row exists for any recipient.
NEVER read that Error Log title as naming the offender; its message lists the sender and every final recipient together.
MUST test the return value of `frappe.sendmail` when the send is load-bearing and the recipient list is small; a falsy return is the only in-process signal that the mail was refused.
NEVER test the return value of a large send; past a hundred final recipients the branch that splits the send has no return statement and gives back the same falsy answer a refused send gives.
MUST count Email Queue rows by status over `reference_name` to judge a bulk send, never the absence of an error, because `send_emails` wraps each per-recipient send in `suppress(Exception)`.
MUST expect cc and bcc on every one of those per-recipient rows, so a cc address receives one email per recipient.
MUST read `smtp_server_instance.quit()` at the end of `send_emails` as unguarded; a first recipient that cannot build a server leaves that name unset and the job ends on its own exception.
MUST read an unsubscribed address as removed before any of this, by `final_recipients`, `final_cc` and `final_bcc`.

## values

stripped ids: `frappe.STANDARD_USERS`, the pair Guest and Administrator
split threshold: more than 100 final recipients, or `queue_separately` passed by the caller
forced queueing: `send_now` with 1000 or more final recipients
job batch: 1000 recipients per `frappe.enqueue`, queue `long`, job name `send_bulk_emails_for`
refused send: Error Log titled `Invalid email address`, return value `[]`

## how

`frappe.sendmail` builds the MIME message before it writes anything, so every address problem is decided before a row exists. That ordering is why a refusal leaves no trace in the Email Queue and why the one Error Log row is the entire record. Treat the call as a parser that either accepts the whole list or discards it.

Two different reasons make the call return something falsy: the list was refused, and the list was too long to answer for. They are indistinguishable at the call site, so pick the check by size. Below the threshold, the return value is the answer. Above it, the rows are the answer and they do not exist until the background job runs, so query by `reference_name` and count statuses.

Passing `frappe.session.user` straight into `recipients` works for every account except the two a developer signs in as first, and it fails by producing a queue row that looks correct.
