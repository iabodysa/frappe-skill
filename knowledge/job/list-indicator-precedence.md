---
name: list-indicator-precedence
description: frappe.get_indicator returns at the first of seven branches that matches, and a DocType State sits ahead of listview_settings.get_indicator but behind the docstatus-driven Draft and Cancelled branches.
triggers: ["get_indicator", "avoid_status_override", "title", "color", "custom", "Doctype State", "list view indicator color", "get_indicator precedence", "the colour of the status dot in the list is wrong", "my custom status colour is ignored in the list view", "why does every row show draft instead of my own status", "the list still shows cancelled even though i set a colour for that status", "my javascript that sets the row colour never runs", "how do i control the colour shown next to a record in the list", "the workflow state is showing in the list and i want my own status instead", "i set a colour on the status table but the list ignores it", "why does the coloured label in the list not match the status field", "turning off the status override changed the colour but not the permissions", "how do i stop the workflow from taking over the label in the list"]
product: frappe
---

# List Indicator Precedence

## paths

frappe/public/js/frappe/model/indicator.js — get_indicator
frappe/public/js/frappe/model/workflow.js — avoid_status_override
frappe/core/doctype/doctype_state/doctype_state.json — title, color, custom

## rules

MUST expect frappe.get_indicator to return at the first branch that matches, in order: doc.__unsaved, the workflow state, Draft on docstatus 0, Cancelled on docstatus 2, a DocType State whose title matches doc.status, listview_settings.get_indicator, then Submitted on docstatus 1.
MUST expect a submittable document at docstatus 0 or 2 to never reach the DocType States branch or listview_settings.get_indicator, because Draft and Cancelled are tested first and end the function when they fire.
MUST set has_indicator_for_draft or has_indicator_for_cancelled on listview_settings to let a submittable document at that docstatus reach the later branches at all.
MUST expect a DocType State whose title equals doc.status to shadow frappe.listview_settings[doctype].get_indicator, because states are read one branch earlier and returning there skips the JS hook.
MUST declare a status by DocType State when the rule is "this status is that colour", because the state row gives the translated label, the colour class and the click-through filter for free, with the colour editable on the DocType form.
NEVER expect a DocType State to express a condition beyond doc.status matching by name; it has no condition and its colour is one of a fixed ten, so a status field under another name, or a colour keyed on more than status, needs listview_settings.get_indicator instead.
MUST set avoid_status_override on a Workflow Document State ("Don't Override Status") to stop the workflow branch firing for documents in that state, so the list indicator falls through toward Draft, Cancelled or the DocType's own status field.
NEVER read avoid_status_override as touching anything past display; nothing on the server consults it — workflow.py does not gate on it, workflow_state still transitions, and every permission and transition rule is unchanged.

## values

palette on a DocType State: Blue, Cyan, Gray, Green, Light Blue, Orange, Pink, Purple, Red, Yellow
branch order: __unsaved, workflow state, Draft (docstatus 0), Cancelled (docstatus 2), DocType State on doc.status, listview_settings.get_indicator, Submitted (docstatus 1)
workflow branch fires when: a Workflow exists for the doctype, and workflow.override_status is falsy or show_workflow_state was passed, and doc[workflow_fieldname] is not in that doctype's avoid_status_override list
avoid_status_override source: Workflow Document State rows filtered on avoid_status_override, built once per doctype into frappe.workflow.avoid_status_override

## how

A DocType State is not a fallback sitting below the JS hook, it is upstream of it — the fifth of seven checks the function tries in order, past which nothing later runs. But States sits behind Draft and Cancelled, both keyed on docstatus rather than on doc.status, so a submittable document showing Draft or Cancelled is never consulting its states table at all; that colour comes from docstatus, not from a state row happening to be absent.

avoid_status_override only decides which of the first two branches runs. It is read once into a per-doctype list and nothing after that point in the file, and nothing on the server, consults it again — declaring it changes what colour a list row shows and nothing about what the document may do next.
