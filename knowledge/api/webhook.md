---
name: webhook
description: A doc event appends to a request-local queue that flushes after commit, the worker makes three attempts and swallows the third failure, and the Webhook Request Log row is the only surviving evidence.
triggers: ["get_all_webhooks", "run_webhooks", "_add_webhook_to_queue", "flush_webhook_execution_queue", "Webhook.validate", "Webhook.on_update", "validate_docevent", "validate_secret", "enqueue_webhook", "log_request", "get_webhook_headers", "get_webhook_data", "get_context", "get_all_queues", "WEBHOOK_SECRET_HEADER", "webhook_docevent", "request_method", "request_structure", "is_dynamic_url", "enable_security", "webhook_secret", "timeout", "background_jobs_queue", "url", "headers", "response", "data", "user", "reference_document", "error", "Document.run_method", "Document.clear_cache", "global_cache_keys", "default_log_clearing_doctypes", "Webhook Request Log", "DocType must be Submittable for the selected Doc Event", "Check Request URL", "Same Field is entered more than once", "webhook not firing", "call an external service on document change", "the webhook never fires when a new record is created", "why does my outgoing notification only work on edits and not on new records", "nothing is sent to the other system when a document is added", "i turned the webhook off and it still keeps sending", "the outgoing call keeps firing after i disabled it in the settings", "why does the rule still run after i deleted it", "no calls went out for the records the import created", "the other system never heard about the rows a migration wrote", "why did the bulk upload not trigger any outgoing messages", "the receiving side says the signature does not match", "our partner rejects our payload as untrusted even though the secret is right", "the job finished fine but the other system never got the message", "the outgoing call gives up after a few tries and nobody is told"]
product: frappe
---

# Webhook

## paths

frappe/integrations/doctype/webhook/__init__.py — get_all_webhooks, run_webhooks, _add_webhook_to_queue, flush_webhook_execution_queue
frappe/integrations/doctype/webhook/webhook.py — Webhook.validate, Webhook.on_update, validate_docevent, validate_secret, enqueue_webhook, log_request, get_webhook_headers, get_webhook_data, get_context, get_all_queues, WEBHOOK_SECRET_HEADER
frappe/integrations/doctype/webhook/webhook.json — webhook_docevent, request_method, request_structure, is_dynamic_url, enable_security, webhook_secret, timeout, background_jobs_queue
frappe/integrations/doctype/webhook_request_log/webhook_request_log.json — url, headers, response, data, user, reference_document, error, webhook
frappe/model/document.py — Document.run_method, Document.clear_cache
frappe/cache_manager.py — global_cache_keys
frappe/hooks.py — default_log_clearing_doctypes

## rules

