---
name: install-app
description: The app is committed to installed_apps before a single one of its hooks has run and nothing wraps the sequence, and the uninstall's only automatic cleanup is the doctypes carrying a Link field to Module Def.
triggers: ["install_app", "add_to_installed_apps", "post_install", "remove_app", "_delete_modules", "_delete_doctypes", "_get_module_linked_doctype_field_map", "remove_from_installed_apps", "add_module_defs", "set_all_patches_as_completed", "uninstall_app", "bench install-app order of operations", "install an app on a site", "the app shows as installed but none of its data was created", "the install crashed partway and now it refuses to install again saying it is already there", "furious that a failed install left the site in a state i cannot repair or repeat", "how do i recover a site where the app is listed but its setup never finished", "roles and permissions from the app stayed behind after i removed it", "why does uninstalling leave rows and grants all over the site", "after removing the app there are leftover fields pointing at things that no longer exist", "the removal reported success but clearly cleaned nothing up", "i need the setup data to survive a failure where should i put it instead of the install step", "a required companion app was missing and the install blew up", "the install stopped without any message and nothing was created"]
product: frappe
---

# Install app

## paths

frappe/installer.py — install_app, add_to_installed_apps, post_install, remove_app, _delete_modules, _delete_doctypes, _get_module_linked_doctype_field_map, remove_from_installed_apps, add_module_defs, set_all_patches_as_completed
frappe/commands/site.py — install_app, uninstall_app

## rules

MUST expect the app to be recorded as installed before any of its hooks run. add_to_installed_apps writes the installed_apps global and commits immediately, and after_install, after_app_install, sync_jobs, sync_fixtures, sync_customizations, sync_dashboards and after_sync all run afterwards with nothing wrapping them.
MUST expect a hook that throws to leave the site reporting the app present while its seed data, fixtures and customizations are partly or entirely absent, and a second bench install-app to refuse because the name is already in the list.
NEVER put anything a site cannot function without in an after_install seeder; a patch, which is stamped only on completion, and an after_migrate step, which can be re-run, both survive a mid-run failure in a way install does not.
MUST expect required_apps in hooks to install recursively before the app itself, and an app absent from apps.txt to raise.
MUST expect frappe.only_for("System Manager") on every app but frappe, and a before_install hook returning False to abandon the install silently.
MUST declare before_uninstall and delete an app's own rows there. remove_app's only automatic cleanup scans DocField for a Link field whose options are Module Def and deletes rows of the doctypes that have one, so Role, Role Profile, Module Profile and Custom DocPerm survive the uninstall permanently.
NEVER read a successful uninstall as evidence the hook ran; an absent before_uninstall makes the loop iterate an empty list and report success.
MUST give a Custom Field a module key. A field written without one gets no module from the sync and no default from db_insert, so it survives the uninstall and can be left pointing at a DocType the same run deleted.
MUST read the DocType cascade as not rescuing this: deleting a DocType removes its Custom DocPerm rows, and the doctypes an app writes permissions ONTO belong to other modules and are not deleted.

## values

install order: required_apps, before_install, before_app_install, add_module_defs, sync_for, add_to_installed_apps, Portal Settings sync_menu, set_all_patches_as_completed, after_install, after_app_install, sync_jobs, sync_fixtures, sync_customizations, sync_dashboards, after_sync
commit point: inside add_to_installed_apps, before every hook that follows
uninstall cleanup: doctypes with a Link field whose options are Module Def
uninstall survivors: Role, Role Profile, Module Profile, Custom DocPerm, a module-less Custom Field
uninstall hooks: before_uninstall, before_app_uninstall, after_uninstall, after_app_uninstall

## how

Install is the one lifecycle the framework declined to make atomic. The primitive exists — the migrate
run wraps each phase in a commit-or-rollback decorator — and install does not use it, so a failure
there leaves a state no command produces and no command repairs. Read the ordering as the real
contract: everything the app needs is written after the point of no return.

Uninstall is a Module Def scan and nothing more. The mental model "the app is removed" is wrong; what
is removed is the doctypes the app owns and the rows that point at its modules. Anything the app wrote
onto someone else's doctype — a grant, a role, a profile — is the app's own job to take back, and the
place to declare that is before_uninstall.
