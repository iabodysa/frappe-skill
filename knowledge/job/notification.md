---
name: notification
description: A channel that fails writes an Error Log and lets the save commit, while a failure one line either side of that catch raises and refuses the save.
triggers: ["Notification.send", "send_notification_by_channel", "get_list_of_recipients", "load_standard_properties", "get_template", "get_documents_for_today", "evaluate_alert", "Notification.on_update", "get_doc_module", "export_module_json", "channel", "event", "get_info_based_on_role", "Role", "Please specify which date field must be checked", "Please specify which value field must be checked", "Please specify the field from which to attach files", "email notification failed silently", "notification channel error handling", "my alert email is not going out and there is no error on screen", "the alert stopped firing and nothing tells me why", "why did my alert turn itself off", "the alert was enabled yesterday and is disabled today on its own", "after renaming a field the alert quietly stopped working", "saving the record fails and the message points at an alert", "the whole save is rolled back because of a notification", "why does one alert break the save and another one does not", "people receive the alert but get permission denied when they click the link", "the link in the alert opens an error page for my staff", "how do i check whether an alert actually ran", "the daily reminder alert never runs anymore"]
product: frappe
---

# Notification

## paths

frappe/email/doctype/notification/notification.py — Notification.send, send_notification_by_channel, get_list_of_recipients, load_standard_properties, get_template, get_documents_for_today, evaluate_alert, Notification.on_update
frappe/modules/utils.py — get_doc_module, export_module_json
frappe/email/doctype/notification/notification.json — channel, event
frappe/core/doctype/role/role.py — get_info_based_on_role

## rules

MUST search Error Log for both `Failed to send Notification` and `Error in Notification` when an alert is reported as not firing; a clean desk is not evidence that the alert never ran.
MUST read `send_notification_by_channel` as catching every exception and writing `Failed to send Notification`, so the document event continues and the save commits.
MUST read `load_standard_properties`, called before that dispatch, and `evaluate_alert`, which ends both its handlers with `frappe.throw`, as raising instead, so the parent write is refused and rolls back.
MUST read `set_property_after_alert` as carrying its own catch, titled `Document update failed`.
NEVER wrap a Notification send in a hand-written try/except; the framework already catches the dispatch, and a wrapper newly hides only the half that raises.
MUST read a channel failure as unretried; the Email channel gets its retries later inside the Email Queue, and only if a queue row was written.
MUST create `<module>/notification/<name>/<name>.py` for any Notification carrying `is_standard`; `get_doc_module` imports that dotted path on every fire, through both `load_standard_properties` and `get_template`, and an empty file satisfies the import.
MUST read `export_module_json` on update as the writer that creates that folder in developer mode.
MUST check Enabled first when a Value Change alert stops firing; `evaluate_alert` writes `enabled` to zero with `db_set` when `has_column` fails for `value_changed`, and nothing turns it back on.
MUST re-point `value_changed` and re-enable the record after renaming a watched field, because the check reads the COLUMN, so a rename landing in the DocType JSON ahead of the schema migration is enough to trip it.
NEVER read that check as covering the other events; only Value Change carries it and only when the document is not new, so a Days Before or Days After alert whose `date_changed` field disappears fails on every run instead.
MUST read `receiver_by_role` as resolving through `get_info_based_on_role` with `ignore_permissions=True`, which walks Has Role to User and checks no permission on `document_type`.
NEVER read a delivered notification as evidence its audience can open the record; the `/app/<doctype>/<name>` link raises PermissionError on click, nothing logs it, and nothing warns at save time.
MUST confirm the named role holds a read DocPerm on `document_type` when writing the Notification, because nothing at runtime will.

## values

channels: Email, Slack, System Notification, SMS
extra: `send_system_notification` adds a System Notification alongside any other channel
events: New, Save, Submit, Cancel, Days After, Days Before, Value Change, Method, Custom
caught title: `Failed to send Notification`
raised title: `Error in Notification`
property write title: `Document update failed`
self-disable message: `Notification <name> has been disabled due to missing field`
role resolver: Role, Has Role, User — with Administrator resolved to the Administrator user directly

## how

One try block decides everything about how a broken alert looks. Inside it, a failure becomes an Error Log and the save succeeds. Outside it, a failure becomes a throw and the save is refused. The template load sits outside on one side and the property write sits outside on the other, so the same broken Notification either loses the alert or loses the document, and the person who pressed Save cannot tell which happened. Diagnose by reading Error Log titles, never by reading the outcome of the save.

A standard Notification is not a record; it is a Python package the framework imports by name on every fire. Ship the folder with the fixture or the alert takes the document down with it.

Reading `receiver_by_role` as a permission decision is the common mistake. It is a mailing list. The permission question is separate and has to be answered when the Notification is written, because the send will succeed either way and the failure appears only when someone clicks the link.
