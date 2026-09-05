---
name: row-scope
description: The user whose User Permissions scope a report's rows arrives as an argument to run, and the pass that applies them recognises a Link column only and drops one whose cells are all empty.
triggers: ["run", "validate_filters_permissions", "get_filtered_data", "get_linked_doctypes", "get_columns_dict", "get_column_as_dict", "has_match", "generate_report_result", "Prepared Report", "Must have report permission to access this report.", "Prepared report render failed", "Report updated successfully", "report rows scoped by user permission", "restrict report rows to user's own data", "users are seeing rows that belong to other people", "why does the report ignore the per user restrictions i set up", "the same report shows all rows to one person and only their own to another", "the rows got filtered correctly yesterday and today everyone sees everything", "restrictions stopped applying when that column happened to be blank in every row", "the scheduled version of the report shows a different set of rows than when i run it myself", "how do i limit a report so each person only sees their own records", "adding a column type made half my rows vanish and i changed no permissions", "the report errors out when i pick a value in the filter dropdown", "it says i must have permission to access this report even though i can open it", "sharing the document did not make the extra rows show up", "why is filtering happening after the query instead of inside it"]
product: frappe
---

# Report row scope

## paths

frappe/desk/query_report.py — run, validate_filters_permissions, get_filtered_data, get_linked_doctypes, get_columns_dict, get_column_as_dict, has_match
frappe/core/doctype/prepared_report/prepared_report.py — generate_report_result

## rules

MUST read a report's rows as scoped by the user argument run received; run falls back to frappe.session.user only when the caller passes none.
MUST give a Query Report column a fieldtype and options, because get_linked_doctypes enters a column into the map only where fieldtype is Link and reads options as the doctype.
MUST expect a Link column carrying no value in any row to be deleted from the map, and an empty map to return every row unchanged.
MUST apply the scoping the answer depends on in the query or in the script; get_filtered_data is a python pass after the query and it recognises what the author labelled.
MUST expect run to throw when a filter declared as Link on the Report carries a value the user can neither read nor select.
NEVER expect a shared document to widen the rows unless the ref_doctype's own Link column survives the empty-column removal.
NEVER read has_match as running wholly as the argument user; the unrestricted-read check inside it reads frappe.session.user.

## values

column string form: label:fieldtype/options:width
row key: the column index for a list or tuple row, the fieldname for a dict row
removal rule: a doctype whose key is absent from the columns that carry a value
no match filters built: result is the data unchanged
Prepared Report user: the Prepared Report record's owner
filter check: read or select on the filter's options doctype for the passed user

## how

Two questions look like one. Whether a user may open the report is asked of the session; which rows
come back is asked of the user argument the caller sent. A Prepared Report job runs the report as
the record's owner, so the same report and the same filters give a different row set depending on
who asked for it.

The row pass is a filter over returned data, not a condition in the query. It builds a map of doctype
to column from the columns' own fieldtype, so the scoping exists only where the report author wrote
a Link column with its options. Add the fieldtype and rows disappear; take it away and they come
back, with no User Permission record changed. Treat the pass as an effect of the column labels and
put the real condition in the SQL or in the script.

The empty-column removal makes the same report scoped on one day and unscoped on another: a run
whose Link column happens to be blank in every row returns the map empty, and an empty map applies
nothing at all.
