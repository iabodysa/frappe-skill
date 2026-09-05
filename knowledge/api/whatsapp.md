---
name: whatsapp
description: WhatsApp exists in ERPNext as two Data fields on Lead and Opportunity and nothing else, and the Notification channel field offers no WhatsApp option, so sending a message is an outbound integration to build.
triggers: ["Lead.whatsapp_no", "get_lead_with_phone_number", "whatsapp_no", "Opportunity.whatsapp", "Notification.channel", "send_notification_by_channel", "Lead", "Opportunity", "Notification", "A Lead requires either a person", "Lead Owner cannot be same as the Lead Email Address", "send a whatsapp message from erpnext", "whatsapp integration", "there is no whatsapp option in the notification setup", "why can i not pick whatsapp when setting up an alert", "how do i send a whatsapp message to a customer from the system", "i filled the whatsapp number field but no message ever goes out", "the whatsapp field is there so why does nothing send", "we want automatic whatsapp messages when a deal changes stage", "adding whatsapp to the alert channel list does nothing", "how do i connect a whatsapp provider to the system", "is whatsapp messaging built in or do we have to build it", "the alert goes out by email but never by whatsapp"]
product: erpnext
---

# WhatsApp

## paths

erpnext/crm/doctype/lead/lead.py — Lead.whatsapp_no, get_lead_with_phone_number
erpnext/crm/doctype/lead/lead.json — whatsapp_no
erpnext/crm/doctype/opportunity/opportunity.py — Opportunity.whatsapp
erpnext/crm/doctype/opportunity/opportunity.json — whatsapp
frappe/email/doctype/notification/notification.py — Notification.channel, send_notification_by_channel

## rules

NEVER read `whatsapp_no` or `whatsapp` as evidence of a channel; both are `Data` fields holding a phone number, and `get_lead_with_phone_number` matches `whatsapp_no` beside `phone` and `mobile_no` when a call arrives.
MUST treat sending a WhatsApp message as an outbound integration to build — a Password field for the token, `create_request_log` for the record and `make_post_request` for the call — not a channel to switch on.
NEVER expect a Notification to reach WhatsApp; `channel` is a `Literal["Email", "Slack", "System Notification", "SMS"]` and `send_notification_by_channel` switches on exactly those four, so no configuration path turns a Notification into a WhatsApp send.

## values

Lead fieldname: `whatsapp_no`, label WhatsApp
Opportunity fieldname: `whatsapp`, label WhatsApp
call lookup order: `phone`, `whatsapp_no`, `mobile_no`, newest record first
Notification channel field: `Literal["Email", "Slack", "System Notification", "SMS"]`, no WhatsApp option

## how

The word appears in the desk, so the first assumption is that a channel exists and only needs configuring. It does not. Two labelled phone-number fields and one `or_filters` clause are the whole of it, and the Notification dispatcher branches on a closed list that stops at SMS.

That settles the shape of the work rather than blocking it. There is no record to configure, so the native route is the outbound one: hold the provider token in a `Password` field on a settings DocType, open an `Integration Request` before the call, and send through `make_post_request`. Adding an option to the Notification channel field is the one route that looks like it works and silently does nothing.
