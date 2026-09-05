---
name: report
description: A Script Report that passes fifteen seconds turns itself into a Prepared Report and a Query Report never does, and execute is unpacked to six values so a two-value return leaves four rendered parts empty.
triggers: ["Report.execute_query_report", "Report.execute_script_report", "Report.execute_module", "Report.execute_script", "enable_prepared_report", "check_safe_sql_query", "generate_report_result", "get_report_result", "add_total_row", "run", "ljust_list", "render_summary", "show_status", "render_chart", "Cannot edit a standard report. Please duplicate and create a new report", "You are not allowed to delete Standard Report", "Must specify a Query to run", "prepared report vs query report", "script report timeout", "my report renders the table but the chart never shows up", "why are the number cards above my report missing", "i wrote a chart into the report and nothing at all appears on screen", "the report looks finished but half of what i returned is just not there", "my report spins forever and never comes back for big date ranges", "the report worked fine last year and now it times out as the table grew", "how do i stop the report from blocking the page while it runs", "i rewrote the slow report as raw sql and it got worse not better", "there is an extra summary line at the bottom of my report that i never asked for", "how do i get rid of the total row at the end of the report", "the numbers in the cards at the top do not agree with the rows in the table", "why does my report sometimes finish in the background and sometimes not"]
product: frappe
---

# Report

## paths

frappe/core/doctype/report/report.py — Report.execute_query_report, Report.execute_script_report, Report.execute_module, Report.execute_script, enable_prepared_report, check_safe_sql_query
frappe/desk/query_report.py — generate_report_result, get_report_result, add_total_row, run
frappe/core/utils.py — ljust_list
frappe/public/js/frappe/views/reports/query_report.js — render_summary, show_status, render_chart

## rules

MUST return six values from execute — columns, result, message, chart, report_summary, skip_total_row — because ljust_list pads a shorter tuple with None and nothing warns.
MUST return the same width on every branch of execute, including the empty-result branch.
MUST build report_summary from the rows already in `result`, never from a second query, because a summary computed apart from the table eventually disagrees with it and the reader cannot tell which is wrong.
MUST return `chart` to get a chart; the Desk draws it through frappe.Chart with no client code and no library in the app.
MUST set skip_total_row to suppress the total row that the Report's own `add_total_row` adds; it has no effect where add_total_row is unset.
MUST keep a report that will run against a growing table as a Script Report: execute_script_report starts a threading.Timer that calls enable_prepared_report after fifteen seconds, so a slow run moves to the background and the operator gets a Prepared Report instead of a spinner.
NEVER convert a Script Report to a Query Report for speed; execute_query_report runs frappe.db.sql synchronously with no timer, so a slow run blocks the request every time.
MUST hoist a query out of a loop before changing the report type, because both types compile to SQL and the cost difference in a slow report is almost always a query issued per row.
NEVER read a chartless, summary-less report as finished; that is what a two-value return looks like.

## values

1 columns: the column definitions
2 result: the rows
3 message: HTML shown above the table by show_status
4 chart: drawn by the Desk through frappe.Chart
5 report_summary: the number cards above the table, drawn by render_summary
6 skip_total_row: suppresses add_total_row
prepared threshold: 15 seconds, Script Report only
query path: check_safe_sql_query, then frappe.db.sql, synchronous

## how

Both halves of this subject work the same way: the framework accepts less than it offers and says nothing. `execute` may return two values and the report renders; the four positions after `result` are simply empty, and a report with no chart and no number cards looks like a report that was never meant to have them. So read the width of the return, not the look of the screen, when asking whether a report is complete.

The type choice is not python against SQL. Both end in one query, and the difference that shows up under growth is whether anything catches the slow run. The script path arms a timer before it runs and disarms it after; the query path has nothing. That makes Script the type that survives a table getting bigger, which is the opposite of the intuition that pushes people to rewrite a slow report as raw SQL.

Write the summary from the rows the table already holds. The moment it comes from its own query it is a second answer to the same question, and the two drift apart in the direction of whichever filter one of them forgot.
