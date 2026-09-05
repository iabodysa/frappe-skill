---
name: standard-json
description: A record shipped as module JSON is imported only when its folder name is one of the nineteen IMPORTABLE_DOCTYPES entries, and once a site has touched the record the skip condition keeps the file out forever.
triggers: ["sync_all", "sync_for", "get_doc_files", "IMPORTABLE_DOCTYPES", "remove_orphan_doctypes", "import_file_by_path", "import_doc", "ignore_values", "calculate_hash", "sync_dashboards", "make_records_in_module", "make_records", "export_doc", "export_to_files", "Only allowed to export customizations in developer mode", "ship a doctype record as json", "importable doctypes list", "my json file is never picked up on the site and nothing complains", "why is the record in the folder not being created when i update", "the export wrote the file fine but nothing imports it", "i changed the shipped file and the site still has the old version", "an updated record does not reach sites where someone opened it", "why does my edit only land on brand new sites", "the chart i shipped never updates on existing installs", "i turned a shipped item back on in the file and it stays off on the site", "the disabled flag will not go back to enabled no matter what i ship", "how do i push a change to a record customers may have edited", "one field on the record updated and another one did not in the same run", "the approval flow i exported is not showing up on other sites"]
product: frappe
---

# Standard JSON

## paths

frappe/model/sync.py — sync_all, sync_for, get_doc_files, IMPORTABLE_DOCTYPES, remove_orphan_doctypes
frappe/modules/import_file.py — import_file_by_path, import_doc, ignore_values, calculate_hash
frappe/utils/dashboard.py — sync_dashboards, make_records_in_module, make_records
frappe/modules/utils.py — export_doc, export_to_files

## rules

MUST check the record's folder name against IMPORTABLE_DOCTYPES before shipping it as is_standard module JSON. get_doc_files walks only those folder names under each module and nothing else, so a JSON under any other folder is never opened.
MUST ship a Workflow as a create-only seed patch. It is not on the list however it was exported, and the patch also gives the DocType-existence check and the master-before-parent ordering a fixture cannot.
MUST ship a Dashboard, a Dashboard Chart or a Number Card through the module's dashboard folders, which sync_dashboards walks as a separate step; they are not on IMPORTABLE_DOCTYPES and the framework's own apps reach them this way.
MUST seed a Kanban Board; it carries no is_standard field at all, so it cannot even be exported.
NEVER read a successful export as evidence an import exists. In developer_mode, saving a Workflow with is_standard 1 runs export_to_files and writes a correct JSON into the module folder, and get_doc_files never opens it — nothing raises and nothing warns.
NEVER trust sync_dashboards to overwrite what its own docstring says it overwrites. make_records calls import_file_by_path with no force flag, so every dashboard file takes the ordinary skip condition and a chart an operator has touched is never updated by any run.
MUST read the two skip conditions as applying to different doctypes. Without force and with the row already present, a DocType is skipped when its stored migration_hash equals the calculated hash, and every OTHER doctype is skipped when its database modified is at or after the file's modified.
MUST make the file's modified strictly newer to land a change on a site whose row is newer; that, and not force or a hand edit on the site, is the fix.
MUST ship a change to a record an operator may have saved as a PATCH. Saving a shipped record in the UI bumps modified, so a hand-disabled Notification, a renamed Workspace shortcut or an edited Print Format survives with no app-side mechanism, and a JSON bump never reaches that site.
NEVER read the DocType exception as unconditional: a hand-edited DocType survives every run that does not change its shipped JSON, and is overwritten on the release that changes any byte.
MUST change enabled, disabled, is_hidden, is_complete or is_skipped on a shipped record through a patch that lifts only rows still carrying the shipped state. ignore_values names those fields per doctype and they are NEVER copied onto a record that already exists, whatever the timestamp says.
MUST query a NEIGHBOURING field to expose that exclusion rather than the field that was changed; a sibling field on the same record moves in the same run while the excluded one stays.

## values

IMPORTABLE_DOCTYPES: doctype, page, report, dashboard_chart_source, print_format, web_page, website_theme, web_form, web_template, notification, print_style, workspace, onboarding_step, module_onboarding, form_tour, client_script, server_script, custom_field, property_setter
not on the list: Workflow, Dashboard, Dashboard Chart, Number Card, Kanban Board
ignore_values: Report disabled prepared_report add_total_row, Print Format disabled, Notification enabled, Print Style disabled, Module Onboarding is_complete, Onboarding Step is_complete is_skipped, Workspace is_hidden
hash condition: DocType only, on the migration_hash field
timestamp condition: every doctype but DocType
sync_for: one commit per file

## how

Shipping a record as module JSON is governed by a LIST, not by a rule, so nothing about a record's
shape tells you whether it will be imported and the failure is silence. Check the folder name first;
the export half works for records the import half never reads, which is exactly the shape that reads as
working when it is not.

The conditions answer a question people rarely ask: whose value is authoritative once a site has touched the
record. The answer is the site's, permanently, and no amount of editing the file changes it. That makes
the JSON the mechanism for shipping a record and never for changing one, and a patch the mechanism for
changing it.

Read ignore_values as a second, independent decision. The timestamp settles whether the RECORD is
re-imported; ignore_values settles which FIELDS are excluded when it is. Those are the fields an
operator uses to turn a shipped thing off, and the framework refuses to turn it back on for them.
