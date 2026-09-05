---
name: integration-request
description: Integration Request is the outbound call log and only create_request_log writes it, so a call made through make_request leaves no row unless the caller opens one itself.
triggers: ["create_request_log", "get_json", "IntegrationRequest.autoname", "update_status", "handle_success", "handle_failure", "clear_old_logs", "status", "integration_request_service", "is_remote_request", "request_description", "request_id", "default_log_clearing_doctypes", "log an outgoing api call", "integration request log", "we make outgoing calls but nothing shows in the log", "there is no record of the request we just sent out", "why is the outgoing call history empty", "our api keys are visible to anyone who opens the call history", "the logs contain the secret we send in the headers", "old call records disappear after a few months", "the log rows vanished and i needed them for an audit", "staff cannot create or edit these log entries from the screen", "the provider calls back and we cannot find the matching request", "when they send the same callback twice we get two rows and wrong numbers", "how do i keep a trace when the call crashes halfway", "my transaction got committed early because of the logging", "the failure handler cannot save the row because validation fires"]
product: frappe
---

# Integration Request

## paths

frappe/integrations/utils.py — create_request_log, get_json
frappe/integrations/doctype/integration_request/integration_request.py — IntegrationRequest.autoname, update_status, handle_success, handle_failure, clear_old_logs
frappe/integrations/doctype/integration_request/integration_request.json — status, integration_request_service, is_remote_request, request_description, request_id
frappe/hooks.py — default_log_clearing_doctypes

## rules

MUST call `create_request_log` before an outbound call and hold the returned document; nothing in `make_request` writes this record and the two are unconnected.
MUST close the record with `handle_success` or `handle_failure`; both use `db_set`, so they run no validation and survive inside an exception handler.
MUST pass `name=` for a call the provider will report back under its own id; `autoname` reads `flags._name`, so the provider's reference becomes the record name and a callback finds it in one `frappe.get_doc`.
MUST accept a commit inside the call; `create_request_log` inserts with `ignore_permissions=True` and commits, so a caller inside a transaction has that transaction split under it.
NEVER expect a person to create the record from the desk; the DocType grants System Manager read and delete only.
NEVER put a credential in `data` or `request_headers`; both are stored verbatim as JSON and kept for 90 days.
NEVER set `integration_type`; the parameter is deprecated in the function's own docstring in favour of `is_remote_request`.
MUST pass `reference_doctype` and `reference_docname` in `kwargs`, or put them inside `data`; when `reference_doctype` is absent from `kwargs` the function parses `data` and reads both out of it.
MUST use `update_status` rather than `handle_success` when the outcome has to merge into `data`; it loads `data`, updates it, saves with `ignore_permissions=True` and commits.

## values

statuses: empty, Queued, Authorized, Completed, Cancelled, Failed
writer: `create_request_log` only
permission: System Manager, read and delete
retention: 90 days
name override: `flags._name`, set from the `name=` argument
deprecated parameter: `integration_type`, replaced by `is_remote_request`
serialization: `frappe.as_json(obj, indent=1)` unless the value is already a string

## how

The log and the call are two separate decisions. `make_request` opens the socket and writes nothing here; `create_request_log` writes the record and opens no socket. An integration that reports "no log row" is usually one that never called the writer, not one whose call failed.

Because the writer commits, the record survives whatever the caller does next. That is the point: the row exists before the provider is contacted, so a crash mid-call still leaves evidence, and the two closers use `db_set` so they can run from inside an exception handler without a validation pass rewriting the row.

Name the record after the provider's own reference whenever the provider will call back. That turns the callback from a search into a lookup, and it makes a duplicate callback collide on the primary key instead of writing a second row nobody reconciles.
