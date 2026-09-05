---
name: states
description: A state's allow_edit role is read only by the desk, and the docstatus jumps between states are refused when the Workflow is saved rather than when a document moves.
triggers: ["validate_docstatus", "state", "doc_status", "update_field", "update_value", "allow_edit", "message", "next_action_email_template", "is_optional_state", "avoid_status_override", "send_email", "apply_workflow", "validate_workflow", "set_workflow_state_on_action", "get_next_possible_transitions", "get_state_optional_field_value", "get_default_state", "get_document_state_roles", "is_read_only", "get_indicator", "refresh", "Workflow", "Workflow Document State", "Workflow Action", "Workflow State not set", "Not a valid Workflow Action", "Self approval is not allowed", "workflow state allow_edit role", "docstatus jump refused", "the form is greyed out for the user but they can still change it from the api", "someone edited a record at a stage where editing should be blocked", "why is the read only stage not actually stopping edits", "it refuses to let me save my approval setup and points at a row number", "i cannot save the approval steps because of an invalid status jump", "why can a draft not go straight to a cancelled stage", "no approval request or email is sent for one of the stages", "the approver never gets notified for a particular step", "why is there no pending action showing for this stage", "new records start in the wrong stage", "the second field that should change with the stage never updates", "approval emails stopped going out even though notifications are on"]
product: frappe
---

# States

## paths

frappe/workflow/doctype/workflow/workflow.py — validate_docstatus
frappe/workflow/doctype/workflow_document_state/workflow_document_state.json — state, doc_status, update_field, update_value, allow_edit, message, next_action_email_template, is_optional_state, avoid_status_override, send_email
frappe/model/workflow.py — apply_workflow, validate_workflow, set_workflow_state_on_action
frappe/workflow/doctype/workflow_action/workflow_action.py — get_next_possible_transitions, get_state_optional_field_value
frappe/public/js/frappe/model/workflow.js — get_default_state, get_document_state_roles, is_read_only
frappe/public/js/frappe/model/indicator.js — get_indicator
frappe/public/js/frappe/form/form.js — refresh

## rules

NEVER treat allow_edit as a permission; it is read by the desk form alone and no Python reads it, so the REST API, a client script and an import write the document whatever the state says.
MUST reach a cancelling state from a submitted state only, because validate_docstatus refuses a doc_status 0 to doc_status 2 transition when the Workflow is saved.
MUST give a pre-submit rejection state doc_status 0, since a draft cannot transition into a cancelled state.
NEVER draw a transition out of a doc_status 2 state; that row is refused whatever it points at.
MUST expect the refusal at Workflow save time and MUST read the transition row number the message carries.
MUST expect no Workflow Action and no email for a transition whose next state carries is_optional_state, because get_next_possible_transitions skips that transition before it collects roles.
MUST order the states table deliberately, because the first row carrying a docstatus is the state a new document defaults to and the state set_workflow_state_on_action writes on a submit or a cancel taken outside apply_workflow.
MUST declare update_field and update_value on the state rather than in a hook when a transition has to move a second field; apply_workflow sets it in the same pass.
MUST set send_email on the state as well as send_email_alert on the Workflow; the enqueue reads both.

## values

doc_status: 0 saved, 1 submitted, 2 cancelled
refused pairs: any state out of doc_status 2, doc_status 1 to 0, doc_status 0 to 2
allow_edit: Link to Role, read by the desk form only
is_optional_state default: 0
avoid_status_override default: 0
send_email default: 1
default state: the first states row whose doc_status equals the document's docstatus
update_field and update_value: applied by apply_workflow after the state field is set

## how

A state row carries two different kinds of setting and they behave nothing alike. `doc_status`, `update_field`, `update_value`, `is_optional_state` and `send_email` are read by Python and change what the framework does. `allow_edit` and `avoid_status_override` are read only by the desk bundle: `is_read_only` compares the state's `allow_edit` role against the user's roles and greys the form. Grey is not refused. A state that must actually be uneditable needs the document submitted, or a permlevel, or a check in the document's own validation.

Design the states before the transitions, because the docstatus shape decides which transitions can exist at all and the refusal arrives when the Workflow is saved, not when a document is stuck. Draw the cancelled state hanging off a submitted state, and give a rejection that must happen before submission a `doc_status` of 0 — a "Rejected" state marked cancelled cannot be reached from a draft at all, and that is discovered on the save that draws the row.

Order matters twice, and both times it is the first matching row that wins. A new document takes the first state carrying its docstatus. A submit or a cancel taken by any path other than `apply_workflow` lands on the first state carrying the resulting docstatus. Reordering the grid therefore changes behaviour with nothing else edited.
