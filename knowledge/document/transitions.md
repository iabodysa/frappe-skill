---
name: transitions
description: Every transition check except self-approval runs on the save path, so writing the state field directly passes a transition whose allow_self_approval is off.
triggers: ["get_transitions", "is_transition_condition_satisfied", "get_workflow_safe_globals", "apply_workflow", "validate_workflow", "has_approval_access", "get_common_transition_actions", "bulk_workflow_approval", "_validate", "get_roles", "validate", "disable_role", "remove_roles", "state", "action", "next_state", "allowed", "allow_self_approval", "condition", "send_email_to_creator", "show_actions", "setup_btn", "Role", "Workflow Transition", "Workflow State not set", "Not a valid Workflow Action", "Self approval is not allowed", "workflow transition condition", "self approval allowed", "the person who raised the request approved it himself and nothing stopped him", "someone approved their own document even though self approval is switched off", "why can the same user create and approve when i turned self approval off", "i keep getting told this is not a valid action but the button was right there", "clicking approve fails with a message about an invalid action", "why does the approval refuse with an invalid action message and name nothing", "the approval works when i test it and breaks for everyone else", "the approve buttons never show up for normal users but they show for me as admin", "why do the approval buttons disappear for the people who actually need them", "i turned the role back on and people still cannot approve anything", "re-enabling the role gave nobody their access back", "the new record refuses to be created in the state i asked for"]
product: frappe
---

# Transitions

## paths

frappe/model/workflow.py — get_transitions, is_transition_condition_satisfied, get_workflow_safe_globals, apply_workflow, validate_workflow, has_approval_access, get_common_transition_actions, bulk_workflow_approval
frappe/model/document.py — _validate, validate_workflow
frappe/permissions.py — get_roles
frappe/core/doctype/role/role.py — validate, disable_role, remove_roles
frappe/workflow/doctype/workflow_transition/workflow_transition.json — state, action, next_state, allowed, allow_self_approval, condition, send_email_to_creator
frappe/public/js/frappe/form/workflow.js — show_actions, has_approval_access, setup_btn

## rules

MUST express segregation of duties as a transition condition, because the condition is evaluated on both the action path and the save path while has_approval_access is called only from apply_workflow.
NEVER read allow_self_approval as a refusal the document itself enforces; it refuses the action item and the emailed action link, and it refuses nothing on save.
MUST expect a WorkflowPermissionError from a save that ignores permissions; ignore_permissions is not read by validate_workflow, whose only escape is frappe.flags.in_install set to frappe.
MUST set owner, and whatever requester field the condition reads, to another user before a seeding script calls apply_workflow, because a condition comparing frappe.session.user to doc.owner excludes the account that inserted the row.
NEVER test a transition as Administrator; get_roles returns every Role name for Administrator with no disabled filter, and has_approval_access waves Administrator past self-approval.
MUST re-grant a Role to each user after clearing its disabled box, because disable_role deletes every Has Role row naming it and re-enabling restores none.
MUST read Not a valid Workflow Action as a transition missing from the candidate list, and MUST look at the role first and the condition second; the message names neither.
MUST keep a condition inside safe_eval's globals — frappe.db.get_value, frappe.db.get_list, frappe.session and the four frappe.utils date helpers — and MUST reach every other value through doc.
MUST expect a transition to a state other than the first to be refused on an insert, because validate_workflow throws when there is no _doc_before_save to derive candidates from.

## values

candidate filter: transition.state equals the current state, transition.allowed is in frappe.get_roles(), condition is true
self-approval check: apply_workflow only
condition check: apply_workflow and validate_workflow
role check: apply_workflow and validate_workflow
allow_self_approval default: 1
send_email_to_creator default: 0
apply_workflow refusals: Not a valid Workflow Action, Self approval is not allowed, Illegal Document Status
save refusal: Workflow State transition not allowed from {0} to {1}
bulk_workflow_approval: under 20 inline, up to 500 enqueued on the short queue, above 500 refused

## how

Two entry points drive a transition and they do not check the same things. `apply_workflow` — the desk action item, the emailed link, bulk approval — finds the transition by its action name, then calls `has_approval_access`. The save path reaches `validate_workflow` from `_validate`, rebuilds the candidate list from the document as it was before the save, and accepts the new state if any candidate carries it as `next_state`. Nothing on that path asks who the owner is.

So the question to ask of any rule you are about to encode is which of the two paths must enforce it. A rule written as `allow_self_approval` holds only where a user presses the button. The same rule written as a condition holds everywhere, because both paths build their candidates through `get_transitions`, and `get_transitions` drops a row whose condition is false before either caller sees it.

The candidate list is also where a role failure disappears. `get_transitions` keeps a row only when `transition.allowed` is among the session user's roles, and an ordinary user's roles come from `Has Role`. Anything that empties those rows — disabling the Role is the destructive one — removes the row from the list rather than raising anything that names the role. Administrator is exempt from both the role source and the self-approval check, which is why a workflow tested under Administrator can be dead for every other user.

A condition is a `safe_eval` string with a deliberately small world. Write it against `doc` and the session; a condition that needs a value the globals do not reach is a condition that belongs in a field the document already carries.
