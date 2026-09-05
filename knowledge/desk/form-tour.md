---
name: form-tour
description: One DocType holds two unrelated products — a ui_tour fires on a route stored in page_route that only the browser ever computes, and a plain Form Tour walks the fields of one form and stores no progress at all.
triggers: ["Form Tour", "Form Tour Step", "ui_tour", "page_route", "get_onboarding_ui_tours", "init_onboarding_tour", "OnboardingTour", "FormTour.init", "update_user_status", "reset_tour", "onboarding_status", "track_steps", "save_on_complete", "first_document", "include_name_field", "new_document_form", "element_selector", "parent_element_selector", "next_step_condition", "next_form_tour", "hide_buttons", "next_on_click", "popover_element", "modal_trigger", "frappe.Driver", "tour not starting", "tour shows on wrong page", "reset tour for all users", "the walkthrough pops up on the wrong screen", "after importing the tour it opens on the old page", "why does my guided tour trigger where it should not?", "the tour never starts and there is no error anywhere", "nothing happens when the walkthrough is supposed to begin", "my guided tour is skipped entirely on the dashboard", "half the steps of my walkthrough are missing", "the tour only showed once and i cannot get it back", "how do i make the walkthrough show again for everyone?", "the walkthrough starts from step one again instead of where i left off", "users who should not see the walkthrough are getting it", "one bad walkthrough row breaks login for every user"]
product: frappe
---

# Form Tour

## paths

frappe/desk/doctype/form_tour/form_tour.py — FormTour.before_save, FormTour.on_update, FormTour.on_trash, reset_tour, update_user_status, get_onboarding_ui_tours
frappe/desk/doctype/form_tour/form_tour.json — ui_tour, page_route, view_name, workspace_name, list_name, report_name, dashboard_name, page_name, new_document_form, reference_doctype, is_standard, track_steps, save_on_complete, first_document, include_name_field
frappe/desk/doctype/form_tour_step/form_tour_step.json — element_selector, parent_element_selector, fieldname, parent_fieldname, is_table_field, position, has_next_condition, next_step_condition, next_form_tour, hide_buttons, next_on_click, popover_element, modal_trigger, ondemand_description, offset_x, offset_y
frappe/desk/doctype/form_tour/form_tour.js — get_path, add_custom_button, check_if_private_workspace, get_first_document
frappe/boot.py — get_onboarding_ui_tours
frappe/public/js/frappe/desk.js — startup
frappe/public/js/onboarding_tours/onboarding_tours.js — init_onboarding_tour, init, build_steps, get_step, update_driver_steps, handle_modal_steps
frappe/public/js/frappe/form/form_tour.js — init, build_steps, get_step, include_name_field, add_step_to_save, handle_table_step, handle_child_table_step, is_next_condition_satisfied
frappe/public/js/frappe/form/form.js — setup_std_layout
frappe/core/doctype/user/user.json — onboarding_status

## rules

MUST save a `ui_tour` through the Form Tour form in the Desk, because `page_route` is computed by `get_path` in the client's `before_save` alone; a tour written by a patch, a fixture, a data import or the REST API keeps its old `page_route` and fires on the old screen while every field on the form reads correctly.
NEVER leave a `ui_tour` row with an empty `page_route`: `get_onboarding_ui_tours` runs `json.loads` on every such row while building bootinfo, so one empty value raises for every user logging in.
MUST expect a `ui_tour` to reach every user: `get_onboarding_ui_tours` filters on `ui_tour` alone with `frappe.get_all`, which checks no permission, and it reads nothing about the roles of the screen being toured.
MUST read a step that highlights nothing as dropped rather than failed — `build_steps` pushes a step only when `element_selector` resolves against `cur_page` or the document — and MUST read a tour that never appears as every step dropped, because `start` returns in silence when none survived.
MUST expect the route match to compare at most the first three positions of the route, with `*` accepted in the second or third and `new-*` in the third, so `List/*/Report` matches every report view; and MUST NOT rely on which tour wins when several match, because `get_onboarding_ui_tours` passes no ordering.
NEVER build a `ui_tour` over a Dashboard: `get_path` writes a `dashboard-view` route for it, and `init_onboarding_tour` skips the whole matching loop for a route whose first position is `dashboard-view`, so the tour is stored, shipped and never fired.
MUST reset a `ui_tour` with `reset_tour`, which rewrites `onboarding_status` on every User row and drops each user's bootinfo cache entry; resaving or re-importing the tour does not show it again, because completion lives on the User and not on the tour.
MUST expect any Form Tour save or delete to clear the whole `bootinfo` cache key rather than one user's, so every user's boot is rebuilt afterwards.
MUST name a plain Form Tour exactly the DocType for it to attach to that form on its own; `FormTour.init` with no tour name checks `frappe.db.exists("Form Tour", frm.doctype)` and then falls back to a `frappe.tour[doctype]` array declared in client script.
MUST expect a plain Form Tour to store nothing: only the `ui_tour` path calls `update_user_status`, so a form tour replays for the same user every time it is invoked.
MUST set `is_standard` AND run in `developer_mode` for a tour to be exported into an app; `on_update` exports on both together, and outside developer mode the form of a standard tour is set read-only and its save disabled.
MUST name every step's `fieldname` from the reference DocType when `ui_tour` is 0, because `before_save` reads `label` and `fieldtype` off the meta field and a name that is not on the DocType raises an AttributeError instead of a validation message.
MUST leave the form dirty for `save_on_complete` to add its save step; `build_steps` adds it only when `is_dirty()` is true at build time, so a tour over an already-saved document ends without the save step it promises.
MUST set `track_steps` for a `ui_tour` to resume; without it `init` forces the start index to 0 on every run even though `onboarding_status` still holds the count.
MUST write a `parent_element_selector` beside any `:has()` selector, which the field's own description gives as the Firefox workaround.

