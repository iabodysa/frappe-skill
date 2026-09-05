---
name: action
description: A Workflow Action row is created once per document and state whatever its status, so a state reached a second time produces no row, no list entry and no email.
triggers: ["process_workflow_actions", "is_workflow_action_already_created", "create_workflow_actions_for_roles", "update_completed_workflow_actions", "get_allowed_roles", "get_workflow_action_by_role", "update_completed_workflow_actions_using_role", "clear_workflow_actions", "get_permission_query_conditions", "has_permission", "get_next_possible_transitions", "get_users_next_action_data", "send_workflow_action_email", "get_workflow_action_url", "get_confirm_workflow_action_url", "apply_action", "confirm_action", "on_doctype_update", "reference_doctype", "reference_name", "workflow_state", "status", "user", "permitted_roles", "completed_by", "completed_by_role", "doc_events", "get_signed_params", "verify_request", "Workflow Action", "workflow action row not created twice", "workflow action list view", "the approval email only arrived the first time", "no email goes out when the document comes back for approval a second time", "why does the approver stop getting notified after it is sent back for changes", "the pending approvals list is empty but there is a document waiting on me", "my approvers cannot see anything in their approval queue", "why can only the administrator see all the pending approvals", "the approval link in the email still works after someone edited the document", "it warns me the document was changed after i opened it but still lets me approve", "how do i find out who actually approved this document", "the second time it reaches the same step nobody is told about it"]
product: frappe
---

# Workflow Action

## paths

frappe/workflow/doctype/workflow_action/workflow_action.py — process_workflow_actions, is_workflow_action_already_created, create_workflow_actions_for_roles, update_completed_workflow_actions, get_allowed_roles, get_workflow_action_by_role, update_completed_workflow_actions_using_role, clear_workflow_actions, get_permission_query_conditions, has_permission, get_next_possible_transitions, get_users_next_action_data, send_workflow_action_email, get_workflow_action_url, get_confirm_workflow_action_url, apply_action, confirm_action, on_doctype_update
frappe/workflow/doctype/workflow_action/workflow_action.json — reference_doctype, reference_name, workflow_state, status, user, permitted_roles, completed_by, completed_by_role
frappe/hooks.py — doc_events
frappe/utils/verified_command.py — get_signed_params, verify_request

## rules

MUST look for a Completed Workflow Action carrying the document and the state before diagnosing a missing approval email as a mail failure; existence alone stops the whole pass.
NEVER rely on the workflow email for an approval that can return to a state it already visited — a reject back to draft, an amendment, a revise and resubmit round; only the second and later rounds are silent.
NEVER build an approval report over Workflow Action for an ordinary user, because the permission query condition pins status to Open and only Administrator is exempt.
MUST answer who approved a document from the Workflow comment the transition adds, not from completed_by.
NEVER read an empty Workflow Action list as proof the row is gone; a direct get_doc on the same Completed row is returned, since has_permission tests the permitted roles and says nothing about status.
NEVER read the edited-document alert as a refusal; a mismatched last_modified only passes alert_doc_change to the same confirmation page, and the confirmation link it offers carries no last_modified at all.
MUST express a re-approval requirement as a transition condition or as a state reset on edit, because a workflow state change is the only thing that expires an emailed action link.
MUST expect the rows to survive every ordinary transition; clear_workflow_actions deletes them and runs from on_trash alone.
MUST enable send_email_alert on the Workflow and send_email on the state before expecting any mail.

## values

created per pass: one Workflow Action, one permitted_roles row per allowed role
existence test: reference_name, reference_doctype and workflow_state — status is not a filter
completed per pass: one row, the lowest permitted role by name
status: Open, Completed
list visibility: Open rows the user's roles permit or that name the user; Administrator sees all
has_permission: the row's permitted roles against the user's roles, status untested
emailed link parameters: doctype, docname, action, current_state, user, last_modified
confirmation link parameters: action, doctype, docname, user
link expires on: a workflow state change
hooked events: on_update, on_cancel, on_trash, on_update_after_submit
index: reference_name, reference_doctype, status

## how

The row is the framework's to-do item for an approver, and everything surprising about it follows from one design decision: the row is keyed by the document and the state it is waiting in, and the existence test that decides whether to create it does not look at status. A document that arrives at a state for the second time finds the first visit's Completed row still there and `process_workflow_actions` returns immediately — before it completes the open rows, before it collects the next transitions, before the mail is enqueued. Any workflow with a loop in it mails once and then goes quiet, so treat the mail as a convenience and the state itself as the thing to watch.

Read the emailed link as a signed statement about a state, not about a document. The first hop compares the document's state to the state the link was signed with, and only a change there gives the Link Expired page. A field that moved since the mail produces an alert on a page that still offers the button, and the confirmation hop re-loads the document as it stands now. So an approver approves today's values from Tuesday's mail; if that is unacceptable, the transition condition is where to say so.

To find out who approved a document, the completed rows are the wrong place to look. They exist and they carry `completed_by` and `completed_by_role`, but the permission query condition appends `status='Open'` outside the role test, so no list, no report and no `get_all` reaches them for any user but Administrator, however wide that user's permissions are. The document's own Workflow comment is the record that ordinary users can read.
