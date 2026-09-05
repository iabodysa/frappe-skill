---
name: list-indicator
description: Four earlier branches answer before a list view's own get_indicator runs, so a custom indicator is skipped whenever a workflow state, a draft, a cancelled document or a declared DocType State matches.
triggers: ["get_indicator", "has_indicator", "set_fields", "get_indicator_html", "get_indicator_dot", "set_indicator", "frappe-ui list indicator precedence", "custom list indicator skipped", "my custom colour dot in the list is being ignored", "the list keeps showing draft in red instead of my own label", "why does my status colour never appear in the list view", "cancelled records always show the same colour no matter what i do", "the badge in the list does not match the status i set", "how do i make the list show my own status label and colour", "my status colour works on some records and not on others", "after i made the doctype submittable the list badge changed on its own", "clicking the status badge filters by the wrong thing", "the label in the list is stuck in english and will not translate", "my colour function gets an empty value for a field that clearly has data", "the field my status logic reads is always empty in the list but fine on the form"]
product: frappe
---

# The list indicator

## paths

frappe/public/js/frappe/model/indicator.js — get_indicator, has_indicator
frappe/public/js/frappe/list/list_view.js — set_fields, get_indicator_html, get_indicator_dot
frappe/public/js/frappe/form/toolbar.js — set_indicator

## rules

MUST expect the resolver to answer from the first branch that matches, in this order: an unsaved document, a workflow state, a draft of a submittable DocType, a cancelled one, a `status` matching a declared DocType State, and only then the list view's own `get_indicator`.
MUST expect a custom `get_indicator` to be skipped entirely on a submittable DocType whose document is a draft or cancelled, and on any DocType that declares a State whose title equals the document's status.
MUST set `has_indicator_for_draft` or `has_indicator_for_cancelled` in the list view settings for the custom function to be reached on those documents.
MUST expect the resolver to fall through past a custom function that returns nothing, to the submitted, status, enabled and disabled branches in that order.
MUST return a label, a colour and a filter string from `get_indicator`, since clicking the indicator applies that filter to the list.
MUST wrap the label so it translates, because the framework's own branches translate theirs against the DocType.
MUST name in `add_fields` every field the indicator reads, because the list query fetches the standard fields, the fields in the list view, the title and image fields, the sort field and this list — and nothing else.
MUST expect a field the indicator reads and `add_fields` omits to arrive undefined, so the function silently takes its else branch.
MUST expect the workflow branch to be skipped where the workflow overrides the status and the caller did not ask for the workflow state, and where the state is in the avoid-override list.

## values

filter string form: `fieldname,=,value`
branch order: unsaved, workflow state, draft, cancelled, DocType State by status, list view get_indicator, submitted, status, enabled, disabled
draft: red, filter on docstatus 0
cancelled: red, filter on docstatus 2
submitted: blue, filter on docstatus 1
settings that reopen a branch: has_indicator_for_draft, has_indicator_for_cancelled
query fields: standard fields, the list view fields, title and image fields, add_fields, the sort field, enabled, disabled, color, and _seen when the DocType tracks seen

## how

The custom function is a late fallback, not an override. It reads as the definition of the indicator because it is the only part an application writes, but four framework branches answer ahead of it, and each of them is a shape an application acquires by accident — making a DocType submittable, or declaring States on it, turns the custom indicator off for most of its documents without a message.

So decide the indicator at the metadata level first. A DocType with declared States needs no function at all, and a submittable one needs the two settings before its function is reached. Then check `add_fields` against every field the function touches: the query is an explicit list, and a field missing from it reaches the function as undefined rather than as an error.
