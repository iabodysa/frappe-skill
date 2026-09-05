---
name: module-onboarding
description: Onboarding progress is stored on the shipped records themselves, so the first user who finishes a step retires that onboarding for the whole site, and a migrate that carries a newer JSON brings it back.
triggers: ["Module Onboarding", "ModuleOnboarding.check_completion", "ModuleOnboarding.mark_as_completed", "ModuleOnboarding.get_allowed_roles", "ModuleOnboarding.get_steps", "reset_progress", "reset_onboarding", "before_export", "get_onboarding_doc", "get_onboardings", "enable_onboarding", "allow_roles", "onboarding_list", "Onboarding Step Map", "onboarding widget not showing", "onboarding disappeared", "dismissed-onboarding", "Let's Get Started", "onboarding block workspace", "IMPORTABLE_DOCTYPES", "the getting started checklist never appears on the page", "why is the setup checklist missing for everyone", "how do i bring back the getting started steps", "one person clicked through the steps and now nobody else sees them", "the checklist disappeared for the whole company after a colleague finished it", "the steps came back after an update even though we had finished them", "why did our completed setup steps reset themselves", "the checklist is gone on my machine but my colleague still sees it", "it vanished for a day and then came back on its own", "only some users can see the setup steps and others cannot", "i marked the steps done but the database still says not finished", "how do i reset the getting started steps for the site"]
product: frappe
---

# Module Onboarding

## paths

frappe/desk/doctype/module_onboarding/module_onboarding.py — ModuleOnboarding.on_update, ModuleOnboarding.get_steps, ModuleOnboarding.get_allowed_roles, ModuleOnboarding.check_completion, ModuleOnboarding.mark_as_completed, ModuleOnboarding.reset_progress, ModuleOnboarding.before_export, ModuleOnboarding.reset_onboarding
frappe/desk/doctype/module_onboarding/module_onboarding.json — module, allow_roles, steps, is_complete, success_message, documentation_url
frappe/desk/doctype/onboarding_step_map/onboarding_step_map.json — step
frappe/desk/desktop.py — get_onboarding_doc, get_onboardings, get_onboarding_steps, update_onboarding_step
frappe/model/sync.py — IMPORTABLE_DOCTYPES, sync_all, sync_for, get_doc_files
frappe/modules/import_file.py — import_file_by_path, calculate_hash
frappe/modules/export_file.py — export_to_files, write_document_file
frappe/public/js/frappe/widgets/onboarding_widget.js — get_onboarding_data, make_body, is_dismissed, set_actions, show_success
frappe/desk/page/setup_wizard/setup_wizard.py — enable_onboarding

## rules

MUST read `is_complete` as SITE state and never as user state, on the parent and on every step alike: the widget writes the shipped record, so the first user who finishes a step hides the onboarding from everyone else on the site.
MUST add a Workspace content block of type `onboarding` naming the record, because `onboarding_list` is built only from those blocks and `get_onboardings` returns an empty list without one; no route, no permission and no log reports the absence.
MUST set `enable_onboarding` in System Settings, which the setup wizard sets on completion; `get_onboarding_doc` returns None before it reads anything else.
MUST list in `allow_roles` every role that should see the onboarding — the table is `reqd`, so unlike a Workspace it cannot ship open — and MUST expect System Manager to see it whether listed or not, because `get_allowed_roles` appends that role.
NEVER read `check_completion` returning True as proof the database was written: it flips `is_complete` in memory and enqueues `mark_as_completed` with `enqueue_after_commit`, so a worker that never runs leaves the row at 0 while the reader was already told the module is done.
MUST count a skipped step as a finished one; `check_completion` tests `is_complete or is_skipped`, so a user who presses Skip on every step retires the onboarding for the site.
MUST keep `module` pointing at the module whose folder is to hold the JSON, because `on_update` exports the parent AND every step named in the steps table into that module with `record_module`, and Onboarding Step carries no module of its own.
MUST expect a `bench migrate` to wipe progress whenever the shipped JSON's `modified` is newer than the row's: `import_file_by_path` skips a non-DocType record only while the database timestamp is at or after the file's, and `before_export` zeroes `is_complete` in the file.
MUST read completing a step as the thing that protects progress from the next migrate — `update_onboarding_step` bumps `modified` — so a site that finished the onboarding keeps it finished until a newer file overtakes that timestamp.
MUST clear progress through `reset_progress`, the whitelisted method the form button calls; `reset_onboarding` is wired to nothing and calls `frappe.only_for("Administrator")`.
MUST read a user reporting the onboarding "gone for a day" as the browser: Dismiss writes the title into the `dismissed-onboarding` localStorage key and `is_dismissed` hides the widget for 24 hours, on that browser only, with no server record.

## values

enabled by: System Settings `enable_onboarding`
rendered by: a Workspace content block of type `onboarding` naming this record
restricted by: `allow_roles` intersected with `frappe.get_roles()`, System Manager always added
completion scope: the site — `is_complete` on the shipped records
dismiss scope: one browser, 24 hours — localStorage key `dismissed-onboarding`
export trigger: `developer_mode` and any save; writes the parent and every step
migrate re-import: a file whose `modified` is newer than the row's, and `is_complete` in that file is 0
success screen: shown when no step is left pending, then Continue deletes the widget

## how

Module Onboarding is one record type shipped in an app folder and mutated in place on the site. There is no per-user progress table anywhere: the widget calls `update_onboarding_step`, which sets the field on the Onboarding Step row, and `get_onboarding_doc` reads `is_complete` off the Module Onboarding row before it decides to render. So onboarding is a property of the site, and the second user to open the Workspace sees whatever the first user left. Anything that must be per-person belongs in a UI tour instead, which stores its progress on the User.

Four independent checks stand between a shipped Module Onboarding and a rendered widget, and three of them fail without a word. The System Settings flag, the `onboarding` block in the Workspace content, the role intersection, and completion. Diagnose by which users see nothing: everyone means the flag or the missing block; one role means `allow_roles`; everyone after one person clicked through means completion. Only the last is recoverable from the Desk, through the Reset button on the Module Onboarding form.

Migrate is the other writer. `module_onboarding`, `onboarding_step` and `form_tour` are all in `IMPORTABLE_DOCTYPES`, so every migrate walks each module folder and re-imports any of these whose file timestamp is newer than the row. The exported file always carries `is_complete: 0`, because `before_export` zeroes it. The consequence is that touching an onboarding JSON in a released app re-opens the onboarding on every site that had already finished it — the file wins, and the user's finished checklist reappears. Ship a changed step only when the module is meant to be walked again.

The steps table is a link table, not an embed. `Onboarding Step Map` holds one Link per row and `get_steps` loads each Onboarding Step as its own document, so two Module Onboarding records that name the same step share its completion. Give each module its own steps unless that sharing is the intent.
