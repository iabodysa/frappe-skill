---
name: onboarding-step
description: A step is completed by the browser announcing it rather than by the framework observing the work, and update_onboarding_step is whitelisted with no role check and no field allowlist.
triggers: ["Onboarding Step", "update_onboarding_step", "get_onboarding_steps", "is_complete", "is_skipped", "value_to_validate", "validate_action", "show_full_form", "show_form_tour", "reference_document", "action_label", "intro_video_url", "callback_message", "Create Entry", "Update Settings", "Show Form Tour", "View Report", "Go to Page", "Watch Video", "mark_complete", "skip_step", "activate_next_step", "get_first_document", "onboarding step not completing", "Looks like you didn't change the value", "the setup step never marks itself as done", "why does my onboarding step stay unfinished after i did the work", "the step got ticked off even though i did nothing", "the checklist marks itself complete the second i click that is useless", "any user can mark the whole setup checklist as finished", "how do i make a setup step complete only when the value is really changed", "it says i did not change the value but i did", "the guided walkthrough does not start on that step", "skipping a step counts it as done", "the step will not complete until i submit the document", "the setup steps are walked in the wrong order", "how do i reset a setup step that is already ticked"]
product: frappe
---

# Onboarding Step

## paths

frappe/desk/doctype/onboarding_step/onboarding_step.py — OnboardingStep.before_export, get_onboarding_steps
frappe/desk/doctype/onboarding_step/onboarding_step.json — action, reference_document, is_single, show_full_form, show_form_tour, form_tour, validate_action, field, value_to_validate, path, callback_title, callback_message, reference_report, report_type, report_description, video_url, intro_video_url, action_label, is_complete, is_skipped
frappe/desk/desktop.py — update_onboarding_step, get_onboarding_steps
frappe/public/js/frappe/widgets/onboarding_widget.js — show_step, mark_complete, skip_step, update_step_status, activate_next_step, create_entry, show_quick_entry, update_settings, show_form_tour, open_report, go_to_page, show_video, get_first_document
frappe/public/js/frappe/form/form_tour.js — init

## rules

NEVER put anything worth protecting on an Onboarding Step: `update_onboarding_step` is `@frappe.whitelist()` with no role check, no permission check and no field allowlist, so any logged-in user can set any field on any step by name.
MUST read every action but Update Settings as completing on NAVIGATION rather than on work done — Go to Page marks the step complete before the route resolves, Watch Video marks it as the player opens, and View Report marks it when the dialog closes however it closes.
MUST use Update Settings for a step that has to be earned; its `after_save` hook is the only comparison the DocType makes, matching `frm.doc[field]` against `value_to_validate`, with `%` standing for any non-empty value.
MUST expect a failed Update Settings comparison to offer Skip Step, which writes `is_skipped`, which the parent counts as complete.
MUST name the Form Tour exactly the reference DocType for an action of `Show Form Tour`, because the `form_tour` link is hidden unless the action is Create Entry with `show_full_form`, and `FormTour.init` with an empty tour name looks up a Form Tour named for the DocType and then falls back to `frappe.tour[doctype]`.
MUST expect a Create Entry step on a submittable DocType to complete only after submit: `get_onboarding_steps` attaches `is_submittable` from the DocType and the widget moves the callback from `after_save` to `after_submit`.
MUST create a Form Tour whose `reference_doctype` is the step's reference document before setting `show_full_form`, because `create_entry` calls `get_first_document`, which reads `first_document` off a Form Tour filtered on that DocType, to decide between the oldest existing record and `new`.
MUST order the steps table in the order they are to be walked; the widget opens the first step that is neither complete nor skipped, advances by index, and falls back to index 0 when none is pending.
MUST write `path` as a Desk route fragment for Go to Page — the field's own example is `#Tree/Account` — and MUST set `callback_title` and `callback_message`, because the default dialog says only that the user may continue.
MUST expect `action_label` to replace the action name on the button, and `intro_video_url` to replace that button entirely with Watch Tutorial until the viewer presses through.
MUST re-export a step through its parent Module Onboarding rather than alone; the record has no module field, and `before_export` zeroes both `is_complete` and `is_skipped` in the file.

## values

| action | what marks it complete |
|---|---|
| Create Entry, quick entry | the quick entry dialog saves |
| Create Entry, show_full_form, not submittable | after_save |
| Create Entry, show_full_form, submittable | after_submit |
| Update Settings | after_save AND the field matches value_to_validate |
| Show Form Tour | the tour's last step, then the Continue dialog |
| View Report | the dialog shown after routing to the report, on any close |
| Go to Page | immediately, before the route resolves |
| Watch Video | immediately, as the player opens |

`%` in value_to_validate: any non-empty value
Skip: writes is_skipped, counted as complete by the parent
step status written by: the browser, through update_onboarding_step
step status stored on: the shipped Onboarding Step row, one value for the whole site

## how

Read the action field as choosing a client-side script, not a server-side check. Each action is one entry in the `actions` map in `show_step`, and each of those routes away, installs `frappe.route_hooks`, and calls `mark_complete` at whatever moment its own flow reaches. Nothing on the server confirms a document was created, a page was read or a video was watched. A step therefore measures that a user pressed a button, and the onboarding is a guided tour rather than a check on the work.

Update Settings is the exception and the way it differs matters. It routes to the Single, scrolls to the field, marks the form dirty so the save button lives, and only in `after_save` compares the value. Three comparisons run and any one passing is enough — the literal `%` against a truthy value, direct equality, and `cstr` equality — so a Check field validated against `1` passes as `"1"`. On a miss the user is offered Go Back or Skip Step, and skipping counts toward the parent's completion, so a validated step still cannot force the work.

The Form Tour link is where this breaks. `show_form_tour` and the `form_tour` link both depend on the action being Create Entry with the full form shown, so selecting the action `Show Form Tour` leaves no way to name a tour on the form at all. The step then calls `frm.tour.init({tour_name: undefined})`, which asks whether a Form Tour named exactly the reference DocType exists. Name the tour after the DocType and the step works; name it anything else and the step routes to a blank new form with no tour and no error.

`update_onboarding_step` is the one endpoint the DocType exposes and it takes `name`, `field` and `value` and passes them to `frappe.db.set_value` unchecked. It is not `allow_guest`, so a session is required, but no role is. Treat every field on an Onboarding Step as writable by any logged-in user, and treat the step's completion state as advisory.
