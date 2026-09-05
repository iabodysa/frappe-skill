---
name: setup-wizard
description: setup_complete is a bare whitelisted call that runs once per site and returns ok instead of refusing when the site is already set up.
triggers: ["setup_complete", "get_setup_stages", "process_setup_stages", "initialize_system_settings_and_user", "enable_setup_wizard_complete", "get_setup_wizard_completed_apps", "get_stages_hooks", "get_setup_complete_hooks", "run_post_setup_complete", "run_setup_success", "handle_setup_exception", "update_global_settings", "update_system_settings", "create_or_update_user", "disable_future_access", "setup_wizard_complete", "setup_wizard_exception", "trigger_site_setup_in_background", "setup_task", "Updating global settings", "Failed to update global settings", "Wrapping up", "Failed to complete setup", "setup wizard", "setup wizard stuck", "rerun the setup wizard", "site already set up", "run something once per site", "the initial setup screen is stuck and never finishes", "why can i run the first time setup again on a site that is already done", "how do i redo the first time setup on this site", "the setup said everything is fine but half the starting data is missing", "one app got its starting data and the other one did not", "the landing page changed by itself after setup", "how do i run something exactly once when a new site is created", "a normal user was able to trigger the whole site setup", "my seed data script wiped the cache and moved the home page", "the setup finished with a green message but nothing was created"]
product: frappe
---

# Setup wizard

## paths

frappe/desk/page/setup_wizard/setup_wizard.py — setup_complete, get_setup_stages, enable_setup_wizard_complete, initialize_system_settings_and_user
frappe/desk/page/setup_wizard/install_fixtures.py
frappe/core/doctype/installed_applications/installed_applications.py — get_setup_wizard_completed_apps

## rules

MUST expect `setup_complete` to carry `@frappe.whitelist()` with no `only_for` and no Administrator check in its body, so it runs as whoever calls it. MUST expect a second call on a site already set up to return a plain ok rather than refuse, so a caller cannot tell a real run from a no-op by the response. MUST expect the stages to be skipped per app: an app already listed as completed has its stage passed over, so a re-run does not repeat what one app did while another still runs. MUST write anything a site needs at first boot into a `setup_wizard_complete` hook, and expect the failure path to reach `setup_wizard_exception` instead. NEVER treat the wizard as a place to enforce a permission; it runs before the roles a permission would rest on exist. NEVER call `setup_complete` from a patch or a test to seed a site; it is the browser's entry point and it clears the cache and rewrites the home page as a side effect.

## values

entry: setup_complete, whitelisted, no only_for
already complete: returns status ok
per-app skip: get_setup_wizard_completed_apps
background: trigger_site_setup_in_background in the site config
success hook: setup_wizard_complete
failure hook: setup_wizard_exception
side effects: home page set to desktop, cache cleared

## how

The wizard is a browser flow that happens to be a whitelisted endpoint, and every surprise it causes comes from reading it as the second thing rather than the first. It has no check of its own, it is idempotent by returning rather than by refusing, and it fires hooks other apps hang work on.

So when a site comes up wrong, the question is not what the wizard did but which app's stage ran and which was skipped, because the skip is per app and silent. And when work has to happen once per site, hang it on the hook rather than calling the entry point, since the entry point also moves the home page and drops the cache on its way past.
