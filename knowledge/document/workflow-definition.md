---
name: workflow-definition
description: Saving a Workflow record with is_active=1 deactivates every other Workflow for the same document_type via a raw UPDATE from any save path, and its child rows are mandatory Links that must already exist.
triggers: ["Workflow.set_active", "saving a Workflow disabled another one", "is_active workflow", "two active workflows on the same doctype", "create_custom_field_for_workflow_state", "update_default_workflow_status", "Workflow Document State reqd", "Workflow Transition reqd", "inserting a Workflow fails because the state does not exist", "workflow insert from a script deactivated the other workflow"]
product: frappe
---

# Workflow definition

## paths

frappe/workflow/doctype/workflow/workflow.py — Workflow.set_active, Workflow.on_update, Workflow.create_custom_field_for_workflow_state, Workflow.update_default_workflow_status
frappe/workflow/doctype/workflow_document_state/workflow_document_state.json — state
frappe/workflow/doctype/workflow_transition/workflow_transition.json — action, state, next_state, allowed
frappe/workflow/doctype/workflow_state/workflow_state.json — workflow_state_name
frappe/workflow/doctype/workflow_action_master/workflow_action_master.json — workflow_action_name

## rules

MUST expect `set_active` to run `UPDATE tabWorkflow SET is_active=0 WHERE document_type=%s` unconditionally whenever a Workflow with `is_active` truthy is saved.
MUST expect that UPDATE to fire from ANY save path, including `insert()` called from a script or a migration, not only from the Desk form.
MUST expect `on_update` to also call `create_custom_field_for_workflow_state` (adds a hidden Custom Field for the configured workflow-state fieldname when one is missing) and `update_default_workflow_status` (a raw UPDATE backfilling empty state columns) on every save.
MUST create the referenced Workflow State, Workflow Action Master and Role rows before inserting a Workflow; `Workflow Document State.state` and `Workflow Transition.action`/`state`/`next_state`/`allowed` are `reqd` Links and the insert fails when the referenced row does not exist.
MUST supply only `workflow_state_name` on a placeholder Workflow State and only `workflow_action_name` on a placeholder Workflow Action Master to unblock a Workflow insert; those are the only `reqd` fields on the two masters, and icon or style properties can arrive on a later save.

## how

A Workflow is not an inert configuration row: saving one with `is_active` on reaches into every sibling Workflow for the same `document_type` and turns it off by direct SQL, and the same save also mutates a Custom Field and backfills a status column — none of it gated on the save coming from the Desk. Seeding a Workflow by script therefore needs its masters created first and needs to expect the deactivation side effect on every insert, not only on a form save.
