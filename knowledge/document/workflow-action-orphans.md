---
name: workflow-action-orphans
description: process_workflow_actions is the only native path that clears a Workflow Action row, it fires from the document lifecycle alone, and Log Settings carries no entry for the doctype, so a state change made outside the lifecycle or a hard delete leaves a stale Open row nothing native ever clears.
triggers: ["process_workflow_actions", "is_workflow_action_already_created", "clear_workflow_actions", "update_completed_workflow_actions", "LogSettings", "Workflow Action", "Log Settings", "workflow action row not cleared", "stale workflow action", "people still see approval requests for documents that were already finished", "old pending approvals never disappear from the list", "why are there approval items sitting there for documents that are long closed", "i changed the status directly in the database and the pending approval stayed open", "after a data import all the old approval requests are still waiting", "turning the approval flow off left everyone with stale pending items", "the document was deleted and its approval request is still listed", "the log cleanup never removes these leftover approval rows", "how do i clean up approval requests nothing ever clears", "the approval request is not created again when the document comes back to the same step", "marking the old rows as done blocked the new approval from appearing"]
product: frappe
---

# Workflow Action orphans

## paths

frappe/workflow/doctype/workflow_action/workflow_action.py — process_workflow_actions, is_workflow_action_already_created, clear_workflow_actions, update_completed_workflow_actions
frappe/core/doctype/log_settings/log_settings.py — LogSettings

## rules

MUST expect `process_workflow_actions` to be the only native maintenance path for `Workflow Action`; it clears rows on `on_trash` and updates completed rows on a state change through the document lifecycle only.
MUST expect a `Workflow Action` row to orphan when the document's state changes by a direct database write, a data import, or a workflow that was deactivated, because none of those routes fires the document lifecycle `process_workflow_actions` hangs off, and it stays orphaned when the document is hard-deleted without `on_trash`.
NEVER expect `Log Settings` or `clear_old_logs` to reach `Workflow Action`; the doctype carries no entry there.
MUST scope an app's own cleanup job to `status = 'Open'` rows only, and MUST delete rather than mark them Completed, because `is_workflow_action_already_created` filters on no status and a Completed row would block re-creating an Open one when a cyclic workflow re-enters the same state.

## how

Every native cleanup is wired to a lifecycle event, and every orphan case is a write that bypassed the lifecycle — the two are the same fact seen from either side, which is why an app's own cleanup job is a justified addition rather than a duplicate of something the framework already does. `Completed` rows are the audit trail and stay; only `Open` rows are stale by construction, and deleting them is the safe verb because the blocking check that would let a stray Completed row suppress a real re-creation has no status filter to catch it.