## values

| field | ui_tour 1 | ui_tour 0 |
|---|---|---|
| what a step points at | `element_selector`, a CSS selector | `fieldname` on `reference_doctype` |
| what fires it | a route change matching `page_route` | a caller invoking `frm.tour.init` |
| where progress is stored | `User.onboarding_status`, per user | nowhere |
| who resets it | `reset_tour`, System Manager only | not applicable |
| when it is loaded | bootinfo, on every login | on demand, by `frappe.db.get_doc` |

route wildcards: `*` in route position two or three, `new-*` in position three
`query-report/X` is matched as `List/X/Report`
`dashboard-view` routes: never matched
minimum viewport for any ui_tour: 992px device width
skipping a ui_tour: the Skip button writes `is_complete` for that tour on the User, the same as finishing it
`update_user_status`: writes the User with `update_modified=False` and drops that user's bootinfo entry

## how

The `ui_tour` check splits the DocType into two products that share only a steps table. With it set, the record is a Desk tour: `page_route` holds a JSON array compared position by position against the current route, boot hands every such array to the browser, and `init_onboarding_tour` re-runs on every route change to find a match. With it clear, the record is a form walkthrough keyed by fieldname on one DocType, started by something that already holds a `frm`. Half the fields on the form are hidden by `depends_on` on this one check, so a tour built with the wrong value looks complete and does nothing.

`page_route` is the fragile part, because it is derived rather than stored by the server. `get_path` runs in the client `before_save`, reads `view_name` and its dependent link, asks whether the workspace is private, and writes the array. Nothing on the server recomputes it. So the durable rule is that the Desk form is the only supported writer of a ui_tour, and the diagnostic for a tour appearing on the wrong screen is to read `page_route` itself rather than the fields that were meant to produce it.

A ui_tour is loaded for everybody and filtered by nothing but the DOM. `get_onboarding_ui_tours` uses `frappe.get_all`, which skips permissions by design, so the tour list in bootinfo is identical for a System Manager and for a user with one role. What actually stops the tour is that its selectors match no element on that user's screen, in which case the steps are silently dropped and the tour never starts. That is a reasonable outcome and an unreliable control: a tour whose steps happen to match a shared element will run for a user who has no business on that screen, and the popover text is the leak.

Completion is per user and lives on the User record as a JSON blob under `onboarding_status`, written with `update_modified=False` so it does not disturb the row's timestamp, followed by an `hdel` of that user's bootinfo entry so the next boot reflects it. The blob carries `steps_complete`, `is_complete` and `all_steps_completed` per tour name, keyed by the tour's `name`. Renaming a tour therefore orphans everyone's progress and shows it again to the whole site; `reset_tour` is the deliberate way to do that, and it walks every User row.

The plain Form Tour adds steps the author did not write. A `Table` field whose next step is inside it grows an "Add a Row" step or expands the first row; a child-table step grows a Collapse step; an `Attach Image` step grows a step over the upload modal; `include_name_field` unshifts a Document Name step; and `save_on_complete` appends a step over the primary action. Step indexes in a tour are therefore not the row indexes in the steps table, which matters for anything that starts a tour at an offset.
