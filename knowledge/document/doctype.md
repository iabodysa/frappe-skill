---
name: doctype
description: Saving a Workflow writes the state field into every document of its type that has none, on every save and with no version history.
triggers: ["validate", "on_update", "set_active", "create_custom_field_for_workflow_state", "update_default_workflow_status", "get_workflow_state_count", "workflow_name", "document_type", "is_active", "override_status", "send_email_alert", "states", "transitions", "workflow_state_field", "get_workflow_name", "get_workflow", "get_workflow_field_value", "Workflow", "Workflow State not set", "Not a valid Workflow Action", "Self approval is not allowed", "workflow state field added to every document", "saving a workflow updates existing documents", "saving the approval setup changed thousands of records and i never asked it to", "every old record suddenly got a status after i edited the approval setup", "why did all my existing documents get a status out of nowhere", "the site hung for minutes when i saved the approval setup on a big table", "nothing in the history explains who set the status on all those rows", "the last modified date did not move but the values changed", "a hidden status field appeared on my form after i set up approvals", "my old approval setup switched itself off when i saved a new one", "two approval setups for the same form and only one of them takes effect", "the new approval setup is ignored until i restart the site", "is it safe to open and re-save the approval setup on a table with a million rows"]
product: frappe
---

# Workflow

## paths

frappe/workflow/doctype/workflow/workflow.py — validate, on_update, set_active, create_custom_field_for_workflow_state, update_default_workflow_status, get_workflow_state_count
frappe/workflow/doctype/workflow/workflow.json — workflow_name, document_type, is_active, override_status, send_email_alert, states, transitions, workflow_state_field
frappe/model/workflow.py — get_workflow_name, get_workflow, get_workflow_field_value

## rules

MUST count the documents of the type whose state field is empty before saving a Workflow over a large table, because update_default_workflow_status runs an unbounded UPDATE inside the request.
MUST expect that UPDATE on every save, not only the first; on_update carries no test for a new document.
NEVER look for that UPDATE in the document history — it is raw SQL, so no hook fires, no Version row is written, no timeline entry appears and modified does not move.
MUST read the first states row carrying a docstatus as the value written for that docstatus, and MUST re-read the grid order before saving, since reordering it changes what is written.
MUST expect the UPDATE to reach a document whose state field was cleared by hand, and to leave every document that already carries a state.
NEVER attribute read_only or hidden on an existing workflow_state_field to the Workflow; the custom field is created only where the DocType has no such field and no property of an existing field is touched.
MUST expect a hidden Link to Workflow State carrying allow_on_submit and no_copy where the field was missing, and MUST point workflow_state_field at an existing Select to keep that Select's own options and permissions.
MUST expect saving with is_active checked to clear is_active on every other Workflow for the same document_type by raw SQL.
MUST clear the cache after creating a Workflow outside the desk, because get_workflow_name caches the answer per doctype and caches the empty string when there is none.

## values

workflow_state_field default: workflow_state
created field: Link to Workflow State, hidden, allow_on_submit, no_copy, owned by Administrator
update_default_workflow_status scope: rows whose state field is empty, matched on docstatus
update_default_workflow_status value: the first states row carrying that docstatus
update_default_workflow_status visibility: none — no hook, no Version, no timeline, modified unchanged
is_active: one active Workflow per document_type, enforced by an UPDATE over tabWorkflow
override_status: read by the desk list indicator only

## how

The Workflow record is configuration that writes data. Saving it runs two side effects before anything else happens: a Custom Field is created when `workflow_state_field` names a field the DocType does not have, and then every existing document of that type whose state field is empty is stamped with a state by raw SQL, one statement per distinct docstatus in the grid. Neither is announced in the document history, so treat opening a live Workflow for a small edit as a data-writing operation over the whole table and check the size of that table first.

That makes the direction of the pointer worth choosing deliberately. Point `workflow_state_field` at a field the DocType already declares and the Workflow adds nothing to the schema and changes no property — anything odd about that field belongs to the app that declared it. Leave it at the default and the framework owns a hidden Link that users never see and reports must join to reach.

`is_active` is a switch over the whole `document_type`, not a flag on this row alone, so a second Workflow drafted alongside a live one goes live the moment it is saved active. Whether a session then sees it depends on the per-doctype cache, which stores the empty string for "no workflow" as readily as it stores a name.
