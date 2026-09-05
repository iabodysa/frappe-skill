---
name: service-level-agreement
description: apply is registered under doc_events["*"]["validate"], so any DocType named on a Service Level Agreement record acquires SLA fields and a validate handler without its controller declaring either.
triggers: ["apply", "get_documents_with_active_service_level_agreement", "set_documents_with_active_service_level_agreement", "remove_sla_if_applied", "before_insert", "create_docfields", "create_custom_fields", "create_communication", "set_first_response_time", "has_website_permission", "doc_events", "Issue", "Select a Default Priority.", "Start Time can", "The Condition", "sla doctype applies to which doctypes", "service level agreement validate hook", "sla timer fields showed up on a form i never set them up on", "why does every record type suddenly have response time fields", "response due and resolution due appeared on my custom form out of nowhere", "my sla dates get wiped out every time i save the ticket", "the response deadline keeps clearing itself for no reason", "why are the sla times blank after saving even though i filled them", "my custom ticket form has sla timers but incoming emails do not attach to it", "replies by email are not being linked to my custom support form", "how do i turn on sla tracking for a record type i built myself", "the first response time is never recorded on my own ticket type", "why does the customer portal show tickets but not my custom ones"]
product: erpnext
---

# Service Level Agreement

## paths

erpnext/support/doctype/service_level_agreement/service_level_agreement.py — apply, get_documents_with_active_service_level_agreement, set_documents_with_active_service_level_agreement, remove_sla_if_applied, before_insert, create_docfields, create_custom_fields
erpnext/support/doctype/issue/issue.py — create_communication, set_first_response_time, has_website_permission
erpnext/hooks.py — doc_events, has_website_permission

## rules

MUST expect apply to run on the validate of every DocType in the site, because it is registered under doc_events["*"]["validate"] rather than under the DocType that carries the SLA.
MUST name a DocType on a Service Level Agreement record to give it SLA fields; apply's only subject test is doc.doctype not in get_documents_with_active_service_level_agreement(), built from the document_type of every Service Level Agreement record.
NEVER expect a custom DocType to need its own controller work for response_by and sla_resolution_by; create_docfields or create_custom_fields inserts the SLA field list into the target meta before an agreement can be saved against it.
MUST expect remove_sla_if_applied to null service_level_agreement, response_by and sla_resolution_by on a document whose doctype carries no active agreement, silently, on the same validate.
NEVER expect a custom ticket DocType to inherit Issue's email side by carrying SLA fields; create_communication, set_first_response_time and has_website_permission are hooked to the Issue name in erpnext/hooks.py, not to whatever carries the SLA.
MUST read before_insert's Issue special case as evidence Issue needs no field injection; its SLA fields are declared as standard fields on the DocType already.

## values

hook registration: doc_events["*"]["validate"] -> apply, one wildcard entry, not per-DocType
active-set cache key: doctypes_with_active_sla, read by get_documents_with_active_service_level_agreement, rebuilt by set_documents_with_active_service_level_agreement on before_insert none / after_insert / on_update / on_trash
field target for a custom DocType: create_docfields when meta.custom is set, create_custom_fields otherwise
fields nulled with no active agreement: service_level_agreement, response_by, sla_resolution_by
Issue hooks in erpnext/hooks.py: has_website_permission for the /issues portal route, on_communication_update -> set_first_response_time

## how

The hook is registered once, against every DocType, so the question a reader should ask is never whether SLA "supports" a given DocType but whether that DocType's name appears on an active Service Level Agreement record. Nothing else gates the wildcard validate — not a DocType flag, not a declared field, not a controller mixin.

The field injection follows the same logic. create_docfields walks the SLA field list and inserts a DocField for each name the target meta lacks, so a custom DocType named on an SLA record acquires service_level_agreement, response_by, sla_resolution_by and the rest without being edited by hand. The reverse holds too: remove_sla_if_applied clears those same fields the moment no active agreement matches, on the same validate that would have set them.

What the wildcard does not carry is Issue's own hooks. create_communication, set_first_response_time and has_website_permission are hooked to the Issue DocType name specifically, in erpnext/hooks.py, so a custom ticket DocType gets SLA timers without gaining inbound-mail threading or a portal route for free.
