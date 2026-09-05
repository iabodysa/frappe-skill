---
name: print-format
description: A print format's body is read from the module's html file before the record's own fields, and a print format written for a Report is compiled in the browser by frappe.template.compile rather than by Jinja on the server.
triggers: ["get_print_format", "get_rendered_template", "validate", "before_save", "get_report_print_format", "frappe.template.compile", "get_query", "Not allowed to print draft documents", "Not allowed to print cancelled documents", "print format html source", "print format compiled for report", "i keep editing the layout in the editor and the printout never changes", "my edits to the printed page are silently ignored nothing errors", "why does printing show an old layout that i cannot find anywhere", "it says no template found but the file is clearly there", "the layout i built for a report comes out blank or throws in the browser", "the same tags that work on a document printout do nothing on a report printout", "how do i pull extra data from the database into a report printout", "it will not let me save changes and complains the layout is standard", "why can i edit one printout but not another", "the printout picked a module i never chose and now looks in the wrong app", "my filters and helpers stopped working when i print a report instead of a document"]
product: frappe
---

# Print Format

## paths

frappe/www/printview.py — get_print_format, get_rendered_template
frappe/printing/doctype/print_format/print_format.py — validate, before_save
frappe/public/js/frappe/views/reports/query_report.js — get_report_print_format
frappe/public/js/frappe/microtemplate.js — frappe.template.compile
frappe/public/js/frappe/form/print_utils.js — get_query

## rules

MUST ask which of the three sources get_print_format will take — the file in the module's Print Format folder, then raw_commands, then html — before editing a print format.
MUST read "No template found at path" as an empty record rather than a missing file, because the message names the path whichever of the three was empty.
MUST mark the Module Def custom to stop the disk read, since that flag is the only branch that skips it.
MUST expect a format created in the desk to take the DocType's own module, and with it that module's app folder.
MUST write a Report print format in the syntax frappe.template.compile accepts, because it rewrites the Jinja delimiters into its own and hands the result to new Function.
NEVER put a Jinja filter, a server global or a frappe.db call in a Report print format; printview.py is not entered, so nothing renders it on the server and validate_print_permission never runs.
MUST expect validate to skip validate_template whenever print_format_type is JS, so a Report format is saved unchecked.
MUST expect before_save to force custom_format 1 and standard No whenever print_format_for is Report.
MUST expect validate to throw "Standard Print Format cannot be updated" for a standard format outside developer_mode, in_migrate, in_install and in_test.

## values

source order: the module's Print Format folder, file named frappe.scrub(name) with an html suffix; then raw_commands; then html
module default: print_format.module, else the doc_type's or report's module
disk read skipped when: the Module Def is flagged custom
Report picker filters: print_format_for Report, print_format_type JS, the current report, disabled 0
Report format fetched as: html and css by frappe.db.get_value, returned as a style tag followed by the html
data a Report format sees: the rows the browser already holds, not a fresh run
disabled format: get_print_format throws DoesNotExistError

## how

The record shows an HTML field, so the record reads as the source. It is the last of three and the
disk wins. A format whose scrubbed name matches a file already present under the module it inherited
is served from that file at every render, and editing the record changes nothing and reports no
error. Ask where the module came from first, because a desk-created format never chose its own
module.

A Report print format and a DocType print format are rows of the same DocType written with the same
delimiters and executed by two different engines in two different processes. Only the DocType one is
Jinja. The Report one is fetched by the browser, its delimiters rewritten, and compiled with
new Function against the rows already loaded — so the language is JavaScript and nothing the server
would have supplied is available. Choose the format's engine by what the page must reach: server
data and a permission check mean a DocType format, the loaded report rows mean a Report format.
