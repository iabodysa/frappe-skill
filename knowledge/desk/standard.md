---
name: standard
description: A report saved with a blank is_standard becomes standard for Administrator in developer_mode, writes its JSON and controllers into the app folder, and then refuses deletion wherever developer_mode is off.
triggers: ["validate", "validate_standard_report", "export_doc", "create_report_py", "on_trash", "execute_script_report", "execute_module", "execute_script", "Report", "Cannot edit a standard report. Please duplicate and create a new report", "You are not allowed to delete Standard Report", "Must specify a Query to run", "standard report vs custom report", "developer mode report save", "it will not let me edit my report anymore and says to duplicate it", "why can i not delete this report on the live server", "how do i delete a report that refuses to be deleted", "i changed the report code in the interface and the output did not change", "my edits to the report script are ignored when it runs", "new files showed up in my app folder after i saved a report", "the report turned into a built in one on its own", "why does the report behave differently on my machine and on the server", "the letterhead i picked on the report keeps clearing itself", "saving a report created python and javascript files i did not ask for"]
product: frappe
---

# Standard reports

## paths

frappe/core/doctype/report/report.py — validate, validate_standard_report, export_doc, create_report_py, on_trash, execute_script_report, execute_module, execute_script

## rules

MUST set is_standard on every report save; validate decides a blank one from the session user and developer_mode.
MUST expect on_update to run export_to_files with create_init, writing the report JSON and an __init__.py into the module's app folder, and make_boilerplate to add controller.py and controller.js for a Script Report.
NEVER edit report_script on a standard Script Report; execute_script_report calls execute_module for is_standard Yes, which imports the module on disk, and reaches execute_script only for No.
NEVER rely on the Script Manager check to hold a standard report; frappe.only_for runs on the is_standard No branch alone.
MUST duplicate rather than edit a record already stored as standard, because validate throws "Cannot edit a standard report. Please duplicate and create a new report".
MUST expect on_trash to throw "You are not allowed to delete Standard Report" unless developer_mode is on or in_migrate or in_patch is set.
MUST expect letter_head to be cleared on save, because it is offered on non-standard reports only.

## values

blank is_standard: No, or Yes for Administrator with developer_mode 1
standard save requires: Administrator, and developer_mode or in_migrate, in_patch, in_install, in_import
export runs when: is_standard Yes and developer_mode 1, skipped under in_import
Script Report code: the module on disk for Yes, report_script through safe_exec for No
non-standard script check: frappe.only_for("Script Manager") for a report_type other than Report Builder or Custom Report
module default: the ref_doctype's module

## how

is_standard is one word that decides three separate behaviours, and a save that leaves it blank
chooses it for you: on a developer bench as Administrator the answer is Yes. Everything after follows
from that word, so set it deliberately and read a new file under an app's report folder as this
branch having fired.

Standard means the disk is the source. The record's JSON and, for a Script Report, its python and
javascript are written out of the database into the app, and from then on the code that runs is the
module, not the field the desk still shows. A report you intend to keep in the database must be
saved as No.

The refusal is asymmetric: the export needs developer_mode, the deletion is blocked without it, so a
standard report created on a bench cannot be removed on the server it was deployed to except through
a migration or a patch.