MUST select `after_insert` for a rule that has to see a new document; `on_change` is appended to the event list only when `doc.flags.in_insert` is false, so it matches nothing on an insert and writes no log row.
MUST create two Webhook records to cover create and update; `webhook_docevent` is a single Select.
NEVER select `before_update_after_submit`; `run_webhooks` appends it to the runtime list, but the Select does not offer it, so no record created in the desk can hold it.
MUST make the DocType submittable before selecting `on_submit`, `on_cancel` or `on_update_after_submit`; `validate_docevent` throws otherwise.
NEVER mirror rows to an outside service with a webhook when a patch or a Data Import writes them; `run_webhooks` returns on `in_import`, `in_patch`, `in_install` and `in_migrate` before it even reads the cache, and records nothing about the skip.
MUST read those four flags as the whole exemption list; a scheduler job, a background job and a `bench execute` call carry none of them and do fire.
MUST re-send from the patch itself when a migration has to reach the outside service, because the patch is the only thing that knows which rows it wrote.
MUST read delivery as enqueued, never inline; `now=frappe.flags.in_test` is the only argument that runs it in the caller, so a test observes a delivery a request never shows.
NEVER expect a webhook after a rollback; the flush is registered on `frappe.db.after_commit`.
MUST expect one request per `(webhook, document)` pair per transaction, carrying the last state of the document; `flush_webhook_execution_queue` deduplicates on that key and keeps the last instance.
MUST name the queue on `background_jobs_queue`, because the fallback is `default`, which is the queue the desk competes for.
MUST run `bench --site <site> clear-cache` after deleting a Webhook record; the class defines `on_update` and no `on_trash`, `Document.clear_cache` is `frappe.clear_document_cache` and touches no global key, and `webhooks` is a global key removed only by a full site clear.
MUST read a save of any unrelated Webhook as the accidental fix, since `on_update` clears the shared key and the symptom then stops reproducing.
NEVER edit `tabWebhook` with `frappe.db.set_value`; that path runs no `on_update`, so clearing `enabled` in SQL leaves the rule live in cache.
MUST count three attempts, not three retries; `range(3)` is the whole budget and `raise_for_status` makes any non-2xx a retried failure.
NEVER expect a pause after a read timeout; the `ReadTimeout` branch writes a log row and falls straight into the next attempt, and only the generic branch sleeps.
MUST budget the named queue for `timeout * 3 + 5` seconds, because the generic branch calls `time.sleep` for one second then four inside the worker.
NEVER read a finished background job as a delivered webhook; the loop swallows the third failure, nothing re-raises, and RQ never retries it.
MUST set `enable_security` and read the signature from the `X-Frappe-Webhook-Signature` header as `base64(HMAC-SHA256(secret, json.dumps(data)))`, with Python's default separators and no `default=str`.
MUST keep every `webhook_json` template deterministic; `get_webhook_headers` calls `get_webhook_data` a second time to sign, and the bytes on the wire come from the other call, so a template rendering `now` or a random value signs a payload the endpoint never receives.
NEVER expect the signature to cover a custom header; the HMAC covers the body, and the `webhook_headers` rows are added after it.
NEVER put a credential in a Webhook Header row; every header is serialized into `Webhook Request Log`, which grants read to System Manager.
NEVER look for a status field on `Webhook Request Log`; a non-empty `response` is the only marker of a delivered call, and `error` holds `frappe.get_traceback()` unconditionally, so a success stores whatever traceback the interpreter last held.
MUST render the URL as a template only when `is_dynamic_url` is set; `enqueue_webhook` renders it against the same context the condition uses.
MUST expect a failure while building the request to log one row and return without any attempt.

## values

cache key: `webhooks`, a global key
events always live: on_update, after_insert, on_submit, on_cancel, on_trash, on_update_after_submit
events added only outside an insert: on_change, before_update_after_submit
events the Select offers: after_insert, on_update, on_submit, on_cancel, on_trash, on_update_after_submit, on_change
skipped when: in_import, in_patch, in_install, in_migrate
attempts: 3
sleep between attempts: 1s then 4s, generic failure branch only
timeout default: 5 seconds
request_method options: POST, PUT, DELETE
request_structure options: Form URL-Encoded, JSON
signature header: X-Frappe-Webhook-Signature
Webhook Request Log fields: url, headers, response, data, user, reference_document, error, webhook
Webhook Request Log permission: System Manager, read and delete
Webhook Request Log retention: 30 days
queue fallback: `default`

## how

Three separate things have to be true before a request leaves the site, and each fails silently on its own. The event has to be in the runtime list, which is not the same list the Select offers. The rule has to be in the `webhooks` cache, which is written on save and cleared on save and never on delete. And the transaction has to commit, because the doc event only appends to a request-local list and hands the flush to `after_commit`. Nothing writes a log row for any of those three misses, so "the webhook did not fire" and "the webhook was never considered" look identical from the outside.

The delivery itself is a loop that cannot report its own failure. It attempts three times, sleeps inside the worker between them, and lets the third exception fall out of the loop, so the RQ job finishes successfully whatever happened. Read the `Webhook Request Log` rows and nothing else: one row per attempt, with `response` filled only when a response came back. `error` is written on every row including the successful one, so it is not the field that tells you.

The signature is computed over a second, independent render of the body. That is fine for a template made of field values and wrong for anything that changes between two calls a microsecond apart. Treat the request body as a pure function of the document, and the signature holds; put a timestamp in it and every delivery fails verification at the far endpoint with no clue on this side.
